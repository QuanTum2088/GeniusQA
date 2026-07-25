#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, BigInteger, UniqueConstraint
from sqlalchemy.sql import func
from app.core.db_base import Base


class AppMenuModel(Base):
    """脚本菜单（目录树）"""

    __tablename__ = "app_menus"
    __table_args__ = {"comment": "APP自动化菜单表"}

    name = Column(String(255), nullable=False, unique=True, comment="名称")
    pid = Column(BigInteger, nullable=False, comment="父id")
    type = Column(Integer, nullable=False, comment="类型")
    user_id = Column(BigInteger, nullable=False, comment="用户ID")


class AppScriptModel(Base):
    """脚本内容"""

    __tablename__ = "app_scripts"
    __table_args__ = {"comment": "APP自动化脚本表"}

    script = Column(JSON, nullable=False, comment="脚本")
    menu_id = Column(BigInteger, nullable=False, unique=True, comment="菜单ID")
    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class AppResultModel(Base):
    """单步执行结果（每个脚本步骤/断言等都会写一条）"""

    __tablename__ = "app_results"
    __table_args__ = {"comment": "APP自动化执行结果表"}

    device = Column(String(255), nullable=False, comment="设备")
    result_id = Column(String(255), nullable=False, comment="结果id")
    name = Column(String(255), nullable=False, comment="脚本名称")
    status = Column(Integer, nullable=False, comment="状态 0失败 1成功 2进行中(兼容旧)")
    log = Column(Text, nullable=True, comment="详情")
    assert_value = Column(JSON, nullable=True, comment="断言详情")
    before_img = Column(Text, nullable=True, comment="执行前截图地址")
    after_img = Column(Text, nullable=True, comment="执行后截图地址")
    video = Column(Text, nullable=True, comment="视频地址")
    performance = Column(JSON, nullable=True, comment="实时性能")
    menu_id = Column(BigInteger, nullable=False, comment="菜单ID")
    create_time = Column(DateTime, server_default=func.now(), comment="执行时间")
    user_id = Column(BigInteger, nullable=False, comment="用户ID")


class AppResultListModel(Base):
    """一次任务执行的汇总（任务名、设备列表、脚本列表、执行统计等）"""

    __tablename__ = "app_result_lists"
    __table_args__ = {"comment": "APP自动化结果汇总表"}

    task_name = Column(String(255), nullable=False, comment="任务名称")
    device_list = Column(JSON, nullable=False, comment="设备列表")
    result_id = Column(String(255), unique=True, nullable=False, comment="结果id")
    script_list = Column(JSON, nullable=False, comment="脚本列表")
    script_status = Column(JSON, nullable=False, comment="脚本执行情况")
    start_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    end_time = Column(DateTime, nullable=True, comment="更新时间")
    user_id = Column(BigInteger, nullable=False, comment="用户ID")


class AppAirtestImageModel(Base):
    """Airtest 图像库"""

    __tablename__ = "app_airtest_images"
    __table_args__ = {"comment": "APP自动化 Airtest 图像库"}

    file_name = Column(String(255), nullable=False, comment="图片名称")
    file_path = Column(Text, nullable=False, comment="图片地址")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    menu_id = Column(BigInteger, nullable=True, comment="所属菜单")


class AppUiTestRunServerModel(Base):
    """Appium 执行服务器"""

    __tablename__ = "app_ui_test_run_server"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_app_ui_test_run_server_user_name"),
        {"comment": "APP测试运行服务器表"},
    )

    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    name = Column(String(255), nullable=False, comment="服务器名称")
    num = Column(Integer, nullable=True, default=0, comment="排序序号")
    server_os = Column(String(16), nullable=True, comment="系统类型 windows/mac/linux")
    ip = Column(String(64), nullable=False, comment="IP")
    port = Column(String(16), nullable=False, default="4723", comment="端口")
    appium_version = Column(String(16), nullable=False, default="2.x", comment="Appium 主版本 1.x/2.x/3.x")
    status = Column(Integer, nullable=False, default=0, comment="连通性 0未检测 1失败 2成功")


class AppUiPageModel(Base):
    """APP页面"""

    __tablename__ = "app_ui_pages"
    __table_args__ = (
        UniqueConstraint("user_id", "module_menu_id", "name", name="uq_app_ui_pages_user_module_name"),
        {"comment": "APP UI 页面表"},
    )

    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    module_menu_id = Column(BigInteger, nullable=False, comment="所属模块=app_menus 文件夹 id")
    name = Column(String(255), nullable=False, comment="页面名称")
    num = Column(Integer, nullable=True, default=0, comment="排序")
    remark = Column(Text, nullable=True, comment="备注")
    activity = Column(String(512), nullable=True, comment="Activity / 页面标识")
    package_name = Column(String(255), nullable=True, comment="包名（可选）")


class AppUiElementModel(Base):
    """页面下定位元素"""

    __tablename__ = "app_ui_elements"
    __table_args__ = {"comment": "APP UI 元素表"}

    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    page_id = Column(BigInteger, nullable=False, comment="页面 id")
    name = Column(String(255), nullable=False, comment="元素名称")
    locate_type = Column(String(64), nullable=False, default="id", comment="定位类型 id/xpath/accessibility_id 等")
    locate_value = Column(Text, nullable=False, comment="定位值")
    num = Column(Integer, nullable=True, default=0, comment="排序")


class AppUiTestRunPhoneModel(Base):
    """运行终端"""

    __tablename__ = "app_ui_test_run_phone"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_app_ui_test_run_phone_user_name"),
        {"comment": "APP测试运行终端表"},
    )

    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    name = Column(String(255), nullable=False, comment="设备别名")
    num = Column(Integer, nullable=True, default=0, comment="排序序号")
    phone_os = Column(String(16), nullable=True, comment="Android / ios")
    os_version = Column(String(255), nullable=True, comment="系统版本")
    device_id = Column(String(255), nullable=False, comment="adb devices / UDID")
    extends = Column(JSON, nullable=True, comment="扩展字段")
    screen = Column(String(64), nullable=True, comment="分辨率")