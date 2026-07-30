"""Simulate exactly what the MCP SDK does to spawn the subprocess."""
import asyncio
import os
import sys
sys.path.insert(0, "D:\\GeniusQA\\backend")

async def main():
    from mcp.client.stdio import get_default_environment, _create_platform_compatible_process, _get_executable_command

    command = "D:\\GeniusQA\\backend\\.venv\\Scripts\\python.exe"
    args = ["-m", "selenium_mcp_server"]
    server_env = {"PYTHONUNBUFFERED": "1"}  # exact DB value

    # MCP SDK merges: {**get_default_environment(), **server.env}
    final_env = {**get_default_environment(), **server_env}
    
    print("=== Final env for subprocess ===")
    for k, v in sorted(final_env.items()):
        if k == "PATH":
            print(f"  {k} = ...{v[-200:]}")
        else:
            print(f"  {k} = {v[:80]}")

    resolved_cmd = _get_executable_command(command)
    print(f"\nResolved command: {resolved_cmd}")
    print(f"Args: {args}")

    try:
        process = await _create_platform_compatible_process(
            command=resolved_cmd,
            args=args,
            env=final_env,
            errlog=sys.stderr,
            cwd=None,
        )
        print(f"\nProcess started, PID={process.pid}")
        
        # Wait briefly and check if it's still alive
        await asyncio.sleep(2)
        returncode = process.returncode
        if returncode is not None:
            print(f"Process exited with code {returncode}")
        else:
            print("Process still running")
        
        # Kill it
        process.kill()
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(main())
