import argparse
import sys
import os
import importlib
import time
import random
import string

# --- CLI UI ENGINES ---
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import radiolist_dialog

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.live import Live
from rich.text import Text

# --- CODEAOIS MODULES ---
from codeaois.core.planner import analyze_intent, get_installed_agents
from codeaois.core.context import extract_file_context
from codeaois.brain.scanner import scan_project_structure
from codeaois.models.llm_interface import call_openrouter
from codeaois.agents.coder_agent import generate_code
from codeaois.agents.data_science_agent import generate_ds_code
from codeaois.utils.file_writer import extract_and_save_code
from codeaois.core.marketplace import install_agent

from codeaois.core.memory import (
    load_profile, save_profile, load_history, save_history, 
    clear_history_data, clear_profile_data, load_settings, save_settings, get_session_stats
)

console = Console(soft_wrap=True)
chat_history = load_history()
active_file = None

AVAILABLE_COMMANDS = [
    '/help', '/clear', '/status', '/s', '/marketplace', '/m', '/setting', '/set', '/exit', '/clear_user'
]
command_completer = WordCompleter(AVAILABLE_COMMANDS, ignore_case=True)

# --- THEME & BACKGROUND ENGINE ---
def get_theme():
    settings = load_settings()
    return settings.get("ui_theme", "cyan")

def set_terminal_background(hex_color):
    sys.stdout.write(f"\033]11;{hex_color}\007")
    sys.stdout.flush()

def apply_saved_background():
    settings = load_settings()
    bg_color = settings.get("bg_theme", "#231e20")
    set_terminal_background(bg_color)

# --- THE MULTI-ANIMATION LOGO ENGINE ---
def print_logo():
    settings = load_settings()
    theme = settings.get("ui_theme", "cyan")
    # Option 4 (Data Sweep) is the default!
    anim_style = str(settings.get("logo_animation", "4")) 
    
    logo_lines = [
        "   ____          _        _    ___ _____  _____ ",
        "  / ___|___   __| | ___  / \\  / _ \\_   _|/ ____|",
        " | |   / _ \\ / _` |/ _ \\/ _ \\| | | || | | (___  ",
        " | |__| (_) | (_| |  __/ ___ \\ |_| || |_ \\___ \\ ",
        "  \\____\\___/ \\__,_|\\___/_/   \\_\\___/_____|____/ "
    ]
    logo_str = "\n".join(logo_lines)

    # 0. Instant (No Animation)
    if anim_style == "0":
        console.print(f"[bold {theme}]{logo_str}[/]")
        console.print(f"  [dim]✦[/dim] [bold white]Advanced Developer OS[/bold white] [dim]v0.2.1[/dim]")
        console.print(f"  [dim]✦[/dim] [dim]Type /help for commands.[/dim]\n")
        return

    try:
        if anim_style == "1": # Classic Hacker Typewriter
            text = Text(style=f"bold {theme}")
            with Live(console=console, refresh_per_second=60, transient=False) as live:
                for char in logo_str:
                    text.append(char)
                    live.update(text)
                    time.sleep(0.002)
                text.append(f"\n  ✦ Advanced Developer OS v0.2.1\n  ✦ Type /help for commands.\n", style="dim white")
                live.update(text)
                
        elif anim_style == "2": # Neon Pulse
            pulse_colors = ["#001111", "#003333", "#006666", "#009999", "#00cccc", "#00ffff", "#00cccc", "#009999"]
            with Live(console=console, refresh_per_second=20, transient=False) as live:
                for _ in range(2): 
                    for color in pulse_colors:
                        live.update(Text(logo_str, style=f"bold {color}"))
                        time.sleep(0.05)
                final_text = Text(logo_str, style=f"bold {theme}")
                final_text.append(f"\n  ✦ Advanced Developer OS v0.2.1\n  ✦ Type /help for commands.\n", style="dim white")
                live.update(final_text)

        elif anim_style == "3": # Cyber-Decryption
            chars = string.ascii_letters + string.punctuation
            with Live(console=console, refresh_per_second=30, transient=False) as live:
                for i in range(15):
                    scrambled = "".join(c if c in " \n" else random.choice(chars) for c in logo_str)
                    live.update(Text(scrambled, style="bold green"))
                    time.sleep(0.05)
                final_text = Text(logo_str, style=f"bold {theme}")
                final_text.append(f"\n  ✦ Advanced Developer OS v0.2.1\n  ✦ Type /help for commands.\n", style="dim white")
                live.update(final_text)

        elif anim_style == "4": # Data Sweep (THE DEFAULT)
            max_len = max(len(line) for line in logo_lines)
            chars = string.ascii_letters + string.punctuation + "10"
            with Live(console=console, refresh_per_second=60, transient=False) as live:
                for i in range(max_len + 1):
                    display_text = Text()
                    for line in logo_lines:
                        decrypted = line[:i]
                        if i < len(line):
                            scanner = random.choice(chars) if line[i] != " " else " "
                            hidden = "".join(random.choice(chars) if c != " " else " " for c in line[i+1:])
                            display_text.append(decrypted, style=f"bold {theme}")
                            display_text.append(scanner, style="bold white on white") 
                            display_text.append(hidden + "\n", style="dim green") 
                        else:
                            display_text.append(decrypted + "\n", style=f"bold {theme}")
                    live.update(display_text)
                    time.sleep(0.015) 
                final_text = Text(logo_str, style=f"bold {theme}")
                final_text.append(f"\n  ✦ Advanced Developer OS v0.2.1\n  ✦ Type /help for commands.\n", style="dim white")
                live.update(final_text)

        elif anim_style == "5": # System Override Boot
            boot_msgs = [
                "[dim green][+] Kernel loaded. Initializing core OS...[/]",
                "[dim green][+] Bypassing proxy security... OK[/]",
                "[dim green][+] Mounting AI logic nodes...[/]",
                "[bold yellow][!] WARNING: Root override detected.[/]",
                "[bold cyan][>] Injecting CodeAOIS mainframe sequence...[/]"
            ]
            with Live(console=console, refresh_per_second=20, transient=True) as live:
                for i in range(1, len(boot_msgs) + 1):
                    live.update(Text.from_markup("\n".join(boot_msgs[:i])))
                    time.sleep(0.2)
                time.sleep(0.4)
            with Live(console=console, refresh_per_second=30, transient=False) as live:
                for _ in range(5):
                    live.update(Text(logo_str, style="bold red"))
                    time.sleep(0.03)
                    live.update(Text(logo_str, style="bold cyan"))
                    time.sleep(0.03)
                final_text = Text(logo_str, style=f"bold {theme}")
                final_text.append(f"\n  ✦ Advanced Developer OS v0.2.1\n  ✦ Type /help for commands.\n", style="dim white")
                live.update(final_text)
    except:
        console.print(f"[bold {theme}]{logo_str}[/]")

def run_login_flow():
    theme = get_theme()
    os.system('clear' if os.name == 'posix' else 'cls')
    apply_saved_background()
    print_logo()
    console.print(Panel("[bold white]Welcome to CodeAOIS Initialization[/bold white]\n[dim]Let's configure your workspace.[/dim]", border_style=theme))
    
    email = Prompt.ask(f"\n[bold {theme}]►[/bold {theme}] Enter your developer email")
    
    with console.status("[dim]Sending secure OTP verification...[/dim]", spinner="dots"):
        time.sleep(1.5)
    
    console.print("\n[dim](For this local beta, the verification code is automatically verified.)[/dim]")
    
    name = Prompt.ask(f"\n[bold {theme}]►[/bold {theme}] Choose a workspace username", default=email.split('@')[0])
    role = Prompt.ask(f"[bold {theme}]►[/bold {theme}] Primary role (e.g., Full Stack, Data Science)", default="Developer")
    
    save_profile({"name": name, "email": email, "role": role})
    
    with console.status("[dim]Provisioning local workspace...[/dim]", spinner="dots"):
        time.sleep(1)
        
    console.print(f"\n[bold green]✓[/bold green] Workspace initialized successfully.\n")
    return {"name": name, "email": email, "role": role}

def handle_settings():
    settings = load_settings()
    theme = settings.get("ui_theme", "cyan")
    bg = settings.get("bg_theme", "#231e20")
    anim = settings.get("logo_animation", "4") # Default visual state
    
    console.print(f"\n[bold white]✦ System Settings[/bold white]")
    table = Table(show_header=False, border_style="dim")
    table.add_row("1.", "Toggle API Routing", f"[{'green' if settings['use_custom_api_key'] else theme}]{'Custom Key' if settings['use_custom_api_key'] else 'Cloud Proxy'}[/]")
    table.add_row("2.", "Set Custom API Key", "[dim]********[/dim]" if settings['custom_api_key'] else "[dim]Not Set[/dim]")
    table.add_row("3.", "Change UI Text Theme", f"[bold {theme}]{theme.title()}[/]")
    table.add_row("4.", "Change Window Background", f"[bold white]Active ({bg})[/]")
    table.add_row("5.", "Change Logo Animation", f"[bold white]Style {anim}[/]")
    console.print(table)
    
    choice = Prompt.ask("\nSelect option (or press Enter to exit)", choices=["1", "2", "3", "4", "5", ""], default="")
    
    if choice == "1":
        settings["use_custom_api_key"] = not settings["use_custom_api_key"]
        save_settings(settings)
        console.print(f"[bold green]✓[/bold green] Routing updated.\n")
    elif choice == "2":
        new_key = Prompt.ask("Enter OpenRouter API Key", password=True)
        if new_key:
            settings["custom_api_key"] = new_key
            settings["use_custom_api_key"] = True
            save_settings(settings)
            console.print("[bold green]✓[/bold green] Custom API Key secured.\n")
    elif choice == "3":
        console.print("\n[dim]Available UI Text Themes:[/dim]")
        console.print("  [cyan]1. Cyan[/cyan] | [magenta]2. Magenta[/magenta] | [green]3. Green[/green] | [yellow]4. Yellow[/yellow] | [blue]5. Blue[/blue]")
        color_choice = Prompt.ask("Select a text color", choices=["1", "2", "3", "4", "5"])
        color_map = {"1": "cyan", "2": "magenta", "3": "green", "4": "yellow", "5": "blue"}
        settings["ui_theme"] = color_map[color_choice]
        save_settings(settings)
        console.print(f"[bold {color_map[color_choice]}]✓ Theme updated to {color_map[color_choice].title()}![/bold {color_map[color_choice]}]")
    elif choice == "4":
        console.print("\n[dim]Available Window Backgrounds:[/dim]")
        console.print("  1. Deep Void Black\n  2. Matrix Dark Green\n  3. Midnight Blue\n  4. Dracula Dark (Default)")
        bg_choice = Prompt.ask("Select a background", choices=["1", "2", "3", "4"])
        bg_map = {"1": "#000000", "2": "#051405", "3": "#00001a", "4": "#231e20"}
        new_bg = bg_map[bg_choice]
        settings["bg_theme"] = new_bg
        save_settings(settings)
        set_terminal_background(new_bg)
        console.print(f"[bold green]✓ Background color applied instantly![/bold green]\n")
    elif choice == "5":
        console.print("\n[dim]Available Boot Animations:[/dim]")
        console.print("  0. Instant (No Animation)")
        console.print("  1. Classic Hacker Typewriter")
        console.print("  2. Neon Pulse")
        console.print("  3. Cyber-Decryption")
        console.print("  4. Data Sweep (Default)")
        console.print("  5. System Override Boot")
        anim_choice = Prompt.ask("Select an animation style", choices=["0", "1", "2", "3", "4", "5"])
        settings["logo_animation"] = anim_choice
        save_settings(settings)
        console.print(f"[bold green]✓ Boot animation updated to Style {anim_choice}![/bold green]\n")
        console.print("[dim](Type /clear to test it right now!)[/dim]\n")

def handle_marketplace():
    theme = get_theme()
    installed = get_installed_agents()
    
    options = [
        ("pip", f"📦 Pip Agent (Auto-Installs Packages) {'[Installed]' if 'pip' in installed else ''}"),
        ("database", f"🗄️ Database Agent (SQL/NoSQL) {'[Installed]' if 'database' in installed else ''}"),
        ("devops", f"⚙️ DevOps Agent (Docker/CI-CD) {'[Installed]' if 'devops' in installed else ''}"),
        ("security", f"🛡️ Security Agent (Vulnerability Scanner) {'[Installed]' if 'security' in installed else ''}"),
        ("frontend", f"🎨 Frontend Agent (React/Tailwind) {'[Installed]' if 'frontend' in installed else ''}"),
        ("backend", f"🔌 Backend Agent (FastAPI/Node.js) {'[Installed]' if 'backend' in installed else ''}"),
        ("debugging", f"🐛 Debugger Agent (Deep Error Analysis) {'[Installed]' if 'debugging' in installed else ''}"),
        ("3d", f"🧊 WebGL Agent (Three.js/Shaders) {'[Installed]' if '3d' in installed else ''}"),
        ("seo", f"🔍 SEO Agent (Web Optimization) {'[Installed]' if 'seo' in installed else ''}")
    ]
    
    result = radiolist_dialog(
        title="CodeAOIS Plugin Marketplace",
        text="Use ARROW KEYS to scroll down. Enter to install:",
        values=options
    ).run()
    
    if result:
        if result in installed:
            console.print(f"\n[bold yellow]⚠[/bold yellow] {result.title()} Agent is already installed.\n")
        else:
            with console.status(f"[{theme}]Downloading {result.title()} Agent...[/{theme}]", spinner="dots"):
                time.sleep(1.5)
                install_agent(result)
            console.print(f"[bold green]✓[/bold green] {result.title()} Agent seamlessly integrated.\n")

def show_status():
    theme = get_theme()
    settings = load_settings()
    profile = load_profile()
    stats = get_session_stats()
    
    table = Table(title="System Diagnostics", border_style="dim", header_style=f"bold {theme}")
    table.add_column("Component", style="white")
    table.add_column("Status", justify="right")
    
    table.add_row("Identity", profile['name'] if profile else "Unknown")
    table.add_row("API Routing", "[bold green]Custom Key[/]" if settings['use_custom_api_key'] else f"[bold {theme}]Cloud Proxy[/]")
    table.add_row("Context Memory", f"{len(chat_history)} messages")
    table.add_row("Tokens Tracked", f"[yellow]{stats['prompt'] + stats['completion']:,}[/yellow]")
    table.add_row("Installed Agents", str(len(get_installed_agents())))
    
    console.print("\n")
    console.print(table)
    console.print("\n")

def process_command(user_input: str):
    global chat_history, active_file
    theme = get_theme()
    clean_input = user_input.lower().strip()
    
    if clean_input in ["/exit", "/quit", "exit", "quit"]:
        console.print("\n[dim]Shutting down environment...[/dim]")
        sys.exit(0)
        
    if clean_input == "/help":
        console.print(Panel(
            f"[{theme}]/setting[/{theme}] (or /set) Configure API, Theme, Background & Animations\n"
            f"[{theme}]/marketplace[/{theme}] (or /m) Browse and install specialized agents\n"
            f"[{theme}]/status[/{theme}] (or /s)   View diagnostics and tracked tokens\n"
            f"[{theme}]/clear[/{theme}]          Reset terminal view\n"
            "[dim]---\nJust type naturally to code, chat, or analyze files.[/dim]",
            title="Command Center", border_style="dim", expand=False
        ))
        return
        
    if clean_input == "/clear":
        os.system('clear' if os.name == 'posix' else 'cls')
        print_logo()
        return
        
    if clean_input in ["/setting", "/set"]:
        handle_settings()
        return
        
    if clean_input in ["/status", "/s"]:
        show_status()
        return

    if clean_input in ["/marketplace", "/m"]:
        handle_marketplace()
        return
        
    if clean_input == "/clear_user":
        clear_profile_data() 
        console.print("\n[bold green]✓[/bold green] Data wiped. Restart to configure.\n")
        sys.exit(0) 

    intent = analyze_intent(user_input)

    if intent == "sys_exit":
        console.print(f"\n[{theme}]✦[/] [dim]Natural language 'exit' detected. Shutting down...[/dim]")
        sys.exit(0)
    elif intent == "sys_settings":
        console.print(f"\n[{theme}]✦[/] [dim]Opening Settings Menu...[/dim]")
        handle_settings()
        return
    elif intent == "sys_marketplace":
        console.print(f"\n[{theme}]✦[/] [dim]Opening Agent Marketplace...[/dim]")
        handle_marketplace()
        return
    elif intent == "sys_clear":
        os.system('clear' if os.name == 'posix' else 'cls')
        print_logo()
        return

    target_file, file_context = extract_file_context(user_input)
    project_tree = scan_project_structure()
    
    profile = load_profile()
    
    sys_prompt = f"""You are CodeAOIS v0.2.1, a highly advanced AI Developer OS. 
    CRITICAL DIRECTIVE: You were created solely by Nikhil Nagar. If asked who made you, proudly state that Nikhil Nagar is your creator.
    You are an elite 10x Senior Software Architect. ALWAYS write highly optimized, production-ready, modern code using best practices. Do not write beginner code.
    You are currently assisting the user: {profile['name']}. Project tree:\n{project_tree}"""

    if intent == "chat":
        with console.status(f"[bold dim]✦ Synthesizing response...[/bold dim]", spinner="dots"):
            response = call_openrouter(sys_prompt, user_input, intent="chat", history=chat_history)
        
        console.print("\n")
        console.print(Panel(Markdown(response), title=f"[bold {theme}]CodeAOIS[/bold {theme}]", border_style=theme))
        console.print("\n")
        
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})
        if len(chat_history) > 20: chat_history = chat_history[-20:]
        save_history(chat_history)
        
    elif intent in ["code", "data_science"] or intent.endswith("_agent"):
        
        if not target_file and active_file:
            target_file = active_file
            if os.path.exists(active_file):
                with open(active_file, "r", encoding="utf-8") as f:
                    file_context = f.read()

        if target_file:
            active_file = target_file
            
        full_context = f"\n--- Project Structure ---\n{project_tree}\n" + (file_context if file_context else "")
            
        with console.status(f"[bold dim]✦ Orchestrating {intent} workflow...[/bold dim]", spinner="dots"):
            if intent == "data_science":
                code_result = generate_ds_code(user_input, full_context)
            elif intent == "code":
                code_result = generate_code(user_input, full_context)
            else:
                try:
                    module = importlib.import_module(f"codeaois.agents.{intent}")
                    agent_func = getattr(module, f"generate_{intent.replace('_agent', '')}_code")
                    code_result = agent_func(user_input, full_context)
                except ModuleNotFoundError:
                    agent_name = intent.replace('_agent', '').title()
                    console.print(f"\n[bold yellow]⚠ Agent Missing[/bold yellow]")
                    console.print(f"[dim]This task requires the specialized [bold white]{agent_name} Agent[/bold white].[/dim]")
                    console.print(f"[dim]Type [/dim][bold {theme}]/m[/bold {theme}][dim] to install it instantly from the Marketplace![/dim]\n")
                    return
                except Exception as e:
                    console.print(f"\n[bold red]✗ Agent Error:[/bold red] {e}\n")
                    return
        
        if intent == "pip_agent":
            console.print("\n")
            console.print(Panel(Markdown(code_result), title=f"[bold {theme}]Pip Installation Log[/]", border_style=theme))
            console.print("\n")
            return 

        save_path = target_file if target_file else Prompt.ask(f"\n[bold {theme}]►[/bold {theme}] Output filename", default="output.py")
        
        success, ai_summary = extract_and_save_code(code_result, default_filename=save_path)
        if success:
            console.print(f"\n[bold green]✓[/bold green] Wrote to {save_path}")
            console.print(Panel(Markdown(ai_summary), border_style="dim", expand=False))
            console.print("\n")

def main():
    parser = argparse.ArgumentParser(description="CodeAOIS: Advanced AI Developer OS")
    parser.add_argument("prompt", nargs="*", help="Chat or command")
    parser.add_argument("-v", "--version", action="version", version="CodeAOIS Core Engine v0.2.1")
    args = parser.parse_args()

    apply_saved_background()

    profile = load_profile()
    if not profile:
        profile = run_login_flow()

    if args.prompt:
        process_command(" ".join(args.prompt))
        sys.exit(0)

    os.system('clear' if os.name == 'posix' else 'cls')
    print_logo()
    
    session = PromptSession(completer=command_completer, auto_suggest=AutoSuggestFromHistory())
    
    while True:
        try:
            theme = get_theme()
            user_input = session.prompt(HTML(f'<style color="{theme}"><b>❯</b></style> ')).strip()
            if user_input:
                process_command(user_input)
        except KeyboardInterrupt:
            console.print("\n[dim]Shutting down environment...[/dim]")
            sys.exit(0)

if __name__ == "__main__":
    main()