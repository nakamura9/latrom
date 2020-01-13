import os 
import compileall
import shutil

class SourceCompiler():
    def __init__(self, root, folders):
        self.root = root
        self.folders = folders

    def move_compiled(self, dir):
        parent_dir = os.path.dirname(dir)
        for _, __, files in os.walk(dir):
            for file in files:
                shutil.move(os.path.join(dir, file), parent_dir)
                self.rename_file(os.path.join(parent_dir, file))

    def rename_file(self, file_name):
        '''renames a file with the cypython-*.pyc to a simple .pyc file'''
        if file_name.endswith('.pyc'):
            new_name = file_name[:file_name.find('.')] + '.pyc'
            try:
                os.rename(file_name, new_name)
            except FileExistsError:
                os.remove(new_name)
                os.rename(file_name, new_name) 
    
    def run(self):
        for f in self.folders:
            f_path = os.path.join(self.root, f)
            compileall.compile_dir(f_path, force=True)
            for dir,_, __ in os.walk(f_path):
                if dir.endswith('__pycache__'):
                    self.move_compiled(dir)
            self.remove_src(f_path)

    

    def remove_src(self, dir):
        for _dir, subdirs, files in os.walk(dir):
            for file in files:
                if file.endswith('.py'):
                    os.remove(os.path.join(_dir, file))
