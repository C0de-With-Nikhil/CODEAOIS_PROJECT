import os
import json
import re
from rich.console import Console
from codeaois.models.llm_interface import call_openrouter

console = Console()

def generate_scaffolder_code(user_input, full_context=""):
    """Forces the AI to design a multi-file project architecture and writes it to disk."""
    console.print("[dim]🏗️  [Scaffolder] Architecting multi-file project structure...[/dim]")
    
    sys_prompt = """You are an Expert Software Architect. The user wants to generate a complete, multi-file project.
    You MUST respond ONLY with a valid JSON object representing the file structure and code. 
    Do not add conversational text. Only JSON.
    
    Format EXACTLY like this:
    {
        "project_name": "my_new_app",
        "files": [
            {"path": "main.py", "content": "print('hello world')"},
            {"path": "src/utils.py", "content": "def add(a,b): return a+b"},
            {"path": "requirements.txt", "content": "requests==2.31.0"}
        ]
    }
    """
    
    # Send request to your active AI model
    response = call_openrouter(sys_prompt, user_input, intent="code", history=[])
    
    try:
        # Extract the JSON even if the AI wraps it in markdown blocks
        json_str = response.strip()
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Fallback: Find the first { and last }
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            
        data = json.loads(json_str)
        project_name = data.get("project_name", "new_project")
        files = data.get("files", [])
        
        if not files:
            return "❌ AI didn't return any valid files to generate."
            
        console.print(f"\n[bold cyan]📦 Building Project Directory: {project_name}[/bold cyan]")
        
        # Build the folders and files!
        for f in files:
            file_path = os.path.join(project_name, f["path"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True) # Create folders if they don't exist
            with open(file_path, "w", encoding="utf-8") as out_file:
                out_file.write(f["content"])
            console.print(f"[green]  + Created: {f['path']}[/green]")
            
        return f"### 🏗️ Scaffolding Complete!\nSuccessfully generated `{project_name}` with {len(files)} files and folders."
        
    except Exception as e:
        return f"❌ **Scaffolder JSON Parsing Error:** The AI failed to output valid JSON. Try a smarter coding model.\n*Error: {e}*"
