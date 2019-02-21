import subprocess
import os 
import sys

BASE_DIR = os.getcwd()

print('Starting reverse proxy')
os.chdir(os.path.join(BASE_DIR, "bin", "nginx"))
subprocess.Popen(["nginx.exe"])# so it is nonblocking


print("Starting Server...")
os.chdir(os.path.join(BASE_DIR, "server"))
proc_server = subprocess.run(["python", "server.py"])

