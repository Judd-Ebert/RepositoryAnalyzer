import keyring

from keyring.errors import PasswordDeleteError

import sqlite3

from typing import Optional

from backend.config.config import KEYRING_SERVICE

from .db_helpers import get_connection


#!** API Key Management **!

def create_api_key(username: str, api_key: str) -> None:
    keyring.set_password(KEYRING_SERVICE, username, api_key)

def get_api_key(username: str,) -> Optional[str]:
    return keyring.get_password(KEYRING_SERVICE, username)

def delete_api_key(username: str) -> None:
    try:
        keyring.delete_password(KEYRING_SERVICE, username)
    except PasswordDeleteError:
        pass

def get_keyring_username(provider, model) -> str:
    return f"chat-{provider}-{model}"