from flask import render_template, jsonify, redirect, url_for, request
from server import app
import os
import json
from tkinter import filedialog
from tkinter import *
import subprocess
import shutil
import urllib
from contextlib import closing

MANAGE_DIR = os.path.abspath('../..')
DB_DIR = os.path.abspath('..')

dbs = []
for _, __, files in os.walk('..'):
    for file in files:
        if file.endswith('.sqlite3'):
            dbs.append(file)


@app.route('/home')
def home():
    current = ""
    with open('../config.json') as conf_file:
        conf = json.load(conf_file)
        current = conf['current']
    return render_template('home.html',database=current)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select-database')
def select_database():
    global dbs
    return render_template('select_database.html', options=dbs)

@app.route('/selected-database/<selection>')
def selected_database(selection):
    global dbs
    selected_db = dbs[int(selection) -1]
    with open('../config.json', 'w') as config:
        json.dump({
            'current': selected_db,
            'db_list': dbs
        }, config)
    return render_template('selection_success.html', selected=selected_db)


@app.route('/create-database', methods=['GET', 'POST'])
def create_database():
    if request.method == 'POST':
        os.chdir(DB_DIR)
        dbname = request.form['name']
        db = open(dbname + '.sqlite3', 'w')
        db.close()
        

        #dump persistant data such as accounts, employees etc.
        # make sure it is in the dir of manage.py
        os.chdir(MANAGE_DIR)
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
        os.chdir(DB_DIR)


        #change the current database for the particular command.
        conf = None
        with open('config.json', 'r') as conf_file:
            conf = json.load(conf_file)
            conf['current'] = dbname + '.sqlite3'

        with open('config.json', 'w') as conf_file:
            json.dump(conf, conf_file)


        # make sure it is in the dir of manage.py
        os.chdir(MANAGE_DIR)

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
        return f'Database {dbname} created successfully'

    else:
        return render_template('create_database.html')

@app.route('/restore-database')
def restore_backup():
    return render_template('restore_backup.html')

@app.route('/open-file')
def open_file():
    root = Tk()
    path = filedialog.askopenfilename()
    root.destroy()
    os.chdir(MANAGE_DIR)
    result = subprocess.run(
                ['python', 'manage.py', 'dbrestore', '-i', path])
    if result.returncode != 0:
        return 'Error during backup restore.'

    return 'backup restored successfully'

@app.route('/load-network-backup')
def load_network_backup():
    
    url = request.form['resource_location']
    filename = url.split('/')[-1]
    path = os.path.join('..', 'backups', filename)
    try:
        with closing(urllib.urlopen(url)) as r:
            with open(path, 'wb') as f:
                shutil.copyfilobj(r, f)

    except Exception as e:
       return f'failed to load resource because of {e}'
    
    else:
        os.chdir(MANAGE_DIR)
        result = subprocess.run(
            ['python', 'manage.py', 'dbrestore', '-i', path])
        if result.returncode != 0:
            return 'failed to load backup.'
        
        return 'backup loaded successfully.'


@app.route('/set-backup', methods=['GET', "POST"])
def set_backup():
    if request.method == "POST":
        conf = None
        root = Tk()
        path = filedialog.askdirectory()
        with open('../config.json', 'r') as conf_file:
            conf = json.load(conf_file)
            conf['backup_dir'] = path

        with open('../config.json', 'w') as conf_file:
            json.dump(conf, conf_file)

        root.destroy()

        return f"{path}"
    else:
        backup_dir = None 
        with open('../config.json', 'r') as conf_file:
            conf = json.load(conf_file)
            backup_dir = conf.get('backup_dir', "")
        return render_template('backup.html', current=backup_dir)
