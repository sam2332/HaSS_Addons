import requests
import os

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')

def get_todo_items(todo_list_entitiy_id):
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    url = 'http://supervisor/core/api/services/todo/get_items?return_response'  # Replace with your actual Home Assistant URL

    data = {
        "entity_id": todo_list_entitiy_id
    }
    response = requests.post(url, headers=headers, json=data)
    todo_items = []
    raw_todo_items =  response.json()
    for todo_item in raw_todo_items['service_response'][todo_list_entitiy_id]['items']:
        todo_items.append(todo_item)
    return todo_items


def add_item(todo_list_entitiy_id, item_name):
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    url = 'http://supervisor/core/api/services/todo/add_item'
    data = {
        "entity_id": todo_list_entitiy_id,
        "item": item_name
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def remove_item(todo_list_entitiy_id, item_name):
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    url = 'http://supervisor/core/api/services/todo/remove_item'
    data = {
        "entity_id": todo_list_entitiy_id,
        "item": item_name
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def get_all_todo_lists():
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    url = 'http://supervisor/core/api/states'
    response = requests.get(url, headers=headers)
    return response.json()