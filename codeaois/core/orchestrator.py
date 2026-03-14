import subprocess
import time
import os
import sys
from rich.console import Console
from rich.panel import Panel

console = Console(soft_wrap=True)

def execute_with_autofix(file_path, agent_func, original_context, max_retries=3):
    """
    Runs a Python file. If it crashes, it feeds the Traceback to the LLM 
    to automatically fix the code and tries again.
    """
    if not os.path.exists(file_path):
        console.print(f"[bold red]✗ File not found: {file_path}[/bold red]")
        return False

    attempt = 1
    
    while attempt <= max_retries:
        console.print(f"\n[bold cyan]🔄 Autonomous Execution [Attempt {attempt}/{max_retries}][/bold cyan]")
        console.print(f"[dim]Running: python {file_path}[/dim]")
        
        # 1. Run the code and capture the terminal output
        result = subprocess.run(
            [sys.executable or "python", file_path], 
            capture_output=True, 
            text=True
        )
        
        # 2. Check for success
        if result.returncode == 0:
            console.print("[bold green]✅ Execution Successful![/bold green]")
            if result.stdout.strip():
                console.print(Panel(result.stdout.strip(), title="Terminal Output", border_style="green"))
            return True
            
        # 3. Catch the error
        error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
        console.print("[bold red]❌ Execution Crashed.[/bold red]")
        console.print(Panel(error_msg, title="Traceback Captured", border_style="red"))
        
        if attempt == max_retries:
            console.print("[bold yellow]⚠️ Maximum self-correction retries reached. Manual fix required.[/bold yellow]")
            return False
            
        # Force the AI to be strictly about code to avoid markdown issues
        fix_prompt = (
            f"I ran the code in `{file_path}` and it crashed with this error:\n"
            f"```\n{error_msg}\n```\n"
            f"Please fix the code to resolve this error. Return ONLY the COMPLETE, fixed Python code inside a markdown block. Do not add explanations."
        )
        
        from codeaois.utils.file_writer import extract_and_save_code
        try:
            # Added a spinner here so you can see if the Proxy is lagging!
            with console.status("[dim]🧠 Analyzing error and waiting for proxy response...[/dim]", spinner="dots"):
                fixed_code_result = agent_func(fix_prompt, original_context)
            
            success, _ = extract_and_save_code(fixed_code_result, default_filename=file_path)
            
            if success:
                console.print(f"[bold green]✓ Patch applied to {file_path}[/bold green]")
            else:
                # BUG FIX: Force save the raw output if markdown extraction fails again!
                with open(file_path, "w", encoding="utf-8") as f:
                    # Clean up common AI conversational junk if it forgot markdown
                    clean_code = fixed_code_result.replace("Here is the fixed code:", "").strip()
                    f.write(clean_code)
                console.print(f"[bold yellow]⚠ AI formatting poor, but forced patch to {file_path}[/bold yellow]")
                
        except Exception as e:
            # If the proxy actually times out, this exception will catch it
            console.print(f"[bold red]✗ Auto-fix engine error (Proxy Timeout?): {e}[/bold red]")
            return False
            
        attempt += 1
        time.sleep(1.5) # Small pause to let the hard drive write the file
        
    return False