"""
Judd Ebert 3/15/2026
Temp test file to run pipeline before converting to FastAPI server
"""

import sys
import os

# Allows running from project root
sys.path.insert(0, os.path.dirname(__file__))

from cloner import clone_repo
from embedder import embed_chunks
from chunker import chunk_repository
from indexer import build_index

TEST_URL = "https://github.com/navdeep-G/samplemod" #Small python repo

def run_pipeline(url: str):
    print(f"\n--- Step 1: Cloning ---")
    local_path = clone_repo(url)
    print(f"Cloned to: {local_path}")

    print(f"\n--- Step 2: Chunking ---")
    chunks = chunk_repository(local_path)
    print(f"Total chunks: {len(chunks)}")
    if chunks:
        s = chunks[0]
        print(f"Sample: file={s['file_path']}, lang={s['language']}, start_line={s['start_line']}")
        print(f"Text preview: {s['text'][:120]!r}")
    
    print(f"\n--- Step 3: Embedding ---")
    chunks = embed_chunks(chunks)
    embedded = sum(1 for c in chunks if "embedding" in c)
    print(f"Embedded: {embedded}/{len(chunks)}")
    if embedded:
        print(f"Dimensions (should be 3072): {len(chunks[0]["embedding"])}")

    print(f"\n--- Step 4: Indexing ---")
    repo_id = build_index(chunks, url)
    print(f"repo_id: {repo_id}")
    print(f"Files: backend/storage/{repo_id}.index + .json")
    print(f"\n--- Done ---")
    return repo_id

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else TEST_URL
    run_pipeline(url)