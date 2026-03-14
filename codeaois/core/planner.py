import os
import re
from rich.console import Console
from codeaois.models.llm_interface import call_openrouter

console = Console()

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
    
    # 1. FAST LOCAL CATCHES
    if any(word in prompt_lower for word in ["exit", "quit", "shut down", "goodbye"]):
        return "sys_exit"
    if any(word in prompt_lower for word in ["setting", "settings", "theme", "background"]) and any(action in prompt_lower for action in ["change", "open", "set", "show"]):
        return "sys_settings"
    if "clear" in prompt_lower and any(word in prompt_lower for word in ["screen", "terminal", "chat"]):
        return "sys_clear"
    if any(word in prompt_lower for word in ["marketplace", "install agent", "download agent", "plugins"]):
        return "sys_marketplace"

    # 2. LLM SUPERVISOR ROUTER
    router_sys_prompt = """You are the CodeAOIS Supervisor Engine.
Your ONLY job is to classify the user's prompt into exactly ONE category.
CRITICAL RULE: If the user is just asking a question, asking for an explanation, or brainstorming (even if they mention a filename like 'memory.py'), you MUST classify it as "chat". 
ONLY classify as "code" if they explicitly command you to write, generate, modify, or create a script.

Available Categories:
- chat: Explanations, questions, reading files, brainstorming.
- code: Writing, editing, or generating Python/JS/HTML scripts.
- data_science: Pandas, plotting, CSV analysis, machine learning.
- pip_agent: Installing Python packages (pip install).
- git_agent: Committing, pushing, version control.
- terminal_agent: Bash commands, creating directories.
- database_agent: SQL, NoSQL, database schemas.
- devops_agent: Docker, CI/CD, AWS, deployment.

Respond with ONLY the exact category name in lowercase. No other text."""

    try:
        # THE FIX: Added the visual spinner back so the terminal doesn't look frozen!
        with console.status("[dim]🧠 Supervisor analyzing intent...[/dim]", spinner="dots"):
            # Pass an empty history so the router only focuses on the current prompt
            response = call_openrouter(router_sys_prompt, prompt, intent="chat", history=[])
        
        # Clean up the AI's response to ensure it's just the exact category string
        intent = response.strip().lower()
        intent = re.sub(r'[^a-z_]', '', intent)

        valid_intents = [
            "chat", "code", "data_science", "pip_agent", "git_agent", 
            "terminal_agent", "database_agent", "devops_agent", 
            "debugging_agent", "3d_agent"
        ]
        
        for valid in valid_intents:
            if valid in intent:
                return valid
                
        return "chat" # Default fallback if the AI gets confused
        
    except Exception:
        # 3. FAILSAFE ROUTER (If the internet/proxy drops, fall back to smart keywords)
        return _fallback_keyword_router(prompt_lower)

def _fallback_keyword_router(prompt_lower: str) -> str:
    """Legacy keyword routing as a backup safety net."""
    words = prompt_lower.replace("?", " ").replace("!", " ").replace(".", " ").replace(",", " ").split()
    
    if any(word in prompt_lower for word in ["terminal", "bash", "mkdir", "run command", "execute", "touch"]):
        return "terminal_agent"
    if any(word in prompt_lower for word in ["git", "commit", "push", "version control"]):
        return "git_agent"
    if any(word in prompt_lower for word in ["pip install", "install package"]):
        return "pip_agent"
    if any(w in words for w in ["data", "csv", "pandas", "plot", "graph"]):
        return "data_science"
        
    # Made the code trigger stricter: requires a VERB and a NOUN
    if any(verb in prompt_lower for verb in ["write", "create", "generate", "build", "code me"]) and any(noun in prompt_lower for noun in ["script", "app", "python", "html"]):
        return "code"
        
    return "chat"