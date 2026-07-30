"""Deep trace: go through the exact same code path as MultiServerMCPClient."""
import asyncio
import sys
import logging
logging.basicConfig(level=logging.DEBUG)
sys.path.insert(0, "D:\\GeniusQA\\backend")

async def main():
    from langchain_mcp_adapters.sessions import create_session
    from mcp import ClientSession

    connection = {
        "transport": "stdio",
        "command": "D:\\GeniusQA\\backend\\.venv\\Scripts\\python.exe",
        "args": ["-m", "selenium_mcp_server"],
        "env": {"PYTHONUNBUFFERED": "1"},
    }

    try:
        async with create_session(connection) as session:
            print(f"Session created, initializing...")
            await session.initialize()
            print("Initialized OK")
            tools_resp = await session.list_tools()
            print(f"Tools: {len(tools_resp.tools)}")
    except BaseExceptionGroup as eg:
        print(f"\nExceptionGroup ({len(eg.exceptions)} sub-exceptions):")
        for i, exc in enumerate(eg.exceptions):
            print(f"  [{i}] {type(exc).__name__}: {exc}")
            if hasattr(exc, 'exceptions'):
                for j, sub in enumerate(exc.exceptions):
                    print(f"    [{i}.{j}] {type(sub).__name__}: {sub}")
                    tb = getattr(sub, '__traceback__', None)
                    if tb:
                        import traceback
                        traceback.print_exception(type(sub), sub, tb)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(main())
