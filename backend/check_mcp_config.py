"""Check the actual MCP config stored in DB vs what _build_server_config produces."""
import asyncio
import sys
sys.path.insert(0, "D:\\GeniusQA\\backend")

async def main():
    from sqlalchemy import select
    from app.database import async_session
    from app.api.v1.Ntesterc_module.Ntesterc_project.model import ProjectMCPConfigModel

    async with async_session() as session:
        result = await session.execute(
            select(ProjectMCPConfigModel).where(ProjectMCPConfigModel.name == "Selenium")
        )
        c = result.scalar_one_or_none()
        if not c:
            print("ERROR: No Selenium config found in DB")
            return

        print("=== Raw DB record ===")
        print(f"  id={c.id}, name={c.name}")
        print(f"  transport={c.transport!r}")
        print(f"  command={c.command!r}")
        print(f"  args={c.args!r}")
        print(f"  env={c.env!r}")
        print(f"  url={c.url!r}")
        print(f"  scope={c.scope!r}")
        print(f"  project_id={c.project_id}")
        print(f"  user_id={c.user_id}")
        print(f"  is_enabled={c.is_enabled}")
        print(f"  headers={getattr(c, 'headers', 'N/A')!r}")
        print(f"  auth_type={getattr(c, 'auth_type', 'N/A')!r}")
        print(f"  auth_config={getattr(c, 'auth_config', 'N/A')!r}")

        # Simulate _build_server_config
        from app.api.v1.Ntesterc_module.Ntesterc_project.project_platform_service import _build_server_config
        cfg, name = _build_server_config(c, workspace_path=None)
        print(f"\n=== _build_server_config result ===")
        print(f"  server_name={name!r}")
        print(f"  server_config={cfg!r}")

        # Now test with MultiServerMCPClient
        print(f"\n=== Testing MultiServerMCPClient ===")
        from langchain_mcp_adapters.client import MultiServerMCPClient
        try:
            client = MultiServerMCPClient(cfg)
            async with client.session(name) as session:
                tools_resp = await session.list_tools()
                remote_tools = tools_resp.tools if hasattr(tools_resp, "tools") else []
                print(f"  SUCCESS: {len(remote_tools)} tools found")
                for t in remote_tools:
                    print(f"    - {t.name}")
        except ExceptionGroup as eg:
            print(f"  ExceptionGroup: {eg}")
            for i, exc in enumerate(eg.exceptions):
                print(f"    [{i}] {type(exc).__name__}: {exc}")
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")

asyncio.run(main())
