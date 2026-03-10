# codeaois/agents/coder_agent.py
from codeaois.models.llm_interface import call_openrouter

def generate_code(user_prompt: str, file_context: str = "") -> str:
    if file_context:
        # SURGICAL MODE: For editing existing files
        system_prompt = (
            "You are the CodeAOIS Coder Agent. The user wants to modify an existing file. "
            "You MUST output your changes using the following strict Search/Replace format:\n\n"
            "<<<<<<< SEARCH\n"
            "[exact existing code to find in the file]\n"
            "=======\n"
            "[new code to replace it with]\n"
            ">>>>>>> REPLACE\n\n"
            "Do not output the entire file. Only output the exact blocks that need changing. "
            "Make sure the SEARCH block matches the existing file exactly, character for character."
        )
    else:
        # CREATION MODE: For brand new files
        system_prompt = (
            "You are the CodeAOIS Coder Agent, an expert senior software engineer. "
            "Your job is to provide highly optimized, functional code. "
            "CRITICAL: Output ONLY the raw, complete code. Do not wrap the code in markdown blocks."
        )
    
    full_prompt = user_prompt
    if file_context:
        full_prompt += f"\n\nHere are the existing files for context:\n{file_context}"
        
    response = call_openrouter(system_prompt, full_prompt, intent="code")
            
    return response.strip()