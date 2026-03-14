# codeaois/agents/tester_agent.py
import subprocess
import sys


def run_test(file_path: str) -> tuple[bool, str]:
    """Runs a Python script and catches any terminal errors."""
    if not file_path or not file_path.endswith('.py'):
        return True, "Not a Python file. Skipping auto-test."

    try:
        # sys.executable ensures it uses your isolated 'venv' Python, not the global one
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=10,  # 10-second kill switch so infinite loops don't crash your computer
        )

        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()

    except subprocess.TimeoutExpired:
        return False, "Error: Script execution timed out (possible infinite loop)."
    except Exception as e:
        return False, str(e)


class TesterAgent:
    def execute(self, task: str) -> str:
        """Execute a test task on a Python file."""
        if not task:
            return "```text\nNo test task provided to the tester agent.\n```"

        success, output = run_test(str(task))
        status = "Success" if success else "Failed"
        return f"```text\n{output}\nStatus: {status}\n```"
