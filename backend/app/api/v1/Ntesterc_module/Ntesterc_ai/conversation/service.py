#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

import uuid
import json
import time
import re
import asyncio
from urllib.parse import urlparse
from typing import List, Optional, Dict, Any, Union
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.api.v1.Ntesterc_module.Ntesterc_ai.conversation.model import ConversationModel
from app.api.v1.Ntesterc_module.Ntesterc_ai.conversation.message_model import MessageModel
from app.api.v1.Ntesterc_module.Ntesterc_ai.conversation.mcp_execution_record import MCPExecutionRecordModel
from app.api.v1.Ntesterc_module.Ntesterc_ai.conversation.llm_service import get_llm_service, get_llm_service_by_id, LLMMessage
from app.api.v1.system.file.service import FileService
from app.api.v1.Ntesterc_module.Ntesterc_project.project_platform_service import (
    query_knowledge_base,
    mcp_list_tools,
    mcp_call_tool,
)
from app.api.v1.Ntesterc_module.Ntesterc_skills.service import run_skill_tool, create_skill_job
from app.api.v1.Ntesterc_module.Ntesterc_skills.model import ProjectSkillModel
from app.api.v1.Ntesterc_module.Ntesterc_skills.execution_model import SkillExecutionJobModel, SkillExecutionEventModel, SkillExecutionArtifactModel
from .schema import (
    ConversationCreateRequest,
    ConversationUpdateRequest,
    SendMessageRequest
)


class ConversationService:
    """对话服务"""
    
    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        user_id: int,
        data: ConversationCreateRequest
    ) -> ConversationModel:
        """创建对话"""
        # 生成会话ID
        session_id = str(uuid.uuid4())
        
        # 创建对话
        conversation = ConversationModel(
            session_id=session_id,
            title=data.title or "新对话",
            llm_config_id=data.llm_config_id,
            user_id=user_id,
            is_active=1,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        
        return conversation
    
    @staticmethod
    async def get_conversation_list(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[ConversationModel], int]:
        """获取对话列表"""
        # 查询总数
        count_stmt = select(func.count(ConversationModel.id)).where(
            ConversationModel.user_id == user_id,
            ConversationModel.enabled_flag == 1
        )
        result = await db.execute(count_stmt)
        total = result.scalar()
        
        # 查询列表
        stmt = select(ConversationModel).where(
            ConversationModel.user_id == user_id,
            ConversationModel.enabled_flag == 1
        ).order_by(desc(ConversationModel.updation_date)).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        conversations = result.scalars().all()
        
        return conversations, total
    
    @staticmethod
    async def get_conversation(
        db: AsyncSession,
        conversation_id: int,
        user_id: int
    ) -> Optional[ConversationModel]:
        """获取对话详情"""
        stmt = select(ConversationModel).where(
            ConversationModel.id == conversation_id,
            ConversationModel.user_id == user_id,
            ConversationModel.enabled_flag == 1
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_conversation(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        data: ConversationUpdateRequest
    ) -> Optional[ConversationModel]:
        """更新对话"""
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)
        if not conversation:
            return None
        
        # 更新字段
        if data.title is not None:
            conversation.title = data.title
        if data.llm_config_id is not None:
            conversation.llm_config_id = data.llm_config_id
        if data.is_active is not None:
            conversation.is_active = 1 if data.is_active else 0
        
        conversation.updated_by = user_id
        
        await db.commit()
        await db.refresh(conversation)
        
        return conversation
    
    @staticmethod
    async def delete_conversation(
        db: AsyncSession,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """删除对话（软删除）"""
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)
        if not conversation:
            return False
        
        conversation.enabled_flag = 0
        conversation.updated_by = user_id
        
        await db.commit()
        return True
    
    @staticmethod
    async def get_message_count(
        db: AsyncSession,
        conversation_id: int
    ) -> int:
        """获取对话消息数量"""
        stmt = select(func.count(MessageModel.id)).where(
            MessageModel.conversation_id == conversation_id,
            MessageModel.enabled_flag == 1
        )
        result = await db.execute(stmt)
        return result.scalar()


class MessageService:
    """消息服务"""
    
    @staticmethod
    def _estimate_tokens(content: Union[str, List[Dict[str, Any]], Any]) -> int:
        """粗略 token 估算（约 1 token ≈ 4 chars）。"""
        if not content:
            return 0
        if isinstance(content, str):
            return max(1, len(content) // 4)
        if isinstance(content, list):
            merged_text = []
            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get("type") == "text":
                    merged_text.append(str(part.get("text") or ""))
                elif part.get("type") == "image_url":
                    merged_text.append(str((part.get("image_url") or {}).get("url") or ""))
            text = "\n".join(merged_text)
            return max(1, len(text) // 4) if text else 0
        text = str(content)
        return max(1, len(text) // 4) if text else 0

    @staticmethod
    def _build_multimodal_user_content(text: str, attachments: Optional[List[Dict[str, Any]]]) -> Union[str, List[Dict[str, Any]]]:
        if not MessageService._has_image_attachment(attachments):
            return text
        parts: List[Dict[str, Any]] = [{"type": "text", "text": text or ""}]
        for item in attachments or []:
            if not isinstance(item, dict):
                continue
            mime = str(item.get("mime_type") or item.get("content_type") or item.get("type") or "").lower()
            url = str(item.get("url") or item.get("file_url") or "").strip()
            if not url:
                continue
            if "image" in mime or url.lower().startswith("data:image/") or url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")):
                parts.append({"type": "image_url", "image_url": {"url": url}})
        return parts if len(parts) > 1 else text

    @staticmethod
    def _has_image_attachment(attachments: Optional[List[Dict[str, Any]]]) -> bool:
        if not attachments:
            return False
        image_exts = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")
        for item in attachments:
            if not isinstance(item, dict):
                continue
            mime = str(item.get("mime_type") or item.get("content_type") or "").lower()
            name = str(item.get("name") or item.get("filename") or "").lower()
            url = str(item.get("url") or item.get("file_url") or "").lower()
            typ = str(item.get("type") or "").lower()
            if "image" in mime or typ == "image":
                return True
            if name.endswith(image_exts) or url.endswith(image_exts):
                return True
            if url.startswith("data:image/"):
                return True
        return False

    @staticmethod
    def _apply_context_limit(
        llm_messages: List[LLMMessage],
        context_limit: int,
        max_tokens: int,
    ) -> List[LLMMessage]:
        if context_limit <= 0:
            return llm_messages
        # 预留输出预算，至少保留 512
        budget = max(512, context_limit - max(0, max_tokens))
        if budget <= 0:
            return llm_messages[-6:] if len(llm_messages) > 6 else llm_messages

        system_msgs = [m for m in llm_messages if m.role == "system"]
        non_system = [m for m in llm_messages if m.role != "system"]

        kept_rev: List[LLMMessage] = []
        used = 0
        for m in reversed(non_system):
            t = MessageService._estimate_tokens(m.content)
            if used + t > budget and kept_rev:
                break
            if used + t > budget and not kept_rev:
                # 至少保留最后一条用户消息
                kept_rev.append(m)
                break
            kept_rev.append(m)
            used += t

        kept_non_system = list(reversed(kept_rev))
        return [*system_msgs, *kept_non_system]

    @staticmethod
    def _apply_llm_runtime_controls(
        llm_messages: List[LLMMessage],
        llm_service: Any,
        data: SendMessageRequest,
    ) -> List[LLMMessage]:
        cfg = getattr(llm_service, "config", {}) or {}
        system_prompt = str(cfg.get("system_prompt") or "").strip()
        supports_vision = bool(cfg.get("supports_vision", False))
        context_limit = int(cfg.get("context_limit") or 0)
        max_tokens = int(cfg.get("max_tokens") or 2000)

        
        if MessageService._has_image_attachment(data.attachments) and not supports_vision:
            raise ValueError("当前 LLM 配置未开启多模态支持，无法处理图片附件")

        new_msgs = list(llm_messages)
        # 系统提示词注入（最高优先级）
        if system_prompt:
            new_msgs = [LLMMessage(role="system", content=system_prompt), *new_msgs]

        
        if supports_vision and MessageService._has_image_attachment(data.attachments):
            for idx in range(len(new_msgs) - 1, -1, -1):
                if new_msgs[idx].role == "user":
                    text = new_msgs[idx].content if isinstance(new_msgs[idx].content, str) else str(new_msgs[idx].content or "")
                    new_msgs[idx] = LLMMessage(
                        role="user",
                        content=MessageService._build_multimodal_user_content(text, data.attachments)
                    )
                    break

        
        new_msgs = MessageService._apply_context_limit(new_msgs, context_limit, max_tokens)
        return new_msgs

    @staticmethod
    def _kb_explicitly_enabled(data: SendMessageRequest) -> bool:
        return bool(
            data.use_knowledge_base
            and data.project_id
            and data.knowledge_base_id
        )

    @staticmethod
    def _is_direct_mode(data: SendMessageRequest) -> bool:
        return str(getattr(data, "tool_mode", "smart") or "smart").strip().lower() == "direct"

    @staticmethod
    def _extract_target_url(text: str) -> str:
        src = str(text or "").strip()
        if not src:
            return ""
        m = re.search(r"https?://[^\s]+", src)
        if m:
            return m.group(0)
        # fallback: ip[:port][/path] or domain[/path]
        m2 = re.search(r"\b((?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/[^\s]*)?|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?::\d+)?(?:/[^\s]*)?)\b", src)
        if m2:
            host = m2.group(1)
            if not host.startswith(("http://", "https://")):
                return f"http://{host}"
            return host
        return ""

    @staticmethod
    def _split_skill_command_steps(command: str) -> List[str]:
        s = (command or "").strip()
        if not s:
            return []
        parts = [p.strip() for p in s.split(" && ") if p.strip()]
        return parts if parts else [s]

    @staticmethod
    def _step_title_and_expectation(step_cmd: str) -> tuple[str, str]:
        low = (step_cmd or "").strip().lower()
        title = "执行子命令"
        expect = "进程退出码为 0；stderr 无阻断性错误。"
        if "agent-browser" in low:
            if re.search(r"\bopen\b", low):
                title, expect = "浏览器：打开 URL", "应导航到用户给定地址；后续「get url」输出应与目标一致。"
            elif "get url" in low:
                title, expect = "浏览器：读取地址栏 URL", "stdout 中应出现当前页的 http(s) 链接（通常为一行）。"
            elif "snapshot" in low:
                title, expect = "浏览器：页面快照", "输出可访问性/结构信息，供检查元素与状态。"
            elif "screenshot" in low:
                title, expect = "浏览器：整页截图", "在会话截图目录生成图片文件，可在下方截图列表打开核验。"
        elif "playwright" in low or "chromium.launch" in low:
            title, expect = "Playwright 自动化", "无头浏览器启动、导航、截图保存成功。"
        return title, expect

    @staticmethod
    def _build_detailed_test_steps_report(
        command: str,
        logs: List[str],
        job_return_code: Optional[int] = None,
        stderr_blob: str = "",
    ) -> str:
        """
        将命令链（&&）与 runner 事件中的「[测试步骤 i/n] 结束 returncode=…」对齐，输出可审计的测试步骤表。
        """
        steps = MessageService._split_skill_command_steps(command)
        if not steps:
            return ""
        rc_by_idx: Dict[int, int] = {}
        for line in logs or []:
            m = re.search(r"\[测试步骤 (\d+)/(\d+)\] 结束 returncode=(-?\d+)", str(line))
            if m:
                rc_by_idx[int(m.group(1))] = int(m.group(3))
        has_marker = any("[测试步骤" in str(x) for x in (logs or []))
        if len(steps) == 1 and not rc_by_idx and has_marker is False and job_return_code is not None:
            rc_by_idx[1] = int(job_return_code)
        url_mismatch = "[URL_MISMATCH]" in (stderr_blob or "")
        cmd_show = command if len(command) <= 520 else command[:520] + "..."
        lines: List[str] = [
            "#### 详细测试步骤",
            "",
            f"- **用例命令链**（`&&` 与 shell 短路一致）: `{cmd_show}`",
            "",
        ]
        for i, step in enumerate(steps, start=1):
            title, expect = MessageService._step_title_and_expectation(step)
            rc = rc_by_idx.get(i)
            sc = step if len(step) <= 220 else step[:220] + "..."
            if rc is None:
                max_done = max(rc_by_idx.keys(), default=0)
                failed_before = any((rc_by_idx.get(k) or 0) != 0 for k in rc_by_idx)
                if i > max_done and failed_before:
                    actual = "未执行（前序步骤非零退出，`&&` 短路，后续子命令未运行）。"
                    verdict = "跳过"
                elif len(steps) == 1 and job_return_code is not None:
                    actual = f"整 job returncode={job_return_code}；stdout/stderr 见下文汇总。"
                    verdict = "通过" if int(job_return_code) == 0 else "失败"
                else:
                    actual = "未从事件流解析到该步的「结束 returncode」行（可能为旧版 runner 单次执行）。"
                    verdict = "未判定"
            else:
                actual = f"returncode={rc}；runner 已在事件中记录本步起止；stdout 按「步骤 {i}/{len(steps)}」分区可查。"
                verdict = "通过" if rc == 0 else "失败"
            lines.append(f"{i}. **{title}**")
            lines.append(f"   - **操作**: `{sc}`")
            lines.append(f"   - **预期**: {expect}")
            lines.append(f"   - **实际**: {actual}")
            lines.append(f"   - **结论**: {verdict}")
            lines.append("")
        if url_mismatch:
            lines.append("- **后置校验**: `[URL_MISMATCH]` 已写入 stderr，表示打开的页面与问题中的目标主机不一致，总用例判失败。")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    async def _run_skill_chain(
        db: AsyncSession,
        user_id: int,
        data: SendMessageRequest,
        llm_messages: List[LLMMessage],
        stream_emit: Optional[Any] = None,
    ) -> tuple[Optional[str], str]:
        """
        Smart-mode skill chain: model decides whether to invoke selected skill.
        """
        if MessageService._is_direct_mode(data):
            return None, "Skill链路跳过（直连模式）"
        if not (data.use_skill and data.project_id and data.skill_id):
            return None, "Skill未开启"
        try:
            stmt = select(ProjectSkillModel).where(
                ProjectSkillModel.id == int(data.skill_id),
                ProjectSkillModel.project_id == int(data.project_id),
                ProjectSkillModel.user_id == user_id,
                ProjectSkillModel.enabled_flag == 1,
                ProjectSkillModel.is_active == 1,
            )
            skill = (await db.execute(stmt)).scalar_one_or_none()
            if not skill:
                return None, "Skill不可用"

            extra = skill.extra_config or {}
            allowed_tools = str(extra.get("allowed_tools") or "")
            skill_name = str(skill.name or "").lower()
            test_guard = (
                "测试执行规范：1) 浏览器场景优先先导航再获取页面结构（snapshot）。"
                "2) 页面变化后需要再次获取结构。3) 关键步骤保留截图。"
                "4) 失败时返回可复现线索（命令、报错、当前URL/截图）。"
            )
            planner_prompt = (
                "你是测试自动化工具路由器。当前可用工具为一个 Skill。"
                "请基于用户问题判断是否调用该 Skill。仅输出 JSON。\n"
                "格式: {\"use_skill\": true|false, \"arguments\": {...}, \"session_id\": \"\"}\n"
                "若无需调用输出 {\"use_skill\": false, \"arguments\": {}, \"session_id\": \"\"}\n\n"
                f"{test_guard}\n\n"
                f"Skill: {skill.name}\n"
                f"描述: {skill.description or ''}\n"
                f"allowed-tools: {allowed_tools}\n"
                f"用户问题: {data.content}"
            )
            pmsgs = llm_messages.copy()
            if pmsgs and pmsgs[-1].role == "user":
                pmsgs[-1] = LLMMessage(role="user", content=planner_prompt)
            else:
                pmsgs.append(LLMMessage(role="user", content=planner_prompt))

            llm_service = await get_llm_service()
            plan_resp = await llm_service.chat_completion(messages=pmsgs, stream=False)
            raw = (plan_resp.content or "").strip()
            if raw.startswith("```"):
                raw = raw.strip("`")
                raw = raw.replace("json", "", 1).strip()
            try:
                plan = json.loads(raw)
            except Exception:
                l = raw.find("{")
                r = raw.rfind("}")
                if l >= 0 and r > l:
                    plan = json.loads(raw[l : r + 1])
                else:
                    return None, f"Skill规划结果无法解析: {raw[:160]}"

            if not bool(plan.get("use_skill")):
                return None, "Skill规划判定无需调用"

            args = plan.get("arguments") if isinstance(plan.get("arguments"), dict) else {}
            # Ensure query fallback for test scenarios
            args.setdefault("query", data.content)
            # Force URL from user request when present (avoid default/irrelevant sites).
            forced_url = MessageService._extract_target_url(str(data.content or ""))
            if forced_url:
                args["url"] = forced_url
            # Normalize common planner typo: agent-browser:open -> agent-browser open
            cmd_raw = str(args.get("command") or "").strip()
            if cmd_raw and "agent-browser:" in cmd_raw:
                cmd_raw = cmd_raw.replace("agent-browser:", "agent-browser ")
                args["command"] = cmd_raw
            # If user provided url and command contains a different url, replace with forced one.
            if forced_url and cmd_raw:
                cmd_raw2 = re.sub(r"https?://[^\s]+", forced_url, cmd_raw)
                args["command"] = cmd_raw2
            # Guard: "agent-browser open" without URL should not fallback to default page.
            open_without_url = re.search(r"\b(?:npx\s+)?agent-browser\s+open\s*$", str(args.get("command") or "").strip(), flags=re.IGNORECASE)
            if open_without_url:
                if forced_url:
                    args["command"] = f"npx agent-browser open {forced_url} && npx agent-browser snapshot -i"
                else:
                    return None, "Skill规划未提供目标URL，请在问题中包含可访问地址（如 http://host:port）"
            # Smart-mode fallback: if planner did not provide runnable arguments,
            # synthesize safe defaults for known browser skills.
            has_runnable = bool((args.get("command") or "").strip() or (args.get("template") or "").strip())
            if not has_runnable:
                if "agent-browser" in skill_name:
                    target_url = forced_url or "https://example.com"
                    args["command"] = (
                        f"npx agent-browser open {target_url} && "
                        "npx agent-browser get url && "
                        "npx agent-browser snapshot -i && "
                        "npx agent-browser screenshot --full"
                    )
                elif "playwright" in skill_name:
                    pw_url = forced_url or "https://example.com"
                    args["command"] = (
                        'node run.js "const dir = process.env.SCREENSHOT_DIR || \\"./media/screenshots\\"; '
                        'const { chromium } = require(\\"playwright\\"); '
                        'const browser = await chromium.launch({ headless: true }); '
                        'const page = await browser.newPage(); '
                        f'await page.goto(\\"{pw_url}\\"); '
                        'await page.screenshot({ path: dir + \\"/smart_example.png\\", fullPage: true }); '
                        'console.log(\\"saved\\", dir + \\"/smart_example.png\\"); '
                        'await browser.close();"'
                    )
            sess = str(plan.get("session_id") or "").strip() or None
            # Unified execution path: enqueue job and wait (async runner pipeline)
            smart_session_id = sess or data.tool_session_id or f"smart_{int(data.project_id)}_{user_id}"
            job_res = await create_skill_job(
                project_id=int(data.project_id),
                user_id=user_id,
                db=db,
                skill_id=int(data.skill_id),
                action_name="smart_plan",
                arguments=args,
                session_id=smart_session_id,
                runner_type=None,
            )
            job_id = int((((job_res or {}).get("data") or {}).get("job_id")) or 0)
            if not job_id:
                return None, "Skill任务创建失败"
            if stream_emit:
                await stream_emit(f"[SkillJob] 已入队: #{job_id}\n")

            # Poll job/events to completion
            start = time.time()
            last_seq = 0
            logs: List[str] = []
            timeout_s = 120
            status = "running"
            while time.time() - start < timeout_s:
                ev_rows = (
                    await db.execute(
                        select(SkillExecutionEventModel)
                        .where(
                            SkillExecutionEventModel.job_id == job_id,
                            SkillExecutionEventModel.seq > last_seq,
                            SkillExecutionEventModel.enabled_flag == 1,
                        )
                        .order_by(SkillExecutionEventModel.seq.asc())
                        .limit(200)
                    )
                ).scalars().all()
                for ev in ev_rows:
                    last_seq = int(ev.seq)
                    msg_line = str(ev.message or "")
                    logs.append(msg_line)
                    if stream_emit:
                        await stream_emit(f"[SkillEvent] {msg_line}\n")

                job = (
                    await db.execute(
                        select(SkillExecutionJobModel).where(
                            SkillExecutionJobModel.id == job_id,
                            SkillExecutionJobModel.enabled_flag == 1,
                        )
                    )
                ).scalar_one_or_none()
                if not job:
                    return None, "Skill任务不存在"
                status = str(job.status or "")
                if status in ("succeeded", "failed", "cancelled"):
                    break
                await asyncio.sleep(1.2)

            job = (
                await db.execute(
                    select(SkillExecutionJobModel).where(
                        SkillExecutionJobModel.id == job_id,
                        SkillExecutionJobModel.enabled_flag == 1,
                    )
                )
            ).scalar_one_or_none()
            if not job:
                return None, "Skill任务不存在"
            if status not in ("succeeded", "failed", "cancelled"):
                status = "failed"
            art_rows = (
                await db.execute(
                    select(SkillExecutionArtifactModel)
                    .where(
                        SkillExecutionArtifactModel.job_id == job_id,
                        SkillExecutionArtifactModel.enabled_flag == 1,
                    )
                    .order_by(SkillExecutionArtifactModel.id.asc())
                )
            ).scalars().all()
            screenshots = [
                {"id": int(a.id), "name": a.name, "relative_path": a.relative_path, "size": a.size}
                for a in art_rows
                if a.kind == "screenshots"
            ]
            artifacts = [
                {"id": int(a.id), "name": a.name, "relative_path": a.relative_path, "size": a.size}
                for a in art_rows
                if a.kind == "artifacts"
            ]
            result = {
                "ok": status == "succeeded",
                "skill_name": skill.name,
                "session_id": smart_session_id,
                "return_code": job.return_code,
                "stdout": job.stdout or ("\n".join(logs[-80:]) if logs else ""),
                "stderr": job.stderr or job.error_message or "",
                "screenshots": screenshots,
                "artifacts": artifacts,
            }
            status = "成功" if result.get("ok") else "失败"
            # Post-check: verify actual opened URL host if target URL exists.
            target_url = str(args.get("url") or "")
            actual_url = ""
            for line in str(result.get("stdout") or "").splitlines():
                s = line.strip()
                if s.startswith("http://") or s.startswith("https://"):
                    actual_url = s
            if target_url and actual_url:
                t_host = (urlparse(target_url).netloc or "").lower()
                a_host = (urlparse(actual_url).netloc or "").lower()
                if t_host and a_host and t_host != a_host:
                    result["ok"] = False
                    result["stderr"] = (
                        (str(result.get("stderr") or "") + "\n").strip()
                        + f"\n[URL_MISMATCH] 目标地址={target_url} 实际打开={actual_url}"
                    ).strip()
                    status = "失败"
            screenshots = result.get("screenshots") or []
            artifacts = result.get("artifacts") or []
            cmd_preview = str(args.get("command") or args.get("template") or "").strip()
            if len(cmd_preview) > 220:
                cmd_preview = cmd_preview[:220] + "..."
            project_id = int(data.project_id)
            sess_key = str(result.get("session_id") or "")
            ss_lines = []
            for x in screenshots[:8]:
                rel = str(x.get("relative_path") or "").replace("\\", "/")
                link = f"/uploads/skills/runtime/screenshots/{project_id}/{sess_key}/{rel}" if rel else ""
                if link:
                    ss_lines.append(f"- [{x.get('name')}]({link})")
                else:
                    ss_lines.append(f"- {x.get('name')} ({rel})")
            af_lines = []
            for x in artifacts[:8]:
                rel = str(x.get("relative_path") or "").replace("\\", "/")
                link = f"/uploads/skills/runtime/artifacts/{project_id}/{sess_key}/{rel}" if rel else ""
                if link:
                    af_lines.append(f"- [{x.get('name')}]({link})")
                else:
                    af_lines.append(f"- {x.get('name')} ({rel})")
            full_cmd = str(args.get("command") or args.get("template") or "").strip()
            steps_report = MessageService._build_detailed_test_steps_report(
                full_cmd,
                logs,
                job_return_code=int(result.get("return_code") or 0),
                stderr_blob=str(result.get("stderr") or ""),
            )
            text = (
                f"智能模式已调用 Skill `{result.get('skill_name')}`（{status}）。\n"
                f"执行会话: `{result.get('session_id') or '-'}`，返回码: `{result.get('return_code')}`。\n"
                f"执行命令/动作: `{cmd_preview or '-'}`\n\n"
                + (steps_report + "\n" if steps_report else "")
                + f"截图数量: {len(screenshots)}\n"
                + ("\n".join(ss_lines) + "\n\n" if ss_lines else "\n")
                + f"产物数量: {len(artifacts)}\n"
                + ("\n".join(af_lines) + "\n\n" if af_lines else "\n")
                + "stdout:\n"
                + f"{result.get('stdout') or '-'}\n\n"
                + "stderr:\n"
                + f"{result.get('stderr') or '-'}"
            )
            return text, f"Skill已调用: {skill.name}"
        except Exception as e:
            return None, f"Skill链路异常: {e}"

    @staticmethod
    async def _run_direct_tool_chain(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        data: SendMessageRequest,
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        provider = (data.tool_provider or "").strip().lower()
        if provider not in ("mcp", "skill"):
            raise ValueError("直连模式请指定 tool_provider（mcp/skill）")

        if provider == "skill":
            if not data.project_id:
                raise ValueError("Skill直连需要 project_id")
            skill_ref = (data.tool_name or "").strip()
            if not skill_ref:
                raise ValueError("Skill直连需要 tool_name（技能ID或名称）")
            arguments = data.tool_arguments if isinstance(data.tool_arguments, dict) else {}
            result = await run_skill_tool(
                project_id=int(data.project_id),
                user_id=user_id,
                db=db,
                skill_ref=skill_ref,
                arguments=arguments,
                session_id=data.tool_session_id,
            )
            assistant_text = (
                f"[直连模式] Skill `{result.get('skill_name')}` 执行"
                f"{'成功' if result.get('ok') else '失败'}。\n\n"
                f"stdout:\n{result.get('stdout') or '-'}\n\n"
                f"stderr:\n{result.get('stderr') or '-'}"
            )
            meta = {
                "tool_mode": "direct",
                "tool_provider": "skill",
                "tool_name": result.get("skill_name"),
                "tool_arguments": arguments,
                "tool_result": result,
            }
            return assistant_text, meta

        # provider == "mcp"
        if not (data.project_id and data.mcp_config_id):
            raise ValueError("MCP直连需要 project_id 和 mcp_config_id")
        tool_name = (data.tool_name or "").strip()
        if not tool_name:
            raise ValueError("MCP直连需要 tool_name")
        arguments = data.tool_arguments if isinstance(data.tool_arguments, dict) else {}

        start_ms = int(time.time() * 1000)
        call_res = await mcp_call_tool(
            project_id=int(data.project_id),
            user_id=user_id,
            config_id=int(data.mcp_config_id),
            db=db,
            tool_name=tool_name,
            arguments=arguments,
        )
        duration_ms = int(time.time() * 1000) - start_ms

        if (call_res or {}).get("code") != 200:
            msg = (call_res or {}).get("message") or "未知错误"
            await MessageService._record_mcp_execution(
                db,
                conversation_id,
                user_id,
                data,
                phase="forced_call",
                status="failed",
                tool_name=tool_name,
                tool_arguments=arguments,
                error_message=msg,
                duration_ms=duration_ms,
            )
            raise ValueError(f"MCP直连调用失败: {msg}")

        result = ((call_res or {}).get("data") or {}).get("result")
        await MessageService._record_mcp_execution(
            db,
            conversation_id,
            user_id,
            data,
            phase="forced_call",
            status="success",
            tool_name=tool_name,
            tool_arguments=arguments,
            output_summary=str(result)[:2000],
            duration_ms=duration_ms,
        )
        assistant_text = f"[直连模式] MCP工具 `{tool_name}` 执行完成。\n\n结果：\n{result}"
        meta = {
            "tool_mode": "direct",
            "tool_provider": "mcp",
            "tool_name": tool_name,
            "tool_arguments": arguments,
            "tool_result": result,
            "duration_ms": duration_ms,
        }
        return assistant_text, meta

    @staticmethod
    def _attachment_storage_file_name(att: Dict[str, Any]) -> Optional[str]:
        url = str(att.get("url") or att.get("file_url") or "").strip()
        if not url:
            return None
        if url.startswith("database://"):
            return url.replace("database://", "", 1).split("?", 1)[0] or None
        if "/api/v1/system/file/content/" in url:
            return url.split("/api/v1/system/file/content/")[-1].split("?", 1)[0] or None
        if "/" not in url and "\\" not in url and ".." not in url:
            return url
        return None

    @staticmethod
    def _is_text_like_attachment(att: Dict[str, Any]) -> bool:
        typ = str(att.get("type") or "").lower()
        name = str(att.get("name") or "").lower()
        if typ.startswith("text/") or typ in ("application/json", "application/xml"):
            return True
        return name.endswith((".txt", ".md", ".csv", ".json", ".xml", ".log", ".yaml", ".yml"))

    @staticmethod
    async def _build_text_attachment_prompt(
        db: AsyncSession,
        user_id: int,
        attachments: Optional[List[Dict[str, Any]]],
    ) -> Optional[str]:
        if not attachments:
            return None
        chunks: List[str] = []
        max_each = 48 * 1024
        for att in attachments:
            if not isinstance(att, dict) or not MessageService._is_text_like_attachment(att):
                continue
            fname = MessageService._attachment_storage_file_name(att)
            if not fname:
                continue
            raw = await FileService.read_file_bytes_for_user(fname, user_id, db)
            if not raw:
                continue
            if len(raw) > max_each:
                raw = raw[:max_each]
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("utf-8", errors="replace")
            label = str(att.get("name") or fname)
            chunks.append(f"### 附件《{label}》全文\n{text}")
        if not chunks:
            return None
        return (
            "用户上传了以下文本类附件，请基于这些内容回答（若与问题无关可简要说明）。\n"
            + "\n\n".join(chunks)
        )
    
    @staticmethod
    async def get_message_list(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[MessageModel], int]:
        """获取消息列表"""
        # 验证对话权限
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)
        if not conversation:
            return [], 0
        
        # 查询总数
        count_stmt = select(func.count(MessageModel.id)).where(
            MessageModel.conversation_id == conversation_id,
            MessageModel.enabled_flag == 1
        )
        result = await db.execute(count_stmt)
        total = result.scalar()
        
        # 查询列表
        stmt = select(MessageModel).where(
            MessageModel.conversation_id == conversation_id,
            MessageModel.enabled_flag == 1
        ).order_by(MessageModel.creation_date).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        return messages, total
    
    @staticmethod
    async def create_message(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        role: str,
        content: str,
        message_type: str = "text",
        meta_data: Optional[Dict[str, Any]] = None,
        tokens_used: Optional[int] = None
    ) -> MessageModel:
        """创建消息"""
        message = MessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_type=message_type,
            meta_data=meta_data,
            tokens_used=tokens_used,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        return message
    
    @staticmethod
    async def _record_mcp_execution(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        data: SendMessageRequest,
        *,
        phase: str,
        status: str,
        tool_name: Optional[str] = None,
        tool_arguments: Optional[Dict[str, Any]] = None,
        output_summary: Optional[str] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
    ) -> None:
        try:
            rec = MCPExecutionRecordModel(
                conversation_id=conversation_id,
                user_id=user_id,
                project_id=data.project_id,
                knowledge_base_id=data.knowledge_base_id,
                mcp_config_id=data.mcp_config_id,
                phase=phase,
                tool_name=tool_name,
                tool_arguments=tool_arguments,
                status=status,
                duration_ms=duration_ms,
                output_summary=output_summary,
                error_message=error_message,
                created_by=user_id,
                updated_by=user_id,
            )
            db.add(rec)
            await db.commit()
        except Exception:
            await db.rollback()

    @staticmethod
    async def _build_rag_system_prompt(
        db: AsyncSession,
        user_id: int,
        data: SendMessageRequest,
    ) -> tuple[Optional[str], str]:
        if not MessageService._kb_explicitly_enabled(data):
            return None, "知识库未开启"
        try:
            rag = await query_knowledge_base(
                project_id=int(data.project_id),
                user_id=user_id,
                kb_id=int(data.knowledge_base_id),
                db=db,
                query=data.content,
                top_k=5,
            )
            results = ((rag or {}).get("data") or {}).get("results") or []
            if not results:
                return (
                    "当前已启用知识库检索，但未检索到相关片段。请明确告诉用户“本次未命中知识库内容”，不要虚构来源。",
                    "知识库已检索但无命中",
                )
            refs = []
            for idx, item in enumerate(results[:5], start=1):
                title = ((item.get("metadata") or {}).get("document_title") or "").strip() or f"片段{idx}"
                content = (item.get("content") or "").strip()
                if content:
                    refs.append(f"[{idx}] {title}\n{content}")
            if not refs:
                return (
                    "当前已启用知识库检索，但未检索到可用片段。请明确告知用户本次未命中知识库内容。",
                    "知识库结果为空",
                )
            return (
                "你可以参考以下知识库检索片段回答用户问题。若片段不足以支持结论，请明确说明。\n\n"
                + "\n\n".join(refs)
            ), f"知识库命中 {len(refs)} 条片段"
        except Exception as e:
            return (
                "当前已启用知识库检索，但检索过程出现异常。请明确告诉用户“知识库检索失败，已退回基础回答”。",
                f"知识库检索异常: {e}",
            )

    @staticmethod
    async def _run_mcp_chain(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        data: SendMessageRequest,
        llm_messages: List[LLMMessage],
    ) -> tuple[Optional[str], str]:
        if not (data.use_mcp and data.project_id and data.mcp_config_id):
            return None, "MCP未开启"
        start_ms = int(time.time() * 1000)
        try:
            tools_res = await mcp_list_tools(
                project_id=int(data.project_id),
                user_id=user_id,
                config_id=int(data.mcp_config_id),
                db=db,
            )
            tools = ((tools_res or {}).get("data") or {}).get("tools") or []
            if not tools:
                await MessageService._record_mcp_execution(
                    db,
                    conversation_id,
                    user_id,
                    data,
                    phase="tool_list",
                    status="failed",
                    error_message=f"MCP工具列表为空: {(tools_res or {}).get('message') or '未知原因'}",
                    duration_ms=int(time.time() * 1000) - start_ms,
                )
                return None, f"MCP工具列表为空: {(tools_res or {}).get('message') or '未知原因'}"

            tool_descriptions = []
            for t in tools[:20]:
                tool_descriptions.append(f"- {t.get('name')}: {t.get('description') or ''}")
            planner_prompt = (
                "你是工具路由器。基于用户问题与工具列表，判断是否需要调用工具。"
                "仅输出 JSON，不要输出其他文本。\n"
                "格式: {\"use_tool\": true|false, \"tool_name\": \"...\", \"arguments\": {...}}\n"
                "若不需要工具，输出 {\"use_tool\": false, \"tool_name\": \"\", \"arguments\": {}}\n\n"
                f"工具列表:\n{chr(10).join(tool_descriptions)}\n\n"
                f"用户问题:\n{data.content}"
            )

            if llm_messages and llm_messages[-1].role == "user":
                llm_messages[-1] = LLMMessage(role="user", content=planner_prompt)
            else:
                llm_messages.append(LLMMessage(role="user", content=planner_prompt))

            llm_service = await get_llm_service()
            plan_resp = await llm_service.chat_completion(messages=llm_messages, stream=False)
            raw = (plan_resp.content or "").strip()
            if raw.startswith("```"):
                raw = raw.strip("`")
                raw = raw.replace("json", "", 1).strip()

            try:
                plan = json.loads(raw)
            except Exception:
                l = raw.find("{")
                r = raw.rfind("}")
                if l >= 0 and r > l:
                    plan = json.loads(raw[l : r + 1])
                else:
                    await MessageService._record_mcp_execution(
                        db,
                        conversation_id,
                        user_id,
                        data,
                        phase="auto_plan",
                        status="failed",
                        error_message=f"MCP规划结果无法解析: {raw[:300]}",
                        duration_ms=int(time.time() * 1000) - start_ms,
                    )
                    return None, f"MCP规划结果无法解析: {raw[:160]}"
            if not plan.get("use_tool"):
                await MessageService._record_mcp_execution(
                    db,
                    conversation_id,
                    user_id,
                    data,
                    phase="auto_plan",
                    status="skipped",
                    output_summary="模型判定无需调用工具",
                    duration_ms=int(time.time() * 1000) - start_ms,
                )
                return None, "MCP规划判定无需调用工具"

            tool_name = (plan.get("tool_name") or "").strip()
            args = plan.get("arguments") or {}
            if not tool_name:
                await MessageService._record_mcp_execution(
                    db,
                    conversation_id,
                    user_id,
                    data,
                    phase="auto_plan",
                    status="failed",
                    error_message="规划未返回工具名",
                    duration_ms=int(time.time() * 1000) - start_ms,
                )
                return None, "MCP规划未返回工具名"

            call_res = await mcp_call_tool(
                project_id=int(data.project_id),
                user_id=user_id,
                config_id=int(data.mcp_config_id),
                db=db,
                tool_name=tool_name,
                arguments=args if isinstance(args, dict) else {},
            )
            if (call_res or {}).get("code") != 200:
                await MessageService._record_mcp_execution(
                    db,
                    conversation_id,
                    user_id,
                    data,
                    phase="tool_call",
                    status="failed",
                    tool_name=tool_name,
                    tool_arguments=args if isinstance(args, dict) else {},
                    error_message=(call_res or {}).get("message") or "未知错误",
                    duration_ms=int(time.time() * 1000) - start_ms,
                )
                return None, f"MCP工具调用失败: {(call_res or {}).get('message') or '未知错误'}"
            result = ((call_res or {}).get("data") or {}).get("result")
            await MessageService._record_mcp_execution(
                db,
                conversation_id,
                user_id,
                data,
                phase="tool_call",
                status="success",
                tool_name=tool_name,
                tool_arguments=args if isinstance(args, dict) else {},
                output_summary=str(result)[:2000],
                duration_ms=int(time.time() * 1000) - start_ms,
            )
            return f"已调用 MCP 工具 `{tool_name}`，返回结果:\n{result}", f"MCP已调用工具: {tool_name}"
        except Exception as e:
            await MessageService._record_mcp_execution(
                db,
                conversation_id,
                user_id,
                data,
                phase="tool_call",
                status="failed",
                error_message=str(e),
                duration_ms=int(time.time() * 1000) - start_ms,
            )
            return None, f"MCP链路异常: {e}"

    @staticmethod
    async def send_message(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        data: SendMessageRequest
    ) -> tuple[MessageModel, MessageModel, Optional[int]]:
        """发送消息并获取AI响应"""
        # 验证对话权限
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversation not found")
        
        # 1. 保存用户消息
        user_message = await MessageService.create_message(
            db,
            conversation_id,
            user_id,
            "user",
            data.content,
            meta_data={"attachments": data.attachments} if data.attachments else None,
        )
        
        # 2. 直连模式：跳过LLM，直接执行工具
        if MessageService._is_direct_mode(data):
            assistant_text, assistant_meta = await MessageService._run_direct_tool_chain(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id,
                data=data,
            )
            assistant_message = await MessageService.create_message(
                db,
                conversation_id,
                user_id,
                "assistant",
                assistant_text,
                meta_data=assistant_meta,
                tokens_used=0,
            )
            if not conversation.title or conversation.title == "新对话":
                conversation.title = data.content[:30] + ("..." if len(data.content) > 30 else "")
                conversation.updated_by = user_id
                await db.commit()
            return user_message, assistant_message, 0

        # 3. 获取对话历史
        messages, _ = await MessageService.get_message_list(db, conversation_id, user_id, limit=50)
        
        # 4. 构建LLM消息列表
        llm_messages = []
        if not MessageService._kb_explicitly_enabled(data):
            llm_messages.append(
                LLMMessage(
                    role="system",
                    content="未启用知识库检索。请仅根据用户消息与下方附件内容回答，不要提及知识库命中、未命中、检索失败或知识库状态。",
                )
            )
        text_att = await MessageService._build_text_attachment_prompt(db, user_id, data.attachments)
        if text_att:
            llm_messages.append(LLMMessage(role="system", content=text_att))
        rag_prompt, rag_status = await MessageService._build_rag_system_prompt(db, user_id, data)
        if rag_prompt:
            llm_messages.append(LLMMessage(role="system", content=rag_prompt))
        if MessageService._kb_explicitly_enabled(data):
            llm_messages.append(LLMMessage(role="system", content=f"[知识库状态]{rag_status}"))
        for msg in messages:
            llm_messages.append(LLMMessage(role=msg.role, content=msg.content))

        mcp_result, mcp_status = await MessageService._run_mcp_chain(db, conversation_id, user_id, data, llm_messages.copy())
        if mcp_result:
            llm_messages.append(LLMMessage(role="system", content=mcp_result))
        if data.use_mcp:
            llm_messages.append(LLMMessage(role="system", content=f"[MCP状态]{mcp_status}"))
        skill_result, skill_status = await MessageService._run_skill_chain(db, user_id, data, llm_messages.copy())
        if skill_result:
            llm_messages.append(LLMMessage(role="system", content=skill_result))
        if data.use_skill:
            llm_messages.append(LLMMessage(role="system", content=f"[Skill状态]{skill_status}"))
        # Smart + skill: return full test execution result directly (no extra AI summary)
        if data.use_skill and skill_result:
            assistant_message = await MessageService.create_message(
                db,
                conversation_id,
                user_id,
                "assistant",
                skill_result,
                tokens_used=0,
            )
            if not conversation.title or conversation.title == "新对话":
                conversation.title = data.content[:30] + ("..." if len(data.content) > 30 else "")
                conversation.updated_by = user_id
                await db.commit()
            return user_message, assistant_message, 0
        
        # 5. 调用LLM服务
        if conversation.llm_config_id:
            llm_service = await get_llm_service_by_id(conversation.llm_config_id)
        else:
            llm_service = await get_llm_service()
        llm_messages = MessageService._apply_llm_runtime_controls(llm_messages, llm_service, data)
        
        response = await llm_service.chat_completion(
            messages=llm_messages,
            stream=False
        )
        
        # 6. 保存AI响应
        assistant_message = await MessageService.create_message(
            db,
            conversation_id,
            user_id,
            "assistant",
            response.content,
            tokens_used=response.total_tokens
        )
        
        # 7. 更新对话标题（如果是第一条消息）
        if not conversation.title or conversation.title == "新对话":
            # 使用用户第一条消息的前30个字符作为标题
            conversation.title = data.content[:30] + ("..." if len(data.content) > 30 else "")
            conversation.updated_by = user_id
            await db.commit()
        
        return user_message, assistant_message, response.total_tokens
    
    @staticmethod
    async def send_message_stream(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        data: SendMessageRequest
    ):
        """发送消息并获取AI流式响应（生成器）"""
        # 验证对话权限
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversation not found")
        
        # 1. 保存用户消息
        user_message = await MessageService.create_message(
            db,
            conversation_id,
            user_id,
            "user",
            data.content,
            meta_data={"attachments": data.attachments} if data.attachments else None,
        )
        
        # 发送用户消息事件
        yield {
            "type": "user_message",
            "data": {
                "id": user_message.id,
                "role": "user",
                "content": user_message.content,
                "creation_date": user_message.creation_date.isoformat()
            }
        }
        
        # 2. 直连模式：跳过LLM，直接执行工具
        if MessageService._is_direct_mode(data):
            assistant_text, assistant_meta = await MessageService._run_direct_tool_chain(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id,
                data=data,
            )
            yield {
                "type": "content",
                "data": {
                    "content": assistant_text
                }
            }
            assistant_message = await MessageService.create_message(
                db,
                conversation_id,
                user_id,
                "assistant",
                assistant_text,
                meta_data=assistant_meta,
                tokens_used=0,
            )
            yield {
                "type": "assistant_message",
                "data": {
                    "id": assistant_message.id,
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tokens_used": assistant_message.tokens_used,
                    "creation_date": assistant_message.creation_date.isoformat()
                }
            }
            if not conversation.title or conversation.title == "新对话":
                conversation.title = data.content[:30] + ("..." if len(data.content) > 30 else "")
                conversation.updated_by = user_id
                await db.commit()
            return

        # 3. 获取对话历史
        messages, _ = await MessageService.get_message_list(db, conversation_id, user_id, limit=50)
        
        # 4. 构建LLM消息列表
        llm_messages = []
        if not MessageService._kb_explicitly_enabled(data):
            llm_messages.append(
                LLMMessage(
                    role="system",
                    content="未启用知识库检索。请仅根据用户消息与下方附件内容回答，不要提及知识库命中、未命中、检索失败或知识库状态。",
                )
            )
        text_att = await MessageService._build_text_attachment_prompt(db, user_id, data.attachments)
        if text_att:
            llm_messages.append(LLMMessage(role="system", content=text_att))
        rag_prompt, rag_status = await MessageService._build_rag_system_prompt(db, user_id, data)
        if rag_prompt:
            llm_messages.append(LLMMessage(role="system", content=rag_prompt))
        if MessageService._kb_explicitly_enabled(data):
            llm_messages.append(LLMMessage(role="system", content=f"[知识库状态]{rag_status}"))
        for msg in messages:
            llm_messages.append(LLMMessage(role=msg.role, content=msg.content))

        mcp_result, mcp_status = await MessageService._run_mcp_chain(db, conversation_id, user_id, data, llm_messages.copy())
        if mcp_result:
            llm_messages.append(LLMMessage(role="system", content=mcp_result))
        if data.use_mcp:
            llm_messages.append(LLMMessage(role="system", content=f"[MCP状态]{mcp_status}"))
        if data.use_skill:
            yield {
                "type": "content",
                "data": {"content": "\n[Skill] 正在规划测试步骤并准备执行...\n"},
            }
        event_queue: "asyncio.Queue[Dict[str, Any]]" = asyncio.Queue()

        async def _emit_skill_stream(text: str):
            await event_queue.put(
                {
                    "type": "content",
                    "data": {"content": text},
                }
            )

        skill_task = asyncio.create_task(
            MessageService._run_skill_chain(
                db,
                user_id,
                data,
                llm_messages.copy(),
                stream_emit=_emit_skill_stream,
            )
        )

        # Real-time drain queue while skill chain is running
        while True:
            if skill_task.done() and event_queue.empty():
                break
            try:
                ev = await asyncio.wait_for(event_queue.get(), timeout=0.8)
                yield ev
            except asyncio.TimeoutError:
                continue

        skill_result, skill_status = await skill_task
        if data.use_skill:
            yield {
                "type": "content",
                "data": {"content": f"[Skill状态] {skill_status}\n"},
            }
        if skill_result:
            # Stream raw tool execution evidence first, then let LLM summarize.
            yield {
                "type": "content",
                "data": {
                    "content": f"\n[Skill执行过程]\n{skill_result}\n"
                },
            }
            llm_messages.append(LLMMessage(role="system", content=skill_result))
        if data.use_skill:
            llm_messages.append(LLMMessage(role="system", content=f"[Skill状态]{skill_status}"))
        # Smart + skill: stream execution result only, no extra LLM summary.
        if data.use_skill and skill_result:
            assistant_message = await MessageService.create_message(
                db,
                conversation_id,
                user_id,
                "assistant",
                skill_result,
                tokens_used=0,
            )
            yield {
                "type": "assistant_message",
                "data": {
                    "id": assistant_message.id,
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tokens_used": assistant_message.tokens_used,
                    "creation_date": assistant_message.creation_date.isoformat(),
                },
            }
            if not conversation.title or conversation.title == "新对话":
                conversation.title = data.content[:30] + ("..." if len(data.content) > 30 else "")
                conversation.updated_by = user_id
                await db.commit()
            return
        
        # 5. 调用LLM服务（流式）
        if conversation.llm_config_id:
            llm_service = await get_llm_service_by_id(conversation.llm_config_id)
        else:
            llm_service = await get_llm_service()
        llm_messages = MessageService._apply_llm_runtime_controls(llm_messages, llm_service, data)
        
        # 收集完整的响应内容
        full_content = ""
        
        # 流式获取响应；若模型未返回 chunk（部分兼容模型常见），自动降级到非流式
        got_chunk = False
        try:
            stream = await llm_service.chat_completion(
                messages=llm_messages,
                stream=True
            )
            async for chunk in stream:
                if not chunk:
                    continue
                got_chunk = True
                full_content += chunk
                # 发送内容块事件
                yield {
                    "type": "content",
                    "data": {
                        "content": chunk
                    }
                }
        except Exception:
            got_chunk = False

        if not got_chunk:
            fallback_resp = await llm_service.chat_completion(
                messages=llm_messages,
                stream=False
            )
            full_content = (fallback_resp.content or "").strip()
            if full_content:
                yield {
                    "type": "content",
                    "data": {
                        "content": full_content
                    }
                }

        # 6. 保存AI响应
        assistant_message = await MessageService.create_message(
            db,
            conversation_id,
            user_id,
            "assistant",
            full_content,
            tokens_used=len(full_content)  # 简单估算，实际应该从LLM响应中获取
        )
        
        # 发送完成事件
        yield {
            "type": "assistant_message",
            "data": {
                "id": assistant_message.id,
                "role": "assistant",
                "content": assistant_message.content,
                "tokens_used": assistant_message.tokens_used,
                "creation_date": assistant_message.creation_date.isoformat()
            }
        }
        
        # 7. 更新对话标题（如果是第一条消息）
        if not conversation.title or conversation.title == "新对话":
            conversation.title = data.content[:30] + ("..." if len(data.content) > 30 else "")
            conversation.updated_by = user_id
            await db.commit()

    @staticmethod
    async def get_mcp_execution_records(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)
        if not conversation:
            return []
        stmt = (
            select(MCPExecutionRecordModel)
            .where(
                MCPExecutionRecordModel.conversation_id == conversation_id,
                MCPExecutionRecordModel.user_id == user_id,
                MCPExecutionRecordModel.enabled_flag == 1,
            )
            .order_by(desc(MCPExecutionRecordModel.creation_date))
            .limit(limit)
        )
        rows = (await db.execute(stmt)).scalars().all()
        return [
            {
                "id": r.id,
                "phase": r.phase,
                "status": r.status,
                "tool_name": r.tool_name,
                "tool_arguments": r.tool_arguments,
                "output_summary": r.output_summary,
                "error_message": r.error_message,
                "duration_ms": r.duration_ms,
                "creation_date": r.creation_date,
            }
            for r in rows
        ]

