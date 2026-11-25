"""Gmail operations: search, read, create draft. Nothing here sends or deletes."""
import base64
from email.message import EmailMessage

from google_auth import service

MAX_BODY_CHARS = 20000


def _gmail():
    return service("gmail", "v1")


def _headers(payload: dict) -> dict:
    return {h["name"].lower(): h["value"] for h in payload.get("headers", [])}


def _decode(data: str) -> str:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", "replace")


def _find_body(part: dict, mime: str) -> str | None:
    if part.get("mimeType") == mime and part.get("body", {}).get("data"):
        return _decode(part["body"]["data"])
    for sub in part.get("parts", []) or []:
        found = _find_body(sub, mime)
        if found:
            return found
    return None


def search_emails(query: str, max_results: int = 10) -> list[dict]:
    max_results = max(1, min(int(max_results), 50))
    resp = _gmail().users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    results = []
    for ref in resp.get("messages", []):
        msg = _gmail().users().messages().get(
            userId="me", id=ref["id"], format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"],
        ).execute()
        h = _headers(msg.get("payload", {}))
        results.append({
            "id": msg["id"],
            "thread_id": msg.get("threadId"),
            "from": h.get("from", ""),
            "subject": h.get("subject", ""),
            "date": h.get("date", ""),
            "snippet": msg.get("snippet", ""),
        })
    return results


def read_email(message_id: str) -> dict:
    msg = _gmail().users().messages().get(userId="me", id=message_id, format="full").execute()
    payload = msg.get("payload", {})
    h = _headers(payload)
    body = _find_body(payload, "text/plain") or _find_body(payload, "text/html") or msg.get("snippet", "")
    truncated = len(body) > MAX_BODY_CHARS
    return {
        "id": msg["id"],
        "thread_id": msg.get("threadId"),
        "from": h.get("from", ""),
        "to": h.get("to", ""),
        "cc": h.get("cc", ""),
        "subject": h.get("subject", ""),
        "date": h.get("date", ""),
        "labels": msg.get("labelIds", []),
        "body": body[:MAX_BODY_CHARS],
        "body_truncated": truncated,
    }


def create_draft(to: str, subject: str, body: str) -> dict:
    message = EmailMessage()
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft = _gmail().users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return {
        "draft_id": draft["id"],
        "message_id": draft.get("message", {}).get("id"),
        "status": "Draft saved. It has NOT been sent.",
    }
