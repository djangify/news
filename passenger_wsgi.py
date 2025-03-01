# -*- coding: utf-8 -*-
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'logs', 'django.log'),
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

try:
    # Add your site directory to the Python path
    SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, SITE_ROOT)
    
    # Define the Python interpreter (needed for cPanel)
    INTERP = "/home/djangify/virtualenv/news_aggregator/3.10/bin/python"
    if sys.executable != INTERP:
        os.execl(INTERP, INTERP, *sys.argv)
    
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_aggregator.settings')
    
    # Import the WSGI application
    from news_aggregator.wsgi import application
    
    # Optional: Passenger path info fix if needed
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

    # Apply the middleware
    application = PassengerPathInfoFix(application)
    
except Exception as e:
    logging.error(f"Failed to start application: {str(e)}", exc_info=True)
    
    # Fallback application that displays the error
    def application(environ, start_response):
        status = '500 Internal Server Error'
        error_msg = f"Application failed to start: {str(e)}"
        output = error_msg.encode('utf-8')
        response_headers = [('Content-type', 'text/plain'),
                          ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]
    