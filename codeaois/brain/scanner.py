# codeaois/brain/scanner.py
import os
import pathspec

import os

# --- THE CONTEXT SHIELD ---
IGNORE_DIRS = {".git", "node_modules", "venv", "env", "__pycache__", ".codeaois_db", "build", "dist", ".idea", ".vscode"}
IGNORE_FILES = {".env", ".DS_Store", "package-lock.json", "yarn.lock"}
IGNORE_EXTS = {".pyc", ".png", ".jpg", ".jpeg", ".exe", ".dll", ".so", ".zip", ".tar.gz", ".pdf", ".mp4"}

def scan_project_structure(root_dir="."):
    """Scans the directory tree, but shields the AI from massive junk folders and binary files."""
    tree_str = ""
    
    for root, dirs, files in os.walk(root_dir):
        # IN-PLACE FILTERING: This physically stops the OS from even looking inside node_modules or .git!
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        folder_name = os.path.basename(root)
        
        if folder_name:
            tree_str += f"{indent}📂 {folder_name}/\n"
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            # Block secret files and heavy images/binaries
            if f in IGNORE_FILES or any(f.endswith(ext) for ext in IGNORE_EXTS):
                continue
            tree_str += f"{subindent}📄 {f}\n"
            
    return tree_str if tree_str else "📂 (Empty Project)"
class CodeScanner:
    def __init__(self, root_dir="."):
        self.root_dir = root_dir
        # Standard directories and files to ignore globally for RAG Embeddings
        self.default_ignores = [
            ".git", "venv", "env", "__pycache__", "node_modules", 
            ".pytest_cache", "dist", "build", "*.egg-info", 
            "*.pyc", "*.png", "*.jpg", "*.pdf", ".codeaois_db"
        ]
        self.ignore_spec = self._load_gitignore()

    def _load_gitignore(self):
        """Loads .gitignore if it exists and combines it with defaults."""
        ignore_patterns = list(self.default_ignores)
        gitignore_path = os.path.join(self.root_dir, ".gitignore")
        
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                ignore_patterns.extend(f.read().splitlines())
                
        return pathspec.PathSpec.from_lines('gitwildmatch', ignore_patterns)

    def scan_project(self):
        """Yields (filepath, content) for all valid code files."""
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            # Filter out ignored directories in-place
            dirnames[:] = [d for d in dirnames if not self.ignore_spec.match_file(os.path.join(dirpath, d))]
            
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, self.root_dir)
                
                if self.ignore_spec.match_file(rel_path):
                    continue
                    
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        yield rel_path, f.read()
                except UnicodeDecodeError:
                    # Skip binary files that slipped through
                    pass