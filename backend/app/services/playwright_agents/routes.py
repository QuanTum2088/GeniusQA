"""
Playwright Test Agents 路由服务函数
支持 MCP Server 和本地 Playwright 双模式
"""
import logging
from fastapi import Request
from typing import Optional

from ...models.playwright_agents import (
    PlaywrightTestPlan,
    PlaywrightGeneratedCode,
)
from .planner_agent import PlannerAgent
from .generator_agent import GeneratorAgent
from ..ai.llm_service import get_llm_service, get_llm_service_by_id

logger = logging.getLogger(__name__)


# ============ Planner Agent ============

async def explore_and_plan(request: Request):
    """探索应用并生成测试计划（支持 MCP 和本地 Playwright 双模式）"""
    try:
        data = await request.json()
        url = data.get('url')
        requirements = data.get('requirements', '')  # 测试需求描述
        llm_config_id = data.get('llm_config_id')
        mcp_config_id = data.get('mcp_config_id')
        max_depth = data.get('max_depth', 2)
        timeout = data.get('timeout', 60)
        
        # 处理空字符串
        if llm_config_id == "":
            llm_config_id = None
        if mcp_config_id == "":
            mcp_config_id = None
        
        logger.info(f"🔍 收到探索请求: URL={url}, requirements={requirements}, mcp_config_id={mcp_config_id}, llm_config_id={llm_config_id}")
        
        # 获取 LLM 服务
        if llm_config_id:
            llm_service = await get_llm_service_by_id(llm_config_id)
        else:
            llm_service = await get_llm_service()
        
        # 创建 Planner Agent
        planner = PlannerAgent(llm_service)
        
        # 获取 MCP 配置（如果提供）
        mcp_config = None
        if mcp_config_id:
            logger.info(f"📡 尝试获取 MCP 配置 ID={mcp_config_id}")
            try:
                from ...models.aitestrebort.project import aitestrebortMCPConfig
                mcp = await aitestrebortMCPConfig.get(id=mcp_config_id)
                mcp_config = {
                    "url": mcp.url,
                    "headers": mcp.headers or {}
                }
                logger.info(f"✅ 成功获取 MCP 配置: {mcp.name} ({mcp.url})")
            except Exception as e:
                logger.error(f"❌ 获取 MCP 配置失败: {str(e)}", exc_info=True)
        else:
            logger.info("⚠️  未提供 mcp_config_id，将使用本地 Playwright")
        
        # 创建测试计划记录
        creator_id = getattr(request.state, 'user', None)
        creator_id = creator_id.id if creator_id else 1
        
        plan = await PlaywrightTestPlan.create(
            url=url,
            max_depth=max_depth,
            timeout=timeout,
            status="exploring",
            test_scenarios=[],  # 初始化为空列表
            llm_config_id=llm_config_id if llm_config_id else None,
            creator_id=creator_id
        )
        
        try:
            # 执行探索（传递 MCP 配置和测试需求）
            result = await planner.explore_and_plan(
                url=url,
                max_depth=max_depth,
                timeout=timeout,
                mcp_config=mcp_config,
                requirements=requirements  # 传递测试需求
            )
            
            # 更新测试计划
            plan.test_scenarios = result["test_scenarios"]
            plan.exploration_result = result["exploration_result"]
            plan.status = "completed"
            await plan.save()
            
            return request.app.success(data={
                "id": plan.id,
                "url": plan.url,
                "test_scenarios": plan.test_scenarios,
                "status": plan.status
            })
            
        except Exception as e:
            plan.status = "failed"
            await plan.save()
            raise e
            
    except Exception as e:
        logger.error(f"探索失败: {str(e)}", exc_info=True)
        return request.app.fail(msg=f"探索失败: {str(e)}")


async def get_test_plans(request: Request):
    """获取测试计划列表"""
    try:
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        url = request.query_params.get('url')
        
        query = PlaywrightTestPlan.all()
        
        if url:
            query = query.filter(url__icontains=url)
        
        total = await query.count()
        plans = await query.order_by('-id').offset((page - 1) * page_size).limit(page_size)
        
        items = []
        for plan in plans:
            items.append({
                "id": plan.id,
                "url": plan.url,
                "max_depth": plan.max_depth,
                "status": plan.status,
                "test_scenarios": plan.test_scenarios,
                "created_at": plan.create_time.strftime("%Y-%m-%d %H:%M:%S") if plan.create_time else None
            })
        
        return request.app.success(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except Exception as e:
        logger.error(f"获取测试计划列表失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


async def get_test_plan_detail(request: Request, plan_id: int):
    """获取测试计划详情"""
    try:
        plan = await PlaywrightTestPlan.get(id=plan_id)
        
        return request.app.success(data={
            "id": plan.id,
            "url": plan.url,
            "max_depth": plan.max_depth,
            "timeout": plan.timeout,
            "status": plan.status,
            "test_scenarios": plan.test_scenarios,
            "exploration_result": plan.exploration_result,
            "created_at": plan.create_time.strftime("%Y-%m-%d %H:%M:%S") if plan.create_time else None
        })
        
    except Exception as e:
        logger.error(f"获取测试计划详情失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


async def delete_test_plan(request: Request, plan_id: int):
    """删除测试计划"""
    try:
        plan = await PlaywrightTestPlan.get(id=plan_id)
        await plan.delete()
        
        return request.app.success(msg="删除成功")
        
    except Exception as e:
        logger.error(f"删除测试计划失败: {str(e)}")
        return request.app.fail(msg=f"删除失败: {str(e)}")


async def get_exploration_steps(request: Request, plan_id: int):
    """获取测试计划的探索过程步骤"""
    try:
        plan = await PlaywrightTestPlan.get(id=plan_id)
        
        # 从 exploration_result 中获取步骤
        exploration_steps = plan.exploration_result.get('exploration_steps', [])
        
        return request.app.success(data={
            "plan_id": plan.id,
            "url": plan.url,
            "steps": exploration_steps,
            "total_steps": len(exploration_steps)
        })
        
    except Exception as e:
        logger.error(f"获取探索步骤失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


# ============ Generator Agent ============

async def generate_test_code(request: Request):
    """生成测试代码"""
    try:
        data = await request.json()
        plan_id = data.get('plan_id')
        llm_config_id = data.get('llm_config_id')
        framework = data.get('framework', 'playwright')
        language = data.get('language', 'typescript')
        
        # 处理空字符串
        if llm_config_id == "":
            llm_config_id = None
        
        plan = await PlaywrightTestPlan.get(id=plan_id)
        
        # 获取 LLM 服务
        if llm_config_id:
            llm_service = await get_llm_service_by_id(llm_config_id)
        else:
            llm_service = await get_llm_service()
        
        generator = GeneratorAgent(llm_service)
        
        creator_id = getattr(request.state, 'user', None)
        creator_id = creator_id.id if creator_id else 1
        
        code_record = await PlaywrightGeneratedCode.create(
            plan_id=plan.id,
            framework=framework,
            language=language,
            code="",
            status="generating",
            llm_config_id=llm_config_id if llm_config_id else None,
            creator_id=creator_id
        )
        
        try:
            result = await generator.generate_test_code(
                test_plan={
                    "url": plan.url,
                    "test_scenarios": plan.test_scenarios
                },
                framework=framework,
                language=language
            )
            
            code_record.code = result["code"]
            code_record.config_file = result["config_file"]
            code_record.status = "completed"
            await code_record.save()
            
            return request.app.success(data={
                "id": code_record.id,
                "plan_id": plan.id,
                "framework": code_record.framework,
                "language": code_record.language,
                "status": code_record.status
            })
            
        except Exception as e:
            code_record.status = "failed"
            await code_record.save()
            raise e
            
    except Exception as e:
        logger.error(f"代码生成失败: {str(e)}")
        return request.app.fail(msg=f"代码生成失败: {str(e)}")


async def get_generated_codes(request: Request):
    """获取生成代码列表"""
    try:
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        
        query = PlaywrightGeneratedCode.all()
        total = await query.count()
        codes = await query.order_by('-id').offset((page - 1) * page_size).limit(page_size)
        
        items = []
        for code in codes:
            items.append({
                "id": code.id,
                "plan_id": code.plan_id,
                "framework": code.framework,
                "language": code.language,
                "status": code.status,
                "created_at": code.create_time.strftime("%Y-%m-%d %H:%M:%S") if code.create_time else None
            })
        
        return request.app.success(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except Exception as e:
        logger.error(f"获取代码列表失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


async def get_generated_code_detail(request: Request, code_id: int):
    """获取代码详情"""
    try:
        code = await PlaywrightGeneratedCode.get(id=code_id)
        
        return request.app.success(data={
            "id": code.id,
            "plan_id": code.plan_id,
            "framework": code.framework,
            "language": code.language,
            "code": code.code,
            "config_file": code.config_file,
            "status": code.status,
            "created_at": code.create_time.strftime("%Y-%m-%d %H:%M:%S") if code.create_time else None
        })
        
    except Exception as e:
        logger.error(f"获取代码详情失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


async def delete_generated_code(request: Request, code_id: int):
    """删除代码"""
    try:
        code = await PlaywrightGeneratedCode.get(id=code_id)
        await code.delete()
        
        return request.app.success(msg="删除成功")
        
    except Exception as e:
        logger.error(f"删除代码失败: {str(e)}")
        return request.app.fail(msg=f"删除失败: {str(e)}")


async def get_statistics(request: Request):
    """获取统计数据"""
    try:
        from ...models.playwright_agents import PlaywrightExecution, PlaywrightHealRecord
        
        total_plans = await PlaywrightTestPlan.all().count()
        total_codes = await PlaywrightGeneratedCode.all().count()
        total_executions = await PlaywrightExecution.all().count()
        total_heals = await PlaywrightHealRecord.all().count()
        
        return request.app.success(data={
            "total_plans": total_plans,
            "total_codes": total_codes,
            "total_executions": total_executions,
            "total_heals": total_heals,
        })
        
    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


# ============ Executor Agent ============

async def execute_test(request: Request):
    """执行测试代码（支持 MCP）"""
    try:
        from ...models.playwright_agents import PlaywrightExecution
        from datetime import datetime
        
        data = await request.json()
        code_id = data.get('code_id')
        browser = data.get('browser', 'chromium')
        headless = data.get('headless', True)
        mcp_config_id = data.get('mcp_config_id')  # MCP 配置 ID
        
        # 处理空字符串
        if mcp_config_id == "":
            mcp_config_id = None
        
        logger.info(f"🚀 收到执行请求: code_id={code_id}, browser={browser}, headless={headless}, mcp_config_id={mcp_config_id}")
        
        # 获取代码记录
        code = await PlaywrightGeneratedCode.get(id=code_id)
        
        # 创建执行记录
        creator_id = getattr(request.state, 'user', None)
        creator_id = creator_id.id if creator_id else 1
        
        execution = await PlaywrightExecution.create(
            code=code,
            browser=browser,
            headless=headless,
            status="running",
            start_time=datetime.now(),
            creator_id=creator_id
        )
        
        try:
            # 优先使用 MCP 执行
            if mcp_config_id:
                logger.info(f"📡 使用 MCP 执行测试")
                from .mcp_executor_agent import MCPExecutorAgent
                from ...models.aitestrebort.project import aitestrebortMCPConfig
                
                mcp_config = await aitestrebortMCPConfig.get(id=mcp_config_id)
                executor = MCPExecutorAgent()
                
                result = await executor.execute_with_mcp(
                    code=code.code,
                    mcp_config={
                        'url': mcp_config.url,
                        'headers': mcp_config.headers or {}
                    },
                    browser=browser,
                    headless=headless
                )
            else:
                logger.info(f"💻 使用本地 Playwright 执行测试")
                from .local_executor_agent import LocalExecutorAgent
                
                executor = LocalExecutorAgent()
                result = await executor.execute_locally(
                    code=code.code,
                    browser=browser,
                    headless=headless
                )
            
            # 更新执行记录
            execution.status = result['status']
            execution.end_time = datetime.now()
            execution.duration = result.get('duration', 0)
            execution.stdout = result.get('stdout', '')
            execution.stderr = result.get('stderr', '')
            execution.exit_code = result.get('exit_code', 0)
            execution.error_message = result.get('error_message')
            execution.screenshots = result.get('screenshots', [])
            execution.videos = result.get('videos', [])
            await execution.save()
            
            logger.info(f"✅ 执行完成: execution_id={execution.id}, status={execution.status}")
            
            return request.app.success(data={
                "execution_id": execution.id,
                "status": execution.status,
                "duration": execution.duration
            })
            
        except Exception as e:
            # 更新执行记录为失败
            execution.status = "failed"
            execution.end_time = datetime.now()
            execution.error_message = str(e)
            await execution.save()
            logger.error(f"❌ 执行失败: {str(e)}", exc_info=True)
            raise e
            
    except Exception as e:
        logger.error(f"执行测试失败: {str(e)}", exc_info=True)
        return request.app.fail(msg=f"执行失败: {str(e)}")


async def get_executions(request: Request):
    """获取执行记录列表"""
    try:
        from ...models.playwright_agents import PlaywrightExecution
        
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        status = request.query_params.get('status')
        code_id = request.query_params.get('code_id')
        
        query = PlaywrightExecution.all()
        
        if status:
            query = query.filter(status=status)
        if code_id:
            query = query.filter(code_id=int(code_id))
        
        total = await query.count()
        executions = await query.order_by('-id').offset((page - 1) * page_size).limit(page_size)
        
        items = []
        for execution in executions:
            items.append({
                "id": execution.id,
                "code_id": execution.code_id,
                "browser": execution.browser,
                "headless": execution.headless,
                "status": execution.status,
                "duration": execution.duration,
                "created_at": execution.create_time.strftime("%Y-%m-%d %H:%M:%S") if execution.create_time else None
            })
        
        return request.app.success(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except Exception as e:
        logger.error(f"获取执行记录列表失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


async def get_execution_detail(request: Request, execution_id: int):
    """获取执行记录详情"""
    try:
        from ...models.playwright_agents import PlaywrightExecution
        
        execution = await PlaywrightExecution.get(id=execution_id)
        
        return request.app.success(data={
            "execution_id": execution.id,
            "code_id": execution.code_id,
            "browser": execution.browser,
            "headless": execution.headless,
            "status": execution.status,
            "start_time": execution.start_time.strftime("%Y-%m-%d %H:%M:%S") if execution.start_time else None,
            "end_time": execution.end_time.strftime("%Y-%m-%d %H:%M:%S") if execution.end_time else None,
            "duration": execution.duration,
            "stdout": execution.stdout,
            "stderr": execution.stderr,
            "exit_code": execution.exit_code,
            "error_message": execution.error_message,
            "screenshots": execution.screenshots,
            "videos": execution.videos
        })
        
    except Exception as e:
        logger.error(f"获取执行记录详情失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


async def get_execution_logs(request: Request, execution_id: int):
    """获取执行日志"""
    try:
        from ...models.playwright_agents import PlaywrightExecution
        
        execution = await PlaywrightExecution.get(id=execution_id)
        
        return request.app.success(data={
            "execution_id": execution.id,
            "status": execution.status,
            "start_time": execution.start_time.strftime("%Y-%m-%d %H:%M:%S") if execution.start_time else None,
            "end_time": execution.end_time.strftime("%Y-%m-%d %H:%M:%S") if execution.end_time else None,
            "duration": execution.duration,
            "stdout": execution.stdout,
            "stderr": execution.stderr,
            "exit_code": execution.exit_code
        })
        
    except Exception as e:
        logger.error(f"获取执行日志失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


async def delete_execution(request: Request, execution_id: int):
    """删除执行记录"""
    try:
        from ...models.playwright_agents import PlaywrightExecution
        
        execution = await PlaywrightExecution.get(id=execution_id)
        await execution.delete()
        
        return request.app.success(msg="删除成功")
        
    except Exception as e:
        logger.error(f"删除执行记录失败: {str(e)}")
        return request.app.fail(msg=f"删除失败: {str(e)}")


# ============ Healer Agent ============

async def heal_failed_test(request: Request):
    """自愈修复失败的测试"""
    try:
        from ...models.playwright_agents import PlaywrightExecution, PlaywrightHealRecord
        from .healer_agent import HealerAgent
        
        data = await request.json()
        execution_id = data.get('execution_id')
        llm_config_id = data.get('llm_config_id')
        
        # 处理空字符串
        if llm_config_id == "":
            llm_config_id = None
        
        execution = await PlaywrightExecution.get(id=execution_id)
        original_code = await execution.code
        
        # 获取 LLM 服务
        if llm_config_id:
            llm_service = await get_llm_service_by_id(llm_config_id)
        else:
            llm_service = await get_llm_service()
        
        creator_id = getattr(request.state, 'user', None)
        creator_id = creator_id.id if creator_id else 1
        
        heal_record = await PlaywrightHealRecord.create(
            execution=execution,
            original_code=original_code,
            status="healing",
            llm_config_id=llm_config_id if llm_config_id else None,
            creator_id=creator_id
        )
        
        try:
            healer = HealerAgent(llm_service)
            result = await healer.heal_test(
                original_code=original_code.code,
                error_message=execution.error_message,
                execution_logs={
                    "stdout": execution.stdout,
                    "stderr": execution.stderr
                }
            )
            
            # 创建修复后的代码记录
            fixed_code = await PlaywrightGeneratedCode.create(
                plan=original_code.plan,
                framework=original_code.framework,
                language=original_code.language,
                code=result["fixed_code"],
                config_file=original_code.config_file,
                status="completed",
                llm_config_id=llm_config_id if llm_config_id else None,
                creator_id=creator_id
            )
            
            heal_record.fixed_code = fixed_code
            heal_record.error_analysis = result["error_analysis"]
            heal_record.fix_description = result["fix_description"]
            heal_record.changes = result["changes"]
            heal_record.status = "success"
            await heal_record.save()
            
            return request.app.success(data={
                "heal_id": heal_record.id,
                "fixed_code_id": fixed_code.id,
                "status": heal_record.status
            })
            
        except Exception as e:
            heal_record.status = "failed"
            await heal_record.save()
            raise e
            
    except Exception as e:
        logger.error(f"自愈修复失败: {str(e)}")
        return request.app.fail(msg=f"自愈修复失败: {str(e)}")
