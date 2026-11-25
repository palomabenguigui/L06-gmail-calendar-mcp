"""Google Calendar operations: list events, find free slots, create event. No deletes."""
from datetime import date as Date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from google_auth import TIMEZONE, service

TZ = ZoneInfo(TIMEZONE)
WORK_START = time(9, 0)
WORK_END = time(18, 0)


def _cal():
    return service("calendar", "v3")


def _parse(value: str) -> datetime:
    """Parse an ISO date-time; values without an offset are taken as Asia/Jerusalem."""
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    return dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt.astimezone(TZ)


def list_events(days_ahead: int = 7) -> list[dict]:
    days_ahead = max(1, min(int(days_ahead), 90))
    now = datetime.now(TZ)
    resp = _cal().events().list(
        calendarId="primary", timeMin=now.isoformat(),
        timeMax=(now + timedelta(days=days_ahead)).isoformat(),
        singleEvents=True, orderBy="startTime", timeZone=TIMEZONE, maxResults=250,
    ).execute()
    return [{
        "id": ev["id"],
        "title": ev.get("summary", "(no title)"),
        "start": ev["start"].get("dateTime", ev["start"].get("date")),
        "end": ev["end"].get("dateTime", ev["end"].get("date")),
        "location": ev.get("location", ""),
        "link": ev.get("htmlLink", ""),
    } for ev in resp.get("items", [])]


def find_free_slots(date: str, duration_minutes: int = 30) -> dict:
    day = Date.fromisoformat(date.strip())
    duration = timedelta(minutes=max(5, int(duration_minutes)))
    start = datetime.combine(day, WORK_START, TZ)
    end = datetime.combine(day, WORK_END, TZ)
    now = datetime.now(TZ)
    if end <= now:
        return {"date": date, "timezone": TIMEZONE, "free_slots": [], "note": "This day is in the past."}
    start = max(start, now.replace(second=0, microsecond=0))
    resp = _cal().freebusy().query(body={
        "timeMin": start.isoformat(), "timeMax": end.isoformat(),
        "timeZone": TIMEZONE, "items": [{"id": "primary"}],
    }).execute()
    busy = sorted(
        (_parse(b["start"]), _parse(b["end"]))
        for b in resp["calendars"]["primary"].get("busy", [])
    )
    slots, cursor = [], start
    for b_start, b_end in busy:
        if b_start - cursor >= duration:
            slots.append((cursor, b_start))
        cursor = max(cursor, b_end)
    if end - cursor >= duration:
        slots.append((cursor, end))
    return {
        "date": date,
        "timezone": TIMEZONE,
        "working_hours": f"{WORK_START:%H:%M}-{WORK_END:%H:%M}",
        "duration_minutes": int(duration.total_seconds() // 60),
        "free_slots": [{"start": s.isoformat(), "end": e.isoformat()} for s, e in slots],
    }


def create_event(title: str, start: str, end: str, description: str = "") -> dict:
    start_dt, end_dt = _parse(start), _parse(end)
    if end_dt <= start_dt:
        raise ValueError("end must be after start.")
    body = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": TIMEZONE},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": TIMEZONE},
    }
    ev = _cal().events().insert(calendarId="primary", body=body, sendUpdates="none").execute()
    return {
        "id": ev["id"],
        "title": ev.get("summary"),
        "start": ev["start"].get("dateTime"),
        "end": ev["end"].get("dateTime"),
        "link": ev.get("htmlLink", ""),
    }
