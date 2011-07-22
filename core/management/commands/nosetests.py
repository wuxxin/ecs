import os, sys, datetime
import importlib
from xml.dom.minidom import parse
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from StringIO import StringIO

from textwrap import wrap

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-o', action='store', dest='outfile', help='output file', default=None),
        make_option('-i', action='store', dest='infile', help='input file', default=None),
        make_option('-d', action='store', dest='cdate', help='cdate', default=None),
    )
    def handle(self, test, **options):
        
        cdate = None
        if not options['outfile']:
            print "no output file specified!"
            return
        if not options['infile']:
            print "no input file specified!"
            return
        if not options['cdate']:
            cdate = datetime.datetime.now()
            print "Warning! no cdate specified. Using now()"
        
        cdate = datetime.datetime.strptime(options['cdate'].replace(' +0000', ''), '%a, %d %b %Y %H:%M:%S')
        
        #FIXME
        print "DEBUG FIXME for workflow model to import 'test' must be in sys.argv at import time:"
        print "test in sys.argv:", 'test' in sys.argv
        
        
        
        #parse xml:
        dom1 = parse(options['infile'])
        
        headerinfo = {}
        headerinfo['date'] = cdate.strftime('%Y.%m.%d %H:%M:%S')
        headerinfo['tests'] = dom1.firstChild.attributes.getNamedItem('tests').value
        headerinfo['failures'] = dom1.firstChild.attributes.getNamedItem('failures').value
        headerinfo['errors'] = dom1.firstChild.attributes.getNamedItem('errors').value
        headerinfo['name'] = dom1.firstChild.attributes.getNamedItem('name').value
        headerinfo['skip'] = dom1.firstChild.attributes.getNamedItem('skip').value
         
        cases = {}
        for testcase in dom1.firstChild.childNodes:
            cname = testcase.attributes.getNamedItem('classname').value
            if not cases.has_key(cname):
                cases[cname] = {}
                cases[cname]['tests'] = []
            
            case = {'failed':False,
                    'errors': [],
                    }
            
            for k in testcase.attributes.keys():
                case[k] = testcase.attributes.getNamedItem(k).value
            
            #check if testcase has child nodes "error" or "failure"
            if testcase.hasChildNodes():
                for child in testcase.childNodes:
                    if child.tagName == 'error':
                        derror = {}
                        for k in child.attributes.keys():
                            derror[k] = child.attributes.getNamedItem(k).value
                        derror['traceback'] = child.childNodes[0].wholeText
                        case['errors'].append(derror)
                    elif child.tagName == 'failure':
                        dfailure = {}
                        for k in child.attributes.keys():
                            dfailure[k] = child.attributes.getNamedItem(k).value
                        dfailure['traceback'] = child.childNodes[0].wholeText
                        case['failure'] = dfailure
                        case['failed'] = True
                    else:
                        print "unhandled testcase child tag in",cname, case['name']
            
            
            cases[cname]['tests'].append(case)
        
        
        undoc_count = 0
        #get all docstring via importing
        for pclassname, casedict in cases.iteritems():
            tests = casedict['tests'] 
            module_doc = ""
            impname = pclassname[:pclassname.rindex('.')]
            classname = pclassname[pclassname.rindex('.')+1:]
            
            try:
                m=importlib.import_module(impname)
                module_doc = m.__doc__
                
                try:
                    c=getattr(m, classname)
                    cases[pclassname]['docstring'] = c.__doc__
                    for test in tests:
                        t=getattr(c, test['name'])
                        test['docstring'] = t.__doc__ if t.__doc__ else ""
                        if not t.__doc__:
                            undoc_count += 1 
                    
                    
                except AttributeError,ae:
                    #FIXME what's different for ecs.tests that it doesn't work?
                    if impname == 'ecs' and classname ==  'tests':
                        print "FIXME: cannot import ecs.tests for unknown reason..."
                        for test in tests:
                            if not test.has_key('docstring'):
                                test['docstring'] = ''
                                print pclassname,test['name'], 'docstring is missing'
                    else:
                        raise AttributeError(ae)
                    
                
                if not cases[pclassname].has_key('docstring'):
                    cases[pclassname]['docstring']=''
                    print pclassname, "docstring is missing"
                
                    
            except ImportError,ie:
                
                print " ",ImportError,ie
                print " ",classname,"failed"
                pass

        
        sortedcases = []
        for key in sorted(cases.iterkeys()):
            cases[key]['pclassname'] = key
            sortedcases.append(cases[key])
        testcases2rst(headerinfo, sortedcases, outfile=options['outfile'])
        print ""
        print "done"
        print "debug: {0} undocumented tests".format(undoc_count)

        
def testcases2rst(headerinfo, cases, outfile, one_case_per_page=False, write_table=True):
    '''dumps testcase data from hudson mixed in with docstrings to a single file'''
    import codecs
    if not cases:
        print "no testcase data to dump"
        return
    
    hlines = []
    if headerinfo:
        hlines.append("")
        hlines.append("")
        hlines.append("Execution Date: {0}".format(headerinfo['date']))
        hlines.append("")
        hlines.append("")
        hlines.append("total tests: {0}".format(headerinfo['tests']))
        hlines.append("total failed tests: {0}".format(headerinfo['failures']))
        hlines.append("")
        hlines.append(".. raw:: latex")
        hlines.append("")
        hlines.append("   \pagebreak")
        hlines.append("   \\newpage")
        hlines.append("")
        hlines.append("")
    
    
    writer = RstTable(maxwidth=200)
    
    
    for case in cases:
        pclassname = case['pclassname']
        tests = case['tests']
        casedict = case
        
        writer.out.append("{0}".format(pclassname) )
        writer.out.append("#"*len(pclassname) )
        writer.out.append("")
        writer.out.append("General description")
        writer.out.append("-------------------")
        writer.out.append("")
        writer.out.append("{0}".format(casedict['docstring']))
        writer.out.append("")
        writer.out.append("Tests")
        writer.out.append("-----")
        writer.out.append("")
        #writer.table_line_multi([('Testcase-ID',34), ('description',40), ('failed/passed', 7), ('time',4)], tableheader=True)
        writer.table_line_multi([('Testcase-ID',34), ('failed/passed', 7), ('time',5)], tableheader=True)
        for test in tests:
            failstring = 'FAILED' if test['failed'] else 'PASSED'
            #writer.table_line_multi([(test['name'],34), (test['docstring'],40), (failstring, 7), (test['time'],5)])
            writer.table_line_multi([(test['name'],34), (failstring, 7), (test['time'],5)])
            
        writer.out.append("")
        writer.out.append("")
        writer.out.append("")
        for test in tests:
            writer.out.append("{0}".format(test['name']))
            writer.out.append("    {0}".format(test['docstring']))
            writer.out.append("")
        writer.out.append("")
        
        if one_case_per_page:
            writer.out.append(".. raw:: latex")
            writer.out.append("")
            writer.out.append("   \pagebreak")
            writer.out.append("   \\newpage")
            writer.out.append("")
            writer.out.append("")
        else:
            writer.out.append("")
            writer.out.append("")
            
    
    fd = codecs.open(outfile, 'wb', encoding='utf-8')
    fd.write('\n'.join(hlines))
    fd.write('\n'.join(writer.out))
    fd.close()
    
class RstTable():
    
    def __init__(self, maxwidth=164):
        self.out = []
        self.maxwidth = maxwidth
        
    
    
    def table_header(self, line):
        self.out.append("%s%s%s" % ("+","-"*(self.maxwidth-2),"+"))
        nline = "| %s" % line
        nline2 = " "*(maxwidth-len(nline)-1)
        self.out.append("%s%s|"  % (nline,nline2))
        self.out.append("%s%s%s" % ("+","="*(self.maxwidth-2),"+"))
    
    def table_sep(self):
        self.out.append("%s%s%s" % ("+","-"*(self.maxwidth-2),"+"))
    
    def table_emptyline(self):
        self.out.append("")
    
    def table_line(self, line):
        lines = []
        if len(line)+4 > self.maxwidth:
            for extraline in wrap(line, self.maxwidth-4):
                nline = "| %s" % extraline
                nline2 = " "*(self.maxwidth-len(nline)-1)
                self.out.append("%s%s|"  % (nline,nline2))
             
        else:
            nline = "| %s" % line
            nline2 = " "*(self.maxwidth-len(nline)-1)
            self.out.append("%s%s|"  % (nline,nline2))
    
    def table_line_multi(self, valuelist=None, tableheader=False, tablefooter=False):
        if not valuelist:
            return
        if tableheader or tablefooter:
            linemarker = u'-'
            i = 0
            for tup in valuelist:
                maxw = tup[1]
                if i == 0:
                    line = u'%s' % ("%s%s%s" % ("+",linemarker*(maxw+3),"+"))
                elif i == len(valuelist)-1:
                    line = u'%s%s' % (line, "%s%s" % (linemarker*(maxw+2),"+"))
                else:
                    line = u'%s%s' % (line, "%s%s" % (linemarker*(maxw+2),"+"))
                i +=1
            self.out.append(line)
        
        tmpout = {}
        i = 0
        for tup in valuelist:
            tmpout[i] = []
            i += 1
        i = 0
        for tup in valuelist:
            maxw = tup[1]
            fval = tup[0]
            if len(fval) > maxw:
                for extraline in wrap(fval, maxw):
                    if len(extraline) != maxw:
                        tmpout[i].append(u'%s%s' % (extraline, u' '*(maxw-len(extraline))))
                    else:
                        tmpout[i].append(extraline)
                    #tmpout[i].append(extraline)
            else:
                if len(fval) != maxw:
                    tmpout[i].append(u'%s%s' % (fval, u' '*(maxw-len(fval))))
                else:
                    tmpout[i].append(fval)
            i +=1
        
        maxlines = 0
        for pos,lines in tmpout.iteritems():
            if len(lines) > maxlines:
                maxlines = len(lines)
         
        for i in xrange(0,maxlines):
            line = u''
            for pos,flist in tmpout.iteritems():
                if pos == 0:
                    line = u'| %s ' % ( flist[i] if i < len(flist) else u' '*(valuelist[pos][1]))
                elif pos == len(tmpout.keys())-1:
                    line = u'%s | %s |' % (line, flist[i] if i < len(flist) else u' '*(valuelist[pos][1]))
                else:
                    line = u'%s | %s' % (line, flist[i] if i < len(flist) else u' '*(valuelist[pos][1]))
                
            self.out.append(line)
        
        line = ''
        i = 0
        linemarker = '-'
        if tableheader:
            linemarker = '='
        #overrules
        if tablefooter:
            linemarker = '-'
        
        for tup in valuelist:
            maxw = tup[1]
            if i == 0:
                line = u'%s' % ("%s%s%s" % ("+",linemarker*(maxw+3),"+"))
            elif i == len(valuelist)-1:
                line = u'%s%s' % (line, "%s%s" % (linemarker*(maxw+2),"+"))
            else:
                line = u'%s%s' % (line, "%s%s" % (linemarker*(maxw+2),"+"))
            i +=1
        self.out.append(line)
    
    
    
    
