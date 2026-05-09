import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

MODELS = ["gpt-image-2", "gpt-image-1", "dall-e-2"]
FORMATS = ["PNG", "JPEG", "WEBP"]


def _load() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def _save(data: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_key() -> str:
    return _load().get("api_key", "")


def save_key(key: str):
    data = _load()
    data["api_key"] = key
    _save(data)


def load_paths() -> tuple[str, str]:
    data = _load()
    return data.get("source_folder", ""), data.get("dest_folder", "")


def save_paths(source: str, dest: str):
    data = _load()
    data["source_folder"] = source
    data["dest_folder"] = dest
    _save(data)


def load_model() -> str:
    return _load().get("model", MODELS[0])


def save_model(model: str):
    data = _load()
    data["model"] = model
    _save(data)


def load_format() -> str:
    return _load().get("format", FORMATS[0])


def save_format(fmt: str):
    data = _load()
    data["format"] = fmt
    _save(data)
