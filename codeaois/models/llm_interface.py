import requests
import json
from codeaois.core.memory import load_settings, log_token_usage

PROXY_URL = "https://codeaois-proxy.vercel.app/api/chat"

def call_openrouter(system_prompt: str, user_prompt: str, intent: str = "chat", history: list = None) -> str:
    """Handles API calls, dynamically routing between Cloud Proxy or Local Custom Key."""
    
    settings = load_settings()
    use_custom = settings.get("use_custom_api_key", False)
    custom_key = settings.get("custom_api_key", "")

    # Clean, premium models list (Strictly free to prevent stealth charges)
    models_to_try = [
        "liquid/lfm-2.5-1.2b-thinking:free",
        "arcee-ai/trinity-large-preview:free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "google/gemma-3-27b-it:free"
    ]

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})

    for model in models_to_try:
        payload = {"model": model, "messages": messages}

        try:
            if use_custom and custom_key:
                # BYPASS PROXY: Direct connection to OpenRouter (Fixes 60s timeout!)
                headers = {
                    "Authorization": f"Bearer {custom_key}",
                    "HTTP-Referer": "https://codeaois.com",
                    "X-Title": "CodeAOIS Local",
                    "Content-Type": "application/json"
                }
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=300 # 5 Minute timeout for massive code files!
                )
            else:
                # SECURE PROXY: Route through Vercel
                response = requests.post(
                    url=PROXY_URL,
                    json=payload,
                    timeout=55
                )
            
            # Skip model if overloaded or out of credits
            if response.status_code in [503, 402, 429]:
                continue 
                
            response.raise_for_status()
            data = response.json()
            
            # NEW: Track tokens used!
            usage = data.get("usage", {})
            log_token_usage(usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))
            
            return data["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException:
            continue 

    return "Error: The AI network is currently overloaded. Please try again or add a Custom API Key using /setting."