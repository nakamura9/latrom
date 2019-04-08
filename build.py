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


Steps:
1.  check if the repository is on master branch and changes have been committed
2.  check that the react js bundles are all properly compiled
3.  runs unit test
4.  collect static files
5.  copy source code
6.  generate trial license
7.  copy install binaries
8.  install python modules based on requirements.txt
9.  copy the updated python package
10. create setup executable and run executable
11. move executable and utility files
12. remove temp files and compress the application
13. increment build counter


Need to add a way to obfuscate mission critical code
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
from build.build_logger import create_logger
from build.consts import *
from build.util import (increment_build_counter, 
                       repo_checks,
                       run_tests)

if len(sys.argv) < 2:
    raise Exception("""
    The application requires an argument, 
    --quick for quick builds or an acceptable build type of:
        -M for major revisions, -m for minor revisions and -p for patches """)

START = time.time()
BASE_DIR = os.getcwd()



QUICK = '--quick' == sys.argv[1]
BUILD_TYPE = None

if not QUICK:
    BUILD_TYPE = sys.argv[1]

REPO = git.Repo(BASE_DIR)


logger = create_logger('build')

if not QUICK:
    repo_checks(REPO, logger)

logger.info("Checking react bundles")
stats_file_path = os.path.join(BASE_DIR, 'assets', 'webpack-stats.json')
stats_file = open(stats_file_path, 'r')

if json.load(stats_file).get("status", "") != "done":
    logger.critical("The webpack bundles are not ready")
    raise Exception("There are errors in the webpack bundles")

if not QUICK:
    run_tests(logger)


    result = subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'])
    if result.returncode != 0:
        logger.info("Failed to collect static files")
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

# set up production settings TODO improve
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

os.chdir(BASE_DIR)

logger.info('copying python')
copy_tree(os.path.join('build', 'app', 'python'), os.path.join('dist', 'app', 'python'))


logger.info("Creating setup executable")
result = subprocess.run(['pyinstaller', os.path.join(
                    BASE_DIR, "build", 'install.py'), '--onefile', '--noconsole'])
if result.returncode != 0:
    logger.critical("The executable for the setup failed to be created")
    raise Exception("The executable for the setup failed to be created")


logger.info("create running executable")
result = subprocess.run(['pyinstaller', os.path.join(
                    BASE_DIR, "build", 'run.py'), '--onefile'])
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
    increment_build_counter(REPO, BUILD_TYPE)

logger.info("Completed the build process successfully in {0:.2f} seconds".format(time.time() - START))