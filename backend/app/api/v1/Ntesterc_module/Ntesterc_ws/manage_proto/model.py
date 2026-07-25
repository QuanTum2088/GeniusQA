from sqlalchemy import Column, String, Text, Integer, BigInteger, DateTime, JSON
from sqlalchemy.sql.schema import Index, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean

from app.core.db_base import Base


class ProtoPackage(Base):
    """协议包主表 - 存储上传的 .proto 文件及生成的 Python 文件信息"""
    __tablename__ = "ws_proto_packages"
    __table_args__ = {"comment": "协议包主表，一条记录对应一个上传的 .proto 文件"}

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    # ---- 文件基础信息 ----
    proto_name = Column(String(100), nullable=False, comment='协议文件名，如 login.proto')
    syntax = Column(String(10), nullable=True, default='proto3', comment='协议语法版本：proto2/proto3')
    package_name = Column(String(100), nullable=True, comment='proto 文件头的 package 声明，如 client_proto')
    module_name = Column(String(100), nullable=False, comment='Python 导入模块名，如 login_pb2')
    file_hash = Column(String(64), nullable=True, comment='文件MD5指纹，用于检测协议内容是否变更')
    version = Column(String(20), nullable=False, comment='协议版本号，如 v1.0')

    # ---- 存储路径 ----
    file_path = Column(String(255), nullable=False, comment='原始 .proto 文件存放路径')
    py_file_path = Column(String(255), nullable=False, comment='protoc 生成的 *_pb2.py 文件绝对路径')

    # ---- 业务审计 ----
    status = Column(Integer, nullable=False, default=1, comment='记录状态：1-启用，0-已废弃')
    remark = Column(Text, nullable=True, comment='备注/协议包描述')


class ProtoInterface(Base):
    """
    接口路由表 - 一条记录代表一个完整的 API 接口（请求 + 响应）
    """
    __tablename__ = 'ws_proto_interfaces'
    __table_args__ = (
        Index('idx_package_id', 'package_id'),
        Index('idx_msg_id', 'req_msg_id', 'resp_msg_id'),
        {'comment': '接口路由表，每个 API 接口（请求+响应）对应一行记录'},
    )

    # ---- 主外键 ----
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    package_id = Column(BigInteger, ForeignKey('ws_proto_packages.id', ondelete='CASCADE'),
                        nullable=False, comment='关联协议包主表ID')

    # ---- 接口路由核心信息 ----
    req_name = Column(String(50), nullable=False, comment='业务操作名，如：Login')
    desc_name = Column(String(50), nullable=False, comment='业务操作描述名称，如：用户登录')
    req_msg_id = Column(Integer, nullable=False, comment='请求消息ID，如：901')
    req_class = Column(String(50), nullable=False, comment='请求结构体名称，如：LoginReq')
    resp_msg_id = Column(Integer, nullable=False, comment='响应消息ID，如：902')
    resp_class = Column(String(50), nullable=False, comment='响应结构体名称，如：LoginResp')

    # ---- 版本与指纹 ----
    current_version = Column(String(20), nullable=False, default='v1.0', comment='当前生效的版本号')
    req_src_md5 = Column(String(32), nullable=True, comment='请求结构体MD5指纹（基于字段编号/类型/名称生成，忽略注释空格）')
    resp_src_md5 = Column(String(32), nullable=True, comment='响应结构体MD5指纹（基于字段编号/类型/名称生成，忽略注释空格）')

    # ---- 展示与体验优化 ----
    req_example = Column(Text, nullable=True, comment='请求体示例（JSON格式），供一键复制填充')
    resp_example = Column(Text, nullable=True, comment='响应体示例（JSON格式），供断言参考')
    enum_context = Column(JSON, nullable=True, comment='该接口涉及的枚举定义汇总，如 {"gender": {"MALE": 1, "FEMALE": 2}}')

    # ---- 业务运维字段 ----
    status = Column(Integer, nullable=False, default=1, comment='接口状态：1-启用，0-已废弃')
    timeout = Column(Integer, nullable=True, comment='期望响应超时时间（秒），为空则取全局默认值')

    # ---- 备注说明 ----
    desc = Column(Text, nullable=True, comment='接口说明/描述，可从 proto 注释提取')


class InterfaceFieldSchema(Base):
    """
    字段快照表 - 扁平化存储请求/响应字段详情，支持版本隔离
    """
    __tablename__ = 'ws_interface_fields'
    __table_args__ = (
        Index('idx_interface_version', 'interface_id', 'version'),
        Index('idx_interface_category', 'interface_id', 'field_category'),
        {'comment': '请求、响应字段快照表，将嵌套 message 扁平化为多行记录，每行一个字段'},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    interface_id = Column(BigInteger, ForeignKey('ws_proto_interfaces.id', ondelete='CASCADE'), nullable=False, comment='关联接口ID')
    version = Column(String(20), nullable=False, comment='版本号，如 v1.0 / v2.0，支持多版本共存')
    field_category = Column(String(10), nullable=False, comment='字段类别：request 表示请求参数，response 表示响应字段')
    field_path = Column(String(255), nullable=False, comment='扁平化路径，嵌套用 . 分隔，如 basic_info.user_name')
    field_type = Column(String(30), nullable=False, comment='映射后的 Python 类型：str/int/bool/enum/bytes/double')
    is_required = Column(Boolean, nullable=False, default=True, comment='是否必填：Proto3 中未标 optional 且非 repeated 即为必填')
    is_repeated = Column(Boolean, nullable=False, default=False, comment='是否为数组类型（repeated 字段）')
    enum_mapping = Column(JSON, nullable=True, comment="仅当 field_type='enum' 时存储映射关系，如 {'MALE': 1, 'FEMALE': 2}")
    field_desc = Column(String(255), nullable=True, comment='字段注释说明，从 proto 注释中提取')


class ProtoChangeLog(Base):
    """
    协议变更审计日志表 - 记录每次版本升级的字段差异
    """
    __tablename__ = 'ws_proto_change_logs'
    __table_args__ = (
        Index('idx_interface_version', 'interface_id', 'from_version', 'to_version'),
        {'comment': '协议变更审计日志，记录字段级差异，供审核人员确认'},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    interface_id = Column(BigInteger, ForeignKey('ws_proto_interfaces.id', ondelete='CASCADE'), nullable=False, comment='关联接口ID')
    from_version = Column(String(20), nullable=False, comment='变更前版本号')
    to_version = Column(String(20), nullable=False, comment='变更后版本号')
    diff_content = Column(JSON, nullable=False, comment="结构化差异内容：{'added': [...], 'removed': [...], 'modified': [...]}")
    review_status = Column(String(20), nullable=False, default='pending', comment='审核状态：pending / approved / rejected')
    reviewer = Column(String(50), nullable=True, comment='审核人')
    review_comment = Column(Text, nullable=True, comment='审核备注/意见')
