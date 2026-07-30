"""Find the actual IDs and reproduce the error."""
import asyncio
import sys
sys.path.insert(0, "D:\\GeniusQA\\backend")

async def main():
    from sqlalchemy import select
    from app.infra.db.sqlalchemy import async_session
    from app.api.v1.Ntesterc_module.Ntesterc_project.model import ProjectMCPConfigModel

    async with async_session() as db:
        result = await db.execute(select(ProjectMCPConfigModel))
        configs = result.scalars().all()
        if not configs:
            print("No MCP configs in DB!")
            return
        for c in configs:
            print(f"Config: id={c.id}, name={c.name}, project_id={c.project_id}, user_id={c.user_id}, transport={c.transport}")

        # Use the first config
        c = configs[0]
        print(f"\nUsing config id={c.id}, project_id={c.project_id}, user_id={c.user_id}")

        from app.api.v1.Ntesterc_module.Ntesterc_project.project_platform_service import mcp_list_tools
        try:
            result = await mcp_list_tools(
                project_id=c.project_id,
                user_id=c.user_id,
                config_id=c.id,
                db=db,
            )
            print("Result:", result)
        except Exception as e:
            print(f"UNCAUGHT: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(main())
