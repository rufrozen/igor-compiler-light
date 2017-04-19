
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

    // 
    getLog(someQ: string): Observable<Protocol.RecordSimple>
    {
        return this.get('/api/log', {'some_q': someQ})
            .catch(response =>
            {
                switch(response.status)
                {
                    case 500: return Observable.throw(Protocol.SomeEnumFromString(response.json()));
                    default: return Observable.throw(response);
                }
            })
            .map(response => Protocol.RecordSimple.fromJson(response.json()));
    }

    //  Some big Desc text
    postLog(id: number, bytes: number, text: string, body: Protocol.RecordSimple): Observable<Protocol.RecordSimple>
    {
        return this.post('/api/log/' + id.toString() + '/hello', {'bytes': bytes, 'text': text}, body.toJson())
            .catch(response =>
            {
                switch(response.status)
                {
                    case 500: return Observable.throw(Protocol.SomeEnumFromString(response.json()));
                    default: return Observable.throw(response);
                }
            })
            .map(response => Protocol.RecordSimple.fromJson(response.json()));
    }

}
