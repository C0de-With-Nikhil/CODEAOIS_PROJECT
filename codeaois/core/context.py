# codeaois/core/context.py
import os

def extract_file_context(user_prompt: str) -> tuple[str, str]:
    """
    Scans the prompt for valid file paths. If a file exists, it reads 
    the contents so the AI can understand the context.
    Returns a tuple: (target_file_path, file_contents_string)
    """
    words = user_prompt.split()
    context_string = ""
    target_file = None
    
    for word in words:
        # Strip away punctuation in case the user types: "edit app.py,"
        clean_word = word.strip("',.\"")
        
        # If the word matches a file in the current directory, grab it!
        if os.path.isfile(clean_word):
            target_file = clean_word
            with open(clean_word, "r", encoding="utf-8") as f:
                context_string += f"\n--- Contents of {clean_word} ---\n{f.read()}\n-------------------\n"
                
    return target_file, context_string