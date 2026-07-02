import os

from openai import OpenAI


# Use local Ollama by default; allow env vars to switch to hosted OpenAI-compatible endpoints.
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
    base_url=os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1"),
)

KEYRING_SERVICE = "RepositoryAnalyzer"

CURRENT_SCHEMA_VERSION = 1

PERMANENT_USER_PREFERENCES_ID = 1

FLOATS_PER_CHUNK=768 # 3072 For Regular Use

STORAGE_DIR = "backend/storage"


SYSTEM_PROMPT = """
You are RepositoryAnalyzer, a codebase Q&A assistant.
Rules:
1) Answer ONLY using the provided context chunks.
2) If context is insufficient, say: "I don't have enough context to answer that."
3) Do not invent files, functions, behavior, or APIs.
4) Cite evidence inline as [file_path:start_line].
5) Be concise and technical.
6) Answer only in English.
Output format:
- Summary: 2-4 sentences
- Evidence: 2-6 bullet points with citations
"""