# config.py
import json
import os

CONFIG_FILE = "config.json"

def load_json():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_json(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def set_config_key(key, value):
    data = load_json()
    data[key] = value
    save_json(data)
