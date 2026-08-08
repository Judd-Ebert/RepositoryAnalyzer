from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.db_helpers import init_db
from contextlib import asynccontextmanager

from backend.api.ingest import router as ingest_router
from  backend.api.query import router as query_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    #Anything I want when app starts
    init_db()
    
    yield
    #Anything I want when app closes


app = FastAPI(lifespan=lifespan)

app.include_router(ingest_router)
app.include_router(query_router)

@app.get("/health")
def health():
    return {"status": "ok"}


# Restrict browser origins to local machine only.
allowed_origins = [
    "tauri://localhost",
    "http://tauri.localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)