import json

def read_file(file):
    with open(file, "r", encoding="utf-8") as f:
        return f.read()
    
def write_file(file, text):
    with open(file, "w", encoding="utf-8") as f:
        f.write(text)
        
def json2str(obj, compact=False):
    if compact:
        return json.dumps(obj, separators=(',',':'))
    else:
        return json.dumps(obj, indent=4, separators=(',', ': '))

def str2json(str):
    return json.loads(str)