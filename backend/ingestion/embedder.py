"""
Judd Ebert 3/15/2026
Go from chunks to vectors using OpenAI embedding
"""

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
import os
from itertools import islice
from tenacity import retry, wait_exponential, retry_if_exception_type

from backend.models.schemas import ImportRequest

load_dotenv()

CHUNKS_PER_CALL = 100

def embed_chunks(chunks: list[dict], request: ImportRequest) -> list[dict]:
    iterator = iter(chunks)
    sliced_chunks = [list(islice(iterator, CHUNKS_PER_CALL)) for _ in range((len(chunks) + CHUNKS_PER_CALL - 1) // CHUNKS_PER_CALL)] # range logic ensures incomplete chunks will be included
    for batch in sliced_chunks:
        call_api_batch(batch, request.embedding_provider, request.embedding_model, request.embedding_key)
    return chunks
    

@retry(
        # Tenacity to retry if function hits rate-limiting
        wait=wait_exponential(multiplier = 1, min = 4, max = 30),
        retry=retry_if_exception_type(RateLimitError),
        )
def call_api_batch(batch: list[dict], embedding_provider: str, embedding_model: str, embedding_api_key: str):
        texts = [chunk["text"] for chunk in batch]
        if embedding_provider == "OpenAI":
            client = OpenAI(api_key=embedding_api_key, base_url="https://api.openai.com/v1") #? Should the API key be accessed through the database here?
            response = client.embeddings.create(
                input=texts,
                # For Regular Use: model="text-embedding-3-large"
                model = embedding_model, #"nomic-embed-text",
            )
        for chunk, embedding_obj in zip(batch, response.data):
             chunk["embedding"] = embedding_obj.embedding
        return batch