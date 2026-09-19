"""The fallback CLI uses the same authenticated MCP endpoint as Codex."""
import json
from pathlib import Path
import httpx

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def call(home: Path, tool: str, arguments: dict):
    config = json.loads((home / "server.json").read_text())
    async with httpx.AsyncClient(headers={"Authorization": "Bearer " + config["token"]},
                                 timeout=60, trust_env=False) as http:
        async with streamable_http_client(f'http://127.0.0.1:{config["port"]}/mcp', http_client=http) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                if tool == "tools/list":
                    return {"tools": [t.model_dump(mode="json") for t in (await session.list_tools()).tools]}
                result = await session.call_tool(tool, arguments)
                if result.isError:
                    raise ValueError("; ".join(c.text for c in result.content if hasattr(c, "text")))
                if result.structuredContent is not None:
                    return result.structuredContent
                return json.loads(next(c.text for c in result.content if hasattr(c, "text")))
