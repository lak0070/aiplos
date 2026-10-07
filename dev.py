"""Run the current WSGI dashboard locally; use Gunicorn for hosted deployments."""
import os
from wsgiref.simple_server import make_server

# Use one exact loopback origin so the browser and API origin check agree.
os.environ['PUBLIC_ORIGIN'] = 'http://127.0.0.1:8000'
from wsgi import application

if __name__ == '__main__':
    with make_server('127.0.0.1', 8000, application) as server:
        print('AIPLOS: http://127.0.0.1:8000 (Ctrl+C to stop)')
        server.serve_forever()
