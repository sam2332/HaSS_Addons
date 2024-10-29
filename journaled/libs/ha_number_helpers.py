import requests
import os

import requests
import os
from datetime import datetime

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')




def create_input_number(name, initial_value=0, min_value=0, max_value=100, step=1):
    if os.environ.get('DISABLE_HAOS_API') == '1':
        return "HAOS API is disabled"
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    url = 'http://supervisor/core/api/services/input_number/create'  # Adjust if needed

    entity_id = f"input_number.{name.lower().replace(' ', '_')}"
    data = {
        "name": name,
        "initial": initial_value,
        "min": min_value,
        "max": max_value,
        "step": step,
        "mode": "slider"
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return f"Input Number created with ID: {entity_id}"
    else:
        return f"Failed to create Input Number: {response.text}"
    
def list_input_numbers():
    if os.environ.get('DISABLE_HAOS_API') == '1':
        return []
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    url = 'http://supervisor/core/api/states'  # Adjust if needed

    response = requests.get(url, headers=headers)
    all_entities = response.json()

    input_numbers = [entity for entity in all_entities if entity['entity_id'].startswith('input_number')]
    return input_numbers


def increment_input_number(entity_id):
    if os.environ.get('DISABLE_HAOS_API') == '1':
        return "HAOS API is disabled"
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    url = f'http://supervisor/core/api/states/{entity_id}'  # Adjust if needed

    # Fetch current value
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Failed to get current value: {response.text}"
    
    current_value = response.json()['state']
    new_value = float(current_value) + 1  # Assuming the step is 1 for incrementing

    # Set new value
    data = {
        "state": new_value
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return f"Input Number incremented to {new_value}"
    else:
        return f"Failed to increment Input Number: {response.text}"
