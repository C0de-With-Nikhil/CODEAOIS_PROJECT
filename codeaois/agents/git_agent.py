import subprocess
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from codeaois.models.llm_interface import call_openrouter
from codeaois.core.memory import load_settings

console = Console()

def get_theme():
    return load_settings().get("ui_theme", "cyan")

def generate_git_code(user_input: str, context: str = "") -> str:
    """Analyze git diffs, generate a commit message using the LLM, and execute git add, commit, push."""
    theme = get_theme()
    console.print("\n[dim]✦ Analyzing git repository...[/dim]")

    try:
        # 1. Check if we're in a git repository
        is_repo = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
        )
        if is_repo.returncode != 0:
            return "```text\nNot a git repository. Please run 'git init' first.\n```"

        # 2. Stage all changes FIRST so we can read the exact diff of everything
        subprocess.run(["git", "add", "."], capture_output=True)
        
        diff = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
        )

        if not diff.stdout.strip():
            return "```text\nNo changes detected. Working tree is clean.\n```"

        # 3. Generate a commit message via the LLM
        system_prompt = (
            "You are a helper that writes short, clear git commit messages based on the provided git diff. "
            "Respond with ONLY the commit message, no quotes, no markdown formatting."
        )
        # Truncate diff to 3000 chars to save tokens!
        full_prompt = f"{user_input}\n\nGit diff:\n{diff.stdout[:3000]}"
        commit_msg = call_openrouter(system_prompt, full_prompt, intent="code").strip()
        commit_msg = commit_msg.replace('"', "'").replace("```text", "").replace("```", "").strip()

        if not commit_msg:
            return "```text\nCould not generate a commit message.\n```"

        console.print(f"\n[bold yellow]⚠ AI Proposed Commit Message:[/bold yellow]")
        console.print(Panel(commit_msg, border_style=theme))

        # 4. Ask the user before committing & pushing
        choice = Prompt.ask(f"[{theme}]Execute `git commit` and `git push`?[/{theme}] [Y/n]", default="y")
        if choice.lower() != "y":
            # Undo the 'git add' if they cancel, to keep their workspace clean!
            subprocess.run(["git", "reset"], capture_output=True)
            return "```text\nGit operation aborted by user.\n```"

        # 5. Commit and Push safely
        console.print("\n[dim]Executing git commands...[/dim]")
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            capture_output=True,
            text=True,
        )
        
        push_res = subprocess.run(
            ["git", "push"],
            capture_output=True,
            text=True,
        )
        
        output = push_res.stdout if push_res.returncode == 0 else push_res.stderr
        status = "Success" if push_res.returncode == 0 else "Failed"

        return f"```text\n{output.strip()}\nStatus: {status}\n```"

    except Exception as e:
        return f"```text\nError: {str(e)}\n```"
