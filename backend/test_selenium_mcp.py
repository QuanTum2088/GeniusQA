"""Test Selenium MCP server directly."""
import asyncio
import sys
sys.path.insert(0, 'D:\\GeniusQA\\backend')

from mcp import StdioServerParameters
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    server_config = {
        "selenium": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["-m", "selenium_mcp_server"],
            "env": {"PYTHONUNBUFFERED": "1"},
        }
    }
    client = MultiServerMCPClient(server_config)
    try:
        async with client.session("selenium") as session:
            print("Session started successfully!")
            tools_resp = await session.list_tools()
            tools = tools_resp.tools if hasattr(tools_resp, "tools") else []
            print(f"Got {len(tools)} tools:")
            for t in tools:
                print(f"  - {t.name}: {t.description[:50] if t.description else ''}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")

asyncio.run(main())
