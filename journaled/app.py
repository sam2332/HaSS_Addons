from flask import Flask, jsonify, request, redirect, url_for,session
import os
import time
import json
import requests
from libs.ConfigFile import ConfigFile
from libs.utils import link_tags, nl2br, wrapped_url_for,u2s
from libs.models import db
from routes import main, tags, settings
SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
app = Flask(__name__)  
app.debug = True
# https://developers.home-assistant.io/docs/add-ons/communication
# https://developers.home-assistant.io/docs/api/rest

CONFIG_PATH = '/config'
ADDON_FILES_DIR_PATH = f'{CONFIG_PATH}/Journal'
#abspath = os.path.abspath(__file__)
ADDON_FILES_DIR_PATH = os.path.abspath(ADDON_FILES_DIR_PATH)
ADDON_CONFIG_FILE = f'{ADDON_FILES_DIR_PATH}/config.json'
# Check If FirstTime Running
if not os.path.exists(ADDON_FILES_DIR_PATH):
    os.makedirs(ADDON_FILES_DIR_PATH)
app.config_file = ConfigFile(ADDON_CONFIG_FILE)
app.config['secret_key'] = os.urandom(24)
# secret_key
app.secret_key = app.config['secret_key']
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{ADDON_FILES_DIR_PATH}/app.db'
print(app.config['SQLALCHEMY_DATABASE_URI'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Register the custom filter in Flask
app.jinja_env.filters['link_tags'] = link_tags
app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['u2s'] = u2s

app.wrapped_url_for = wrapped_url_for
@app.context_processor
def override_url_for():
    global wrapped_url_for
    return dict(url_for=wrapped_url_for)


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
