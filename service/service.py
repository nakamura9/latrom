import os
import subprocess
import copy 
import socket
import win32serviceutil

import servicemanager
import win32event
import win32service
import sys
from winreg import *
import winreg

#add wkhtmltopdf path to path
import logging
logging.basicConfig(level=logging.DEBUG, filename='service.log')
logger = logging.getLogger()

# get path from registry stored for the application by the installer

key = OpenKey(HKEY_LOCAL_MACHINE, r"SOFTWARE\\suave")
val, reg_type = QueryValueEx(key, 'SERVICE_PATH')
WORKING_DIR = os.path.abspath(os.path.dirname(val)) 
print(WORKING_DIR)

os.chdir(WORKING_DIR)

ENVIRONMENT = copy.deepcopy(os.environ)
ENVIRONMENT['PATH'] = ";".join([
    os.path.abspath('python'),
    os.path.abspath(os.path.join('bin', 'wkhtmltopdf', 'bin')),
    os.path.abspath('server'),
    ]) + ';' + ENVIRONMENT["PATH"]

class UmisoftService(win32serviceutil.ServiceFramework):
    _svc_name_ = "SuaveService"
    _svc_display_name_ = "suave_service"
    _svc_description_ = "Starts the application server in the background"


    @classmethod
    def parse_command_line(cls):
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, *args):
        super().__init__(*args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
    
    def SvcDoRun(self):
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                             servicemanager.PYS_SERVICE_STARTED,
                             (self._svc_name_, ''))
        self.main()

    def start(self):
        pass

    def stop(self):
        self.background_tasks.kill()
        self.server.kill()

    def main(self):
        #check license 

        os.chdir(os.path.join(WORKING_DIR, 'server'))
        self.background_tasks =subprocess.Popen(
            ['../python/python.exe', 'manage.py', 'process_tasks'], 
            env=ENVIRONMENT)
        self.server = subprocess.Popen(['../python/python.exe', 'manage.py', 'runserver', '0.0.0.0:8000'], 
            env=ENVIRONMENT)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(UmisoftService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(UmisoftService)