# Todos.
- Need to update the job status based on what's going on in the backend in ingest.py. I have the comments where it needs to go now but need to figure out how to update them realtime - likely in the database?
- Need an endpoint that will access the database and get the status of the job at any time. Should be relatively simply once I have the DB setup.
- Make api key storage secure using OS-level storage
    I think i remember doing this?
- Validate the chat api key
- Further steps: create UI for frontend ingestion, give it functionality to request status updates every 1-2 second

- Support local ai models as far as frontend entering goes, should be fine honestly on teh backend as long as it's openai formatted
    - Need to probably query for Ollama in the backend
        - Will have a toggle for "Using Ollama?" and when that's switched on it can look for models in the backend
        - Toggle will make a call to FastAPI, which will call Ollama, which will then report back to FastAPI and back to the frontend
        
- Cleanup UI for landing page


!TODO! Need to have better filtration for chat vs. embedding models
!TODO! Need to allow for a user to use local for one but not the other model


Flow for Database:
App startup
Backend starts and initializes SQLite automatically.

- Frontend collects embedding/chat provider + model + keys.
- User starts ingestion
- Frontend sends github_url + selected provider/model references.
- Frontend navigates to loading/progress UI with job_id.
- Frontend polling
- Frontend polls GET /jobs/{job_id} every 1 to 2 seconds.
- UI renders live progress from that response.
- Completion
- Frontend stops polling and moves to query screen.
- Failure handling
- Frontend stops polling and shows actionable error text.
- Ongoing schema evolution
- New table/column later: add migration step tied to schema version.
- Existing users upgrade automatically on next startup without manual DB setup.