# storage.py
import json
import os

FILENAME = "local_activity.json"

def save_state(data: dict):
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=4)

def load_state():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            return json.load(f)
    return {}