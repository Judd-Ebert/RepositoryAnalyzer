from pydantic import BaseModel

class QueryRequest(BaseModel):
    repo_id: str
    question: str

class ImportRequest(BaseModel):
    github_url: str