import asyncio
import sys
sys.path.insert(0, 'D:\\GeniusQA\\backend')

async def check():
    from app.database import async_session
    from app.api.v1.Ntesterc_module.Ntesterc_project.model import ProjectMCPConfigModel
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(select(ProjectMCPConfigModel))
        configs = result.scalars().all()
        for config in configs:
            print(f"--- Config: {config.name} (id={config.id}) ---")
            print(f"  transport: {config.transport}")
            print(f"  command: {config.command}")
            print(f"  args: {config.args}")
            print(f"  env: {config.env}")
            print(f"  url: {config.url}")
            print(f"  scope: {config.scope}")
            print(f"  project_id: {config.project_id}")
            print(f"  user_id: {config.user_id}")
            print(f"  is_enabled: {config.is_enabled}")
        if not configs:
            print("No MCP configs found in database")

asyncio.run(check())
