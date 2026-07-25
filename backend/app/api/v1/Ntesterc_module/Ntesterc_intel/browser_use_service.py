#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

"""
Browser-use AI浏览器服务，基于browser-use框架实现自然语言驱动的浏览器自动化
"""

import os
import sys
import asyncio
import shutil
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# 禁用browser-use遥测
os.environ['ANONYMIZED_TELEMETRY'] = 'false'

# Windows平台修复：设置事件循环策略和环境变量
if sys.platform == 'win32':
    # 设置环境变量
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '0'  # 使用系统浏览器
    os.environ['BROWSER_USE_WINDOWS_COMPAT'] = 'true'
    
    # 在Windows上使用ProactorEventLoop以支持子进程
    try:
        # 检查当前事件循环策略
        current_policy = asyncio.get_event_loop_policy()
        if not isinstance(current_policy, asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            logger.info("已设置Windows ProactorEventLoop策略以支持浏览器子进程")
        
    except Exception as e:
        logger.warning(f"设置Windows事件循环策略失败: {e}")

try:
    from langchain_openai import ChatOpenAI
    from browser_use import Agent, Controller
    from browser_use.browser.profile import BrowserProfile
    from browser_use.browser.browser import Browser
    BROWSER_USE_AVAILABLE = True
except ImportError:
    BROWSER_USE_AVAILABLE = False
    logger.warning("browser-use not installed. AI browser features will be disabled.")


class PydanticCompatibleChatOpenAI(ChatOpenAI):
    """兼容Pydantic 2.x的ChatOpenAI包装类"""
    
    class Config:
        # 允许额外字段
        extra = 'allow'
        # 允许任意类型
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保model属性存在
        model_name = kwargs.get('model', kwargs.get('model_name', 'gpt-3.5-turbo'))
        object.__setattr__(self, 'model', model_name)
        object.__setattr__(self, 'model_name', model_name)
    
    def __setattr__(self, name, value):
        """重写__setattr__以允许动态属性"""
        try:
            # 尝试使用父类的setattr
            super().__setattr__(name, value)
        except (ValueError, AttributeError):
            # 如果失败，直接设置到__dict__
            object.__setattr__(self, name, value)
    
    def __getattr__(self, name):
        """重写__getattr__以支持动态属性"""
        # 先检查__dict__
        if name in self.__dict__:
            return self.__dict__[name]
        
        try:
            return super().__getattr__(name)
        except AttributeError:
            # 返回默认值而不是抛出异常
            if name == 'model' or name == 'model_name':
                return 'gpt-3.5-turbo'
            elif name == 'provider':
                return 'openai'
            raise


class BrowserUseService:
    """Browser-use AI浏览器服务"""
    
    def __init__(self, model_config: Dict[str, Any]):
        """初始化服务
        
        Args:
            model_config: AI模型配置
                - api_key: API密钥
                - base_url: API基础URL
                - model_name: 模型名称
                - temperature: 温度参数
                - max_tokens: 最大token数
        """
        if not BROWSER_USE_AVAILABLE:
            raise ImportError(
                "browser-use is not installed. "
                "Please install it with: pip install browser-use playwright langchain-openai"
            )
        
        self.model_config = model_config
        self.llm = PydanticCompatibleChatOpenAI(
            api_key=model_config['api_key'],
            base_url=model_config['base_url'],
            model=model_config['model_name'],
            temperature=model_config.get('temperature', 0.7),
            max_tokens=model_config.get('max_tokens', 4096)
        )
        
        # 设置provider属性（browser-use需要）
        try:
            object.__setattr__(self.llm, 'provider', 'openai')
        except Exception as e:
            logger.warning(f"Failed to set provider attribute: {e}")

    
    async def execute_task(
        self,
        task: str,
        base_url: Optional[str] = None,
        max_steps: int = 50,
        headless: bool = False,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """执行AI浏览器任务
        
        Args:
            task: 任务描述（自然语言）
            base_url: 起始URL（可选）
            max_steps: 最大步骤数
            headless: 是否无头模式
            callback: 进度回调函数 async def callback(step_info: dict)
        
        Returns:
            执行结果字典:
            {
                'status': 'completed'|'failed',
                'steps': [步骤列表],
                'logs': [日志列表],
                'screenshots': [截图路径列表],
                'gif_path': 'GIF录制路径',
                'error': '错误信息（如果失败）'
            }
        """
        # 如果提供了base_url，添加到任务描述中
        if base_url:
            task = f"首先访问 {base_url}，然后{task}"
        
        # 执行结果
        result = {
            'status': 'pending',
            'steps': [],
            'logs': [],
            'screenshots': [],
            'gif_path': None,
            'error': None
        }
        
        try:
            logger.info(f"开始执行Browser-use任务: {task[:100]}...")
            
            # Windows兼容性检查
            if sys.platform == 'win32':
                # 检查是否在正确的事件循环中
                try:
                    loop = asyncio.get_running_loop()
                    if not isinstance(loop, asyncio.ProactorEventLoop):
                        logger.warning("当前不是ProactorEventLoop，Browser-use可能无法正常工作")
                except Exception as e:
                    logger.warning(f"事件循环检查失败: {e}")
                
                # 设置Windows环境变量
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '0'  # 使用系统浏览器
                os.environ['BROWSER_USE_WINDOWS_COMPAT'] = 'true'
            
            # 创建浏览器配置
            browser_config = {
                'headless': headless,
                'disable_security': True,  # 禁用安全限制以提高兼容性
                'keep_open': False,
            }
            
            # Windows特殊配置
            if sys.platform == 'win32':
                # 尝试使用系统Chrome
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', '')),
                ]
                
                chrome_path = None
                for path in chrome_paths:
                    if os.path.exists(path):
                        chrome_path = path
                        break
                
                if chrome_path:
                    logger.info(f"找到系统Chrome: {chrome_path}")
                    browser_config.update({
                        'executable_path': chrome_path,
                        'use_persistent_context': False,
                        'disable_extensions': True,
                        'disable_dev_shm_usage': True,
                        'args': [
                            '--no-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-gpu',
                            '--remote-debugging-port=9222',
                        ]
                    })
                else:
                    logger.warning("未找到系统Chrome，将使用默认配置")
            
            # 创建Controller和Agent
            controller = Controller()
            
            # Windows下尝试不同的Agent创建方式
            if sys.platform == 'win32':
                try:
                    # 方式1：使用自定义浏览器配置
                    from browser_use.browser.browser import Browser
                    from browser_use.browser.context import BrowserContext
                    
                    # 创建自定义浏览器实例
                    browser = Browser(
                        headless=headless,
                        browser_type='chromium'
                    )
                    
                    agent = Agent(
                        task=task,
                        llm=self.llm,
                        controller=controller,
                        max_actions_per_step=10,
                        browser=browser
                    )
                    logger.info("使用自定义浏览器配置创建Agent")
                    
                except Exception as e:
                    logger.warning(f"自定义浏览器配置失败: {e}，尝试默认配置")
                    # 方式2：使用默认配置
                    agent = Agent(
                        task=task,
                        llm=self.llm,
                        controller=controller,
                        max_actions_per_step=10
                    )
            else:
                # 非Windows系统使用默认配置
                agent = Agent(
                    task=task,
                    llm=self.llm,
                    controller=controller,
                    max_actions_per_step=10
                )
            
            # 执行任务
            start_time = datetime.now()
            
            # Windows下使用超时机制防止无限等待
            if sys.platform == 'win32':
                timeout = max_steps * 30  # 每步最多30秒
                try:
                    history = await asyncio.wait_for(
                        agent.run(max_steps=max_steps), 
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    raise Exception(f"任务执行超时（{timeout}秒），可能是Windows兼容性问题")
            else:
                history = await agent.run(max_steps=max_steps)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Browser-use任务执行完成，耗时: {duration}s")
            
            # 解析执行历史
            if hasattr(history, 'history') and history.history:
                for idx, item in enumerate(history.history):
                    step_info = {
                        'step_number': idx + 1,
                        'action': str(item.action) if hasattr(item, 'action') else 'unknown',
                        'result': str(item.result) if hasattr(item, 'result') else '',
                        'timestamp': datetime.now().isoformat()
                    }
                    result['steps'].append(step_info)
                    result['logs'].append(
                        f"[步骤 {step_info['step_number']}] {step_info['action']}"
                    )
                    
                    # 调用回调函数
                    if callback:
                        try:
                            await callback(step_info)
                        except Exception as e:
                            logger.error(f"回调函数执行失败: {e}")
            
            # 处理GIF录制文件
            gif_path = await self._save_gif_recording()
            if gif_path:
                result['gif_path'] = gif_path
            
            result['status'] = 'completed'
            logger.info(f"Browser-use任务成功完成，共{len(result['steps'])}步")
            
        except NotImplementedError as e:
            # Windows子进程问题的特殊处理
            error_msg = f"Windows环境下Browser-use子进程启动失败: {str(e)}"
            logger.error(f"Windows兼容性错误: {error_msg}")
            result['status'] = 'failed'
            result['error'] = error_msg
            result['logs'].append(f"[Windows兼容性错误] {error_msg}")
            result['logs'].append("这是Browser-use在Windows环境下的已知问题，需要特殊配置或使用WSL")
            
        except Exception as e:
            logger.error(f"Browser-use任务执行失败: {str(e)}", exc_info=True)
            result['status'] = 'failed'
            result['error'] = str(e)
            
            # 添加失败日志
            import traceback
            error_traceback = traceback.format_exc()
            result['logs'].append(f"执行失败: {str(e)}")
            result['logs'].append(f"详细错误:\n{error_traceback}")
            result['logs'].append(f"[错误] {str(e)}")
        
        return result

    
    async def _save_gif_recording(self) -> Optional[str]:
        """保存Browser-use生成的GIF录制文件
        
        Browser-use默认会在当前目录生成agent_history.gif
        我们需要将其移动到static目录
        
        Returns:
            保存后的相对路径，如果没有GIF则返回None
        """
        try:
            # Browser-use默认GIF路径
            default_gif = Path('agent_history.gif')
            
            if not default_gif.exists():
                logger.warning("未找到Browser-use生成的GIF文件")
                return None
            
            # 生成唯一文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            gif_filename = f'ai_execution_{timestamp}.gif'
            
            # 目标目录
            upload_dir = Path('backend/static/upload/ai_recording')
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # 目标路径
            target_path = upload_dir / gif_filename
            
            # 移动文件
            shutil.move(str(default_gif), str(target_path))
            
            # 返回相对路径（用于前端访问）
            relative_path = f'ai_recording/{gif_filename}'
            logger.info(f"GIF录制已保存: {relative_path}")
            
            return relative_path
            
        except Exception as e:
            logger.error(f"保存GIF录制失败: {e}")
            return None
    
    @staticmethod
    def is_available() -> bool:
        """检查Browser-use是否可用"""
        if not BROWSER_USE_AVAILABLE:
            return False
        
        # Windows兼容性检查
        if sys.platform == 'win32':
            try:
                # 检查是否可以创建子进程
                import subprocess
                subprocess.run(['echo', 'test'], capture_output=True, timeout=5)
                return True
            except Exception:
                logger.warning("Windows环境下子进程创建测试失败，Browser-use可能无法正常工作")
                return False
        
        return True
    
    @staticmethod
    def get_compatibility_info() -> Dict[str, Any]:
        """获取兼容性信息"""
        info = {
            'platform': sys.platform,
            'browser_use_available': BROWSER_USE_AVAILABLE,
            'subprocess_support': False,
            'event_loop_policy': None,
            'recommendations': []
        }
        
        # 检查子进程支持
        try:
            import subprocess
            subprocess.run(['echo', 'test'], capture_output=True, timeout=5)
            info['subprocess_support'] = True
        except Exception:
            info['subprocess_support'] = False
        
        # 检查事件循环策略
        try:
            policy = asyncio.get_event_loop_policy()
            info['event_loop_policy'] = type(policy).__name__
        except Exception:
            info['event_loop_policy'] = 'unknown'
        
        # 生成建议
        if sys.platform == 'win32':
            if not info['subprocess_support']:
                info['recommendations'].append("Windows环境下子进程支持有限，建议使用Linux环境")
            if info['event_loop_policy'] != 'WindowsProactorEventLoopPolicy':
                info['recommendations'].append("建议使用ProactorEventLoop策略")
        
        return info
    
    @staticmethod
    def get_required_packages() -> List[str]:
        """获取所需的Python包列表"""
        return [
            'browser-use',
            'playwright',
            'langchain-openai'
        ]


# 便捷函数
async def execute_browser_task(
    task: str,
    model_config: Dict[str, Any],
    base_url: Optional[str] = None,
    max_steps: int = 50,
    headless: bool = False,
    callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """执行Browser-use任务的便捷函数
    
    Args:
        task: 任务描述
        model_config: AI模型配置
        base_url: 起始URL
        max_steps: 最大步骤数
        headless: 是否无头模式
        callback: 进度回调
    
    Returns:
        执行结果
    """
    service = BrowserUseService(model_config)
    return await service.execute_task(
        task=task,
        base_url=base_url,
        max_steps=max_steps,
        headless=headless,
        callback=callback
    )
