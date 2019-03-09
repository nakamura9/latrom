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

# each update build is assigned to a major release 
# each update builds up on the last released update
# major build changes cannot be updated
# changes to the requirements of the applications must prevent any update from #
# being performed, instead suggesting a new major release

import sys
import os 
import shutil
from distutils.dir_util import copy_tree
import time
import git 
from build_logger import create_logger
import json
import re

START = time.time()
BASE_DIR = os.path.dirname(os.getcwd())
REPO = git.Repo(BASE_DIR)
BUILD_COUNTER = None

logger = create_logger('update')

with open(os.path.join(BASE_DIR, 'build_counter.json'), 'r') as bc:
    BUILD_COUNTER  = json.load(bc)

if len(BUILD_COUNTER['major_releases']) == 0:
    raise Exception("No previous major release found. Build the application using the -M argument and then updates can be made to the release")

UPDATE_FROM = BUILD_COUNTER['major_releases'][-1]['hash'] # newest release

#check the current changes have been committed
if len(REPO.index.diff(None)) > 0:
    logger.critical("Changes to the repository were not yet committed")
    #raise Exception("Please commit changes before continuing with the build process")



#get specific versions commit sha
def get_sha_from_version(counter, version):
    for build in counter['builds']:
        if build['version'] == version:
            return build['hash']



#search for specific commit 
def get_specific_commit(repo, sha):
    for commit in repo.iter_commits():
        if commit.hexsha == sha:
            return commit

    return None

def search_differences(diffs, regex):
    results = []
    for diff in diffs:
        if re.search(regex, diff.b_path):
            results.append(diff.b_path)

    return results 

# get diffs between current version and supplied argument version

commit = get_specific_commit(REPO, UPDATE_FROM)


diffs = REPO.head.commit.diff(UPDATE_FROM)

# analyse differences to make changes on differences
# seach for changes to the requirements.txt
requirements = search_differences(diffs, r'^requirements.txt$')
if len(requirements) > 0:
    logger.critical("The applications dependancies have changed. Exiting")
    raise Exception("The dependencies for the application have changed. Build a"
    " new release instead of an update to this version of the software")

update_dir = os.path.join(BASE_DIR, 'dist', 'update', 'files')
if not os.path.exists(update_dir):
    os.mkdir(update_dir)

fail_counter = 0
delete_list = open(os.path.join(os.path.dirname(update_dir), 'del_list.txt'), 'w')
for d in diffs:
    if d.change_type == "D":
        delete_list.write(d.b_path + '\n')
    else:
        pathname = d.b_path.replace("/", "\\")
        dest_dir = os.path.join(update_dir, os.path.dirname(pathname))
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        try:
            shutil.copy(os.path.join(BASE_DIR, pathname), dest_dir)
        except:
            fail_counter += 1
            print(d.change_type)

delete_list.close()


if fail_counter > 0:
    logger.warning("{} files failed to copy".format(fail_counter))
    raise Exception('Some files failed to copy')

# check if a diff is a deleted file. if so create a file with a list of files to delete
# analyse webpack stats
# analyse common_data_static
# analyse source files 
# analyse 