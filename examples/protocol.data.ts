
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

//  Some desc text
export const enum SomeEnum
{
    Null,
    Val1, // 
    Val2, //  important tag
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

// 
export const enum GlobalEnum
{
    Null,
    Global1, //  is it global_1
    Global2, //  is it global_2
    Global3, //  is it global_3
}
export function GlobalEnumToString(val: GlobalEnum)
{
    let arr = [
        null,
        'global_1',
        'global_2',
        'global_3'
    ];
    return arr[val]
}
export function GlobalEnumFromString(json: string)
{
    switch(json)
    {
        case 'global_1': return GlobalEnum.Global1;
        case 'global_2': return GlobalEnum.Global2;
        case 'global_3': return GlobalEnum.Global3;
        default: return GlobalEnum.Null;
    }
}

// 
export const enum BigInnerRecordStatusEnum
{
    Null,
    Data1, // 
    Data2, // 
}
export function BigInnerRecordStatusEnumToString(val: BigInnerRecordStatusEnum)
{
    let arr = [
        null,
        'data1',
        'data2'
    ];
    return arr[val]
}
export function BigInnerRecordStatusEnumFromString(json: string)
{
    switch(json)
    {
        case 'data1': return BigInnerRecordStatusEnum.Data1;
        case 'data2': return BigInnerRecordStatusEnum.Data2;
        default: return BigInnerRecordStatusEnum.Null;
    }
}

//  is it custom
export const enum BigInnerRecordCustomEnum
{
    Null,
    MyVal1, //  is it my_val_1
    Global3, //  is it global_3
    MyVal3, // 
}
export function BigInnerRecordCustomEnumToString(val: BigInnerRecordCustomEnum)
{
    let arr = [
        null,
        'my_val_1',
        'global_3',
        'my_val_3'
    ];
    return arr[val]
}
export function BigInnerRecordCustomEnumFromString(json: string)
{
    switch(json)
    {
        case 'my_val_1': return BigInnerRecordCustomEnum.MyVal1;
        case 'global_3': return BigInnerRecordCustomEnum.Global3;
        case 'my_val_3': return BigInnerRecordCustomEnum.MyVal3;
        default: return BigInnerRecordCustomEnum.Null;
    }
}

// 
export const enum DeleteSecondRequestBodyItemEnum
{
    Null,
    Type1, // 
    Type2, // 
    Global1, //  is it global_1
}
export function DeleteSecondRequestBodyItemEnumToString(val: DeleteSecondRequestBodyItemEnum)
{
    let arr = [
        null,
        'type1',
        'type2',
        'global_1'
    ];
    return arr[val]
}
export function DeleteSecondRequestBodyItemEnumFromString(json: string)
{
    switch(json)
    {
        case 'type1': return DeleteSecondRequestBodyItemEnum.Type1;
        case 'type2': return DeleteSecondRequestBodyItemEnum.Type2;
        case 'global_1': return DeleteSecondRequestBodyItemEnum.Global1;
        default: return DeleteSecondRequestBodyItemEnum.Null;
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

export class BigInnerRecord
{
    result: boolean; // 
    status: BigInnerRecordStatusEnum; // 
    custom: BigInnerRecordCustomEnum; //  is it custom
    
    static fromJson(json: Object): BigInnerRecord
    {
        let obj = new BigInnerRecord();
        obj.result = <boolean>json['result'];
        obj.status = BigInnerRecordStatusEnumFromString(json['status']);
        obj.custom = BigInnerRecordCustomEnumFromString(json['custom']);
        return obj;
    }

    toJson(): Object
    {
        let obj: Object =
        {
            'result': this.result,
            'status': BigInnerRecordStatusEnumToString(this.status),
            'custom': BigInnerRecordCustomEnumToString(this.custom),
        }
        return obj;
    }
}

export class DeleteSecondRequestBody
{
    data: number; // 
    item: DeleteSecondRequestBodyItemEnum; // 
    
    static fromJson(json: Object): DeleteSecondRequestBody
    {
        let obj = new DeleteSecondRequestBody();
        obj.data = <number>json['data'];
        obj.item = DeleteSecondRequestBodyItemEnumFromString(json['item']);
        return obj;
    }

    toJson(): Object
    {
        let obj: Object =
        {
            'data': this.data,
            'item': DeleteSecondRequestBodyItemEnumToString(this.item),
        }
        return obj;
    }
}

export class DeleteSecondResponse200
{
    error: string; // 
    
    static fromJson(json: Object): DeleteSecondResponse200
    {
        let obj = new DeleteSecondResponse200();
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
