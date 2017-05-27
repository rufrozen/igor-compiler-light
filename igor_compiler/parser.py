import json, traceback, inflection
from pypeg2 import *
from .utils import *

# pip install pypeg2

class Number(int):
    regex = re.compile(r"[0-9]+")

class Varname(str):
    regex = re.compile(r"[a-zA-Z_][a-zA-Z_0-9]*")
    
selfname = attr("name", Varname)

class Urlname():
    grammar = attr("name", re.compile(r"[a-zA-Z0-9_/-]+"))
    def build(self):
        return {
            'tag': 'url',
            'url': self.name,
        }
    
class Urlparam():
    grammar = "{", selfname,"}"
    def build(self):
        return {
            'tag': 'param',
            'param': self.name,
        }

class DescriptionOld():
    grammar = attr("name", re.compile(r"(?m)\[.*?\]", flags=re.S))
    
class Description():
    grammar = attr("name", re.compile(r"\#.*"))
    
selfdesc = attr("desc", optional(Description))
def getdesc(desc): return desc.name[1:] if desc else ""

class DefaultValue(int):
    grammar = "=", Number

class MethodType(Keyword):
    grammar = Enum( K("POST"), K("GET"), K("PUT"), K("DELETE") )

class SimpleType(Keyword):
    grammar = Enum( K("number"), K("int"), K("string"), K("bool"), K("json"), K("Date") )
    def build(self):
        return {
            'tag': self.name,
        }

class VarType():
    grammar = selfname
    def build(self):
        return {
            'tag': 'ref',
            'ref': self.name,
        }
        
class ListType():    
    def build(self):
        return {
            'tag': 'list',
            'item_type': self.item_type.build(),
        }
    
class DictType():    
    def build(self):
        return {
            'tag': 'dict',
            'value_type': self.value_type.build(),
        }
    
class Type():
    grammar = attr("value", [SimpleType, ListType, DictType, VarType])
    @property
    def name(self): return self.value.name
    def build(self):
        return self.value.build()

ListType.grammar = "list", "<", attr("item_type", Type), ">"
DictType.grammar = "dict", "<", "string", ",", attr("value_type", Type), ">"

class EnumItem():
    grammar = selfdesc, optional(attr("ref", Varname), "."), selfname, ";"
    def build(self, context):
        return {
            'description': getdesc(self.desc),
            'name': self.name,
            'ref': self.ref if hasattr(self, 'ref') else None
        }

class EnumBody(List):
    grammar = "{", maybe_some(EnumItem), "}"
    def build(self, context):
        return [a.build(context) for a in self]

class Enum:
    grammar = selfdesc, "enum", selfname, attr("items", EnumBody)
    def collect(self, context):
        context.add({
            'tag': 'enum',
            'description': getdesc(self.desc),
            'name': self.name,
            'items': self.items.build(context)
        })

class RecordItem():
    grammar = selfdesc, flag("property", "@"), flag("optional", "?"), attr('type', Type), selfname, ";"
    def build(self, context):
        return {
            'name': self.name,
            'description': getdesc(self.desc),
            'type': self.type.build(),
            'optional': self.optional,
            'property': self.property
        }

def make_name(data):
    return inflection.camelize('_'.join(data))

class RecordInlineEnum():
    grammar = selfdesc, "enum", flag("property", "@"), flag("optional", "?"), selfname, attr("items", EnumBody)
    def fullname(self, context):
        return make_name(context.record_name + [self.name, 'enum'])
    def collect(self, context):
        context.add({
            'tag': 'enum',
            'description': getdesc(self.desc),
            'name': self.fullname(context),
            'items': self.items.build(context)
        })

    def build(self, context):
        self.collect(context)
        return {
            'name': self.name,
            'description': getdesc(self.desc),
            'type': {
                'tag': 'ref',
                'ref': self.fullname(context),
            },
            'optional': self.optional,
            'property': self.property
        }
    
class RecordBody(List):
    grammar = "{",  maybe_some([RecordItem, RecordInlineEnum]), "}"
    def build(self, context):
        return [a.build(context) for a in self]

class Record(List):
    grammar = selfdesc, "record", selfname, attr("items", RecordBody)
    def collect(self, context):
        context.record_name = [self.name]
        context.add({
            'tag': 'record',
            'description': getdesc(self.desc),
            'name': make_name(context.record_name),
            'items': self.items.build(context)
        })
        context.record_name = []

class ServiceMethod():
    grammar = "method", attr("method", MethodType), ";"
    def build(self, context):
        return self.method.name
    
class ServiceParam():
    grammar = selfdesc, "param", attr("type", SimpleType), selfname, ";"
    def build(self, context):
        return {
            'name': self.name,
            'description': getdesc(self.desc),
            'type': self.type.build()
        }
    
class ServiceQuery():
    grammar = selfdesc, "query", attr("type", [SimpleType, VarType]), selfname, ";"
    def build(self, context):
        return {
            'name': self.name,
            'description': getdesc(self.desc),
            'type': self.type.build()
        }
    
class ServiceUrl(List):
    grammar = "url", some([Urlname, Urlparam]), ";"
    def build(self, context):
        return [a.build() for a in self]
    
class ServiceInline():
    grammar = attr("type", Type), ";"
    def build(self, context):
        return self.type.build()

class ServiceRecordInline():
    grammar = "record", attr("items", RecordBody)
    def collect(self, context):
        context.add({
            'tag': 'record',
            'description': '',
            'name': make_name(context.record_name),
            'items': self.items.build(context)
        })
    def build(self, context):
        self.collect(context)
        return {
            'tag': 'ref',
            'ref': make_name(context.record_name)
        }

class ServiceBody():
    grammar = "body", attr("data", [ServiceRecordInline, ServiceInline])
    def build(self, context):
        context.record_name = [context.service_name, 'request', 'body']
        res = self.data.build(context);
        context.record_name = []
        return res
        
class ServiceResponse():
    grammar = selfdesc, "response", attr("status", Number), attr("data", [ServiceRecordInline, ServiceInline])
    def build(self, context):
        context.record_name = [context.service_name, 'response', str(self.status)]
        res = {
            'status': self.status,
            'description': getdesc(self.desc),
            'type': self.data.build(context)
        }
        context.record_name = []
        return res
    
class Service(List):
    grammar = selfdesc, "service", selfname, "{",  maybe_some([ServiceMethod, ServiceUrl, ServiceParam, ServiceQuery, ServiceBody, ServiceResponse]), "}"
    
    def filter_one_build(self, context, childType):
        for a in self:
            if type(a) is childType:
                return a.build(context)
        return None

    def filter_build(self, context, childType):
        return [a.build(context) for a in self if type(a) is childType]
    
    def collect(self, context):
        context.service_name = self.name
        context.add({
            'tag': 'service',
            'description': getdesc(self.desc),
            'name': self.name,
            'method': self.filter_one_build(context, ServiceMethod),
            'url': self.filter_one_build(context, ServiceUrl),
            'body': self.filter_one_build(context, ServiceBody),
            'query': self.filter_build(context, ServiceQuery),
            'params': self.filter_build(context, ServiceParam),
            'responses': self.filter_build(context, ServiceResponse),
        })
        context.service_name = None
        

class Definition():
    grammar = attr("value", [Enum, Record, Service])
    def collect(self, context):
        self.value.collect(context)
    
class File(List):
    grammar = maybe_some(Definition)
    def collect(self, context):
        for a in self:
            a.collect(context)

class IgorParser:
    def __init__(self):
        self.error = None
        self.data = None
        self.record_name = []
        self.service_name = None

    def add(self, item):
        self.data.append(item)
    
    def parse(self, filename):
        try:
            self.error = None
            self.data = []
            text = read_file(filename)
            parse(text, File, comment=comment_cpp).collect(self)
            return True
        except SyntaxError as err:
            self.error = err
            return False
    
    def print_error(self):
        print('line: ' + str(self.error.lineno))
        print('position: ' + str(self.error.offset))
        print('text: ' + str(self.error.text))
        print('error: ' + str(self.error.msg))
        
