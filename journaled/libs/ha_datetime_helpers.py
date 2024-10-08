import requests
import os
import logging
import requests
import os
from datetime import datetime

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')

def list_datetime_helpers():
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    url = 'http://supervisor/core/api/states'  # Replace with your actual Home Assistant URL if different

    response = requests.get(url, headers=headers)
    all_entities = response.json()

    datetime_helpers = [entity for entity in all_entities if entity['entity_id'].startswith('input_datetime')]
    return datetime_helpers



def update_datetime_helper(entity_id):
    headers = {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json'
    }
    url = 'http://supervisor/core/api/states/' + entity_id  # Replace with your actual Home Assistant URL if different
    current_time = datetime.now().isoformat()
    logging.info(f"Updating {entity_id} to {current_time   }")
    data = {
        "state": current_time
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()



