# codeaois/agents/3d_agent.py
from codeaois.models.llm_interface import call_openrouter

def generate_3d_code(user_prompt: str, file_context: str = "") -> str:
    """Specialized 3D Agent worker."""
    system_prompt = (
        "You are the CodeAOIS 3D Agent. "
        "Your job is to provide highly optimized, expert-level code strictly for your specific domain. "
        "CRITICAL: Output ONLY the raw, complete code. Do not wrap the code in markdown blocks."
    )
    
    full_prompt = user_prompt
    if file_context:
        full_prompt += f"\n\nHere are the existing files for context:\n{file_context}"
        
    response = call_openrouter(system_prompt, full_prompt)
    
    if response.startswith("```"):
        lines = response.split("\n")
        if len(lines) > 2:
            response = "\n".join(lines[1:-1])
            
    return response.strip()
