"""Smoke test: start server.py over stdio, list its tools, call list_events(days_ahead=1).

Usage:  uv run test_server.py
"""
import asyncio
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).resolve().parent
PRIVATE_DIR = str(Path("~/my-private").expanduser().resolve())


async def main() -> None:
    params = StdioServerParameters(
        command="uv",
        args=["run", "--directory", str(HERE), "server.py"],
        env={**os.environ, "GOOGLE_PRIVATE_DIR": PRIVATE_DIR},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            print(f"Tools ({len(tools)}):")
            for tool in tools:
                print(f"  - {tool.name}: {(tool.description or '').splitlines()[0]}")

            print("\nlist_events(days_ahead=1):")
            result = await session.call_tool("list_events", {"days_ahead": 1})
            if result.isError:
                print("  ERROR:", " ".join(c.text for c in result.content if hasattr(c, "text")))
                raise SystemExit(1)
            events = (result.structuredContent or {}).get("result")
            if events is None:
                print("  " + "\n  ".join(c.text for c in result.content if hasattr(c, "text")))
            elif not events:
                print("  No events in the next 24 hours.")
            else:
                for ev in events:
                    print(f"  - {ev['start']} -> {ev['end']}  {ev['title']}")
    print("\nOK")


if __name__ == "__main__":
    asyncio.run(main())
