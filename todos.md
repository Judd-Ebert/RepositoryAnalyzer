# Todos.
- Create SQLite database with correct Schema. Should include repositories, user preferences, jobs, and anything else I'm missing.
- Need to update the job status based on what's going on in the backend in ingest.py. I have the comments where it needs to go now but need to figure out how to update them realtime - likely in the database?
- Need an endpoint that will access the database and get the status of the job at any time. Should be relatively simply once I have the DB setup.
- Make api key storage secure using OS-level storage
- Validate the chat api key? Need to decide when to do this.
- Further steps: create UI for frontend ingestion, give it functionality to request status updates every 1-2 second
