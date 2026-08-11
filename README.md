# Repository Analyzer

Repository Analyzer is a local-first tool for turning a GitHub repository into a searchable, question-answering codebase assistant. It clones a repo, splits it into chunks, creates embeddings, builds a FAISS index, and lets you ask questions about the code through a FastAPI backend.

## What it does

- Ingest a GitHub repository from the UI
- Choose embedding and chat providers/models
- Support OpenAI and Ollama workflows
- Index repository content for semantic search
- Ask questions about the indexed codebase

## Tech stack

- Backend: FastAPI, Python, SQLite, FAISS, OpenAI-compatible APIs
- Frontend: React, TypeScript, Vite
- Desktop app: Tauri

## Project structure

- backend/ — FastAPI app, ingestion pipeline, database helpers, search/retrieval logic
- frontend/RepositoryAnalyzerApp/ — React and Tauri frontend
- backend/storage/ — generated indexes and local database files

## Setup

### Requirements

- Python 3.10+
- Node.js 18+ and npm
- Rust toolchain for Tauri development
- Optional: Ollama running locally on http://localhost:11434 for local model support

### Backend

```bash
cd /Users/juddebert/Development/RepositoryAnalyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set the environment variables you need before starting the server:

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"   # optional
export OLLAMA_BASE_URL="http://localhost:11434/v1"  # optional
export OLLAMA_API_KEY="ollama"                      # optional
```

Run the backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at http://127.0.0.1:8000.

### Frontend

```bash
cd frontend/RepositoryAnalyzerApp
npm install
npm run dev
```

To run the desktop app:

```bash
npm run tauri dev
```

> The frontend currently calls the local FastAPI backend on port 8000 during development.

## How the flow works

1. The UI sends a GitHub URL and model/provider choices to the backend.
2. The backend clones the repository, chunks the files, creates embeddings, and builds a FAISS index.
3. The app stores repo metadata and ingestion job state in SQLite.
4. You can then query the indexed repository through the search and explanation flow.

## Notes

- The app stores its local SQLite database in backend/storage/app.db.
- Ollama support is already wired in, but provider/model handling is still being refined.
- The current UI is focused on getting the ingestion workflow working cleanly first.

## Current focus

- Wiring up live ingestion status updates so the UI can show what stage the backend is in
- Adding a job-status endpoint and polling flow for progress updates during imports
- Tightening provider selection and model handling for OpenAI and Ollama
- Cleaning up the landing page and initial onboarding experience

## Next steps

- Finish the end-to-end job tracking flow, including status updates in the database and UI polling
- Add better validation for embedding and chat API keys, including clearer failure states
- Improve the model picker so chat and embedding providers/models can be handled more cleanly
- Support more flexible local/remote provider combinations, including Ollama-backed workflows
- Polish the ingestion experience and error handling for failed or partial imports
