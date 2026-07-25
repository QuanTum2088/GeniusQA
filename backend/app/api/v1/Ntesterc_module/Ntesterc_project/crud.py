#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.base_crud import BaseCRUD
from app.api.v1.Ntesterc_module.Ntesterc_project.model import ProjectModel, ProjectMemberModel, ProjectEnvironmentModel


class ProjectCRUD(BaseCRUD[ProjectModel]):
    """项目CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ProjectModel, db)
    
    async def get_by_name_crud(self, name: str) -> Optional[ProjectModel]:
        """根据项目名称获取项目"""
        stmt = select(self.model).where(self.model.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_projects_crud(
        self,
        user_id: int,
        conditions: list = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[ProjectModel], int]:
        """获取用户参与的项目列表"""
        # 查询用户参与的项目ID
        member_stmt = select(ProjectMemberModel.project_id).where(
            ProjectMemberModel.user_id == user_id
        )
        member_result = await self.db.execute(member_stmt)
        project_ids = [row[0] for row in member_result.fetchall()]
        
        if not project_ids:
            return [], 0
        
        # 构建查询条件
        query_conditions = [self.model.id.in_(project_ids)]
        if conditions:
            query_conditions.extend(conditions)
        
        # 查询总数
        count_stmt = select(func.count(self.model.id)).where(and_(*query_conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # 查询列表
        stmt = (
            select(self.model)
            .where(and_(*query_conditions))
            .options(selectinload(self.model.members), selectinload(self.model.environments))
            .order_by(self.model.creation_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_with_relations_crud(self, project_id: int) -> Optional[ProjectModel]:
        """获取项目（包含关联数据）"""
        stmt = (
            select(self.model)
            .where(self.model.id == project_id)
            .options(
                selectinload(self.model.members),
                selectinload(self.model.environments),
                selectinload(self.model.owner)  # 预加载项目负责人
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class ProjectMemberCRUD(BaseCRUD[ProjectMemberModel]):
    """项目成员CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ProjectMemberModel, db)
    
    async def get_by_project_user_crud(
        self,
        project_id: int,
        user_id: int
    ) -> Optional[ProjectMemberModel]:
        """根据项目ID和用户ID获取成员"""
        stmt = select(self.model).where(
            and_(
                self.model.project_id == project_id,
                self.model.user_id == user_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_project_members_crud(self, project_id: int) -> List[ProjectMemberModel]:
        """获取项目所有成员"""
        stmt = (
            select(self.model)
            .where(self.model.project_id == project_id)
            .options(selectinload(self.model.user))
            .order_by(self.model.creation_date.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def check_user_in_project_crud(self, project_id: int, user_id: int) -> bool:
        """检查用户是否在项目中"""
        member = await self.get_by_project_user_crud(project_id, user_id)
        return member is not None
    
    async def get_user_role_in_project_crud(
        self,
        project_id: int,
        user_id: int
    ) -> Optional[str]:
        """获取用户在项目中的角色"""
        member = await self.get_by_project_user_crud(project_id, user_id)
        return member.role if member else None
    
    async def get_by_id_with_user_crud(self, member_id: int) -> Optional[ProjectMemberModel]:
        """根据ID获取成员（包含用户信息）"""
        stmt = (
            select(self.model)
            .where(self.model.id == member_id)
            .options(selectinload(self.model.user))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class ProjectEnvironmentCRUD(BaseCRUD[ProjectEnvironmentModel]):
    """项目环境CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ProjectEnvironmentModel, db)
    
    async def get_by_project_name_crud(
        self,
        project_id: int,
        name: str
    ) -> Optional[ProjectEnvironmentModel]:
        """根据项目ID和环境名称获取环境"""
        stmt = select(self.model).where(
            and_(
                self.model.project_id == project_id,
                self.model.name == name
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_project_environments_crud(
        self,
        project_id: int
    ) -> List[ProjectEnvironmentModel]:
        """获取项目所有环境"""
        stmt = (
            select(self.model)
            .where(self.model.project_id == project_id)
            .order_by(self.model.is_default.desc(), self.model.creation_date.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def clear_default_environments_crud(self, project_id: int, exclude_id: Optional[int] = None) -> None:
        """清除项目的默认环境标记"""
        from sqlalchemy import update
        stmt = update(self.model).where(
            and_(
                self.model.project_id == project_id,
                self.model.is_default == True
            )
        )
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        stmt = stmt.values(is_default=False)
        await self.db.execute(stmt)
        await self.db.commit()
