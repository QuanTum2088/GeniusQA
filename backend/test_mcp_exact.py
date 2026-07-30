"""Simulate the backend's mcp_list_tools function to reproduce the error."""
import asyncio
import sys
sys.path.insert(0, 'D:\\GeniusQA\\backend')

# Use the same pattern as the backend
async def test():
    from langchain_mcp_adapters.client import MultiServerMCPClient
    
    # Same config as _build_server_config produces
    server_config = {
        "Selenium": {
            "transport": "stdio",
            "command": "D:\\GeniusQA\\backend\\.venv\\Scripts\\python.exe",
            "args": ["-m", "selenium_mcp_server"],
            "env": {
                "PATH": "D:\\Chrome\\Application;C:\\WINDOWS\\System32;C:\\WINDOWS;C:\\Program Files (x86)\\Microsoft\\Edge\\Application",
                "SELENIUM_BROWSER": "chrome",
                "SELENIUM_CHROME_BINARY": "D:\\Chrome\\Application\\chrome.exe"
            }
        }
    }
    server_name = "Selenium"
    
    try:
        client = MultiServerMCPClient(server_config)
        async with client.session(server_name) as session:
            tools_resp = await session.list_tools()
            remote_tools = tools_resp.tools if hasattr(tools_resp, "tools") else []
        items = []
        for t in remote_tools or []:
            items.append(
                {
                    "name": getattr(t, "name", ""),
                    "description": getattr(t, "description", "") or "",
                    "input_schema": getattr(t, "inputSchema", {}) or {},
                }
            )
        print(f"OK: tools count = {len(items)}")
    except Exception as e:
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
