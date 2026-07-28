from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config, pool
from alembic import context

# 添加项目根目录到 Python 路径（从 app/alembic 向上两级）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 导入配置
from config import config as app_config

# this is the Alembic Config object
config = context.config

# 设置数据库 URL（从 .env 读取）
# % 在 configparser 中是插值字符，需转义为 %% 避免解析错误（如密码含 %40 等编码字符）
config.set_main_option('sqlalchemy.url', app_config.DATABASE_URI_SYNC.replace('%', '%%'))

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 导入模型的 metadata
target_metadata = None

try:
    # 导入 Base 和所有模型
    from app.core.db_base import Base
    target_metadata = Base.metadata
    

    from app.api.v1.system.permission import rbac_model
    from app.api.v1.Ntesterc_module.Ntesterc_task_scheduler import celery_beat_model
    from app.api.v1.Ntesterc_module.Ntesterc_project import legacy_api_model

    # 导入 AI 模型
    from app.api.v1.Ntesterc_module.Ntesterc_ai.conversation.model import ConversationModel
    from app.api.v1.Ntesterc_module.Ntesterc_ai.conversation.message_model import MessageModel
    from app.api.v1.Ntesterc_module.Ntesterc_ai.conversation.mcp_execution_record import MCPExecutionRecordModel
    from app.api.v1.Ntesterc_module.Ntesterc_ai.llm_config.model import LLMConfigModel
    from app.api.v1.Ntesterc_module.Ntesterc_ai.usage.model import LLMUsageLogModel
    
    # 直接导入模型模块，避免触发 controller 和 service 的导入
    import sys
    import os
    backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(0, backend_path)
    
    # 导入所有模块的 model.py（只导入模块，不导入具体类）
    # 系统模块
    from app.api.v1.system.user import model as user_model
    from app.api.v1.system.role import model as role_model
    from app.api.v1.system.menu import model as menu_model
    from app.api.v1.system.permission import model as permission_model
    from app.api.v1.system.dept import model as dept_model
    from app.api.v1.system.dict import model as dict_model
    from app.api.v1.system.log import model as log_model
    from app.api.v1.system.file import model as file_model
    from app.api.v1.system.code_generator import model as code_gen_model
    from app.api.v1.Ntesterc_module.Ntesterc_intel import model as ai_intelligence_model
    from app.api.v1.Ntesterc_module.Ntesterc_project import model as projects_model
    from app.api.v1.Ntesterc_module.Ntesterc_testcases import model as testcases_model
    from app.api.v1.Ntesterc_module.Ntesterc_api_testing import model as api_testing_model
    from app.api.v1.Ntesterc_module.Ntesterc_api import model as api_automation_model
    from app.api.v1.Ntesterc_module.Ntesterc_ui import model as ui_automation_model
    from app.api.v1.Ntesterc_module.Ntesterc_app import model as app_management_model
    from app.api.v1.Ntesterc_module.Ntesterc_web import model as web_management_model
    from app.api.v1.Ntesterc_module.Ntesterc_notifications import model as notifications_model
    from app.api.v1.Ntesterc_module.Ntesterc_task_scheduler import model as task_scheduler_model
    from app.api.v1.Ntesterc_module.Ntesterc_reviews import model as reviews_model
    from app.api.v1.Ntesterc_module.Ntesterc_assistant import model as assistant_model
    from app.api.v1.Ntesterc_module.Ntesterc_data_factory import model as data_factory_model
    from app.api.v1.Ntesterc_module.Ntesterc_desk import model as desktop_automation_model
    from app.api.v1.Ntesterc_module.Ntesterc_mini import model as miniprogram_automation_model
    from app.api.v1.Ntesterc_module.Ntesterc_performance.config import model as perf_config_model
    from app.api.v1.Ntesterc_module.Ntesterc_performance.files import model as perf_files_model
    from app.api.v1.Ntesterc_module.Ntesterc_performance.scenario import model as perf_scenario_model

    print(f"成功导入 {len(target_metadata.tables)} 个表")

except Exception as e:
    print(f"导入模型失败: {e}")
    print("请确保：")
    print("1. 已安装所有依赖: pip install -r requirements")
    print("2. .env 配置正确")
    print("3. 在虚拟环境中运行")
    import traceback
    traceback.print_exc()
    raise


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
