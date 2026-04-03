from backend.config.config import FLOATS_PER_CHUNK, STORAGE_DIR, client

def explain(question: str, chunks: list{dict}) -> dict:

    