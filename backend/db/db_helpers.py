import sqlite3
from typing import Optional

from backend.config.config import PERMANENT_USER_PREFERENCES_ID

DB_PATH = "backend/storage/app.db"

#!** Utils**!

def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def mark_repository_ingested(github_url: str, repo_id: str) -> None:
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE repositories
            SET repo_id = ?,
            last_ingested_at = CURRENT_TIMESTAMP
            WHERE github_url = ?
            """,
            (repo_id, github_url),
        )
        connection.commit()
    finally:
        connection.close()

def init_db():
    connection = sqlite3.connect(DB_PATH) #Finds/creates the file
    connection.row_factory = sqlite3.Row #Can access rows by their names instead of indicies
    cursor = connection.cursor() #Lets me run commands on db

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS repositories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        github_url TEXT NOT NULL UNIQUE,
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
        embedding_api_key_username TEXT NOT NULL,
        chat_api_key_username TEXT NOT NULL,
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
        error_code TEXT,
        error_message TEXT,
        repo_id TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        started_at TEXT,
        finished_at TEXT
        );"""
    )

    connection.commit()
    connection.close()

#!** Preferences Management **!

def set_preferences(embedding_provider: str, embedding_model: str, chat_provider: str, chat_model: str, embedding_api_key_username: str, chat_api_key_username: str) -> None:
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT OR REPLACE INTO preferences (id, embedding_provider, embedding_model, chat_provider, chat_model, embedding_api_key_username, chat_api_key_username) VALUES (?, ?, ?, ?, ?, ?, ?);
            """
            (PERMANENT_USER_PREFERENCES_ID, embedding_provider, embedding_model, chat_provider, chat_model, embedding_api_key_username, chat_api_key_username),
        )
        connection.commit()
    finally:
        connection.close()

#!** Repository Management **!

def upsert_repository(github_url: str) -> int:
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT OR IGNORE INTO repositories (github_url) VALUES (?);
            """,
            (github_url,),
        )
        cursor.execute(
            """
            SELECT id FROM repositories
            WHERE github_url = ?;
            """,
            (github_url,),
        )
        row = cursor.fetchone()
        connection.commit()
        return int(row["id"])
    finally:
        connection.close()


#!** Job Management **!


def create_job(job_id: str, github_url: str, status: str = "queued") -> None:
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO jobs (job_id, github_url, status) VALUES (?, ?, ?);
            """,
            (job_id, github_url, status),
        )
        connection.commit()
    finally:
        connection.close()

def update_job_status(job_id: str, stage: str, status: str, error_code: Optional[str] = None, error_message: Optional[str] = None) -> None:
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE jobs
            SET
                status = ?,
                stage = ?,
                error_code = COALESCE(?, error_code),
                error_message = COALESCE(?, error_message)
            WHERE job_id = ?
            """,
            (status, stage, error_code, error_message, job_id),
        )
        connection.commit()
    finally:
        connection.close()

def get_job_status(job_id: str) -> Optional[sqlite3.Row]:
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT * FROM jobs
            WHERE job_id = ?;
            """,
            (job_id,),
        )
        return cursor.fetchone()
    finally:
        connection.close()