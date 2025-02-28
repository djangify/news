# -*- coding: utf-8 -*-
import datetime
import os
import sys

# Define the Python interpreter (needed for cPanel)
INTERP = "/home/djangify/virtualenv/news_aggregator/3.10/bin/python"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add your site directory to the Python path
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SITE_ROOT)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_aggregator.settings')

# Simple fallback application for testing
def simple_app(environ, start_response):
    status = '200 OK'
    output = b'Hello World THIS IS News Aggregator!'
    response_headers = [('Content-type', 'text/plain'),
                       ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]

# Try to load the Django application, use simple_app as fallback
try:
    # First check if we can import Django
    import django

    # Then try to get the WSGI application
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    
    # If that works, add the path info fix
    class PassengerPathInfoFix:
        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            from urllib.parse import unquote
            request_uri = unquote(environ.get('REQUEST_URI', ''))
            script_name = unquote(environ.get('SCRIPT_NAME', ''))
            offset = request_uri.startswith(script_name) and len(script_name) or 0
            environ['PATH_INFO'] = request_uri[offset:].split('?', 1)[0]
            return self.app(environ, start_response)

    application = PassengerPathInfoFix(application)
    
except Exception as err:
    # Log the error with proper encoding
    with open(os.path.join(SITE_ROOT, 'wsgi_error.log'), 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now()}: {str(err)}\n")
    # If anything fails, use the simple application
    application = simple_app