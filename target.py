# ecs main application environment setup
import os
import subprocess
import sys
import shutil
import tempfile
import logging
import string
import random
import distutils.dir_util
import time
import copy

from uuid import uuid4
from fabric.api import local, env, warn, abort, settings

from deployment.utils import get_pythonenv, import_from, get_pythonexe, zipball_create, write_regex_replace
from deployment.utils import touch, control_upstart, apache_setup, strbool, strint, write_template, write_template_dir
from deployment.pkgmanager import get_pkg_manager, packageline_split
from deployment.appsupport import SetupTargetObject
from deployment.conf import load_config


class SetupTarget(SetupTargetObject):
    """ SetupTarget(use_sudo=True, dry=False, hostname=None, ip=None) """ 
    def __init__(self, *args, **kwargs):
        dirname = os.path.dirname(__file__)
        config_file = kwargs.pop('config', None)
        if config_file is None:
            config_file = os.path.join(dirname, '..', 'ecs.yml')
        self.destructive = kwargs.pop('destructive', False)
        super(SetupTarget, self).__init__(*args, **kwargs)
        self.dirname = dirname
        self.appname = 'ecs'
        
        if config_file:
            self.configure(config_file)
        
    def configure(self, config_file):
        self.config = load_config(config_file)
        self.homedir = os.path.expanduser('~')
        self.configdir = os.path.join(self.homedir, 'ecs-conf')
        self.pythonexedir = os.path.dirname(get_pythonexe())
        # set legacy attributes
        for attr in ('ip', 'host'):
            setattr(self, attr, self.config[attr])
        self.config['local_hostname'] = self.config['host'].split('.')[0]
        # set default for parameter that are optional
        self.config.setdefault('debug.filter_smtp', False)
        self.config.setdefault('ssl.chain', '') # chain is optional
        self.config.setdefault('postgresql.username', self.config['user'])
        self.config.setdefault('postgresql.database', self.config['user'])
        self.config.setdefault('rabbitmq.username', self.config['user'])
        self.config.setdefault('rabbitmq.password', self.random_string(20))
        self.config.setdefault('mediaserver.storage.encrypt_key', os.path.join(self.homedir, 'src', 'ecs', 'ecs_mediaserver.pub'))
        self.config.setdefault('mediaserver.storage.signing_key', os.path.join(self.homedir, 'src', 'ecs', 'ecs_authority.sec'))
        self.config.setdefault('mediaserver.storage.decrypt_key', os.path.join(self.homedir, 'src', 'ecs', 'ecs_mediaserver.sec'))
        self.config.setdefault('mediaserver.storage.verify_key', os.path.join(self.homedir, 'src', 'ecs', 'ecs_authority.pub'))
        self.config.setdefault('storagevault.implementation', 'ecs.mediaserver.storagevault.LocalFileStorageVault')
        self.config.setdefault('storagevault.options.localfilestorage_root', os.path.join(self.homedir, 'ecs-storage-vault')) 

    def random_string(self, length=40, simpleset=False):
        if simpleset:
            chars = string.ascii_letters + string.digits
        else:
            chars = string.ascii_letters + string.digits + "_-,.+#!?$%&/()[]{}*;:=<>" # ~6.4 bit/char
            
        return ''.join(random.choice(chars) for i in xrange(length))
        
    def print_random_string(self, length=40, simpleset=False):
        simpleset= strbool(simpleset)
        length = strint(length)
        
        print self.random_string(length=length, simpleset=simpleset)
    
    def get_config_template(self, template):
        with open(os.path.join(self.dirname, 'templates', 'config', template)) as f:
            data = f.read()
        return data
    
    def write_config_template(self, template, dst, context=None, filemode=None, backup=True, force=False, use_sudo=False):
        if context is None:
            context = self.config
        write_template(os.path.join(self.dirname, 'templates', 'config', template),
            dst, context=context, filemode=filemode, backup=backup, force=force, use_sudo=use_sudo)
        
    def help(self, *args, **kwargs):
        print('''fab target:{0},action[,config=path-to-config.yml]
  * actions: system_setup, update, and others
        
        '''.format(self.appname))

    def system_setup(self, *args, **kwargs):
        ''' System Setup; Destructive, idempotent '''
        self.destructive = True
        self.setup(self, *args, **kwargs)
    
    def setup(self, *args, **kwargs):
        ''' Setup; idempotent, tries not to overwrite existing database or eg. ECS-CA , except destructive=True '''
        self.directory_config()
        self.host_config(with_current_ip=True)
        self.servercert_config()
        
        self.backup_config()
        self.mail_config()
        self.queuing_config()
        
        # install_logrotate(appname, use_sudo=use_sudo, dry=dry)

        self.db_clear()
        self.django_config()
        self.gpg_config()
        self.ca_config()        
        self.ca_update()
        self.db_update()
        
        self.search_config()
        self.search_update()
        
        self.apache_baseline()
        self.apache_config()
        self.catalina_config()
        self.daemons_install()
        
        self.custom_network_config()
        self.host_config(with_current_ip=False)
        self.firewall_config()

        self.apache_restart()
        self.daemons_start()


    def update(self, *args, **kwargs):
        ''' System Update: Non destructive '''
        self.directory_config()
        
        self.env_update()
        self.db_update()
        
        self.search_config()
        self.search_update()
        
        self.apache_restart()
        self.daemons_start()

    def maintenance(self, enable=True):
        ''' Enable/Disable System Maintenance (stop daemons, display service html)'''
        enable= strbool(enable)
        if enable:
            touch(os.path.join(self.configdir, 'service.now'))
            self.wsgi_reload()
            self.daemons_stop()
        else:
            os.remove(os.path.join(self.configdir, 'service.now'))
            self.daemons_start()
            self.wsgi_reload()        
    
    def directory_config(self):
        homedir = os.path.expanduser('~')
        for name in ('empty_html', 'public_html', '.python-eggs', 'ecs-conf'):
            pathname = os.path.join(homedir, name)
            if not os.path.exists(pathname):
                os.mkdir(pathname)
        
        # /opt/ecs directory
        pathname = os.path.join('/opt', self.appname)
        if not os.path.exists(pathname):
            local('sudo mkdir {0}'.format(pathname))
        local('sudo chown {0}:{0} {1}'.format(self.appname, pathname))

                
    def host_config(self, with_current_ip=False):
        with_current_ip = strbool(with_current_ip)
        
        _, tmp = tempfile.mkstemp()
        with tempfile.NamedTemporaryFile() as h:
            h.write(self.config['host'])
            h.flush()
            local('sudo cp {0} /etc/hostname'.format(h.name))
        local('sudo hostname -F /etc/hostname')

        value = local('ip addr show eth0 | grep inet[^6] | sed -re "s/[[:space:]]+inet.([^ /]+).+/\\1/g"', capture=True)
        if value != self.config['ip']:
            warn('current ip ({0}) and to be configured ip ({1}) are not the same'.format(value, self.config['ip']))

        if with_current_ip: 
            if value.succeeded:
                self.config['current_ip'] = value
                if self.config['current_ip'] != self.config['ip']:
                    warn('Temporary set hosts resolution of {0} to {1} instead of {2}'.format(
                        self.config['host'], self.config['current_ip'], self.config['ip']))
            else:
                abort("no ip address ? ip addr grep returned: {0}".format(value))
        else:
            self.config['current_ip'] = self.config['ip']
        
        self.write_config_template('hosts', tmp)
        local('sudo cp %s /etc/hosts' % tmp)
        os.remove(tmp)
    
    def custom_network_config(self):
        if 'network.resolv' in self.config:
            with tempfile.NamedTemporaryFile() as t:
                t.write(self.config['network.resolv'])
                t.flush()
                local('sudo cp {0} /etc/resolv.conf'.format(t.name))
                
        if 'network.interfaces' in self.config:
            with tempfile.NamedTemporaryFile() as t:
                t.write(self.config['network.interfaces'])
                t.flush()
                local('sudo cp {0} /etc/network/interfaces'.format(t.name))
 
    def firewall_config(self):
        write_template_dir(os.path.join(self.dirname, 'templates', 'config', 'shorewall'), '/', use_sudo=True)
        local('sudo /etc/init.d/shorewall restart')               
        
    def backup_config(self):
        if 'backup.host' not in self.config:
            warn('no backup configuration, skipping backup config')
        else:
            local('sudo rm -r /root/.gnupg')
            local('sudo gpg --homedir /root/.gnupg --rebuild-keydb-caches')
            local('sudo gpg --homedir /root/.gnupg --batch --yes --import {0}'.format(self.config.get_path('backup.encrypt_gpg_sec')))
            local('sudo gpg --homedir /root/.gnupg --batch --yes --import {0}'.format(self.config.get_path('backup.encrypt_gpg_pub')))

            with settings(warn_only=True):
                local('sudo mkdir -m 0600 -p /root/.duply/root')
                local('sudo mkdir -m 0600 -p /root/.duply/opt')
            
            self.config['duplicity.duply_path'] = self.pythonexedir
                
            self.config['duplicity.root'] = os.path.join(self.config['backup.hostdir'], 'root')
            self.config['duplicity.include'] = "SOURCE='/'"
            self.write_config_template('duply.template', 
                '/root/.duply/root/conf', context=self.config, use_sudo=True, filemode= '0600')
            self.write_config_template('duplicity.root.files', '/root/.duply/root/exclude', use_sudo=True)

            self.config['duplicity.root'] = os.path.join(self.config['backup.hostdir'], 'opt')
            self.config['duplicity.include'] = "SOURCE='/opt'"
            self.write_config_template('duply.template', 
                '/root/.duply/opt/conf', context=self.config, use_sudo=True, filemode= '0600')
            self.write_config_template('duplicity.opt.files', '/root/.duply/opt/exclude', use_sudo=True)

            self.config['duplicity.duply_conf'] = "root"
            with settings(warn_only=True): # remove legacy duply script, before it was renamed
                local('sudo bash -c "if test -f /etc/backup.d/90duply.sh; then rm /etc/backup.d/90duply.sh; fi"')
            self.write_config_template('duply-backupninja.sh',
                '/etc/backup.d/90duply-root.sh', backup=False, use_sudo=True, filemode= '0600')
            
            self.config['duplicity.duply_conf'] = "opt"
            with settings(warn_only=True): # remove legacy duply script, before it was renamed
                local('sudo bash -c "if test -f /etc/backup.d/91duply.sh; then rm /etc/backup.d/91duply.sh; fi"')
            self.write_config_template('duply-backupninja.sh',
                '/etc/backup.d/91duply-opt.sh', backup=False, use_sudo=True, filemode= '0600')
            
            self.write_config_template('10.sys', 
                '/etc/backup.d/10.sys', backup=False, use_sudo=True, filemode= '0600')
        
            self.write_config_template('20.pgsql', 
                '/etc/backup.d/20.pgsql', backup=False, use_sudo=True, filemode= '0600')

    def servercert_config(self):
        target_key = '/etc/ssl/private/{0}.key'.format(self.host)
        target_cert = '/etc/ssl/certs/{0}.pem'.format(self.host)
        target_chain = '/etc/ssl/certs/{0}.chain.pem'.format(self.host)
        target_combined = '/etc/ssl/certs/{0}.combined.pem'.format(self.host)
        
        try:
            ssl_key = self.config.get_path('ssl.key')
            ssl_cert = self.config.get_path('ssl.cert')
            local('sudo cp {0} {1}'.format(ssl_key, target_key))
            local('sudo cp {0} {1}'.format(ssl_cert, target_cert))
            local('sudo chmod 0600 {0}'.format(target_key))
        except KeyError:
            warn('Missing SSL key or certificate - a new pair will be generated')
            openssl_cnf = os.path.join(self.configdir, 'openssl-ssl.cnf')
            self.write_config_template('openssl-ssl.cnf', openssl_cnf)
            local('sudo openssl req -config {0} -nodes -new -newkey rsa:2048 -days 365 -x509 -keyout {1} -out {2}'.format(openssl_cnf, target_key, target_cert))
        
        # copy chain file (if exist, or create empty file instead)
        ssl_chain = self.config.get_path('ssl.chain')
        if not ssl_chain:
            with tempfile.NamedTemporaryFile() as t:
                t.write("\n")
                t.flush()
                local('sudo cp {0} {1}'.format(t.name, target_chain))
        else:
            local('sudo cp {0} {1}' % (ssl_chain, target_chain))
        
        # combine cert plus chain to combined.pem
        local('sudo bash -c "cat {0} {1} > {2}"'.format(target_cert, target_chain, target_combined))
            
        local('sudo update-ca-certificates --verbose --fresh') # needed for all in special java that pdf-as knows server cert
        
    def mail_config(self):
        '''
        with tempfile.NamedTemporaryFile() as h:
            h.write(self.config['host'])
            h.flush()
            local('sudo cp {0} /etc/mailname'.format(h.name))
    
        self.config['postfix.cert'] = '/etc/ssl/private/{0}.pem'.format(self.host)
        self.config['postfix.key'] = '/etc/ssl/private/{0}.key'.format(self.host)
        self.write_config_template('postfix.main.cf', '/etc/postfix/main.cf', use_sudo=True)
        self.write_config_template('postfix.master.cf', '/etc/postfix/master.cf', use_sudo=True)                                   
        self.write_config_template('aliases', '/etc/aliases', use_sudo=True)
        
smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
myhostname = ecsdev.ep3.at
mydestination = ecsdev.ep3.at, localhost.ep3.at, , localhost
myorigin = /etc/mailname # $myhostname
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128 %(ip)s/32
[localhost:8823]

mydestination =
local_recipient_maps =
local_transport = error:local mail delivery is disabled
myorigin = /etc/mailname # $myhostname
relay_domains = $myhostname

  myorigin = example.com
  mydestination =
  local_recipient_maps =
  local_transport = error:local mail delivery is disabled
  relay_domains = example.com
  parent_domain_matches_subdomains = 
      debug_peer_list smtpd_access_maps
  smtpd_recipient_restrictions =
      permit_mynetworks reject_unauth_destination
  
  relay_recipient_maps = hash:/etc/postfix/relay_recipients
  transport_maps = hash:/etc/postfix/transport

/etc/postfix/transport:
$myhostname   smtp:[localhost:8823]
        '''
        pass
        
    def gpg_config(self):
        for key, filename in (('encrypt_key', 'ecs_mediaserver.pub'), ('signing_key', 'ecs_authority.sec'), ('decrypt_key', 'ecs_mediaserver.sec'), ('verify_key', 'ecs_authority.pub')):
            try:
                path = self.config.get_path('mediaserver.storage.%s' % key)
                shutil.copy(path, os.path.join(self.configdir, filename))
            except KeyError:
                pass
    
    def ca_config(self):
        if self.destructive:
            openssl_cnf = os.path.join(self.configdir, 'openssl-ca.cnf')
            from ecs.pki.openssl import CA
            cadir = os.path.join(self.homedir, 'ecs-ca')
            if os.path.exists(cadir):
                local('rm -r %s' % cadir)
            ca = CA(cadir, config=openssl_cnf)
            self.write_config_template('openssl-ca.cnf', openssl_cnf, ca.__dict__)
        else:
            warn("Not overwriting openssl-ca.cnf, not removing ecs-ca directory because destructive=False")
        
    def ca_update(self):
        try:
            replacement = self.config.get_path('ca.dir')
        except KeyError:
            return
        basedir = os.path.join(self.homedir, 'ecs-ca')
        if os.path.exists(basedir):
            warn('CA directory exists (%s), refusing to overwrite.' % basedir)
        else:
            shutil.copytree(replacement, basedir)
        
    def django_config(self):
        self.write_config_template('django.py', os.path.join(self.configdir, 'django.py'))
        
    def apache_baseline(self):
        baseline_bootstrap = ['sudo'] if self.use_sudo else []
        baseline_bootstrap += [os.path.join(os.path.dirname(env.real_fabfile), 'bootstrap.py'), '--baseline', '/etc/apache2/ecs/wsgibaseline/']
        local(subprocess.list2cmdline(baseline_bootstrap))
 
    def apache_config(self):
        apache_mkdirs = ['sudo'] if self.use_sudo else []
        apache_mkdirs += ['mkdir', '-p', '/etc/apache2/ecs', '/etc/apache2/ecs/apache.wsgi', '/etc/apache2/ecs/apache.conf']
        local(subprocess.list2cmdline(apache_mkdirs))
        apache_setup(self.appname, use_sudo=self.use_sudo, 
            hostname=self.host, 
            ip=self.ip, 
            ca_certificate_file=os.path.join(self.homedir, 'ecs-ca', 'ca.cert.pem'),
            ca_revocation_file=os.path.join(self.homedir, 'ecs-ca', 'crl.pem'),
        )

    def catalina_config(self):
        write_regex_replace(
            os.path.join(get_pythonenv(), 'tomcat-6', 'conf', 'server.xml'),
            r'^'+
            r'([ \t]+<!--[ \t]*\n|\r\n)?'+
            r'([ \t]+<Connector port="8009" protocol="AJP/1.3" redirectPort="8443" />[ \t]*\n|\r\n)'+
            r'([ \t]+-->[ \t]*\n|\r\n)?',
            r'\2', multiline=True)
        """ # FIXME: Disabled because of cert problems
        write_regex_replace(
            os.path.join(get_pythonenv(), 'tomcat-6', 'conf', 'pdf-as', 'cfg', 'config.properties'),
            r'(moc.sign.url=)(http[s]?://[^/]+)(/bkuonline/http-security-layer-request)',
            #r'\1https://{0}\3'.format(self.config['host']))
            r'\1http://{0}:4780\3'.format(self.config['host']))
        write_regex_replace(
            os.path.join(get_pythonenv(), 'tomcat-6', 'conf', 'pdf-as', 'cfg', 'pdf-as-web.properties'),
            r'([#]?)(retrieve_signature_data_url_override=)(http[s]?://[^/]+)(/pdf-as/RetrieveSignatureData)',
            #r'\2https://{0}\4'.format(self.config['host']))
            r'\2http://{0}:4780\4'.format(self.config['host']))
        """

    def catalina_cmd(self, what):
        TOMCAT_DIR = os.path.join(get_pythonenv(), 'tomcat-6') 
        if sys.platform == 'win32':
            cmd = "set CATALINA_BASE={0}&set CATALINA_OPTS=-Dpdf-as.work-dir={0}\\conf\\pdf-as&cd {0}&bin\\catalina.bat {1}".format(TOMCAT_DIR, what)
        else:
            cmd = subprocess.list2cmdline(['env', 'CATALINA_BASE={0}'.format(TOMCAT_DIR), 'CATALINA_OPTS=-Dpdf-as.work-dir={0}/conf/pdf-as'.format(TOMCAT_DIR), '{0}/bin/catalina.sh'.format(TOMCAT_DIR), what])
        return cmd
    
    def start_dev_signing(self):
        local(self.catalina_cmd('start'))
        
    def stop_dev_signing(self):
        local(self.catalina_cmd('stop'))
    
    def apache_restart(self):
        local('sudo /etc/init.d/apache2 restart')
        
    def wsgi_reload(self):
        local('sudo touch /etc/apache2/ecs/apache.wsgi/ecs-wsgi.py')
        
    def daemons_install(self):
        control_upstart(self.appname, "install", upgrade=True, use_sudo=self.use_sudo, dry=self.dry)

    def daemons_stop(self):
        control_upstart(self.appname, "stop", use_sudo=self.use_sudo, fail_soft=True, dry=self.dry)
        
    def daemons_start(self):
        control_upstart(self.appname, "start", use_sudo=self.use_sudo, dry=self.dry)
        
    def db_clear(self):
        local("sudo su - postgres -c \'createuser -S -d -R %(postgresql.username)s\' | true" % self.config)
        if self.destructive:
            local('dropdb %(postgresql.database)s | true' % self.config, capture=True)            
        else:
            warn("Not dropping/destroying database, because destructive=False")            
        local('createdb --template=template0 --encoding=utf8 --locale=de_DE.utf8 %(postgresql.database)s | true' % self.config)
             
    def db_update(self):
        local('cd {0}/src/ecs; . {0}/environment/bin/activate; ./manage.py syncdb --noinput'.format(self.homedir))
        local('cd {0}/src/ecs; . {0}/environment/bin/activate; ./manage.py migrate --noinput'.format(self.homedir))
        local('cd {0}/src/ecs; . {0}/environment/bin/activate; ./manage.py bootstrap'.format(self.homedir))

    def db_dump(self):
        cmd = 'pg_dump --encoding="utf-8" --format=custom %(postgresql.database)s --file={0}/%(postgresql.database)s.pgdump'.format(self.homedir)
        local(cmd % self.config)

    def db_restore(self):
        with settings(warn_only=True):
            istext = local('file {0}/%(postgresql.database)s.pgdump | grep text'.format(self.homedir) % self.config, capture=True).succeeded
        if istext:
            cmd = 'psql --file={0}/%(postgresql.database)s.pgdump --dbname=%(postgresql.database)s'.format(self.homedir)
        else:
            cmd = 'pg_restore --format=custom --dbname=%(postgresql.database)s {0}/%(postgresql.database)s.pgdump'.format(self.homedir)
        local(cmd % self.config)
                
    def env_clear(self):
        # todo: implement env_clear
        pass
    
    def env_boot(self):
        env_bootstrap = ['sudo'] if self.use_sudo else []
        env_bootstrap += [os.path.join(os.path.dirname(env.real_fabfile), 'bootstrap.py'), 'whereever/sdfkljsd']
        pass
        # FIXME implement env_boot
    
    def env_update(self):
        local('sudo bash -c "cd {0}/src/; . {0}/environment/bin/activate;  fab appreq:ecs,flavor=system"'.format(self.homedir))
        local('cd {0}/src/; . {0}/environment/bin/activate; fab appenv:ecs,flavor=system'.format(self.homedir))
        
    def queuing_config(self):
        with settings(warn_only=True):
            local('sudo killall beam')
            local('sudo killall epmd')
            time.sleep(1)
            local('sudo killall beam')
            local('sudo killall epmd')
            time.sleep(1)
            local('sudo apt-get -y remove --purge rabbitmq-server')
            local('sudo killall beam')
            local('sudo killall epmd')
            time.sleep(1)
            local('sudo bash -c  "export DEBIAN_FRONTEND=noninteractive; apt-get install -q -y rabbitmq-server"')
            
        #local('sudo rabbitmqctl force_reset')
        #if int(local('sudo rabbitmqctl list_vhosts | grep %(rabbitmq.username)s | wc -l' % self.config, capture=True)):
        #    local('sudo rabbitmqctl delete_vhost %(rabbitmq.username)s' % self.config)
        
        local('sudo rabbitmqctl add_vhost %s' % self.username)
            
        if int(local('sudo rabbitmqctl list_users | grep %(rabbitmq.username)s | wc -l' % self.config, capture=True)):
            local('sudo rabbitmqctl delete_user %(rabbitmq.username)s ' % self.config)
        
        local('sudo rabbitmqctl add_user %(rabbitmq.username)s %(rabbitmq.password)s' % self.config)
        local('sudo rabbitmqctl set_permissions -p %(rabbitmq.username)s %(rabbitmq.username)s ".*" ".*" ".*"' % self.config)
            
        
    def search_config(self):
        source_schema = os.path.join(self.homedir, 'ecs-conf', 'solr_schema.xml')
        source_jetty =  os.path.join(self.homedir, 'ecs-conf', 'jetty.cnf')
        local('cd {0}/src/ecs; . {0}/environment/bin/activate; ./manage.py build_solr_schema > {1}'.format(
            self.homedir,  source_schema))
        local('sudo cp {0} /etc/solr/conf/schema.xml'.format(source_schema))
        with open(source_jetty, 'w') as f:
            f.write("NO_START=0\nVERBOSE=yes\nJETTY_PORT=8983\n")
        local('sudo cp {0} /etc/default/jetty'.format(source_jetty))
        local('sudo /etc/init.d/jetty stop')
        time.sleep(5) 
        local('sudo /etc/init.d/jetty start')
        time.sleep(10) # jetty needs time to startup

    def search_update(self):
        local('cd {0}/src/ecs; . {0}/environment/bin/activate;  if test -d ../../ecs-whoosh; then rm -rf ../../ecs-whoosh; fi; ./manage.py rebuild_index --noinput '.format(self.homedir))


def custom_check_gettext_runtime(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), 'bin', checkfilename))
    
def custom_install_gettext_runtime(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    pkg_manager.static_install_unzip(filename, get_pythonenv(), checkfilename, pkgline)
    return True

def custom_check_gettext_tools(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), 'bin', checkfilename))
    
def custom_install_gettext_tools(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    pkg_manager.static_install_unzip(filename, get_pythonenv(), checkfilename, pkgline)
    return True

  
def custom_check_tomcat_apt_user(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), "tomcat-6", "conf", "server.xml"))
    
def custom_install_tomcat_apt_user(pkgline, filename):
    tomcatpath = os.path.join(get_pythonenv(), "tomcat-6")
    
    if os.path.exists(os.path.join(tomcatpath)):
        if os.path.exists(tomcatpath+"-old"):
            shutil.rmtree(tomcatpath+"-old")
        shutil.move(tomcatpath, tomcatpath+"-old")
        
    install = 'tomcat6-instance-create -p 4780 -c 4705 \'{0}\''.format(tomcatpath)
    popen = subprocess.Popen(install, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    stdout, stderr = popen.communicate() 
    returncode = popen.returncode  
    if returncode != 0:
        print "Error:", returncode, stdout, stderr
        return False
    else:
        return True

def custom_check_tomcat_other_user(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), "tomcat-6", "conf", "server.xml"))
    
def custom_install_tomcat_other_user(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    temp_dir = tempfile.mkdtemp()
    temp_dest = os.path.join(temp_dir, checkfilename)
    final_dest = os.path.join(get_pythonenv(), "tomcat-6")
    result = False
    
    try:
        if os.path.exists(final_dest):
            shutil.rmtree(final_dest)
        if pkg_manager.static_install_tar(filename, temp_dir, checkfilename, pkgline):
            write_regex_replace(os.path.join(temp_dest, 'conf', 'server.xml'),
                r'([ \t])+(<Connector port=)("[0-9]+")([ ]+protocol="HTTP/1.1")',
                r'\1\2"4780"\4')
            shutil.copytree(temp_dest, final_dest)
            result = True
    finally:    
        shutil.rmtree(temp_dir)
    
    return result


def custom_check_pdfas(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), "tomcat-6", "webapps", checkfilename))
   
def custom_install_pdfas(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    temp_dir = tempfile.mkdtemp()
    temp_dest = os.path.join(temp_dir, "tomcat-6")
    final_dest = os.path.join(get_pythonenv(), "tomcat-6")
    result = False
    
    try:
        pkg_manager.static_install_unzip(filename, temp_dir, checkfilename, pkgline)
        if pkg_manager.static_install_unzip(filename, temp_dir, checkfilename, pkgline):
            write_regex_replace(
                os.path.join(temp_dest, 'conf', 'pdf-as', 'cfg', 'config.properties'),
                r'(moc.sign.url=)(http://127.0.0.1:8080)(/bkuonline/http-security-layer-request)',
                r'\1http://localhost:4780\3')
            write_regex_replace(
                os.path.join(temp_dest, 'conf', 'pdf-as', 'cfg', 'pdf-as-web.properties'),
                r'([#]?)(retrieve_signature_data_url_override=)(http://localhost:8080)(/pdf-as/RetrieveSignatureData)',
                r'\2http://localhost:4780\4')
            
            distutils.dir_util.copy_tree(temp_dest, final_dest, verbose=True)
            result = True
    finally:    
        shutil.rmtree(temp_dir)
    
    return result


def custom_check_mocca(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), "tomcat-6", "webapps", checkfilename))

def custom_install_mocca(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    outputdir = os.path.join(get_pythonenv(), "tomcat-6", "webapps")
    pkg_manager = get_pkg_manager()
    return pkg_manager.static_install_copy(filename, outputdir, checkfilename, pkgline)


def custom_install_pdftotext(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    tempdir = tempfile.mkdtemp()
    outputdir = os.path.dirname(get_pythonexe())
    result = False
    
    try:
        if pkg_manager.static_install_unzip(filename, tempdir, checkfilename, pkgline):
            try:
                shutil.copy(os.path.join(tempdir,"xpdfbin-win-3.03", "bin32", checkfilename), 
                    os.path.join(outputdir, checkfilename))
            except EnvironmentError:
                pass
            else:
                result = True
    finally:    
        shutil.rmtree(tempdir)
    
    return result


def custom_check_duply(pkgline, checkfilename):
    return os.path.exists(os.path.join(os.path.dirname(get_pythonexe()), checkfilename))

def custom_install_duply(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    tempdir = tempfile.mkdtemp()
    outputdir = os.path.dirname(get_pythonexe())
    result = False
    
    try:
        if pkg_manager.static_install_tar(filename, tempdir, checkfilename, pkgline):
            try:
                shutil.copy(os.path.join(tempdir, 'duply_1.5.5.4', checkfilename), 
                    os.path.join(outputdir, checkfilename))
            except EnvironmentError:
                pass
            else:
                result = True
    finally:    
        shutil.rmtree(tempdir)
    
    return result
