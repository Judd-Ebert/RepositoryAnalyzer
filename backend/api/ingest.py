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

from openai import OpenAI
import openai

import logging

import uuid


# ** Helper Functions

def validate_openai_embedding_access(api_key: str, model: str) -> None:
        try:
            client = OpenAI(api_key=api_key)
            client.models.retrieve(model)

        except openai.AuthenticationError:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "invalid_api_key",
                    "message": "Your OpenAI API key is invalid.",
                    "retryable": False,
                    "provider": "openai",
                },
            )

        except openai.PermissionDeniedError:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "model_access_denied",
                    "message": "API key is valid, but it does not have access to this model.",
                    "retryable": False,
                    "provider": "openai",
                },
            )

        except openai.NotFoundError:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "model_not_found",
                    "message": "The selected OpenAI model does not exist.",
                    "retryable": False,
                    "provider": "openai",
                },
            )

        except openai.RateLimitError:
            raise HTTPException(
                status_code=429,
                detail={
                    "code": "rate_limited_or_quota",
                    "message": "OpenAI rate limit or quota reached. Try again shortly.",
                    "retryable": True,
                    "provider": "openai",
                },
            )

        except (openai.APIConnectionError, openai.APITimeoutError):
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "provider_unreachable",
                    "message": "Could not reach OpenAI. Check network and try again.",
                    "retryable": True,
                    "provider": "openai",
                },
            )
        
        except openai.APIStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail={
                    "code": "provider_error",
                    "message": "OpenAI returned an unexpected error.",
                    "retryable": True,
                    "provider": "openai",
                },
            )
        
def process_repo_task(github_url: str, job_id: str, request: ImportRequest):
    """Clones, chunks, embeds, and indexes a repo URL"""
    local_path = None

    try:
        #Status = Importing
        local_path = clone_repo(github_url)
        
        #Status = Chunking
        chunks = chunk_repository(local_path)
        if not chunks:
            logging.error("Text chunks not found")
        
        #Status = Embedding
        chunks = embed_chunks(chunks, request)

        #Status = Indexing
        repo_id = build_index(chunks, github_url)
        
    except Exception as e:
        logging.error(f"Failed to ingest {github_url}: {e}")
    finally:
        if local_path:
            shutil.rmtree(local_path, ignore_errors=True) #Deletes copied files
    
    #Status = Completed


# ** Routes


router = APIRouter()
@router.post("/ingest")
async def ingest(request: ImportRequest, background_tasks: BackgroundTasks):
    #Validate Keys
    if request.embedding_provider == "OpenAI":
        validate_openai_embedding_access(request.embedding_key, request.embedding_model)

    """Creates background task to ingest and sends back message"""
    github_url = request.github_url
    
    if "github.com" not in github_url:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    
    job_id = str(uuid.uuid4())
    
    background_tasks.add_task(process_repo_task, github_url, job_id, request)
    
    return {"message": "Ingestion started", "url": github_url, "job_id": job_id} 

   