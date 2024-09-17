import requests
import os

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')

def get_todo_items(todo_list_entitiy_id):
    
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    # Set up your URL and headers
    url = 'http://supervisor/core/api/services/todo/get_items?return_response'  
    # Define your data (service_data)
    data = {
        "entity_id": todo_list_entitiy_id
    }
    # Make the POST request
    response = requests.post(url, headers=headers, json=data)
    todo_items = []
    # Print out the result
    raw_todo_items =  response.json()
    for todo_item in raw_todo_items['service_response'][todo_list_entitiy_id]['items']:
        todo_items.append(todo_item)
        
    return todo_items

def add_item(todo_list_entitiy_id, item_name):
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    # Set up your URL and headers
    url = 'http://supervisor/core/api/services/todo/add_item'
    data = {
        "entity_id": todo_list_entitiy_id,
        "item": item_name
    }
    # Make the POST request
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def remove_item(todo_list_entitiy_id, item_name):
    
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    # Set up your URL and headers
    url = 'http://supervisor/core/api/services/todo/remove_item'
    data = {
        "entity_id": todo_list_entitiy_id,
        "item": item_name
    }
    # Make the POST request
    response = requests.post(url, headers=headers, json=data)
    return response.json()
