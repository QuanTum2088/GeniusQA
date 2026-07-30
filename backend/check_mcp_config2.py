import asyncio
import sys
sys.path.insert(0, 'D:\\GeniusQA\\backend')
from app.infra.db.sqlalchemy import async_session
from app.api.v1.Ntesterc_module.Ntesterc_project.model import ProjectMCPConfigModel
from sqlalchemy import select

async def main():
    async with async_session() as db:
        result = await db.execute(select(ProjectMCPConfigModel))
        configs = result.scalars().all()
        for c in configs:
            print(f'ID={c.id} name={c.name} transport={c.transport} command={c.command} args={c.args} url={c.url} env={c.env}')

asyncio.run(main())
