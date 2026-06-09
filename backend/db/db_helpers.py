import sqlite3


def init_db():
    connection = sqlite3.connect("backend/storage/app.db") #Finds/creates the file
    connection.row_factory = sqlite3.Row #Can access rows by their names instead of indicies
    cursor = connection.cursor() #Lets me run commands on db

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS repositories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        github_url TEXT NOT NULL UNIQUE,
        repo_hash TEXT,
        repo_id TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_ingested_at TEXT
        );"""
    )
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        embedding_provider TEXT NOT NULL,
        embedding_model TEXT NOT NULL,
        chat_provider TEXT NOT NULL,
        chat_model TEXT NOT NULL,
        embedding_credential_ref TEXT,
        chat_credential_ref TEXT,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );"""
    )
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT NOT NULL UNIQUE,
        github_url TEXT NOT NULL,
        status TEXT NOT NULL,
        stage TEXT,
        progress INTEGER DEFAULT 0,
        error_code TEXT,
        error_message TEXT,
        repo_id TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        started_at TEXT,
        finished_at TEXT
        );"""
    )

#def migrate_db():
