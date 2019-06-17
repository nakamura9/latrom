from server import app
import webview
import threading
import time
import os

def create_browser_window():
    webview.create_window('Installer', 'http://localhost:5000/')

def start_server():
    app.run(host='127.0.0.1', port='5000', threaded=True)

if __name__ == '__main__':
    t = threading.Timer(1.5, start_server)
    t.daemon =True
    t.start()
    create_browser_window()