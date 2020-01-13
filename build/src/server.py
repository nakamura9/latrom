from waitress import serve

from latrom.wsgi import application

if __name__ == "__main__":
    serve(application, port='8989')