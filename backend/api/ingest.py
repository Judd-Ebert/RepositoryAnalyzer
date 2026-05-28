from fastapi import HTTPException, BackgroundTasks
from fastapi import APIRouter
import shutil
from backend.ingestion.cloner import clone_repo
from backend.ingestion.chunker import chunk_repository
from backend.ingestion.embedder import embed_chunks
from backend.ingestion.indexer import build_index
from backend.search.retriever import retrieve
from backend.llm.explainer import explain
from backend.models.schemas import ImportRequest
import logging

router = APIRouter()

@router.post("/ingest")
async def ingest(request: ImportRequest, background_tasks: BackgroundTasks):
    """Creates background task to ingest and sends back message"""
    github_url = request.github_url
    
    if "github.com" not in github_url:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    
    background_tasks.add_task(process_repo_task, github_url)
    
    return {"message": "Ingestion started", "url": github_url} #Return background job id here for pinging?
    
def process_repo_task(github_url: str):
    """Clones, chunks, embeds, and indexes a repo URL"""
    local_path = None

    try:
        local_path = clone_repo(github_url)
        
        chunks = chunk_repository(local_path)
        if not chunks:
            logging.error("Text chunks not found")
        
        chunks = embed_chunks(chunks)
        
        repo_id = build_index(chunks, github_url)
        
    except Exception as e:
        logging.error(f"Failed to ingest {github_url}: {e}")
    finally:
        if local_path:
            shutil.rmtree(local_path, ignore_errors=True) #Deletes copied files