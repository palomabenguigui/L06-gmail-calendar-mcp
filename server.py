"""gmail-calendar MCP server (stdio). Never prints to stdout and never opens a browser.

There is intentionally NO tool that sends or deletes anything.
"""
import logging
import sys

from mcp.server.fastmcp import FastMCP

import calendar_tools
import gmail_tools

# stdout is the MCP protocol channel: all logging goes to stderr.
logging.basicConfig(stream=sys.stderr, level=logging.WARNING)

mcp = FastMCP("gmail-calendar")


@mcp.tool()
def search_emails(query: str, max_results: int = 10) -> list[dict]:
    """Search Gmail using Gmail search syntax (e.g. 'from:bob is:unread newer_than:7d').
    Returns id, sender, subject, date and snippet for up to max_results messages (max 50)."""
    return gmail_tools.search_emails(query, max_results)


@mcp.tool()
def read_email(message_id: str) -> dict:
    """Read one Gmail message by id: headers (from, to, cc, subject, date), labels and plain-text body."""
    return gmail_tools.read_email(message_id)


@mcp.tool()
def create_draft(to: str, subject: str, body: str) -> dict:
    """Save a new Gmail DRAFT (plain text). The draft is NOT sent; the user reviews and sends it in Gmail."""
    return gmail_tools.create_draft(to, subject, body)


@mcp.tool()
def list_events(days_ahead: int = 7) -> list[dict]:
    """List events on the primary Google Calendar from now until days_ahead days from now (Asia/Jerusalem time)."""
    return calendar_tools.list_events(days_ahead)


@mcp.tool()
def find_free_slots(date: str, duration_minutes: int = 30) -> dict:
    """Find free time windows of at least duration_minutes on a date (YYYY-MM-DD),
    within working hours 09:00-18:00 Asia/Jerusalem, based on the primary calendar."""
    return calendar_tools.find_free_slots(date, duration_minutes)


@mcp.tool()
def create_event(title: str, start: str, end: str, description: str = "") -> dict:
    """Create an event on the primary calendar. start/end are ISO date-times like '2026-12-01T10:00';
    without an offset they are taken as Asia/Jerusalem time. No invitations are emailed."""
    return calendar_tools.create_event(title, start, end, description)


if __name__ == "__main__":
    mcp.run(transport="stdio")
