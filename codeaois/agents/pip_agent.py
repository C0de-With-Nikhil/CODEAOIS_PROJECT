import subprocess
import sys
import re
from rich.console import Console
from codeaois.models.llm_interface import call_openrouter

console = Console()

def generate_pip_code(user_input: str, context: str) -> str:
    """
    The Auto-Pip Agent. It uses the LLM to extract package names, physically installs them on the OS,
    and returns an installation log.
    """
    # 1. Ask the AI to extract JUST the package names from the user's sentence
    sys_prompt = "You are a package extractor tool. The user wants to install Python packages. Reply ONLY with the exact pip package names separated by spaces. Nothing else. No markdown. Example: requests pandas numpy"
    
    console.print("\n[dim]✦ Analyzing required dependencies...[/dim]")
    packages_str = call_openrouter(sys_prompt, user_input, intent="code")
    
    # Split the response into a list of words
    packages = packages_str.strip().split()
    
    if not packages or "error" in packages_str.lower():
        return "```text\nCould not detect any valid packages to install.\n```"
        
    console.print(f"[bold cyan]📦 Auto-Pip Agent initialized![/bold cyan]")
    
    success_logs = []
    
    # 2. Physically run the installation commands on the user's computer!
    for pkg in packages:
        # Clean the package name to prevent security injection attacks
        pkg = re.sub(r'[^a-zA-Z0-9_\-\.]', '', pkg)
        if not pkg: 
            continue
            
        console.print(f"[dim]Executing: pip install {pkg}...[/dim]")
        
        try:
            # Runs `python -m pip install <package>` directly in the background!
            result = subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True, text=True)
            
            if result.returncode == 0:
                success_logs.append(f"✅ Successfully installed: {pkg}")
                console.print(f"[bold green]✓ {pkg} installed successfully![/bold green]")
            else:
                success_logs.append(f"❌ Failed to install {pkg}\nError: {result.stderr.strip()}")
                console.print(f"[bold red]✗ Failed to install {pkg}[/bold red]")
                
        except Exception as e:
            success_logs.append(f"❌ System Error running pip: {e}")
            
    final_log = "\n".join(success_logs)
    
    # 3. Return a text block so main.py saves the installation logs
    return f"```text\n--- CodeAOIS Pip Installation Log ---\n{final_log}\n```\nI have finished executing the pip installation on your local system! Check the logs saved to the file."