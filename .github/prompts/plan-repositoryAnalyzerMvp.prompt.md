# Plan: Repository Analyzer MVP (RAG Q&A)

**TL;DR** — Python FastAPI backend with a CLI-first interface. Ingests a GitHub repo, chunks code with language awareness, embeds with OpenAI, stores in a local FAISS index, then answers questions by retrieving top-k chunks and prompting GPT-4o-mini. Clean 4-phase build: ingestion → Q&A → CLI → API.

---

## Project Structure
```
RepositoryAnalyzer/
  backend/
    main.py                    # FastAPI app
    ingestion/
      cloner.py                # git clone via GitPython
      chunker.py               # language-aware splitting
      embedder.py              # OpenAI batch embedding calls
      indexer.py               # FAISS build + save/load
    search/
      retriever.py             # query → FAISS → top-k chunks
    llm/
      explainer.py             # GPT-4o-mini prompt + response
    models/
      schemas.py               # Pydantic schemas
    storage/                   # persisted .index + .json files per repo
    requirements.txt
  cli.py                       # CLI entry point
```

---

## Phase 1 — Ingestion Pipeline *(core, build first)*
1. **`cloner.py`** — Validate GitHub URL, `git clone` into a temp directory via GitPython. Return local path.
2. **`chunker.py`** — Walk the directory tree; skip `.git`, `node_modules`, `__pycache__`, binary files. Split text files using LangChain's `RecursiveCharacterTextSplitter` with language-aware splitters (~512 tokens, 64-token overlap). Attach metadata: `file_path`, `start_line`, `language`.
3. **`embedder.py`** — Batch-embed chunks via `openai.embeddings.create` (`text-embedding-3-large`). Use `tenacity` for retry/rate-limit handling.
4. **`indexer.py`** — Normalize embeddings, build `faiss.IndexFlatIP` (inner product = cosine on normalized vecs). Persist as `storage/{repo_id}.index` + `storage/{repo_id}.json`. `repo_id = md5(github_url)[:12]`.

## Phase 2 — Q&A Pipeline *(depends on Phase 1)*
5. **`retriever.py`** — Embed the query with the same model, normalize, search FAISS index, return top-k (default 8) chunks with scores and source metadata.
6. **`explainer.py`** — Build a system prompt instructing the model to answer from context only. Inject retrieved chunks with file/line references. Call GPT-4o-mini.

## Phase 3 — CLI *(parallel with Phase 2)*
7. **`cli.py`** — Two commands using `click`:
   - `ingest <github_url>` → runs ingestion, prints `repo_id` and chunk count
   - `ask <repo_id> "<question>"` → runs retrieval + LLM, prints answer + source files

## Phase 4 — FastAPI Backend *(depends on Phases 1–2)*
8. **`main.py`** — Three endpoints:
   - `POST /ingest { github_url }` → returns `{ repo_id, chunk_count }`
   - `POST /query { repo_id, question }` → returns `{ answer, sources: [{file, lines, snippet}] }`
   - `GET /repos` → list all indexed repos from `storage/`
9. Add CORS middleware (pre-wired for future React frontend).

---

## Key Libraries (`requirements.txt`)
`openai`, `faiss-cpu`, `langchain-text-splitters`, `gitpython`, `fastapi`, `uvicorn`, `tiktoken`, `tenacity`, `numpy`, `python-dotenv`, `click`

---

## Verification
1. Run `python cli.py ingest https://github.com/some/small-repo` → confirm non-zero chunk count and files appear in `storage/`
2. Run `python cli.py ask <repo_id> "What does this repo do?"` → confirm coherent answer with source file references
3. Start FastAPI (`uvicorn backend.main:app`) and test `/ingest` + `/query` via the auto-generated `/docs` UI
4. Edge cases: empty repo, binary-only files, very large single file (chunking truncation), invalid GitHub URL

---

## Decisions
- **LangChain used only for text-splitting** — keeps the codebase lean and explicit, no LangChain abstractions around the rest of the pipeline
- **FAISS local** — ideal for MVP; swap to Qdrant/Pinecone when multi-user or hosted deployment is needed
- **CLI first** — the core pipeline is fully testable without spinning up a server
- **Excluded from MVP**: auth, persistent DB, dependency graphs, knowledge graphs, semantic code understanding (future roadmap)
