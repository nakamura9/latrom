import subprocess


def backup_db():
    # -z compresses the database
    subprocess.run(['python', 'manage.py', 'dbbackup', '-z'])