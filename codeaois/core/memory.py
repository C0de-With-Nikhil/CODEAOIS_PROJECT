import json
import os
from pathlib import Path
from supabase import create_client, Client

# Setup hidden directory in the user's home folder
HOME_DIR = Path.home() / ".codeaois"
HOME_DIR.mkdir(exist_ok=True)

PROFILE_PATH = HOME_DIR / "profile.json"
HISTORY_PATH = HOME_DIR / "history.json"
SETTINGS_PATH = HOME_DIR / "settings.json"
SESSION_PATH = HOME_DIR / "session.json" 

# --- CLOUD CONFIGURATION ---
SUPABASE_URL = "https://glqjztnlwgfiewgrrjwk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdscWp6dG5sd2dmaWV3Z3JyandrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM0NjgyNjYsImV4cCI6MjA4OTA0NDI2Nn0.J14vujO9GJ-TAsngmKo5Z7vRUApR5Xh1RRhKe1MNowM"

def get_cloud_client():
    """Returns a Supabase client if keys are set, else None."""
    if not SUPABASE_URL or "YOUR_SUPABASE" in SUPABASE_URL: 
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

def sync_to_cloud(user_email, data_type, content):
    """Pushes local json data to the Supabase cloud user_data table."""
    client = get_cloud_client()
    if not client or not user_email: 
        return
    try:
        client.table("user_data").upsert({
            "email": user_email,
            "data_type": data_type, # 'history' or 'profile'
            "payload": content
        }).execute()
    except:
        pass

def pull_from_cloud(user_email, data_type):
    """Fetches global history/profile when logging into a new PC."""
    client = get_cloud_client()
    if not client or not user_email: 
        return None
    try:
        response = client.table("user_data").select("payload").eq("email", user_email).eq("data_type", data_type).execute()
        return response.data[0]['payload'] if response.data else None
    except:
        return None

# --- PROFILE & LOGIN ---
def load_profile():
    if PROFILE_PATH.exists():
        with open(PROFILE_PATH, "r") as f:
            return json.load(f)
    return None

def save_profile(data):
    # 1. Save Locally
    with open(PROFILE_PATH, "w") as f:
        json.dump(data, f, indent=4)
    # 2. Sync to Cloud
    if data and data.get('email'):
        sync_to_cloud(data['email'], 'profile', data)

# --- SETTINGS ---
def load_settings():
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    return {
        "use_custom_api_key": False,
        "custom_api_key": "",
        "ui_theme": "cyan",
        "bg_theme": "#231e20",
        "logo_animation": "4"
    }

def save_settings(settings_data):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings_data, f, indent=4)

# --- TOKEN TRACKER ---
def log_token_usage(prompt_tokens: int, completion_tokens: int):
    stats = {"prompt": 0, "completion": 0}
    if SESSION_PATH.exists():
        with open(SESSION_PATH, "r") as f:
            stats = json.load(f)
            
    stats["prompt"] += prompt_tokens
    stats["completion"] += completion_tokens
    
    with open(SESSION_PATH, "w") as f:
        json.dump(stats, f, indent=4)
        
    # Sync tokens to the Cloud Identity!
    profile = load_profile()
    if profile and profile.get('email'):
        sync_to_cloud(profile['email'], 'session', stats)

def get_session_stats():
    if SESSION_PATH.exists():
        with open(SESSION_PATH, "r") as f:
            return json.load(f)
    return {"prompt": 0, "completion": 0}

def restore_cloud_tokens(email):
    """Pulls tokens from cloud for existing users, or resets to 0 for new users."""
    cloud_session = pull_from_cloud(email, 'session')
    if cloud_session:
        with open(SESSION_PATH, "w") as f:
            json.dump(cloud_session, f, indent=4)
        return True
    else:
        # Reset to 0 for new user
        with open(SESSION_PATH, "w") as f:
            json.dump({"prompt": 0, "completion": 0}, f, indent=4)
        return False
    
def get_session_stats():
    if SESSION_PATH.exists():
        with open(SESSION_PATH, "r") as f:
            return json.load(f)
    return {"prompt": 0, "completion": 0}

# --- HISTORY & CLEANUP ---
def load_history():
    # 1. Try Local first
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, "r") as f:
            hist = json.load(f)
            if hist: return hist
    # 2. Try Cloud recovery if local is empty
    profile = load_profile()
    if profile and profile.get('email'):
        cloud_hist = pull_from_cloud(profile['email'], 'history')
        if cloud_hist:
            save_history(cloud_hist) # Cache it locally
            return cloud_hist
    return []

def save_history(history):
    # 1. Save Locally
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=4)
    # 2. Sync to Cloud
    profile = load_profile()
    if profile and profile.get('email'):
        sync_to_cloud(profile['email'], 'history', history)

def clear_history_data():
    if HISTORY_PATH.exists():
        os.remove(HISTORY_PATH)

def clear_profile_data():
    # Added SESSION_PATH back so tokens reset to 0 for new users!
    paths = [PROFILE_PATH, SETTINGS_PATH, SESSION_PATH, HISTORY_PATH] 
    for p in paths:
        if p.exists():
            os.remove(p)