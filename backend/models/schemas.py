from pydantic import BaseModel

class QueryRequest(BaseModel):
    repo_id: str
    question: str

class ImportRequest(BaseModel):
    github_url: str
    embedding_provider: str
    embedding_model: str
    chat_provider: str
    chat_model: str