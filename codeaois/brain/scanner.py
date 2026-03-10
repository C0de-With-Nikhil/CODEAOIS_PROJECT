# codeaois/brain/scanner.py
import os

def scan_project_structure(root_dir: str = ".", ignore_dirs: list = None, max_depth: int = 3, max_files: int = 200) -> str:
    """
    Goal #9: Project Brain (with safety limits).
    Scans the folder structure but strictly limits depth and file count 
    to prevent network timeouts when run in massive directories like '~'.
    """
    if ignore_dirs is None:
        # Added OS-level hidden folders to ignore list
        ignore_dirs = ['.git', '__pycache__', 'venv', 'env', 'node_modules', '.venv', 'codeaois.egg-info', '.cache', '.config', '.local']

    tree_str = f"📁 Project Root: {os.path.abspath(root_dir)}\n"
    file_count = 0
    
    # Calculate starting depth
    start_level = root_dir.rstrip(os.sep).count(os.sep)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Calculate current depth relative to start
        current_level = dirpath.rstrip(os.sep).count(os.sep)
        level = current_level - start_level
        
        # Stop digging if we hit our depth limit
        if level > max_depth:
            dirnames[:] = [] # Clear the list to stop os.walk from going deeper
            continue

        dirnames[:] = [d for d in dirnames if d not in ignore_dirs and not d.startswith('.')]
        
        indent = ' ' * 4 * level
        folder_name = os.path.basename(dirpath)
        
        if level > 0:
            tree_str += f"{indent}📂 {folder_name}/\n"
            
        sub_indent = ' ' * 4 * (level + 1)
        for f in filenames:
            # Emergency Stop: Prevent massive payloads from timing out the API
            if file_count >= max_files:
                tree_str += f"{sub_indent}... [Max file limit reached to protect API connection]\n"
                return tree_str 
                
            if f != '.env' and not f.startswith('.'):
                tree_str += f"{sub_indent}📄 {f}\n"
                file_count += 1
                
    return tree_str