# codeaois/agents/git_agent.py
import subprocess
import os

def auto_commit(filepath: str, message: str = "Auto-commit by CodeAOIS Coder Agent"):
    """
    Goal #8: Autonomous Version Control.
    Automatically stages and commits files modified by the AI.
    """
    # Check if we are inside a Git repository
    if not os.path.exists(".git"):
        print("   -> ⚠️  [Git Agent]: No .git repository found in this folder. Skipping auto-commit.")
        return

    try:
        print(f"   -> 🌿 [Git Agent]: Staging {filepath}...")
        subprocess.run(["git", "add", filepath], check=True, capture_output=True)
        
        print("   -> 🌿 [Git Agent]: Creating commit...")
        subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True)
        
        print("   -> ✅ [Git Agent]: Version control secured.")
        
    except subprocess.CalledProcessError as e:
        print(f"   -> ❌ [Git Agent Error]: Failed to commit. Is your git configured? {e}")