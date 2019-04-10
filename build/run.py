import subprocess
import os 
import sys
import copy
import atexit
import webbrowser
import time
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENVIRONMENT = copy.deepcopy(os.environ)
ENVIRONMENT['PATH'] += ";" if not ENVIRONMENT['PATH'].endswith(";") else ""
ENVIRONMENT['PATH'] += ";".join([os.path.join(BASE_DIR, 'python'),
                                os.path.join(BASE_DIR, 'bin',
                                                    'wkhtmltopdf', 
                                                    'bin'),
                                os.path.join(BASE_DIR, "server")])

def load_browser():
    #gives enough time for the server to start
    time.sleep(5)
    print("Opening Browser")
    webbrowser.open_new_tab("http://localhost/login")


print('Starting reverse proxy')
os.chdir(os.path.join(BASE_DIR, 'bin', 'nginx'))
proxy_proc = subprocess.Popen(["nginx.exe"])# Popen so it is nonblocking

#Non blocking on the main turead
thr = threading.Thread(target=load_browser)
thr.start()

print("Starting Server...")
os.chdir(os.path.join(BASE_DIR, 'server'))
proc_server = subprocess.run(["python", "server.py"], 
    env=ENVIRONMENT)

def exit_handler():
    global proc_server
    global proxy_proc

    print("closing the server")
    proxy_proc.kill()
    proc_server.kill()

atexit.register(exit_handler)