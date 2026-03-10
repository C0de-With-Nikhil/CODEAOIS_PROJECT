import os
import numpy as np
from sentence_transformers import SentenceTransformer

# Lightweight model for semantic search
model = SentenceTransformer("all-MiniLM-L6-v2")

class ProjectEmbeddings:
    def __init__(self):
        self.index = {}  # {filepath: embedding}

    def build_index(self, project_path="."):
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in {"aois_env", ".git", "__pycache__", "node_modules"}]
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    with open(path, "r", encoding="utf-8") as file:
                        content = file.read()
                    embedding = model.encode(content)
                    self.index[path] = embedding

    def search(self, query, top_k=3):
        q_vec = model.encode(query)
        distances = [(f, np.dot(q_vec, emb)) for f, emb in self.index.items()]
        distances.sort(key=lambda x: x[1], reverse=True)
        return distances[:top_k]