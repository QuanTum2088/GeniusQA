#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from .crud import (
    APIProjectCRUD,
    APICollectionCRUD,
    APIRequestCRUD,
    APIEnvironmentCRUD,
    APITestSuiteCRUD,
    APITestSuiteRequestCRUD,
    APIRequestHistoryCRUD,
    PublicScriptCRUD,
    DatabaseConfigCRUD
)
from .schema import (
    APIProjectCreateSchema,
    APIProjectUpdateSchema,
    APIProjectOutSchema,
    APICollectionCreateSchema,
    APICollectionUpdateSchema,
    APICollectionOutSchema,
    APIRequestCreateSchema,
    APIRequestUpdateSchema,
    APIRequestOutSchema,
    APIEnvironmentCreateSchema,
    APIEnvironmentUpdateSchema,
    APIEnvironmentOutSchema,
    APITestSuiteCreateSchema,
    APITestSuiteUpdateSchema,
    APITestSuiteOutSchema,
    APIRequestHistoryOutSchema
)
from .executor import request_executor


class APIProjectService:
    """API项目服务"""
    
    @staticmethod
    async def create_api_project(
        db: AsyncSession,
        data: APIProjectCreateSchema,
        user_id: int
    ) -> Dict[str, Any]:
        """创建API项目"""
        api_project_crud = APIProjectCRUD(db)
        # 创建API项目
        api_project = await api_project_crud.create_crud(data.model_dump())
        
        return APIProjectOutSchema.model_validate(api_project).model_dump()
    
    @staticmethod
    async def get_api_project_list(
        db: AsyncSession,
        project_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取API项目列表"""
        api_project_crud = APIProjectCRUD(db)
        skip = (page - 1) * page_size
        items, total = await api_project_crud.get_by_project_id(
            db=db,
            project_id=project_id,
            skip=skip,
            limit=page_size
        )
        
        return {
            "items": [APIProjectOutSchema.model_validate(item).model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def get_api_project(
        db: AsyncSession,
        api_project_id: int
    ) -> Dict[str, Any]:
        """获取API项目详情"""
        api_project_crud = APIProjectCRUD(db)
        api_project = await api_project_crud.get_by_id_crud(api_project_id)
        if not api_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API项目不存在"
            )
        
        return APIProjectOutSchema.model_validate(api_project).model_dump()
    
    @staticmethod
    async def update_api_project(
        db: AsyncSession,
        api_project_id: int,
        data: APIProjectUpdateSchema,
        user_id: int
    ) -> Dict[str, Any]:
        """更新API项目"""
        api_project_crud = APIProjectCRUD(db)
        api_project = await api_project_crud.get_by_id_crud(api_project_id)
        if not api_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API项目不存在"
            )
        
        # 更新API项目
        updated_project = await api_project_crud.update_crud(api_project.id, data.model_dump(exclude_unset=True))
        
        return APIProjectOutSchema.model_validate(updated_project).model_dump()
    
    @staticmethod
    async def delete_api_project(
        db: AsyncSession,
        api_project_id: int,
        user_id: int
    ):
        """删除API项目"""
        api_project_crud = APIProjectCRUD(db)
        api_project = await api_project_crud.get_by_id_crud(api_project_id)
        if not api_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API项目不存在"
            )
        
        await api_project_crud.delete_crud([api_project_id])


class APICollectionService:
    """API集合服务"""
    
    @staticmethod
    async def create_collection(
        db: AsyncSession,
        data: APICollectionCreateSchema,
        user_id: int
    ) -> Dict[str, Any]:
        """创建API集合"""
        api_collection_crud = APICollectionCRUD(db)
        collection = await api_collection_crud.create_crud(data.model_dump())
        
        return APICollectionOutSchema.model_validate(collection).model_dump()
    
    @staticmethod
    async def get_collection_tree(
        db: AsyncSession,
        api_project_id: int
    ) -> List[Dict[str, Any]]:
        """获取API集合树"""
        api_collection_crud = APICollectionCRUD(db)
        api_request_crud = APIRequestCRUD(db)
        
        # 获取所有集合
        collections = await api_collection_crud.get_by_api_project_id(
            db=db,
            api_project_id=api_project_id
        )
        
        # 获取所有请求
        requests = await api_request_crud.get_by_api_project_id(
            db=db,
            api_project_id=api_project_id
        )
        
        # 构建树形结构
        collection_dict = {}
        root_collections = []
        
        # 初始化集合字典
        for collection in collections:
            collection_data = APICollectionOutSchema.model_validate(collection).model_dump()
            collection_data['children'] = []
            collection_data['requests'] = []
            collection_dict[collection.id] = collection_data
        
        # 将请求添加到对应的集合
        for request in requests:
            request_data = APIRequestOutSchema.model_validate(request).model_dump()
            if request.collection_id and request.collection_id in collection_dict:
                collection_dict[request.collection_id]['requests'].append(request_data)
        
        # 构建集合树形结构
        for collection_data in collection_dict.values():
            if collection_data['parent_id'] is None:
                root_collections.append(collection_data)
            else:
                parent = collection_dict.get(collection_data['parent_id'])
                if parent:
                    parent['children'].append(collection_data)
        
        return root_collections
    
    @staticmethod
    async def update_collection(
        db: AsyncSession,
        collection_id: int,
        data: APICollectionUpdateSchema,
        user_id: int
    ) -> Dict[str, Any]:
        """更新API集合"""
        api_collection_crud = APICollectionCRUD(db)
        collection = await api_collection_crud.get_by_id_crud(collection_id)
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API集合不存在"
            )
        
        updated_collection = await api_collection_crud.update_crud(collection.id, data.model_dump(exclude_unset=True))
        
        return APICollectionOutSchema.model_validate(updated_collection).model_dump()
    
    @staticmethod
    async def delete_collection(
        db: AsyncSession,
        collection_id: int,
        user_id: int
    ):
        """删除API集合"""
        api_collection_crud = APICollectionCRUD(db)
        collection = await api_collection_crud.get_by_id_crud(collection_id)
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API集合不存在"
            )
        
        await api_collection_crud.delete_crud([collection_id])


class APIRequestService:
    """API请求服务"""
    
    @staticmethod
    async def create_request(
        db: AsyncSession,
        data: APIRequestCreateSchema,
        user_id: int
    ) -> Dict[str, Any]:
        """创建API请求"""
        api_request_crud = APIRequestCRUD(db)
        request = await api_request_crud.create_crud(data.model_dump())
        
        return APIRequestOutSchema.model_validate(request).model_dump()
    
    @staticmethod
    async def get_request_list(
        db: AsyncSession,
        collection_id: int,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """获取API请求列表"""
        api_request_crud = APIRequestCRUD(db)
        skip = (page - 1) * page_size
        items, total = await api_request_crud.get_by_collection_id(
            db=db,
            collection_id=collection_id,
            skip=skip,
            limit=page_size
        )
        
        return {
            "items": [APIRequestOutSchema.model_validate(item).model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def get_request(
        db: AsyncSession,
        request_id: int
    ) -> Dict[str, Any]:
        """获取API请求详情"""
        api_request_crud = APIRequestCRUD(db)
        request = await api_request_crud.get_by_id_crud(request_id)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API请求不存在"
            )
        
        return APIRequestOutSchema.model_validate(request).model_dump()
    
    @staticmethod
    async def update_request(
        db: AsyncSession,
        request_id: int,
        data: APIRequestUpdateSchema,
        user_id: int
    ) -> Dict[str, Any]:
        """更新API请求"""
        api_request_crud = APIRequestCRUD(db)
        request = await api_request_crud.get_by_id_crud(request_id)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API请求不存在"
            )
        
        updated_request = await api_request_crud.update_crud(request.id, data.model_dump(exclude_unset=True))
        
        return APIRequestOutSchema.model_validate(updated_request).model_dump()
    
    @staticmethod
    async def delete_request(
        db: AsyncSession,
        request_id: int,
        user_id: int
    ):
        """删除API请求"""
        api_request_crud = APIRequestCRUD(db)
        request = await api_request_crud.get_by_id_crud(request_id)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API请求不存在"
            )
        
        await api_request_crud.delete_crud([request_id])
    
    @staticmethod
    async def execute_request(
        db: AsyncSession,
        request_id: int,
        environment_id: Optional[int],
        user_id: int
    ) -> Dict[str, Any]:
        """执行API请求"""
        result = await request_executor.execute_request(
            db=db,
            request_id=request_id,
            environment_id=environment_id,
            user_id=user_id
        )
        return result


class APIEnvironmentService:
    """API环境变量服务"""
    
    @staticmethod
    async def create_environment(
        db: AsyncSession,
        data: APIEnvironmentCreateSchema,
        user_id: int
    ) -> Dict[str, Any]:
        """创建API环境变量"""
        api_environment_crud = APIEnvironmentCRUD(db)
        # 如果设置为激活，先取消其他环境的激活状态
        if data.is_active:
            active_env = await api_environment_crud.get_active_environment(
                db=db,
                project_id=data.project_id
            )
            if active_env:
                active_env.is_active = False
                active_env.updated_by = user_id
                await db.commit()
        
        # 创建环境变量
        environment = await api_environment_crud.create_crud(data.model_dump())
        
        return APIEnvironmentOutSchema.model_validate(environment).model_dump()
    
    @staticmethod
    async def get_environment_list(
        db: AsyncSession,
        project_id: int
    ) -> List[Dict[str, Any]]:
        """获取环境变量列表"""
        api_environment_crud = APIEnvironmentCRUD(db)
        environments = await api_environment_crud.get_by_project_id(
            db=db,
            project_id=project_id
        )
        
        return [APIEnvironmentOutSchema.model_validate(env).model_dump() for env in environments]
    
    @staticmethod
    async def get_environment(
        db: AsyncSession,
        environment_id: int
    ) -> Dict[str, Any]:
        """获取环境变量详情"""
        api_environment_crud = APIEnvironmentCRUD(db)
        environment = await api_environment_crud.get_by_id_crud(environment_id)
        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="环境变量不存在"
            )
        
        return APIEnvironmentOutSchema.model_validate(environment).model_dump()
    
    @staticmethod
    async def update_environment(
        db: AsyncSession,
        environment_id: int,
        data: APIEnvironmentUpdateSchema,
        user_id: int
    ) -> Dict[str, Any]:
        """更新环境变量"""
        api_environment_crud = APIEnvironmentCRUD(db)
        environment = await api_environment_crud.get_by_id_crud(environment_id)
        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="环境变量不存在"
            )
        
        # 如果设置为激活，先取消其他环境的激活状态
        if data.is_active:
            active_env = await api_environment_crud.get_active_environment(
                db=db,
                project_id=environment.project_id
            )
            if active_env and active_env.id != environment_id:
                active_env.is_active = False
                active_env.updated_by = user_id
                await db.commit()
        
        # 更新环境变量
        updated_environment = await api_environment_crud.update_crud(environment.id, data.model_dump(exclude_unset=True))
        
        return APIEnvironmentOutSchema.model_validate(updated_environment).model_dump()
    
    @staticmethod
    async def delete_environment(
        db: AsyncSession,
        environment_id: int,
        user_id: int
    ):
        """删除环境变量"""
        api_environment_crud = APIEnvironmentCRUD(db)
        environment = await api_environment_crud.get_by_id_crud(environment_id)
        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="环境变量不存在"
            )
        
        await api_environment_crud.delete_crud([environment_id])
    
    @staticmethod
    async def activate_environment(
        db: AsyncSession,
        environment_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """激活环境变量"""
        api_environment_crud = APIEnvironmentCRUD(db)
        environment = await api_environment_crud.get_by_id_crud(environment_id)
        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="环境变量不存在"
            )
        
        # 取消其他环境的激活状态
        active_env = await api_environment_crud.get_active_environment(
            db=db,
            project_id=environment.project_id
        )
        if active_env and active_env.id != environment_id:
            active_env.is_active = False
            active_env.updated_by = user_id
        
        # 激活当前环境
        environment.is_active = True
        environment.updated_by = user_id
        await db.commit()
        await db.refresh(environment)
        
        return APIEnvironmentOutSchema.model_validate(environment).model_dump()


class APITestSuiteService:
    """API测试套件服务"""
    
    @staticmethod
    async def create_test_suite(
        db: AsyncSession,
        data: APITestSuiteCreateSchema,
        user_id: int
    ) -> Dict[str, Any]:
        """创建API测试套件"""
        api_test_suite_crud = APITestSuiteCRUD(db)
        api_test_suite_request_crud = APITestSuiteRequestCRUD(db)
        # 创建测试套件
        request_ids = data.request_ids or []
        suite_data = data.model_dump(exclude={'request_ids'})
        
        test_suite = await api_test_suite_crud.create_crud(suite_data)
        
        # 关联请求
        for idx, request_id in enumerate(request_ids):
            suite_request_data = {
                'test_suite_id': test_suite.id,
                'request_id': request_id,
                'order_num': idx + 1
            }
            await api_test_suite_request_crud.create_crud(suite_request_data)
        
        result = APITestSuiteOutSchema.model_validate(test_suite).model_dump()
        result['request_count'] = len(request_ids)
        
        return result
    
    @staticmethod
    async def get_test_suite_list(
        db: AsyncSession,
        api_project_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取测试套件列表"""
        api_test_suite_crud = APITestSuiteCRUD(db)
        api_test_suite_request_crud = APITestSuiteRequestCRUD(db)
        skip = (page - 1) * page_size
        items, total = await api_test_suite_crud.get_by_api_project_id(
            db=db,
            api_project_id=api_project_id,
            skip=skip,
            limit=page_size
        )
        
        # 获取每个套件的请求数量
        result_items = []
        for item in items:
            suite_data = APITestSuiteOutSchema.model_validate(item).model_dump()
            # 获取关联的请求数量
            suite_requests = await api_test_suite_request_crud.get_by_suite_id(
                db=db,
                test_suite_id=item.id
            )
            suite_data['request_count'] = len(suite_requests)
            result_items.append(suite_data)
        
        return {
            "items": result_items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def get_test_suite(
        db: AsyncSession,
        test_suite_id: int
    ) -> Dict[str, Any]:
        """获取测试套件详情"""
        api_test_suite_crud = APITestSuiteCRUD(db)
        api_test_suite_request_crud = APITestSuiteRequestCRUD(db)
        api_request_crud = APIRequestCRUD(db)
        test_suite = await api_test_suite_crud.get_by_id_crud(test_suite_id)
        if not test_suite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="测试套件不存在"
            )
        
        # 获取关联的请求
        suite_requests = await api_test_suite_request_crud.get_by_suite_id(
            db=db,
            test_suite_id=test_suite_id
        )
        
        # 获取请求详情
        request_list = []
        for suite_request in suite_requests:
            request = await api_request_crud.get_by_id_crud(suite_request.request_id)
            if request:
                request_data = APIRequestOutSchema.model_validate(request).model_dump()
                request_data['order_num'] = suite_request.order_num
                request_list.append(request_data)
        
        result = APITestSuiteOutSchema.model_validate(test_suite).model_dump()
        result['requests'] = sorted(request_list, key=lambda x: x['order_num'])
        result['request_count'] = len(request_list)
        
        return result
    
    @staticmethod
    async def update_test_suite(
        db: AsyncSession,
        test_suite_id: int,
        data: APITestSuiteUpdateSchema,
        user_id: int
    ) -> Dict[str, Any]:
        """更新测试套件"""
        api_test_suite_crud = APITestSuiteCRUD(db)
        api_test_suite_request_crud = APITestSuiteRequestCRUD(db)
        test_suite = await api_test_suite_crud.get_by_id_crud(test_suite_id)
        if not test_suite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="测试套件不存在"
            )
        
        # 更新套件基本信息
        request_ids = data.request_ids
        suite_data = data.model_dump(exclude={'request_ids'}, exclude_unset=True)
        
        updated_suite = await api_test_suite_crud.update_crud(test_suite.id, suite_data)
        
        # 如果提供了request_ids，更新关联关系
        if request_ids is not None:

            await api_test_suite_request_crud.delete_by_suite_id(
                db=db,
                test_suite_id=test_suite_id,
                user_id=user_id
            )
            
            # 创建新的关联
            for idx, request_id in enumerate(request_ids):
                suite_request_data = {
                    'test_suite_id': test_suite_id,
                    'request_id': request_id,
                    'order_num': idx + 1
                }
                await api_test_suite_request_crud.create_crud(suite_request_data)
        
        result = APITestSuiteOutSchema.model_validate(updated_suite).model_dump()
        
        # 获取请求数量
        suite_requests = await api_test_suite_request_crud.get_by_suite_id(
            db=db,
            test_suite_id=test_suite_id
        )
        result['request_count'] = len(suite_requests)
        
        return result
    
    @staticmethod
    async def delete_test_suite(
        db: AsyncSession,
        test_suite_id: int,
        user_id: int
    ):
        """删除测试套件"""
        api_test_suite_crud = APITestSuiteCRUD(db)
        api_test_suite_request_crud = APITestSuiteRequestCRUD(db)
        test_suite = await api_test_suite_crud.get_by_id_crud(test_suite_id)
        if not test_suite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="测试套件不存在"
            )
        
        # 删除关联的请求
        await api_test_suite_request_crud.delete_by_suite_id(
            db=db,
            test_suite_id=test_suite_id,
            user_id=user_id
        )
        
        # 删除套件
        await api_test_suite_crud.delete_crud([test_suite_id])
    
    @staticmethod
    async def execute_test_suite(
        db: AsyncSession,
        test_suite_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """执行测试套件"""
        from datetime import datetime
        from .model import APITestExecutionModel
        
        api_test_suite_crud = APITestSuiteCRUD(db)
        api_test_suite_request_crud = APITestSuiteRequestCRUD(db)
        api_request_crud = APIRequestCRUD(db)
        
        # 获取测试套件
        test_suite = await api_test_suite_crud.get_by_id_crud(test_suite_id)
        if not test_suite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="测试套件不存在"
            )
        
        # 获取关联的请求
        suite_requests = await api_test_suite_request_crud.get_by_suite_id(
            db=db,
            test_suite_id=test_suite_id
        )
        
        if not suite_requests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="测试套件中没有请求"
            )
        
        # 创建执行记录
        execution = APITestExecutionModel(
            test_suite_id=test_suite_id,
            status='RUNNING',
            start_time=datetime.now(),
            total_requests=len(suite_requests),
            passed_requests=0,
            failed_requests=0,
            executed_by=user_id
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # 执行所有请求
        results = []
        passed_count = 0
        failed_count = 0
        
        for suite_request in sorted(suite_requests, key=lambda x: x.order_num):
            try:
                # 获取请求信息
                request = await api_request_crud.get_by_id_crud(suite_request.request_id)
                request_name = request.name if request else f"请求 {suite_request.request_id}"
                
                # 执行请求
                result = await request_executor.execute_request(
                    db=db,
                    request_id=suite_request.request_id,
                    environment_id=test_suite.environment_id,
                    user_id=user_id
                )
                
                # 判断是否通过
                passed = result.get('assertions_passed', True) and not result.get('error_message')
                if passed:
                    passed_count += 1
                else:
                    failed_count += 1
                
                # 构建结果对象（扁平化结构）
                results.append({
                    'request_id': suite_request.request_id,
                    'request_name': request_name,
                    'order_num': suite_request.order_num,
                    'status_code': result.get('status_code', 0),
                    'response_time': result.get('response_time', 0),
                    'passed': passed,
                    'error_message': result.get('error_message'),
                    'assertions_results': result.get('assertions_results', [])
                })
            
            except Exception as e:
                failed_count += 1
                results.append({
                    'request_id': suite_request.request_id,
                    'request_name': f"请求 {suite_request.request_id}",
                    'order_num': suite_request.order_num,
                    'status_code': 0,
                    'response_time': 0,
                    'passed': False,
                    'error_message': str(e),
                    'assertions_results': []
                })
        
        # 更新执行记录
        execution.status = 'SUCCESS' if failed_count == 0 else 'FAILED'
        execution.end_time = datetime.now()
        execution.passed_requests = passed_count
        execution.failed_requests = failed_count
        execution.results = results
        
        await db.commit()
        await db.refresh(execution)
        
        return {
            'execution_id': execution.id,
            'status': execution.status,
            'total_requests': execution.total_requests,
            'passed_requests': execution.passed_requests,
            'failed_requests': execution.failed_requests,
            'start_time': execution.start_time,
            'end_time': execution.end_time,
            'results': results
        }


class APIRequestHistoryService:
    """API请求历史服务"""
    
    @staticmethod
    @staticmethod
    async def get_request_history_list(
        db: AsyncSession,
        request_id: int,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """获取请求历史列表"""
        api_request_history_crud = APIRequestHistoryCRUD()
        skip = (page - 1) * page_size
        items, total = await api_request_history_crud.get_by_request_id(
            db=db,
            request_id=request_id,
            skip=skip,
            limit=page_size
        )
        
        return {
            "items": [APIRequestHistoryOutSchema.model_validate(item).model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def get_request_history(
        db: AsyncSession,
        history_id: int
    ) -> Dict[str, Any]:
        """获取请求历史详情"""
        api_request_history_crud = APIRequestHistoryCRUD()
        history = await api_request_history_crud.get_by_id(db=db, history_id=history_id)
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="历史记录不存在"
            )
        
        return APIRequestHistoryOutSchema.model_validate(history).model_dump()



class SSLCertificateService:
    """SSL证书服务"""
    
    @staticmethod
    async def create_certificate(
        db: AsyncSession,
        data: 'SSLCertificateCreateSchema',
        user_id: int
    ) -> Dict[str, Any]:
        """创建SSL证书"""
        from .crud import SSLCertificateCRUD
        from .schema import SSLCertificateOutSchema
        
        ssl_cert_crud = SSLCertificateCRUD(db)
        
        # 验证证书类型
        if data.cert_type not in ['CA', 'CLIENT']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="证书类型必须是 CA 或 CLIENT"
            )
        
        # 验证必要字段
        if data.cert_type == 'CA' and not data.ca_cert:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CA证书类型必须提供ca_cert字段"
            )
        
        if data.cert_type == 'CLIENT' and (not data.client_cert or not data.client_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="客户端证书类型必须提供client_cert和client_key字段"
            )
        
        # 创建证书
        certificate = await ssl_cert_crud.create_crud(data=data.model_dump())
        
        return SSLCertificateOutSchema.model_validate(certificate).model_dump()
    
    @staticmethod
    async def get_certificate_list(
        db: AsyncSession,
        project_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取证书列表"""
        from .crud import SSLCertificateCRUD
        from .schema import SSLCertificateOutSchema
        
        ssl_cert_crud = SSLCertificateCRUD(db)
        skip = (page - 1) * page_size
        items, total = await ssl_cert_crud.get_by_project_id(
            db=db,
            project_id=project_id,
            skip=skip,
            limit=page_size
        )
        
        return {
            "items": [SSLCertificateOutSchema.model_validate(item).model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def get_certificate(
        db: AsyncSession,
        cert_id: int
    ) -> Dict[str, Any]:
        """获取证书详情"""
        from .crud import SSLCertificateCRUD
        from .schema import SSLCertificateDetailSchema
        
        ssl_cert_crud = SSLCertificateCRUD(db)
        certificate = await ssl_cert_crud.get_by_id_crud(cert_id)
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="证书不存在"
            )
        
        return SSLCertificateDetailSchema.model_validate(certificate).model_dump()
    
    @staticmethod
    async def update_certificate(
        db: AsyncSession,
        cert_id: int,
        data: 'SSLCertificateUpdateSchema',
        user_id: int
    ) -> Dict[str, Any]:
        """更新证书"""
        from .crud import SSLCertificateCRUD
        from .schema import SSLCertificateOutSchema
        
        ssl_cert_crud = SSLCertificateCRUD(db)
        certificate = await ssl_cert_crud.get_by_id_crud(cert_id)
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="证书不存在"
            )
        
        updated_cert = await ssl_cert_crud.update_crud(certificate.id, data.model_dump(exclude_unset=True))
        
        return SSLCertificateOutSchema.model_validate(updated_cert).model_dump()
    
    @staticmethod
    async def delete_certificate(
        db: AsyncSession,
        cert_id: int,
        user_id: int
    ):
        """删除证书"""
        from .crud import SSLCertificateCRUD
        
        ssl_cert_crud = SSLCertificateCRUD(db)
        certificate = await ssl_cert_crud.get_by_id_crud(cert_id)
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="证书不存在"
            )
        
        await ssl_cert_crud.delete_crud([cert_id])
    
    @staticmethod
    async def toggle_certificate(
        db: AsyncSession,
        cert_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """切换证书启用状态"""
        from .crud import SSLCertificateCRUD
        
        ssl_cert_crud = SSLCertificateCRUD(db)
        certificate = await ssl_cert_crud.get_by_id_crud(cert_id)
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="证书不存在"
            )
        
        is_active = await ssl_cert_crud.toggle_active(db=db, cert_id=cert_id)
        
        return {
            "id": cert_id,
            "is_active": is_active
        }



class PublicScriptService:
    """公共脚本服务"""
    
    @staticmethod
    async def get_list(db: AsyncSession, project_id: int, page: int = 1, page_size: int = 20):
        """获取公共脚本列表"""
        crud = PublicScriptCRUD(db)
        return await crud.get_by_project(db, project_id, page, page_size)
    
    @staticmethod
    async def create(db: AsyncSession, data: dict, user_id: int):
        """创建公共脚本"""
        crud = PublicScriptCRUD(db)
        data['created_by'] = user_id
        data['updated_by'] = user_id
        return await crud.create_crud(data=data)
    
    @staticmethod
    async def update(db: AsyncSession, script_id: int, data: dict, user_id: int):
        """更新公共脚本"""
        crud = PublicScriptCRUD(db)
        data['updated_by'] = user_id
        return await crud.update_crud(id=script_id, data=data)
    
    @staticmethod
    async def delete(db: AsyncSession, script_id: int):
        """删除公共脚本"""
        crud = PublicScriptCRUD(db)
        return await crud.delete_crud(ids=[script_id])
    
    @staticmethod
    async def get_detail(db: AsyncSession, script_id: int):
        """获取公共脚本详情"""
        crud = PublicScriptCRUD(db)
        return await crud.get_by_id_crud(script_id)


class DatabaseConfigService:
    """数据库配置服务"""
    
    @staticmethod
    async def get_list(db: AsyncSession, project_id: int, page: int = 1, page_size: int = 20):
        """获取数据库配置列表"""
        crud = DatabaseConfigCRUD(db)
        return await crud.get_by_project(db, project_id, page, page_size)
    
    @staticmethod
    async def create(db: AsyncSession, data: dict, user_id: int):
        """创建数据库配置"""
        crud = DatabaseConfigCRUD(db)
        data['created_by'] = user_id
        data['updated_by'] = user_id
        # TODO: 加密密码
        return await crud.create_crud(data=data)
    
    @staticmethod
    async def update(db: AsyncSession, config_id: int, data: dict, user_id: int):
        """更新数据库配置"""
        crud = DatabaseConfigCRUD(db)
        data['updated_by'] = user_id
        # TODO: 加密密码
        return await crud.update_crud(id=config_id, data=data)
    
    @staticmethod
    async def delete(db: AsyncSession, config_id: int):
        """删除数据库配置"""
        crud = DatabaseConfigCRUD(db)
        return await crud.delete_crud(ids=[config_id])
    
    @staticmethod
    async def get_detail(db: AsyncSession, config_id: int):
        """获取数据库配置详情"""
        crud = DatabaseConfigCRUD(db)
        return await crud.get_by_id_crud(config_id)
    
    @staticmethod
    async def test_connection(db: AsyncSession, config_id: int):
        """测试数据库连接"""
        crud = DatabaseConfigCRUD(db)
        config = await crud.get_by_id_crud(config_id)
        
        if not config:
            raise ValueError('数据库配置不存在')
        
        try:
            if config.db_type == 'mysql':
                import asyncmy
                connection = await asyncmy.connect(
                    host=config.host,
                    port=config.port,
                    user=config.username,
                    password=config.password,
                    db=config.database_name,
                )
                connection.close()
                return {'success': True, 'message': '连接成功'}
            else:
                return {'success': False, 'message': f'暂不支持{config.db_type}类型的连接测试'}
        except Exception as e:
            return {'success': False, 'message': f'连接失败: {str(e)}'}
