import os
import json
import re
from pathlib import Path

class CodebaseMemory:
    def __init__(self, project_path="."):
        self.project_path = Path(project_path)
        self.db_dir = self.project_path / ".codeaois_db"
        self.db_file = self.db_dir / "local_index.json"
        
        # Folders and files we DO NOT want the AI to read
        self.ignore_dirs = {".git", "__pycache__", "venv", "env", "node_modules", ".codeaois_db", "dist", "build"}
        self.ignore_exts = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".exe", ".dll", ".so", ".pdf", ".zip"}

    def _chunk_text(self, text, max_chars=1500):
        """Chops large code files into digestible blocks for the AI."""
        lines = text.split('\n')
        chunks = []
        current_chunk = ""
        
        for line in lines:
            if len(current_chunk) + len(line) > max_chars:
                chunks.append(current_chunk)
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
                
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def index_project(self):
        """Scans the project, chunks the code, and saves it to the local brain."""
        self.db_dir.mkdir(exist_ok=True)
        
        chunks_indexed = 0
        index_data = []

        for root, dirs, files in os.walk(self.project_path):
            # Skip ignored directories and hidden folders
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs and not d.startswith('.')]
            
            for file in files:
                # Skip ignored extensions and hidden files
                if any(file.endswith(ext) for ext in self.ignore_exts) or file.startswith('.'):
                    continue
                    
                file_path = Path(root) / file
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Break the file into chunks
                    chunks = self._chunk_text(content)
                    
                    for i, chunk in enumerate(chunks):
                        index_data.append({
                            "file": str(file_path.relative_to(self.project_path)),
                            "chunk_id": i,
                            "content": chunk
                        })
                        chunks_indexed += 1
                except Exception:
                    # Silently skip binary files or files with weird encodings
                    continue 

        # Save the brain to the hidden database folder
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=4)
            
        return chunks_indexed
    
    def search(self, query, top_k=3):
        """Searches the local JSON brain for chunks matching the user's prompt."""
        if not self.db_file.exists():
            return "" # Brain is empty, run /index first
            
        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                index_data = json.load(f)
        except Exception:
            return ""

        # Simple keyword scoring engine
        query_words = set(re.findall(r'\w+', query.lower()))
        # Ignore common filler words
        stop_words = {"a", "the", "is", "in", "to", "and", "how", "what", "where", "write", "code"}
        search_words = query_words - stop_words
        
        if not search_words:
            return ""

        scored_chunks = []
        for item in index_data:
            chunk_text = item["content"].lower()
            # Give a point for every matching keyword
            score = sum(1 for word in search_words if word in chunk_text)
            if score > 0:
                scored_chunks.append((score, item))

        # Sort from highest score to lowest
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Grab the top results and format them
        results = []
        for score, item in scored_chunks[:top_k]:
            results.append(f"--- Auto-Retrieved Context: {item['file']} ---\n{item['content']}")
            
        return "\n\n".join(results)