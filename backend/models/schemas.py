from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    repo_id: str
    question: str

class ImportRequest(BaseModel):
    github_url: str
    embedding_provider: str
    embedding_model: str
    embedding_key: Optional[str] = None
    chat_provider: str
    chat_model: str
    chat_key: Optional[str] = None