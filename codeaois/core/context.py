# codeaois/core/context.py
import os

def extract_file_context(user_prompt: str) -> tuple[str, str]:
    """Finds all files in the prompt, targets the first, and reads all of them for context."""
    
    # Clean up punctuation so 'index.html,' doesn't break the scanner
    clean_prompt = user_prompt.replace(",", " ").replace("'", "").replace('"', "")
    words = clean_prompt.split()
    
    mentioned_files = []
    valid_extensions = [".py", ".js", ".html", ".css", ".json", ".txt", ".csv", ".md", ".db", ".sql"]
    
    # 1. Find every single file mentioned in the sentence
    for word in words:
        for ext in valid_extensions:
            if word.endswith(ext):
                clean_name = word.strip(".:;!?")
                if clean_name not in mentioned_files:
                    mentioned_files.append(clean_name)

    # If no files are mentioned, return nothing (main.py will use active_file fallback)
    if not mentioned_files:
        return None, ""
        
    # 2. The FIRST file mentioned is our target for editing
    target_file = mentioned_files[0]
    
    # 3. Build a massive context string containing EVERY file they mentioned
    combined_context = ""
    for file_name in mentioned_files:
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as f:
                content = f.read()
            combined_context += f"\n--- Contents of {file_name} ---\n{content}\n"
        else:
            combined_context += f"\n--- {file_name} (File does not exist yet) ---\n"
            
    return target_file, combined_context