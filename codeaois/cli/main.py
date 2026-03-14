import argparse
import sys
import os
import importlib
import time
import random
import string
import re
import smtplib
from email.mime.text import MIMEText
import base64

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
from rich.progress import Progress, SpinnerColumn, TextColumn

# --- CODEAOIS MODULES ---
from codeaois.core._auth import send_real_otp
from codeaois.core.planner import analyze_intent, get_installed_agents
from codeaois.core.context import extract_file_context, get_semantic_context
from codeaois.brain.scanner import scan_project_structure
from codeaois.brain.embeddings import CodebaseMemory
from codeaois.models.llm_interface import call_openrouter
from codeaois.agents.coder_agent import generate_code
from codeaois.agents.data_science_agent import generate_ds_code
from codeaois.utils.file_writer import extract_and_save_code
from codeaois.core.marketplace import install_agent
from codeaois.core.memory import (
    load_profile, save_profile, load_history, save_history, 
    clear_history_data, clear_profile_data, load_settings, save_settings, 
    get_session_stats, pull_from_cloud
)

console = Console(soft_wrap=True)
chat_history = load_history()
active_file = None

AVAILABLE_COMMANDS = [
    '/help', '/clear', '/status', '/s', '/marketplace', '/m', '/setting', '/set', '/exit', '/clear_user', '/index'
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

# --- THE REAL SMTP OTP ENGINE ---
def send_real_otp(receiver_email, otp_code):
    """Sends a REAL email using Decoded Base64 credentials from _auth.py."""
    # Import your secure decoding function
    from codeaois.core._auth import get_secure_credentials
    
    sender_email, sender_password = get_secure_credentials()

    # If decoding fails or strings are empty, return False to trigger Dev Sandbox
    if not sender_email or not sender_password:
        return False

    msg = MIMEText(
        f"Hello!\n\n"
        f"Your CodeAOIS secure login verification code is: {otp_code}\n\n"
        f"This code links your current session to your global cloud history.\n\n"
        f"Welcome to the OS.\n- The CodeAOIS Team"
    )
    msg['Subject'] = 'CodeAOIS Secure Login Verification'
    msg['From'] = f"CodeAOIS Security <{sender_email}>"
    msg['To'] = receiver_email

    try:
        # Connect to Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [receiver_email], msg.as_string())
        return True
    except Exception:
        # If there's a login error (wrong App Pass), fallback to sandbox
        return False

# --- THE MULTI-ANIMATION LOGO ENGINE ---
def print_logo():
    settings = load_settings()
    theme = settings.get("ui_theme", "cyan")
    anim_style = str(settings.get("logo_animation", "4")) 
    
    logo_lines = [
        "   ____          _        _    ___ _____  _____ ",
        "  / ___|___   __| | ___  / \\  / _ \\_   _|/ ____|",
        " | |   / _ \\ / _` |/ _ \\/ _ \\| | | || | | (___  ",
        " | |__| (_) | (_| |  __/ ___ \\ |_| || |_ \\___ \\ ",
        "  \\____\\___/ \\__,_|\\___/_/   \\_\\___/_____|____/ "
    ]
    logo_str = "\n".join(logo_lines)

    if anim_style == "0":
        console.print(f"[bold {theme}]{logo_str}[/]")
        console.print(f"  [dim]✦[/dim] [bold white]Advanced Developer OS[/bold white] [dim]v0.2.6[/dim]")
        console.print(f"  [dim]✦[/dim] [dim]Type /help for commands.[/dim]\n")
        return

    try:
        if anim_style == "1":
            text = Text(style=f"bold {theme}")
            with Live(console=console, refresh_per_second=60, transient=False) as live:
                for char in logo_str:
                    text.append(char)
                    live.update(text)
                    time.sleep(0.002)
                text.append(f"\n  ✦ Advanced Developer OS v0.3.0\n  ✦ Type /help for commands.\n", style="dim white")
                live.update(text)
                
        elif anim_style == "2":
            pulse_colors = ["#001111", "#003333", "#006666", "#009999", "#00cccc", "#00ffff", "#00cccc", "#009999"]
            with Live(console=console, refresh_per_second=20, transient=False) as live:
                for _ in range(2): 
                    for color in pulse_colors:
                        live.update(Text(logo_str, style=f"bold {color}"))
                        time.sleep(0.05)
                final_text = Text(logo_str, style=f"bold {theme}")
                final_text.append(f"\n  ✦ Advanced Developer OS v0.2.6\n  ✦ Type /help for commands.\n", style="dim white")
                live.update(final_text)

        elif anim_style == "3":
            chars = string.ascii_letters + string.punctuation
            with Live(console=console, refresh_per_second=30, transient=False) as live:
                for i in range(15):
                    scrambled = "".join(c if c in " \n" else random.choice(chars) for c in logo_str)
                    live.update(Text(scrambled, style="bold green"))
                    time.sleep(0.05)
                final_text = Text(logo_str, style=f"bold {theme}")
                final_text.append(f"\n  ✦ Advanced Developer OS v0.2.6\n  ✦ Type /help for commands.\n", style="dim white")
                live.update(final_text)

        elif anim_style == "4":
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
                final_text.append(f"\n  ✦ Advanced Developer OS v0.2.6\n  ✦ Type /help for commands.\n", style="dim white")
                live.update(final_text)

        elif anim_style == "5":
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
                final_text.append(f"\n  ✦ Advanced Developer OS v0.2.6\n  ✦ Type /help for commands.\n", style="dim white")
                live.update(final_text)
    except:
        console.print(f"[bold {theme}]{logo_str}[/]")
        console.print(f"  [dim]✦[/dim] [bold white]Advanced Developer OS[/bold white] [dim]v0.2.6[/dim]")

def run_login_flow():
    theme = get_theme()
    os.system('clear' if os.name == 'posix' else 'cls')
    apply_saved_background()
    print_logo()
    console.print(Panel("[bold white]Global Workspace Sync[/bold white]\n[dim]Secure login via private SMTP. Syncing history to Supabase Cloud.[/dim]", border_style=theme))
    
    email = Prompt.ask(f"\n[bold {theme}]►[/bold {theme}] Enter your developer email").strip()
    real_otp = str(random.randint(100000, 999999))
    
    with console.status("[dim]Sending secure verification code...[/dim]", spinner="dots"):
        from codeaois.core._auth import send_real_otp
        email_sent = send_real_otp(email, real_otp)
        time.sleep(1.5)
        
    if email_sent:
        console.print(f"[bold green]✓ Verification Code sent to {email}![/bold green]")
    else:
        console.print(f"\n[dim yellow]⚠ Private Mail Server Offline. Showing code in DEV SANDBOX:[/dim yellow]")
        console.print(f"[bold magenta]Your secure 6-digit OTP is: [bold white]{real_otp}[/][/]\n")
    
    verified = False
    attempts = 3
    while attempts > 0:
        user_otp = Prompt.ask(f"[bold {theme}]►[/bold {theme}] Enter 6-digit OTP")
        
        if user_otp.strip() == real_otp:
            console.print("[bold green]✓ Verified! Connecting to Supabase Cloud...[/bold green]")
            
            # --- THE MAGIC ATTACHMENT ---
            from codeaois.core.memory import pull_from_cloud, save_history, restore_cloud_tokens
            
            with console.status("[dim]Pulling Cloud Assets...[/dim]", spinner="dots"):
                cloud_profile = pull_from_cloud(email, 'profile')
                cloud_history = pull_from_cloud(email, 'history')
                tokens_restored = restore_cloud_tokens(email)
                
            if cloud_profile:
                save_profile(cloud_profile)
                name = cloud_profile.get('name', 'Developer')
                console.print(f"[bold green]✓ Welcome back, {name}![/bold green]")
            else:
                console.print("\n[dim]✦ New Identity Detected. Setting up local profile...[/dim]")
                name = Prompt.ask(f"[bold {theme}]►[/bold {theme}] Choose username", default=email.split('@')[0])
                role = Prompt.ask(f"[bold {theme}]►[/bold {theme}] Primary role", default="Developer")
                save_profile({"name": name, "email": email, "role": role})

            if cloud_history:
                save_history(cloud_history) 
                console.print(f"[dim]✦ Restored {len(cloud_history)} messages from cloud memory.[/dim]")
                
            if tokens_restored:
                console.print(f"[dim]✦ Restored lifetime tokens from cloud.[/dim]")
            
            verified = True
            break
            
        attempts -= 1
        if attempts > 0:
            console.print(f"[bold red]✗ Invalid OTP. {attempts} attempts remaining.[/bold red]")
    
    if not verified:
        console.print("[bold red]Access Denied. Exiting.[/bold red]")
        sys.exit(1)

    console.print(f"\n[bold green]✓[/bold green] Workspace initialized successfully.\n")
    return load_profile()

def handle_settings():
    settings = load_settings()
    theme = settings.get("ui_theme", "cyan")
    bg = settings.get("bg_theme", "#231e20")
    anim = settings.get("logo_animation", "4")
    
    console.print(f"\n[bold white]✦ System Settings[/bold white]")
    table = Table(show_header=False, border_style="dim")
    table.add_row("1.", "Active AI Engine", f"[{'green' if settings.get('use_custom_api_key') else theme}]{'Custom Pro Key' if settings.get('use_custom_api_key') else 'CodeAOIS API'}[/]")
    table.add_row("2.", "Set Custom API Key", "[dim]********[/dim]" if settings.get('custom_api_key') else "[dim]Not Set[/dim]")
    table.add_row("3.", "Switch to CodeAOIS API", "")
    table.add_row("4.", "Change UI Text Theme", f"[bold {theme}]{theme.title()}[/]")
    table.add_row("5.", "Change Window Background", f"[bold white]Active ({bg})[/]")
    table.add_row("6.", "Change Logo Animation", f"[bold white]Style {anim}[/]")
    console.print(table)
    
    choice = Prompt.ask("\nSelect option (or press Enter to exit)", choices=["1", "2", "3", "4", "5", "6", ""], default="")
    
    if choice == "1":
        settings["use_custom_api_key"] = not settings.get("use_custom_api_key")
        save_settings(settings)
        console.print(f"[bold green]✓[/bold green] Engine switched.\n")
    elif choice == "2":
        new_key = Prompt.ask("Enter OpenRouter API Key (Press Enter to cancel)", password=True).strip()
        if new_key:
            settings["custom_api_key"] = new_key
            settings["use_custom_api_key"] = True
            save_settings(settings)
            console.print("[bold green]✓ Engine upgraded to Pro Mode with Custom Key.[/bold green]\n")
        else:
            console.print("[bold yellow]⚠ Action canceled. API Key cannot be empty.[/bold yellow]\n")
    elif choice == "3":
        settings["use_custom_api_key"] = False
        save_settings(settings)
        console.print(f"[bold green]✓[/bold green] Downgraded to CodeAOIS API.\n")
    elif choice == "4":
        console.print("\n[dim]Available UI Text Themes:[/dim]")
        console.print("  [cyan]1. Cyan[/cyan] | [magenta]2. Magenta[/magenta] | [green]3. Green[/green] | [yellow]4. Yellow[/yellow] | [blue]5. Blue[/blue]")
        color_choice = Prompt.ask("Select a text color", choices=["1", "2", "3", "4", "5"])
        color_map = {"1": "cyan", "2": "magenta", "3": "green", "4": "yellow", "5": "blue"}
        settings["ui_theme"] = color_map[color_choice]
        save_settings(settings)
        console.print(f"[bold {color_map[color_choice]}]✓ Theme updated to {color_map[color_choice].title()}![/bold {color_map[color_choice]}]")
    elif choice == "5":
        console.print("\n[dim]Available Window Backgrounds:[/dim]")
        console.print("  1. Deep Void Black\n  2. Matrix Dark Green\n  3. Midnight Blue\n  4. Dracula Dark (Default)")
        bg_choice = Prompt.ask("Select a background", choices=["1", "2", "3", "4"])
        bg_map = {"1": "#000000", "2": "#051405", "3": "#00001a", "4": "#231e20"}
        new_bg = bg_map[bg_choice]
        settings["bg_theme"] = new_bg
        save_settings(settings)
        set_terminal_background(new_bg)
        console.print(f"[bold green]✓ Background color applied instantly![/bold green]\n")
    elif choice == "6":
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

# --- NEW INDEXING ENGINE ---
def index_workspace():
    """CLI command to scan and embed the local codebase."""
    console.print(Panel.fit("[bold cyan]🧠 Initializing CodeAOIS Brain...[/bold cyan]", border_style="cyan"))
    
    memory = CodebaseMemory(project_path=".")
    
    with Progress(
        SpinnerColumn("dots", style="bold green"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="[cyan]Scanning directories, chunking files, and calculating embeddings...[/cyan]", total=None)
        chunks_indexed = memory.index_project()
        
    if chunks_indexed > 0:
        console.print(f"[bold green]✅ Workspace Indexing Complete![/bold green]")
        console.print(f"📦 Embedded [bold yellow]{chunks_indexed}[/bold yellow] semantic code chunks into '.codeaois_db'.")
        console.print("💡 Your agents can now instantly read and search your entire project context.\n")
    else:
        console.print("[bold yellow]⚠️ No code files found to index or project is empty.[/bold yellow]\n")

def show_status():
    theme = get_theme()
    settings = load_settings()
    profile = load_profile()
    stats = get_session_stats()
    
    table = Table(title="System Diagnostics", border_style="dim", header_style=f"bold {theme}")
    table.add_column("Component", style="white")
    table.add_column("Status", justify="right")
    
    table.add_row("Identity", profile['name'] if profile else "Unknown")
    table.add_row("API Routing", "[bold green]Custom Pro Key[/]" if settings.get('use_custom_api_key') else f"[bold {theme}]CodeAOIS API[/]")
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
            f"[{theme}]/index[/{theme}]          Scan and embed your codebase into local memory\n"
            f"[{theme}]/clear[/{theme}]          Reset terminal view\n"
            "[dim]---\nUse @filename to make the AI read specific files (e.g. 'Explain @main.py')[/dim]",
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

    if clean_input == "/index":
        index_workspace()
        return

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

    deep_context = ""
    mentioned_files = re.findall(r'@([\w\.\-\/]+)', user_input)
    
    if mentioned_files:
        console.print(f"\n[dim]✦ Context Engine scanning: {', '.join(mentioned_files)}...[/dim]")
        for file_path in mentioned_files:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    deep_context += f"\n--- EXPLICIT FILE CONTEXT: {file_path} ---\n{f.read()}\n"
            else:
                console.print(f"[bold yellow]⚠ Warning: Could not find file '{file_path}'[/bold yellow]")

    target_file, file_context = extract_file_context(user_input)
    project_tree = scan_project_structure()
    semantic_context = get_semantic_context(user_input)
    
    # --- BUG FIX 1: Provide User's Name to AI ---
    profile = load_profile()
    user_name = profile.get("name", "Developer") if profile else "Developer"
    
    sys_prompt = f"""You are CodeAOIS v0.3.0, an elite AI Developer OS created by Nikhil Nagar. You are assisting {user_name}.
    You have access to the user's local codebase.
    
    PROJECT STRUCTURE:
    {project_tree}
    
    SEMANTICALLY RELEVANT CODE:
    {semantic_context}
    
    {deep_context}
    
    DIRECTIVE: Use the provided code snippets to give highly accurate, project-specific answers."""

    if intent == "chat":
        with console.status(f"[bold dim]✦ Synthesizing response...[/bold dim]", spinner="dots"):
            response = call_openrouter(sys_prompt, user_input, intent="chat", history=chat_history)
        
        console.print("\n")
        console.print(Panel(Markdown(response), title=f"[bold {theme}]CodeAOIS[/bold {theme}]", border_style=theme))
        console.print("\n")
        
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})
        if len(chat_history) > 100: chat_history = chat_history[-100:]
        save_history(chat_history)
        
    elif intent in ["code", "data_science"] or intent.endswith("_agent"):
        if not target_file and active_file:
            target_file = active_file
            if os.path.exists(active_file):
                with open(active_file, "r", encoding="utf-8") as f:
                    file_context = f.read()

        if target_file:
            active_file = target_file
            
        full_context = f"\n--- Project Structure ---\n{project_tree}\n" + (file_context if file_context else "") + deep_context
            
        if intent in ["pip_agent", "terminal_agent", "git_agent"]:
            try:
                module = importlib.import_module(f"codeaois.agents.{intent}")
                agent_func = getattr(module, f"generate_{intent.replace('_agent', '')}_code")
                code_result = agent_func(user_input, full_context)
            except Exception as e:
                console.print(f"\n[bold red]✗ Agent Error:[/bold red] {e}\n")
                return
        else:
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
                    if intent in ["pip_agent", "terminal_agent", "git_agent"]:
                        console.print("\n")
                        if intent == "terminal_agent": panel_title = "Terminal Execution Log"
                        elif intent == "git_agent": panel_title = "Git Execution Log"
                        else: panel_title = "Pip Installation Log"
        
                        console.print(Panel(Markdown(code_result), title=f"[bold {theme}]{panel_title}[/]", border_style=theme))
                        console.print("\n")
                        return

        save_path = target_file if target_file else Prompt.ask(f"\n[bold {theme}]►[/bold {theme}] Output filename", default="output.py")
        
        save_path = target_file if target_file else Prompt.ask(f"\n[bold {theme}]►[/bold {theme}] Output filename", default="output.py")
        
        success, ai_summary = extract_and_save_code(code_result, default_filename=save_path)
        
        if success:
            console.print(f"\n[bold green]✓[/bold green] Wrote to {save_path}")
            console.print(Panel(Markdown(ai_summary), border_style="dim", expand=False))
        else:
            # BUG FIX: If the AI forgot to use Markdown code blocks, force save the raw text anyway!
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(code_result)
            console.print(f"\n[bold yellow]⚠ AI formatting error, but forced write to {save_path}[/bold yellow]")
            console.print(Panel(Markdown(code_result), border_style="yellow", expand=False))
            
        # --- AUTONOMOUS RUNNER INTEGRATION ---
        if save_path.endswith('.py'):
            run_choice = Prompt.ask(f"\n[bold cyan]►[/bold cyan] Execute [bold white]{save_path}[/bold white] with Auto-Fix Engine?", choices=["y", "n"], default="y")
            if run_choice.lower() == 'y':
                from codeaois.core.orchestrator import execute_with_autofix
                
                # Figure out which agent should fix the code
                if intent == "data_science": fix_agent = generate_ds_code
                elif intent == "code": fix_agent = generate_code
                else: fix_agent = generate_code
                
                # Start the autonomous loop!
                execute_with_autofix(save_path, fix_agent, full_context)
                
        console.print("\n")
def main():
    global chat_history # --- BUG FIX 2: Explicitly declare the global variable so it can be reloaded ---
    
    parser = argparse.ArgumentParser(description="CodeAOIS: Advanced AI Developer OS")
    parser.add_argument("prompt", nargs="*", help="Chat or command")
    parser.add_argument("-v", "--version", action="version", version="CodeAOIS Core Engine v0.2.6")
    args = parser.parse_args()

    apply_saved_background()

    profile = load_profile()
    if not profile:
        profile = run_login_flow()
        
    # --- CRITICAL BUG FIX 2 UPDATE ---
    # Refresh the in-memory chat_history from the file right here
    chat_history = load_history()

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