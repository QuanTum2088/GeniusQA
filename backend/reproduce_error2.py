"""Directly test the MCP connection from within the running backend's environment,
bypassing auth/member checks."""
import asyncio
import sys
sys.path.insert(0, "D:\\GeniusQA\\backend")

async def main():
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from app.api.v1.Ntesterc_module.Ntesterc_project.project_platform_service import _build_server_config, _get_mcp_config
    from app.infra.db.sqlalchemy import async_session
    from sqlalchemy import select
    from app.api.v1.Ntesterc_module.Ntesterc_project.model import ProjectMCPConfigModel

    async with async_session() as db:
        # Get the Selenium config directly
        c = (await db.execute(
            select(ProjectMCPConfigModel).where(ProjectMCPConfigModel.id == 9)
        )).scalar_one_or_none()
        if not c:
            print("Selenium config not found")
            return

        print(f"Config: id={c.id}, name={c.name}, transport={c.transport}")
        print(f"  command={c.command!r}")
        print(f"  args={c.args!r}")
        print(f"  env type={type(c.env)}, keys={list(c.env.keys()) if isinstance(c.env, dict) else 'N/A'}")
        print(f"  scope={c.scope!r}")

        # Build server config
        server_config, server_name = _build_server_config(c, workspace_path=None)
        print(f"\nserver_config: {server_config}")
        print(f"server_name: {server_name}")

        # Try connecting with detailed error handling
        print(f"\n--- Connecting with MultiServerMCPClient ---")
        try:
            client = MultiServerMCPClient(server_config)
            async with client.session(server_name) as session:
                tools_resp = await session.list_tools()
                remote_tools = tools_resp.tools if hasattr(tools_resp, "tools") else []
                print(f"SUCCESS: {len(remote_tools)} tools")
                for t in remote_tools:
                    print(f"  - {t.name}")
        except BaseExceptionGroup as eg:
            print(f"ExceptionGroup with {len(eg.exceptions)} sub-exceptions:")
            for i, exc in enumerate(eg.exceptions):
                print(f"  [{i}] {type(exc).__name__}: {exc}")
                if hasattr(exc, '__cause__') and exc.__cause__:
                    print(f"       caused by: {type(exc.__cause__).__name__}: {exc.__cause__}")
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(main())
