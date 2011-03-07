# -*- coding: utf-8 -*-
"""
simple interactive shell for editing multiple tickets
trying to wrapup tracrpc functionality in an interactive shell 
"""

'''
Created on Mar 3, 2011

@author: scripty
'''

import cmd
import readline
import sys
import os
import optparse

from pprint import pprint


class ShellOptParser(optparse.OptionParser):
    
    def __init__(self):
        optparse.OptionParser.__init__(self)
        #cmd.Cmd.__init__(self)
    
    def error(self, msg):
        '''my own option parser error handling function that does not exit, it throws an optionparseException'''
        print msg
        #self.print_usage(sys.stderr)
        raise Exception('option parsing error')
        #return
    
        
"""'q': 'query $0',
    'v': 'view $0',
    'e': 'edit $0',
    'c': 'create $0',
    'log': 'changelog $0',
    'Q': 'quit',
    'EOF': 'quit',"""
DEFAULT_ALIASES = {
    'v': 'view $0',
    'g': 'get $0',
    'q': 'query $0',
    'qe': 'queryedit $0',
    'pqe': 'pausequeryedit',
    'sqe': 'stopqueryedit',
    'Q': 'quit',
    'b': 'previousticket',
    '<': 'previousticket',
    'n': 'nextticket',
    '>': 'nextticket',
    'e': 'edit $0',
    'm': 'milestone',
    'c': 'component',
    'pl': 'parentlinks',
    'cl': 'childlinks',
    'l': 'links',
    'p': 'setpriority',
    's': 'status',
    'sm': 'showmilestones',
    'milestones': 'showmilestones',
    'pt': 'parsetest $0',
    
}

class TracShell(cmd.Cmd):
    '''
    classdocs
    '''
    tracrpc = None
    ticketid = None
    singleticketmode = False
    
    username = None
    
    batcheditmode = False
    batchquery = None
    batchticketlist = None
    batchskip = None
    batchticketindex = None
    currentticketid = None
    currentticket = None
    
    #future use:
    batch_showonnext = False
    append_max0_toquery = False
    batchprefetch = 0
    
    
    stdprompt = 'tshell> '
    optparser = None
    
    def __init__(self, tracrpc=None, ticketid=None, tracpath=None, debug=False):
        '''
        Constructor
        '''
        
        histfile = os.path.join(os.environ["HOME"], ".tracshellhist")
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass
        
        import atexit
        atexit.register(readline.write_history_file, histfile)
        del histfile

        #self.optparser = ShellOptParser()
        #tracrpc lolfoo...
        if not tracrpc:
            #print "pass a tacrpc instance as arg. scripty's OOriented foo lol is very lol..."
            #return None
            from deployment.utils import fabdir
            sys.path.append(fabdir())
            from deployment.ada.issuetracker import _getbot
            self.tracrpc, self.username = _getbot(tracpath=tracpath, debug=debug)
        else:    
            self.tracrpc = tracrpc
        
        if ticketid:
            try:
                self.ticketid = int(ticketid)
                self.singleticketmode = True
            except ValueError:
                print "non integer value supplied to tracshell as ticketid"
                return None
        
        cmd.Cmd.__init__(self)
        self.prompt = self.stdprompt
        self.aliases = {}
        self.aliases.update(DEFAULT_ALIASES)
    
    def refetchticketafteredit(fn):
        '''my funky decorator to refetch the current ticket, after the function returned'''
        def wrapped(self, *args, **kwargs):
            #print "calling func:%s" % fn
            ret = fn(self, *args, **kwargs)
            #print "refetching ticket"
            self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
            return ret
        
        return wrapped
    
    def do_status(self, args):
        '''display internal status/mode information'''
        print "batcheditmode:",self.batcheditmode
        print "currentticketid:",self.currentticketid
        print "currentticketidindex:",self.batchticketindex
        print "batchquery:",self.batchquery
        print "batchskip:",self.batchskip
        print "batchticketlist:",self.batchticketlist
        
    
    def do_help(self, args):
        '''help'''
        cmd.Cmd.do_help(self,args)
        """
        if self.batcheditmode:
            print "e to edit (summary,description)"
            print "m for milestone"
            print "c for component"
            print "l for ticket links"
            print "p for priority"
            print "b or < for previous ticket"
            print "n or > for next ticket"
        """
    
    def do_aliases(self, args):
        '''list aliases'''
        print "defined aliases:"
        for alias,cmd in DEFAULT_ALIASES.iteritems():
            print '%s\t%s' % (alias, cmd)
    
    def parsercleanup(fn):
        ''' decorator to remove all options from optparser instance does not work...'''
        def wrapped(self, *args, **kwargs):
            print "decorator not implemented!!!"
            ret = fn(self, *args, **kwargs)
            """
            print "cleaning optparser:"
            
            print "options present:"
            for opt in self.optparser.option_list:
                print "option:",opt.get_opt_string()
                
            print ""
            print "cleaning"
            print ""
            for opt in self.optparser.option_list:
                self.optparser.remove_option(opt.get_opt_string())
            
            for opt in self.optparser.option_list:
                print "option:",opt.get_opt_string()
            
            print "cleaning done"
            """
            return ret
        
        return wrapped
    
    
    def run(self):
        print "tracshell:"
        if self.singleticketmode:
            print "ticket:",self.ticketid
        else:
            pass
        
        self.cmdloop("introbanner")
    
    def postcmd(self, stop, line):
        ''' '''
        if self.batcheditmode:
            self.prompt = "batch>ID-%d: " % self.currentticketid
        elif not self.batcheditmode and self.currentticketid != None:
            self.prompt = "single>ID-%d: " % self.currentticketid
        else:
            self.prompt = self.stdprompt
        
        cmd.Cmd.postcmd(self, stop, line)
        
    
    def do_test(self, args=None):
        print "test method"
        print "args:",args
        
    def do_quit(self, _):
        """
        Quit the program
        Shortcut: Q
        """
        # cmd.Cmd passes an arg no matter what
        # which we don't care about here.
        # possible bug?
        print "Goodbye!"
        sys.exit()
        
    def emptyline(self):
        """Method called when an empty line is entered in response to the prompt. If this method is not overridden, it repeats the last nonempty command entered."""
        return
    
    def precmd(self, line):
        """handles alias commands for line (which can be a string or list of args)"""
        if isinstance(line, basestring):
            parts = line.split(' ')
        else:
            parts = list(line)
            line = ' '.join(line)
        cmd = parts[0]
        if cmd in self.aliases:
            cmd = self.aliases[cmd]
            #print "cmd:",cmd
            args = parts[1:]
            unused_args = [] # they go into $0 if it exists
            for index, arg in enumerate(args):
                #print "i:",index,"arg:",arg
                param_placeholder = '$%d' % (index + 1)
                if param_placeholder in cmd:
                    cmd = cmd.replace(param_placeholder, arg)
                else:
                    unused_args.append(arg)
            if unused_args and '$0' in cmd:
                cmd = cmd.replace('$0', ' '.join(unused_args))
                #print "cmd:",cmd
            #print "returning cmd:"
            #pprint(cmd)
            return cmd
        else:
            #print "returning line:"
            #pprint(line)
            return line
    
    
    #@parsercleanup
    #@refetchticketafteredit
    def do_edit(self, args):
        '''edit a ticket'''
        parser = ShellOptParser()
        parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)
        parser.add_option('-c', '--comment', action='store', dest='comment', default=None)
        tid = None
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        if len(args) < 1 and not self.currentticketid:
            print("at least one ticket id is needed.")
            return
        elif len(args) > 1:
            print "too many arguments"
            return
        elif len(args) == 0 and self.currentticketid:
            tid = self.currentticketid
        else:
            try:
                tid = args[0]
            except ValueError:
                print "only ints are valid ticket IDs"
                return
        
        self.tracrpc.edit_ticket(tid, comment=opts.comment)
    
    def do_forget(self, args):
        '''forget the current ticket - only in non batchmode'''
        if self.batcheditmode:
            print "error: batcheditmode is on. this only works in non batchmode"
        else:
            self.currentticketid = None
            self.currentticket = None
        
    def do_get(self, args):
        '''get ticket specified by ID - fetches the ticket for interactive editing.'''
        parser = ShellOptParser()
        parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)
        tid = None
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        if len(args) < 1 and not self.batcheditmode:
            print("at least one ticket id is needed.")
            return
        elif not self.batcheditmode:
            try:
                tid = int(args[0])
            except ValueError:
                print "only integers are valid ticket IDs"                
                return
        
        if self.batcheditmode and tid not in self.batchticketlist:
            print "that ticket is not in your current query. use 'pausequeryedit' or 'stopqueryedit'..."
            return
        elif self.batcheditmode and tid in self.batchticketlist:
            self.batchticketindex = self.batchticketlist.index(tid)
            self.currentticketid =  tid
            self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
        else:
            self.currentticketid =  tid
            self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True) 
        
    def do_view(self, args):
        '''view a ticket: view ID [-v|--verbos=]'''
        parser = ShellOptParser()
        parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)
        tid = None
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        if len(args) < 1 and not self.currentticketid:
            print("at least one ticket id is needed.")
            return
        elif len(args) > 1:
            print "too many arguments"
            return
        elif len(args) == 0 and self.currentticketid:
            tid = self.currentticketid
        else:
            try:
                tid = args[0]
            except ValueError:
                print "only ints are valid ticket IDs"
                return
        
        if tid == self.currentticketid:
            self.print_ticket(self.currentticket)            
        else:
            self.print_ticket(self.tracrpc._get_ticket(tid, getlinks=True))
        
    
    
    def do_query(self, args):
        '''query trac for tickets,params: query,[(int)skip],[True|False (output only numbers]'''
        parser = ShellOptParser()
        parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)
        parser.add_option('-s', '--skip', action='store', dest='skip', type='int', default=0)
        parser.add_option('-n', '--onlynumbers', action='store_true', dest='onlynumbers', default=False)
        parser.add_option('-m', '--max0', action='store_true', dest='addmax0', default=False, help="add max=0 to query")
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        if len(args) < 1:
            print "please supply a query"
            return
        elif len(args) > 1:
            print "too many arguments"
            return
        
        q = args[0]
        if opts.addmax0 == True:
            q = '%s&max=0' % q
        self.tracrpc.simple_query(query=q, only_numbers=opts.only_numbers, skip=opts.skip)
    
    
    def do_queryedit(self, args):
        '''batch edit a series of tickets,params: query,[(int)skip]'''
        parser = ShellOptParser()
        parser.add_option('-s', '--skip', action='store', dest='skip', type='int', default=0)
        parser.add_option('-m', '--max0', action='store_true', dest='addmax0', default=False, help="add max=0 to query")
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        if len(args) < 1:
            print "please supply a query"
            return
        elif len(args) > 1:
            print "too many arguments"
            return
        
        q = args[0]
        if opts.addmax0 == True:
            q = '%s&max=0' % q
        
        skip = opts.skip
        self.batcheditmode = True
        self.batchquery = q
        self.batchticketlist = None
        self.batchskip = skip
        
        ticket_ids = self.tracrpc._safe_rpc(self.tracrpc.jsonrpc.ticket.query, q)

        if skip > len(ticket_ids):
            print "with skip=%d, i would skip all tickets... skipping 0 tickets."
            skip = 0
        
        self.batchticketlist = ticket_ids[skip:]
        
        print "%d tickets fetched - %s skipped" % (len(ticket_ids), skip)
        self.batchticketindex = 0
        self.currentticketid =  self.batchticketlist[self.batchticketindex]
        self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
        print "batchmode turned on!"
        return
    
    def do_pausequeryedit(self, args):
        '''pause a query edit session'''
        print "not implemented!"
        return
    
    def do_stopqueryedit(self,args):
        '''stop a query edit session'''
        tmp = raw_input("sure? (y/n)")
        if tmp.lower() == 'y':
            self.batcheditmode = False
            self.batchquery = None
            self.batchskip = None
            self.batchticketindex = None
            self.batchticketlist = None
            self.currentticketid = None
            self.currentticket = None
            
        else:
            print "continuing query edit session"
            
    
    def do_previousticket(self, args):
        '''select the next ticket in batchedit mode'''
        if not self.batcheditmode:
            print "not in batcheditmode!"
            return
        if self.batchticketindex-1 < 0:
            self.batchticketindex = len(self.batchticketlist)-1
            print "wrapped: giving you the last ticket"
        else:
            self.batchticketindex -= 1
        
        self.currentticketid = self.batchticketlist[self.batchticketindex]
        self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
        if self.batch_showonnext:
            self.tracrpc.show_ticket(self.currentticketid, verbose=True)
    
    def do_nextticket(self, args):
        '''select the next ticket in batchedit mode'''
        if not self.batcheditmode:
            print "not in batcheditmode!"
            return
        
        if self.batchticketindex+1 > len(self.batchticketlist)-1:
            self.batchticketindex = 0
            print "wrapped: giving you the first ticket"
        else:
            self.batchticketindex += 1
        
        self.currentticketid = self.batchticketlist[self.batchticketindex]
        self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
        if self.batch_showonnext:
            self.tracrpc.show_ticket(self.currentticketid, verbose=True)
    
    
    @refetchticketafteredit
    def do_component(self,args):
        '''set component of a ticket'''
        if not self.currentticketid:
            print "no ticket set - use 'get ID' or do a queryedit"
            return
        print "possible values:",', '.join(self.tracrpc.get_components())
        print "current component: '%s'" % self.currentticket['component']
        component = raw_input('new component: ')
        self.tracrpc.update_ticket_field(self.currentticketid, fieldname='component', new_value=component, forbiddenvaluelist=[None,], comment=None)
    
    @refetchticketafteredit
    def do_milestone(self,args):
        '''set milestone of a ticket'''
        if not self.currentticketid:
            print "no ticket set - use 'get ID' or do a queryedit"
            return
        print "possible values:",', '.join(self.tracrpc.get_milestones())
        print "current milestone: '%s'" % self.currentticket['milestone']
        milestone = raw_input('new milestone: ')
        self.tracrpc.update_ticket_field(self.currentticketid, fieldname='milestone', new_value=milestone, forbiddenvaluelist=[None,], comment=None)
    
    @refetchticketafteredit
    def do_parentlinks(self,args):
        '''set parentlinks of a ticket'''
        if not self.currentticketid:
            print "no ticket set - use 'get ID' or do a queryedit"
            return
        print "current parents: ", self.currentticket['parents']
        idlist = []
        linkline = raw_input('new linklist(willoverwrite): ')
        sepchar = ' '
        if ',' in linkline:
            sepchar = ','
        tmpidlist = linkline.split(sepchar)
        idlist = []
        for id in tmpidlist:
            if id != '':
                try:
                    idlist.append(int(id))
                except ValueError:
                    print "only integers are valid ticket IDS!"
                    return
        
        print "new parents: ", ', '.join([str(id) for id in idlist])
        print "non listed links will be removed!"
        choice = raw_input("correct? (y/n) :")
        if choice.lower() == 'y':
            self.tracrpc.update_ticket_parentlinks(self.currentticketid, newparentlistarg=idlist)
        
    @refetchticketafteredit
    def do_childlinks(self,args):
        '''set childlinks of a ticket'''
        if not self.currentticketid:
            print "no ticket set - use 'get ID' or do a queryedit"
            return
        print "current children: ", self.currentticket['children']
        linkline = raw_input('new linklist(willoverwrite): ')
        sepchar = ' '
        if ',' in linkline:
            sepchar = ','
        tmpidlist = linkline.split(sepchar)
        idlist = []
        for id in tmpidlist:
            if id != '':
                try:
                    idlist.append(int(id))
                except ValueError:
                    print "only integers are valid ticket IDS!"
                    return
        
        print "new children: ", ', '.join([str(id) for id in idlist])
        print "non listed links will be removed!"
        choice = raw_input("correct? (y/n) :")
        if choice.lower() == 'y':
            self.tracrpc.link_tickets(self.currentticketid, idlist, deletenonlistedtargets=True)
        
    
    @refetchticketafteredit
    def do_links(self,args):
        '''set links of a ticket'''
        if not self.currentticketid:
            print "no ticket set - use 'get ID' or do a queryedit"
            return
        print "current children: ", self.currentticket['children']
        print "current parents: ", self.currentticket['parents']
        
    @refetchticketafteredit   
    def do_setpriority(self,args):
        '''set priority of a ticket'''
        if not self.currentticketid:
            print "no ticket set - use 'get ID' or do a queryedit"
            return
        print "possible values:",', '.join(self.tracrpc.get_priorities())
        print "current priority: '%s'" % self.currentticket['priority']
        priority = raw_input('new priority: ')
        self.tracrpc.update_ticket_field(self.currentticketid, fieldname='priority', new_value=priority, forbiddenvaluelist=[None,], comment=None)
    
    
    def do_showmilestones(self,args):
        '''show all defined milestones'''
        self.tracrpc.show_milestones()
    
    def do_showpriorities(self, args):
        '''show all defined priorities'''
        self.tracrpc.show_priorities()
    
    def do_showcomponents(self, args):
        '''show all defnied components'''
        self.tracrpc.show_components()
    
    def print_ticket(self,ticket):
        '''prints a ticket in a nicer way than tracrpc'''
        pprint(ticket)
        
if __name__ == '__main__':
    s = TracShell()
    s.run()

