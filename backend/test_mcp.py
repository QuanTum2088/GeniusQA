import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test():
    server_params = StdioServerParameters(
        command='D:\\GeniusQA\\backend\\.venv\\Scripts\\python.exe',
        args=['-m', 'selenium_mcp_server'],
    )
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                result = await session.initialize()
                print('Server initialized:', result)
                tools = await session.list_tools()
                print('Tools:', tools)
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())
