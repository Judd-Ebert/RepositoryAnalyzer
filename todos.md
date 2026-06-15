# Todos.
- Create SQLite database with correct Schema. Should include repositories, user preferences, jobs, and anything else I'm missing.
- Need to update the job status based on what's going on in the backend in ingest.py. I have the comments where it needs to go now but need to figure out how to update them realtime - likely in the database?
- Need an endpoint that will access the database and get the status of the job at any time. Should be relatively simply once I have the DB setup.
- Make api key storage secure using OS-level storage
- Validate the chat api key? Need to decide when to do this.
- Further steps: create UI for frontend ingestion, give it functionality to request status updates every 1-2 second



Flow for Database:
App startup
Backend starts and initializes SQLite automatically.

- Frontend collects embedding/chat provider + model + keys.
- Backend stores preferences in SQLite.
- Backend stores raw keys in OS secure storage, and saves only credential references in SQLite.
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
- No raw key leakage in logs or error payloads.
- Ongoing schema evolution
- New table/column later: add migration step tied to schema version.
- Existing users upgrade automatically on next startup without manual DB setup.