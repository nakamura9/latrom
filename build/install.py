import logging
import os
import subprocess
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import sys
import re
import json
from distutils.dir_util import copy_tree
import shutil
import time
import copy
import build_logger
#the install app should collect a default username and password
# the server should have a name 
# the install script should do some dns and configure the pdf


logger = build_logger.create_logger('install')
SYS_PATH = os.environ['path']
BASE_DIR = os.getcwd()
INSTALL_CONFIG = {}

#NB the trailing slash must match between the media location  and the formatted path
NGINX_CONFIG = '''
    worker_processes  1;


events {{
    worker_connections  1024;
}}



http {{
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;

    upstream django {{
        server      localhost:8000;
    }}


    server {{
        listen       80;
        server_name  localhost;
        charset      utf-8;
        root  /html/;
        try_files $uri @django;

        location /media {{
            alias   "{}";
            
        }}


        location @django {{
            proxy_pass http://127.0.0.1:8000;
            proxy_redirect          off;
            proxy_set_header        Host            $host;
            proxy_set_header        X-Real-IP       $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
            }}

    }}
}}
'''


def create_superuser(env):
    '''edits a the common fixture to include a default superuser as defined by the prompts in the install process'''
    global INSTALL_CONFIG
    global BASE_DIR

    result = subprocess.run(['python', 'password_util.py', 
        INSTALL_CONFIG['password']], env=env)
    if result.returncode != 0:
        raise Exception("Failed to create password hash")
    with open('hashed_password.txt', 'r') as f:
        password = f.read()

    os.remove('hashed_password.txt')
    userdata = {
        "model": 'auth.user',
        'pk': 2,
        'fields': {
            'username': INSTALL_CONFIG['username'],
            'password': password,
            'is_superuser': True,
            'is_staff': True,
            'is_active': True
        }
    }
    fixture_path = os.path.join(INSTALL_CONFIG['path'], 'server', 'common_data', 'fixtures', 'common.json')
    common_fixture = json.load(open(fixture_path, 'r'))
    common_fixture.append(userdata)
    os.remove(fixture_path)

    json.dump(common_fixture, open(fixture_path, 'w'))

class WelcomePage(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.grid()
        self.create_widgets()
        self.CAN_GO_BACK = False
        self.CAN_MOVE_FORWARD = True

    def create_widgets(self):
        self.welcomeMessage = tk.Label(self, text="This program will install suave business tools on your computer. click next to continue.", anchor=tk.N, height=7, wraplength=450, justify=tk.LEFT)
        self.welcomeMessage.grid(row=0, column=0, padx=20)

class SelectFolderPage(ttk.Frame):
    def __init__(self, master=None):
        global INSTALL_CONFIG

        super().__init__(master)
        self.master = master
        self.grid()
        self.current_path = os.getcwd()
        self.path_variable = tk.StringVar()
        self.path_variable.set(f"Current Path: {self.current_path}")
        INSTALL_CONFIG['path'] = self.current_path#set path in init        
        
        self.create_widgets()
        self.CAN_GO_BACK = True
        self.CAN_MOVE_FORWARD = True

    def create_widgets(self):
        self.title_label = tk.Label(self, 
            text="Select the path to install the application", anchor=tk.W, height=1, justify=tk.LEFT)
        self.title_label.grid(row=0, column=0, padx=20, sticky=tk.W)
        self.path_label = tk.Label(self, 
            textvariable=self.path_variable, height=4, wraplength=450, justify=tk.LEFT, pady=2, padx=20)
        self.path_label.grid(row=1, column=0, padx=20)
        self.select_path_button = ttk.Button(self,
                                            text="Select Path",
                                            command=self.select_path)
        
        self.select_path_button.grid(row=2, column=0, sticky=tk.E, padx=20)

    def select_path(self):
        global INSTALL_CONFIG
        path = filedialog.askdirectory()
        if path != "":
            self.current_path = path
            self.path_variable.set(f"Current Path: {self.current_path}")
            INSTALL_CONFIG['path'] = self.current_path

        else:
            pass # prevent user from continuing

class CreateSuperUserPage(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        
        self.grid()
        self.username = tk.StringVar()
        self.email = tk.StringVar()
        self.password = tk.StringVar()
        self.password_confirm = tk.StringVar()

        self.validation_status = tk.StringVar()

        self.create_widgets()
        self.CAN_GO_BACK = True
        self.CAN_MOVE_FORWARD = False


    def create_widgets(self):
        
        valid_username = (self.register(self.validate_username), '%P')
        valid_email = (self.register(self.validate_email), '%P')
        valid_password = (self.register(self.validate_password), '%P')
        valid_confirm_pass = (self.register(self.validate_confirm_password), 
            '%P')
        
        self.title_label = tk.Label(self, 
            text="Create The Primary User for the software package", 
            anchor=tk.W)
        self.username_label = tk.Label(self, text="Username:")
        self.username_entry = tk.Entry(self, textvariable=self.username, 
            validate='key', validatecommand=valid_username)
        self.email_label = tk.Label(self, text="Email:")
        self.email_entry = ttk.Entry(self, textvariable=self.email, 
                                            validatecommand=valid_email, 
                                            validate="key")
        self.password_label = ttk.Label(self, text="Password:")
        self.password_entry = ttk.Entry(self, textvariable=self.password, 
                                            validatecommand=valid_password, 
                                            validate="all", show="*")
        self.password_confirm_label = ttk.Label(self, text="Confirm Password:")
        self.password_confirm_entry = ttk.Entry(self, 
                                            textvariable=self.password_confirm, 
                                            validatecommand=valid_confirm_pass, 
                                            validate="all", show="*")
        self.validation_label = ttk.Label(self, 
                                            textvariable=self.validation_status)
        self.title_label.grid(row=0, column=0, columnspan=2, 
            sticky=tk.W, padx=20)
        self.username_label.grid(row=1, column=0)
        self.username_entry.grid(row=1, column=1)
        self.email_label.grid(row=2, column=0)
        self.email_entry.grid(row=2, column=1)
        self.password_label.grid(row=3, column=0)
        self.password_entry.grid(row=3, column=1)
        self.password_confirm_label.grid(row=4, column=0)
        self.password_confirm_entry.grid(row=4, column=1)
        self.validation_label.grid(row=5, column=0, columnspan=2, padx=20)

    def validate_username(self, val):
        if len(val) > 6:
            self.validation_status.set("Username Ok")
            self.validate_email(self.email.get())
        else:
            self.validation_status.set("Username too short, use at least 6 characters")
            self.CAN_MOVE_FORWARD =False
            self.master.update_buttons()
        return True

    
    def validate_email(self, val):
        if re.match("^.*@.*\..*$", val):
            self.validation_status.set("Email OK")
            self.validate_password(self.password.get())
            
        else:
            self.validation_status.set("Email must have a '@' symbol and at least 1 '.' afterwards")
            self.CAN_MOVE_FORWARD =False
            self.master.update_buttons()
            
        return True


    def validate_password(self, val):
        if len(val) > 7:
            self.validation_status.set("Password OK")
            self.validate_confirm_password(self.password_confirm.get())
            
        else:
            self.validation_status.set("Password Too short")
            self.CAN_MOVE_FORWARD =False
            self.master.update_buttons()
        return True

    def validate_confirm_password(self, val):
        if self.password_entry.get() == val:
            self.validation_status.set("Passwords Match")
            self.validate()
            
        else:
            self.validation_status.set("Passwords do not match")
            
            self.CAN_MOVE_FORWARD =False
            self.master.update_buttons()
        return True

    def validate(self):
        self.validation_status.set("User Credentials OK")
        self.CAN_MOVE_FORWARD =True
        INSTALL_CONFIG.update({
            'username': self.username.get(),
            'email': self.email.get(),
            'password': self.password.get()
        })
        self.master.update_buttons()
        return True

        
        
class InstallApplicationPage(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.grid()
        self.progress_var = tk.IntVar()
        self.progress_var.set(0)
        self.status = tk.StringVar()
        self.status.set("Starting Installation")
        self.CAN_GO_BACK = False
        self.CAN_MOVE_FORWARD = False
        self.create_widgets()
        
        

    def create_widgets(self):
        self.title_label = tk.Label(self, 
            text="Installing Suave Business Tools", anchor=tk.W)
        self.progress = ttk.Progressbar(self, 
            length=400, mode='determinate', 
            variable=self.progress_var, 
            maximum=100)
        self.status_label = tk.Label(self, textvariable=self.status)
        
        self.title_label.grid(row=0, column=0)
        self.progress.grid(column=0, row=1, padx=45, pady=20)
        self.status_label.grid(row=2, column=0)
        

    def push_message(self, message):
        global logger
        self.status.set(message)
        logger.info(message)


    def install(self):
        global logger
        global SYS_PATH
        global BASE_DIR
        global INSTALL_CONFIG
        global NGINX_CONFIG
        TARGET_DIR = INSTALL_CONFIG['path']

        ENVIRONMENT = copy.deepcopy(os.environ)
        ENVIRONMENT['PATH'] +=  ";" if not SYS_PATH.endswith(";") else ""
        ENVIRONMENT['PATH'] += ";".join([os.path.join(TARGET_DIR, 'python'),
                                os.path.join(TARGET_DIR, 'bin',
                                                        'wkhtmltopdf', 
                                                        'bin')])

        logger.info(TARGET_DIR)
        if TARGET_DIR != os.getcwd():
            self.push_message("Copying application files")
            for dir in ['bin', 'database', 'python', 'server']:
                copy_tree(dir, os.path.join(TARGET_DIR, dir))

            shutil.copy('run.exe', TARGET_DIR)
        self.progress_var.set(30)
        self.update()
        
        self.push_message("Adding python to system path")
        self.push_message("Adding wkhtmltopdf to system path")
    

        
        self.push_message("Installing Visual C++ binaries")
        self.progress_var.set(40)
        self.update()


        os.chdir(os.path.join(TARGET_DIR, 'bin'))
        result = subprocess.run('./vc_redist.x64.exe')
        if result.returncode != 0:
            logger.critical('some dependancies were not properly installed')

        os.chdir(TARGET_DIR)
        self.push_message("Creating superuser")#KEY!
        create_superuser(ENVIRONMENT)
        self.progress_var.set(50)

        os.chdir(os.path.join(TARGET_DIR, 'server'))

        self.push_message("Creating a new database")
        results = subprocess.run(['python', 'manage.py', 'migrate'], env=ENVIRONMENT)
        
        self.progress_var.set(90)
        self.update()

        self.push_message("Installing database fixtures")

        results = subprocess.run(['python', 'manage.py', 'loaddata', 'accounts.json', 'journals.json', 'settings.json', 'common.json', 'employees.json', 'inventory.json', 'invoicing.json', 'planner.json'], env=ENVIRONMENT)
    

        if results.returncode != 0:
            raise Exception("Failed to install database")

        nginx_path = os.path.join(TARGET_DIR, 'bin', 'nginx', 'conf','nginx.conf')
        os.remove(nginx_path)
        with open(nginx_path, 'w') as conf:
            conf.write(NGINX_CONFIG.format(os.path.join(TARGET_DIR, 'server', 'media')))

        self.push_message("Installed Application successfully.")
        self.progress_var.set(100)

        


class InstallGUI(ttk.Frame):
    current_page = 0
    pages = [
        WelcomePage,
        SelectFolderPage,
        CreateSuperUserPage,
        InstallApplicationPage,
    ]
    def __init__(self, master=None, width=640, height=320):
        super().__init__(master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.header = ttk.Label(self,
                                text="Suave Business Tools")
        self.header.config(font=('Times', 32))
        self.container = WelcomePage(self)
        self.cancelButton = ttk.Button(self, 
                                text="Cancel", 
                                command=self.quit)
        self.backButton = ttk.Button(self, 
                                text="Back", 
                                command=self.back)
        self.nextButton = ttk.Button(self, 
                                text="Next", 
                                command=self.next)
        self.header.grid(row=0,column=0,columnspan=3)
        self.container.grid(row=1, column=0, columnspan=3)
        self.nextButton.grid(row=2, column=0, sticky=tk.S + tk.E)
        self.backButton.grid(row=2, column=1, sticky=tk.S + tk.E)
        self.cancelButton.grid(row=2, column=2, sticky=tk.S + tk.E)

    def next(self):
        if self.current_page + 1 > len(self.pages) - 1:
            pass
        else:
            self.current_page += 1
        self.get_current_page()


    def back(self):
        if self.current_page - 1 < 0:
            pass
        else:
            self.current_page -= 1
        self.get_current_page()

    def update_buttons(self):
        if self.container.CAN_GO_BACK:
            self.backButton.state(['!disabled'])
        else:
            self.backButton.state(['disabled'])

        if self.container.CAN_MOVE_FORWARD:
            self.nextButton.state(['!disabled'])
        else:
            self.nextButton.state(['disabled'])

    def get_current_page(self):
        global logger

        page =  self.pages[self.current_page]
        self.container.destroy()
        self.container = page(self)
        self.container.grid(row=1, column=0, columnspan=3)
        self.update_buttons()

        self.update()
        if isinstance(self.container, InstallApplicationPage):
            
            try:
                self.container.install()
                messagebox.showinfo('Installation Status', 
                    "Install Completed Successfully")
                
                
            except Exception as e:
                logger.critical(e)
                messagebox.showerror("Installation Status", 
                    "Installation failed to complete successfully.")
                self.quit()
        

app = InstallGUI()
app.master.title=("Suave Business Tools")
app.master.geometry("500x200")
app.mainloop()


