#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from __future__ import annotations

import multiprocessing
from datetime import datetime
from typing import Any, Dict, List
import threading
import psutil
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from .model import MiniMenuModel, MiniResultListModel, MiniResultModel, MiniScriptModel
from .runners.factory import list_frameworks, list_platforms

_pid_index: Dict[int, Dict[str, Any]] = {}
_proc_index: Dict[int, multiprocessing.Process] = {}
_index_lock = threading.Lock()


def _cleanup_finished_processes() -> None:
    with _index_lock:
        finished = [pid for pid, p in _proc_index.items() if not p.is_alive()]
        for pid in finished:
            _pid_index.pop(pid, None)
            proc = _proc_index.pop(pid, None)
            if proc:
                proc.join(timeout=1)


class MiniAutomationService:

    # ── 菜单 ──────────────────────────────────────────────
    @staticmethod
    async def get_menu(db: AsyncSession, user_id: int, project_id: Optional[int] = None) -> List[Dict]:
        q = select(MiniMenuModel).where(
            MiniMenuModel.user_id == user_id,
            MiniMenuModel.enabled_flag == 1,
        )
        if project_id:
            q = q.where(MiniMenuModel.project_id == project_id)
        rows = (await db.execute(q.order_by(MiniMenuModel.id))).scalars().all()
        nodes = [{"id": r.id, "name": r.name, "pid": int(r.pid), "type": int(r.type)} for r in rows]
        node_map = {n["id"]: {**n, "children": []} for n in nodes}
        roots: List[Dict] = []
        for n in nodes:
            pid = int(n["pid"])
            if pid and pid in node_map:
                node_map[pid]["children"].append(node_map[n["id"]])
            else:
                roots.append(node_map[n["id"]])
        return roots

    @staticmethod
    async def add_menu(db: AsyncSession, name: str, pid: int, mtype: int,
                       user_id: int, project_id: Optional[int] = None) -> Dict:
        menu = MiniMenuModel(name=name, pid=pid, type=mtype, user_id=user_id, project_id=project_id)
        db.add(menu)
        await db.flush()
        if mtype == 2:
            db.add(MiniScriptModel(
                menu_id=menu.id, platform="wechat", framework="minium",
                script=[], user_id=user_id,
            ))
        await db.commit()
        return {"id": menu.id, "name": name, "pid": pid, "type": mtype}

    @staticmethod
    async def rename_menu(db: AsyncSession, menu_id: int, name: str, user_id: int) -> bool:
        await db.execute(
            update(MiniMenuModel)
            .where(MiniMenuModel.id == menu_id, MiniMenuModel.user_id == user_id)
            .values(name=name)
        )
        await db.commit()
        return True

    @staticmethod
    async def delete_menu(db: AsyncSession, menu_id: int, user_id: int) -> bool:
        """递归删除菜单节点及其所有子节点和脚本"""
        async def _collect_ids(mid: int) -> List[int]:
            ids = [mid]
            children = (await db.execute(
                select(MiniMenuModel.id).where(
                    MiniMenuModel.pid == mid,
                    MiniMenuModel.user_id == user_id,
                    MiniMenuModel.enabled_flag == 1,
                )
            )).scalars().all()
            for cid in children:
                ids.extend(await _collect_ids(cid))
            return ids

        all_ids = await _collect_ids(menu_id)
        await db.execute(
            delete(MiniScriptModel).where(
                MiniScriptModel.menu_id.in_(all_ids),
                MiniScriptModel.user_id == user_id,
            )
        )
        await db.execute(
            delete(MiniMenuModel).where(
                MiniMenuModel.id.in_(all_ids),
                MiniMenuModel.user_id == user_id,
            )
        )
        await db.commit()
        return True

    # ── 脚本 ──────────────────────────────────────────────
    @staticmethod
    async def get_script(db: AsyncSession, menu_id: int, user_id: int) -> Dict:
        row = (await db.execute(
            select(MiniScriptModel)
            .where(MiniScriptModel.menu_id == menu_id, MiniScriptModel.user_id == user_id,
                   MiniScriptModel.enabled_flag == 1)
        )).scalar_one_or_none()
        if not row:
            return {"id": menu_id, "platform": "wechat", "framework": "minium",
                    "script": [], "platform_config": {}}
        return {
            "id": row.menu_id, "platform": row.platform, "framework": row.framework,
            "script": row.script or [], "platform_config": row.platform_config or {},
        }

    @staticmethod
    async def save_script(db: AsyncSession, menu_id: int, platform: str, framework: str,
                          steps: List[Dict], platform_config: Dict, user_id: int) -> bool:
        row = (await db.execute(
            select(MiniScriptModel)
            .where(MiniScriptModel.menu_id == menu_id, MiniScriptModel.user_id == user_id)
        )).scalar_one_or_none()
        if row:
            row.platform = platform
            row.framework = framework
            row.script = steps
            row.platform_config = platform_config
            flag_modified(row, "script")
            flag_modified(row, "platform_config")
        else:
            db.add(MiniScriptModel(
                menu_id=menu_id, platform=platform, framework=framework,
                script=steps, platform_config=platform_config, user_id=user_id,
            ))
        await db.commit()
        return True

    # ── 执行 ──────────────────────────────────────────────
    @staticmethod
    async def run_script(db: AsyncSession, menu_id: int, task_name: str, result_id: str,
                         platform: str, framework: str,
                         platform_config: Dict, user_id: int,
                         project_id: Optional[int] = None) -> Dict:
        from .executor import run_mini_process

        row = (await db.execute(
            select(MiniScriptModel)
            .where(MiniScriptModel.menu_id == menu_id, MiniScriptModel.user_id == user_id,
                   MiniScriptModel.enabled_flag == 1)
        )).scalar_one_or_none()
        steps = list(row.script or []) if row else []
        merged_config = dict(row.platform_config or {}) if row else {}
        merged_config.update(platform_config or {})

        db.add(MiniResultListModel(
            task_name=task_name, result_id=result_id,
            platform=platform, framework=framework,
            script_list=[{"id": menu_id, "name": task_name}],
            script_status=[{"status": "running", "total": len(steps), "passed": 0, "fail": 0}],
            project_id=project_id,
            user_id=user_id,
        ))
        await db.commit()

        p = multiprocessing.Process(
            target=run_mini_process,
            kwargs=dict(
                result_id=result_id, menu_id=menu_id, user_id=user_id,
                steps=steps, framework=framework, platform=platform,
                platform_config=merged_config, task_name=task_name,
            ),
            daemon=False,
        )
        p.start()
        with _index_lock:
            _pid_index[p.pid] = {"result_id": result_id}
            _proc_index[p.pid] = p
        _cleanup_finished_processes()
        return {"result_id": result_id, "pid": p.pid}

    @staticmethod
    async def stop_script(db: AsyncSession, result_id: str, user_id: int) -> bool:
        row = (await db.execute(
            select(MiniResultListModel)
            .where(MiniResultListModel.result_id == result_id,
                   MiniResultListModel.user_id == user_id)
        )).scalar_one_or_none()
        if not row:
            return False
        with _index_lock:
            to_clean = [(pid, info) for pid, info in _pid_index.items()
                        if info.get("result_id") == result_id]
        for pid, _ in to_clean:
            try:
                if psutil.pid_exists(pid):
                    psutil.Process(pid).terminate()
            except Exception:
                pass
            with _index_lock:
                _pid_index.pop(pid, None)
                proc = _proc_index.pop(pid, None)
                if proc:
                    proc.join(timeout=3)
        row.end_time = datetime.now()
        ss = list(row.script_status or [])
        ss.append({"stopped": True, "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        row.script_status = ss
        flag_modified(row, "script_status")
        await db.commit()
        return True

    # ── 结果 ──────────────────────────────────────────────
    @staticmethod
    async def get_result_list(db: AsyncSession, user_id: int,
                              page: int, page_size: int, search: Dict) -> Dict:
        from sqlalchemy import func
        q = select(MiniResultListModel).where(
            MiniResultListModel.user_id == user_id,
            MiniResultListModel.enabled_flag == 1,
        )
        if search.get("task_name"):
            q = q.where(MiniResultListModel.task_name.contains(search["task_name"]))
        if search.get("platform"):
            q = q.where(MiniResultListModel.platform == search["platform"])
        if search.get("project_id"):
            q = q.where(MiniResultListModel.project_id == int(search["project_id"]))
        q = q.order_by(MiniResultListModel.id.desc())

        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        rows = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()
        content = [
            {
                "id": r.id, "task_name": r.task_name, "result_id": r.result_id,
                "platform": r.platform, "framework": r.framework,
                "script_status": r.script_status,
                "start_time": str(r.start_time) if r.start_time else "",
                "end_time": str(r.end_time) if r.end_time else "",
            }
            for r in rows
        ]
        return {"content": content, "total": total, "page": page, "pageSize": page_size}

    @staticmethod
    async def get_result_detail(db: AsyncSession, result_id: str, user_id: int) -> List[Dict]:
        rows = (await db.execute(
            select(MiniResultModel)
            .where(MiniResultModel.result_id == result_id,
                   MiniResultModel.user_id == user_id,
                   MiniResultModel.enabled_flag == 1)
            .order_by(MiniResultModel.id)
        )).scalars().all()
        return [
            {
                "name": r.name, "status": r.status, "log": r.log,
                "before_img": r.before_img, "after_img": r.after_img,
                "assert_value": r.assert_value,
                "create_time": str(r.create_time) if r.create_time else "",
            }
            for r in rows
        ]

    @staticmethod
    def get_frameworks() -> list:
        return list_frameworks()

    @staticmethod
    def get_platforms() -> Dict:
        return list_platforms()

    @staticmethod
    async def get_run_status(result_id: str, user_id: int) -> Dict:
        """查询执行状态"""
        with _index_lock:
            running_pids = [
                pid for pid, info in _pid_index.items()
                if info.get("result_id") == result_id
            ]
        is_running = any(psutil.pid_exists(pid) for pid in running_pids)
        return {"result_id": result_id, "is_running": is_running}

    @staticmethod
    async def delete_result(db: AsyncSession, result_id: str, user_id: int) -> bool:
        """删除执行记录"""
        row = (await db.execute(
            select(MiniResultListModel).where(
                MiniResultListModel.result_id == result_id,
                MiniResultListModel.user_id == user_id,
            )
        )).scalar_one_or_none()
        if not row:
            return False
        await db.execute(
            delete(MiniResultModel).where(
                MiniResultModel.result_id == result_id,
                MiniResultModel.user_id == user_id,
            )
        )
        await db.execute(
            delete(MiniResultListModel).where(
                MiniResultListModel.result_id == result_id,
                MiniResultListModel.user_id == user_id,
            )
        )
        await db.commit()
        return True

    @staticmethod
    async def copy_script(db: AsyncSession, menu_id: int, new_name: str, user_id: int) -> Dict:
        """复制脚本"""
        src_menu = (await db.execute(
            select(MiniMenuModel).where(
                MiniMenuModel.id == menu_id,
                MiniMenuModel.user_id == user_id,
                MiniMenuModel.enabled_flag == 1,
            )
        )).scalar_one_or_none()
        if not src_menu:
            raise ValueError("脚本不存在")

        src_script = (await db.execute(
            select(MiniScriptModel).where(
                MiniScriptModel.menu_id == menu_id,
                MiniScriptModel.user_id == user_id,
            )
        )).scalar_one_or_none()

        new_menu = MiniMenuModel(
            name=new_name, pid=int(src_menu.pid),
            type=int(src_menu.type), user_id=user_id,
        )
        db.add(new_menu)
        await db.flush()

        if src_script:
            db.add(MiniScriptModel(
                menu_id=new_menu.id,
                platform=src_script.platform,
                framework=src_script.framework,
                script=list(src_script.script or []),
                platform_config=dict(src_script.platform_config or {}),
                user_id=user_id,
            ))
        await db.commit()
        return {"id": new_menu.id, "name": new_name, "pid": int(src_menu.pid), "type": int(src_menu.type)}
