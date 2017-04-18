
function arrayFromJson<T>(json: any, fromJson: (json: Object) => T)
{
    return (<Array<Object>>json).map(fromJson);
}

function jsonHasValue(json: Object, key: string)
{
    return key in json && json[key] != null;
}

export const enum SomeEnum
{
    Null,
    Val1,
    Val2
}
export function SomeEnumToString(val: SomeEnum)
{
    let arr = [
        null,
        'val1',
        'val2'
    ];
    return arr[val]
}
export function SomeEnumFromString(json: string)
{
    switch(json)
    {
        case 'val1': return SomeEnum.Val1;
        case 'val2': return SomeEnum.Val2;
        default: return SomeEnum.Null;
    }
}

export class RecordEmpty
{

    
    static fromJson(json: Object): RecordEmpty
    {
        let obj = new RecordEmpty();

        return obj;
    }

    toJson(): Object
    {
        let obj: Object =
        {

        }
        return obj;
    }
}

export class RecordSimple
{
    boolVal: boolean; // 
    strVal: string; // 
    intVal: number; //  cool number
    optInt: number | null; // 
    jsonNumber: number; // 
    rowJson: any; // 
    
    static fromJson(json: Object): RecordSimple
    {
        let obj = new RecordSimple();
        obj.boolVal = <boolean>json['bool_val'];
        obj.strVal = <string>json['str_val'];
        obj.intVal = <number>json['int_val'];
        obj.optInt = jsonHasValue(json, 'opt_int') ? <number>json['opt_int'] : null;
        obj.jsonNumber = <number>json['json_number'];
        obj.rowJson = <any>json['row_json'];
        return obj;
    }

    toJson(): Object
    {
        let obj: Object =
        {
            'bool_val': this.boolVal,
            'str_val': this.strVal,
            'int_val': this.intVal,
            'opt_int': this.optInt == null ? null : this.optInt,
            'json_number': this.jsonNumber,
            'row_json': this.rowJson,
        }
        return obj;
    }
}

export class RecordComplex
{
    simple: RecordSimple; // 
    keys: Array<string>; // 
    enums: Array<SomeEnum>; // 
    someEnum: SomeEnum; // 
    customType: Date; // 
    
    static fromJson(json: Object): RecordComplex
    {
        let obj = new RecordComplex();
        obj.simple = RecordSimple.fromJson(json['simple']);
        obj.keys = arrayFromJson(json['keys'], el => <string>el);
        obj.enums = arrayFromJson(json['enums'], el => SomeEnumFromString(el));
        obj.someEnum = SomeEnumFromString(json['some_enum']);
        obj.customType = new Date(json['custom_type'] * 1000);
        return obj;
    }

    toJson(): Object
    {
        let obj: Object =
        {
            'simple': this.simple.toJson(),
            'keys': this.keys.map(el => el),
            'enums': this.enums.map(el => SomeEnumToString(el)),
            'some_enum': SomeEnumToString(this.someEnum),
            'custom_type': Math.ceil(this.customType.getTime() / 1000),
        }
        return obj;
    }
}
