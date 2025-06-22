import json
import os

def load_data(filepath):
    """
    Load JSON data from the given file path.
    Returns an empty list if the file does not exist.
    """
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(filepath, data):
    """
    Save data as JSON to the given file path.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
