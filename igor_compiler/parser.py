import json, traceback
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

class Type():
    grammar = attr("value", [SimpleType, ListType, VarType])
    def build(self):
        return self.value.build()

ListType.grammar = "list", "<", attr("item_type", Type), ">"

class EnumItem():
    grammar = selfdesc, selfname, ";"
    def build(self):
        return {
            'description': getdesc(self.desc),
            'name': self.name
        }
    
class Enum(List):
    grammar = selfdesc, "enum", selfname, "{", maybe_some(EnumItem), "}"
    def build(self):
        return {
            'tag': 'enum',
            'description': getdesc(self.desc),
            'name': self.name,
            'items': [a.build() for a in self]
        }

class RecordItem():
    grammar = selfdesc, flag("optional", "?"), attr('type', Type), selfname, ";"
    def build(self):
        return {
            'name': self.name,
            'description': getdesc(self.desc),
            'type': self.type.build(),
            'optional': self.optional
        }

class Record(List):
    grammar = selfdesc, "record", selfname, "{",  maybe_some(RecordItem), "}"
    def build(self):
        return {
            'tag': 'record',
            'description': getdesc(self.desc),
            'name': self.name,
            'items': [a.build() for a in self]
        }

class ServiceMethod():
    grammar = "method", attr("method", MethodType), ";"
    
class ServiceParam():
    grammar = selfdesc, "param", attr("type", SimpleType), selfname, ";"
    def build(self):
        return {
            'name': self.name,
            'description': getdesc(self.desc),
            'type': self.type.build()
        }
    
class ServiceQuery():
    grammar = selfdesc, "query", attr("type", SimpleType), selfname, ";"
    def build(self):
        return {
            'name': self.name,
            'description': getdesc(self.desc),
            'type': self.type.build()
        }
    
class ServiceUrl(List):
    grammar = "url", some([Urlname, Urlparam]), ";"

class ServiceBody():
    grammar = "body", attr("type", Type), ";"
    
class ServiceResponse():
    grammar = selfdesc, "response", attr("status", Number), attr("type", Type), ";"
    def build(self):
        return {
            'status': self.status,
            'description': getdesc(self.desc),
            'type': self.type.build()
        }
    
class Service(List):
    grammar = selfdesc, "service", selfname, "{",  maybe_some([ServiceMethod, ServiceUrl, ServiceParam, ServiceQuery, ServiceBody, ServiceResponse]), "}"
    
    def filter_one(self, childType):
        for a in self:
            if type(a) is childType:
                return a
        return None

    def filter_build(self, childType):
        return [a.build() for a in self if type(a) is childType]
    
    def build(self):
        body = self.filter_one(ServiceBody)
        return {
            'tag': 'service',
            'description': getdesc(self.desc),
            'name': self.name,
            'method': self.filter_one(ServiceMethod).method.name,
            'url': [a.build() for a in self.filter_one(ServiceUrl)],
            'body': body.type.build() if body else None,
            'query': self.filter_build(ServiceQuery),
            'params': self.filter_build(ServiceParam),
            'responses': self.filter_build(ServiceResponse),
        }

class Definition():
    grammar = attr("value", [Enum, Record, Service])
    def build(self):
        return self.value.build()
    
class File(List):
    grammar = maybe_some(Definition)
    def build(self):
        return [a.build() for a in self]

class IgorParser:
    def __init__(self):
        self.error = None
        self.data = None
    
    def parse(self, filename):
        try:
            text = read_file(filename)
            self.data = parse(text, File).build()
            return True
        except SyntaxError as err:
            self.error = err
            return False

    def save(self, path, compact=False):
        write_file(path, json2str(self.data, compact))
    
    def print_error(self):
        print('line: ' + str(err.lineno))
        print('position: ' + str(err.offset))
        print('text: ' + str(err.text))
        print('error: ' + str(err.msg))
        
