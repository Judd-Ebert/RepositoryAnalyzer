from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from fastapi import APIRouter

import logging

from backend.search.retriever import retrieve
from backend.llm.explainer import explain

router = APIRouter()

@router.get("/query")
async def query(repo_id: str, question: str, top_k: int):
    """Ask a question about an indexed repo"""
    try:
        chunks = retrieve(repo_id=repo_id, question=question, top_k=top_k)
        if not chunks:
            logging.error("No chunks found")
            raise HTTPException(status_code=404, detail="No relevant chunks found")
        def result_generator():
            yield from explain(question=question, chunks=chunks)
        return StreamingResponse(result_generator(), media_type="text/plain")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to explain {question}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate answer")