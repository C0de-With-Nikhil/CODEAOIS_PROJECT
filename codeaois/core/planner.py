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
    
    installed_agents = get_installed_agents()
    for agent in installed_agents:
        if agent in prompt_lower:
            return f"{agent}_agent" 
            
    ds_keywords = ["dataframe", "pandas", "numpy", "plot", "matplotlib", "seaborn", "csv", "dataset", "jupyter", "ipynb", "machine learning"]
    if any(kw in prompt_lower for kw in ds_keywords):
        return "data_science"
        
    tech_nouns = ["script", "code", "python", "function", "app", "program", "system", "file", "bot", "website", "module", "html", "css", "javascript", "api", "database", "sql"]
    action_verbs = ["write", "create", "build", "make", "generate", "update", "fix", "debug", "refactor", "change", "edit", "modify"]
    
    # --- THE FIX: DYNAMIC FILE DETECTION ---
    common_extensions = [".py", ".js", ".html", ".css", ".json", ".txt", ".csv", ".md"]
    has_file_extension = any(any(word.endswith(ext) for ext in common_extensions) for word in prompt_lower.split())
    
    has_action = any(v in prompt_lower for v in action_verbs)
    has_noun = any(n in prompt_lower.split() for n in tech_nouns)
    
    # If they use an action verb + (a tech word OR a specific filename), it's CODE!
    if (has_noun or has_file_extension) and has_action:
        return "code"
    elif (has_noun or has_file_extension) and len(prompt_lower.split()) > 3:
        return "code"
        
    return "chat"