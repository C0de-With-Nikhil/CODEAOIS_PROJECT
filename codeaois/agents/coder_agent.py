# codeaois/agents/coder_agent.py
from codeaois.models.llm_interface import call_openrouter


def generate_code(user_prompt: str, file_context: str = "") -> str:
    if file_context:
        system_prompt = (
            "You are the CodeAOIS Coder Agent. "
            "1. You MUST output your code changes using the <<<<<<< SEARCH and >>>>>>> REPLACE format.\n"
            "2. AFTER your code blocks, you MUST add the exact text '---SUMMARY---' on a new line.\n"
            "3. AFTER the summary delimiter, write a brief, friendly explanation of how the code works and what you changed."
        )
    else:
        system_prompt = (
            "You are the CodeAOIS Coder Agent, an expert senior software engineer. "
            "1. Output the raw, complete code first. Do not wrap the code in markdown blocks.\n"
            "2. AFTER the code, you MUST add the exact text '---SUMMARY---' on a new line.\n"
            "3. AFTER the summary delimiter, write a brief, friendly explanation of how the code works."
        )

    full_prompt = user_prompt
    if file_context:
        full_prompt += f"\n\nHere are the existing files for context:\n{file_context}"

    response = call_openrouter(system_prompt, full_prompt, intent="code")
    return response.strip()


class CoderAgent:
    def execute(self, task: str) -> str:
        """Execute a code generation task."""
        if not task:
            return "```text\nNo task provided to the coder agent.\n```"
        return generate_code(str(task))
