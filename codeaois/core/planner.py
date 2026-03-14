import os

def get_installed_agents():
    agent_dir = os.path.join(os.path.dirname(__file__), '..', 'agents')
    installed = []
    if os.path.exists(agent_dir):
        for file in os.listdir(agent_dir):
            if file.endswith('_agent.py') and file not in ['__init__.py', 'coder_agent.py', 'data_science_agent.py', 'git_agent.py', 'terminal_agent.py']:
                installed.append(file.replace('_agent.py', ''))
    return installed

def analyze_intent(prompt: str) -> str:
    prompt_lower = prompt.lower()
    words = prompt_lower.replace("?", " ").replace("!", " ").replace(".", " ").replace(",", " ").split()
    
    if any(word in prompt_lower for word in ["exit", "quit", "shut down", "goodbye"]):
        return "sys_exit"
    if any(word in prompt_lower for word in ["setting", "settings", "theme", "background"]):
        if any(action in prompt_lower for action in ["change", "open", "set", "show"]):
            return "sys_settings"
    if "clear" in prompt_lower and any(word in prompt_lower for word in ["screen", "terminal", "chat"]):
        return "sys_clear"
    if any(word in prompt_lower for word in ["marketplace", "install agent", "download agent", "plugins"]):
        return "sys_marketplace"
        
    # --- Terminal Routing ---
    if any(word in prompt_lower for word in ["terminal", "bash", "mkdir", "run command", "execute", "touch", "create folder"]):
        return "terminal_agent"
        
    # --- Git Routing ---
    if any(word in prompt_lower for word in ["git", "commit", "push", "save my work", "version control", "github"]):
        return "git_agent"
        
    if any(word in prompt_lower for word in ["pip install", "install package", "python package", "pip module"]):
        return "pip_agent"
    if any(word in prompt_lower for word in ["database", "sql", "nosql", "postgres", "mongodb"]):
        return "database_agent"
    if any(word in prompt_lower for word in ["docker", "deploy", "ci/cd", "aws", "kubernetes"]):
        return "devops_agent"
    if any(word in prompt_lower for word in ["debug", "fix this error", "traceback"]):
        return "debugging_agent"
    if any(word in prompt_lower for word in ["3d", "webgl", "three.js", "shader"]):
        return "3d_agent"
        
    if any(w in words for w in ["data", "csv", "pandas", "plot", "graph"]):
        return "data_science"
    if any(w in words for w in ["code", "html", "python", "function", "script", "app", "css", "js"]):
        return "code"
        
    return "chat"