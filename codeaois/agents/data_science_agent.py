# codeaois/agents/data_science_agent.py
from codeaois.models.llm_interface import call_openrouter

def generate_ds_code(user_prompt: str, file_context: str = "") -> str:
    system_prompt = (
        "You are the CodeAOIS Data Science Agent, an elite data scientist and Python developer. "
        "Your job is to provide highly optimized, memory-efficient code for data manipulation, "
        "analysis, and visualization. "
        "CRITICAL: Output ONLY the raw, complete code. Do not wrap the code in markdown blocks."
    )
    
    full_prompt = user_prompt
    if file_context:
        full_prompt += f"\n\nHere are the existing files for context. Modify as requested:\n{file_context}"
        
    # Pass the data_science intent to trigger the Qwen/Step model list
    response = call_openrouter(system_prompt, full_prompt, intent="data_science")
    
    if response.startswith("```"):
        lines = response.split("\n")
        if len(lines) > 2:
            response = "\n".join(lines[1:-1])
            
    return response.strip()