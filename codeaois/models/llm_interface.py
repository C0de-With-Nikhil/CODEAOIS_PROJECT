# codeaois/models/llm_interface.py
import os
import requests
import json
from pathlib import Path

def get_api_key() -> str:
    key = os.getenv("OPENROUTER_API_KEY")
    if key: return key
    
    base_dir = Path(__file__).resolve().parent.parent
    possible_paths = [base_dir / ".env", base_dir.parent / ".env"]
    
    for env_path in possible_paths:
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "OPENROUTER_API_KEY" in line.upper():
                        parts = line.split("=", 1)
                        if len(parts) > 1: return parts[1].strip().strip('\'"')
    return ""

# --- ADDED HISTORY PARAMETER ---
def call_openrouter(system_prompt: str, user_prompt: str, intent: str = "chat", history: list = None) -> str:
    """Handles API calls with split fallback loops and conversation memory."""
    api_key = get_api_key()
    if not api_key:
        return "[Error]: Failed to extract OPENROUTER_API_KEY."

    if intent in ["code", "data_science"]:
        models_to_try = [
            "stepfun/step-3.5-flash:free",
            "qwen/qwen3-vl-30b-a3b-thinking:free",
            "qwen/qwen3-vl-235b-a22b-thinking:free",
            "stepfun/step-3.5-flash:free"
        ]
    else:
        models_to_try = [
            "liquid/lfm-2.5-1.2b-thinking:free",
            "arcee-ai/trinity-large-preview:free",
            "liquid/lfm-2.5-1.2b-instruct:free",
            "arcee-ai/trinity-mini:free"
        ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/codeaois/codeaois",
        "X-Title": "CodeAOIS Developer OS",
        "Content-Type": "application/json"
    }

    # --- BUILD THE MEMORY PAYLOAD ---
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})

    for model in models_to_try:
        print(f"📡 [LLM Interface] Routing request to {model}...")
        payload = {
            "model": model,
            "messages": messages
        }

        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=45
            )
            
            if response.status_code == 429:
                print(f"   -> ⚠️ Server overloaded (429). Instantly falling back to next free model...")
                continue
                
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException:
            print(f"   -> ⚠️ Network error on {model}. Trying fallback...")
            continue

    return "[API Error]: All free models in this category are overloaded. Please try again in 60 seconds."