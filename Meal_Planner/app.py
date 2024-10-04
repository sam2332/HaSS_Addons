from flask import Flask, jsonify, request, redirect, url_for, render_template # type: ignore
import os
import time
import logging
logging.basicConfig(level=logging.INFO)
import json
import requests
from Libs.ConfigFile import ConfigFile
from Libs.SuggestionsManager import SuggestionsManager
from Libs.CategoryEngine import CategoryEngine
from Libs.todo_list_api import get_todo_items, add_item, remove_item,get_all_todo_lists
from Libs.DiscoverEngine import DiscoverEngine

app = Flask(__name__)  

# Fixes url_for when running behind a reverse proxy
@app.context_processor
def override_url_for():
    def wrapped_url_for(endpoint, **values):
        # Get the ingress path from the request headers
        ingress_path = request.headers.get('X-Ingress-Path', '')
        if ingress_path:
            # Use the ingress path from the header to build the URL
            return f"{ingress_path}{url_for(endpoint, **values)}"
        else:
            # Fallback to normal url_for if no ingress path is found
            return url_for(endpoint, **values)
    return dict(url_for=wrapped_url_for)

# https://developers.home-assistant.io/docs/add-ons/communication
# https://developers.home-assistant.io/docs/api/rest

CONFIG_PATH = '/config/'
ADDON_FILES_DIR_PATH = f'{CONFIG_PATH}/PersonalShopper'
ADDON_CONFIG_FILE = f'{ADDON_FILES_DIR_PATH}/Config.json'
ADDON_SUGGESTIONS_DB_FILE = f'{ADDON_FILES_DIR_PATH}/Suggestions.db'

# Check If FirstTime Running
if not os.path.exists(ADDON_FILES_DIR_PATH):
    os.makedirs(ADDON_FILES_DIR_PATH)

config_file = ConfigFile(ADDON_CONFIG_FILE)

def go_home(request):
    # Get the ingress path from the request headers
    ingress_path = request.headers.get('X-Ingress-Path', '')
    # Redirect to the home page using the ingress path
    return redirect(f"{ingress_path}/")

@app.route('/', methods=['GET', 'POST'])
def main():

    todo_list_entitiy_id = config_file.get('todo_list_entitiy_id')
    if not todo_list_entitiy_id or todo_list_entitiy_id == "":
        if request.args.get('entity_id'):
            entity_id = request.args.get('entity_id')
            config_file.set('todo_list_entitiy_id', entity_id)
            return go_home(request)

        else:
            states = get_all_todo_lists()
            return render_template('setup.html', states=states)
    else:
      
        return render_template(
            'index.html',
            todo_list_entitiy_id=todo_list_entitiy_id,
            active_tab = "main",
        )  




#settings_change_list
@app.route('/settings_change_list', methods=['get'])
def settings_change_list():
    config_file.set('todo_list_entitiy_id',"")
    return go_home(request)

@app.route('/settings', methods=['GET'])
def settings():
    todo_list_entitiy_id=config_file.get('todo_list_entitiy_id')
    return render_template(
        'settings.html',
        todo_list_entitiy_id=todo_list_entitiy_id,
        active_tab = "settings"
    )
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
