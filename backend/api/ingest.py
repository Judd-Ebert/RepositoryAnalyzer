from fastapi import HTTPException, BackgroundTasks
from fastapi import APIRouter
import shutil
from backend.db.db_helpers import create_job, set_preferences, update_job_status, upsert_repository
from backend.ingestion.cloner import clone_repo
from backend.ingestion.chunker import chunk_repository
from backend.ingestion.embedder import embed_chunks
from backend.ingestion.indexer import build_index
from backend.models.schemas import ImportRequest

from openai import OpenAI
import openai

import logging

import uuid


# ** Helper Functions

def validate_openai_embedding_access(api_key: str, model: str) -> None:
        #Dummy call to check if API key is valid and has access to the model
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
        update_job_status(job_id, status="running", stage="importing")
        local_path = clone_repo(github_url)
        
        #Status = Chunking
        update_job_status(job_id, status="running", stage="chunking")
        chunks = chunk_repository(local_path)
        if not chunks:
            update_job_status(job_id, status="running", stage="failed", error_message="No text chunks were created from the repository.")
            logging.error("Text chunks not found")
        
        #Status = Embedding
        update_job_status(job_id, status="running", stage="embedding")
        chunks = embed_chunks(chunks, request)

        #Status = Indexing
        update_job_status(job_id, status="running", stage="indexing")
        repo_id = build_index(chunks, github_url)
        
    except Exception as e:
        logging.error(f"Failed to ingest {github_url}: {e}")
        update_job_status(job_id, status="failed", stage="failed", error_message=str(e))  # Update job status on failure
    finally:
        if local_path:
            shutil.rmtree(local_path, ignore_errors=True) #Deletes copied files
    
    #Status = Completed
    update_job_status(job_id, status="completed", stage="completed")


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
    
    #Create Keys
    
    
    set_preferences(
        embedding_provider=request.embedding_provider,
        embedding_model=request.embedding_model,
        chat_provider=request.chat_provider,
        chat_model=request.chat_model,
        embedding_credential_ref=f"embedding-{job_id}",
        chat_credential_ref=f"chat-{job_id}"
    )
    upsert_repository(github_url)
    
    job_id = str(uuid.uuid4())
    create_job(job_id, github_url, "queued")
    
    background_tasks.add_task(process_repo_task, github_url, job_id, request)
    
    return {"message": "Ingestion started", "url": github_url, "job_id": job_id} 

   