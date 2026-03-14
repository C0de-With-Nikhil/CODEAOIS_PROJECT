# codeaois/brain/scanner.py
import os
import pathspec

def scan_project_structure(root_dir=".", max_depth=3):
    """Generates a simple string tree of the project for the LLM context prompt."""
    tree = []
    # Ignore these heavy/hidden directories in the prompt tree
    ignore_dirs = {".git", "venv", "env", "__pycache__", "node_modules", ".codeaois_db", "codeaois.egg-info", "dist"}
    
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        level = root.replace(root_dir, '').count(os.sep)
        
        if level > max_depth:
            continue
            
        indent = ' ' * 4 * level
        folder_name = os.path.basename(root) if root != "." else os.path.basename(os.path.abspath(root_dir))
        tree.append(f"{indent}📂 {folder_name}/")
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if not f.endswith((".pyc", ".png", ".jpg", ".whl", ".tar.gz", ".vsix")):
                tree.append(f"{subindent}📄 {f}")
                
    return "\n".join(tree)

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