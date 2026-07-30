import asyncio
import sys
sys.path.insert(0, 'D:\\GeniusQA\\backend')

async def test():
    from langchain_mcp_adapters.client import MultiServerMCPClient
    
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
    
    try:
        client = MultiServerMCPClient(server_config)
        async with client.session("Selenium") as session:
            tools_resp = await session.list_tools()
            remote_tools = tools_resp.tools if hasattr(tools_resp, "tools") else []
            print(f"Tools found: {len(remote_tools)}")
            for t in remote_tools:
                print(f"  - {t.name}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
