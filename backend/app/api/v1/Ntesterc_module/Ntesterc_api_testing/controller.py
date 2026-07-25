#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from typing import Optional

from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.db.sqlalchemy import get_db

from app.common.response import success_response

from app.core.dependencies import get_current_user_id

from .schema import (

    APIProjectCreateSchema,

    APIProjectUpdateSchema,

    APIProjectPaginationSchema,

    APICollectionCreateSchema,

    APICollectionUpdateSchema,

    APIRequestCreateSchema,

    APIRequestUpdateSchema,

    APIRequestPaginationSchema,

    APIRequestExecuteSchema,

    APIEnvironmentCreateSchema,

    APIEnvironmentUpdateSchema,

    APITestSuiteCreateSchema,

    APITestSuiteUpdateSchema,

    APITestSuitePaginationSchema,

    APIRequestHistoryPaginationSchema,

    ImportDataSchema,

    ExportResultSchema,

    ImportResultSchema,

    SSLCertificateCreateSchema,

    SSLCertificateUpdateSchema,

    PublicScriptCreate,

    PublicScriptUpdate,

    DatabaseConfigCreate,

    DatabaseConfigUpdate

)

from .service import (

    APIProjectService,

    APICollectionService,

    APIRequestService,

    APIEnvironmentService,

    APITestSuiteService,

    APIRequestHistoryService,

    SSLCertificateService,

    PublicScriptService,

    DatabaseConfigService

)

from .import_export import import_export_service



router = APIRouter(tags=["API测试"])





# ==================== API项目管理 ====================

@router.post("/projects", summary="创建API项目")

async def create_api_project(

    data: APIProjectCreateSchema,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """创建API项目"""

    result = await APIProjectService.create_api_project(db, data, user_id)

    return success_response(data=result, message="创建成功")





@router.get("/projects", summary="获取API项目列表")

async def get_api_project_list(

    project_id: int = Query(..., description="项目ID"),

    page: int = Query(1, ge=1, description="页码"),

    page_size: int = Query(20, ge=1, le=1000, description="每页数量"),

    db: AsyncSession = Depends(get_db)

):

    """获取API项目列表"""

    result = await APIProjectService.get_api_project_list(db, project_id, page, page_size)

    return success_response(data=result)





@router.get("/projects/{api_project_id}", summary="获取API项目详情")

async def get_api_project(

    api_project_id: int,

    db: AsyncSession = Depends(get_db)

):

    """获取API项目详情"""

    result = await APIProjectService.get_api_project(db, api_project_id)

    return success_response(data=result)





@router.put("/projects/{api_project_id}", summary="更新API项目")

async def update_api_project(

    api_project_id: int,

    data: APIProjectUpdateSchema,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """更新API项目"""

    result = await APIProjectService.update_api_project(db, api_project_id, data, user_id)

    return success_response(data=result, message="更新成功")





@router.delete("/projects/{api_project_id}", summary="删除API项目")

async def delete_api_project(

    api_project_id: int,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """删除API项目"""

    await APIProjectService.delete_api_project(db, api_project_id, user_id)

    return success_response(message="删除成功")





# ==================== API集合管理 ====================

@router.post("/collections", summary="创建API集合")

async def create_collection(

    data: APICollectionCreateSchema,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """创建API集合"""

    result = await APICollectionService.create_collection(db, data, user_id)

    return success_response(data=result, message="创建成功")





@router.get("/collections/tree", summary="获取API集合树")

async def get_collection_tree(

    api_project_id: int = Query(..., description="API项目ID"),

    db: AsyncSession = Depends(get_db)

):

    """获取API集合树"""

    result = await APICollectionService.get_collection_tree(db, api_project_id)

    return success_response(data=result)





@router.put("/collections/{collection_id}", summary="更新API集合")

async def update_collection(

    collection_id: int,

    data: APICollectionUpdateSchema,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """更新API集合"""

    result = await APICollectionService.update_collection(db, collection_id, data, user_id)

    return success_response(data=result, message="更新成功")





@router.delete("/collections/{collection_id}", summary="删除API集合")

async def delete_collection(

    collection_id: int,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """删除API集合"""

    await APICollectionService.delete_collection(db, collection_id, user_id)

    return success_response(message="删除成功")





# ==================== API请求管理 ====================

@router.post("/requests", summary="创建API请求")

async def create_request(

    data: APIRequestCreateSchema,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """创建API请求"""

    result = await APIRequestService.create_request(db, data, user_id)

    return success_response(data=result, message="创建成功")





@router.get("/requests", summary="获取API请求列表")

async def get_request_list(

    collection_id: int = Query(..., description="集合ID"),

    page: int = Query(1, ge=1, description="页码"),

    page_size: int = Query(100, ge=1, le=1000, description="每页数量"),

    db: AsyncSession = Depends(get_db)

):

    """获取API请求列表"""

    result = await APIRequestService.get_request_list(db, collection_id, page, page_size)

    return success_response(data=result)





@router.get("/requests/{request_id}", summary="获取API请求详情")

async def get_request(

    request_id: int,

    db: AsyncSession = Depends(get_db)

):

    """获取API请求详情"""

    result = await APIRequestService.get_request(db, request_id)

    return success_response(data=result)





@router.put("/requests/{request_id}", summary="更新API请求")

async def update_request(

    request_id: int,

    data: APIRequestUpdateSchema,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """更新API请求"""

    result = await APIRequestService.update_request(db, request_id, data, user_id)

    return success_response(data=result, message="更新成功")





@router.delete("/requests/{request_id}", summary="删除API请求")

async def delete_request(

    request_id: int,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """删除API请求"""

    await APIRequestService.delete_request(db, request_id, user_id)

    return success_response(message="删除成功")





@router.post("/requests/{request_id}/execute", summary="执行API请求")

async def execute_request(

    request_id: int,

    data: APIRequestExecuteSchema,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """执行API请求"""

    result = await APIRequestService.execute_request(db, request_id, data.environment_id, user_id)

    return success_response(data=result)





# ==================== API环境变量管理 ====================

@router.post("/environments", summary="创建API环境变量")

async def create_environment(

    data: APIEnvironmentCreateSchema,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """创建API环境变量"""

    result = await APIEnvironmentService.create_environment(db, data, user_id)

    return success_response(data=result, message="创建成功")





@router.get("/environments", summary="获取API环境变量列表")

async def get_environment_list(

    project_id: int = Query(..., description="项目ID"),

    db: AsyncSession = Depends(get_db)

):

    """获取API环境变量列表"""

    result = await APIEnvironmentService.get_environment_list(db, project_id)

    return success_response(data=result)





@router.get("/environments/export", summary="导出环境变量")

async def export_environments(

    project_id: int = Query(..., description="项目ID"),

    db: AsyncSession = Depends(get_db)

):

    """导出环境变量"""

    result = await import_export_service.export_environments(db, project_id)

    

    filename = f"environments_export.json"

    

    return success_response(data={

        'data': result,

        'filename': filename

    })





@router.post("/environments/import", summary="导入环境变量")

async def import_environments(

    project_id: int = Query(..., description="项目ID"),

    data: ImportDataSchema = None,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """导入环境变量"""

    try:

        result = await import_export_service.import_environments(

            db=db,

            project_id=project_id,

            import_data=data.data,

            user_id=user_id

        )

        return success_response(data=result, message="导入成功")

    except Exception as e:

        return success_response(data={

            'success': False,

            'message': f"导入失败: {str(e)}"

        })





@router.get("/environments/{environment_id}", summary="获取API环境变量详情")

async def get_environment(

    environment_id: int,

    db: AsyncSession = Depends(get_db)

):

    """获取API环境变量详情"""

    result = await APIEnvironmentService.get_environment(db, environment_id)

    return success_response(data=result)





@router.put("/environments/{environment_id}", summary="更新API环境变量")

async def update_environment(

    environment_id: int,

    data: APIEnvironmentUpdateSchema,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """更新API环境变量"""

    result = await APIEnvironmentService.update_environment(db, environment_id, data, user_id)

    return success_response(data=result, message="更新成功")





@router.delete("/environments/{environment_id}", summary="删除API环境变量")

async def delete_environment(

    environment_id: int,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """删除API环境变量"""

    await APIEnvironmentService.delete_environment(db, environment_id, user_id)

    return success_response(message="删除成功")





@router.post("/environments/{environment_id}/activate", summary="激活API环境变量")

async def activate_environment(

    environment_id: int,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """激活API环境变量"""

    result = await APIEnvironmentService.activate_environment(db, environment_id, user_id)

    return success_response(data=result, message="激活成功")







# ==================== API测试套件管理 ====================

@router.post("/test_suites", summary="创建API测试套件")

async def create_test_suite(

    data: APITestSuiteCreateSchema,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """创建API测试套件"""

    result = await APITestSuiteService.create_test_suite(db, data, user_id)

    return success_response(data=result, message="创建成功")





@router.get("/test_suites", summary="获取API测试套件列表")

async def get_test_suite_list(

    api_project_id: int = Query(..., description="API项目ID"),

    page: int = Query(1, ge=1, description="页码"),

    page_size: int = Query(20, ge=1, le=1000, description="每页数量"),

    db: AsyncSession = Depends(get_db)

):

    """获取API测试套件列表"""

    result = await APITestSuiteService.get_test_suite_list(db, api_project_id, page, page_size)

    return success_response(data=result)





@router.get("/test_suites/{test_suite_id}", summary="获取API测试套件详情")

async def get_test_suite(

    test_suite_id: int,

    db: AsyncSession = Depends(get_db)

):

    """获取API测试套件详情"""

    result = await APITestSuiteService.get_test_suite(db, test_suite_id)

    return success_response(data=result)





@router.put("/test_suites/{test_suite_id}", summary="更新API测试套件")

async def update_test_suite(

    test_suite_id: int,

    data: APITestSuiteUpdateSchema,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """更新API测试套件"""

    result = await APITestSuiteService.update_test_suite(db, test_suite_id, data, user_id)

    return success_response(data=result, message="更新成功")





@router.delete("/test_suites/{test_suite_id}", summary="删除API测试套件")

async def delete_test_suite(

    test_suite_id: int,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """删除API测试套件"""

    await APITestSuiteService.delete_test_suite(db, test_suite_id, user_id)

    return success_response(message="删除成功")





@router.post("/test_suites/{test_suite_id}/execute", summary="执行API测试套件")

async def execute_test_suite(

    test_suite_id: int,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """执行API测试套件"""

    result = await APITestSuiteService.execute_test_suite(db, test_suite_id, user_id)

    return success_response(data=result, message="执行完成")





# ==================== API请求历史管理 ====================

@router.get("/requests/{request_id}/history", summary="获取API请求历史列表")

async def get_request_history_list(

    request_id: int,

    page: int = Query(1, ge=1, description="页码"),

    page_size: int = Query(50, ge=1, le=1000, description="每页数量"),

    db: AsyncSession = Depends(get_db)

):

    """获取API请求历史列表"""

    result = await APIRequestHistoryService.get_request_history_list(db, request_id, page, page_size)

    return success_response(data=result)





@router.get("/history/{history_id}", summary="获取API请求历史详情")

async def get_request_history(

    history_id: int,

    db: AsyncSession = Depends(get_db)

):

    """获取API请求历史详情"""

    result = await APIRequestHistoryService.get_request_history(db, history_id)

    return success_response(data=result)







# ==================== 导入导出功能 ====================

@router.get("/projects/{api_project_id}/export", summary="导出API项目")

async def export_api_project(

    api_project_id: int,

    db: AsyncSession = Depends(get_db)

):

    """导出API项目（包含集合和请求）"""

    result = await import_export_service.export_api_project(db, api_project_id)

    

    # 获取项目名称作为文件名

    project_name = result.get('project', {}).get('name', 'api_project')

    filename = f"{project_name}_export.json"

    

    return success_response(data={

        'data': result,

        'filename': filename

    })





@router.post("/projects/import", summary="导入API项目")

async def import_api_project(

    project_id: int = Query(..., description="目标项目ID"),

    data: ImportDataSchema = None,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """导入API项目"""

    try:

        result = await import_export_service.import_api_project(

            db=db,

            project_id=project_id,

            import_data=data.data,

            user_id=user_id

        )

        return success_response(data=result, message="导入成功")

    except Exception as e:

        return success_response(data={

            'success': False,

            'message': f"导入失败: {str(e)}"

        })





@router.get("/collections/{collection_id}/export", summary="导出API集合")

async def export_collection(

    collection_id: int,

    db: AsyncSession = Depends(get_db)

):

    """导出单个集合（包含请求）"""

    result = await import_export_service.export_collection(db, collection_id)

    

    # 获取集合名称作为文件名

    collection_name = result.get('collection', {}).get('name', 'collection')

    filename = f"{collection_name}_export.json"

    

    return success_response(data={

        'data': result,

        'filename': filename

    })





@router.post("/collections/import", summary="导入API集合")

async def import_collection(

    api_project_id: int = Query(..., description="API项目ID"),

    parent_id: Optional[int] = Query(None, description="父集合ID"),

    data: ImportDataSchema = None,

    db: AsyncSession = Depends(get_db),

    user_id: int = Depends(get_current_user_id)

):

    """导入集合"""

    try:

        result = await import_export_service.import_collection(

            db=db,

            api_project_id=api_project_id,

            import_data=data.data,

            user_id=user_id,

            parent_id=parent_id

        )

        return success_response(data=result, message="导入成功")

    except Exception as e:

        return success_response(data={

            'success': False,

            'message': f"导入失败: {str(e)}"

        })




# ==================== SSL证书管理 ====================
@router.post("/ssl-certificates", summary="创建SSL证书")
async def create_ssl_certificate(
    data: SSLCertificateCreateSchema,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """创建SSL证书"""
    result = await SSLCertificateService.create_certificate(db, data, user_id)
    return success_response(data=result)


@router.get("/ssl-certificates", summary="获取SSL证书列表")
async def list_ssl_certificates(
    project_id: int = Query(..., description="项目ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取SSL证书列表"""
    result = await SSLCertificateService.get_certificate_list(db, project_id, page, page_size)
    return success_response(data=result)


@router.get("/ssl-certificates/{cert_id}", summary="获取SSL证书详情")
async def get_ssl_certificate(
    cert_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取SSL证书详情"""
    result = await SSLCertificateService.get_certificate(db, cert_id)
    return success_response(data=result)


@router.put("/ssl-certificates/{cert_id}", summary="更新SSL证书")
async def update_ssl_certificate(
    cert_id: int,
    data: SSLCertificateUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """更新SSL证书"""
    result = await SSLCertificateService.update_certificate(db, cert_id, data, user_id)
    return success_response(data=result)


@router.delete("/ssl-certificates/{cert_id}", summary="删除SSL证书")
async def delete_ssl_certificate(
    cert_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """删除SSL证书"""
    await SSLCertificateService.delete_certificate(db, cert_id, user_id)
    return success_response(message="删除成功")


@router.put("/ssl-certificates/{cert_id}/toggle", summary="切换SSL证书启用状态")
async def toggle_ssl_certificate(
    cert_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """切换SSL证书启用状态"""
    result = await SSLCertificateService.toggle_certificate(db, cert_id, user_id)
    return success_response(data=result)



# ==================== 公共脚本管理 ====================

@router.get('/public-scripts', summary='获取公共脚本列表')
async def get_public_scripts(
    project_id: int,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取公共脚本列表"""
    result = await PublicScriptService.get_list(db, project_id, page, page_size)
    return success_response(data=result)


@router.post('/public-scripts', summary='创建公共脚本')
async def create_public_script(
    data: PublicScriptCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """创建公共脚本"""
    script = await PublicScriptService.create(db, data.dict(), user_id)
    return success_response(data=script)


@router.put('/public-scripts/{script_id}', summary='更新公共脚本')
async def update_public_script(
    script_id: int,
    data: PublicScriptUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """更新公共脚本"""
    script = await PublicScriptService.update(db, script_id, data.dict(exclude_unset=True), user_id)
    return success_response(data=script)


@router.delete('/public-scripts/{script_id}', summary='删除公共脚本')
async def delete_public_script(
    script_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """删除公共脚本"""
    await PublicScriptService.delete(db, script_id)
    return success_response(message='删除成功')


@router.get('/public-scripts/{script_id}', summary='获取公共脚本详情')
async def get_public_script_detail(
    script_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取公共脚本详情"""
    script = await PublicScriptService.get_detail(db, script_id)
    return success_response(data=script)


# ==================== 数据库配置管理 ====================

@router.get('/database-configs', summary='获取数据库配置列表')
async def get_database_configs(
    project_id: int,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取数据库配置列表"""
    result = await DatabaseConfigService.get_list(db, project_id, page, page_size)
    return success_response(data=result)


@router.post('/database-configs', summary='创建数据库配置')
async def create_database_config(
    data: DatabaseConfigCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """创建数据库配置"""
    config = await DatabaseConfigService.create(db, data.dict(), user_id)
    return success_response(data=config)


@router.put('/database-configs/{config_id}', summary='更新数据库配置')
async def update_database_config(
    config_id: int,
    data: DatabaseConfigUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """更新数据库配置"""
    config = await DatabaseConfigService.update(db, config_id, data.dict(exclude_unset=True), user_id)
    return success_response(data=config)


@router.delete('/database-configs/{config_id}', summary='删除数据库配置')
async def delete_database_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """删除数据库配置"""
    await DatabaseConfigService.delete(db, config_id)
    return success_response(message='删除成功')


@router.get('/database-configs/{config_id}', summary='获取数据库配置详情')
async def get_database_config_detail(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取数据库配置详情"""
    config = await DatabaseConfigService.get_detail(db, config_id)
    return success_response(data=config)


@router.post('/database-configs/{config_id}/test', summary='测试数据库连接')
async def test_database_connection(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """测试数据库连接"""
    result = await DatabaseConfigService.test_connection(db, config_id)
    return success_response(data=result)


