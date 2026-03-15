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
    
    prompt_lower = prompt.lower()
    prompt_clean = prompt_lower.strip()
    
    # 0. ZERO-LATENCY GREETINGS (Don't waste API calls on "hi")
    if prompt_clean in ["hi", "hello", "hey", "yo", "sup", "test", "who are you", "help"]:
        return "chat"
    
    # --- 🏗️ AUTO-SCAFFOLDER TRIGGER ---
    scaffold_triggers = [
        "scaffold", "build a full project", "create a full project", 
        "generate an app", "create a new project", "multi-file", 
        "multiple files", "project structure", "make me a project",
        "build a directory", "generate a workspace", "create an app"
    ]
    if any(trigger in prompt_lower for trigger in scaffold_triggers):
        return "scaffolder_agent"
    
    # --- 🚀 THE BULLETPROOF OVERRIDE ---
    # If the prompt explicitly asks for code, force the Swarm instantly!
    code_triggers = ["write the code", "write code", "build a", "create a", "implement", "script for"]
    if any(trigger in prompt_lower for trigger in code_triggers):
        return "code"  # Instantly routes to the Multi-Agent Swarm!
        
    # If using your /lite command
    if prompt_lower.startswith("/lite "):
        return "lite_code"
    # -----------------------------------

# --- 🌐 AUTO-RESEARCHER TRIGGER ---
    # Instantly trigger the live web search for common real-world question formats
    search_triggers = ["who won", "who is", "what is the current", "news about", "search for", "look up", "tell me about the", "who wins"]
    if any(trigger in prompt_lower for trigger in search_triggers):
        return "researcher_agent"

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

Available Categories:
- chat: General conversation, logic, explaining existing code, or brainstorming.
- researcher_agent: CRITICAL for any questions about recent events, current news, sports results, updated documentation, or if they explicitly ask to search the web.
- code: Writing, editing, or generating Python/JS/HTML scripts.
- data_science: Pandas, plotting, CSV analysis, machine learning.
- pip_agent: Installing Python packages (pip install).
- git_agent: save my work,Committing, pushing, version control.
- terminal_agent: Bash commands, creating directories.
- database_agent: SQL, NoSQL, database schemas.
- devops_agent: Docker, CI/CD, AWS, deployment.
- code: Writing, editing, or generating code in ANY programming language (Rust, Go, C++, Java, JS, Python, HTML, etc.).
- vision_agent: Used ONLY when the user asks to "test", "look at", "review", or "see" an HTML/UI file.
- researcher_agent: MUST be used for ANY questions about current events, sports, weather, news, real-world facts, or whenever the user asks "who", "what", "where", or "when" about non-coding topics.
- researcher_agent: MUST be used for ANY questions about current events, sports, weather, news, real-world facts, or whenever the user asks "who", "what", "where", or "when" about non-coding topics.
- scaffolder_agent: MUST be used when the user asks to "scaffold", "build a full project", "create an app structure", or generate multiple files/folders at once.
Respond with ONLY the exact category name in lowercase. No other text."""

    try:
        # THE FIX: Added the visual spinner back so the terminal doesn't look frozen!
        with console.status("[dim]🧠 Supervisor analyzing intent...[/dim]", spinner="dots"):
        # Pass intent="supervisor" so llm_interface knows to use the strict, free routing brain!
            response = call_openrouter(router_sys_prompt, prompt, intent="supervisor", history=[])
        
        # Clean up the AI's response
        intent_raw = response.strip().lower()
        intent_clean = re.sub(r'[^a-z_]', '', intent_raw)

        valid_intents = [
            "chat", "code", "data_science", "pip_agent", "git_agent", 
            "terminal_agent", "database_agent", "devops_agent", 
            "debugging_agent", "3d_agent", "researcher_agent", "vision_agent", "scaffolder_agent"
        ]
        
        # 1. First, check if the AI followed instructions and gave an EXACT match
        for valid in valid_intents:
            if valid == intent_clean:
                return valid
                
        # 2. If it was chatty, look for the keyword inside the sentence
        for valid in valid_intents:
            if valid in intent_clean:
                return valid
                
        return "chat" # Default fallback
        
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