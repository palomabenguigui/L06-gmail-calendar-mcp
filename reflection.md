# L06 Reflection

## What did we ask the agent?
We asked Claude Code, in English, to build an MCP server named "gmail-calendar" in Python (FastMCP, uv, stdio). It reuses a Google OAuth client and token.json stored in a private folder outside the project (~/my-private). The server exposes six tools: search_emails, read_email, create_draft, list_events, find_free_slots and create_event. We then registered it in Claude Code and used it in free language: we asked what was in the calendar, created the L05 draft and event, and asked for a free hour for a "Study group".

## How did we check that the result is correct?
- We reviewed the table of tools and confirmed that none of them sends or deletes anything.
- test_server.py started the server, listed its six tools (tools/list) and called list_events (tools/call) without the agent.
- /mcp showed gmail-calendar as connected with 6 tools.
- For each request, the terminal showed a call to gmail-calendar, not new code.
- We checked the results in Google itself: the "L06 test" draft in Gmail Drafts (not sent), and the "MCP works" and "Study group" events in Google Calendar.
- Before the first commit, git status confirmed that no token.json, client_secret or .env file was included.

## Which tool did we leave out, and why?
We left out any tool that sends email (users.messages.send) or deletes emails or events, even though the Google APIs support them. The agent reads email content, and a message could contain hidden instructions (prompt injection). If the tool does not exist, the agent cannot act on them. When we asked it to send the draft and delete the event, it answered that it has no such tools. The agent prepares, and a human sends. We also disabled the claude.ai Gmail connector in Claude Code, because it can send email and would bypass this boundary.

## L05 vs L06: what changed?
In L05 the agent wrote a fixed program (main.py) that does one task in a fixed order. Any new request needs a new prompt and a new program. In L06 the agent built a server that offers tools, and the model chooses which tools to use for each free-language request. Example: "find a free hour and add an event" worked with find_free_slots and create_event, without new code. The secrets and the Google APIs stayed the same; what changed is who decides the steps (code vs. model). The safety boundary also changed: it is now the list of tools the server exposes. The cost is that the tool descriptions are sent to the model in every request (tokens), and we have less control over each step.
