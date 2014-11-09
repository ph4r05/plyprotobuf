__author__ = "Dusan (Ph4r05) Klinec"
__copyright__ = "Copyright (C) 2014 Dusan (ph4r05) Klinec"
__license__ = "Apache License, Version 2.0"
__version__ = "1.0"

import ply.lex as lex
import ply.yacc as yacc
from .model import *

class ProtobufLexer(object):
    keywords = ('double', 'float', 'int32', 'int64', 'uint32', 'uint64', 'sint32', 'sint64',
                'fixed32', 'fixed64', 'sfixed32', 'sfixed64', 'bool', 'string', 'bytes',
                'message', 'required', 'optional', 'repeated', 'enum', 'extensions', 'max', 'extends', 'extend',
                'to', 'package', 'service', 'rpc', 'returns', 'true', 'false', 'option', 'import')

    tokens = [
        'NAME',
        'NUM',
        'STRING_LITERAL',
        'LINE_COMMENT', 'BLOCK_COMMENT',

        'LBRACE', 'RBRACE', 'LBRACK', 'RBRACK',
        'LPAR', 'RPAR', 'EQ', 'SEMI'

    ] + [k.upper() for k in keywords]
    literals = '()+-*/=?:,.^|&~!=[]{};<>@%'

    t_NUM = r'[+-]?\d+'
    t_STRING_LITERAL = r'\"([^\\\n]|(\\.))*?\"'

    t_ignore_LINE_COMMENT = '//.*'
    def t_BLOCK_COMMENT(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')

    t_LBRACE = '{'
    t_RBRACE = '}'
    t_LBRACK = '\\['
    t_RBRACK = '\\]'
    t_LPAR = '\\('
    t_RPAR = '\\)'
    t_EQ = '='
    t_SEMI = ';'
    t_ignore = ' \t\f'

    def t_NAME(self, t):
        '[A-Za-z_$][A-Za-z0-9_$]*'
        if t.value in ProtobufLexer.keywords:
            t.type = t.value.upper()
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_newline2(self, t):
        r'(\r\n)+'
        t.lexer.lineno += len(t.value) / 2

    def t_error(self, t):
        print("Illegal character '{}' ({}) in line {}".format(t.value[0], hex(ord(t.value[0])), t.lexer.lineno))
        t.lexer.skip(1)

class ProtobufParser(object):
    tokens = ProtobufLexer.tokens

    def p_empty(self, p):
        '''empty :'''
        pass

    def p_field_modifier(self,p):
        '''field_modifier : REQUIRED
                          | OPTIONAL
                          | REPEATED'''
        p[0] = p[1]

    def p_primitive_type(self, p):
        '''primitive_type : DOUBLE
                          | FLOAT
                          | INT32
                          | INT64
                          | UINT32
                          | UINT64
                          | SINT32
                          | SINT64
                          | FIXED32
                          | FIXED64
                          | SFIXED32
                          | SFIXED64
                          | BOOL
                          | STRING
                          | BYTES'''
        p[0] = p[1]

    def p_field_id(self, p):
        '''field_id : NUM'''
        p[0] = p[1]

    def p_rvalue(self, p):
        '''rvalue : NUM
                  | TRUE
                  | FALSE'''
        p[0] = p[1]

    def p_rvalue2(self, p):
        '''rvalue : NAME'''
        p[0] = Name(p[1])

    def p_field_directive(self, p):
        '''field_directive : LBRACK NAME EQ rvalue RBRACK'''
        p[0] = FieldDirective(Name(p[2]), p[4])

    def p_field_directive_times(self, p):
        '''field_directive_times : field_directive_plus'''
        p[0] = p[1]

    def p_field_directive_times2(self, p):
        '''field_directive_times : empty'''
        p[0] = []

    def p_field_directive_plus(self, p):
        '''field_directive_plus : field_directive
                               | field_directive_plus field_directive'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_field_type(self, p):
        '''field_type : primitive_type'''
        p[0] = FieldType(p[1])

    def p_field_type2(self, p):
        '''field_type : NAME'''
        p[0] = Name(p[1])

    # Root of the field declaration.
    def p_field_definition(self, p):
        '''field_definition : field_modifier field_type NAME EQ field_id field_directive_times SEMI'''
        p[0] = FieldDefinition(p[1], p[2], Name(p[3]), p[5], p[6])

    # Root of the enum field declaration.
    def p_enum_field(self, p):
        '''enum_field : NAME EQ NUM SEMI'''
        p[0] = EnumFieldDefinition(Name(p[1]), p[3])

    def p_enum_body_part(self, p):
        '''enum_body_part : enum_field
                          | option_directive'''
        p[0] = p[1]

    def p_enum_body(self, p):
        '''enum_body : enum_body_part
                    | enum_body enum_body_part'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_enum_body_opt(self, p):
        '''enum_body_opt : empty'''
        p[0] = []

    def p_enum_body_opt2(self, p):
        '''enum_body_opt : enum_body'''
        p[0] = p[1]

    # Root of the enum declaration.
    # enum_definition ::= 'enum' ident '{' { ident '=' integer ';' }* '}'
    def p_enum_definition(self, p):
        '''enum_definition : ENUM NAME LBRACE enum_body_opt RBRACE'''
        p[0] = EnumDefinition(Name(p[2]), p[4])

    def p_extensions_to(self, p):
        '''extensions_to : MAX'''
        p[0] = ExtensionsMax()

    def p_extensions_to2(self, p):
        '''extensions_to : NUM'''
        p[0] = p[1]

    # extensions_definition ::= 'extensions' integer 'to' integer ';'
    def p_extensions_definition(self, p):
        '''extensions_definition : EXTENSIONS NUM TO extensions_to SEMI'''
        p[0] = ExtensionsDirective(p[2], p[4])

    # message_extension ::= 'extend' ident '{' message_body '}'
    def p_message_extension(self, p):
        '''message_extension : EXTEND NAME LBRACE message_body RBRACE'''
        p[0] = MessageExtension(Name(p[2]), p[4])

    def p_message_body_part(self, p):
        '''message_body_part : field_definition
                           | enum_definition
                           | message_definition
                           | extensions_definition
                           | message_extension'''
        p[0] = p[1]

    # message_body ::= { field_definition | enum_definition | message_definition | extensions_definition | message_extension }*
    def p_message_body(self, p):
        '''message_body : empty'''
        p[0] = []

    # message_body ::= { field_definition | enum_definition | message_definition | extensions_definition | message_extension }*
    def p_message_body2(self, p):
        '''message_body : message_body_part
                      | message_body message_body_part'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    # Root of the message declaration.
    # message_definition = MESSAGE_ - ident("messageId") + LBRACE + message_body("body") + RBRACE
    def p_message_definition(self, p):
        '''message_definition : MESSAGE NAME LBRACE message_body RBRACE'''
        p[0] = MessageDefinition(Name(p[2]), p[4])

    # method_definition ::= 'rpc' ident '(' [ ident ] ')' 'returns' '(' [ ident ] ')' ';'
    def p_method_definition(self, p):
        '''method_definition : RPC NAME LPAR NAME RPAR RETURNS LPAR NAME RPAR'''
        p[0] = MethodDefinition(Name(p[2]), Name(p[4]), Name(p[8]))

    def p_method_definition_opt(self, p):
        '''method_definition_opt : empty'''
        p[0] = []

    def p_method_definition_opt2(self, p):
        '''method_definition_opt : method_definition
                          | method_definition_opt method_definition'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    # service_definition ::= 'service' ident '{' method_definition* '}'
    # service_definition = SERVICE_ - ident("serviceName") + LBRACE + ZeroOrMore(Group(method_definition)) + RBRACE
    def p_service_definition(self, p):
        '''service_definition : SERVICE NAME LBRACE method_definition_opt RBRACE'''
        p[0] = ServiceDefinition(Name(p[2]), p[4])

    # package_directive ::= 'package' ident [ '.' ident]* ';'
    def p_package_directive(self,p):
        '''package_directive : PACKAGE NAME SEMI'''
        p[0] = PackageStatement(Name(p[2]))

    # import_directive = IMPORT_ - quotedString("importFileSpec") + SEMI
    def p_import_directive(self, p):
        '''import_directive : IMPORT STRING_LITERAL SEMI'''
        p[0] = ImportStatement(Literal(p[2]))

    def p_option_rvalue(self, p):
        '''option_rvalue : NUM
                         | TRUE
                         | FALSE'''
        p[0] = p[1]

    def p_option_rvalue2(self, p):
        '''option_rvalue : STRING_LITERAL'''
        p[0] = Literal(p[1])

    # option_directive = OPTION_ - ident("optionName") + EQ + quotedString("optionValue") + SEMI
    def p_option_directive(self, p):
        '''option_directive : OPTION NAME EQ option_rvalue SEMI'''
        p[0] = OptionStatement(Name(p[2]), p[4])

    # topLevelStatement = Group(message_definition | message_extension | enum_definition | service_definition | import_directive | option_directive)
    def p_topLevel(self,p):
        '''topLevel : message_definition
                    | message_extension
                    | enum_definition
                    | service_definition
                    | import_directive
                    | option_directive'''
        p[0] = p[1]

    def p_package_definition(self, p):
        '''package_definition : package_directive'''
        p[0] = p[1]

    def p_packages2(self, p):
        '''package_definition : empty'''
        p[0] = []

    def p_statements2(self, p):
        '''statements : topLevel
                      | statements topLevel'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_statements(self, p):
        '''statements : empty'''
        p[0] = []

    # parser = Optional(package_directive) + ZeroOrMore(topLevelStatement)
    def p_goal2(self, p):
        '''goal : package_definition statements'''
        p[0] = [p[1], p[2]]

    def p_error(self, p):
        print('error: {}'.format(p))

class ProtobufAnalyzer(object):

    def __init__(self):
        self.lexer = lex.lex(module=ProtobufLexer(), optimize=1)
        self.parser = yacc.yacc(module=ProtobufParser(), start='goal', optimize=1)

    def tokenize_string(self, code):
        self.lexer.input(code)
        for token in self.lexer:
            print(token)

    def tokenize_file(self, _file):
        if type(_file) == str:
            _file = file(_file)
        content = ''
        for line in _file:
            content += line
        return self.tokenize_string(content)

    def parse_string(self, code, debug=0, lineno=1, prefix=''):
        self.lexer.lineno = lineno
        return self.parser.parse(prefix + code, lexer=self.lexer, debug=debug)

    def parse_file(self, _file, debug=0):
        if type(_file) == str:
            _file = file(_file)
        content = ''
        for line in _file:
            content += line
        return self.parse_string(content, debug=debug)
