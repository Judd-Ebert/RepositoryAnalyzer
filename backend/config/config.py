import os

from openai import OpenAI
from typing import Optional\

KEYRING_SERVICE = "RepositoryAnalyzer"

CURRENT_SCHEMA_VERSION = 1

PERMANENT_USER_PREFERENCES_ID = 1

FLOATS_PER_CHUNK=768 # 3072 For Regular Use

STORAGE_DIR = "backend/storage"

OPENAI_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")

OLLAMA_CHAT_MODELS = [
    "llama3.3",
    "llama3.2",
    "llama3.1",
    "mistral",
    "qwen2.5",
    "gemma2",
    "phi3.5",
    "deepseek-r1",
    "codellama",
    "mixtral",
    "qwen:latest",
]

OLLAMA_EMBEDDING_MODELS = [
    "nomic-embed-text",
    "mxbai-embed-large",
    "all-minilm",
    "bge-m3",
    "bge-large",
    "snowflake-arctic-embed",
]

def normalize_provider(provider: str) -> str:
    if not provider:
        raise ValueError("Provider is required.")

    provider = provider.strip().lower()
    if provider == "openai":
        return "OpenAI"
    elif provider == "ollama":
        return "Ollama"
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def is_ollama(provider: str) -> bool:
    return normalize_provider(provider) == "Ollama"

def is_openai(provider: str) -> bool:
    return normalize_provider(provider) == "OpenAI"

def provider_base_url(provider: str) -> str:
    if is_openai(provider):
        return OPENAI_URL
    elif is_ollama(provider):
        return OLLAMA_URL
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def provider_api_key(provider: str, explicit_key: Optional[str] | None = None) -> str:
    if explicit_key:
        return explicit_key
    if is_ollama(provider):
        return os.environ.get("OLLAMA_API_KEY", "ollama")
    return os.environ.get("OPENAI_API_KEY")

def build_client(provider: str, explicit_key: Optional[str] | None = None) -> OpenAI:
    return OpenAI(
        api_key=provider_api_key(provider, explicit_key),
        base_url=provider_base_url(provider)
    )



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