"""Local WSGI entry point; FLASK CLI also supports `--app app`."""
import os

from waitress import serve
from app import create_app

app = create_app()

if __name__ == '__main__':
    serve(app, host=os.environ.get('HOST', '127.0.0.1'), port=int(os.environ.get('PORT', '5000')))
