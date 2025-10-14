# storage.py
import json
import os

FILENAME = "local_activity.json"

def save_state(data: dict):
    try:
        with open(FILENAME, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Error saving state:", e)

def load_state():
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, "r") as f:
                return json.load(f)
        except Exception as e:
            print("Error loading state:", e)
            return {}
    return {}