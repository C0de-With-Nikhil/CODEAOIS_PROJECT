import requests
import time
from codeaois.core.memory import load_settings, log_token_usage
import base64
import mimetypes

PROXY_URL = "https://codeaois-proxy.vercel.app/api/chat"

def fetch_available_models(api_key, provider="openrouter"):
    """Fetches the live list of models based on the active API provider."""
    try:
        if provider == "gemini":
            # Direct connection to Google AI Studio
            resp = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", timeout=10)
            if resp.status_code == 200:
                # Filter for text/chat models and strip the "models/" prefix
                return [m["name"].split("/")[-1] for m in resp.json().get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]
        
        elif provider == "groq":
            headers = {"Authorization": f"Bearer {api_key}"}
            resp = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=10)
            if resp.status_code == 200:
                return [model["id"] for model in resp.json().get("data", [])]
                
        elif provider == "openai":
            headers = {"Authorization": f"Bearer {api_key}"}
            resp = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
            if resp.status_code == 200:
                return [model["id"] for model in resp.json().get("data", [])]
                
        else: # Default OpenRouter
            headers = {"Authorization": f"Bearer {api_key}"}
            resp = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
            if resp.status_code == 200:
                return [model["id"] for model in resp.json().get("data", [])]
                
    except Exception as e:
        return []
    return []

def encode_image(image_path):
    """Converts a local image into a Base64 string for the AI to read."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')
    
def call_openrouter(system_prompt: str, user_prompt: str, intent: str = "chat", history: list = None, image_path: str = None) -> str:
    """Handles API calls, dynamically routing between Cloud Proxy or Local Custom Key."""
    
    settings = load_settings()
    use_custom = settings.get("use_custom_api_key", False)
    custom_key = settings.get("custom_api_key", "")
    custom_model = settings.get("custom_model", "")
    provider = settings.get("custom_api_provider", "openrouter")

    # --- DUAL-BRAIN ARCHITECTURE ---
    if intent == "supervisor":
        # Fast, free brain for background tasks
        models_to_try = ["meta-llama/llama-3.1-8b-instruct:free"]
    elif use_custom and custom_key and custom_model:
        # Custom Pro brain for actual work
        models_to_try = [custom_model]
    else:
        # CodeAOIS Global Free Fallback List
        models_to_try = [
            "liquid/lfm-2.5-1.2b-thinking:free",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "google/gemma-3-27b-it:free",
            "meta-llama/llama-3.1-8b-instruct:free",
            "mistralai/mistral-7b-instruct:free"
        ]

    messages = [{"role": "system", "content": system_prompt}]
    if history: messages.extend(history)
    
    # --- VISION INTEGRATION ---
    if image_path:
        mime_type = mimetypes.guess_type(image_path)[0] or "image/png"
        base64_img = encode_image(image_path)
        messages.append({
            "role": "user", 
            "content": [
                {"type": "text", "text": user_prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_img}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": user_prompt})
        
    for model in models_to_try:
        payload = {"model": model, "messages": messages}

        try:
            if use_custom and custom_key and intent != "supervisor":
                # --- DYNAMIC UNIVERSAL ROUTING ---
                if provider == "gemini":
                    api_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
                    headers = {"Authorization": f"Bearer {custom_key}", "Content-Type": "application/json"}
                elif provider == "groq":
                    api_url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {custom_key}", "Content-Type": "application/json"}
                elif provider == "openai":
                    api_url = "https://api.openai.com/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {custom_key}", "Content-Type": "application/json"}
                else: # Default OpenRouter
                    api_url = "https://openrouter.ai/api/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {custom_key}", "HTTP-Referer": "https://codeaois.com", "X-Title": "CodeAOIS"}
                
                response = requests.post(api_url, headers=headers, json=payload, timeout=300)
            else:
                response = requests.post(PROXY_URL, json=payload, timeout=55)
            
            # --- BULLETPROOF ERROR HANDLING ---
            if response.status_code != 200:
                if use_custom and intent != "supervisor":
                    # Only show raw errors to Pro users
                    return f"❌ **API Error {response.status_code} ({provider.upper()})**\nThis usually means you are out of credits, hit a rate limit, or the key is invalid.\n*Details: {response.text}*"
                else:
                    # Free API users: wait 1 second and try the next model silently
                    time.sleep(1)
                    continue 
                    
            response.raise_for_status()
            data = response.json()
            
            usage = data.get("usage", {})
            log_token_usage(usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))
            
            return data["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            if use_custom and intent != "supervisor":
                return f"❌ **API Connection Error:**\n{e}"
            continue 

    return "Error: The AI network is heavily rate-limited right now. Please try again in a few moments, or activate a Custom API Key using /setting."