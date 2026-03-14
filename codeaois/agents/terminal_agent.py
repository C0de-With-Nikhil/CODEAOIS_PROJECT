import subprocess
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from codeaois.models.llm_interface import call_openrouter
from codeaois.core.memory import load_settings

console = Console()

def get_theme():
    return load_settings().get("ui_theme", "cyan")

def generate_terminal_code(user_input: str, context: str) -> str:
    """Extracts bash commands from the LLM and executes them safely."""
    theme = get_theme()
    
    sys_prompt = "You are a terminal command extractor. Convert the user's request into a single bash/terminal command or a short chain of commands (like `mkdir foo && cd foo`). Return ONLY the raw terminal command, no markdown, no explanations."
    
    console.print("\n[dim]✦ Translating request to terminal commands...[/dim]")
    
    try:
        command = call_openrouter(sys_prompt, user_input, intent="code").strip()
        
        # Clean up any markdown the AI accidentally sends
        command = command.replace("```bash", "").replace("```sh", "").replace("```", "").replace("\n", " ").strip()
        
        if not command:
            return "```text\nCould not determine a valid terminal command.\n```"
            
        # --- HUMAN IN THE LOOP SAFETY CHECK ---
        console.print(f"\n[bold yellow]⚠ SECURITY CHECKPOINT[/bold yellow]")
        console.print(f"The AI requested to execute: [bold white]{command}[/bold white]")
        choice = Prompt.ask(f"[{theme}]Allow execution?[/{theme}] [Y/n]", default="y")
        
        if choice.lower() != 'y':
            return "```text\nExecution aborted by user. Stay safe!\n```"
            
        console.print(f"\n[dim]Executing: {command}[/dim]")
        
        # Actually run the command on the OS!
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        output = result.stdout if result.returncode == 0 else result.stderr
        log_color = "green" if result.returncode == 0 else "red"
        
        if output.strip():
            console.print(Panel(output.strip(), title="Terminal Output", border_style=log_color))
        else:
            console.print(f"[{log_color}]✓ Command executed successfully with no output.[/{log_color}]")
        
        status = 'Success' if result.returncode == 0 else 'Failed'
        return f"```text\n{output.strip()}\nStatus: {status}\n```"
    except Exception as e:
        return f"```text\nError executing command: {str(e)}\n```"