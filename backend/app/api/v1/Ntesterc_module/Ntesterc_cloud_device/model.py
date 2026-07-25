"""
云真机设备模块数据模型
"""

from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, BigInteger
from sqlalchemy.sql import func
from app.core.db_base import Base


class AppDevice(Base):
    """云真机设备表"""

    __tablename__ = "app_devices"
    __table_args__ = {"comment": "云真机设备表"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    device_name = Column(String(255), nullable=False, comment="设备名称")
    device_id = Column(String(255), nullable=False, comment="设备ID")
    device_status = Column(Integer, nullable=False, default=1, comment="设备状态: 1-空闲, 2-使用中, 3-离线")
    device_type = Column(String(255), nullable=False, comment="设备类型")
    device_version = Column(String(255), nullable=True, comment="设备版本")
    device_info = Column(JSON, nullable=True, comment="设备详细信息")
    file_path = Column(Text, nullable=False, comment="设备图片路径")
    device_description = Column(Text, nullable=True, comment="设备描述")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    creation_date = Column(DateTime, nullable=True, comment="创建时间")
    created_by = Column(Integer, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, nullable=True, comment="更新时间")
    updated_by = Column(Integer, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, nullable=False, default=1, comment="是否删除, 0 删除 1 非删除")
    trace_id = Column(String(255), nullable=True, comment="trace_id")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")


class AppDeviceLog(Base):
    """设备使用日志表"""

    __tablename__ = "app_device_logs"
    __table_args__ = {"comment": "设备使用日志表"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    device_id = Column(Integer, nullable=False, comment="设备ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    start_time = Column(DateTime, server_default=func.now(), comment="开始使用时间")
    end_time = Column(DateTime, nullable=True, comment="结束使用时间")
    creation_date = Column(DateTime, nullable=True, comment="创建时间")
    created_by = Column(Integer, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, nullable=True, comment="更新时间")
    updated_by = Column(Integer, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, nullable=False, default=1, comment="是否删除, 0 删除 1 非删除")
    trace_id = Column(String(255), nullable=True, comment="trace_id")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")


class AppDeviceInstall(Base):
    """设备APP安装历史表"""

    __tablename__ = "app_device_installs"
    __table_args__ = {"comment": "设备APP安装历史表"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    apk_name = Column(Text, nullable=False, comment="APK名称")
    apk_path = Column(Text, nullable=False, comment="APK路径")
    device_id = Column(Integer, nullable=False, comment="设备ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    create_time = Column(DateTime, server_default=func.now(), comment="安装时间")
    creation_date = Column(DateTime, nullable=True, comment="创建时间")
    created_by = Column(Integer, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, nullable=True, comment="更新时间")
    updated_by = Column(Integer, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, nullable=False, default=1, comment="是否删除, 0 删除 1 非删除")
    trace_id = Column(String(255), nullable=True, comment="trace_id")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")


class AppDeviceLogList(Base):
    """设备日志列表"""

    __tablename__ = "app_device_log_lists"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键")
    name = Column(String(255), nullable=False, comment="名称")
    together_id = Column(Integer, nullable=False, comment="关联ID")
    creation_date = Column(DateTime, nullable=True, comment="创建时间")
    created_by = Column(BigInteger, nullable=True, comment="创建人ID")
    updation_date = Column(DateTime, nullable=True, comment="更新时间")
    updated_by = Column(BigInteger, nullable=True, comment="更新人ID")
    enabled_flag = Column(Integer, nullable=False, comment="是否删除, 0 删除 1 非删除")
    trace_id = Column(String(255), nullable=True, comment="trace_id")
