# codeaois/core/marketplace.py
import os
import time
from pathlib import Path

def install_agent(agent_name: str):
    """
    Goal #11: Agent Marketplace.
    Simulates downloading and installing a specialized worker agent.
    """
    print(f"🌐 [Marketplace]: Searching registry for '{agent_name}'...")
    time.sleep(1) # Simulate network latency
    
    # Clean up the name so it safely formats as a Python file (e.g., "3D Agent" -> "3d_agent")
    clean_name = agent_name.lower().replace("-", "_").replace(" ", "_")
    if not clean_name.endswith("_agent"):
        clean_name += "_agent"
        
    filename = f"{clean_name}.py"
    
    # Safely target the codeaois/agents/ directory
    # __file__ is marketplace.py -> parent is core/ -> parent is codeaois/ -> /agents
    agents_dir = Path(__file__).resolve().parent.parent / "agents"
    file_path = agents_dir / filename
    
    if file_path.exists():
        print(f"✅ [Marketplace]: '{clean_name}' is already installed at {file_path}")
        return
        
    print(f"⬇️  [Marketplace]: Downloading '{clean_name}'...")
    time.sleep(1.5) # Simulate download time
    
    # Generate the boilerplate code for the new agent
    function_name = clean_name.replace("_agent", "")
    agent_code = f'''# codeaois/agents/{filename}
from codeaois.models.llm_interface import call_openrouter

def generate_{function_name}_code(user_prompt: str, file_context: str = "") -> str:
    """Specialized {clean_name.replace('_', ' ').title()} worker."""
    system_prompt = (
        "You are the CodeAOIS {clean_name.replace('_', ' ').title()}. "
        "Your job is to provide highly optimized, expert-level code strictly for your specific domain. "
        "CRITICAL: Output ONLY the raw, complete code. Do not wrap the code in markdown blocks."
    )
    
    full_prompt = user_prompt
    if file_context:
        full_prompt += f"\\n\\nHere are the existing files for context:\\n{{file_context}}"
        
    response = call_openrouter(system_prompt, full_prompt)
    
    if response.startswith("```"):
        lines = response.split("\\n")
        if len(lines) > 2:
            response = "\\n".join(lines[1:-1])
            
    return response.strip()
'''
    
    # Save the new agent into the OS
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(agent_code)
        
    print(f"🚀 [Marketplace]: Successfully installed '{clean_name}'!")
    print(f"   -> Location: {file_path}")