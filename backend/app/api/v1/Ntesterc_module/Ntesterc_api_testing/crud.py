#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.core.base_crud import BaseCRUD
from .model import (
    APIProjectModel,
    APICollectionModel,
    APIRequestModel,
    APIEnvironmentModel,
    APITestSuiteModel,
    APITestSuiteRequestModel,
    APIRequestHistoryModel,
    APISSLCertificateModel,
    APIPublicScriptModel,
    APIDatabaseConfigModel
)


class APIProjectCRUD(BaseCRUD[APIProjectModel]):
    """API项目CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(APIProjectModel, db)
    
    async def get_by_project_id(
        self,
        db: AsyncSession,
        project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[APIProjectModel], int]:
        """根据项目ID获取API项目列表"""
        # 查询总数
        count_query = select(func.count(self.model.id)).where(
            and_(
                self.model.project_id == project_id,
                self.model.enabled_flag == 1
            )
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询数据
        query = select(self.model).where(
            and_(
                self.model.project_id == project_id,
                self.model.enabled_flag == 1
            )
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return list(items), total


class APICollectionCRUD(BaseCRUD[APICollectionModel]):
    """API集合CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(APICollectionModel, db)
    
    async def get_by_api_project_id(
        self,
        db: AsyncSession,
        api_project_id: int
    ) -> List[APICollectionModel]:
        """根据API项目ID获取集合列表（树形结构）"""
        query = select(self.model).where(
            and_(
                self.model.api_project_id == api_project_id,
                self.model.enabled_flag == 1
            )
        ).order_by(self.model.order_num, self.model.id)
        
        result = await db.execute(query)
        return list(result.scalars().all())


class APIRequestCRUD(BaseCRUD[APIRequestModel]):
    """API请求CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(APIRequestModel, db)
    
    async def get_by_collection_id(
        self,
        db: AsyncSession,
        collection_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[APIRequestModel], int]:
        """根据集合ID获取请求列表"""
        # 查询总数
        count_query = select(func.count(self.model.id)).where(
            and_(
                self.model.collection_id == collection_id,
                self.model.enabled_flag == 1
            )
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询数据
        query = select(self.model).where(
            and_(
                self.model.collection_id == collection_id,
                self.model.enabled_flag == 1
            )
        ).order_by(self.model.order_num, self.model.id).offset(skip).limit(limit)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_by_api_project_id(
        self,
        db: AsyncSession,
        api_project_id: int
    ) -> List[APIRequestModel]:
        """根据API项目ID获取所有请求"""
        # 需要通过collection关联查询
        from .model import APICollectionModel
        
        query = select(self.model).join(
            APICollectionModel,
            self.model.collection_id == APICollectionModel.id
        ).where(
            and_(
                APICollectionModel.api_project_id == api_project_id,
                self.model.enabled_flag == 1,
                APICollectionModel.enabled_flag == 1
            )
        ).order_by(self.model.collection_id, self.model.order_num, self.model.id)
        
        result = await db.execute(query)
        return list(result.scalars().all())


class APIEnvironmentCRUD(BaseCRUD[APIEnvironmentModel]):
    """API环境变量CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(APIEnvironmentModel, db)
    
    async def get_by_project_id(
        self,
        db: AsyncSession,
        project_id: int
    ) -> List[APIEnvironmentModel]:
        """根据项目ID获取环境变量列表"""
        query = select(self.model).where(
            and_(
                self.model.project_id == project_id,
                self.model.enabled_flag == 1
            )
        )
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_active_environment(
        self,
        db: AsyncSession,
        project_id: int
    ) -> Optional[APIEnvironmentModel]:
        """获取激活的环境"""
        query = select(self.model).where(
            and_(
                self.model.project_id == project_id,
                self.model.is_active == True,
                self.model.enabled_flag == 1
            )
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()


class APITestSuiteCRUD(BaseCRUD[APITestSuiteModel]):
    """API测试套件CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(APITestSuiteModel, db)
    
    async def get_by_api_project_id(
        self,
        db: AsyncSession,
        api_project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[APITestSuiteModel], int]:
        """根据API项目ID获取测试套件列表"""
        # 查询总数
        count_query = select(func.count(self.model.id)).where(
            and_(
                self.model.api_project_id == api_project_id,
                self.model.enabled_flag == 1
            )
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询数据
        query = select(self.model).where(
            and_(
                self.model.api_project_id == api_project_id,
                self.model.enabled_flag == 1
            )
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return list(items), total


class APITestSuiteRequestCRUD(BaseCRUD[APITestSuiteRequestModel]):
    """套件请求关联CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(APITestSuiteRequestModel, db)
    
    async def get_by_suite_id(
        self,
        db: AsyncSession,
        test_suite_id: int
    ) -> List[APITestSuiteRequestModel]:
        """根据套件ID获取关联的请求"""
        query = select(self.model).where(
            and_(
                self.model.test_suite_id == test_suite_id,
                self.model.enabled_flag == 1
            )
        ).order_by(self.model.order_num)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def delete_by_suite_id(
        self,
        db: AsyncSession,
        test_suite_id: int,
        user_id: int
    ):
        """删除套件的所有请求关联"""
        query = select(self.model).where(
            self.model.test_suite_id == test_suite_id
        )
        result = await db.execute(query)
        items = result.scalars().all()
        
        for item in items:
            item.enabled_flag = 0
            item.updated_by = user_id
        
        await db.commit()


class APIRequestHistoryCRUD:
    """API请求历史CRUD"""
    
    async def get_by_request_id(
        self,
        db: AsyncSession,
        request_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[APIRequestHistoryModel], int]:
        """根据请求ID获取历史记录"""
        from .model import APIRequestHistoryModel
        
        # 查询总数
        count_query = select(func.count(APIRequestHistoryModel.id)).where(
            APIRequestHistoryModel.request_id == request_id
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询数据
        query = select(APIRequestHistoryModel).where(
            APIRequestHistoryModel.request_id == request_id
        ).order_by(APIRequestHistoryModel.executed_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_by_id(
        self,
        db: AsyncSession,
        history_id: int
    ) -> Optional[APIRequestHistoryModel]:
        """根据ID获取历史记录"""
        from .model import APIRequestHistoryModel
        
        query = select(APIRequestHistoryModel).where(
            APIRequestHistoryModel.id == history_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


# CRUD实例将在Service层创建，不在这里预先实例化



class SSLCertificateCRUD(BaseCRUD):
    """SSL证书CRUD"""
    
    def __init__(self, db: AsyncSession):
        from .model import APISSLCertificateModel
        super().__init__(APISSLCertificateModel, db)
    
    async def get_by_project_id(
        self,
        db: AsyncSession,
        project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list, int]:
        """获取项目的所有证书"""
        from .model import APISSLCertificateModel
        conditions = [APISSLCertificateModel.project_id == project_id]
        return await self.get_list_crud(
            conditions=conditions,
            skip=skip,
            limit=limit
        )
    
    async def get_by_domain(
        self,
        db: AsyncSession,
        domain: str,
        project_id: int
    ) -> list:
        """
        根据域名匹配证书（支持通配符）
        匹配优先级：精确匹配 > 通配符匹配 > 全局匹配
        """
        from .model import APISSLCertificateModel
        from sqlalchemy import select, or_
        
        # 提取主域名用于通配符匹配
        domain_parts = domain.split('.')
        
        # 构建查询条件
        conditions = [
            APISSLCertificateModel.project_id == project_id,
            APISSLCertificateModel.is_active == True,
            or_(
                # 精确匹配
                APISSLCertificateModel.domain == domain,
                # 通配符匹配
                APISSLCertificateModel.domain == f'*.{".".join(domain_parts[-2:])}' if len(domain_parts) >= 2 else None,
                # 全局匹配
                APISSLCertificateModel.domain == '*',
                # 空域名（匹配所有）
                APISSLCertificateModel.domain.is_(None)
            )
        ]
        
        stmt = select(APISSLCertificateModel).where(*conditions)
        result = await db.execute(stmt)
        certificates = result.scalars().all()
        
        # 按优先级排序
        def get_priority(cert):
            if cert.domain == domain:
                return 0  # 精确匹配最高优先级
            elif cert.domain and cert.domain.startswith('*.'):
                return 1  # 通配符匹配次之
            elif cert.domain == '*':
                return 2  # 全局匹配再次
            else:
                return 3  # 空域名最低
        
        return sorted(certificates, key=get_priority)
    
    async def toggle_active(
        self,
        db: AsyncSession,
        cert_id: int
    ) -> bool:
        """切换证书启用状态"""
        from .model import APISSLCertificateModel
        cert = await self.get_by_id_crud(cert_id)
        if cert:
            cert.is_active = not cert.is_active
            await db.commit()
            await db.refresh(cert)
            return cert.is_active
        return False



class PublicScriptCRUD(BaseCRUD[APIPublicScriptModel]):
    """公共脚本CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(APIPublicScriptModel, db)
    
    async def get_by_project(
        self,
        db: AsyncSession,
        project_id: int,
        page: int = 1,
        page_size: int = 20
    ):
        """根据项目ID获取公共脚本列表"""
        query = select(self.model).where(
            self.model.project_id == project_id,
            self.model.enabled_flag == 1
        ).order_by(self.model.creation_date.desc())
        
        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        # 获取总数
        count_query = select(func.count(self.model.id)).where(
            self.model.project_id == project_id,
            self.model.enabled_flag == 1
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        return {'items': items, 'total': total}


class DatabaseConfigCRUD(BaseCRUD[APIDatabaseConfigModel]):
    """数据库配置CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(APIDatabaseConfigModel, db)
    
    async def get_by_project(
        self,
        db: AsyncSession,
        project_id: int,
        page: int = 1,
        page_size: int = 20
    ):
        """根据项目ID获取数据库配置列表"""
        query = select(self.model).where(
            self.model.project_id == project_id,
            self.model.enabled_flag == 1
        ).order_by(self.model.creation_date.desc())
        
        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        # 获取总数
        count_query = select(func.count(self.model.id)).where(
            self.model.project_id == project_id,
            self.model.enabled_flag == 1
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        return {'items': items, 'total': total}
