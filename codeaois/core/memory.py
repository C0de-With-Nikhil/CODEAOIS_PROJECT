import json
import os
from pathlib import Path

# Setup hidden directory in the user's home folder
HOME_DIR = Path.home() / ".codeaois"
HOME_DIR.mkdir(exist_ok=True)

PROFILE_PATH = HOME_DIR / "profile.json"
HISTORY_PATH = HOME_DIR / "history.json"
SETTINGS_PATH = HOME_DIR / "settings.json"
SESSION_PATH = HOME_DIR / "session.json" # <-- NEW: Tracks token usage!

# --- PROFILE & LOGIN ---
def load_profile():
    if PROFILE_PATH.exists():
        with open(PROFILE_PATH, "r") as f:
            return json.load(f)
    return None

def save_profile(data):
    with open(PROFILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

# --- SETTINGS (Phase 1) ---
def load_settings():
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    # Default Settings if it's the user's first time
    return {
        "use_custom_api_key": False,
        "custom_api_key": ""
    }

def save_settings(settings_data):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings_data, f, indent=4)

# --- TOKEN TRACKER (New Idea!) ---
def log_token_usage(prompt_tokens: int, completion_tokens: int):
    stats = {"prompt": 0, "completion": 0}
    if SESSION_PATH.exists():
        with open(SESSION_PATH, "r") as f:
            stats = json.load(f)
    
    stats["prompt"] += prompt_tokens
    stats["completion"] += completion_tokens
    
    with open(SESSION_PATH, "w") as f:
        json.dump(stats, f, indent=4)

def get_session_stats():
    if SESSION_PATH.exists():
        with open(SESSION_PATH, "r") as f:
            return json.load(f)
    return {"prompt": 0, "completion": 0}

# --- HISTORY & CLEANUP ---
def load_history():
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=4)

def clear_history_data():
    if HISTORY_PATH.exists():
        os.remove(HISTORY_PATH)

def clear_profile_data():
    if PROFILE_PATH.exists():
        os.remove(PROFILE_PATH)
    if SETTINGS_PATH.exists():
        os.remove(SETTINGS_PATH)
    if SESSION_PATH.exists():
        os.remove(SESSION_PATH)