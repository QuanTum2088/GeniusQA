#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""接口自动化 Mock 运行时：按路径匹配 Api，再按期望/脚本返回响应。"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from .model import ApiModel


_VAR_RE = re.compile(r"\{\{[^{}]+\}\}|\$\{[^}]+\}")
_PATH_PARAM_RE = re.compile(r"\{([^{}/]+)\}|:([A-Za-z_][A-Za-z0-9_]*)")


def normalize_api_path(url: str) -> str:
    """去掉环境变量占位符，提取纯 path（不含 query）。"""
    u = str(url or "").strip()
    u = _VAR_RE.sub("", u)
    if re.match(r"^https?://", u, re.I):
        parsed = urlparse(u)
        u = parsed.path or "/"
    else:
        u = u.split("?", 1)[0]
    u = re.sub(r"/+", "/", u)
    if not u.startswith("/"):
        u = "/" + u
    return u.rstrip("/") or "/"


def path_to_regex(api_path: str) -> Tuple[re.Pattern, List[str]]:
    """将 /pet/{id} 转为正则，并返回参数名列表。"""
    names: List[str] = []

    def _repl(m: re.Match) -> str:
        name = m.group(1) or m.group(2)
        names.append(name)
        return r"(?P<%s>[^/]+)" % re.escape(name)

    pattern = _PATH_PARAM_RE.sub(_repl, api_path)
    pattern = "^" + pattern.rstrip("/") + "/?$"
    return re.compile(pattern), names


def client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for") or request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    xri = request.headers.get("x-real-ip") or request.headers.get("X-Real-IP")
    if xri:
        return xri.strip()
    return request.client.host if request.client else ""


def _compare(actual: Any, operator: str, expect: str) -> bool:
    op = (operator or "eq").lower()
    actual_str = "" if actual is None else str(actual)
    expect = "" if expect is None else str(expect)
    if op in ("exists", "exist"):
        return actual is not None and actual_str != ""
    if op in ("not_exists", "not_exist"):
        return actual is None or actual_str == ""
    if op in ("eq", "equals", "=="):
        return actual_str == expect
    if op in ("neq", "!=", "not_equals"):
        return actual_str != expect
    if op == "contains":
        return expect in actual_str
    if op in ("not_contains", "notcontains"):
        return expect not in actual_str
    if op in ("regex", "regexp"):
        try:
            return bool(re.search(expect, actual_str))
        except re.error:
            return False
    if op in ("gt", "gte", "lt", "lte"):
        try:
            a, e = float(actual_str), float(expect)
        except (TypeError, ValueError):
            return False
        if op == "gt":
            return a > e
        if op == "gte":
            return a >= e
        if op == "lt":
            return a < e
        return a <= e
    return actual_str == expect


def _jsonpath_get(data: Any, expr: str) -> Any:
    """轻量取值：支持 a.b / $.a.b / a[0].b。"""
    if not expr:
        return None
    path = expr.strip()
    if path.startswith("$."):
        path = path[2:]
    elif path.startswith("$"):
        path = path[1:].lstrip(".")
    cur = data
    for part in re.split(r"\.|(?=\[)", path):
        if not part:
            continue
        m = re.match(r"^(\w+)?(?:\[(\d+)\])?$", part)
        if not m:
            if isinstance(cur, dict):
                cur = cur.get(part)
            else:
                return None
            continue
        key, idx = m.group(1), m.group(2)
        if key:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(key)
        if idx is not None:
            try:
                cur = cur[int(idx)]  # type: ignore[index]
            except Exception:
                return None
    return cur


def _get_cookie_map(request: Request) -> Dict[str, str]:
    return {k: v for k, v in request.cookies.items()}


def _get_param_value(
    location: str,
    name: str,
    query: Dict[str, Any],
    path_params: Dict[str, str],
    headers: Dict[str, str],
    cookies: Dict[str, str],
    body: Any,
) -> Any:
    loc = (location or "query").lower()
    if loc == "query":
        return query.get(name)
    if loc == "path":
        return path_params.get(name)
    if loc == "header":
        # header 名大小写不敏感
        lower = {k.lower(): v for k, v in headers.items()}
        return lower.get((name or "").lower())
    if loc == "cookie":
        return cookies.get(name)
    if loc == "body":
        if isinstance(body, dict):
            if name in body:
                return body.get(name)
            return _jsonpath_get(body, name)
        return None
    return None


def match_expect(
    expect: Dict[str, Any],
    *,
    ip: str,
    query: Dict[str, Any],
    path_params: Dict[str, str],
    headers: Dict[str, str],
    cookies: Dict[str, str],
    body: Any,
) -> bool:
    if expect.get("ipEnabled"):
        ips = [x.strip() for x in str(expect.get("ips") or "").split(",") if x.strip()]
        if not ips or ip not in ips:
            return False
    for cond in expect.get("paramConditions") or []:
        if not isinstance(cond, dict):
            continue
        name = str(cond.get("name") or "").strip()
        if not name and cond.get("operator") not in ("exists", "not_exists"):
            continue
        actual = _get_param_value(
            str(cond.get("location") or "query"),
            name,
            query,
            path_params,
            headers,
            cookies,
            body,
        )
        if not _compare(actual, str(cond.get("operator") or "eq"), str(cond.get("value") or "")):
            return False
    return True


def build_response_from_expect(expect: Dict[str, Any]) -> Dict[str, Any]:
    raw_body = expect.get("body")
    body: Any
    if isinstance(raw_body, (dict, list)):
        body = raw_body
    else:
        text = str(raw_body or "").strip()
        if not text:
            body = {}
        else:
            try:
                body = json.loads(text)
            except Exception:
                body = text
    headers: Dict[str, str] = {}
    for h in expect.get("headers") or []:
        if isinstance(h, dict) and str(h.get("key") or "").strip():
            headers[str(h["key"]).strip()] = str(h.get("value") or "")
    return {
        "status": int(expect.get("status") or 200),
        "delay": int(expect.get("delay") or 0),
        "headers": headers,
        "body": body,
        "matched": expect.get("name") or "unnamed",
    }


def run_mock_script(
    script: str,
    *,
    method: str,
    path: str,
    query: Dict[str, Any],
    path_params: Dict[str, str],
    headers: Dict[str, str],
    cookies: Dict[str, str],
    body: Any,
    default_body: Any = None,
) -> Optional[Dict[str, Any]]:
    """执行自定义 Mock 脚本。支持 mock.mockResponse / fox.mockResponse.setBody 等常见写法。"""
    if not (script or "").strip():
        return None

    state: Dict[str, Any] = {
        "body": default_body if default_body is not None else {},
        "status": 200,
        "headers": {},
        "delay": 0,
        "used": False,
    }

    class _MockResponse:
        def mockResponse(self, data: Any = None, **kwargs: Any) -> Any:
            state["used"] = True
            if data is not None:
                state["body"] = data
            if "code" in kwargs:
                state["status"] = int(kwargs["code"])
            if "status" in kwargs:
                state["status"] = int(kwargs["status"])
            if "headers" in kwargs and isinstance(kwargs["headers"], dict):
                state["headers"].update({str(k): str(v) for k, v in kwargs["headers"].items()})
            return state["body"]

        def setBody(self, data: Any) -> None:
            state["used"] = True
            state["body"] = data

        def setCode(self, code: int) -> None:
            state["used"] = True
            state["status"] = int(code)

        def setDelay(self, ms: int) -> None:
            state["used"] = True
            state["delay"] = int(ms)

        def json(self) -> Any:
            return state["body"]

        @property
        def headers(self) -> Dict[str, str]:
            return state["headers"]

        @property
        def code(self) -> int:
            return int(state["status"])

    class _MockRequest:
        def __init__(self) -> None:
            self.method = method
            self.path = path
            self.query = query
            self.pathParams = path_params
            self.headers = headers
            self.cookies = cookies
            self.body = body

        def getParam(self, key: str) -> Any:
            if key in path_params:
                return path_params[key]
            if key in query:
                return query[key]
            if isinstance(body, dict) and key in body:
                return body[key]
            return None

    mock_resp = _MockResponse()
    mock_req = _MockRequest()
    fox = type("Fox", (), {"mockRequest": mock_req, "mockResponse": mock_resp})()
    mock = type("Mock", (), {"mockResponse": mock_resp.mockResponse, "mockRequest": mock_req})()

    safe_builtins = {
        "True": True,
        "False": False,
        "None": None,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "dict": dict,
        "list": list,
        "len": len,
        "min": min,
        "max": max,
        "sum": sum,
        "abs": abs,
        "round": round,
        "json": json,
        "re": re,
    }
    try:
        exec(  # noqa: S102 — 受控 Mock 脚本执行
            script,
            {"__builtins__": safe_builtins},
            {"mock": mock, "fox": fox, "$$": fox},
        )
    except Exception as e:
        return {
            "status": 500,
            "delay": 0,
            "headers": {"X-Mock-Error": "script"},
            "body": {"msg": "Mock 脚本执行失败", "exception": str(e)},
            "matched": "script_error",
        }
    if not state["used"]:
        return None
    return {
        "status": int(state["status"]),
        "delay": int(state["delay"]),
        "headers": dict(state["headers"]),
        "body": state["body"],
        "matched": "script",
    }


class ApiMockRuntime:
    @staticmethod
    async def resolve(
        db: AsyncSession,
        request: Request,
        path: str,
    ) -> Dict[str, Any]:
        req_path = normalize_api_path("/" + (path or "").lstrip("/"))
        api_id_hint = request.query_params.get("_api_id") or request.query_params.get("api_id")
        service_id_hint = request.query_params.get("_service_id") or request.query_params.get("service_id")

        stmt = select(ApiModel).where(ApiModel.enabled_flag == 1)
        if api_id_hint:
            try:
                stmt = stmt.where(ApiModel.id == int(api_id_hint))
            except ValueError:
                pass
        if service_id_hint:
            try:
                stmt = stmt.where(ApiModel.api_service_id == int(service_id_hint))
            except ValueError:
                pass
        rows = (await db.execute(stmt.order_by(ApiModel.id.desc()))).scalars().all()

        matched_api: Optional[ApiModel] = None
        path_params: Dict[str, str] = {}
        for row in rows:
            api_path = normalize_api_path(row.url or "")
            regex, names = path_to_regex(api_path)
            m = regex.match(req_path)
            if m:
                matched_api = row
                path_params = {k: m.group(k) for k in names}
                break
            # 无 path 参数时也允许尾部完全相等
            if api_path == req_path:
                matched_api = row
                break

        if not matched_api:
            return {
                "status": 404,
                "delay": 0,
                "headers": {"X-Mock-Status": "api-not-found"},
                "body": {
                    "msg": "未找到对应 Mock 接口",
                    "path": req_path,
                    "hint": "请确认接口已保存，且 Mock 地址路径与接口 URL（去掉环境变量前缀后）一致；可用 ?_api_id=接口ID 精确定位",
                },
                "matched": None,
            }

        req_cfg = matched_api.req if isinstance(matched_api.req, dict) else {}
        mock_cfg = req_cfg.get("mock") if isinstance(req_cfg.get("mock"), dict) else {}
        # 兼容顶层 mock 字段（若以后扩展）
        if not mock_cfg and isinstance(getattr(matched_api, "document", None), dict):
            mock_cfg = (matched_api.document or {}).get("mock") or {}

        # 解析请求体
        body: Any = None
        try:
            raw = await request.body()
            if raw:
                ctype = (request.headers.get("content-type") or "").lower()
                text = raw.decode("utf-8", errors="replace")
                if "application/json" in ctype or text[:1] in "{[":
                    try:
                        body = json.loads(text)
                    except Exception:
                        body = text
                elif "application/x-www-form-urlencoded" in ctype:
                    body = {k: (v[0] if len(v) == 1 else v) for k, v in parse_qs(text).items()}
                else:
                    body = text
        except Exception:
            body = None

        # query（去掉内部定位参数）
        query: Dict[str, Any] = {}
        for k, v in request.query_params.multi_items():
            if k in ("_api_id", "api_id", "_service_id", "service_id"):
                continue
            if k in query:
                prev = query[k]
                query[k] = prev + [v] if isinstance(prev, list) else [prev, v]
            else:
                query[k] = v

        headers = {k: v for k, v in request.headers.items()}
        cookies = _get_cookie_map(request)
        ip = client_ip(request)

        expects = mock_cfg.get("expects") if isinstance(mock_cfg.get("expects"), list) else []
        for expect in expects:
            if not isinstance(expect, dict):
                continue
            if match_expect(
                expect,
                ip=ip,
                query=query,
                path_params=path_params,
                headers=headers,
                cookies=cookies,
                body=body,
            ):
                result = build_response_from_expect(expect)
                result["headers"] = {
                    **result["headers"],
                    "X-Mock-Api-Id": str(matched_api.id),
                    "X-Mock-Matched": str(result.get("matched") or ""),
                }
                # 期望命中后仍允许脚本二次改写
                if mock_cfg.get("scriptEnabled") and mock_cfg.get("script"):
                    script_res = run_mock_script(
                        str(mock_cfg.get("script") or ""),
                        method=request.method,
                        path=req_path,
                        query=query,
                        path_params=path_params,
                        headers=headers,
                        cookies=cookies,
                        body=body,
                        default_body=result["body"],
                    )
                    if script_res:
                        merged_headers = {
                            **(result.get("headers") or {}),
                            **(script_res.get("headers") or {}),
                        }
                        merged_headers["X-Mock-Api-Id"] = str(matched_api.id)
                        merged_headers["X-Mock-Matched"] = "expect+script"
                        script_res["headers"] = merged_headers
                        return script_res
                return result

        # 未命中期望：走脚本或默认
        if mock_cfg.get("scriptEnabled") and mock_cfg.get("script"):
            script_res = run_mock_script(
                str(mock_cfg.get("script") or ""),
                method=request.method,
                path=req_path,
                query=query,
                path_params=path_params,
                headers=headers,
                cookies=cookies,
                body=body,
                default_body={},
            )
            if script_res:
                merged_headers = dict(script_res.get("headers") or {})
                merged_headers["X-Mock-Api-Id"] = str(matched_api.id)
                merged_headers["X-Mock-Matched"] = "script"
                script_res["headers"] = merged_headers
                return script_res

        return {
            "status": 200,
            "delay": 0,
            "headers": {
                "X-Mock-Api-Id": str(matched_api.id),
                "X-Mock-Matched": "default",
            },
            "body": {
                "msg": "Mock 默认响应：未匹配到期望，且未启用脚本",
                "api_id": matched_api.id,
                "path": req_path,
            },
            "matched": "default",
        }
