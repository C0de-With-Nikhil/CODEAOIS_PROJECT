# codeaois/cli/main.py
import argparse
import sys
import os
import importlib 

# --- CLI UI ENGINES ---
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table # <-- ADD THIS!

# --- CODEAOIS MODULES ---
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
from codeaois.agents.tester_agent import run_test

# Print Colors
C_BLUE = '\033[94m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_PURPLE = '\033[95m'
C_CYAN = '\033[96m'
C_RESET = '\033[0m'
C_BOLD = '\033[1m'

# Globals
console = Console()
chat_history = load_history()
active_file = None  # The OS remembers the file you are working on

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
    print(" 🟢 UI Engine: Prompt Toolkit & Rich Markdown")
    print(" 🟢 Security Dry-Run: Enabled\n")

def process_command(user_input: str):
    global chat_history, active_file
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
        
        # --- 1. THE EXPANDED AGENT REGISTRY ---
        available_agents = {
            "database": {
                "desc": "SQL, NoSQL, ORM",
                "summary": "Writes optimized queries, designs schemas, and handles database migrations."
            },
            "3d": {
                "desc": "Three.js, WebGL, Unity",
                "summary": "Generates complex 3D math, shaders, and game engine scripts."
            },
            "debugging": {
                "desc": "Deep Error Analysis",
                "summary": "Reads crash logs, finds root causes, and suggests exact line-by-line fixes."
            },
            "devops": {
                "desc": "Docker, CI/CD, AWS",
                "summary": "Writes Dockerfiles, GitHub Actions, and infrastructure automation."
            }
        }
        
        # --- 2. BUILD THE STUNNING UI TABLE ---
        print("\n")
        table = Table(title="🛒 CodeAOIS Agent Marketplace", border_style="purple", header_style="bold cyan")
        table.add_column("Agent Name", style="bold white", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Core Focus", style="magenta")
        table.add_column("Agent Capabilities", style="dim")
        
        for agent, info in available_agents.items():
            if agent in installed:
                status = "[bold green]✓ Installed[/bold green]"
            else:
                status = "[bold yellow]○ Available[/bold yellow]"
                
            table.add_row(agent.title(), status, info["desc"], info["summary"])
            
        console.print(table)
        print("\n")
        
        # --- 3. THE INTERACTIVE AUTO-INSTALLER ---
        choice = input(f"{C_BLUE}Enter an agent name to install (or press Enter to close): {C_RESET}").strip().lower()
        
        if choice in available_agents:
            if choice in installed:
                print(f"{C_YELLOW}⚠️ You already have the {choice.title()} Agent installed!{C_RESET}\n")
            else:
                print(f"{C_GREEN}⬇️ Downloading {choice.title()} Agent from registry...{C_RESET}")
                install_agent(choice)
                print(f"{C_GREEN}✅ {choice.title()} Agent successfully integrated into the OS!{C_RESET}\n")
        elif choice:
            print(f"{C_YELLOW}⚠️ Agent '{choice}' not found in the marketplace.{C_RESET}\n")
            
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
        
        project_tree = scan_project_structure()
        
        system_prompt = (
            f"You are CodeAOIS, an advanced AI Developer OS running directly in the user's terminal. "
            f"The user's name is {user_name} ({user_role}).\n"
            f"CRITICAL: You have FULL access to the user's file system. Here is their current project structure:\n{project_tree}\n"
            f"Currently focused file: {active_file if active_file else 'None'}\n"
            f"If the user asks 'can you see my code' or asks about their files, say YES and reference the project structure. "
            f"DO NOT EVER say you cannot view files."
        )
        
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
        
        # ACTIVE FILE MEMORY
        if not target_file and active_file:
            print(f"   🔗 Auto-locking to previous file: {active_file}")
            target_file = active_file
            if os.path.exists(active_file):
                with open(active_file, "r", encoding="utf-8") as f:
                    file_context = f.read()

        if target_file:
            active_file = target_file
            print(f"   📂 Target file locked: {target_file}")
            
        print(f"   🧠 Scanning project context...")
        project_tree = scan_project_structure()
        
        brain_context = f"\n--- Project Structure Overview ---\n{project_tree}\n----------------------------------\n"
        full_context = brain_context + file_context if file_context else brain_context
            
        print(f"   {C_YELLOW}⚡ Generating code...{C_RESET}")
        
        # --- GENERATE THE CODE_RESULT VARIABLE ---
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
        
        # --- EXTRACT SAVE PATH ---
        if target_file:
            save_path = target_file
        else:
            print("\n" + "-"*50)
            custom_name = input(f"{C_BLUE}📁 Enter filename with extension (e.g., app.py): {C_RESET}").strip()
            save_path = custom_name if custom_name else "untitled_generation.txt"
            print("-"*50)
        
        # --- SAVE AND SHOW SUMMARY ---
        success, ai_summary = extract_and_save_code(code_result, default_filename=save_path)
        if success:
            auto_commit(save_path, message=f"CodeAOIS auto-update: {save_path} via {intent}")
            print("\n")
            md = Markdown(ai_summary)
            console.print(Panel(md, title="[bold cyan]Agent Summary[/bold cyan]", border_style="cyan", expand=False))
            print("\n")
            
            # --- NEW: BRIDGE THE BRAINS ---
            # Inject the coding action into the shared chat memory!
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({
                "role": "assistant", 
                "content": f"[System Log: I successfully generated code and saved it to '{save_path}'. Here is my summary of what I did: {ai_summary}]"
            })
            if len(chat_history) > 20: chat_history = chat_history[-20:]
            save_history(chat_history)
# --- NEW: THE MULTI-AGENT TESTER LOOP ---
            if save_path.endswith('.py'):
                confirm_test = input(f"{C_PURPLE}🧪 [Tester Agent] Shall I execute '{save_path}' to check for errors? [Y/n]: {C_RESET}").strip().lower()
                
                if confirm_test in ['y', '']:
                    print(f"   {C_PURPLE}⚙️ Running tests...{C_RESET}")
                    test_success, test_output = run_test(save_path)
                    
                    if test_success:
                        print(f"{C_GREEN}✅ Test Passed! Terminal Output:\n{C_RESET}{test_output}\n")
                    else:
                        print(f"{C_YELLOW}❌ Test Failed! Crash Log:\n{C_RESET}{test_output}\n")
                        
                        # The Loop-Back!
                        fix_confirm = input(f"{C_PURPLE}🔁 Pass crash log back to Coder Agent to fix? [Y/n]: {C_RESET}").strip().lower()
                        if fix_confirm in ['y', '']:
                            print(f"{C_GREEN}⚙️ Re-Engaging Coder agent for bug fix...{C_RESET}")
                            
                            # Automatically generate a new prompt with the error log
                            fix_prompt = f"I ran {save_path} and got this error:\n{test_output}\nPlease fix the code."
                            
                            # Recursively call the command processor to handle the fix!
                            process_command(fix_prompt)
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
    
    session = PromptSession(
        completer=command_completer,
        auto_suggest=AutoSuggestFromHistory(),
        complete_while_typing=True
    )
    
    while True:
        try:
            user_input = session.prompt(HTML('<b><ansigreen>CodeAOIS></ansigreen></b> ')).strip()
            if not user_input:
                continue
            process_command(user_input)
        except KeyboardInterrupt:
            print(f"\n{C_GREEN}👋 Terminating CodeAOIS session. Happy coding!{C_RESET}")
            sys.exit(0)

if __name__ == "__main__":
    main()