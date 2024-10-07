from flask import Flask, jsonify, request, redirect, url_for,session, send_from_directory
import os
import time
import json
import requests
from libs.ConfigFile import ConfigFile
from libs.utils import link_tags, nl2br, wrapped_url_for,u2s,time_link,set_timezone
from libs.models import db
from routes import main, tags, settings
SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
try:
    set_timezone()
except Exception as e:
    pass
app = Flask(
    __name__,
    "/static",
    "static"
)  
# https://developers.home-assistant.io/docs/add-ons/communication
# https://developers.home-assistant.io/docs/api/rest
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable default caching behavior for static files

CONFIG_PATH = '/config'
# if windows
if os.name == 'nt':
    CONFIG_PATH = 'C:/config'
    
ADDON_FILES_DIR_PATH = f'{CONFIG_PATH}/Journal'
#abspath = os.path.abspath(__file__)
ADDON_FILES_DIR_PATH = os.path.abspath(ADDON_FILES_DIR_PATH)
ADDON_CONFIG_FILE = f'{ADDON_FILES_DIR_PATH}/config.json'
UPLOAD_FOLDER = f'{ADDON_FILES_DIR_PATH}/uploads'
if os.path.exists(UPLOAD_FOLDER) == False:
    os.makedirs(UPLOAD_FOLDER)


#static file cache prevent
@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response

app.filesystem_paths = {}
app.filesystem_paths['ADDON_CONFIG_FILE'] = ADDON_CONFIG_FILE
app.filesystem_paths['ADDON_FILES_DIR_PATH'] = ADDON_FILES_DIR_PATH
app.filesystem_paths['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Check If FirstTime Running
if not os.path.exists(ADDON_FILES_DIR_PATH):
    os.makedirs(ADDON_FILES_DIR_PATH)
app.config_file = ConfigFile(ADDON_CONFIG_FILE)
app.config['secret_key'] = os.urandom(24)
# secret_key
app.secret_key = app.config['secret_key']
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{ADDON_FILES_DIR_PATH}/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Register the custom filter in Flask
app.jinja_env.filters['link_tags'] = link_tags
app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['u2s'] = u2s
app.jinja_env.filters['time_link'] = time_link

app.wrapped_url_for = wrapped_url_for
@app.context_processor
def override_url_for():
    global wrapped_url_for
    return dict(url_for=wrapped_url_for,ourl_for=url_for)


db.init_app(app)
#init db
with app.app_context():
    db.create_all()
    db.session.commit()
    
# Register Blueprints
main.register_blueprint(app)
tags.register_blueprint(app)
settings.register_blueprint(app)


with app.app_context():
    db.create_all()
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
