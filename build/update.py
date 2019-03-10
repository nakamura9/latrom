# replace all updated files with those stored in the files folder 
# delete all the files marked for deleting
# run the migrate service on 

import os 
import json
from distutils.dir_util import copy_tree

class VersionString():
    def __init__(self, value):
        self.value = value
        major, minor, patch = value.split('.')
        self.major = int(major)
        self.minor = int(minor)
        self.patch = int(patch)

    def __lt__(self, other):
        if other.major > self.major:
            return True

        if other.minor > self.minor:
            return True

        if other.patch > self.patch:
            return True


        return False

    def __eq__(self, other):
        return self.value == other.value 

def run():

    update_metadata = None
    delete_files = None
    INSTALLER_DIR = os.getcwd()

    if os.path.exists('delete_files.txt'):
        delete_files = open('delete_files.txt', 'r')

    with open('meta.json', 'r') as meta:
        update_metadata = json.load(meta)


    #find the application path
    app_path = os.environ.get("SBT_PATH", None)

    ENVIRONMENT = copy.deepcopy(os.environ)
    ENVIRONMENT['PATH'] +=  ";" if not SYS_PATH.endswith(";") else ""
    ENVIRONMENT['PATH'] += os.path.join(app_path, 'python') + ";"

    if not app_path:
        raise Exception('Could Not find the application path on the system, contact support for assistance')# allow users to set this variable manually if they know what they are doing 

    # ensure that the version we are replacing is lower than the update
    config = None
    with open(os.path.join(app_path, 'server', 'global_config.json'), 'r') as fp:
        config = json.load(fp)



    installed_verison = VersionString(config['application_version'])
    incoming_version = VersionString(update_metadata['version'])


    if installed_verison >= incoming_version:
        raise Exception("Installation cannot continue because the incoming version of the software is less than or equal to the currently installed version")

    #copy the source files
    #iterates over changed files and replaces the ones in the application 
    # directory
    for _dir, subdirs, files in os.walk(os.path.join(INSTALLER_DIR, 'files')):
        for file in files:
            #first remove the existing file in the target
            os.remove(os.path.join(app_path, 'server', _dir, file))
            # copy the replacement from the files folder into the place of the old 
            # file
            shutil.copy(os.path.join(INSTALLER_DIR, 'files', _dir, file),
                os.path.join(app_path, 'server', _dir))

    #delete the marked files
    if delete_files:
        for file in delete_files:
            os.remove(os.path.join(app_path, 'server', file))

    delete_files.close()



    #migrate the database
    os.chdir(os.path.join(app_path, 'server'))
    results = subprocess.run(['python', 'manage.py', 'migrate'], env=ENVIRONMENT)

    os.chdir(INSTALLER_DIR)

    print('completed the update successfully')

if __name__ == "__main__":
    run()