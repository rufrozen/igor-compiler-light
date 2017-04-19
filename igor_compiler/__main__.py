from .compiler import IgorCompiler

if __name__ == '__main__':
    compiler = IgorCompiler()
    if compiler.parse_args():
        compiler.run()
    print("DONE")