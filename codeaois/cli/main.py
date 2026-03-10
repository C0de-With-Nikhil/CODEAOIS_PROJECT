# codeaois/cli/main.py
import argparse
import sys
import os
import importlib 

# --- NEW: THE PROFESSIONAL CLI ENGINE ---
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML

from codeaois.core.planner import analyze_intent, get_installed_agents
from codeaois.core.context import extract_file_context
from codeaois.brain.scanner import scan_project_structure
from codeaois.models.llm_interface import call_openrouter
from codeaois.agents.coder_agent import generate_code
from codeaois.agents.data_science_agent import generate_ds_code
from codeaois.utils.file_writer import extract_and_save_code
from codeaois.agents.git_agent import auto_commit
from codeaois.core.marketplace import install_agent
from codeaois.core.memory import load_profile, create_profile, load_history, save_history, clear_history_data, clear_profile_data

# Print Colors
C_BLUE = '\033[94m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_PURPLE = '\033[95m'
C_CYAN = '\033[96m'
C_RESET = '\033[0m'
C_BOLD = '\033[1m'

chat_history = load_history()

# --- CONFIGURE AUTOCOMPLETE OPTIONS ---
AVAILABLE_COMMANDS = [
    '/help', '/clear', '/clear_history', '/clear_user', 
    '/status', '/marketplace', '/install', '/exit', '/quit'
]
command_completer = WordCompleter(AVAILABLE_COMMANDS, ignore_case=True)

def print_logo():
    logo = f"""{C_BLUE}{C_BOLD}
   ____          _        _    ___ _____  _____ 
  / ___|___   __| | ___  / \\  / _ \\_   _|/ ____|
 | |   / _ \\ / _` |/ _ \\/ _ \\| | | || | | (___  
 | |__| (_) | (_| |  __/ ___ \\ |_| || |_ \\___ \\ 
  \\____\\___/ \\__,_|\\___/_/   \\_\\___/_____|____/ 
{C_RESET}"""
    print(logo)
    print(f"{C_CYAN}  ▶ Advanced AI Developer OS v0.1.0{C_RESET}")
    print(f"{C_CYAN}  ▶ Type /help to see available commands.{C_RESET}\n")

def show_help():
    print(f"\n{C_PURPLE}=== CodeAOIS Command Center ==={C_RESET}")
    print(f"{C_YELLOW}/marketplace{C_RESET}   - View available specialized agents")
    print(f"{C_YELLOW}/install <x>{C_RESET}   - Download an agent (e.g., /install database)")
    print(f"{C_YELLOW}/clear{C_RESET}         - Clear the terminal screen")
    print(f"{C_YELLOW}/clear_history{C_RESET} - Wipe your conversation memory")
    print(f"{C_YELLOW}/clear_user{C_RESET}    - Wipe your profile and restart setup")
    print(f"{C_YELLOW}/status{C_RESET}        - View current OS constraints and active models")
    print(f"{C_YELLOW}/exit{C_RESET}          - Close the CodeAOIS environment")
    print(f"{C_PURPLE}==============================={C_RESET}\n")

def show_status():
    print(f"\n{C_BLUE}[OS Status]{C_RESET}")
    print(" 🟢 Core Engine: Online")
    print(" 🟢 Model Router: Liquid/Arcee (Chat) | Step/Qwen (Code)")
    print(" 🟢 Project Brain: Active")
    print(" 🟢 Plugin Architecture: Dynamic Auto-Discovery")
    print(" 🟢 UI Engine: Prompt Toolkit (Ghost Text Active)")
    print(" 🟢 Security Dry-Run: Enabled\n")

def process_command(user_input: str):
    global chat_history
    clean_input = user_input.lower().strip()
    
    if clean_input in ["/exit", "/quit", "exit", "quit"]:
        print(f"\n{C_GREEN}👋 Terminating CodeAOIS session. Happy coding!{C_RESET}")
        sys.exit(0)
        
    if clean_input == "/help":
        show_help()
        return
        
    if clean_input == "/clear":
        os.system('clear' if os.name == 'posix' else 'cls')
        print_logo()
        return
        
    if clean_input == "/clear_history":
        chat_history.clear() 
        clear_history_data() 
        print(f"\n{C_GREEN}🧹 Conversation history wiped clean. I have amnesia!{C_RESET}\n")
        return
        
    if clean_input == "/clear_user":
        clear_profile_data() 
        print(f"\n{C_GREEN}👤 User profile deleted. Exiting so you can restart setup...{C_RESET}\n")
        sys.exit(0) 
        
    if clean_input == "/status":
        show_status()
        return

    if clean_input == "/marketplace":
        installed = get_installed_agents()
        print(f"\n{C_PURPLE}🛒 CODEAOIS AGENT MARKETPLACE{C_RESET}")
        
        available_agents = {
            "database": "SQL, NoSQL, ORM optimization",
            "3d": "Three.js, WebGL, Unity scripts",
            "debugging": "Deep stack trace analysis",
            "devops": "Docker, CI/CD, Terraform"
        }
        
        for agent, desc in available_agents.items():
            if agent in installed:
                status = f"{C_GREEN}[Installed]{C_RESET}"
            else:
                status = f"{C_YELLOW}[Not Installed]{C_RESET}"
            print(f"  - {agent:<10} {status:<24} ({desc})")
            
        print(f"\nTo install an agent, type: {C_YELLOW}/install <agent_name>{C_RESET}\n")
        return

    if clean_input.startswith("/install"):
        parts = clean_input.split()
        if len(parts) > 1:
            agent_target = parts[1].strip()
            install_agent(agent_target)
        else:
            print(f"\n{C_YELLOW}⚠️  Missing agent name! Please specify an agent (e.g., /install database){C_RESET}\n")
        return

    print(f"\n{C_CYAN}[System]{C_RESET} Analyzing intent...")
    intent = analyze_intent(user_input)
    
    if intent == "chat":
        print(f"{C_BLUE}💬 [Chat Mode]{C_RESET} Asking AI...")
        
        profile = load_profile()
        user_name = profile["name"] if profile else "Developer"
        user_role = profile["role"] if profile else "Coding"
        
        system_prompt = f"You are CodeAOIS, an advanced AI Developer OS. The user's name is {user_name} and they focus on {user_role}. Be helpful, concise, and conversational."
        
        response = call_openrouter(system_prompt, user_input, intent="chat", history=chat_history)
        print(f"\n{C_BOLD}🤖 CodeAOIS:{C_RESET} {response}\n")
        
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})
        if len(chat_history) > 20: chat_history = chat_history[-20:]
        save_history(chat_history)
        
    elif intent in ["code", "data_science"] or intent.endswith("_agent"):
        
        if intent == "data_science":
            print(f"{C_PURPLE}📊 [Data Science Mode]{C_RESET} Engaging specialized agent...")
        elif intent == "code":
            print(f"{C_GREEN}⚙️ [Code Mode]{C_RESET} Engaging Coder agent...")
        else:
            plugin_name = intent.replace('_agent', '').title()
            print(f"{C_PURPLE}🔌 [Plugin Mode]{C_RESET} Engaging specialized {plugin_name} Agent...")
            
        target_file, file_context = extract_file_context(user_input)
        if target_file:
            print(f"   📂 Target file locked: {target_file}")
            
        print(f"   🧠 Scanning project context...")
        project_tree = scan_project_structure()
        
        brain_context = f"\n--- Project Structure Overview ---\n{project_tree}\n----------------------------------\n"
        full_context = brain_context + file_context if file_context else brain_context
            
        print(f"   {C_YELLOW}⚡ Generating code...{C_RESET}")
        
        if intent == "data_science":
            code_result = generate_ds_code(user_input, full_context)
        elif intent == "code":
            code_result = generate_code(user_input, full_context)
        else:
            try:
                module = importlib.import_module(f"codeaois.agents.{intent}")
                func_name = f"generate_{intent.replace('_agent', '')}_code"
                agent_func = getattr(module, func_name)
                code_result = agent_func(user_input, full_context)
            except Exception as e:
                print(f"\n{C_YELLOW}⚠️ Error executing plugin {intent}: {e}{C_RESET}")
                return
        
        if target_file:
            save_path = target_file
        else:
            print("\n" + "-"*50)
            custom_name = input(f"{C_BLUE}📁 Enter filename with extension (e.g., app.py): {C_RESET}").strip()
            save_path = custom_name if custom_name else "untitled_generation.txt"
            print("-"*50)
        
        success = extract_and_save_code(code_result, default_filename=save_path)
        if success:
            auto_commit(save_path, message=f"CodeAOIS auto-update: {save_path} via {intent}")
            
    else:
        print(f"{C_YELLOW}❓ Unknown intent. Please try rephrasing.{C_RESET}")

def main():
    parser = argparse.ArgumentParser(
        description="CodeAOIS: Advanced AI Developer OS",
        usage="codeaois [prompt] or codeaois [options]"
    )
    parser.add_argument("prompt", nargs="*", help="Chat or command for CodeAOIS")
    parser.add_argument("-v", "--version", action="version", version="CodeAOIS Core Engine v0.1.0")
    args = parser.parse_args()

    profile = load_profile()
    if not profile:
        profile = create_profile()

    if args.prompt:
        user_input = " ".join(args.prompt)
        process_command(user_input)
        sys.exit(0)

    os.system('clear' if os.name == 'posix' else 'cls')
    print_logo()
    
    if profile:
        print(f"{C_CYAN}  Welcome back, {profile.get('name', 'Developer')}!{C_RESET}\n")
    
    # --- INITIALIZE THE PROMPT TOOLKIT SESSION ---
    session = PromptSession(
        completer=command_completer,
        auto_suggest=AutoSuggestFromHistory(),
        complete_while_typing=True
    )
    
    while True:
        try:
            # The new interactive prompt with bold green formatting!
            user_input = session.prompt(HTML('<b><ansigreen>CodeAOIS></ansigreen></b> ')).strip()
            if not user_input:
                continue
            process_command(user_input)
        except KeyboardInterrupt:
            print(f"\n{C_GREEN}👋 Terminating CodeAOIS session. Happy coding!{C_RESET}")
            sys.exit(0)

if __name__ == "__main__":
    main()