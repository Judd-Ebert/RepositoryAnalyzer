from pydantic import BaseModel

class QueryRequest(BaseModel):
    repo_id: str
    question: str