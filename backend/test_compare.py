"""Compare: MultiServerMCPClient vs direct create_session."""
import asyncio
import sys
sys.path.insert(0, "D:\\GeniusQA\\backend")

async def main():
    from langchain_mcp_adapters.sessions import create_session
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext

    connection = {
        "transport": "stdio",
        "command": "D:\\GeniusQA\\backend\\.venv\\Scripts\\python.exe",
        "args": ["-m", "selenium_mcp_server"],
        "env": {"PYTHONUNBUFFERED": "1"},
    }

    # Test 1: Direct create_session (no callbacks)
    print("=== Test 1: Direct create_session ===")
    try:
        async with create_session(connection) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"  OK: {len(tools.tools)} tools")
    except BaseExceptionGroup as eg:
        print(f"  FAIL: ExceptionGroup")
        for i, exc in enumerate(eg.exceptions):
            print(f"    [{i}] {type(exc).__name__}: {exc}")

    # Test 2: create_session with callbacks (like MultiServerMCPClient)
    print("\n=== Test 2: create_session with callbacks ===")
    callbacks = Callbacks()
    ctx = CallbackContext(server_name="Selenium")
    mcp_callbacks = callbacks.to_mcp_format(context=ctx)
    try:
        async with create_session(connection, mcp_callbacks=mcp_callbacks) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"  OK: {len(tools.tools)} tools")
    except BaseExceptionGroup as eg:
        print(f"  FAIL: ExceptionGroup")
        for i, exc in enumerate(eg.exceptions):
            print(f"    [{i}] {type(exc).__name__}: {exc}")

    # Test 3: MultiServerMCPClient
    print("\n=== Test 3: MultiServerMCPClient ===")
    try:
        client = MultiServerMCPClient({"Selenium": connection})
        async with client.session("Selenium") as session:
            tools_resp = await session.list_tools()
            print(f"  OK: {len(tools_resp.tools)} tools")
    except BaseExceptionGroup as eg:
        print(f"  FAIL: ExceptionGroup")
        for i, exc in enumerate(eg.exceptions):
            print(f"    [{i}] {type(exc).__name__}: {exc}")

asyncio.run(main())
