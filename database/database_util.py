"""
The database util is used to select databases for use by the system.
It iterates over all the database files in this folder and presents them to the 
admin as options for selection.
It also iterates over all the backups for the currently selected database and 
performs restoration as necessary
The tool must also support copying backups to other folders or to network locations.
The backup service is automated but there should be a backup now button for immediate backups.

"""

import json
import os
import sys
import datetime
import re
import shutil
import urllib
from contextlib import closing
import subprocess
from tkinter import filedialog
from tkinter import *




def restore_backup():
    '''Allows restoration of backups from dumps of local files or dumps stored remotely.'''
    print("Restore from:")
    print("1. Local File")
    print("2. Network Location")

    option = ''
    while option not in ['1', '2']:
        option = input("select an option: ")

    if option == '1':
        root=Tk()

        while True:
            path = filedialog.askopenfilename()

        
            os.chdir('..')
            result = subprocess.run(
                ['python', 'manage.py', 'dbrestore', '-i', path])
            if result.returncode == 1:
                
                retry = input('Failed to restore file. Try again?(y/n)')
                if retry == 'y':
                    continue
                break
            else:
                print('database restored successfully.')
                break
        root.destroy()
    else:
        while True:
            url = input('Enter backup network resource address')
            filename = url.split('/')[-1]
            try:
                with closing(urllib.urlopen(url)) as r:
                    with open(filename, 'wb') as f:
                        shutil.copyfilobj(r, f)

            except:
                print('failed to load resource.')
                retry = input('Try Again? (y/n)')
                if retry == 'y':
                    continue
                else:
                    break


def create_new_database():
    
    name = ""
    dbname = ""
    while True :
        name = input('Enter the name of the new database: ')
        dbname = name + '.sqlite3'    
        if os.path.exists(dbname):
            print("Database with this name exists")
            continue

        if re.match('\w', name):
            break

    db = open(dbname, 'w')
    db.close()
    DBDIR = os.getcwd()
    

    #dump persistant data such as accounts, employees etc.
    # make sure it is in the dir of manage.py
    os.chdir('..')
    subprocess.run(['python', 
            'manage.py', 
            'dumpdata', 
            'auth',
            'employees',
            'invoicing',
            'inventory',
            'planner',
            'services',
            'accounting',
            'common_data',
            'messaging',
            '--e=invoicing.invoice',
            '--e=invoicing.creditnote',
            '--e=invoicing.creditnoteline',
            '--e=invoicing.payment',
            '--e=auth.permission',
            '--e=inventory.orderpayment',
            '--e=inventory.order',
            '--e=inventory.stockreceipt',
            '--e=inventory.orderitem',
            '--e=inventory.debitnote',
            '--e=inventory.debitnoteline',
            '--e=invoicing.invoiceline',
            '--e=accounting.expense',
            '--e=accounting.credit',
            '--e=accounting.debit',
            '--e=accounting.journalentry',
            '--e=employees.leave',
            '--e=employees.payslip',
            '--e=employees.employeetimesheet',
            '--e=employees.attendanceline',
           '--e=messaging.email',
            '--e=services.serviceworkorder',
            '--e=services.workorderexpense',
            '--e=services.timelog',
            '--e=services.workorderrequest',
            '--e=services.equipmentrequisition',
            '--e=services.equipmentrequisitionline',
            '--e=services.consumablesrequisitionline',
            '--e=services.consumablesrequisition',
            '--e=contenttypes',
             '-o', 'data.json'])
    os.chdir(DBDIR)


    #change the current database for the particular command.
    conf = None
    with open('config.json', 'r') as conf_file:
        conf = json.load(conf_file)
        conf['current'] = name + '.sqlite3'

    with open('config.json', 'w') as conf_file:
        json.dump(conf, conf_file)


    # make sure it is in the dir of manage.py
    os.chdir('..')

    # migrate database
    subprocess.run(['python', 'manage.py', 'migrate'])
    # install fixtures
    subprocess.run(['python', 'manage.py', 'loaddata', 'accounts.json', 
                    'journals.json', 'settings.json',
                    'common.json', 'employees.json', 'inventory.json', 
                    'invoicing.json', 'planner.json', 
                    'data.json'])# obtained from the data dump

    print("Database created successfully.")
    if os.path.exists('data.json'):
        os.remove('data.json')


def select_database():
    dbs = []
    for _, __, files in os.walk('.'):
        for file in files:
            if file.endswith('.sqlite3'):
                dbs.append(file)

    print("Listed Below are the currently available databases")
    for i, dbname in enumerate(dbs, 1):
        print(f"{i}. {dbname}")

    while True:
        selection = input('Please select a database to get started:')
        try:
            selection = int(selection)
        except:
            continue

        if selection > len(dbs) or selection < 1:
            continue

        selected_db = dbs[selection-1]
        print(f'You have selected the database {selected_db}')
        conf = None
        with open('config.json', 'r') as conf_file:
            conf = json.load(conf_file)
            conf['current'] = selected_db
            conf['db_list'] = dbs

        with open('config.json', 'w') as conf_file:
            json.dump(conf, conf_file)

        # keep db up to date
        os.chdir('..')
        subprocess.run(['python', 'manage.py', 'migrate'])
        break


if __name__ == "__main__":
    print("Welcome to Suave DButil")
    print("Please ensure the server is not running concurrently with this utility")
    print("=======================")
    print("1. Select a database")
    print("2. Restore a backup")
    print("3. Create a new database")
    print("4. Quit")

    option = ''
    while option not in ['1', '2', '3', '4']:
        option = input("What would you like to do?")

        if option == '1':
            select_database()

        elif option == '2':
            restore_backup()
        elif option =="3":
            create_new_database()
        else:
            break
