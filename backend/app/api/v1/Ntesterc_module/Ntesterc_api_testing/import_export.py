#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
import json
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from .crud import (
    APIProjectCRUD,
    APICollectionCRUD,
    APIRequestCRUD,
    APIEnvironmentCRUD
)
from .format_converter import format_converter


class ImportExportService:
    """导入导出服务"""
    
    @staticmethod
    async def export_api_project(
        db: AsyncSession,
        api_project_id: int
    ) -> Dict[str, Any]:
        """导出API项目（包含集合和请求）"""
        # 创建CRUD实例
        api_project_crud = APIProjectCRUD(db)
        api_collection_crud = APICollectionCRUD(db)
        api_request_crud = APIRequestCRUD(db)
        
        # 获取API项目
        api_project = await api_project_crud.get_by_id_crud(api_project_id)
        if not api_project:
            raise ValueError("API项目不存在")
        
        # 导出项目基本信息
        export_data = {
            'version': '1.0',
            'type': 'api_project',
            'project': {
                'name': api_project.name,
                'description': api_project.description,
                'project_type': api_project.project_type,
                'base_url': api_project.base_url
            },
            'collections': [],
            'requests': []
        }
        
        # 获取所有集合
        collections = await api_collection_crud.get_by_api_project_id(
            db=db,
            api_project_id=api_project_id
        )
        
        # 构建集合映射
        collection_map = {}
        for collection in collections:
            collection_data = {
                'id': collection.id,
                'name': collection.name,
                'description': collection.description,
                'parent_id': collection.parent_id,
                'order_num': collection.order_num
            }
            collection_map[collection.id] = collection_data
            export_data['collections'].append(collection_data)
        
        # 获取所有请求
        for collection in collections:
            requests, _ = await api_request_crud.get_by_collection_id(
                db=db,
                collection_id=collection.id,
                skip=0,
                limit=10000
            )
            
            for request in requests:
                request_data = {
                    'collection_id': request.collection_id,
                    'name': request.name,
                    'description': request.description,
                    'request_type': request.request_type,
                    'method': request.method,
                    'url': request.url,
                    'headers': request.headers,
                    'params': request.params,
                    'body': request.body,
                    'auth': request.auth,
                    'pre_request_script': request.pre_request_script,
                    'post_request_script': request.post_request_script,
                    'assertions': request.assertions,
                    'order_num': request.order_num
                }
                export_data['requests'].append(request_data)
        
        return export_data
    
    @staticmethod
    async def import_api_project(
        db: AsyncSession,
        project_id: int,
        import_data: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """导入API项目，支持多种格式"""
        # 检测并转换格式
        format_type = format_converter.detect_format(import_data)
        print(f"[DEBUG] 检测到的格式: {format_type}")
        
        if format_type == 'unknown':
            raise ValueError("无法识别的导入格式，支持的格式：内部格式、OpenAPI/Swagger、Apifox、Postman")
        
        # 转换为内部格式
        if format_type != 'internal':
            print(f"[DEBUG] 正在转换 {format_type} 格式到内部格式...")
            import_data = format_converter.convert_to_internal(import_data, format_type)
            print(f"[DEBUG] 转换完成，集合数: {len(import_data.get('collections', []))}, 请求数: {len(import_data.get('requests', []))}")
        
        # 创建CRUD实例
        api_project_crud = APIProjectCRUD(db)
        api_collection_crud = APICollectionCRUD(db)
        api_request_crud = APIRequestCRUD(db)
        
        # 创建API项目
        project_data = import_data.get('project', {})
        project_data['project_id'] = project_id
        
        api_project = await api_project_crud.create_crud(data=project_data)
        
        # 导入集合（需要处理父子关系）
        collection_id_map = {}  
        collections_data = import_data.get('collections', [])
        
        # 先导入没有父级的集合
        root_collections = [c for c in collections_data if c.get('parent_id') is None]
        for collection_data in root_collections:
            old_id = collection_data.pop('id', None)
            collection_data['api_project_id'] = api_project.id
            collection_data['parent_id'] = None
            
            collection = await api_collection_crud.create_crud(data=collection_data)
            if old_id:
                collection_id_map[old_id] = collection.id
        
        # 再导入有父级的集合
        child_collections = [c for c in collections_data if c.get('parent_id') is not None]
        for collection_data in child_collections:
            old_id = collection_data.pop('id', None)
            old_parent_id = collection_data.get('parent_id')
            
            collection_data['api_project_id'] = api_project.id
            collection_data['parent_id'] = collection_id_map.get(old_parent_id)
            
            collection = await api_collection_crud.create_crud(data=collection_data)
            if old_id:
                collection_id_map[old_id] = collection.id
        
        # 导入请求
        requests_data = import_data.get('requests', [])
        imported_requests = 0
        
        for request_data in requests_data:
            old_collection_id = request_data.get('collection_id')
            new_collection_id = collection_id_map.get(old_collection_id)
            
            if new_collection_id:
                request_data['collection_id'] = new_collection_id
                
                await api_request_crud.create_crud(data=request_data)
                imported_requests += 1
        
        return {
            'api_project_id': api_project.id,
            'collections_count': len(collection_id_map),
            'requests_count': imported_requests,
            'format': format_type
        }
    
    @staticmethod
    async def export_collection(
        db: AsyncSession,
        collection_id: int
    ) -> Dict[str, Any]:
        """导出单个集合（包含请求）"""
        # 创建CRUD实例
        api_collection_crud = APICollectionCRUD(db)
        api_request_crud = APIRequestCRUD(db)
        
        # 获取集合
        collection = await api_collection_crud.get_by_id_crud(collection_id)
        if not collection:
            raise ValueError("集合不存在")
        
        # 导出集合信息
        export_data = {
            'version': '1.0',
            'type': 'collection',
            'collection': {
                'name': collection.name,
                'description': collection.description,
                'order_num': collection.order_num
            },
            'requests': []
        }
        
        # 获取集合下的所有请求
        requests, _ = await api_request_crud.get_by_collection_id(
            db=db,
            collection_id=collection_id,
            skip=0,
            limit=10000
        )
        
        for request in requests:
            request_data = {
                'name': request.name,
                'description': request.description,
                'request_type': request.request_type,
                'method': request.method,
                'url': request.url,
                'headers': request.headers,
                'params': request.params,
                'body': request.body,
                'auth': request.auth,
                'pre_request_script': request.pre_request_script,
                'post_request_script': request.post_request_script,
                'assertions': request.assertions,
                'order_num': request.order_num
            }
            export_data['requests'].append(request_data)
        
        return export_data
    
    @staticmethod
    async def import_collection(
        db: AsyncSession,
        api_project_id: int,
        import_data: Dict[str, Any],
        user_id: int,
        parent_id: int = None
    ) -> Dict[str, Any]:
        """导入集合"""
        if import_data.get('type') != 'collection':
            raise ValueError("不支持的导入格式")
        
        # 创建CRUD实例
        api_collection_crud = APICollectionCRUD(db)
        api_request_crud = APIRequestCRUD(db)
        
        # 创建集合
        collection_data = import_data.get('collection', {})
        collection_data['api_project_id'] = api_project_id
        collection_data['parent_id'] = parent_id
        
        collection = await api_collection_crud.create_crud(data=collection_data)
        
        # 导入请求
        requests_data = import_data.get('requests', [])
        imported_requests = 0
        
        for request_data in requests_data:
            request_data['collection_id'] = collection.id
            
            await api_request_crud.create_crud(data=request_data)
            imported_requests += 1
        
        return {
            'collection_id': collection.id,
            'requests_count': imported_requests
        }
    
    @staticmethod
    async def export_environments(
        db: AsyncSession,
        project_id: int
    ) -> Dict[str, Any]:
        """导出环境变量"""
        # 创建CRUD实例
        api_environment_crud = APIEnvironmentCRUD(db)
        
        # 获取所有环境变量
        environments = await api_environment_crud.get_by_project_id(
            db=db,
            project_id=project_id
        )
        
        export_data = {
            'version': '1.0',
            'type': 'environments',
            'environments': []
        }
        
        for env in environments:
            env_data = {
                'name': env.name,
                'scope': env.scope,
                'variables': env.variables,
                'is_active': env.is_active
            }
            export_data['environments'].append(env_data)
        
        return export_data
    
    @staticmethod
    async def import_environments(
        db: AsyncSession,
        project_id: int,
        import_data: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """导入环境变量"""
        if import_data.get('type') != 'environments':
            raise ValueError("不支持的导入格式")
        
        # 创建CRUD实例
        api_environment_crud = APIEnvironmentCRUD(db)
        
        environments_data = import_data.get('environments', [])
        imported_count = 0
        
        for env_data in environments_data:
            env_data['project_id'] = project_id
            
            await api_environment_crud.create_crud(data=env_data)
            imported_count += 1
        
        return {
            'imported_count': imported_count
        }


# 创建服务实例
import_export_service = ImportExportService()
