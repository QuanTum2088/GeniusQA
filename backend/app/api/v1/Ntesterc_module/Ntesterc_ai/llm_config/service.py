#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

import time
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.api.v1.Ntesterc_module.Ntesterc_ai.llm_config.model import LLMConfigModel
from app.api.v1.Ntesterc_module.Ntesterc_ai.llm_config.schema import (
    LLMConfigCreateSchema,
    LLMConfigUpdateSchema,
    LLMConfigTestSchema
)

logger = logging.getLogger(__name__)


class LLMConfigService:
    """LLM 配置服务"""
    
    @classmethod
    async def get_list(
        cls,
        db: AsyncSession,
        provider: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[LLMConfigModel]:
        """获取配置列表"""
        query = select(LLMConfigModel).where(LLMConfigModel.enabled_flag == 1)
        
        if provider:
            query = query.where(LLMConfigModel.provider == provider)
        
        if is_active is not None:
            query = query.where(LLMConfigModel.is_active == is_active)
        
        query = query.order_by(LLMConfigModel.is_default.desc(), LLMConfigModel.id.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @classmethod
    async def get_by_id(cls, db: AsyncSession, config_id: int) -> Optional[LLMConfigModel]:
        """根据ID获取配置"""
        query = select(LLMConfigModel).where(
            LLMConfigModel.id == config_id,
            LLMConfigModel.enabled_flag == 1
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_default(cls, db: AsyncSession) -> Optional[LLMConfigModel]:
        """获取默认配置"""
        query = select(LLMConfigModel).where(
            LLMConfigModel.is_default == True,
            LLMConfigModel.is_active == True,
            LLMConfigModel.enabled_flag == 1
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        data: LLMConfigCreateSchema,
        user_id: Optional[int] = None
    ) -> LLMConfigModel:
        """创建配置"""
        # 如果设置为默认配置，先取消其他默认配置
        if data.is_default:
            await cls._unset_all_defaults(db)
        
        # 创建新配置
        config = LLMConfigModel(
            config_name=data.config_name,
            name=data.name,
            provider=data.provider,
            model_name=data.model_name,
            api_key=data.api_key,
            base_url=data.base_url,
            system_prompt=data.system_prompt,
            temperature=data.temperature,
            max_tokens=data.max_tokens,
            supports_vision=data.supports_vision,
            context_limit=data.context_limit,
            is_default=data.is_default,
            is_active=data.is_active,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(config)
        await db.commit()
        await db.refresh(config)
        
        return config
    
    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        config_id: int,
        data: LLMConfigUpdateSchema,
        user_id: Optional[int] = None
    ) -> LLMConfigModel:
        """更新配置"""
        # 检查配置是否存在
        config = await cls.get_by_id(db, config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        # 如果设置为默认配置，先取消其他默认配置
        if data.is_default:
            await cls._unset_all_defaults(db)
        
        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        update_data['updated_by'] = user_id
        
        # 检查API Key是否是脱敏值（包含****），如果是则保留数据库中的原值
        if 'api_key' in update_data and update_data['api_key'] and '****' in update_data['api_key']:
            logger.warning(f"检测到脱敏的API Key: {update_data['api_key']}, 将保留数据库中的原值")
            # 保留数据库中的原值
            update_data['api_key'] = config.api_key
            logger.info(f"保留原API Key: {config.api_key[:10]}...")
        
        stmt = (
            update(LLMConfigModel)
            .where(LLMConfigModel.id == config_id)
            .values(**update_data)
        )
        
        await db.execute(stmt)
        await db.commit()
        
        # 重新获取更新后的配置
        return await cls.get_by_id(db, config_id)
    
    @classmethod
    async def delete(cls, db: AsyncSession, config_id: int) -> bool:
        """删除配置（硬删除）。先解除关联引用，避免外键冲突。"""
        config = await cls.get_by_id(db, config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")

        # 1. 解除对话对 LLM 配置的外键引用（ON DELETE RESTRICT）
        try:
            from app.api.v1.Ntesterc_module.Ntesterc_ai.conversation.model import ConversationModel

            clear_conv = await db.execute(
                update(ConversationModel)
                .where(ConversationModel.llm_config_id == config_id)
                .values(llm_config_id=None)
            )
            if clear_conv.rowcount:
                logger.info(
                    f"删除LLM配置前已清空 {clear_conv.rowcount} 条对话的 llm_config_id: config_id={config_id}"
                )
        except Exception as e:
            logger.warning(f"清空对话 llm_config_id 失败: {e}")
            raise HTTPException(status_code=400, detail=f"无法删除：对话关联清理失败（{e}）")

        # 2. 解除 AI 模型配置关联（无外键，置空即可）
        try:
            from app.api.v1.Ntesterc_module.Ntesterc_intel.model import AIModelConfigModel

            clear_ai = await db.execute(
                update(AIModelConfigModel)
                .where(AIModelConfigModel.llm_config_id == config_id)
                .values(llm_config_id=None)
            )
            if clear_ai.rowcount:
                logger.info(
                    f"删除LLM配置前已清空 {clear_ai.rowcount} 条AI模型配置的 llm_config_id: config_id={config_id}"
                )
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"清空AI模型配置 llm_config_id 时出错: {e}")

        # 3. 解除用量日志关联（无外键，置空保留历史）
        try:
            from app.api.v1.Ntesterc_module.Ntesterc_ai.usage.model import LLMUsageLogModel

            await db.execute(
                update(LLMUsageLogModel)
                .where(LLMUsageLogModel.llm_config_id == config_id)
                .values(llm_config_id=None)
            )
        except Exception as e:
            logger.warning(f"清空用量日志 llm_config_id 时出错: {e}")

        # 4. 硬删除配置本身
        stmt = delete(LLMConfigModel).where(LLMConfigModel.id == config_id)
        await db.execute(stmt)
        await db.commit()

        logger.info(f"硬删除LLM配置成功: ID={config_id}, Name={config.config_name}")
        return True
    
    @classmethod
    async def set_default(cls, db: AsyncSession, config_id: int) -> LLMConfigModel:
        """设置为默认配置"""
        import logging
        logger = logging.getLogger(__name__)
        
        # 先检查配置是否存在
        config = await cls.get_by_id(db, config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        logger.info(f"[set_default] 开始设置默认配置: config_id={config_id}, config_name={config.config_name}")
        
        # 取消所有默认配置
        logger.info("[set_default] 取消所有默认配置...")
        await cls._unset_all_defaults(db)
        
        # 验证是否成功取消
        check_stmt = select(LLMConfigModel).where(
            LLMConfigModel.is_default == True,
            LLMConfigModel.enabled_flag == 1
        )
        check_result = await db.execute(check_stmt)
        remaining_defaults = check_result.scalars().all()
        if remaining_defaults:
            logger.warning(f"[set_default] 仍有 {len(remaining_defaults)} 个配置标记为默认")
            for rd in remaining_defaults:
                logger.warning(f"  - ID={rd.id}, name={rd.config_name}")
        else:
            logger.info("[set_default] 所有默认配置已取消")
        
        # 设置当前配置为默认
        logger.info(f"[set_default] 设置 config_id={config_id} 为默认...")
        stmt = (
            update(LLMConfigModel)
            .where(LLMConfigModel.id == config_id)
            .values(is_default=True)
        )
        await db.execute(stmt)
        await db.commit()
        
        logger.info("[set_default] 提交完成，重新查询配置...")
        
        # 重新获取更新后的配置
        updated_config = await cls.get_by_id(db, config_id)
        logger.info(f"[set_default] 更新后的配置: ID={updated_config.id}, is_default={updated_config.is_default}")
        
        # 验证数据库中的状态
        verify_stmt = select(LLMConfigModel).where(LLMConfigModel.enabled_flag == 1)
        verify_result = await db.execute(verify_stmt)
        all_configs = verify_result.scalars().all()
        logger.info(f"[set_default] 所有配置状态:")
        for c in all_configs:
            logger.info(f"  - ID={c.id}, name={c.config_name}, is_default={c.is_default}, is_active={c.is_active}")
        
        return updated_config
    
    @classmethod
    async def test_config(
        cls,
        db: AsyncSession,
        data: LLMConfigTestSchema
    ) -> Dict[str, Any]:
        """测试配置，失败时返回可读的具体错误信息。"""
        import httpx
        import re as _re

        if data.config_id:
            config = await cls.get_by_id(db, data.config_id)
            if not config:
                return {
                    "success": False,
                    "message": "测试失败",
                    "error": "配置不存在或已删除（配置ID无效）",
                }
            provider = config.provider
            api_key = config.api_key
            base_url = config.base_url
            model_name = config.name or config.model_name
        else:
            provider = data.provider
            api_key = data.api_key
            base_url = data.base_url
            model_name = data.name

        if not api_key:
            return {
                "success": False,
                "message": "测试失败",
                "error": "API Key 为空，请先填写有效的密钥",
            }
        if not model_name:
            return {
                "success": False,
                "message": "测试失败",
                "error": "模型名称为空，请先填写模型名称",
            }

        clean_url = (base_url or "").rstrip("/")
        for ep in ["/chat/completions", "/completions"]:
            if clean_url.endswith(ep):
                clean_url = clean_url[: -len(ep)].rstrip("/")
                break
        if (
            clean_url
            and not _re.search(r"/v\d+(/|$)", clean_url)
            and not clean_url.endswith("/compatible-mode/v1")
        ):
            clean_url = clean_url + "/v1"

        endpoint = (
            f"{clean_url}/chat/completions"
            if clean_url
            else "https://api.openai.com/v1/chat/completions"
        )

        start_time = time.time()
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": data.test_message}],
                "max_tokens": 100,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(endpoint, json=payload, headers=headers)

            latency = round(time.time() - start_time, 2)

            if response.status_code == 200:
                result = response.json()
                content = (
                    result.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                return {
                    "success": True,
                    "message": "测试成功",
                    "response": content,
                    "latency": latency,
                    "endpoint": endpoint,
                    "provider": provider,
                    "model": model_name,
                }

            detail = cls._extract_api_error_detail(response)
            return {
                "success": False,
                "message": "测试失败",
                "error": (
                    f"HTTP {response.status_code}，请求地址：{endpoint}\n"
                    f"模型：{model_name}\n"
                    f"详情：{detail}"
                ),
                "latency": latency,
                "endpoint": endpoint,
            }

        except httpx.ConnectError as e:
            latency = round(time.time() - start_time, 2)
            return {
                "success": False,
                "message": "测试失败",
                "error": (
                    f"无法连接到 LLM 服务：{endpoint}\n"
                    f"原因：{cls._friendly_exception(e)}\n"
                    "请检查 Base URL 是否正确，以及网络/代理是否可达。"
                ),
                "latency": latency,
                "endpoint": endpoint,
            }
        except httpx.TimeoutException as e:
            latency = round(time.time() - start_time, 2)
            return {
                "success": False,
                "message": "测试失败",
                "error": (
                    f"连接超时（30秒）：{endpoint}\n"
                    f"原因：{cls._friendly_exception(e)}\n"
                    "请检查网络延迟，或确认服务地址是否可访问。"
                ),
                "latency": latency,
                "endpoint": endpoint,
            }
        except Exception as e:
            latency = round(time.time() - start_time, 2)
            return {
                "success": False,
                "message": "测试失败",
                "error": (
                    f"请求地址：{endpoint}\n"
                    f"原因：{cls._friendly_exception(e)}"
                ),
                "latency": latency,
                "endpoint": endpoint,
            }

    @staticmethod
    def _extract_api_error_detail(response) -> str:
        """从 LLM API 响应中提取可读错误。"""
        text = (response.text or "").strip()
        if not text:
            return response.reason_phrase or "无响应内容"
        try:
            body = response.json()
            if isinstance(body, dict):
                err = body.get("error")
                if isinstance(err, dict):
                    msg = err.get("message") or err.get("msg") or str(err)
                    code = err.get("code") or err.get("type")
                    return f"{msg}" + (f"（code={code}）" if code else "")
                if isinstance(err, str):
                    return err
                for key in ("message", "msg", "detail"):
                    if body.get(key):
                        return str(body[key])
                return str(body)[:800]
        except Exception:
            pass
        return text[:800]

    @staticmethod
    def _friendly_exception(exc: Exception) -> str:
        """将常见网络异常转为更易读的说明。"""
        raw = str(exc).strip() or exc.__class__.__name__
        lower = raw.lower()
        if "all connection attempts failed" in lower:
            return f"所有连接尝试均失败（{raw}）"
        if "name or service not known" in lower or "getaddrinfo failed" in lower:
            return f"域名解析失败（{raw}）"
        if "certificate" in lower or "ssl" in lower:
            return f"证书/SSL 校验失败（{raw}）"
        if "connection refused" in lower:
            return f"连接被拒绝（{raw}）"
        return raw

    @classmethod
    async def _unset_all_defaults(cls, db: AsyncSession):
        """取消所有默认配置"""
        stmt = (
            update(LLMConfigModel)
            .where(LLMConfigModel.is_default == True)
            .values(is_default=False)
        )
        await db.execute(stmt)
