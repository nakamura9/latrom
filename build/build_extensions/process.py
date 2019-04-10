import os
import subprocess
import shutil


def build():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(base_dir)

        #compile
        res = subprocess.run(['python', 'setup.py', 'build_ext'])


        if res.returncode != 0:
            raise Exception(' The extensions failed to build correctly')

        ext_path = os.path.join(base_dir, 'build', 'lib.win-amd64-3.7')
        for _dir, __, files in os.walk(ext_path):
            for file_name in files:
                new_name = file_name[:file_name.find('.')] + '.pyd'
                try:
                    os.rename(os.path.join(ext_path, _dir, file_name), new_name)
                except FileExistsError:
                    os.remove(new_name)
                    os.rename(os.path.join(ext_path, _dir, file_name), new_name)


        #move the compiled files to the appropriate locations
        target_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(base_dir)), 'dist', 'app', 'server')
        file_mapping= {
            'license.pyd': os.path.join(target_dir, 'common_data', 'middleware'),
            'base.pyd': os.path.join(target_dir, 'latrom', 'settings'),
            'users.pyd': os.path.join(target_dir, 'common_data', 'middleware')
        }

        for fil in file_mapping.keys():
            shutil.move(fil, file_mapping[fil])
            #remove the pyc
            name = fil.split('.')[0] + '.pyc'
            os.remove(os.path.join(file_mapping[fil], name))

    except:
        pass
    
    finally:                
        #clean up
        for fil in ['license.pyd', 'users.pyd', 'base.pyd', 'build']:
            if os.path.exists(fil):
                try:
                    os.remove(fil)
                except:
                    shutil.rmtree(fil)

if __name__ == "__main__":
    build()