# codeaois/utils/file_writer.py
import os
import re
C_YELLOW = '\033[93m'
C_GREEN = '\033[92m'
C_RESET = '\033[0m'

def extract_and_save_code(response_text: str, default_filename: str = "untitled_generation.txt") -> tuple[bool, str]:
    """Saves the code and returns the AI's explanation summary."""
    
    # Split the AI's response into Code and Summary
    parts = response_text.split("---SUMMARY---")
    code_part = parts[0].strip()
    summary_part = parts[1].strip() if len(parts) > 1 else "No summary provided by the agent."

    # --- 1. SURGICAL EDIT MODE ---
    if "<<<<<<< SEARCH" in code_part:
        if not os.path.exists(default_filename):
            print(f"⚠️ Error: Target file {default_filename} does not exist.")
            return False, ""
            
        with open(default_filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        blocks = code_part.split("<<<<<<< SEARCH\n")[1:]
        success_count = 0
        new_content = content
        
        for block in blocks:
            if "=======\n" not in block or ">>>>>>> REPLACE" not in block:
                continue
            
            search_part = block.split("=======\n")[0]
            replace_part = block.split("=======\n")[1].split(">>>>>>> REPLACE")[0]
            
            if search_part in new_content:
                new_content = new_content.replace(search_part, replace_part)
                success_count += 1
                
        if success_count > 0:
            confirm = input(f"\n{C_YELLOW}⚠️ [Security] Allow modification of {success_count} section(s) in '{default_filename}'? [Y/n]: {C_RESET}").strip().lower()
            if confirm not in ['y', '']:
                return False, ""
                
            with open(default_filename, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"{C_GREEN}✅ Surgically updated {default_filename}{C_RESET}")
            return True, summary_part
        return False, ""
        
    # --- 2. NEW FILE MODE ---
    if "```" in code_part:
        lines = code_part.split("\n")
        code_lines = [line for line in lines if not line.startswith("```")]
        code_part = "\n".join(code_lines)
            
    confirm = input(f"\n{C_YELLOW}⚠️ [Security] Allow creation of '{default_filename}'? [Y/n]: {C_RESET}").strip().lower()
    if confirm not in ['y', '']:
        return False, ""
        
    with open(default_filename, "w", encoding="utf-8") as f:
        f.write(code_part.strip())
        
    print(f"{C_GREEN}✅ Successfully created: {default_filename}{C_RESET}")
    return True, summary_part