import compileall
import os
import datetime
import json

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