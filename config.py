import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_key() -> str:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("api_key", "")
    return ""


def save_key(key: str):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": key}, f)
