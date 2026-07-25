#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from __future__ import annotations

import multiprocessing
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import threading
import psutil
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from .model import (
    DesktopMenuModel,
    DesktopResultListModel,
    DesktopResultModel,
    DesktopScriptModel,
)
from .runners.factory import list_frameworks

# 进程索引（内存级，重启后清空）
_pid_index: Dict[int, Dict[str, Any]] = {}
_proc_index: Dict[int, multiprocessing.Process] = {}
_index_lock = threading.Lock()


def _cleanup_finished_processes() -> None:
    """清理已结束的子进程，防止内存泄漏"""
    with _index_lock:
        finished = [pid for pid, p in _proc_index.items() if not p.is_alive()]
        for pid in finished:
            _pid_index.pop(pid, None)
            proc = _proc_index.pop(pid, None)
            if proc:
                proc.join(timeout=1)  # 回收资源，避免僵尸进程


class DesktopAutomationService:

    # ── 菜单 ──────────────────────────────────────────────
    @staticmethod
    async def get_menu(db: AsyncSession, user_id: int, project_id: Optional[int] = None) -> List[Dict]:
        q = select(DesktopMenuModel).where(
            DesktopMenuModel.user_id == user_id,
            DesktopMenuModel.enabled_flag == 1,
        )
        if project_id:
            q = q.where(DesktopMenuModel.project_id == project_id)
        rows = (await db.execute(q.order_by(DesktopMenuModel.id))).scalars().all()

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
        menu = DesktopMenuModel(name=name, pid=pid, type=mtype, user_id=user_id, project_id=project_id)
        db.add(menu)
        await db.flush()
        if mtype == 2:
            db.add(DesktopScriptModel(menu_id=menu.id, framework="pywinauto", script=[], user_id=user_id))
        await db.commit()
        return {"id": menu.id, "name": name, "pid": pid, "type": mtype}

    @staticmethod
    async def rename_menu(db: AsyncSession, menu_id: int, name: str, user_id: int) -> bool:
        await db.execute(
            update(DesktopMenuModel)
            .where(DesktopMenuModel.id == menu_id, DesktopMenuModel.user_id == user_id)
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
                select(DesktopMenuModel.id).where(
                    DesktopMenuModel.pid == mid,
                    DesktopMenuModel.user_id == user_id,
                    DesktopMenuModel.enabled_flag == 1,
                )
            )).scalars().all()
            for cid in children:
                ids.extend(await _collect_ids(cid))
            return ids

        all_ids = await _collect_ids(menu_id)
        await db.execute(
            delete(DesktopScriptModel).where(
                DesktopScriptModel.menu_id.in_(all_ids),
                DesktopScriptModel.user_id == user_id,
            )
        )
        await db.execute(
            delete(DesktopMenuModel).where(
                DesktopMenuModel.id.in_(all_ids),
                DesktopMenuModel.user_id == user_id,
            )
        )
        await db.commit()
        return True

    # ── 脚本 ──────────────────────────────────────────────
    @staticmethod
    async def get_script(db: AsyncSession, menu_id: int, user_id: int) -> Dict:
        row = (await db.execute(
            select(DesktopScriptModel)
            .where(DesktopScriptModel.menu_id == menu_id, DesktopScriptModel.user_id == user_id,
                   DesktopScriptModel.enabled_flag == 1)
        )).scalar_one_or_none()
        if not row:
            return {"id": menu_id, "framework": "pywinauto", "script": []}
        return {"id": row.menu_id, "framework": row.framework, "script": row.script or []}

    @staticmethod
    async def save_script(db: AsyncSession, menu_id: int, framework: str,
                          steps: List[Dict], user_id: int) -> bool:
        row = (await db.execute(
            select(DesktopScriptModel)
            .where(DesktopScriptModel.menu_id == menu_id, DesktopScriptModel.user_id == user_id)
        )).scalar_one_or_none()
        if row:
            row.framework = framework
            row.script = steps
            flag_modified(row, "script")
        else:
            db.add(DesktopScriptModel(menu_id=menu_id, framework=framework, script=steps, user_id=user_id))
        await db.commit()
        return True

    # ── 执行 ──────────────────────────────────────────────
    @staticmethod
    async def run_script(db: AsyncSession, menu_id: int, task_name: str,
                         result_id: str, framework: str, user_id: int,
                         project_id: Optional[int] = None) -> Dict:
        from .executor import run_desktop_process

        row = (await db.execute(
            select(DesktopScriptModel)
            .where(DesktopScriptModel.menu_id == menu_id, DesktopScriptModel.user_id == user_id,
                   DesktopScriptModel.enabled_flag == 1)
        )).scalar_one_or_none()
        steps = list(row.script or []) if row else []

        db.add(DesktopResultListModel(
            task_name=task_name,
            result_id=result_id,
            framework=framework,
            script_list=[{"id": menu_id, "name": task_name}],
            script_status=[{"status": "running", "total": len(steps), "passed": 0, "fail": 0}],
            project_id=project_id,
            user_id=user_id,
        ))
        await db.commit()

        # 启动子进程
        p = multiprocessing.Process(
            target=run_desktop_process,
            kwargs=dict(
                result_id=result_id,
                menu_id=menu_id,
                user_id=user_id,
                steps=steps,
                framework=framework,
                task_name=task_name,
            ),
            daemon=False,  # 非 daemon：父进程重启后子进程仍可完成当前任务
        )
        p.start()
        with _index_lock:
            _pid_index[p.pid] = {"result_id": result_id, "menu_id": menu_id}
            _proc_index[p.pid] = p

        # 定期清理已结束的进程
        _cleanup_finished_processes()

        return {"result_id": result_id, "pid": p.pid}

    @staticmethod
    async def stop_script(db: AsyncSession, result_id: str, user_id: int) -> bool:
        row = (await db.execute(
            select(DesktopResultListModel)
            .where(DesktopResultListModel.result_id == result_id,
                   DesktopResultListModel.user_id == user_id)
        )).scalar_one_or_none()
        if not row:
            return False

        # 终止进程
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

    # ── 结果查询 ──────────────────────────────────────────
    @staticmethod
    async def get_result_list(db: AsyncSession, user_id: int,
                              page: int, page_size: int, search: Dict) -> Dict:
        q = select(DesktopResultListModel).where(
            DesktopResultListModel.user_id == user_id,
            DesktopResultListModel.enabled_flag == 1,
        )
        if search.get("task_name"):
            q = q.where(DesktopResultListModel.task_name.contains(search["task_name"]))
        if search.get("project_id"):
            q = q.where(DesktopResultListModel.project_id == int(search["project_id"]))
        q = q.order_by(DesktopResultListModel.id.desc())

        from sqlalchemy import func
        total_q = select(func.count()).select_from(q.subquery())
        total = (await db.execute(total_q)).scalar() or 0

        rows = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()
        content = [
            {
                "id": r.id, "task_name": r.task_name, "result_id": r.result_id,
                "framework": r.framework, "script_status": r.script_status,
                "start_time": str(r.start_time) if r.start_time else "",
                "end_time": str(r.end_time) if r.end_time else "",
            }
            for r in rows
        ]
        return {"content": content, "total": total, "page": page, "pageSize": page_size}

    @staticmethod
    async def get_result_detail(db: AsyncSession, result_id: str, user_id: int) -> List[Dict]:
        rows = (await db.execute(
            select(DesktopResultModel)
            .where(DesktopResultModel.result_id == result_id,
                   DesktopResultModel.user_id == user_id,
                   DesktopResultModel.enabled_flag == 1)
            .order_by(DesktopResultModel.id)
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
    def get_frameworks() -> List[str]:
        return list_frameworks()

    @staticmethod
    async def get_run_status(result_id: str, user_id: int) -> Dict:
        """查询执行状态（是否还在运行）"""
        with _index_lock:
            running_pids = [
                pid for pid, info in _pid_index.items()
                if info.get("result_id") == result_id
            ]
        is_running = any(
            psutil.pid_exists(pid) for pid in running_pids
        )
        return {"result_id": result_id, "is_running": is_running}

    @staticmethod
    async def delete_result(db: AsyncSession, result_id: str, user_id: int) -> bool:
        """删除执行记录（汇总 + 步骤详情）"""
        # 先确认归属
        row = (await db.execute(
            select(DesktopResultListModel).where(
                DesktopResultListModel.result_id == result_id,
                DesktopResultListModel.user_id == user_id,
            )
        )).scalar_one_or_none()
        if not row:
            return False
        await db.execute(
            delete(DesktopResultModel).where(
                DesktopResultModel.result_id == result_id,
                DesktopResultModel.user_id == user_id,
            )
        )
        await db.execute(
            delete(DesktopResultListModel).where(
                DesktopResultListModel.result_id == result_id,
                DesktopResultListModel.user_id == user_id,
            )
        )
        await db.commit()
        return True

    @staticmethod
    async def copy_script(db: AsyncSession, menu_id: int, new_name: str, user_id: int) -> Dict:
        """复制脚本到同级目录"""
        # 获取原菜单节点
        src_menu = (await db.execute(
            select(DesktopMenuModel).where(
                DesktopMenuModel.id == menu_id,
                DesktopMenuModel.user_id == user_id,
                DesktopMenuModel.enabled_flag == 1,
            )
        )).scalar_one_or_none()
        if not src_menu:
            raise ValueError("脚本不存在")

        # 获取原脚本内容
        src_script = (await db.execute(
            select(DesktopScriptModel).where(
                DesktopScriptModel.menu_id == menu_id,
                DesktopScriptModel.user_id == user_id,
            )
        )).scalar_one_or_none()

        # 创建新菜单节点
        new_menu = DesktopMenuModel(
            name=new_name, pid=int(src_menu.pid),
            type=int(src_menu.type), user_id=user_id,
        )
        db.add(new_menu)
        await db.flush()

        # 复制脚本内容
        if src_script:
            db.add(DesktopScriptModel(
                menu_id=new_menu.id,
                framework=src_script.framework,
                script=list(src_script.script or []),
                user_id=user_id,
            ))
        await db.commit()
        return {"id": new_menu.id, "name": new_name, "pid": int(src_menu.pid), "type": int(src_menu.type)}
