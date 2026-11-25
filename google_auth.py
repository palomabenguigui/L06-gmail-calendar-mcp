"""Shared Google auth helpers. Secrets stay in $GOOGLE_PRIVATE_DIR; nothing here prints."""
import glob
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]
TIMEZONE = "Asia/Jerusalem"


def private_dir() -> Path:
    """Folder holding client_secret*.json and token.json, from GOOGLE_PRIVATE_DIR."""
    value = os.environ.get("GOOGLE_PRIVATE_DIR")
    if not value:
        raise RuntimeError("Set GOOGLE_PRIVATE_DIR to the folder with your Google OAuth files.")
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise RuntimeError("GOOGLE_PRIVATE_DIR does not point to an existing folder.")
    return path


def client_secret_file() -> Path:
    matches = sorted(glob.glob(str(private_dir() / "client_secret*.json")))
    if not matches:
        raise RuntimeError("No client_secret*.json found in GOOGLE_PRIVATE_DIR.")
    return Path(matches[0])


def token_file() -> Path:
    return private_dir() / "token.json"


def save_token(creds: Credentials) -> None:
    path = token_file()
    path.write_text(creds.to_json())
    os.chmod(path, 0o600)


def load_credentials() -> Credentials:
    """Load token.json and refresh it if needed. Never opens a browser."""
    path = token_file()
    if not path.exists():
        raise RuntimeError("token.json not found. Run login.py once first.")
    creds = Credentials.from_authorized_user_file(str(path), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_token(creds)
        else:
            raise RuntimeError("Google token is invalid. Run login.py again.")
    return creds


_services: dict = {}


def service(name: str, version: str):
    """Cached Gmail/Calendar API client."""
    key = (name, version)
    if key not in _services:
        _services[key] = build(name, version, credentials=load_credentials(), cache_discovery=False)
    return _services[key]
