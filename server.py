# Import the Flask app from app.py
from app import app

# ASGI wrapper with /api prefix support
from asgiref.wsgi import WsgiToAsgi
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Flask as FlaskApp

# Mount Flask app at /api
mounted_app = DispatcherMiddleware(FlaskApp('dummy'), {
    '/api': app
})

# Convert to ASGI for Uvicorn
app = WsgiToAsgi(mounted_app)
