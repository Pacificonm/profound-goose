import json
import os


def save_command_tracker(data, filename="command_tracker.json"):
    with open(filename, 'w') as file:
        json.dump(data, file)


def load_command_tracker(filename="command_tracker.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}
