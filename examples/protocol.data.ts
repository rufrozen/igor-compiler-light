
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

export const enum BigInnerRecord3
{
    Null,
    Data1,
    Data2
}
export function BigInnerRecord3ToString(val: BigInnerRecord3)
{
    let arr = [
        null,
        'data1',
        'data2'
    ];
    return arr[val]
}
export function BigInnerRecord3FromString(json: string)
{
    switch(json)
    {
        case 'data1': return BigInnerRecord3.Data1;
        case 'data2': return BigInnerRecord3.Data2;
        default: return BigInnerRecord3.Null;
    }
}

export const enum InlineRecordDeleteEnum
{
    Null,
    Type1,
    Type2
}
export function InlineRecordDeleteEnumToString(val: InlineRecordDeleteEnum)
{
    let arr = [
        null,
        'type1',
        'type2'
    ];
    return arr[val]
}
export function InlineRecordDeleteEnumFromString(json: string)
{
    switch(json)
    {
        case 'type1': return InlineRecordDeleteEnum.Type1;
        case 'type2': return InlineRecordDeleteEnum.Type2;
        default: return InlineRecordDeleteEnum.Null;
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
        obj.keys = listFromJson(json['keys'], el1 => <string>el1);
        obj.enums = listFromJson(json['enums'], el1 => SomeEnumFromString(el1));
        obj.someEnum = SomeEnumFromString(json['some_enum']);
        obj.customType = new Date(json['custom_type'] * 1000);
        return obj;
    }

    toJson(): Object
    {
        let obj: Object =
        {
            'simple': this.simple.toJson(),
            'keys': listToJson(this.keys, el1 => el1),
            'enums': listToJson(this.enums, el1 => SomeEnumToString(el1)),
            'some_enum': SomeEnumToString(this.someEnum),
            'custom_type': Math.ceil(this.customType.getTime() / 1000),
        }
        return obj;
    }
}

export class RecordSecond
{
    obj: RecordComplex; // 
    complexList: Array<Array<RecordComplex>>; // 
    simpleDict: {[key: string]: number}; // 
    complexDict: {[key: string]: Array<RecordComplex>}; // 
    
    static fromJson(json: Object): RecordSecond
    {
        let obj = new RecordSecond();
        obj.obj = RecordComplex.fromJson(json['obj']);
        obj.complexList = listFromJson(json['complex_list'], el1 => listFromJson(el1, el2 => RecordComplex.fromJson(el2)));
        obj.simpleDict = dictFromJson(json['simple_dict'], el1 => <number>el1);
        obj.complexDict = dictFromJson(json['complex_dict'], el1 => listFromJson(el1, el2 => RecordComplex.fromJson(el2)));
        return obj;
    }

    toJson(): Object
    {
        let obj: Object =
        {
            'obj': this.obj.toJson(),
            'complex_list': listToJson(this.complexList, el1 => listToJson(el1, el2 => el2.toJson())),
            'simple_dict': dictToJson(this.simpleDict, el1 => el1),
            'complex_dict': dictToJson(this.complexDict, el1 => listToJson(el1, el2 => el2.toJson())),
        }
        return obj;
    }
}

export class BigInnerRecord2
{
    result: boolean; // 
    dataEnum: BigInnerRecord3; // 
    
    static fromJson(json: Object): BigInnerRecord2
    {
        let obj = new BigInnerRecord2();
        obj.result = <boolean>json['result'];
        obj.dataEnum = BigInnerRecord3FromString(json['data_enum']);
        return obj;
    }

    toJson(): Object
    {
        let obj: Object =
        {
            'result': this.result,
            'data_enum': BigInnerRecord3ToString(this.dataEnum),
        }
        return obj;
    }
}

export class BigInnerRecord1
{
    dataRecord: BigInnerRecord2; // 
    value: number; // 
    dataOutsideEnum: BigInnerRecord3; // 
    
    static fromJson(json: Object): BigInnerRecord1
    {
        let obj = new BigInnerRecord1();
        obj.dataRecord = BigInnerRecord2.fromJson(json['data_record']);
        obj.value = <number>json['value'];
        obj.dataOutsideEnum = BigInnerRecord3FromString(json['data_outside_enum']);
        return obj;
    }

    toJson(): Object
    {
        let obj: Object =
        {
            'data_record': this.dataRecord.toJson(),
            'value': this.value,
            'data_outside_enum': BigInnerRecord3ToString(this.dataOutsideEnum),
        }
        return obj;
    }
}

export class InlineRecordDelete
{
    data: number; // 
    dataEnum: InlineRecordDeleteEnum; // 
    
    static fromJson(json: Object): InlineRecordDelete
    {
        let obj = new InlineRecordDelete();
        obj.data = <number>json['data'];
        obj.dataEnum = InlineRecordDeleteEnumFromString(json['data_enum']);
        return obj;
    }

    toJson(): Object
    {
        let obj: Object =
        {
            'data': this.data,
            'data_enum': InlineRecordDeleteEnumToString(this.dataEnum),
        }
        return obj;
    }
}

export class InlineRecordReply
{
    error: string; // 
    
    static fromJson(json: Object): InlineRecordReply
    {
        let obj = new InlineRecordReply();
        obj.error = <string>json['error'];
        return obj;
    }

    toJson(): Object
    {
        let obj: Object =
        {
            'error': this.error,
        }
        return obj;
    }
}
