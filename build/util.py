import compileall
import os
import datetime
import json
import copy
import subprocess

def remove_source_files(source_dir):
    '''iterates over source_dir and removes all .py files'''
    for _dir, subdirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.py'):
                os.remove(os.path.join(_dir, file))

        

def compile_app(root_dir, APPS):
    '''Compiles all the files listed as apps for the project'''
    for app in APPS:
        compileall.compile_dir(os.path.join(root_dir, app), force=True)

    remove_source_files(root_dir)


def increment_build_counter(REPO, BUILD_TYPE):
    '''takes a build counter file and increments the build number based on the 
    build argument supplied. The build must not have the argument --quick and 
    the argument should be -M for a major build, -m for a minor build and -p 
    for a patch'''
    
    today = datetime.date.today()
    new_build = None
    with open("build_counter.json", 'r') as f:
        current_build = json.load(f)

        new_build_count = copy.deepcopy(current_build)
        
        if BUILD_TYPE == '-M':
            new_build_count['major'] += 1
            new_build_count['minor'] = 0
            new_build_count['patch'] = 0

        elif BUILD_TYPE == '-m':
            new_build_count['minor'] += 1
            new_build_count['patch'] = 0

        elif BUILD_TYPE == '-p':
            new_build_count['patch'] += 1


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
        if BUILD_TYPE == "-M":
            major_release = copy.deepcopy(build_summary)
            major_release['updates'] = []
            current_build['major_releases'].append(major_release)
            
        new_build['builds'] = current_build['builds']
        new_build['major_releases'] = current_build['major_releases']

    with open('build_counter.json', 'w') as bc:
        json.dump(new_build, bc)


def repo_checks(repo, logger):
    if len(repo.index.diff(None)) > 0:
        logger.critical("Changes to the repository were not yet committed")
        raise Exception("Please commit changes before continuing with the build process")

    if repo.head.reference.name != "master":
        logger.critical("The build is not on the master branch")
        raise Exception("The build is not on the master branch please checkout to master")


def run_tests(logger):
    logger.info("running unit tests")
    result = subprocess.run(['python', 'manage.py', 'test'])
    if result.returncode != 0:
        logger.info("failed unit tests preventing application from building")
        raise Exception('The build cannot continue because of a failed unit test.')