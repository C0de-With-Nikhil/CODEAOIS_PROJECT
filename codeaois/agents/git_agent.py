# codeaois/agents/git_agent.py
import subprocess
import os

C_YELLOW = '\033[93m'
C_GREEN = '\033[92m'
C_RESET = '\033[0m'

def run_git_command(command: list) -> tuple[bool, str]:
    """Quietly executes a terminal command and returns the result."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def auto_commit(file_path: str, message: str):
    """Automatically stages and commits a modified file."""
    
    # 1. Check if the user is inside a Git repository
    is_git, _ = run_git_command(["git", "rev-parse", "--is-inside-work-tree"])
    if not is_git:
        print(f"   {C_YELLOW}⚠️ [Git Agent] No .git repository found in this folder. Skipping auto-commit.{C_RESET}")
        return

    print(f"   {C_GREEN}🌿 [Git Agent] Engaging version control...{C_RESET}")

    # 2. Stage only the specific file the AI just modified
    success, err = run_git_command(["git", "add", file_path])
    if not success:
        print(f"   {C_YELLOW}⚠️ [Git Agent] Failed to stage file: {err}{C_RESET}")
        return

    # 3. Double-check that there are actually changes to save
    has_changes, diff = run_git_command(["git", "status", "--porcelain"])
    if not has_changes or not diff:
        print(f"   {C_YELLOW}⚠️ [Git Agent] No actual code changes detected for {file_path}.{C_RESET}")
        return

    # 4. Commit the changes to the timeline
    commit_success, commit_err = run_git_command(["git", "commit", "-m", message])
    if commit_success:
        print(f"   {C_GREEN}✅ [Git Agent] Successfully committed changes to {file_path}!{C_RESET}")
    else:
        print(f"   {C_YELLOW}⚠️ [Git Agent] Commit failed: {commit_err}{C_RESET}")