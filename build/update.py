#To build an update
# use git to identify changed and new source files
# store them in a tree similar to that of the original
# send the 

# to update the app
# look for the apps path in the system_path
# replace the source files that have changed
# migrate the database
# restart the server

# must have a command line argument for the previous version

import sys
import os 
import shutil
from distutils.dir_util import copy_tree
import time
import git 
from build_logger import create_logger
import json

if len(sys.argv) < 2:
    raise Exception("Please provide a version to update the software from"
    "in the form of M.m.p (Major.minor.patch)")

UPDATE_FROM = sys.argv[1] #a version 
START = time.time()
BASE_DIR = os.path.dirname(os.getcwd())
REPO = git.Repo(BASE_DIR)
BUILD_COUNTER = None

logger = create_logger('update')

with open(os.path.join(BASE_DIR, 'build_counter.json'), 'r') as bc:
    BUILD_COUNTER  = json.load(bc)

#check the current changes have been committed
if len(REPO.index.diff(None)) > 0:
    logger.critical("Changes to the repository were not yet committed")
    #raise Exception("Please commit changes before continuing with the build process")

#check if the stated version is valid
build_versions = [i['version'] for i in BUILD_COUNTER['builds']]
if UPDATE_FROM  not in build_versions:
    raise Exception('Invalid Build number, please select one of {}'.format(
        " \n".join(build_versions)
    ))

#get specific versions commit sha
def get_sha_from_version(version):
    global BUILD_COUNTER
    for build in BUILD_COUNTER['builds']:
        if build['version'] == version:
            return build['hash']



#search for specific commit 
def get_specific_commit(repo, sha):
    for commit in repo.iter_commits():
        if commit.hexsha == sha:
            return commit

    return None

# get diffs between current version and supplied argument version

sha = get_sha_from_version(UPDATE_FROM)
commit = get_specific_commit(REPO, sha)


diff = REPO.head.commit.diff(sha)

print(diff)

# analyse differences to make changes on differences
# analyse webpack stats
# analyse common_data_static
# analyse source files 
# analyse 