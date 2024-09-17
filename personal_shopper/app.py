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
from Libs.todo_list_api import get_todo_items, add_item, remove_item
from Libs.DiscoverEngine import DiscoverEngine

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
app = Flask(__name__)  

# Set the base URL

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
ADDON_CONFIG_FILE = f'{ADDON_FILES_DIR_PATH}/config.json'
ADDON_SUGGESTIONS_DB_FILE = f'{ADDON_FILES_DIR_PATH}/suggestions.db'
ADDON_DISCOVER_CSV_FILE = f'{ADDON_FILES_DIR_PATH}/Discovery.csv'

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
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }

    todo_list_entitiy_id = config_file.get('todo_list_entitiy_id')
    if not todo_list_entitiy_id or todo_list_entitiy_id == "":
        # Set up the headers
        if request.args.get('entity_id'):
            entity_id = request.args.get('entity_id')
            config_file.set('todo_list_entitiy_id', entity_id)
            return go_home(request)

        else:
            # Define the URL
            url = 'http://supervisor/core/api/states'
            # Make the GET request
            response = requests.get(url, headers=headers)

            states =  response.json()
            return render_template('setup.html', states=states)
    else:
        suggestions_manager = SuggestionsManager(ADDON_SUGGESTIONS_DB_FILE)
        todo_items = get_todo_items(todo_list_entitiy_id)
        needs_action_todo_items = [item for item in todo_items if item['status'] != 'needs_action']
        suggestion_count = 20
        if request.args.get('suggestion_count'):
            suggestion_count = int(request.args.get('suggestion_count'))
        if request.args.get('category_filter'):
            suggestions = suggestions_manager.suggest_items([item['summary'] for item in todo_items], suggestion_count, request.args.get('category_filter'))
        else:
            suggestions = suggestions_manager.suggest_items([item['summary'] for item in todo_items], suggestion_count)
        categories = suggestions_manager.get_categories()
        return render_template(
            'index.html',
            needs_action_todo_items=needs_action_todo_items,
            suggestions=suggestions,
            categories=categories,
            active_tab = "main",
        )  




#discover new foods
@app.route('/discover', methods=['GET'])
def discover():
    discover_engine = DiscoverEngine()
    if request.args.get('category_filter'):
        discoveries = discover_engine.discover(75, category=request.args.get('category_filter'))
    else:
        discoveries = discover_engine.discover(75)
    categories = discover_engine.get_categories()
    return render_template('discover.html', suggestions=discoveries, categories=categories,active_tab = "discover")

#settings_update_all_categories
@app.route('/settings_update_all_categories', methods=['get'])
def settings_update_all_categories():
    suggestions_manager = SuggestionsManager(ADDON_SUGGESTIONS_DB_FILE)
    category_engine = CategoryEngine()
    for item in suggestions_manager.get_all_items():
        logging.info(f"Updating category for {item}")
        category = category_engine.guess(item)
        suggestions_manager.update_category(item, category)


    return go_home(request)






@app.route('/process_completed', methods=['GET'])
def process_completed():
    suggestions_manager = SuggestionsManager(ADDON_SUGGESTIONS_DB_FILE)
    todo_items = get_todo_items(config_file.get('todo_list_entitiy_id'))
    completed = []
    for item in todo_items:
        if item['status'] == 'completed':
            completed.append(item['summary'])
            remove_item(config_file.get('todo_list_entitiy_id'), item['summary'])
    suggestions_manager.touch_items(completed)
    return go_home(request)
    
#add_suggestion
@app.route('/add_suggestion', methods=['get'])
def add_suggestion():
    suggestions_manager = SuggestionsManager(ADDON_SUGGESTIONS_DB_FILE)
    item_name = request.args.get('suggestion')
    add_item(config_file.get('todo_list_entitiy_id'), item_name)
    return go_home(request)

#settings_change_list
@app.route('/settings_change_list', methods=['get'])
def settings_change_list():
    config_file.set('todo_list_entitiy_id',"")
    return go_home(request)

#remove_suggestion
@app.route('/remove_suggestion', methods=['get'])
def remove_suggestion():
    suggestions_manager = SuggestionsManager(ADDON_SUGGESTIONS_DB_FILE)
    item_name = request.args.get('suggestion')
    suggestions_manager.remove_item(item_name)
    return go_home(request)

#remove_todo_item
@app.route('/remove_todo_item', methods=['get'])
def remove_todo_item():
    item_name = request.args.get('item')
    remove_item(config_file.get('todo_list_entitiy_id'), item_name)
    return go_home(request)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        todo_list_entitiy_id = request.form['todo_list_entitiy_id']
        config_file.set('todo_list_entitiy_id', todo_list_entitiy_id)
        return go_home(request)
    else:
        return render_template('settings.html', todo_list_entitiy_id=config_file.get('todo_list_entitiy_id'),active_tab = "settings")
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
