"""
Judd Ebert 3/15/2026
Go from vectors to searchable index
"""

FLOATS_PER_CHUNK=768 # 3072 For Regular Use
STORAGE_DIR = "backend/storage"

import faiss
import hashlib
import numpy as np
import json
import os
def build_index(chunks: list[dict], github_url:str):
    chunks_array = np.zeros((len(chunks), FLOATS_PER_CHUNK), dtype=np.float32)
    for i, chunk in enumerate(chunks):
        chunks_array[i] = chunk["embedding"]
    
    faiss.normalize_L2(chunks_array) #Normalizes all arrays for cosine similarity

    index = faiss.IndexFlatIP(FLOATS_PER_CHUNK) #Index for searching
    index.add(chunks_array)

    repo_id = hashlib.md5(github_url.encode()).hexdigest()[:12]
    os.makedirs(STORAGE_DIR, exist_ok=True)

    faiss.write_index(index, f"{STORAGE_DIR}/{repo_id}.index")

    metadata = [
        {k: v for k, v in chunk.items() if k!= "embedding"}
        for chunk in chunks
    ]
    with open(f"{STORAGE_DIR}/{repo_id}.json", "w") as f:
        json.dump(metadata, f)

    return repo_id