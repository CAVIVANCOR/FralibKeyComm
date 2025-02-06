import json

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        pass