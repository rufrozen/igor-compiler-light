import json, inflection, io, os
from .utils import *

# pip install inflection

header = '''
function listFromJson<T>(json: any, fromJson: (json: any) => T)
{
    return (<Array<Object>>json).map(fromJson);
}

function listToJson<T>(data: T[], toJson: (data: T) => any)
{
    return data.map(toJson);
}

function dictToJson<T>(data: {[key: string]: T}, toJson: (data: T) => any)
{
    let res: Object = {};
    for (let key in data)
        res[key] = toJson(data[key]);
    return res
}

function dictFromJson<T>(json: any, fromJson: (json: any) => T)
{
    let res: {[key: string]: T} = {};
    let src = <Object>json;
    for (let key in src)
        res[key] = fromJson(src[key]);
    return res
}

function jsonHasValue(json: Object, key: string)
{
    return key in json && json[key] != null;
}

function dictClone<T>(data: {[key: string]: T}, copy: (data: T) => T)
{
    let res: {[key: string]: T} = {};
    for (let key in data)
        res[key] = copy(data[key]);
    return res
}

function listClone<T>(data: T[], copy: (data: T) => T)
{
    return data.map(copy);
}

function stringClone(str: string)
{
    return (' ' + str).slice(1);
}

function jsonClone(json: any)
{
    return JSON.parse(JSON.stringify(json));
}

function dateClone(date: Date)
{
    return new Date(date.getTime());
}
'''

def wrap(text, border="'"):
    return border + text + border

def offset(count, text):
    return '\n'.join([spaces(count) + a for a in text.split('\n')])

def spaces(count):
    if count > 0: return '    ' + spaces(count - 1)
    else: return ''

def load(path):
    with open(path, 'r', encoding='utf8') as f:
        return json.loads(f.read())

def save(path, text):
    with open(path, 'w', encoding='utf8') as f:
        f.write(text)

global_prefix = ''
global_enums = {}
global_records = {}
global_varname = 0
    
class Type:
    def __init__(self, schema, index = 1):
        self.schema = schema
        self.index = index;

    @property
    def is_ref(self): return self.tag == 'ref'
    
    @property
    def is_list(self): return self.tag == 'list'
    
    @property
    def is_dict(self): return self.tag == 'dict'
    
    @property
    def is_enum(self): return self.is_ref and self.ref in global_enums
    
    @property
    def is_record(self): return self.is_ref and self.ref in global_records
    
    @property
    def is_simple(self):
        return self.tag in ['number', 'int', 'string', 'bool', 'json', 'Date']
       
    @property
    def tag(self): return self.schema['tag']
    
    @property
    def ref(self): return self.schema['ref']
    
    @property
    def fullref(self): return global_prefix + self.schema['ref']
    
    @property
    def item_type(self):
        return Type(self.schema['item_type'], self.index + 1)
    
    @property
    def value_type(self):
        return Type(self.schema['value_type'], self.index + 1)
    
    @property
    def param_name(self):
        return 'el' + str(self.index)
    
    @property
    def declaration(self):
        if self.is_ref: return self.fullref
        elif self.is_list: return 'Array<' + self.item_type.declaration + '>'
        elif self.is_dict: return '{[key: string]: ' + self.value_type.declaration + '}'
        elif self.tag == 'json': return 'any'
        elif self.tag == 'int': return 'number'
        elif self.tag == 'bool': return 'boolean'
        elif self.tag == 'Date': return 'Date'
        elif self.is_simple: return self.tag
        else: raise GenerationError('unknown type ' + self.tag)

    def clone(self, var):
        if self.is_record: return var + ".clone()"
        elif self.is_list:
            el = self.param_name
            return "listClone({var}, {el} => {item})".format(el=el, var=var, item=self.item_type.clone(el))
        elif self.is_dict:
            el = self.param_name
            return "dictClone({var}, {el} => {item})".format(el=el, var=var, item=self.value_type.clone(el))
        elif self.tag == 'Date': return "dateClone({var})".format(var=var)
        elif self.tag == 'json': return "jsonClone({var})".format(var=var)
        elif self.tag == 'string': return "stringClone({var})".format(var=var)
        else:
            return var

    def from_json(self, json):
        if self.is_record: return "{s.fullref}.fromJson({json})".format(s=self, json=json)
        elif self.is_enum: return "{s.fullref}FromString({json})".format(s=self, json=json)
        elif self.is_list:
            el = self.param_name
            return "listFromJson({json}, {el} => {item})".format(json=json, el=el, item=self.item_type.from_json(el))
        elif self.is_dict:
            el = self.param_name
            return "dictFromJson({json}, {el} => {item})".format(json=json, el=el, item=self.value_type.from_json(el))
        elif self.tag == 'Date': return "new Date({json} * 1000)".format(json=json)
        elif self.is_simple: return "<{s.declaration}>{json}".format(s=self, json=json)
        else: raise GenerationError('unknown type ' + self.tag)

    
    def to_json(self, var):
        if self.is_record: return "{var}.toJson()".format(var=var)
        elif self.is_enum: return "{s.fullref}ToString({var})".format(s=self, var=var)
        elif self.is_list:
            el = self.param_name
            return "listToJson({var}, {el} => {item})".format(var=var, el=el, item=self.item_type.to_json(el))
        elif self.is_dict:
            el = self.param_name
            return "dictToJson({var}, {el} => {item})".format(var=var, el=el, item=self.value_type.to_json(el))
        elif self.tag == 'Date': return "Math.ceil({var}.getTime() / 1000)".format(var=var)
        elif self.is_simple: return var
        else: raise GenerationError('unknown type ' + self.tag)

def enum_item_desc(data):
    ref = data['ref']
    if ref != None:
        return global_enums[ref].item_desc(data['name'])
    return data['description']

def enum_item(data):
    return spaces(1) + inflection.camelize(data['name']) + ', // ' + enum_item_desc(data)

class Enum:
    def __init__(self, schema):
        self.schema = schema
        global_enums[self.name] = self
        
    @property
    def name(self): return self.schema['name']
    
    @property
    def desc(self): return self.schema['description']
    
    @property
    def items(self): return self.schema['items']
    
    @property
    def items_name(self): return [a['name'] for a in self.items]
    
    @property
    def items_desc(self): return [enum_item_desc(a) for a in self.items]
    
    def item_desc(self, item):
        for a in self.items:
            if a['name'] == item:
                return enum_item_desc(a)
        raise GenerationError("enum " + self.name + " doesn't have item " + item)
    
    @property
    def delcaration(self):
        return '\n'.join([enum_item(v) for v in self.items])
    
    @property
    def to_desc(self):
        return ',\n'.join([spaces(2) + wrap(v.replace("'", "\\'").strip()) for v in self.items_desc])
    
    @property
    def to_json(self):
        return ',\n'.join([spaces(2) + wrap(v) for v in self.items_name])
    
    @property
    def from_json(self):
        frm = "case '{j}': return {n}.{v};"
        return '\n'.join([spaces(2) + frm.format(v=inflection.camelize(v),j=v,n=self.name) for v in self.items_name])
    
    def generate(self):
        return '''
// {s.desc}
export const enum {s.name}
{{
    Null,
{s.delcaration}
}}
export function {s.name}ToString(val: {s.name})
{{
    let arr = [
        null,
{s.to_json}
    ];
    return arr[val]
}}
export function {s.name}FromString(json: string)
{{
    switch(json)
    {{
{s.from_json}
        default: return {s.name}.Null;
    }}
}}
export function {s.name}ToDescription(val: {s.name})
{{
    let arr = [
        null,
{s.to_desc}
    ];
    return arr[val]
}}
'''.format(s=self)

class Property:
    def __init__(self, schema):
        self.schema = schema

    @property
    def name(self): return self.schema['name']
    
    @property
    def desc(self): return self.schema['description']
    
    @property
    def optional(self): return self.schema['optional']
    
    @property
    def is_property(self): return self.schema['property']

    @property
    def has_varname(self):
        return '_has_' + self.varname
    
    @property
    def private_varname(self):
        return '_' + self.varname
    
    @property
    def varname(self):
        return inflection.camelize(self.name, False)
        
    @property
    def vartype(self): return Type(self.schema['type'])

    @property
    def vartype_delcaration(self):
        if self.optional:
            return self.vartype.declaration + ' | null'
        else:
            return self.vartype.declaration

    @property
    def delcaration(self):
        if self.is_property:
            var = "private {s.private_varname}: {s.vartype_delcaration}; // {s.desc}".format(s=self)
            has = "private {s.has_varname}: boolean = false;".format(s=self)
            get = "get {s.varname}() : {s.vartype_delcaration} {{ return this.{s.private_varname}; }}".format(s=self)
            set = "set {s.varname}(val : {s.vartype_delcaration}) {{ this.{s.private_varname} = val; this.{s.has_varname} = true; }}".format(s=self)
            return [var, has, get, set]
        else:
            res = "{s.varname}: {s.vartype_delcaration}; // {s.desc}".format(s=self)
            return [res]
        
    @property
    def clone_src(self):
        return self.vartype.clone("this." + self.varname)

    def clone(self):
        if self.optional:
            return "res.{s.varname} = this.{s.varname} == null ? null : {s.clone_src};".format(s=self)
        else:
            return "res.{s.varname} = {s.clone_src};".format(s=self)
    
    @property
    def json_src(self): return "json['{s.name}']".format(s=self)

    @property
    def var_src(self): return "this.{s.varname}".format(s=self)
    
    @property
    def type_to_json(self): return self.vartype.to_json(self.var_src)
    
    @property
    def type_from_json(self): return self.vartype.from_json(self.json_src)
    
    def from_json(self):
        if self.optional:
            return "obj.{s.varname} = jsonHasValue(json, '{s.name}') ? {s.type_from_json} : null;".format(s=self)
        else:
            return "obj.{s.varname} = {s.type_from_json};".format(s=self)           
        
    def to_json(self):
        if self.optional:
            return "'{s.name}': {s.var_src} == null ? null : {s.type_to_json},".format(s=self)
        else:
            return "'{s.name}': {s.type_to_json},".format(s=self)

    def property_to_json(self):
        prefix = "if (this.{s.has_varname}) obj['{s.name}'] = "
        if self.optional:
            return (prefix + "{s.var_src} == null ? null : {s.type_to_json};").format(s=self)
        else:
            return (prefix + "{s.type_to_json};").format(s=self)

class Record:
    def __init__(self, schema):
        self.schema = schema
        global_records[self.name] = self

    @property
    def name(self): return self.schema['name']
    
    @property
    def desc(self): return self.schema['description']
    
    @property
    def items(self): return [Property(a) for a in self.schema['items']]
    
    @property
    def delcaration(self):
        return '\n'.join([spaces(1) + d for p in self.items for d in p.delcaration])

    @property
    def clone(self):
        return '\n'.join([spaces(2) + p.clone() for p in self.items]) 
    
    @property
    def from_json(self):
        return '\n'.join([spaces(2) + p.from_json() for p in self.items])
    
    @property
    def to_json(self):
        return '\n'.join([spaces(3) + p.to_json() for p in self.items if not p.is_property])
    
    @property
    def property_to_json(self):
        return '\n'.join([spaces(2) + p.property_to_json() for p in self.items if p.is_property])
    
    def generate(self):
        return '''
export class {s.name}
{{
{s.delcaration}
    
    static fromJson(json: Object): {s.name}
    {{
        let obj = new {s.name}();
{s.from_json}
        return obj;
    }}

    toJson(): Object
    {{
        let obj: Object =
        {{
{s.to_json}
        }};
{s.property_to_json}
        return obj;
    }}

    clone(): {s.name}
    {{
        let res = new {s.name}();
{s.clone}
        return res;
    }}
}}
'''.format(s=self)

def url_text(url):
    if url['tag'] == 'url': return wrap(url['url'])
    else: return inflection.camelize(url['param'], False) + ".toString()"

def query_text(schema):
    type = Type(schema['type'])
    name = schema['name']
    var = inflection.camelize(name, False)
    return wrap(name) + ': ' + type.to_json(var)

class Service:
    def __init__(self, schema):
        self.schema = schema

    @property
    def method(self): return self.schema['method'].lower()

    @property
    def name(self): return inflection.camelize(self.schema['name'], False)
    
    @property
    def has_body(self): return self.schema['body'] != None
    
    @property
    def desc(self):
        return '\n'.join([spaces(1) + '// ' + a for a in self.schema['description'].split('\n')])
    
    @property
    def url(self):
        return ' + '.join([url_text(a) for a in self.schema['url']])

    @property
    def query(self):
        return '{' + ', '.join([query_text(p) for p in self.schema['query']]) + '}';
    
    @property
    def fun_name(self):
        base = self.name[1:].replace('/', '_').replace('-', '_').replace(':', '')
        return self.method + inflection.camelize(base)
    
    @property
    def fun_args(self):
        args = []
        for p in (self.schema['params'] + self.schema['query']):
            vartype = Type(p['type'])
            args.append(inflection.camelize(p['name'], False) + ': ' + vartype.declaration)
        if self.has_body:
            vartype = Type(self.schema['body'])
            args.append('body: ' + vartype.declaration)
        return ', '.join(args)
    
    @property
    def call_args(self):
        args = [self.url, self.query]
        if self.method != 'get':
            if self.has_body:
                vartype = Type(self.schema['body'])
                args.append(vartype.to_json('body'))
            else:
                args.append('{}')
        return ', '.join(args)

    def find_response_200(self):
        for v in self.schema['responses']:
            if v['status'] == 200:
                return v
        raise GenerationError('empty_200_reply')

    def response_type(self):
        return Type(self.find_response_200()['type'])

    @property
    def response_declaration(self):
        return self.response_type().declaration
        
    @property
    def response_ok(self):
        vartype = self.response_type()
        return vartype.from_json('response.json()')
    
    def response_error(self, schema):
        s = schema['status']
        r = Type(schema['type']).from_json('response.json()')
        return 'case {s}: return Observable.throw({r});'.format(s=s,r=r)
    
    @property
    def response_errors(self):
        return '\n'.join([spaces(5) + self.response_error(v) for v in self.schema['responses'] if v['status'] != 200])

    def generate(self):
        return '''
{s.desc}
    {s.name}({s.fun_args}): Observable<{s.response_declaration}>
    {{
        return this.{s.method}({s.call_args})
            .catch(response =>
            {{
                switch(response.status)
                {{
{s.response_errors}
                    default: return Observable.throw(response);
                }}
            }})
            .map(response => {s.response_ok});
    }}
'''.format(s=self)

def print_declarations(name, data):
    print(name + ': \n  ' + '\n  '.join([a.name for a in data]))

class IgorGeneratorTs:
    def __init__(self, schema):
        self.schema = schema
        self.services = [Service(a) for a in schema if a['tag'] == 'service']
        self.records = [Record(a) for a in schema if a['tag'] == 'record']
        self.enums = [Enum(a) for a in schema if a['tag'] == 'enum']
        print_declarations('Enums', self.enums)
        print_declarations('Records', self.records)
        print_declarations('Services', self.services)

    def requests(self):
        return ''.join([a.generate() for a in self.services])
    
    def generate_data(self):
        global global_prefix
        global_prefix = ''
        return header + ''.join([a.generate() for a in self.enums]) + ''.join([a.generate() for a in self.records])

    def generate_service(self):
        global global_prefix
        global_prefix = 'Protocol.'
        return '''
import {Observable} from "rxjs/Rx";
import {Response} from "@angular/http";
import * as Protocol from "./protocol.data"

export abstract class ProtocolService
{
    constructor() { }

    abstract get(path: string, query: Object): Observable<Response>;
    abstract put(path: string, query: Object, body: Object): Observable<Response>;
    abstract delete(path: string, query: Object, body: Object): Observable<Response>;
    abstract post(path: string, query: Object, body: Object): Observable<Response>;
%requests%
}
'''.replace('%requests%', self.requests())
