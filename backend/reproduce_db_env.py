"""Test with the exact env from DB to reproduce the failure."""
import asyncio
import sys
sys.path.insert(0, "D:\\GeniusQA\\backend")

async def main():
    from langchain_mcp_adapters.client import MultiServerMCPClient

    # Exact env from DB
    server_config = {
        "Selenium": {
            "transport": "stdio",
            "command": "D:\\GeniusQA\\backend\\.venv\\Scripts\\python.exe",
            "args": ["-m", "selenium_mcp_server"],
            "env": {"PYTHONUNBUFFERED": "1"},  # <-- exact DB value
        }
    }

    try:
        client = MultiServerMCPClient(server_config)
        async with client.session("Selenium") as session:
            tools_resp = await session.list_tools()
            remote_tools = tools_resp.tools if hasattr(tools_resp, "tools") else []
            print(f"SUCCESS: {len(remote_tools)} tools")
    except BaseExceptionGroup as eg:
        for i, exc in enumerate(eg.exceptions):
            print(f"  [{i}] {type(exc).__name__}: {exc}")
            if hasattr(exc, 'exceptions'):
                for j, sub in enumerate(exc.exceptions):
                    print(f"    [{i}.{j}] {type(sub).__name__}: {sub}")
                    if hasattr(sub, '__cause__') and sub.__cause__:
                        print(f"           caused by: {type(sub.__cause__).__name__}: {sub.__cause__}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")

asyncio.run(main())
