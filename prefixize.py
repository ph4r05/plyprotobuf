#!/usr/bin/env python2
"""
Adds ObjectiveC prefixes to the Protocol Buffers entities.
Used with Protoc objective C compiler: https://github.com/alexeyxo/protobuf-objc

@author Ph4r05
"""

import sys
import re
import plyproto.parser
import plyproto.model as m
import argparse
import traceback
import os.path

class MyVisitor(m.Visitor):
    content=""
    offset=0
    statementsChanged=0
    prefix=""

    def prefixize(self, lu, oldId):
        '''
        Simple frefixization - with constant prefix to all identifiers (flat).
        :param lu:
        :return:
        '''
        return self.replace(lu, self.prefix + str(oldId))

    def replace(self, lu, newCode):
        '''
        Replaces given LU string occurrence with the new one. Modifies local state.
        :param lu:
        :param newCode:
        :return:
        '''
        if not hasattr(lu, "lexspan"):
            raise Exception("LU does not implement lexspan, %s" % lu)
        if lu.lexspan == None:
            raise Exception("LU has None lexspan, %s" % lu)

        # Computing code positions/lengths.
        constCodePart=""
        oldCodeLen=lu.lexspan[1] - (lu.lexspan[0]-len(constCodePart))
        codeStart=self.offset+lu.lexspan[0]-1-len(constCodePart)
        codeEnd=self.offset+lu.lexspan[1]-1

        # Change the content, replace with the new version.
        newCodeLen = len(newCode)
        newContent = self.content[:codeStart] + newCode + self.content[codeEnd:]
        self.content = newContent
        self.offset += newCodeLen - oldCodeLen
        self.statementsChanged+=1

    def __init__(self):
        super(MyVisitor, self).__init__()

        self.first_field = True
        self.first_method = True

    def visit_PackageStatement(self, obj):
        '''Ignore'''
        return True

    def visit_ImportStatement(self, obj):
        '''Ignore'''
        return True

    def visit_OptionStatement(self, obj):
        '''Ignore'''
        return True

    def visit_FieldDirective(self, obj):
        '''Ignore, Field directive, e.g., default value.'''
        return True

    def visit_FieldType(self, obj):
        '''Field type, if type is name, then it may need refactoring consistent with refactoring rules according to the table'''
        return True

    def visit_FieldDefinition(self, obj):
        '''New field defined in a message, check type, if is name, prefixize.'''
        if self.verbose > 3:
            print "\tField: name=%s, lex=%s" % (obj.name, obj.lexspan)

        if isinstance(obj.ftype, m.Name):
            self.prefixize(obj.ftype, obj.ftype.value)

        return True

    def visit_EnumFieldDefinition(self, obj):
        if self.verbose > 3:
            print "\tEnumField: name=%s, %s" % (obj.name, obj)

        return True

    def visit_EnumDefinition(self, obj):
        '''New enum definition, refactor name'''
        if self.verbose > 3:
            print "Enum, [%s] body=%s\n\n" % (obj.name, obj.body)

        self.prefixize(obj.name, obj.name.value)
        return True

    def visit_MessageDefinition(self, obj):
        '''New message, refactor name, w.r.t. path'''
        if self.verbose > 3:
            print "Message, [%s] lex=%s body=|%s|\n" % (obj.name, obj.lexspan, obj.body)

        self.prefixize(obj.name, str(obj.name.value))
        return True

    def visit_MessageExtension(self, obj):
        '''New message extension, refactor'''
        if self.verbose > 3:
            print "MessageEXT, [%s] body=%s\n\n" % (obj.name, obj.body)

        self.prefixize(obj.name, obj.name.value)
        return True

    def visit_MethodDefinition(self, obj):
        return True

    def visit_ServiceDefinition(self, obj):
        return True

    def visit_ExtensionsDirective(self, obj):
        return True

    def visit_Literal(self, obj):
        return True

    def visit_Name(self, obj):
        return True

    def visit_Proto(self, obj):
        return True
       
# Main executable code
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Log statements formating string converter.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i','--in-place',  help='Overwrites provided file with the new content', required=False, default=False, dest='inplace')
    parser.add_argument('-p','--prefix',    help='Constant prefix to be prepended to the entities found', required=False, default="", dest='prefix')
    parser.add_argument('-o','--outdir',    help='Output directory', required=False, default="", dest='outdir')
    parser.add_argument('-e','--echo',      help='Writes output to the standard output', required=False, default=False)
    parser.add_argument('-v','--verbose',   help='Writes output to the standard output', required=False, default=0, type=int)
    parser.add_argument('file')
    args = parser.parse_args()
    
    # Load the file and instantiate the visitor object.
    p = plyproto.parser.ProtobufAnalyzer()
    if args.verbose>0:
        print " [-] Processing file: %s" % (args.file)
    
    # Start the parsing.
    try:
        v = MyVisitor()
        v.offset = 0
        v.prefix = args.prefix
        with open(args.file, 'r') as content_file:
            v.content = content_file.read()
        
        tree = p.parse_file(args.file)
        tree.accept(v)
        
        # If here, probably no exception occurred.
        if args.echo:
            print v.content
        if args.outdir != None and len(args.outdir)>0 and v.statementsChanged>0:
            outfile = args.outdir + '/' + v.prefix + os.path.basename(args.file).capitalize()
            with open(outfile, 'w') as f:
                f.write(v.content)
        if args.inplace and v.statementsChanged>0:
            with open(args.file, 'w') as f:
                f.write(v.content)
                
        if args.verbose>0:
            print " [-] Processing finished, changed=%d" % v.statementsChanged
    except Exception as e:
        print "    Error occurred! file[%s]" % (args.file), e
        if args.verbose>1:
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        sys.exit(1)
        
