#!/usr/bin/env python3
import asyncio
import logging
import os
import sys

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

BASE_URL = os.environ.get("OPENCLAW_BASE_URL", "http://VOTRE_OPENCLAW:18790/v1")
API_KEY = os.environ.get("OPENCLAW_API_KEY", "")
MODEL = os.environ.get("OPENCLAW_MODEL", "openclaw/main")

logging.basicConfig(
    level=logging.INFO,
    format="[bridge] %(message)s",
    stream=sys.stderr
)

server = Server("openclaw-bridge")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="ask",
            description="Ask Alex a quick question",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string"}
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="delegate",
            description="Delegate a full task to Alex",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"}
                },
                "required": ["prompt"]
            }
        ),
    ]

async def _call(messages):
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": MODEL, "messages": messages},
        )
        return response.json()["choices"][0]["message"]["content"]

@server.call_tool()
async def call_tool(name, arguments):
    if name == "ask":
        messages = [{"role": "user", "content": arguments["question"]}]
    else:
        messages = [{"role": "user", "content": arguments["prompt"]}]

    reply = await _call(messages)
    return [TextContent(type="text", text=reply)]

async def main():
    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
