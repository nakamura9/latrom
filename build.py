'''The build process creates an exe that will install the application on the target machine
the application consists of the server files( the pyd equivalents not the plain text source )
the server also includes the wkhtml2pdf binary
it includes the python install - it will make sure that all the requirements.txt are met in the file


with time this build script will target multiple os's

the installer exe will add wkhtml2pdf to the path as well as python
it will create a windows service that starts with windows and runs the server

'''
import time
import json
import logging

import subprocess
import shutil
import sys
import os
from distutils.dir_util import copy_tree

QUICK = '--quick' in sys.argv

START = time.time()
BASE_DIR = os.getcwd()
SYS_PATH = os.environ['path']
APPS = [
    'accounting',
    'common_data',
    'employees',
    'inventory',
    'invoicing',
    'messaging',
    'manufacturing',
    'planner',
    'services',
    'latrom'
]

TREE = [
    'dist',
    'dist/app',
    'dist/app/server',
    'dist/app/database',
    'dist/app/bin',
    'dist/app/python' 
]

def remove_python_from_path():
    paths = os.environ['path'].split(";")
    new_path = [path for path in paths if not "Python" in path]
    return ";".join(new_path)       


log_file = os.path.join(BASE_DIR, "build.log")
if os.path.exists(log_file):
    os.remove(log_file)

logger = logging.getLogger('build_process')
logger.setLevel(logging.DEBUG)

log_format = logging.Formatter("%(asctime)s [%(levelname)-5.5s ] %(message)s")

file_handler = logging.FileHandler('build.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)
logger.addHandler(file_handler)


logger.info("Checking react bundles")
stats_file_path = os.path.join(BASE_DIR, 'assets', 'webpack-stats.json')
stats_file = open(stats_file_path, 'r')

if json.load(stats_file).get("status", "") != "done":
    logger.critical("The webpack bundles are not ready")
    raise Exception("There are errors in the webpack bundles")

if not QUICK:
    logger.info("running unit tests")
    result = subprocess.run(['python', 'manage.py', 'test'])
    if result.returncode != 0:
        logger.info("failed unit tests preventing application from building")
        raise Exception('The build cannot continue because of a failed unit test.')


    result = subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'])
    if result.returncode != 0:
        logger.info("Failed to collect stati files")
        raise Exception("The static files collection process failed")


logger.info("copying source code")
if os.path.exists('dist'):
    shutil.rmtree('dist')

for path in TREE:
    os.mkdir(os.path.join(path))

for app in APPS:
    logger.info(app)
    copy_tree(app, os.path.join('dist', 'app', 'server', app))

os.remove(os.path.join('dist', 'app', 'server', 'latrom', '__init__.py'))
shutil.copy(os.path.join('build', 'app', 'server', 'latrom', '__init__.py'),
    os.path.join('dist', 'app', 'server', 'latrom', 'settings'))

os.chdir(os.path.join(BASE_DIR, 'build', 'app', 'server'))

result = subprocess.run(['python', 'license_creator.py', 'trial.json'])

os.chdir(BASE_DIR)

if result.returncode != 0:
    raise Exception("The trial license generation process failed")

FILES = [
    'license.json',
    'global_config.json',
    'server.py',
    'manage.py'
    ]

for file in FILES:
    shutil.copy(os.path.join('build', 'app', 'server', file,),
        os.path.join('dist', 'app', 'server'))
    


logger.info('copying binaries')#vc++ nginx wkhtml
copy_tree(os.path.join('build', 'app', 'bin'), os.path.join(
    'dist', 'app', 'bin'))

logger.info('installing python modules')

os.chdir(os.path.join(BASE_DIR, 'build', 'app', 'python'))

requirements_path = os.path.join(BASE_DIR, 'requirements.txt')

os.environ['path'] = remove_python_from_path()

if not QUICK:
    result = subprocess.run(['./python', '-m', 'pip', 'install', '-r', 
        requirements_path])

    if result.returncode != 0:
        raise Exception("Failed to install some modules to python")

os.environ['path'] = SYS_PATH
os.chdir(BASE_DIR)

logger.info('copying python')
copy_tree(os.path.join('build', 'app', 'python'), os.path.join('dist', 'app', 'python'))


logger.info("Creating setup executable")
result = subprocess.run(['pyinstaller', os.path.join(
                    BASE_DIR, "build", "app", 'install.py'), '--onefile', '--noconsole'])
if result.returncode != 0:
    logger.critical("The executable for the setup failed to be created")
    raise Exception("The executable for the setup failed to be created")


logger.info("create running executable")
result = subprocess.run(['pyinstaller', os.path.join(
                    BASE_DIR, "build", "app", 'run.py'), '--onefile'])
if result.returncode != 0:
    logger.critical("The executable for the application runner failed to be created")
    raise Exception("The executable for the application runner failed to be created")

logger.info("moving executables")
shutil.move(os.path.join(BASE_DIR, "dist", "run.exe"), 
    os.path.join(BASE_DIR, "dist", "app"))
shutil.move(os.path.join(BASE_DIR, "dist", "install.exe"), 
    os.path.join(BASE_DIR, "dist", "app"))

logger.info("moving utilities")
shutil.copy(os.path.join(BASE_DIR, 'build', 'app', 'password_util.py'),
    os.path.join(BASE_DIR, "dist", "app"))
shutil.copy(stats_file_path, os.path.join(BASE_DIR, "dist", "app", "server"))

logger.info("removing temp files")
shutil.rmtree(os.path.join(BASE_DIR, "build", "install"))
shutil.rmtree(os.path.join(BASE_DIR, "build", "run"))

logger.info("Compressing the application")
shutil.make_archive(os.path.join('dist', 'archive'), 'zip', os.path.abspath('dist'))

logger.info("Completed the build process successfully in {0:.2f} seconds".format(time.time() - START))

#create a secret key

# create temp license with key
# ship it with software
# add to os environment
# delete key
# store key in database on server
# all license signatures for the specific customer must use the same secret key 
# to generate
# the license check module must retrieve the secret key from the environment
# build the zip file for every deployment