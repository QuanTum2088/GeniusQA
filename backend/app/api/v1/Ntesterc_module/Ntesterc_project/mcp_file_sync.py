#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

"""
MCP 文件同步（平台通用）与按需导出适配器。

默认写入（N-Tester）：
- project → {workspace}/.n-tester/mcp.json
- local   → ~/.n-tester/mcp.json → projects[absWorkspace].mcpServers
- user    → ~/.n-tester/mcp.json → mcpServers

按需导出（可选）：
- claude → ~/.claude.json / {workspace}/.mcp.json（Claude Code 兼容）
- cursor → ~/.cursor/mcp.json / {workspace}/.cursor/mcp.json
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

VALID_SCOPES = {"local", "project", "user"}
EXPORT_FORMATS = {"n-tester", "claude", "cursor"}


def ntester_home() -> Path:
    override = (os.getenv("NTESTER_HOME") or os.getenv("MCP_NTESTER_HOME") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".n-tester"


def ntester_user_mcp_path() -> Path:
    return ntester_home() / "mcp.json"


def project_mcp_json_path(workspace_path: str) -> Path:
    """项目共享：仓库内平台文件。"""
    return Path(workspace_path).expanduser().resolve() / ".n-tester" / "mcp.json"


def claude_home() -> Path:
    override = (os.getenv("MCP_CLAUDE_HOME") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path.home()


def claude_json_path() -> Path:
    return claude_home() / ".claude.json"


def claude_project_mcp_path(workspace_path: str) -> Path:
    return Path(workspace_path).expanduser().resolve() / ".mcp.json"


def cursor_home() -> Path:
    override = (os.getenv("MCP_CURSOR_HOME") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".cursor"


def cursor_user_mcp_path() -> Path:
    return cursor_home() / "mcp.json"


def cursor_project_mcp_path(workspace_path: str) -> Path:
    return Path(workspace_path).expanduser().resolve() / ".cursor" / "mcp.json"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning(f"读取 MCP 配置文件失败 {path}: {e}")
        return {}


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def config_to_server_entry(cfg: Any) -> Dict[str, Any]:
    """ORM/dict → 通用 mcpServers 单项（stdio / http / sse）。"""
    transport = (
        getattr(cfg, "transport", None)
        or (cfg.get("transport") if isinstance(cfg, dict) else None)
        or "streamable-http"
    )
    transport = str(transport).strip().lower()

    def _g(key, default=None):
        if isinstance(cfg, dict):
            return cfg.get(key, default)
        return getattr(cfg, key, default)

    if transport in ("stdio",):
        entry: Dict[str, Any] = {
            "type": "stdio",
            "command": (_g("command") or "").strip() or "npx",
            "args": list(_g("args") or []),
        }
        env = _g("env") or {}
        if isinstance(env, dict) and env:
            entry["env"] = {str(k): str(v) for k, v in env.items() if k}
        return entry

    type_map = {
        "sse": "sse",
        "http": "http",
        "streamable-http": "http",
        "streamable_http": "http",
    }
    entry = {
        "type": type_map.get(transport, "http"),
        "url": (_g("url") or "").strip(),
    }
    headers = dict(_g("headers") or {})
    headers = merge_auth_headers(
        headers,
        _g("auth_type"),
        _g("auth_config"),
        for_file=True,
        scope=_g("scope") or "user",
    )
    if headers:
        entry["headers"] = headers
    return entry


# 兼容旧名
config_to_claude_entry = config_to_server_entry


def merge_auth_headers(
    headers: Optional[Dict[str, Any]],
    auth_type: Optional[str],
    auth_config: Optional[Dict[str, Any]],
    *,
    for_file: bool = False,
    scope: str = "user",
) -> Dict[str, str]:
    out = {str(k): str(v) for k, v in (headers or {}).items() if k}
    auth_type = (auth_type or "none").lower()
    auth_config = auth_config or {}
    if auth_type == "bearer":
        token = str(auth_config.get("token") or "").strip()
        if token and "Authorization" not in out and "authorization" not in {k.lower() for k in out}:
            if for_file and scope == "project" and not token.startswith("${"):
                out["Authorization"] = "Bearer ${MCP_TOKEN}"
            else:
                out["Authorization"] = f"Bearer {token}"
    elif auth_type == "api_key":
        header_name = str(auth_config.get("header_name") or "X-API-Key").strip() or "X-API-Key"
        api_key = str(auth_config.get("api_key") or "").strip()
        if api_key and header_name not in out:
            if for_file and scope == "project" and not api_key.startswith("${"):
                out[header_name] = "${MCP_API_KEY}"
            else:
                out[header_name] = api_key
    return out


def upsert_server_in_mcp_json(
    path: Path, server_name: str, entry: Dict[str, Any], old_name: Optional[str] = None
) -> None:
    data = _read_json(path)
    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        servers = {}
    if old_name and old_name != server_name and old_name in servers:
        servers.pop(old_name, None)
    servers[server_name] = entry
    data["mcpServers"] = servers
    if "version" not in data:
        data["version"] = 1
    _write_json(path, data)


def remove_server_from_mcp_json(path: Path, server_name: str) -> None:
    if not path.exists():
        return
    data = _read_json(path)
    servers = data.get("mcpServers")
    if isinstance(servers, dict) and server_name in servers:
        servers.pop(server_name, None)
        data["mcpServers"] = servers
        _write_json(path, data)


def upsert_local_or_user(
    *,
    scope: str,
    workspace_path: Optional[str],
    server_name: str,
    entry: Dict[str, Any],
    old_name: Optional[str] = None,
    path: Optional[Path] = None,
) -> Path:
    """写入用户级 mcp.json（local 嵌 projects，user 写顶层 mcpServers）。"""
    target = path or ntester_user_mcp_path()
    data = _read_json(target)
    if scope == "user":
        servers = data.get("mcpServers")
        if not isinstance(servers, dict):
            servers = {}
        if old_name and old_name != server_name:
            servers.pop(old_name, None)
        servers[server_name] = entry
        data["mcpServers"] = servers
    else:
        if not workspace_path:
            raise ValueError("项目私有作用域需要配置项目本机工作目录 workspace_path")
        abs_ws = str(Path(workspace_path).expanduser().resolve())
        projects = data.get("projects")
        if not isinstance(projects, dict):
            projects = {}
        proj = projects.get(abs_ws)
        if not isinstance(proj, dict):
            proj = {}
        servers = proj.get("mcpServers")
        if not isinstance(servers, dict):
            servers = {}
        if old_name and old_name != server_name:
            servers.pop(old_name, None)
        servers[server_name] = entry
        proj["mcpServers"] = servers
        projects[abs_ws] = proj
        data["projects"] = projects
    if "version" not in data:
        data["version"] = 1
    _write_json(target, data)
    return target


def remove_local_or_user(
    *,
    scope: str,
    workspace_path: Optional[str],
    server_name: str,
    path: Optional[Path] = None,
) -> None:
    target = path or ntester_user_mcp_path()
    if not target.exists():
        return
    data = _read_json(target)
    if scope == "user":
        servers = data.get("mcpServers")
        if isinstance(servers, dict):
            servers.pop(server_name, None)
            data["mcpServers"] = servers
            _write_json(target, data)
        return
    if not workspace_path:
        return
    abs_ws = str(Path(workspace_path).expanduser().resolve())
    projects = data.get("projects")
    if not isinstance(projects, dict):
        return
    proj = projects.get(abs_ws)
    if not isinstance(proj, dict):
        return
    servers = proj.get("mcpServers")
    if isinstance(servers, dict):
        servers.pop(server_name, None)
        proj["mcpServers"] = servers
        projects[abs_ws] = proj
        data["projects"] = projects
        _write_json(target, data)


def sync_config_to_files(cfg: Any, *, workspace_path: Optional[str], old_name: Optional[str] = None) -> Dict[str, Any]:
    """按作用域同步到 N-Tester 平台文件。"""
    scope = (getattr(cfg, "scope", None) or "user").strip().lower()
    name = getattr(cfg, "name")
    entry = config_to_server_entry(cfg)
    written: Dict[str, Any] = {"scope": scope, "name": name, "format": "n-tester"}

    if scope == "project":
        if not workspace_path:
            raise ValueError("项目共享作用域需要配置项目本机工作目录 workspace_path")
        path = project_mcp_json_path(workspace_path)
        upsert_server_in_mcp_json(path, name, entry, old_name=old_name)
        written["path"] = str(path)
        return written

    if scope in ("local", "user"):
        path = upsert_local_or_user(
            scope=scope,
            workspace_path=workspace_path if scope == "local" else None,
            server_name=name,
            entry=entry,
            old_name=old_name,
            path=ntester_user_mcp_path(),
        )
        written["path"] = str(path)
        return written

    raise ValueError(f"不支持的作用域: {scope}")


def remove_config_from_files(cfg: Any, *, workspace_path: Optional[str]) -> None:
    scope = (getattr(cfg, "scope", None) or "user").strip().lower()
    name = getattr(cfg, "name")
    if scope == "project":
        if workspace_path:
            remove_server_from_mcp_json(project_mcp_json_path(workspace_path), name)
        return
    if scope in ("local", "user"):
        remove_local_or_user(
            scope=scope,
            workspace_path=workspace_path if scope == "local" else None,
            server_name=name,
            path=ntester_user_mcp_path(),
        )


def parse_mcp_json_file(path: Path) -> List[Dict[str, Any]]:
    """解析含 mcpServers 的文件为平台配置列表（兼容 N-Tester / Claude / Cursor）。"""
    data = _read_json(path)
    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        return []
    items: List[Dict[str, Any]] = []
    for name, entry in servers.items():
        if not isinstance(entry, dict):
            continue
        t = str(entry.get("type") or "").lower()
        if not t:
            if entry.get("command"):
                t = "stdio"
            elif entry.get("url"):
                t = "http"
            else:
                continue
        item: Dict[str, Any] = {"name": name, "is_enabled": True}
        if t == "stdio":
            item["transport"] = "stdio"
            item["command"] = entry.get("command") or "npx"
            item["args"] = entry.get("args") or []
            item["env"] = entry.get("env") or {}
            item["url"] = ""
        elif t == "sse":
            item["transport"] = "sse"
            item["url"] = entry.get("url") or ""
            item["headers"] = entry.get("headers") or {}
        else:
            item["transport"] = "streamable-http"
            item["url"] = entry.get("url") or ""
            item["headers"] = entry.get("headers") or {}
        items.append(item)
    return items


def default_import_candidates(workspace_path: str) -> List[Path]:
    """导入时按优先级尝试的路径。"""
    ws = Path(workspace_path).expanduser().resolve()
    return [
        ws / ".n-tester" / "mcp.json",
        ws / ".mcp.json",
        ws / ".cursor" / "mcp.json",
    ]


def export_configs(
    configs: List[Any],
    *,
    format: str,
    workspace_path: Optional[str] = None,
    write: bool = True,
) -> Dict[str, Any]:
    """按目标客户端格式导出。format: n-tester | claude | cursor"""
    fmt = (format or "n-tester").strip().lower()
    if fmt not in EXPORT_FORMATS:
        raise ValueError(f"不支持的导出格式: {format}，可选 {sorted(EXPORT_FORMATS)}")

    by_scope: Dict[str, List[Any]] = {"project": [], "local": [], "user": []}
    for c in configs:
        scope = (getattr(c, "scope", None) or "user").strip().lower()
        if scope not in by_scope:
            scope = "user"
        by_scope[scope].append(c)

    written: List[Dict[str, Any]] = []
    payloads: Dict[str, Any] = {}

    def _entries(rows: List[Any]) -> Dict[str, Any]:
        return {getattr(r, "name"): config_to_server_entry(r) for r in rows}

    if fmt == "n-tester":
        for c in by_scope["project"] + by_scope["local"] + by_scope["user"]:
            info = sync_config_to_files(c, workspace_path=workspace_path) if write else {
                "path": describe_write_path(getattr(c, "scope", "user"), workspace_path),
                "scope": getattr(c, "scope", "user"),
            }
            written.append(info)
        if write:
            if by_scope["project"] and workspace_path:
                p = project_mcp_json_path(workspace_path)
                payloads[str(p)] = _read_json(p)
            if by_scope["local"] or by_scope["user"]:
                payloads[str(ntester_user_mcp_path())] = _read_json(ntester_user_mcp_path())
        return {"format": fmt, "written": written, "preview": payloads}

    if fmt == "claude":
        if by_scope["project"]:
            if not workspace_path:
                raise ValueError("导出 Claude 项目共享配置需要 workspace_path")
            path = claude_project_mcp_path(workspace_path)
            for c in by_scope["project"]:
                if write:
                    upsert_server_in_mcp_json(path, getattr(c, "name"), config_to_server_entry(c))
            payloads[str(path)] = _read_json(path) if write else {"mcpServers": _entries(by_scope["project"])}
            written.append({"path": str(path), "scope": "project"})
        if by_scope["local"] or by_scope["user"]:
            path = claude_json_path()
            for c in by_scope["user"]:
                if write:
                    upsert_local_or_user(
                        scope="user",
                        workspace_path=None,
                        server_name=getattr(c, "name"),
                        entry=config_to_server_entry(c),
                        path=path,
                    )
            for c in by_scope["local"]:
                if write:
                    upsert_local_or_user(
                        scope="local",
                        workspace_path=workspace_path,
                        server_name=getattr(c, "name"),
                        entry=config_to_server_entry(c),
                        path=path,
                    )
            payloads[str(path)] = _read_json(path) if write else {"mcpServers": _entries(by_scope["user"])}
            written.append({"path": str(path), "scope": "local+user"})
        return {"format": fmt, "written": written, "preview": payloads}

    # cursor
    if by_scope["project"]:
        if not workspace_path:
            raise ValueError("导出 Cursor 项目共享配置需要 workspace_path")
        path = cursor_project_mcp_path(workspace_path)
        for c in by_scope["project"]:
            if write:
                upsert_server_in_mcp_json(path, getattr(c, "name"), config_to_server_entry(c))
        payloads[str(path)] = _read_json(path) if write else {"mcpServers": _entries(by_scope["project"])}
        written.append({"path": str(path), "scope": "project"})
    user_rows = by_scope["local"] + by_scope["user"]
    if user_rows:
        path = cursor_user_mcp_path()
        for c in user_rows:
            if write:
                upsert_server_in_mcp_json(path, getattr(c, "name"), config_to_server_entry(c))
        payloads[str(path)] = _read_json(path) if write else {"mcpServers": _entries(user_rows)}
        written.append({"path": str(path), "scope": "local+user"})
    return {"format": fmt, "written": written, "preview": payloads}


def describe_write_path(scope: str, workspace_path: Optional[str] = None) -> str:
    scope = (scope or "user").lower()
    ws = workspace_path or "{workspace}"
    if scope == "project":
        return f"{ws}/.n-tester/mcp.json"
    if scope == "local":
        return f"~/.n-tester/mcp.json → projects[{ws}].mcpServers"
    return "~/.n-tester/mcp.json → mcpServers"
