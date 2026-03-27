"""
Judd Ebert 3/15/2026
Go from chunks to vectors using OpenAI embedding
"""

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
import os
from itertools import islice
from tenacity import retry, wait_exponential, retry_if_exception_type
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
CHUNKS_PER_CALL = 100

def embed_chunks(chunks: list[dict]) -> list[dict]:
    iterator = iter(chunks)
    sliced_chunks = [list(islice(iterator, CHUNKS_PER_CALL)) for _ in range((len(chunks) + CHUNKS_PER_CALL - 1) // CHUNKS_PER_CALL)] # range logic ensures incomplete chunks will be included
    for batch in sliced_chunks:
        call_api(batch)
    return chunks
    

@retry( # Tenacity to retry if function hits rate-limiting
        wait=wait_exponential(multiplier = 1, min = 4, max = 30),
        retry=retry_if_exception_type(RateLimitError),
        )
def call_api(batch: list[dict]):
        texts = [chunk["text"] for chunk in batch]
        response = client.embeddings.create(
            input=texts,
            model="text-embedding-3-large"
        )
        for chunk, embedding_obj in zip(batch, response.data):
             chunk["embedding"] = embedding_obj.embedding
        return batch