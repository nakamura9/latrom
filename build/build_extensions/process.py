import os
import subprocess


def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    res = subprocess.run(['python', 'setup.py', 'build_ext'])

    if res.returncode != 0:
        raise Exception(' The extensions failed to build correctly')

    ext_path = os.path.join(base_dir, 'build', 'lib.win-amd64-3.7')
    for _, __, file_name in os.walk(ext_path):
        new_name = file_name[:file_name.find('.')]
        try:
            os.rename(os.path.join(ext_path, file), new_name)
        except:
            os.remove(new_name)
            os.rename(os.path.join(ext_path, file), new_name)

            
if __name__ == "__main__":
    build()