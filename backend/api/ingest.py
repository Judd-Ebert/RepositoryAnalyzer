from fastapi import HTTPException, BackgroundTasks
from fastapi import APIRouter
import shutil
from backend.db.api_key_storage_helpers import create_api_key
from backend.db.db_helpers import create_job, set_preferences, update_job_status, upsert_repository
from backend.ingestion.cloner import clone_repo
from backend.ingestion.chunker import chunk_repository
from backend.ingestion.embedder import embed_chunks
from backend.ingestion.indexer import build_index
from backend.models.schemas import ImportRequest
from backend.config.config import OLLAMA_URL, build_client, normalize_provider

from openai import OpenAI
import openai

import logging

import uuid


# ** Helper Functions

def validate_embedding_access(api_key: str, model: str, provider: str,) -> None:
        #Dummy call to check if API key is valid and has access to the model
        provider = normalize_provider(provider)
        if provider not in ("OpenAI", "Ollama"):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "unsupported_provider",
                    "message": f"Unsupported embedding provider: {provider}",
                    "retryable": False,
                    "provider": provider,
                },
            )
        try:
            client= build_client(provider, api_key)
            client.embeddings.create(
                input=["test"],
                model=model,
            )
        except openai.AuthenticationError:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "invalid_api_key",
                    "message": f"Your {provider} API key is invalid.",
                    "retryable": False,
                    "provider": provider,
                },
            )

        except openai.PermissionDeniedError:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "model_access_denied",
                    "message": "API key is valid, but it does not have access to this model.",
                    "retryable": False,
                    "provider": provider,
                },
            )

        except openai.NotFoundError:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "model_not_found",
                    "message": f"The selected {provider} model does not exist.",
                    "retryable": False,
                    "provider": provider,
                },
            )

        except openai.RateLimitError:
            raise HTTPException(
                status_code=429,
                detail={
                    "code": "rate_limited_or_quota",
                    "message": f"{provider} rate limit or quota reached. Try again shortly.",
                    "retryable": True,
                    "provider": provider,
                },
            )

        except (openai.APIConnectionError, openai.APITimeoutError):
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "provider_unreachable",
                    "message": f"Could not reach {provider}. Check network and try again.",
                    "retryable": True,
                    "provider": provider,
                },
            )
        
        except openai.APIStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail={
                    "code": "provider_error",
                    "message": f"{provider} returned an unexpected error.",
                    "retryable": True,
                    "provider": provider,
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
    if request.embedding_provider == "OpenAI" or request.embedding_provider == "Ollama":
        validate_embedding_access(request.embedding_key, request.embedding_model, request.embedding_provider)

    """Creates background task to ingest and sends back message"""
    github_url = request.github_url
    
    if "github.com" not in github_url:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    
    #Create Keys
    chat_model_username = f"chat-{request.chat_provider}-{request.chat_model}"
    embedding_model_username = f"embedding-{request.embedding_provider}-{request.embedding_model}"

    create_api_key(embedding_model_username, request.embedding_key)
    create_api_key(chat_model_username, request.chat_key)
    
    set_preferences(
        embedding_provider=request.embedding_provider,
        embedding_model=request.embedding_model,
        chat_provider=request.chat_provider,
        chat_model=request.chat_model,
        embedding_api_key_username=embedding_model_username,
        chat_api_key_username=chat_model_username,
    )
    upsert_repository(github_url)
    
    job_id = str(uuid.uuid4())
    create_job(job_id, github_url, "queued")
    
    background_tasks.add_task(process_repo_task, github_url, job_id, request)
    
    return {"message": "Ingestion started", "url": github_url, "job_id": job_id} 

   