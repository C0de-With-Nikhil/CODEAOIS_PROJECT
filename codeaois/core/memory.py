# codeaois/core/memory.py
import os
import json
from pathlib import Path

PROFILE_PATH = Path.home() / ".codeaois_profile.json"
HISTORY_PATH = Path.home() / ".codeaois_history.json" # <-- NEW: Persistent history file

def load_profile():
    """Loads the user's profile if it exists."""
    if PROFILE_PATH.exists():
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def create_profile():
    """The one-time signup process."""
    print("\n" + "*"*50)
    print("🌟 Welcome to CodeAOIS! Let's set up your developer profile.")
    print("*"*50)
    
    name = input("What is your name? ").strip()
    role = input("What is your primary focus? (e.g., Data Science student, Web Dev): ").strip()
    
    profile = {
        "name": name,
        "role": role,
    }
    
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=4)
        
    print(f"\n✅ Profile created! Nice to meet you, {name}.")
    print(f"Your memory is securely stored at: {PROFILE_PATH}")
    print("*"*50 + "\n")
    
    return profile

def load_history() -> list:
    """Loads previous chat history from the hard drive."""
    if HISTORY_PATH.exists():
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_history(history_list: list):
    """Saves the current chat history to the hard drive."""
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history_list, f, indent=4)

# codeaois/core/memory.py
# ... [Keep your existing code at the top] ...

def clear_history_data():
    """Deletes the chat history file from the hard drive."""
    if HISTORY_PATH.exists():
        os.remove(HISTORY_PATH)

def clear_profile_data():
    """Deletes the user profile file from the hard drive."""
    if PROFILE_PATH.exists():
        os.remove(PROFILE_PATH)