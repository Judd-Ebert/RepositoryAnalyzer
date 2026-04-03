import faiss
import json
import numpy as np
from backend.config.config import client, FLOATS_PER_CHUNK, STORAGE_DIR



def retrieve(repo_id: str, question: str, top_k: int = 8) -> list[dict]:
    index, metadata =load_data(repo_id)
    # Numpy converts the List to a 2D array of dimensions [1, FLOATS_PER_CHUNK] for the Faiss cosine comparison
    embedded_question = np.array(call_api_question(question), dtype=np.float32).reshape(1, FLOATS_PER_CHUNK) 
    faiss.normalize_L2(embedded_question)

    distances, indices = index.search(embedded_question, top_k)

    responses = []

    for i, position in enumerate(indices[0]):
        if position == -1:
            continue
        responses.append({**metadata[position], "score": float(distances[0][i])})

    return responses


def load_data(repo_id: str):
    index = faiss.read_index(f"{STORAGE_DIR}/{repo_id}.index")

    with open(f"{STORAGE_DIR}/{repo_id}.json") as f:
        metadata = json.load(f)
    return index, metadata


def call_api_question(question: str):
    response = client.embeddings.create(
        input=question,
        # For Regular Use: model="text-embedding-3-large"
        model = "nomic-embed-text"
    )
    return response.data[0].embedding

if __name__ == "__main__":
    results = retrieve("86b1d73dd0bc", "What does this repo do?")
    for r in results:
        print(r["score"], r["file_path"], r["start_line"])
        print(r["text"][:100])
        print()