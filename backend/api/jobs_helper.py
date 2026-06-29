from fastapi import APIRouter, HTTPException
from backend.db.db_helpers import get_job_status


router = APIRouter()
@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    """
    Get the status of a job by its ID.
    """
    job = get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
