# codeaois/core/planner.py
import os
from pathlib import Path

def get_installed_agents() -> list:
    agents_dir = Path(__file__).resolve().parent.parent / "agents"
    if not agents_dir.exists():
        return []
    
    agents = []
    for f in os.listdir(agents_dir):
        if f.endswith("_agent.py") and f not in ["coder_agent.py", "data_science_agent.py", "git_agent.py"]:
            agents.append(f.replace("_agent.py", ""))
    return agents

def analyze_intent(user_prompt: str) -> str:
    prompt_lower = user_prompt.lower().strip()
    
    # --- 1. STRICT CONVERSATIONAL OVERRIDES ---
    # If a prompt starts with these words, force Chat Mode immediately!
    chat_triggers = ["explain", "why", "how", "what", "who", "good job", "thanks", "hello", "hi", "hey"]
    if any(prompt_lower.startswith(trigger) for trigger in chat_triggers):
        return "chat"
    
    # --- 2. DYNAMIC PLUGINS ---
    installed_agents = get_installed_agents()
    for agent in installed_agents:
        if agent in prompt_lower:
            return f"{agent}_agent" 
            
    # --- 3. DATA SCIENCE ---
    ds_keywords = ["dataframe", "pandas", "numpy", "plot", "matplotlib", "seaborn", "csv", "dataset", "jupyter", "ipynb", "machine learning"]
    if any(kw in prompt_lower for kw in ds_keywords):
        return "data_science"
        
    # --- 4. CODER AGENT ---
    tech_nouns = ["script", "code", "python", "function", "app", "program", "system", "file", "bot", "website", "module", "html", "css", "javascript", "api", "database", "sql"]
    action_verbs = ["write", "create", "build", "make", "generate", "update", "fix", "debug", "refactor", "change", "edit", "modify", "connect", "link"]
    common_extensions = [".py", ".js", ".html", ".css", ".json", ".txt", ".csv", ".md"]
    
    has_file_extension = any(any(word.endswith(ext) for ext in common_extensions) for word in prompt_lower.split())
    has_action = any(v in prompt_lower for v in action_verbs)
    has_noun = any(n in prompt_lower.split() for n in tech_nouns)
    
    # The Golden Rule: It ONLY writes code if it has an Action Verb AND (a Tech Noun OR File Extension)
    # We removed the buggy "len > 3" fallback here!
    if (has_noun or has_file_extension) and has_action:
        return "code"
        
    # --- 5. DEFAULT FALLBACK ---
    return "chat"