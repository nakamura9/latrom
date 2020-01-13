import time
import datetime
import sys
import logging
import os
import copy
import json
import subprocess
import shutil
from distutils.dir_util import copy_tree


class DjangoProjectBuilder():
    def __init__(self, sys_args):
        self.args = sys_args
        self.start = time.time()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.app_list = ['accounting', 'common_data', 'employees',
                'inventory', 'invoicing', 'messaging', 'manufacturing',
                'planner', 'services', 'latrom']
        self.run()

    def run(self):
        self.parse_args()
        self.configure_logger()
        self.setup_environment()
        self.collect_static()
        self.copy_src()
        self.move_util_files()
        self.build_installer()
        self.build_service()
        self.package_app()
        self.cleanup()

    def parse_args(self):
        if len(self.args) < 2:
            raise Exception("""
            The application requires 1 argument,
            1. A string representing the path of the application
            """)
        
        self.app_dir = self.args[1]
        if not os.path.exists(self.app_dir) or not os.path.exists(
                os.path.join(self.app_dir, 'manage.py')):
            raise Exception('The application path provided is incorrect or no valid django application was found in this directory')

    def configure_logger(self):
        log_file = "build.log"
        if os.path.exists(log_file):
            os.remove(log_file)

        self.logger = logging.getLogger('name')
        self.logger.setLevel(logging.DEBUG)

        log_format = logging.Formatter("%(asctime)s [%(levelname)-5.5s ] %(message)s")

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_format)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def setup_environment(self):
        self.dir = os.path.dirname(os.path.abspath(__file__))
        self.dist_dir = os.path.join(self.dir, 'dist')
        self.temp_dir = os.path.join(self.dir, 'temp')
        if os.path.exists(self.dist_dir):
            shutil.rmtree(self.dist_dir)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        os.mkdir(self.dist_dir)
        os.mkdir(self.temp_dir)




        
    def collect_static(self):
        self.logger.info('Step[5] collecting static files')
        result = subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'])
        if result.returncode != 0:
            self.logger.error("Failed to collect static files")
            raise Exception("The static files collection process failed")

    def copy_src(self):
        self.logger.info("Step [6] copying source code")
        for path in ['service','service/server', 'service/database']:
            os.mkdir(os.path.join(self.temp_dir, path))

        for app in self.app_list:
            self.logger.info(app)
            copy_tree(os.path.join(self.app_dir, app), 
                os.path.join(self.temp_dir, 'service', 'server', app))

        # create an empty deploy.txt which will be used as a flag to trigger 
        # production mode.
        with open(os.path.join(self.temp_dir, 'service', 'server', 'latrom', 
                'settings', 'deploy.txt') ,'w') as f:
            f.write('')

    def move_util_files(self):
        self.logger.info('Step [10] moving webpack-stats file')
        shutil.copy(os.path.join(self.app_dir, 'assets', 'webpack-stats.json'), 
            os.path.join(self.temp_dir, 'service', 'server'))

        self.logger.info('Step [11] moving binaries(wkhtmltopdf etc.)')
        shutil.copytree(os.path.join(self.base_dir, 'build', 'bin'), 
            os.path.join(self.temp_dir, 'service', 'bin'))
        

    def build_installer(self):
        #TODO update installer!
        self.logger.info("Step [12] Creating setup executable")
        os.chdir(os.path.join(self.base_dir, 'installer'))
        env = copy.deepcopy(os.environ)
        env['PATH'] = ";".join([
            os.path.join(self.base_dir, 'installer'),
            os.path.join(self.base_dir, 'client'),
            os.path.join(self.base_dir, 'installer', 'env', 'Scripts')
        ]) 

        
        result = subprocess.run(
            ['pyinstaller', 'installer.py', '--clean', '--uac-admin',
                '--onefile'], env=env)

        if result.returncode != 0:
            self.logger.critical(
                "The executable for the setup failed to be created")
            raise Exception("The executable for the setup failed to be created")

    def build_service(self):
        self.logger.info('Step [14] building service')
        self.logger.info('Step [15] moving python')
        os.chdir(self.base_dir)
        shutil.copytree(os.path.join('build', 'python'), 
            os.path.join(self.temp_dir, 'service', 'python'))
        os.chdir(os.path.join(self.temp_dir, 'service', 'python'))
        requirements = os.path.abspath(os.path.join(self.base_dir, 
            'requirements.txt'))

        self.logger.info('Step [16] installing packages')
        result = subprocess.run(['./python', '-m', 'pip', 'install', '-r', 
            requirements])

        if result.returncode != 0:
            self.logger.info("Failed to install some packages to python")
            raise Exception("Failed to install some modules to python")

        self.logger.info("Step [16] Creating service executable")
        os.chdir(os.path.join(self.base_dir, 'service'))
        result = subprocess.run(['pyinstaller', 'service.py', '--clean', 
            '--uac-admin'])
        if result.returncode != 0:
            self.logger.critical(
                "The executable for the service failed to be created")
            raise Exception("The executable for the service failed to be created")


    def package_app(self):
        self.logger.info('Step [19] packaging app')
        self.logger.info('Step [20] moving src')
        for _,__, files in os.walk(os.path.join(self.base_dir, 'build', 'src')):
            for file in files:
                shutil.copy(os.path.join(self.base_dir, 'build', 'src', file),
                    os.path.join(self.temp_dir, 'service', 'server'))
        
        #moving config
        shutil.move(
            os.path.join(self.temp_dir, 'service', 'server', 'config.json'), 
            os.path.join(self.temp_dir, 'service','database', 'config.json')
            )


        self.logger.info('Step [21] moving executables')
        #installer
        shutil.copy(os.path.join(self.base_dir, 'installer', 'dist', 
                'installer.exe'), os.path.join(self.temp_dir))
        shutil.copy(os.path.join(self.base_dir, 'installer', 'build', 
                'installer','installer.exe.manifest'), 
                os.path.join(self.temp_dir))
        
        #service
        shutil.copytree(os.path.join(self.base_dir, 'service', 'dist',
                'service'), os.path.join(self.temp_dir, 'service', 'service'))
        
        self.logger.info("Step [22] Compressing the application")
        # shutil.make_archive('temp', 'zip', 'dist')
        
        #TODO move config.json to database


    def cleanup(self):
        self.logger.info("Completed the build process successfully in {0:.2f} seconds".format(time.time() - self.start))

#TODO moved password util to server update installer to reflect this change!!!!

if __name__ == "__main__":
    DjangoProjectBuilder(sys.argv)