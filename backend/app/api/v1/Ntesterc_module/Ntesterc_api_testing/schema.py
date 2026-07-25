#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.base_schema import BaseSchema, TimestampSchema, PageSchema


# ==================== API项目 ====================
class APIProjectCreateSchema(BaseModel):
    """API项目创建"""
    project_id: int = Field(..., description='关联项目ID')
    name: str = Field(..., max_length=200, description='API项目名称')
    description: Optional[str] = Field(None, description='项目描述')
    project_type: str = Field('HTTP', description='类型: HTTP/WEBSOCKET')
    base_url: Optional[str] = Field(None, max_length=500, description='基础URL')


class APIProjectUpdateSchema(BaseModel):
    """API项目更新"""
    name: Optional[str] = Field(None, max_length=200, description='API项目名称')
    description: Optional[str] = Field(None, description='项目描述')
    project_type: Optional[str] = Field(None, description='类型')
    base_url: Optional[str] = Field(None, max_length=500, description='基础URL')


class APIProjectOutSchema(TimestampSchema):
    """API项目输出"""
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    project_type: str
    base_url: Optional[str] = None


# ==================== API集合 ====================
class APICollectionCreateSchema(BaseModel):
    """API集合创建"""
    api_project_id: int = Field(..., description='API项目ID')
    name: str = Field(..., max_length=200, description='集合名称')
    description: Optional[str] = Field(None, description='集合描述')
    parent_id: Optional[int] = Field(None, description='父级集合ID')
    order_num: int = Field(0, description='排序')


class APICollectionUpdateSchema(BaseModel):
    """API集合更新"""
    name: Optional[str] = Field(None, max_length=200, description='集合名称')
    description: Optional[str] = Field(None, description='集合描述')
    parent_id: Optional[int] = Field(None, description='父级集合ID')
    order_num: Optional[int] = Field(None, description='排序')


class APICollectionOutSchema(TimestampSchema):
    """API集合输出"""
    id: int
    api_project_id: int
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    order_num: int
    children: Optional[List['APICollectionOutSchema']] = []


# ==================== API请求 ====================
class APIRequestCreateSchema(BaseModel):
    """API请求创建"""
    collection_id: int = Field(..., description='所属集合ID')
    name: str = Field(..., max_length=200, description='请求名称')
    description: Optional[str] = Field(None, description='请求描述')
    request_type: str = Field('HTTP', description='请求类型')
    method: str = Field('GET', description='请求方法')
    url: str = Field(..., description='请求URL')
    headers: Optional[Dict[str, Any]] = Field(None, description='请求头')
    params: Optional[Dict[str, Any]] = Field(None, description='URL参数')
    body: Optional[Any] = Field(None, description='请求体')
    cookies: Optional[Dict[str, Any]] = Field(None, description='Cookies')
    auth: Optional[Dict[str, Any]] = Field(None, description='认证信息')
    pre_request_script: Optional[Any] = Field(None, description='前置操作列表（兼容字符串和列表）')
    post_request_script: Optional[Any] = Field(None, description='后置操作列表（兼容字符串和列表）')
    assertions: Optional[List[Dict[str, Any]]] = Field(None, description='断言规则')
    verify_ssl: bool = Field(True, description='SSL证书验证')
    follow_redirects: bool = Field(True, description='自动跟随重定向')
    timeout: int = Field(30000, description='超时时间(毫秒)')
    order_num: int = Field(0, description='排序')


class APIRequestUpdateSchema(BaseModel):
    """API请求更新"""
    name: Optional[str] = Field(None, max_length=200, description='请求名称')
    description: Optional[str] = Field(None, description='请求描述')
    request_type: Optional[str] = Field(None, description='请求类型')
    method: Optional[str] = Field(None, description='请求方法')
    url: Optional[str] = Field(None, description='请求URL')
    headers: Optional[Dict[str, Any]] = Field(None, description='请求头')
    params: Optional[Dict[str, Any]] = Field(None, description='URL参数')
    body: Optional[Any] = Field(None, description='请求体')
    cookies: Optional[Dict[str, Any]] = Field(None, description='Cookies')
    auth: Optional[Dict[str, Any]] = Field(None, description='认证信息')
    pre_request_script: Optional[Any] = Field(None, description='前置操作列表（兼容字符串和列表）')
    post_request_script: Optional[Any] = Field(None, description='后置操作列表（兼容字符串和列表）')
    assertions: Optional[List[Dict[str, Any]]] = Field(None, description='断言规则')
    verify_ssl: Optional[bool] = Field(None, description='SSL证书验证')
    follow_redirects: Optional[bool] = Field(None, description='自动跟随重定向')
    timeout: Optional[int] = Field(None, description='超时时间(毫秒)')
    order_num: Optional[int] = Field(None, description='排序')


class APIRequestOutSchema(TimestampSchema):
    """API请求输出"""
    id: int
    collection_id: int
    name: str
    description: Optional[str] = None
    request_type: str
    method: str
    url: str
    headers: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    body: Optional[Any] = None
    cookies: Optional[Dict[str, Any]] = None
    auth: Optional[Dict[str, Any]] = None
    pre_request_script: Optional[List[Dict[str, Any]]] = None
    post_request_script: Optional[List[Dict[str, Any]]] = None
    assertions: Optional[List[Dict[str, Any]]] = None
    verify_ssl: bool = True
    follow_redirects: bool = True
    timeout: int = 30000
    order_num: int


# ==================== API环境变量 ====================
class APIEnvironmentCreateSchema(BaseModel):
    """API环境变量创建"""
    project_id: int = Field(..., description='关联项目ID')
    name: str = Field(..., max_length=200, description='环境名称')
    scope: str = Field('LOCAL', description='作用域: GLOBAL/LOCAL')
    variables: Optional[Dict[str, Any]] = Field(None, description='环境变量')
    is_active: bool = Field(False, description='是否激活')


class APIEnvironmentUpdateSchema(BaseModel):
    """API环境变量更新"""
    name: Optional[str] = Field(None, max_length=200, description='环境名称')
    scope: Optional[str] = Field(None, description='作用域')
    variables: Optional[Dict[str, Any]] = Field(None, description='环境变量')
    is_active: Optional[bool] = Field(None, description='是否激活')


class APIEnvironmentOutSchema(TimestampSchema):
    """API环境变量输出"""
    id: int
    project_id: int
    name: str
    scope: str
    variables: Optional[Dict[str, Any]] = None
    is_active: bool


# ==================== API测试套件 ====================
class APITestSuiteCreateSchema(BaseModel):
    """API测试套件创建"""
    api_project_id: int = Field(..., description='API项目ID')
    name: str = Field(..., max_length=200, description='套件名称')
    description: Optional[str] = Field(None, description='套件描述')
    environment_id: Optional[int] = Field(None, description='执行环境ID')
    request_ids: Optional[List[int]] = Field([], description='请求ID列表')


class APITestSuiteUpdateSchema(BaseModel):
    """API测试套件更新"""
    name: Optional[str] = Field(None, max_length=200, description='套件名称')
    description: Optional[str] = Field(None, description='套件描述')
    environment_id: Optional[int] = Field(None, description='执行环境ID')
    request_ids: Optional[List[int]] = Field(None, description='请求ID列表')


class APITestSuiteOutSchema(TimestampSchema):
    """API测试套件输出"""
    id: int
    api_project_id: int
    name: str
    description: Optional[str] = None
    environment_id: Optional[int] = None
    request_count: int = 0


# ==================== 请求执行 ====================
class APIRequestExecuteSchema(BaseModel):
    """API请求执行"""
    environment_id: Optional[int] = Field(None, description='环境ID')


class APIRequestExecuteResultSchema(BaseModel):
    """API请求执行结果"""
    status_code: int
    response_time: float
    response_data: Dict[str, Any]
    error_message: Optional[str] = None
    assertions_results: Optional[List[Dict[str, Any]]] = None


# ==================== 请求历史 ====================
class APIRequestHistoryOutSchema(BaseModel):
    """API请求历史输出"""
    model_config = {"from_attributes": True}
    
    id: int
    request_id: int
    environment_id: Optional[int] = None
    environment_name: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    assertions_results: Optional[List[Dict[str, Any]]] = None
    assertions_passed: Optional[bool] = None
    executed_by: int
    executed_at: Optional[datetime] = None
    
    # Base fields
    creation_date: Optional[datetime] = None
    created_by: Optional[int] = None
    updation_date: Optional[datetime] = None
    updated_by: Optional[int] = None
    enabled_flag: Optional[int] = None
    trace_id: Optional[str] = None


class APIRequestHistoryBaseSchema(BaseSchema):
    """API请求历史分页"""
    items: List[APIRequestHistoryOutSchema]


# ==================== 套件执行 ====================
class APITestSuiteExecuteSchema(BaseModel):
    """API测试套件执行"""
    environment_id: Optional[int] = Field(None, description='环境ID')


class APITestSuiteExecuteResultSchema(BaseModel):
    """API测试套件执行结果"""
    execution_id: int
    status: str
    total_requests: int
    passed_requests: int
    failed_requests: int
    start_time: datetime
    end_time: Optional[datetime] = None


# 分页响应
class APIProjectBaseSchema(BaseSchema):
    """API项目分页"""
    items: List[APIProjectOutSchema]


class APICollectionBaseSchema(BaseSchema):
    """API集合分页"""
    items: List[APICollectionOutSchema]


class APIRequestBaseSchema(BaseSchema):
    """API请求分页"""
    items: List[APIRequestOutSchema]


class APIEnvironmentBaseSchema(BaseSchema):
    """API环境变量分页"""
    items: List[APIEnvironmentOutSchema]


class APITestSuiteBaseSchema(BaseSchema):
    """API测试套件分页"""
    items: List[APITestSuiteOutSchema]


# ==================== 导入导出 ====================
class ImportDataSchema(BaseModel):
    """导入数据"""
    data: Dict[str, Any] = Field(..., description='导入的JSON数据')


class ExportResultSchema(BaseModel):
    """导出结果"""
    data: Dict[str, Any] = Field(..., description='导出的JSON数据')
    filename: str = Field(..., description='建议的文件名')


class ImportResultSchema(BaseModel):
    """导入结果"""
    success: bool = Field(..., description='是否成功')
    message: str = Field(..., description='结果消息')
    data: Optional[Dict[str, Any]] = Field(None, description='导入统计数据')




# ==================== 分页响应 ====================
class APIProjectPaginationSchema(BaseSchema):
    """API项目分页"""
    total: int
    page: int
    page_size: int
    items: List[APIProjectOutSchema]


class APICollectionPaginationSchema(BaseSchema):
    """API集合分页"""
    total: int
    page: int
    page_size: int
    items: List[APICollectionOutSchema]


class APIRequestPaginationSchema(BaseSchema):
    """API请求分页"""
    total: int
    page: int
    page_size: int
    items: List[APIRequestOutSchema]


class APIEnvironmentPaginationSchema(BaseSchema):
    """API环境变量分页"""
    total: int
    page: int
    page_size: int
    items: List[APIEnvironmentOutSchema]


class APITestSuitePaginationSchema(BaseSchema):
    """API测试套件分页"""
    total: int
    page: int
    page_size: int
    items: List[APITestSuiteOutSchema]


class APIRequestHistoryPaginationSchema(BaseSchema):
    """API请求历史分页"""
    total: int
    page: int
    page_size: int
    items: List[APIRequestHistoryOutSchema]


# ==================== SSL证书 ====================
class SSLCertificateCreateSchema(BaseModel):
    """SSL证书创建"""
    project_id: int = Field(..., description='关联项目ID')
    name: str = Field(..., max_length=200, description='证书名称')
    cert_type: str = Field(..., description='证书类型: CA/CLIENT')
    domain: Optional[str] = Field(None, max_length=500, description='适用域名（支持通配符）')
    ca_cert: Optional[str] = Field(None, description='CA证书内容（PEM格式）')
    client_cert: Optional[str] = Field(None, description='客户端证书内容（CRT/PEM格式）')
    client_key: Optional[str] = Field(None, description='客户端私钥内容（KEY/PEM格式）')
    passphrase: Optional[str] = Field(None, max_length=500, description='私钥密码')
    is_active: bool = Field(True, description='是否启用')
    description: Optional[str] = Field(None, description='描述')


class SSLCertificateUpdateSchema(BaseModel):
    """SSL证书更新"""
    name: Optional[str] = Field(None, max_length=200, description='证书名称')
    domain: Optional[str] = Field(None, max_length=500, description='适用域名')
    ca_cert: Optional[str] = Field(None, description='CA证书内容')
    client_cert: Optional[str] = Field(None, description='客户端证书内容')
    client_key: Optional[str] = Field(None, description='客户端私钥内容')
    passphrase: Optional[str] = Field(None, max_length=500, description='私钥密码')
    is_active: Optional[bool] = Field(None, description='是否启用')
    description: Optional[str] = Field(None, description='描述')


class SSLCertificateOutSchema(TimestampSchema):
    """SSL证书输出（不包含敏感信息）"""
    id: int
    project_id: int
    name: str
    cert_type: str
    domain: Optional[str] = None
    is_active: bool
    description: Optional[str] = None
    # 注意：不返回证书内容和密码


class SSLCertificateDetailSchema(TimestampSchema):
    """SSL证书详情（包含证书内容，不包含私钥）"""
    id: int
    project_id: int
    name: str
    cert_type: str
    domain: Optional[str] = None
    ca_cert: Optional[str] = None
    client_cert: Optional[str] = None
    # 注意：不返回私钥和密码
    is_active: bool
    description: Optional[str] = None


class SSLCertificatePaginationSchema(BaseSchema):
    """SSL证书分页"""
    total: int
    page: int
    page_size: int
    items: List[SSLCertificateOutSchema]



# ==================== 公共脚本 ====================

class PublicScriptBase(BaseModel):
    """公共脚本基础Schema"""
    project_id: int
    name: str
    description: Optional[str] = None
    script_type: str = 'javascript'
    script_content: str
    category: Optional[str] = None
    is_active: bool = True


class PublicScriptCreate(PublicScriptBase):
    """创建公共脚本"""
    pass


class PublicScriptUpdate(BaseModel):
    """更新公共脚本"""
    name: Optional[str] = None
    description: Optional[str] = None
    script_type: Optional[str] = None
    script_content: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class PublicScriptResponse(PublicScriptBase):
    """公共脚本响应"""
    id: int
    creation_date: Optional[datetime] = None
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True


# ==================== 数据库配置 ====================

class DatabaseConfigBase(BaseModel):
    """数据库配置基础Schema"""
    project_id: int
    name: str
    description: Optional[str] = None
    db_type: str
    host: str
    port: int
    database_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_params: Optional[Dict[str, Any]] = None
    is_active: bool = True


class DatabaseConfigCreate(DatabaseConfigBase):
    """创建数据库配置"""
    pass


class DatabaseConfigUpdate(BaseModel):
    """更新数据库配置"""
    name: Optional[str] = None
    description: Optional[str] = None
    db_type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_params: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DatabaseConfigResponse(DatabaseConfigBase):
    """数据库配置响应"""
    id: int
    creation_date: Optional[datetime] = None
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True


# ==================== 操作定义 ====================

class OperationBase(BaseModel):
    """操作基础Schema"""
    type: str  # script/public_script/database/wait/extract/import_request
    enabled: bool = True
    description: Optional[str] = None


class ScriptOperation(OperationBase):
    """脚本操作"""
    type: str = 'script'
    script: str


class PublicScriptOperation(OperationBase):
    """公共脚本操作"""
    type: str = 'public_script'
    script_id: int


class DatabaseOperation(OperationBase):
    """数据库操作"""
    type: str = 'database'
    db_config_id: int
    sql: str
    save_to_var: Optional[str] = None


class WaitOperation(OperationBase):
    """等待操作"""
    type: str = 'wait'
    wait_time: int  # 毫秒


class ExtractOperation(OperationBase):
    """提取变量操作"""
    type: str = 'extract'
    extract_type: str  # jsonpath/regex/header
    source: str = 'body'  # body/header/status
    expression: str
    var_name: str


class ImportRequestOperation(OperationBase):
    """导入其它接口操作"""
    type: str = 'import_request'
    request_id: int
    environment_id: Optional[int] = None
