#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
from sqlalchemy import Column, BigInteger, String, Text, Integer, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.db_base import Base


class APIProjectModel(Base):
    """API项目模型"""
    __tablename__ = 'api_projects'
    
    project_id = Column(BigInteger, nullable=False, comment='关联项目ID', index=True)
    name = Column(String(200), nullable=False, comment='API项目名称')
    description = Column(Text, comment='项目描述')
    project_type = Column(String(20), default='HTTP', comment='类型: HTTP/WEBSOCKET')
    base_url = Column(String(500), comment='基础URL')


class APICollectionModel(Base):
    """API集合模型"""
    __tablename__ = 'api_collections'
    
    api_project_id = Column(BigInteger, nullable=False, comment='API项目ID', index=True)
    name = Column(String(200), nullable=False, comment='集合名称')
    description = Column(Text, comment='集合描述')
    parent_id = Column(BigInteger, comment='父级集合ID', index=True)
    order_num = Column(Integer, default=0, comment='排序')


class APIRequestModel(Base):
    """API请求模型"""
    __tablename__ = 'api_requests'
    
    collection_id = Column(BigInteger, nullable=False, comment='所属集合ID', index=True)
    name = Column(String(200), nullable=False, comment='请求名称')
    description = Column(Text, comment='请求描述')
    request_type = Column(String(20), default='HTTP', comment='请求类型: HTTP/WEBSOCKET')
    method = Column(String(10), default='GET', comment='请求方法')
    url = Column(Text, nullable=False, comment='请求URL')
    headers = Column(JSON, comment='请求头')
    params = Column(JSON, comment='URL参数')
    body = Column(JSON, comment='请求体')
    cookies = Column(JSON, comment='Cookies')
    auth = Column(JSON, comment='认证信息')
    pre_request_script = Column(JSON, comment='前置操作列表')
    post_request_script = Column(JSON, comment='后置操作列表')
    assertions = Column(JSON, comment='断言规则')
    verify_ssl = Column(Boolean, default=True, comment='SSL证书验证')
    follow_redirects = Column(Boolean, default=True, comment='自动跟随重定向')
    timeout = Column(Integer, default=30000, comment='超时时间(毫秒)')
    order_num = Column(Integer, default=0, comment='排序')


class APISSLCertificateModel(Base):
    """SSL证书模型"""
    __tablename__ = 'api_ssl_certificate'
    
    project_id = Column(BigInteger, nullable=False, comment='关联项目ID', index=True)
    name = Column(String(200), nullable=False, comment='证书名称')
    cert_type = Column(String(50), nullable=False, comment='证书类型: CA/CLIENT')
    domain = Column(String(500), comment='适用域名（支持通配符）', index=True)
    ca_cert = Column(Text, comment='CA证书内容（PEM格式）')
    client_cert = Column(Text, comment='客户端证书内容（CRT/PEM格式）')
    client_key = Column(Text, comment='客户端私钥内容（KEY/PEM格式）')
    passphrase = Column(String(500), comment='私钥密码（加密存储）')
    is_active = Column(Boolean, default=True, comment='是否启用')
    description = Column(Text, comment='描述')


class APIEnvironmentModel(Base):
    """API环境变量模型"""
    __tablename__ = 'api_environments'
    
    project_id = Column(BigInteger, nullable=False, comment='关联项目ID', index=True)
    name = Column(String(200), nullable=False, comment='环境名称')
    scope = Column(String(10), default='LOCAL', comment='作用域: GLOBAL/LOCAL')
    variables = Column(JSON, comment='环境变量')
    is_active = Column(Boolean, default=False, comment='是否激活')


class APIRequestHistoryModel(Base):
    """API请求历史模型"""
    __tablename__ = 'api_request_histories'
    __table_args__ = {'extend_existing': True}
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    request_id = Column(BigInteger, nullable=False, comment='关联请求ID', index=True)
    environment_id = Column(BigInteger, comment='使用环境ID')
    environment_name = Column(String(200), comment='环境名称')
    request_data = Column(JSON, comment='请求数据')
    response_data = Column(JSON, comment='响应数据')
    status_code = Column(Integer, comment='状态码')
    response_time = Column(Float, comment='响应时间(ms)')
    error_message = Column(Text, comment='错误信息')
    assertions_results = Column(JSON, comment='断言结果')
    assertions_passed = Column(Boolean, comment='断言是否通过')
    executed_by = Column(BigInteger, nullable=False, comment='执行者ID')
    executed_at = Column(DateTime, comment='执行时间', index=True)


class APITestSuiteModel(Base):
    """API测试套件模型"""
    __tablename__ = 'api_test_suites'
    
    api_project_id = Column(BigInteger, nullable=False, comment='API项目ID', index=True)
    name = Column(String(200), nullable=False, comment='套件名称')
    description = Column(Text, comment='套件描述')
    environment_id = Column(BigInteger, comment='执行环境ID')


class APITestSuiteRequestModel(Base):
    """套件请求关联模型"""
    __tablename__ = 'api_test_suite_requests'
    
    test_suite_id = Column(BigInteger, nullable=False, comment='测试套件ID')
    request_id = Column(BigInteger, nullable=False, comment='API请求ID')
    order_num = Column(Integer, default=0, comment='执行顺序')
    assertions = Column(JSON, comment='断言规则')


class APITestExecutionModel(Base):
    """API测试执行模型"""
    __tablename__ = 'api_test_executions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    test_suite_id = Column(BigInteger, nullable=False, comment='测试套件ID', index=True)
    status = Column(String(20), default='PENDING', comment='执行状态', index=True)
    start_time = Column(DateTime, comment='开始时间')
    end_time = Column(DateTime, comment='结束时间')
    total_requests = Column(Integer, default=0, comment='总请求数')
    passed_requests = Column(Integer, default=0, comment='通过请求数')
    failed_requests = Column(Integer, default=0, comment='失败请求数')
    results = Column(JSON, comment='执行结果')
    executed_by = Column(BigInteger, nullable=False, comment='执行者ID')



class APIPublicScriptModel(Base):
    """公共脚本模型"""
    __tablename__ = 'api_public_scripts'
    
    project_id = Column(BigInteger, nullable=False, comment='关联项目ID', index=True)
    name = Column(String(200), nullable=False, comment='脚本名称')
    description = Column(Text, comment='脚本描述')
    script_type = Column(String(20), default='javascript', comment='脚本类型: javascript/python')
    script_content = Column(Text, nullable=False, comment='脚本内容')
    category = Column(String(50), comment='分类', index=True)
    is_active = Column(Boolean, default=True, comment='是否启用')


class APIDatabaseConfigModel(Base):
    """数据库连接配置模型"""
    __tablename__ = 'api_database_configs'
    
    project_id = Column(BigInteger, nullable=False, comment='关联项目ID', index=True)
    name = Column(String(200), nullable=False, comment='连接名称')
    description = Column(Text, comment='连接描述')
    db_type = Column(String(20), nullable=False, comment='数据库类型: mysql/postgresql/mongodb/redis')
    host = Column(String(200), nullable=False, comment='主机地址')
    port = Column(Integer, nullable=False, comment='端口')
    database_name = Column(String(200), comment='数据库名')
    username = Column(String(200), comment='用户名')
    password = Column(String(500), comment='密码（加密存储）')
    connection_params = Column(JSON, comment='其他连接参数')
    is_active = Column(Boolean, default=True, comment='是否启用')
