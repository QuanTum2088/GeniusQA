#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, BigInteger, Float, Date, DECIMAL
from sqlalchemy.sql import func
from app.core.db_base import Base


class RequirementDocumentModel(Base):
    """需求文档表"""
    
    __tablename__ = "requirement_documents"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    project_id = Column(BigInteger, nullable=False, comment="关联项目ID")
    title = Column(String(200), nullable=False, comment="文档标题")
    file_path = Column(String(500), nullable=False, comment="文档文件路径")
    document_type = Column(String(10), nullable=False, comment="文档类型: pdf/docx/txt/md")
    status = Column(String(20), default="uploaded", comment="状态: uploaded/analyzing/analyzed/failed")
    file_size = Column(Integer, nullable=True, comment="文件大小(bytes)")
    extracted_text = Column(Text, nullable=True, comment="提取的文本内容")
    uploaded_by = Column(BigInteger, nullable=False, comment="上传者ID")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(BigInteger, nullable=True, comment="创建人ID")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class RequirementAnalysisModel(Base):
    """需求分析表"""
    
    __tablename__ = "requirement_analyses"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    document_id = Column(BigInteger, nullable=True, comment="文档ID")
    analysis_result = Column(JSON, nullable=True, comment="分析结果")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    created_by = Column(BigInteger, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class BusinessRequirementModel(Base):
    """业务需求表"""
    
    __tablename__ = "business_requirements"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    title = Column(String(200), nullable=False, comment="需求标题")
    description = Column(Text, nullable=True, comment="需求描述")
    project_id = Column(BigInteger, nullable=True, comment="项目ID")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    created_by = Column(BigInteger, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class GeneratedTestCaseModel(Base):
    """生成的测试用例表"""
    
    __tablename__ = "generated_test_cases"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    case_name = Column(String(200), nullable=False, comment="用例名称")
    case_content = Column(Text, nullable=True, comment="用例内容")
    task_id = Column(BigInteger, nullable=True, comment="任务ID")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    created_by = Column(BigInteger, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class TestCaseGenerationTaskModel(Base):
    """测试用例生成任务表"""
    
    __tablename__ = "testcase_generation_tasks"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    project_id = Column(BigInteger, nullable=True, comment="关联项目ID")
    task_id = Column(String(50), nullable=False, unique=True, comment="任务ID")
    title = Column(String(200), nullable=False, comment="任务标题")
    requirement_text = Column(Text, nullable=False, comment="需求描述")
    status = Column(String(20), default="pending", comment="状态")
    progress = Column(Integer, default=0, comment="进度百分比")
    output_mode = Column(String(10), default="stream", comment="输出模式: stream/complete")
    stream_buffer = Column(Text, nullable=True, comment="流式输出缓冲区")
    stream_position = Column(Integer, default=0, comment="流式输出位置")
    last_stream_update = Column(DateTime, nullable=True, comment="最后流式更新时间")
    writer_model_config_id = Column(BigInteger, nullable=True, comment="编写模型配置ID")
    reviewer_model_config_id = Column(BigInteger, nullable=True, comment="评审模型配置ID")
    writer_prompt_config_id = Column(BigInteger, nullable=True, comment="编写提示词配置ID")
    reviewer_prompt_config_id = Column(BigInteger, nullable=True, comment="评审提示词配置ID")
    generated_test_cases = Column(Text, nullable=True, comment="生成的测试用例")
    review_feedback = Column(Text, nullable=True, comment="评审反馈")
    final_test_cases = Column(Text, nullable=True, comment="最终测试用例")
    generation_log = Column(Text, nullable=True, comment="生成日志")
    error_message = Column(Text, nullable=True, comment="错误信息")
    created_by = Column(BigInteger, nullable=False, comment="创建者ID")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    is_saved_to_records = Column(Integer, default=0, comment="是否已保存到记录")
    saved_at = Column(DateTime, nullable=True, comment="保存到记录时间")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class AIModelConfigModel(Base):
    """AI模型配置表"""
    
    __tablename__ = "ai_model_configs"
    __table_args__ = {"comment": "AI模型配置表"}
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="配置名称")
    model_type = Column(String(20), nullable=False, comment="模型类型: deepseek/qwen/siliconflow/zhipu/other")
    role = Column(String(20), nullable=False, comment="角色: writer/reviewer/browser_use_text")
    api_key = Column(String(200), nullable=True, comment="API Key")
    base_url = Column(String(500), nullable=False, comment="API Base URL")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    max_tokens = Column(Integer, default=4096, comment="最大Token数")
    temperature = Column(Float, default=0.7, comment="温度参数")
    top_p = Column(Float, default=0.9, comment="Top P参数")
    is_active = Column(Integer, default=1, comment="是否启用")
    created_by = Column(BigInteger, nullable=False, comment="创建者ID")
    llm_config_id = Column(BigInteger, nullable=True, comment="关联的LLM配置ID")
    creation_date = Column(DateTime, server_default=func.now())
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now())
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    updated_by = Column(BigInteger, nullable=True)
    trace_id = Column(String(255), nullable=True)


class PromptConfigModel(Base):
    """提示词配置表"""
    
    __tablename__ = "prompt_configs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    name = Column(String(100), nullable=False, comment="配置名称")
    prompt_type = Column(String(20), nullable=False, comment="提示词类型: writer/reviewer")
    content = Column(Text, nullable=False, comment="提示词内容")
    is_active = Column(Integer, default=1, comment="是否启用")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    created_by = Column(BigInteger, nullable=False, comment="创建人ID")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class GenerationConfigModel(Base):
    """生成配置表"""
    
    __tablename__ = "generation_configs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    config_name = Column(String(100), nullable=False, comment="配置名称")
    config_data = Column(JSON, nullable=True, comment="配置数据")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    created_by = Column(BigInteger, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class AICaseModel(Base):
    """AI智能浏览器用例表"""
    
    __tablename__ = "ai_cases"
    __table_args__ = {"comment": "AI智能浏览器用例表"}
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ui_project_id = Column(BigInteger, nullable=True, comment="所属UI项目ID")
    source_project_id = Column(BigInteger, nullable=True, comment="来源项目ID（测试管理项目）")
    source_module_id = Column(BigInteger, nullable=True, comment="来源模块ID（测试管理模块）")
    name = Column(String(200), nullable=False, comment="用例名称")
    description = Column(Text, nullable=True, comment="描述")
    task_description = Column(Text, nullable=False, comment="任务描述")
    status = Column(String(20), default="active", comment="状态: draft-草稿, active-激活, archived-归档")
    source_type = Column(String(20), default="manual", comment="来源类型: manual-手动创建, import-Excel导入, testcase-测试用例")
    priority = Column(String(10), default="P2", comment="优先级: P0-最高, P1-高, P2-中, P3-低")
    precondition = Column(Text, nullable=True, comment="前置条件")
    test_steps = Column(JSON, nullable=True, comment="测试步骤")
    expected_result = Column(Text, nullable=True, comment="预期结果")
    execution_mode = Column(String(20), default="headless", comment="执行模式")
    timeout = Column(Integer, default=300, comment="超时时间(秒)")
    created_by = Column(BigInteger, nullable=True, comment="创建者ID")
    creation_date = Column(DateTime, server_default=func.now())
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now())
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    updated_by = Column(BigInteger, nullable=True)
    trace_id = Column(String(255), nullable=True)


class AIExecutionRecordModel(Base):
    """AI执行记录表"""
    
    __tablename__ = "ai_execution_records"
    __table_args__ = {"comment": "AI执行记录表"}
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ui_project_id = Column(BigInteger, nullable=True, comment="所属UI项目ID")
    ai_case_id = Column(BigInteger, nullable=True, comment="关联AI用例ID")
    case_name = Column(String(200), nullable=False, comment="用例名称快照")
    task_description = Column(Text, nullable=True, comment="任务描述")
    execution_mode = Column(String(20), default="text", comment="执行模式")
    status = Column(String(20), default="pending", comment="执行状态")
    start_time = Column(DateTime, server_default=func.now(), comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    duration = Column(Float, nullable=True, comment="执行时长(秒)")
    logs = Column(Text, nullable=True, comment="执行日志")
    error_message = Column(Text, nullable=True, comment="错误信息")
    steps_completed = Column(JSON, nullable=True, comment="已完成步骤")
    planned_tasks = Column(JSON, nullable=True, comment="规划任务")
    executed_by = Column(BigInteger, nullable=True, comment="执行人ID")
    gif_path = Column(String(500), nullable=True, comment="GIF录制路径")
    screenshots_sequence = Column(JSON, nullable=True, comment="截图序列")
    creation_date = Column(DateTime, server_default=func.now())
    created_by = Column(BigInteger, nullable=True, comment="创建者ID")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now())
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    updated_by = Column(BigInteger, nullable=True)
    trace_id = Column(String(255), nullable=True)
    total_tokens = Column(Integer, default=0, comment="Token总使用量")
    prompt_tokens = Column(Integer, default=0, comment="提示词Token数")
    completion_tokens = Column(Integer, default=0, comment="完成Token数")
    api_calls = Column(Integer, default=0, comment="API调用次数")


class AITestSuiteModel(Base):
    """AI测试套件表"""
    
    __tablename__ = "ai_test_suites"
    __table_args__ = {"comment": "AI测试套件表"}
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    name = Column(String(200), nullable=False, comment="套件名称")
    description = Column(Text, nullable=True, comment="套件描述")
    project_id = Column(Integer, nullable=False, comment="关联项目ID")
    status = Column(String(20), default="active", comment="状态：active/archived")
    created_by = Column(Integer, nullable=True, comment="创建人ID")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_by = Column(Integer, nullable=True, comment="更新人ID")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class AITestSuiteModuleModel(Base):
    """AI测试套件模块关联表"""
    
    __tablename__ = "ai_test_suite_modules"
    __table_args__ = {"comment": "AI测试套件模块关联表"}
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    suite_id = Column(Integer, nullable=False, comment="套件ID")
    module_id = Column(Integer, nullable=False, comment="模块ID")
    module_name = Column(String(200), nullable=True, comment="模块名称（冗余字段，方便查询）")
    execution_order = Column(Integer, nullable=False, comment="执行顺序")
    created_by = Column(Integer, nullable=True, comment="创建人ID")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(Integer, nullable=True, comment="更新人ID")


class FigmaConfigModel(Base):
    """Figma配置表"""
    
    __tablename__ = "figma_configs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    config_name = Column(String(100), nullable=False, comment="配置名称")
    api_token = Column(String(200), nullable=True, comment="Figma API Token")
    file_key = Column(String(200), nullable=True, comment="Figma文件Key")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    created_by = Column(BigInteger, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class FigmaExtractionTaskModel(Base):
    """Figma提取任务表"""
    
    __tablename__ = "figma_extraction_tasks"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    task_name = Column(String(200), nullable=False, comment="任务名称")
    status = Column(String(20), nullable=True, comment="任务状态")
    result = Column(JSON, nullable=True, comment="提取结果")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    created_by = Column(BigInteger, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class FigmaAPICallLogModel(Base):
    """Figma API调用日志表"""
    
    __tablename__ = "figma_api_call_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    api_endpoint = Column(String(200), nullable=True, comment="API端点")
    request_data = Column(JSON, nullable=True, comment="请求数据")
    response_data = Column(JSON, nullable=True, comment="响应数据")
    status_code = Column(Integer, nullable=True, comment="状态码")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    created_by = Column(BigInteger, nullable=True, comment="创建人ID")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class FigmaFileCacheModel(Base):
    """Figma文件缓存表"""
    
    __tablename__ = "figma_file_cache"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    file_key = Column(String(200), nullable=False, comment="Figma文件Key")
    cache_data = Column(JSON, nullable=True, comment="缓存数据")
    last_updated = Column(DateTime, nullable=True, comment="最后更新时间")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    created_by = Column(BigInteger, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class AITestReportModel(Base):
    """AI测试报告表"""
    
    __tablename__ = "ai_test_reports"
    __table_args__ = {"comment": "AI测试报告表"}
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键")
    report_id = Column(String(100), nullable=False, unique=True, comment="报告ID")
    report_name = Column(String(200), nullable=False, comment="报告名称")
    project_id = Column(BigInteger, nullable=True, comment="项目ID")
    project_name = Column(String(200), nullable=True, comment="项目名称")
    start_date = Column(Date, nullable=True, comment="开始日期")
    end_date = Column(Date, nullable=True, comment="结束日期")
    date_range = Column(String(100), nullable=True, comment="时间范围")
    status = Column(String(50), default="generated", comment="报告状态")
    total_cases = Column(Integer, default=0, comment="总用例数")
    total_executions = Column(Integer, default=0, comment="总执行次数")
    success_count = Column(Integer, default=0, comment="成功次数")
    failed_count = Column(Integer, default=0, comment="失败次数")
    success_rate = Column(DECIMAL(5, 2), default=0.00, comment="成功率")
    total_duration = Column(DECIMAL(10, 2), default=0.00, comment="总执行时长(秒)")
    avg_duration = Column(DECIMAL(10, 2), default=0.00, comment="平均时长(秒)")
    total_tokens = Column(BigInteger, default=0, comment="总Token使用量")
    report_data = Column(JSON, nullable=True, comment="报告详细数据")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    created_by = Column(BigInteger, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, default=1, comment="是否删除, 0 删除 1 非删除")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class TestCaseTemplateModel(Base):
    """测试用例模板配置表"""
    
    __tablename__ = "testcase_templates"
    __table_args__ = {"comment": "测试用例模板配置表"}
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(Text, nullable=True, comment="模板描述")
    template_type = Column(String(20), default="ui", comment="模板类型: ui/api/performance/main")
    field_mapping = Column(JSON, nullable=False, comment="字段映射配置")
    is_default = Column(Integer, default=0, comment="是否默认模板")
    is_active = Column(Integer, default=1, comment="是否启用")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    created_by = Column(BigInteger, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")


class AITestSuiteExecutionModel(Base):
    """AI测试套件执行记录模型"""
    
    __tablename__ = "ai_test_suite_executions"
    __table_args__ = {"comment": "AI测试套件执行记录表"}
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    suite_id = Column(Integer, nullable=False, comment="套件ID")
    suite_name = Column(String(200), nullable=True, comment="套件名称（冗余字段）")
    execution_name = Column(String(200), nullable=True, comment="执行名称")
    execution_mode = Column(String(20), default="headless", comment="执行模式：headless/headed")
    status = Column(String(20), default="running", comment="状态：running/completed/failed")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    duration = Column(DECIMAL(10, 2), comment="执行时长（秒）")
    total_modules = Column(Integer, default=0, comment="总模块数")
    completed_modules = Column(Integer, default=0, comment="已完成模块数")
    failed_modules = Column(Integer, default=0, comment="失败模块数")
    total_cases = Column(Integer, default=0, comment="总用例数")
    passed_cases = Column(Integer, default=0, comment="通过用例数")
    failed_cases = Column(Integer, default=0, comment="失败用例数")
    error_message = Column(Text, comment="错误信息")
    created_by = Column(Integer, nullable=True, comment="创建人ID")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(Integer, nullable=True, comment="更新人ID")


class AITestSuiteModuleExecutionModel(Base):
    """AI测试套件模块执行记录模型"""
    
    __tablename__ = "ai_test_suite_module_executions"
    __table_args__ = {"comment": "AI测试套件模块执行记录表"}
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    suite_execution_id = Column(Integer, nullable=False, comment="套件执行记录ID")
    module_id = Column(Integer, nullable=False, comment="模块ID")
    module_name = Column(String(200), nullable=True, comment="模块名称")
    execution_order = Column(Integer, nullable=True, comment="执行顺序")
    status = Column(String(20), default="pending", comment="状态：pending/running/completed/failed")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    duration = Column(DECIMAL(10, 2), comment="执行时长（秒）")
    total_cases = Column(Integer, default=0, comment="总用例数")
    passed_cases = Column(Integer, default=0, comment="通过用例数")
    failed_cases = Column(Integer, default=0, comment="失败用例数")
    error_message = Column(Text, comment="错误信息")
    created_by = Column(Integer, nullable=True, comment="创建人ID")
    creation_date = Column(DateTime, server_default=func.now(), comment="创建时间")
    enabled_flag = Column(Integer, default=1, comment="启用标志")
    trace_id = Column(String(255), nullable=True, comment="trace_id")
    updation_date = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(Integer, nullable=True, comment="更新人ID")