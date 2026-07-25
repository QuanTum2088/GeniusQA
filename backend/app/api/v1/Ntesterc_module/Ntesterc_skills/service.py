#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, List
from fastapi import HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.Ntesterc_module.Ntesterc_project.service import ProjectService
from app.api.v1.Ntesterc_module.Ntesterc_skills.model import ProjectSkillModel
from app.api.v1.Ntesterc_module.Ntesterc_skills.execution_model import SkillExecutionArtifactModel, SkillExecutionEventModel, SkillExecutionJobModel
from app.common.response import page_response, success_response

SKILL_ROOT = Path(os.getenv("SKILL_UPLOAD_DIR", "uploads/skills"))
DEFAULT_RUNNER_TYPE = (os.getenv("SKILL_RUNNER_TYPE") or "local").strip().lower()  # local/docker


async def _check_member(project_id: int, user_id: int, db: AsyncSession) -> None:
    await ProjectService._check_project_member(project_id, user_id, db)  # noqa: SLF001


async def _check_role(project_id: int, user_id: int, roles: List[str], db: AsyncSession) -> None:
    await ProjectService._check_project_permission(project_id, user_id, roles, db)  # noqa: SLF001


def _iso(dt) -> Optional[str]:
    if not dt:
        return None
    return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


def _safe_skill_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", (name or "").strip())[:120]


def _parse_skill_description(skill_dir: Path) -> str:
    md = skill_dir / "SKILL.md"
    if not md.exists():
        return ""
    try:
        text = md.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            return s.lstrip("#").strip()[:255]
        return s[:255]
    return ""


def _parse_skill_md(md_path: Path) -> dict:
    """
    Parse SKILL.md with optional YAML-like frontmatter:
    ---
    name: xxx
    description: yyy
    allowed-tools: Bash(cmd1), Bash(cmd2)
    ---
    """
    try:
        text = md_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}
    lines = text.splitlines()
    if len(lines) >= 3 and lines[0].strip() == "---":
        meta = {}
        i = 1
        while i < len(lines):
            if lines[i].strip() == "---":
                break
            line = lines[i].strip()
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip()
            i += 1
        return meta
    return {}


def _scan_skill_pack(repo_dir: Path) -> List[dict]:
    """
    Scan repo_dir/skills/**/SKILL.md and return list of skill dict:
    {name, description, allowed_tools, skill_dir}
    """
    skills_dir = repo_dir / "skills"
    if not skills_dir.exists():
        return []
    items = []
    for md in skills_dir.rglob("SKILL.md"):
        meta = _parse_skill_md(md)
        name = (meta.get("name") or md.parent.name).strip()
        desc = (meta.get("description") or "").strip() or _parse_skill_description(md.parent)
        allowed = (meta.get("allowed-tools") or meta.get("allowed_tools") or "").strip()
        items.append(
            {
                "name": name,
                "description": desc,
                "allowed_tools": allowed,
                "skill_dir": md.parent,
            }
        )
    return items


def _build_skill_runtime_dirs(project_id: int, session_key: str) -> tuple[Path, Path]:
    screenshots_dir = SKILL_ROOT / "runtime" / "screenshots" / str(project_id) / session_key
    artifacts_dir = SKILL_ROOT / "runtime" / "artifacts" / str(project_id) / session_key
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    return screenshots_dir, artifacts_dir


def _collect_files(base_dir: Path) -> List[dict]:
    if not base_dir.exists():
        return []
    files: List[dict] = []
    for p in base_dir.rglob("*"):
        if p.is_file():
            rel = str(p.relative_to(base_dir)).replace("\\", "/")
            files.append({"name": p.name, "relative_path": rel, "size": p.stat().st_size})
    return files


def _list_templates(skill_dir: Path) -> List[dict]:
    tdir = skill_dir / "templates"
    if not tdir.exists():
        return []
    items: List[dict] = []
    for p in sorted(tdir.glob("*")):
        if p.is_file():
            items.append({"name": p.name, "relative_path": f"templates/{p.name}", "size": p.stat().st_size})
    return items


def _quote_cmd_arg(value: str) -> str:
    # Compatible with cmd/powershell shell parsing for common paths/args
    return '"' + str(value).replace('"', '\\"') + '"'


def _smart_decode(data: bytes | str | None) -> str:
    if data is None:
        return ""
    if isinstance(data, str):
        return data
    for enc in ("utf-8", "gbk"):
        try:
            return data.decode(enc)
        except Exception:
            continue
    return data.decode("utf-8", errors="ignore")


def _inject_agent_browser_session(command: str, session_id: Optional[str]) -> str:
    cmd = (command or "").strip()
    sid = (session_id or "").strip()
    if not cmd or not sid:
        return cmd
    # Already has session options
    if re.search(r"--session-name\s+\S+|--session\s+\S+", cmd, flags=re.IGNORECASE):
        return cmd
    # npx agent-browser ...
    cmd = re.sub(
        r"\bnpx\s+agent-browser\b",
        f"npx agent-browser --session-name {sid}",
        cmd,
        count=1,
        flags=re.IGNORECASE,
    )
    # agent-browser ...
    cmd = re.sub(
        r"(?<!npx\s)\bagent-browser\b",
        f"agent-browser --session-name {sid}",
        cmd,
        count=1,
        flags=re.IGNORECASE,
    )
    return cmd


def _resolve_skill_command(
    *,
    entry_command: str,
    skill_dir: Path,
    arguments: Optional[dict],
) -> str:
    cmd = (entry_command or "").strip()
    if cmd:
        return cmd
    args = arguments or {}
    override_cmd = str(args.get("command") or args.get("__command") or "").strip()
    if override_cmd:
        return override_cmd

    template = str(args.get("template") or "").strip()
    if template:
        template_name = Path(template).name
        template_path = skill_dir / "templates" / template_name
        if not template_path.exists() or not template_path.is_file():
            raise HTTPException(status_code=400, detail=f"模板不存在: {template_name}")
        template_args = args.get("template_args")
        if not isinstance(template_args, list):
            template_args = []
        tail = " ".join(_quote_cmd_arg(str(x)) for x in template_args)
        # agent-browser templates are shell scripts; run with bash explicitly.
        if template_path.suffix.lower() == ".sh":
            return f"bash {_quote_cmd_arg(str(template_path))}" + (f" {tail}" if tail else "")
        return _quote_cmd_arg(str(template_path)) + (f" {tail}" if tail else "")

    return ""


async def get_skill_manifest(project_id: int, user_id: int, skill_id: int, db: AsyncSession) -> dict:
    await _check_member(project_id, user_id, db)
    stmt = select(ProjectSkillModel).where(
        ProjectSkillModel.id == skill_id,
        ProjectSkillModel.project_id == project_id,
        ProjectSkillModel.user_id == user_id,
        ProjectSkillModel.enabled_flag == 1,
    )
    m = (await db.execute(stmt)).scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="技能不存在")
    skill_dir = Path(m.skill_path or "")
    extra = m.extra_config or {}
    allowed = (extra.get("allowed_tools") or "").strip()
    templates = _list_templates(skill_dir) if skill_dir.exists() else []
    return success_response(
        data={
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "scenario_category": m.scenario_category,
            "source_type": m.source_type,
            "repo_url": m.repo_url,
            "skill_path": m.skill_path,
            "entry_command": m.entry_command,
            "is_active": m.is_active,
            "allowed_tools": allowed,
            "templates": templates,
            "extra_config": extra,
        },
        message="查询成功",
    )


async def list_skills(
    project_id: int,
    user_id: int,
    db: AsyncSession,
    search: str = "",
    scenario_category: str = "",
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    await _check_member(project_id, user_id, db)
    q = select(ProjectSkillModel).where(
        ProjectSkillModel.project_id == project_id,
        ProjectSkillModel.user_id == user_id,
        ProjectSkillModel.enabled_flag == 1,
    )
    if search:
        q = q.where(ProjectSkillModel.name.contains(search))
    if scenario_category:
        q = q.where(ProjectSkillModel.scenario_category == scenario_category)
    if is_active is not None:
        q = q.where(ProjectSkillModel.is_active == is_active)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
    q = q.order_by(ProjectSkillModel.id.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(q)).scalars().all()
    items = [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "scenario_category": r.scenario_category,
            "source_type": r.source_type,
            "repo_url": r.repo_url,
            "skill_path": r.skill_path,
            "entry_command": r.entry_command,
            "is_active": r.is_active,
            "extra_config": r.extra_config or {},
            "allowed_tools": ((r.extra_config or {}).get("allowed_tools") or ""),
            "created_at": _iso(r.creation_date),
            "updated_at": _iso(r.updation_date),
        }
        for r in rows
    ]
    return page_response(items, total, page, page_size, "查询成功")


async def create_skill(project_id: int, user_id: int, db: AsyncSession, data: dict) -> dict:
    await _check_role(project_id, user_id, ["owner", "admin", "developer"], db)
    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="技能名称不能为空")
    dup = await db.execute(
        select(ProjectSkillModel.id).where(
            ProjectSkillModel.project_id == project_id,
            ProjectSkillModel.user_id == user_id,
            ProjectSkillModel.name == name,
            ProjectSkillModel.enabled_flag == 1,
        )
    )
    if dup.scalar():
        raise HTTPException(status_code=400, detail="技能名称已存在")
    m = ProjectSkillModel(
        project_id=project_id,
        user_id=user_id,
        name=name,
        description=data.get("description"),
        scenario_category=data.get("scenario_category"),
        source_type=(data.get("source_type") or "builtin").strip().lower(),
        repo_url=data.get("repo_url"),
        skill_path=data.get("skill_path"),
        entry_command=data.get("entry_command"),
        is_active=bool(data.get("is_active", True)),
        extra_config=data.get("extra_config") if isinstance(data.get("extra_config"), dict) else {},
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return success_response(data={"id": m.id}, message="创建成功")


async def update_skill(project_id: int, user_id: int, skill_id: int, db: AsyncSession, data: dict) -> dict:
    await _check_role(project_id, user_id, ["owner", "admin", "developer"], db)
    stmt = select(ProjectSkillModel).where(
        ProjectSkillModel.id == skill_id,
        ProjectSkillModel.project_id == project_id,
        ProjectSkillModel.user_id == user_id,
        ProjectSkillModel.enabled_flag == 1,
    )
    m = (await db.execute(stmt)).scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="技能不存在")
    if data.get("name"):
        new_name = str(data["name"]).strip()
        dup = await db.execute(
            select(ProjectSkillModel.id).where(
                ProjectSkillModel.project_id == project_id,
                ProjectSkillModel.user_id == user_id,
                ProjectSkillModel.name == new_name,
                ProjectSkillModel.id != skill_id,
                ProjectSkillModel.enabled_flag == 1,
            )
        )
        if dup.scalar():
            raise HTTPException(status_code=400, detail="技能名称已存在")
        m.name = new_name
    for f in ("description", "scenario_category", "repo_url", "skill_path", "entry_command"):
        if f in data:
            setattr(m, f, data.get(f))
    if "source_type" in data and data.get("source_type"):
        m.source_type = str(data.get("source_type")).strip().lower()
    if "is_active" in data:
        m.is_active = bool(data.get("is_active"))
    if "extra_config" in data and isinstance(data.get("extra_config"), dict):
        m.extra_config = data.get("extra_config")
    m.updated_by = user_id
    await db.commit()
    await db.refresh(m)
    return success_response(data={"id": m.id}, message="更新成功")


async def delete_skill(project_id: int, user_id: int, skill_id: int, db: AsyncSession) -> dict:
    await _check_role(project_id, user_id, ["owner", "admin"], db)
    stmt = select(ProjectSkillModel).where(
        ProjectSkillModel.id == skill_id,
        ProjectSkillModel.project_id == project_id,
        ProjectSkillModel.user_id == user_id,
        ProjectSkillModel.enabled_flag == 1,
    )
    m = (await db.execute(stmt)).scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="技能不存在")
    m.enabled_flag = 0
    m.updated_by = user_id
    await db.commit()
    return success_response(message="删除成功")


async def import_skill_from_git(project_id: int, user_id: int, db: AsyncSession, data: dict) -> dict:
    await _check_role(project_id, user_id, ["owner", "admin", "developer"], db)
    repo_url = str(data.get("repo_url") or "").strip()
    if not repo_url:
        raise HTTPException(status_code=400, detail="repo_url 不能为空")
    name = _safe_skill_name(str(data.get("name") or Path(repo_url).stem or "skill"))
    base_dir = SKILL_ROOT / str(project_id) / str(user_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    dst = base_dir / f"{secrets.token_hex(6)}_{name}"
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(dst)],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
    except Exception as e:
        shutil.rmtree(dst, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f"拉取仓库失败: {e}")

    payload = {
        "scenario_category": data.get("scenario_category"),
        "source_type": "gitee" if "gitee.com" in repo_url else "github" if "github.com" in repo_url else "git",
        "repo_url": repo_url,
        "is_active": True,
    }

    # If repo is a skill pack (multi-SKILL.md layout), create one record per SKILL.md under /skills
    pack = _scan_skill_pack(dst)
    if pack:
        created_ids: List[int] = []
        for item in pack:
            skill_name = _safe_skill_name(item["name"])
            extra = {
                "allowed_tools": item.get("allowed_tools") or "",
                "pack_root": str(dst),
            }
            res = await create_skill(
                project_id,
                user_id,
                db,
                {
                    "name": skill_name,
                    "description": item.get("description"),
                    "scenario_category": payload.get("scenario_category") or skill_name,
                    "source_type": payload["source_type"],
                    "repo_url": repo_url,
                    "skill_path": str(item["skill_dir"]),
                    # entry_command left empty: prefer SKILL.md allowed-tools / templates
                    "entry_command": str(data.get("entry_command") or "").strip() or None,
                    "is_active": True,
                    "extra_config": extra,
                },
            )
            created_ids.append(int(((res or {}).get("data") or {}).get("id") or 0))
        return success_response(data={"created": created_ids, "count": len(created_ids)}, message="导入成功")

    # Fallback: treat repo root as a single skill
    res = await create_skill(
        project_id,
        user_id,
        db,
        {
            "name": name,
            "description": str(data.get("description") or _parse_skill_description(dst)),
            "scenario_category": payload.get("scenario_category"),
            "source_type": payload["source_type"],
            "repo_url": repo_url,
            "skill_path": str(dst),
            "entry_command": str(data.get("entry_command") or "").strip() or None,
            "is_active": True,
            "extra_config": data.get("extra_config") if isinstance(data.get("extra_config"), dict) else {},
        },
    )
    return success_response(data={"created": [((res or {}).get("data") or {}).get("id")], "count": 1}, message="导入成功")


async def import_skill_from_upload(
    project_id: int,
    user_id: int,
    db: AsyncSession,
    file: UploadFile,
    scenario_category: Optional[str] = None,
    entry_command: Optional[str] = None,
) -> dict:
    await _check_role(project_id, user_id, ["owner", "admin", "developer"], db)
    filename = file.filename or "skill.zip"
    if not filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="仅支持 zip 包上传")
    base_dir = SKILL_ROOT / str(project_id) / str(user_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    name = _safe_skill_name(Path(filename).stem or "skill")
    dst = base_dir / f"{secrets.token_hex(6)}_{name}"
    dst.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tf:
        raw = await file.read()
        tf.write(raw)
        zip_path = Path(tf.name)
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dst)
    except Exception as e:
        shutil.rmtree(dst, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f"解压失败: {e}")
    finally:
        try:
            zip_path.unlink(missing_ok=True)
        except Exception:
            pass
    payload = {
        "name": name,
        "description": _parse_skill_description(dst),
        "scenario_category": scenario_category,
        "source_type": "upload",
        "repo_url": None,
        "skill_path": str(dst),
        "entry_command": (entry_command or "").strip() or None,
        "is_active": True,
        "extra_config": {},
    }

    pack = _scan_skill_pack(dst)
    if pack:
        created_ids: List[int] = []
        for item in pack:
            skill_name = _safe_skill_name(item["name"])
            extra = {
                "allowed_tools": item.get("allowed_tools") or "",
                "pack_root": str(dst),
            }
            res = await create_skill(
                project_id,
                user_id,
                db,
                {
                    "name": skill_name,
                    "description": item.get("description"),
                    "scenario_category": scenario_category or skill_name,
                    "source_type": "upload",
                    "repo_url": None,
                    "skill_path": str(item["skill_dir"]),
                    "entry_command": (entry_command or "").strip() or None,
                    "is_active": True,
                    "extra_config": extra,
                },
            )
            created_ids.append(int(((res or {}).get("data") or {}).get("id") or 0))
        return success_response(data={"created": created_ids, "count": len(created_ids)}, message="导入成功")

    res = await create_skill(project_id, user_id, db, payload)
    return success_response(data={"created": [((res or {}).get("data") or {}).get("id")], "count": 1}, message="导入成功")


async def get_skill_content(project_id: int, user_id: int, skill_id: int, db: AsyncSession) -> dict:
    await _check_member(project_id, user_id, db)
    stmt = select(ProjectSkillModel).where(
        ProjectSkillModel.id == skill_id,
        ProjectSkillModel.project_id == project_id,
        ProjectSkillModel.user_id == user_id,
        ProjectSkillModel.enabled_flag == 1,
    )
    m = (await db.execute(stmt)).scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="技能不存在")
    if not m.skill_path:
        return success_response(data={"skill_id": skill_id, "content": ""}, message="查询成功")
    md = Path(m.skill_path) / "SKILL.md"
    text = md.read_text(encoding="utf-8", errors="ignore") if md.exists() else ""
    return success_response(data={"skill_id": skill_id, "content": text}, message="查询成功")


async def run_skill_tool(
    project_id: int,
    user_id: int,
    db: AsyncSession,
    *,
    skill_ref: str,
    arguments: Optional[dict] = None,
    session_id: Optional[str] = None,
) -> dict:
    await _check_member(project_id, user_id, db)
    ref = (skill_ref or "").strip()
    if not ref:
        raise HTTPException(status_code=400, detail="skill_ref 不能为空")
    stmt = select(ProjectSkillModel).where(
        ProjectSkillModel.project_id == project_id,
        ProjectSkillModel.user_id == user_id,
        ProjectSkillModel.enabled_flag == 1,
        ProjectSkillModel.is_active == 1,
    )
    stmt = stmt.where(ProjectSkillModel.id == int(ref)) if ref.isdigit() else stmt.where(ProjectSkillModel.name == ref)
    m = (await db.execute(stmt)).scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="技能不存在或未启用")
    skill_dir = Path(m.skill_path or "")
    if not skill_dir.exists():
        raise HTTPException(status_code=400, detail="技能目录不存在，请重新导入技能")

    extra = m.extra_config or {}
    sess = (session_id or f"s{secrets.token_hex(4)}").strip()
    screenshots_dir, artifacts_dir = _build_skill_runtime_dirs(project_id, sess)
    env = os.environ.copy()
    env["SCREENSHOT_DIR"] = str(screenshots_dir)
    env["SKILL_OUTPUT_DIR"] = str(artifacts_dir)
    env["ARTIFACT_DIR"] = str(artifacts_dir)
    env["SKILL_ARGS_JSON"] = json.dumps(arguments or {}, ensure_ascii=False)
    env["SKILL_SESSION_ID"] = sess
    env["PROJECT_ID"] = str(project_id)
    env["USER_ID"] = str(user_id)
    cmd = _resolve_skill_command(entry_command=m.entry_command or "", skill_dir=skill_dir, arguments=arguments)
    cmd = _inject_agent_browser_session(cmd, sess)

    # Guard: allowed-tools like "agent-browser:*" are NOT runnable commands.
    # Users sometimes paste them into command and npm treats it as an invalid tag name.
    if re.search(r"\bagent-browser:\*?\b", cmd, flags=re.IGNORECASE):
        raise HTTPException(
            status_code=400,
            detail=(
                "检测到非法命令片段 'agent-browser:*' 或 'agent-browser:'。"
                " 这是 SKILL.md 中 allowed-tools 的权限声明，不是可执行命令。"
                " 请改用例如: 'npx agent-browser --help' 或 'agent-browser open https://example.com'。"
            ),
        )

    # Allow workdir override for monorepo skills
    workdir = (extra.get("workdir") or "").strip()
    cwd = skill_dir
    if workdir:
        wd = Path(workdir)
        if not wd.is_absolute():
            pack_root = Path(str(extra.get("pack_root") or "")).resolve() if extra.get("pack_root") else None
            base = pack_root if pack_root and pack_root.exists() else skill_dir
            wd = (base / workdir).resolve()
        if wd.exists():
            cwd = wd

    if not cmd:
        allowed = (extra.get("allowed_tools") or "").strip()
        templates = _list_templates(skill_dir)
        raise HTTPException(
            status_code=400,
            detail=(
                "未配置 entry_command，无法执行该 Skill。"
                + " 可通过 arguments.command 或 arguments.template 执行。"
                + (f" allowed-tools: {allowed}。" if allowed else "")
                + (f" templates: {[t['name'] for t in templates]}。" if templates else "")
            ),
        )

    try:
        cp = subprocess.run(
            cmd,
            cwd=str(cwd),
            env=env,
            shell=True,
            capture_output=True,
            text=False,
            timeout=240,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="技能执行超时")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"技能执行异常: {e}")

    out_text = _smart_decode(cp.stdout)
    err_text = _smart_decode(cp.stderr)
    return {
        "ok": cp.returncode == 0,
        "skill_id": m.id,
        "skill_name": m.name,
        "session_id": sess,
        "return_code": cp.returncode,
        "stdout": (out_text or "").strip()[:12000],
        "stderr": (err_text or "").strip()[:8000],
        "artifacts": _collect_files(artifacts_dir),
        "screenshots": _collect_files(screenshots_dir),
    }


async def execute_skill(project_id: int, user_id: int, skill_id: int, db: AsyncSession, data: dict) -> dict:
    result = await run_skill_tool(
        project_id=project_id,
        user_id=user_id,
        db=db,
        skill_ref=str(skill_id),
        arguments=data.get("arguments") if isinstance(data.get("arguments"), dict) else {},
        session_id=data.get("session_id"),
    )
    return success_response(data=result, message="执行成功" if result.get("ok") else "执行失败")


async def create_skill_job(
    project_id: int,
    user_id: int,
    db: AsyncSession,
    *,
    skill_id: int,
    action_name: Optional[str],
    arguments: Optional[dict],
    session_id: Optional[str],
    runner_type: Optional[str] = None,
) -> dict:
    """
    Create async execution job for production runner.
    The runner will execute `command` inside skill_dir with env dirs mounted.
    """
    await _check_member(project_id, user_id, db)
    stmt = select(ProjectSkillModel).where(
        ProjectSkillModel.id == skill_id,
        ProjectSkillModel.project_id == project_id,
        ProjectSkillModel.user_id == user_id,
        ProjectSkillModel.enabled_flag == 1,
        ProjectSkillModel.is_active == 1,
    )
    m = (await db.execute(stmt)).scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="技能不存在或未启用")
    skill_dir = Path(m.skill_path or "")
    if not skill_dir.exists():
        raise HTTPException(status_code=400, detail="技能目录不存在，请重新导入技能")

    args = arguments if isinstance(arguments, dict) else {}
    cmd = _resolve_skill_command(entry_command=m.entry_command or "", skill_dir=skill_dir, arguments=args)
    cmd = _inject_agent_browser_session(cmd, session_id)
    if not cmd:
        extra = m.extra_config or {}
        allowed = (extra.get("allowed_tools") or "").strip()
        templates = _list_templates(skill_dir)
        raise HTTPException(
            status_code=400,
            detail=(
                "未配置 entry_command，无法创建执行任务。"
                + " 请通过 arguments.command 或 arguments.template 指定执行内容。"
                + (f" allowed-tools: {allowed}。" if allowed else "")
                + (f" templates: {[t['name'] for t in templates]}。" if templates else "")
            ),
        )

    if re.search(r"\bagent-browser:\*?\b", cmd, flags=re.IGNORECASE):
        raise HTTPException(status_code=400, detail="命令包含 allowed-tools 片段（agent-browser:*），请改用 npx/agent-browser 实际命令。")

    runtime_key = (session_id or f"j{secrets.token_hex(6)}").strip()
    rt = (runner_type or DEFAULT_RUNNER_TYPE or "local").strip().lower()
    job = SkillExecutionJobModel(
        project_id=project_id,
        user_id=user_id,
        skill_id=skill_id,
        action_name=action_name,
        command=cmd,
        input_args=args,
        session_id=session_id,
        status="pending",
        runtime_key=runtime_key,
        runner_type=rt,
        runner_meta={"skill_dir": str(skill_dir)},
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Seed first event
    db.add(SkillExecutionEventModel(job_id=job.id, seq=1, level="info", message=f"queued runner={rt}"))
    await db.commit()

    return success_response(
        data={
            "job_id": int(job.id),
            "status": job.status,
            "runner_type": rt,
            "runtime_key": runtime_key,
        },
        message="已入队",
    )


async def get_skill_job(project_id: int, user_id: int, db: AsyncSession, job_id: int) -> dict:
    await _check_member(project_id, user_id, db)
    stmt = select(SkillExecutionJobModel).where(
        SkillExecutionJobModel.id == job_id,
        SkillExecutionJobModel.project_id == project_id,
        SkillExecutionJobModel.user_id == user_id,
        SkillExecutionJobModel.enabled_flag == 1,
    )
    j = (await db.execute(stmt)).scalar_one_or_none()
    if not j:
        raise HTTPException(status_code=404, detail="任务不存在")
    return success_response(
        data={
            "job_id": int(j.id),
            "skill_id": int(j.skill_id),
            "status": j.status,
            "action_name": j.action_name,
            "session_id": j.session_id,
            "runner_type": j.runner_type,
            "return_code": j.return_code,
            "stdout": (j.stdout or ""),
            "stderr": (j.stderr or ""),
            "error_message": j.error_message,
            "queued_at": _iso(j.queued_at),
            "started_at": _iso(j.started_at),
            "finished_at": _iso(j.finished_at),
        },
        message="查询成功",
    )


async def list_job_artifacts(project_id: int, user_id: int, db: AsyncSession, job_id: int) -> dict:
    await _check_member(project_id, user_id, db)
    j = (await db.execute(select(SkillExecutionJobModel).where(
        SkillExecutionJobModel.id == job_id,
        SkillExecutionJobModel.project_id == project_id,
        SkillExecutionJobModel.user_id == user_id,
        SkillExecutionJobModel.enabled_flag == 1,
    ))).scalar_one_or_none()
    if not j:
        raise HTTPException(status_code=404, detail="任务不存在")
    rows = (await db.execute(
        select(SkillExecutionArtifactModel).where(
            SkillExecutionArtifactModel.job_id == job_id,
            SkillExecutionArtifactModel.enabled_flag == 1,
        ).order_by(SkillExecutionArtifactModel.id.asc())
    )).scalars().all()
    items = [{"id": int(r.id), "kind": r.kind, "name": r.name, "relative_path": r.relative_path, "size": r.size} for r in rows]
    return success_response(data={"job_id": job_id, "items": items}, message="查询成功")

