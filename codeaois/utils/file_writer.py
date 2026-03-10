# codeaois/utils/file_writer.py
import os

# ANSI color codes
C_YELLOW = '\033[93m'
C_GREEN = '\033[92m'
C_RESET = '\033[0m'

def extract_and_save_code(response_text: str, default_filename: str) -> bool:
    """Surgically edits an existing file or creates a new one with a security prompt."""
    
    # --- 1. SURGICAL EDIT MODE (Search & Replace) ---
    if "<<<<<<< SEARCH" in response_text:
        if not os.path.exists(default_filename):
            print(f"⚠️ Error: Target file {default_filename} does not exist for editing.")
            return False
            
        with open(default_filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        blocks = response_text.split("<<<<<<< SEARCH\n")[1:]
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
            else:
                print(f"⚠️ Could not find exact match for one of the SEARCH blocks. Skipped.")
        
        if success_count > 0:
            # --- THE SURGICAL SECURITY PROMPT ---
            confirm = input(f"\n{C_YELLOW}⚠️ [Security Dry-Run] Allow CodeAOIS to surgically modify {success_count} section(s) in '{default_filename}'? [Y/n]: {C_RESET}").strip().lower()
            if confirm != 'y' and confirm != '':
                print(f"🛑 Edit cancelled by user.")
                return False
                
            with open(default_filename, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"{C_GREEN}✅ Surgically updated {success_count} section(s) in: {default_filename}{C_RESET}")
            return True
        return False
        
    # --- 2. NEW FILE MODE (Standard Overwrite) ---
    code = response_text
    
    if "```" in code:
        lines = code.split("\n")
        code_lines = []
        in_block = False
        for line in lines:
            if line.startswith("```"):
                in_block = not in_block
                continue
            if in_block:
                code_lines.append(line)
        if code_lines:
            code = "\n".join(code_lines)
            
    # --- THE NEW FILE SECURITY PROMPT ---
    confirm = input(f"\n{C_YELLOW}⚠️ [Security Dry-Run] Allow CodeAOIS to create/overwrite the file '{default_filename}'? [Y/n]: {C_RESET}").strip().lower()
    if confirm != 'y' and confirm != '':
        print(f"🛑 File write cancelled by user.")
        return False
        
    with open(default_filename, "w", encoding="utf-8") as f:
        f.write(code.strip())
        
    print(f"{C_GREEN}✅ Successfully created: {default_filename}{C_RESET}")
    return True