from fastapi import HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from ..main import app

import logging

from backend.search.retriever import retrieve
from backend.llm.explainer import explain

@app.get("/query")
async def query(repo_id: str, question: str, top_k: int):
    """Ask a question about an indexed repo"""
    try:
        chunks = retrieve(repo_id=repo_id, question=question, top_k=top_k)
        if not chunks:
            logging.error("No chunks found")
        
        async def result_generator():
            result = explain(question=question, chunks=chunks)
        
        