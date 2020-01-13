import os
import sys 
import subprocess
from winreg import *

dir = os.getcwd()
try:
    print('Installing latrom')
    print('Is the current directory the one you want to install'
        ' the application in?')
    print(dir)

    val = input('y or n: ')
    while val not in ['y', 'n']:
        val = input('y or n: ')

    if val == 'n':
        print('Please copy the application files to the desired'
            ' directory and start again')
        input('Press enter to exit.')
        sys.exit()

    print('installing dependancies')
    os.chdir(os.path.join(dir, 'service', 'bin'))
    result = subprocess.run('./vc_redist.x64.exe')
    if result.returncode != 0:
        print('some dependencies were not properly installed')


    print('creating database')
    os.chdir(os.path.join(dir,'service', 'server'))
    results = subprocess.run(['../python/python.exe', 'manage.py', 'migrate'])
    if results.returncode != 0:
        print("Failed to make migrations")
        input('Press enter to exit.')
        sys.exit()

    print('installing fixtures')
    results = subprocess.run(['../python/python.exe', 'manage.py', 'loaddata', 
        'accounts.json', 'journals.json', 'settings.json', 'common.json', 
        'employees.json', 'inventory.json', 'invoicing.json', 'planner.json', 
        'payroll.json'])


    if results.returncode != 0:
        print("Failed to install fixtures")
        input('Press enter to exit.')
        sys.exit()

    print('installing service')
    
    try:
        key = CreateKey(HKEY_LOCAL_MACHINE, r'SOFTWARE\\suave')
        SetValueEx(key, "SERVICE_PATH", 0, REG_SZ, os.path.join(dir, 'service', 'service'))
        CloseKey(key)
    except Exception as e:
        print(e)
        print("failed to install registry")
        input('press enter to exit')
        sys.exit()

    os.chdir(os.path.join(dir, 'service', 'service'))
    result = subprocess.run(['service.exe', '--startup=auto', 'install'], 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        print("Failed to install service")
        input('press enter to exit')
        sys.exit()

    result = subprocess.run(['service.exe', 'start'])

    if result.returncode != 0:
        print("Failed to start service")
        
    print("Application installed successfully")
    input('Press any key to exit')
    sys.exit()
except Exception as e:
    print(e)
    input('press enter key to exit.')
