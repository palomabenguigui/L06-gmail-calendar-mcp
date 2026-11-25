# PRD – gmail-calendar MCP server (L06)

## Goal
Redo the L05 task (save a Gmail draft and create a Google Calendar event) through an MCP server instead of a fixed script. An AI agent (Claude Code) calls the server's tools in response to free-language requests, without new code for each request.

## Users
- The project owner, using Claude Code on their own computer with their own Google account.
- The AI agent, which calls the tools on the owner's behalf.

## Tools (Python, FastMCP, uv, stdio; time zone Asia/Jerusalem)
| Tool | What it does |
|------|--------------|
| `search_emails(query, max_results)` | Search Gmail with Gmail search syntax; returns id, sender, subject, date, snippet (max 50) |
| `read_email(message_id)` | Read one message: headers, labels, plain-text body |
| `create_draft(to, subject, body)` | Save a plain-text draft; it is **not** sent |
| `list_events(days_ahead)` | List primary-calendar events from now to N days ahead |
| `find_free_slots(date, duration_minutes)` | Free windows on a date within 09:00–18:00 |
| `create_event(title, start, end, description)` | Create an event on the primary calendar; no invitations emailed |

## Out of scope
- **No sending email and no deleting** emails, drafts or events, although the Google APIs support them. The agent reads email content, which may contain hidden instructions (prompt injection); if the tool does not exist, the agent cannot act on them. The agent prepares, and a human sends or deletes.
- No other Google services, no other calendars, no invitations, no remote hosting.

## Security
- The OAuth client (`client_secret*.json`) and `token.json` live in `~/my-private`, outside the project, found through `GOOGLE_PRIVATE_DIR`. `token.json` is saved with permissions 600.
- `.gitignore` excludes `token.json`, `client_secret*.json`, `credentials.json`, `.env`, `.venv/`, `__pycache__/`.
- The server runs locally over stdio only: no network port. It never opens a browser (login is a separate one-time `login.py`) and logs only to stderr.

## Verification
- `test_server.py` starts the server over stdio, lists its 6 tools and calls `list_events` without the agent.
- `/mcp` in Claude Code shows gmail-calendar as connected with 6 tools.
- In Google: the "L06 test" draft appears in Gmail Drafts (not sent), and the "MCP works" and "Study group" events appear in Google Calendar.
- Asked to send the draft and delete the event, the agent refused: no such tool exists.

## Acceptance criteria
1. The server exposes exactly the six tools above, and none of them sends or deletes.
2. `uv run test_server.py` lists 6 tools and ends with `OK`.
3. A free-language request creates a draft that is visible in Gmail Drafts and not sent.
4. A free-language request creates an event at the correct Asia/Jerusalem time, and `find_free_slots` + `create_event` place an event in a free slot.
5. A request to send or delete is not carried out.
6. No secret file is in the repository.
