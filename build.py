'''The build process creates an exe that will install the application on the target machine
the application consists of the server files( the pyd equivalents not the plain text source )
the server also includes the wkhtml2pdf binary
it includes the python install - it will make sure that all the requirements.txt are met in the file


with time this build script will target multiple os's

THE BUILD COUNTER
Major.minor.patch
the build counter is incremented by each build if the build completes successfully 

each build must exist on the master branch with all changes committed.
Each build is linked to this hash value
each build must have an argument specifying if the build is major minor or a 
patch
versions will not be recorded for quick builds
'''
import time
import datetime
import json
import logging

import subprocess
import shutil
import sys
import os
from distutils.dir_util import copy_tree
import git 
import compileall

START = time.time()
BASE_DIR = os.getcwd()
SYS_PATH = os.environ['path']

QUICK = '--quick' == sys.argv[1]
BUILD_TYPE = None

if not QUICK:
    BUILD_TYPE = sys.argv[1]

REPO = git.Repo(BASE_DIR)

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

def increment_build_counter():
    global REPO
    today = datetime.date.today()
    new_build = None
    with open("build_counter.json", 'r') as f:
        current_build = json.load(f)
        new_build_count = {
            "major": current_build['major'] + 1 if BUILD_TYPE == "-M" else 0,
            "minor": current_build['minor'] + 1 if BUILD_TYPE == "-m" else 0,
            "patch": current_build['patch'] + 1 if BUILD_TYPE == "-p" else 0
        }
        build_summary = {
            "version": "{}.{}.{}".format(
                new_build_count['major'], 
                new_build_count['minor'],
                new_build_count['patch']),
            "hash": REPO.head.commit.hexsha,
            "date": f"{today.strftime('%d/%m/%Y')}"
        }
        new_build = new_build_count
        current_build['builds'].append(build_summary)
        new_build['builds'] = current_build['builds']

    with open('build_counter.json', 'w') as bc:
        json.dump(new_build, bc)

def remove_source_files(source_dir):
    for _dir, subdirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.py'):
                os.remove(os.path.join(_dir, file))

        

def compile_app(root_dir):
    global APPS
    for app in APPS:
        compileall.compile_dir(os.path.join(root_dir, app), force=True)

    remove_source_files(root_dir)


compile_app('caleb')
raise Exception()

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


if len(REPO.index.diff(None)) > 0:
    logger.critical("Changes to the repository were not yet committed")
    raise Exception("Please commit changes before continuing with the build process")

if REPO.head.reference.name != "master":
    logger.critical("The build is not on the master branch")
    raise Excepiton("The build is not on the master branch please checkout to master")


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

#compile_app(os.path.join('dist', 'app', 'server'))


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

if not QUICK:
    increment_build_counter()


logger.info("Completed the build process successfully in {0:.2f} seconds".format(time.time() - START))