import os
import json

CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.captive_portal_config.json')
DEFAULT_LOG_PATH = os.path.join(os.path.expanduser('~'), 'captive_portal_app.log')

DEFAULT_CONFIG = {
    "check_interval_seconds": 30,
    "log_path": DEFAULT_LOG_PATH
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Merge with defaults in case of missing keys
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception:
        return False
