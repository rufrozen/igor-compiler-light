import os, sys, argparse
from .parser import IgorParser
from .generator_ts import IgorGeneratorTs
from .utils import *

class IgorCompiler:
    def __init__(self):
        self.parser = IgorParser()
        self.args = None
    
    def parse_args(self):
        parser = argparse.ArgumentParser(
            description='igor compiler', 
            formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument('-i', '--input', help='input igor file')
        parser.add_argument('-t', '--typescript', help='genereate typescript folder')
        parser.add_argument('-s', '--schema', help='generate json schema file')
        parser.add_argument('-c', '--json-compact', action='store_true', help='compact schema json')
        
        self.args = parser.parse_args()
        if self.args.input == None:
            parser.print_help()
            return False
        else:
            return True

    def run(self):
        self.parser.parse(self.args.input)
        
        if self.args.schema != None:
            self.parser.save(self.args.schema, self.args.json_compact)
            
        if self.args.typescript != None:
            self.gen_ts()
            
    def gen_ts(self):
        target_dir = self.args.typescript
        target_data_path = 'protocol.data.ts'
        target_service_path = 'protocol.service.ts'
        ts = IgorGeneratorTs(self.parser.data)
        write_file(os.path.join(target_dir, target_data_path), ts.generate_data())
        write_file(os.path.join(target_dir, target_service_path), ts.generate_service())