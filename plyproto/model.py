__author__ = "Dusan (Ph4r05) Klinec"
__copyright__ = "Copyright (C) 2014 Dusan (ph4r05) Klinec"
__license__ = "Apache License, Version 2.0"
__version__ = "1.0"

# Base node
class SourceElement(object):
    '''
    A SourceElement is the base class for all elements that occur in a Java
    file parsed by plyj.
    '''
    def __init__(self):
        super(SourceElement, self).__init__()
        self._fields = []

    def __repr__(self):
        equals = ("{0}={1!r}".format(k, getattr(self, k))
                  for k in self._fields)
        args = ", ".join(equals)
        return "{0}({1})".format(self.__class__.__name__, args)

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def accept(self, visitor):
        pass

class PackageDeclaration(SourceElement):
    def __init__(self, name):
        super(PackageDeclaration, self).__init__()
        self._fields = ['name']
        self.name = name

    def accept(self, visitor):
        visitor.visit_PackageDeclaration(self)

class ImportStatement(SourceElement):
    def __init__(self, name):
        super(ImportStatement, self).__init__()
        self._fields = ['name']
        self.name = name

    def accept(self, visitor):
        visitor.visit_ImportStatement(self)

class OptionDefinition(SourceElement):
    def __init__(self, name, value):
        super(OptionDefinition, self).__init__()
        self._fields = ['name', 'value']
        self.name = name
        self.value = value

    def accept(self, visitor):
        visitor.visit_OptionDefinition(self)

class FieldDirectiveDeclaration(SourceElement):
    def __init__(self, name, value):
        super(FieldDirectiveDeclaration, self).__init__()
        self._fields = ['name', 'value']
        self.name = name
        self.value = value

    def accept(self, visitor):
        visitor.visit_FieldDirectiveDeclaration(self)

class FieldPrimitiveType(SourceElement):
    def __init__(self, name):
        super(FieldPrimitiveType, self).__init__()
        self._fields = ['name']
        self.name = name

    def accept(self, visitor):
        visitor.visit_FieldPrimitiveType(self)

class FieldDeclaration(SourceElement):
    def __init__(self, field_modifier, ftype, name, fieldId, fieldDirective):
        super(FieldDeclaration, self).__init__()
        self._fields = ['field_modifier', 'ftype', 'name', 'fieldId', 'fieldDirective']
        self.name = name
        self.field_modifier = field_modifier
        self.ftype = ftype
        self.fieldId = fieldId
        self.fieldDirective = fieldDirective

    def accept(self, visitor):
        visitor.visit_FieldDeclaration(self)

class EnumFieldDeclaration(SourceElement):
    def __init__(self, name, fieldId):
        super(EnumFieldDeclaration, self).__init__()
        self._fields = ['name', 'fieldId']
        self.name = name
        self.fieldId = fieldId

    def accept(self, visitor):
        visitor.visit_EnumFieldDeclaration(self)

class EnumDeclaration(SourceElement):
    def __init__(self, name, body):
        super(EnumDeclaration, self).__init__()
        self._fields = ['name', 'body']
        self.name = name
        self.body = body

    def accept(self, visitor):
        if visitor.visit_EnumDeclaration(self):
            for s in self.body:
                s.accept(visitor)

class MessageDeclaration(SourceElement):
    def __init__(self, name, body):
        super(MessageDeclaration, self).__init__()
        self._fields = ['name', 'body']
        self.name = name
        self.body = body

    def accept(self, visitor):
        if visitor.visit_MessageDeclaration(self):
            for s in self.body:
                s.accept(visitor)

class MessageExtension(SourceElement):
    def __init__(self, name, body):
        super(MessageExtension, self).__init__()
        self._fields = ['name', 'body']
        self.name = name
        self.body = body

    def accept(self, visitor):
        if visitor.visit_MessageExtension(self):
            for s in self.body:
                s.accept(visitor)

class MethodDefinition(SourceElement):
    def __init__(self, name, name2, name3):
        super(MethodDefinition, self).__init__()
        self._fields = ['name', 'name2', 'name3']
        self.name = name
        self.name2 = name2
        self.name3 = name3

    def accept(self, visitor):
        visitor.visit_MethodDefinition(self)

class ServiceDeclaration(SourceElement):
    def __init__(self, name, body):
        super(ServiceDeclaration, self).__init__()
        self._fields = ['name', 'body']
        self.name = name
        self.body = body

    def accept(self, visitor):
        if visitor.visit_ServiceDeclaration(self):
            for s in self.body:
                s.accept(visitor)

class ExtensionsMax(SourceElement):
    pass

class ExtensionsDirective(SourceElement):
    def __init__(self, fromVal, toVal):
        super(ExtensionsDirective, self).__init__()
        self._fields = ['fromVal', 'toVal']
        self.fromVal = fromVal
        self.toVal = toVal

    def accept(self, visitor):
        visitor.visit_ExtensionsDirective(self)

class Literal(SourceElement):

    def __init__(self, value):
        super(Literal, self).__init__()
        self._fields = ['value']
        self.value = value

    def accept(self, visitor):
        visitor.visit_Literal(self)

class Name(SourceElement):

    def __init__(self, value):
        super(Name, self).__init__()
        self._fields = ['value']
        self.value = value

    def append_name(self, name):
        try:
            self.value = self.value + '.' + name.value
        except:
            self.value = self.value + '.' + name

    def accept(self, visitor):
        visitor.visit_Name(self)


class Visitor(object):

    def __init__(self, verbose=False):
        self.verbose = verbose

    def __getattr__(self, name):
        if not name.startswith('visit_'):
            raise AttributeError('name must start with visit_ but was {}'
                                 .format(name))

        def f(element):
            if self.verbose:
                msg = 'unimplemented call to {}; ignoring ({})'
                print(msg.format(name, element))
            return True
        return f
