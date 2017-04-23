import os, sys, argparse, glob
from .parser import IgorParser
from .generator_ts import IgorGeneratorTs
from .utils import *

class IgorCompiler:
    def __init__(self):
        self.version = "0.1.2"
        self.data = []
        self.args = None
    
    def parse_args(self):
        parser = argparse.ArgumentParser(
            description='igor compiler', 
            formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument('igor', nargs='*', help='input igor file')
        parser.add_argument('-t', '--typescript', help='genereate typescript folder')
        parser.add_argument('-s', '--schema', help='generate json schema file')
        parser.add_argument('-c', '--json-compact', action='store_true', help='compact schema json')
        parser.add_argument('-v', '--version', action='store_true', help='compiler version')
        
        self.args = parser.parse_args()
        if self.args.version:
            print(self.version)
            return False
        if self.args.igor == []:
            parser.print_help()
            return False
        return True

    def save(self, path, compact=False):
        write_file(path, json2str(self.data, compact))

    def files(self):
        return [f for g in self.args.igor for f in glob.glob(g)]

    def run(self):
        p = IgorParser()
        for f in self.files():
            print('parse: ' + f)
            if not p.parse(f):
               p.print_error()
               return
            self.data += p.data
        
        if self.args.schema != None:
            print('save schema...')
            self.save(self.args.schema, self.args.json_compact)
            
        if self.args.typescript != None:
            print('generate typescript...')
            try:
                self.gen_ts()
            except GenerationError as e:
                print(e)

        print("DONE")
            
    def gen_ts(self):
        target_dir = self.args.typescript
        target_data_path = 'protocol.data.ts'
        target_service_path = 'protocol.service.ts'
        ts = IgorGeneratorTs(self.data)
        write_file(os.path.join(target_dir, target_data_path), ts.generate_data())
        write_file(os.path.join(target_dir, target_service_path), ts.generate_service())
