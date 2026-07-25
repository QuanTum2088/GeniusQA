#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from .model import (
    NtestRepositoryModel,
    NtestCoverageReportModel,
    NtestCoverageDetailModel,
)
from .jacoco_parser import JaCoCoParser


def _row_to_dict(row) -> Dict[str, Any]:
    """Convert a SQLAlchemy model instance to a plain dict."""
    d = row.__dict__.copy()
    d.pop("_sa_instance_state", None)
    return d


# ---------------------------------------------------------------------------
# JaCoCo CLI jar path — resolved relative to the backend root
# ---------------------------------------------------------------------------
def _get_jacoco_jar_path() -> str:
    """Return the absolute path to org.jacoco.cli.jar."""
    backend_root = Path(__file__).resolve().parents[4]
    jar = backend_root / "org.jacoco.cli.jar"
    if not jar.exists():
        raise FileNotFoundError(
            f"org.jacoco.cli.jar not found at {jar}. "
            "Please place the jar in the project root directory."
        )
    return str(jar)


class PrecisionTestService:
    """精准测试服务层"""

    # ------------------------------------------------------------------ #
    # Task 3.1 — Repository management methods                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    async def list_repositories(
        db: AsyncSession, body: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """分页查询仓库列表"""
        service_id = body.get("service_id")
        name_filter = body.get("name", "")
        page = int(body.get("page", 1))
        page_size = int(body.get("pageSize", 20))

        stmt = (
            select(NtestRepositoryModel)
            .where(
                NtestRepositoryModel.service_id == service_id,
                NtestRepositoryModel.enabled_flag == 1,
            )
        )
        if name_filter:
            stmt = stmt.where(
                NtestRepositoryModel.name.like(f"%{name_filter}%")
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Paginate
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        rows = result.scalars().all()
        content = [_row_to_dict(r) for r in rows]

        return {
            "content": content,
            "total": total,
            "page": page,
            "pageSize": page_size,
        }

    @staticmethod
    async def save_repository(
        db: AsyncSession, body: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """新增或更新仓库"""
        repo_id = body.get("id")

        if repo_id:
            # UPDATE
            result = await db.execute(
                select(NtestRepositoryModel).where(
                    NtestRepositoryModel.id == repo_id,
                    NtestRepositoryModel.enabled_flag == 1,
                )
            )
            repo = result.scalar_one_or_none()
            if not repo:
                return {"code": 400, "message": "仓库不存在", "data": None}

            repo.name = body.get("name", repo.name)
            repo.html_url = body.get("html_url", repo.html_url)
            repo.description = body.get("description", repo.description)
            repo.service_id = body.get("service_id", repo.service_id)
            repo.service_host = body.get("service_host", repo.service_host)
            repo.jacoco_port = int(body.get("jacoco_port") or repo.jacoco_port or 6300)
            repo.lang_type = body.get("lang_type", repo.lang_type) or "java"
            repo.updated_by = user_id
            repo.updation_date = datetime.now()
            await db.flush()
            return _row_to_dict(repo)
        else:
            # INSERT
            repo = NtestRepositoryModel(
                name=body.get("name"),
                html_url=body.get("html_url"),
                description=body.get("description"),
                service_id=body.get("service_id"),
                service_host=body.get("service_host"),
                jacoco_port=int(body.get("jacoco_port") or 6300),
                lang_type=body.get("lang_type") or "java",
                created_by=user_id,
                updated_by=user_id,
            )
            db.add(repo)
            await db.flush()
            await db.refresh(repo)
            return _row_to_dict(repo)

    @staticmethod
    async def delete_repository(
        db: AsyncSession, body: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """逻辑删除仓库"""
        repo_id = body.get("id")

        result = await db.execute(
            select(NtestRepositoryModel).where(
                NtestRepositoryModel.id == repo_id,
                NtestRepositoryModel.enabled_flag == 1,
            )
        )
        repo = result.scalar_one_or_none()
        if not repo:
            return {"code": 400, "message": "仓库不存在", "data": None}

        repo.enabled_flag = 0
        repo.updated_by = user_id
        repo.updation_date = datetime.now()
        await db.flush()
        return {"code": 0, "message": "删除成功", "data": None}

    # ------------------------------------------------------------------ #
    # Task 3.2 — Coverage report management methods                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    async def list_reports(
        db: AsyncSession, body: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """分页查询覆盖率报告列表"""
        service_id = body.get("service_id")
        name_filter = body.get("name", "")
        page = int(body.get("page", 1))
        page_size = int(body.get("pageSize", 20))

        stmt = (
            select(NtestCoverageReportModel)
            .where(
                NtestCoverageReportModel.service_id == service_id,
                NtestCoverageReportModel.enabled_flag == 1,
            )
        )
        if name_filter:
            stmt = stmt.where(
                NtestCoverageReportModel.name.like(f"%{name_filter}%")
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        rows = result.scalars().all()
        content = [_row_to_dict(r) for r in rows]

        return {
            "content": content,
            "total": total,
            "page": page,
            "pageSize": page_size,
        }

    @staticmethod
    async def get_report(
        db: AsyncSession, body: Dict[str, Any], user_id: int
    ) -> Optional[Dict[str, Any]]:
        """按 id 查询单条报告"""
        report_id = body.get("id")
        result = await db.execute(
            select(NtestCoverageReportModel).where(
                NtestCoverageReportModel.id == report_id,
                NtestCoverageReportModel.enabled_flag == 1,
            )
        )
        report = result.scalar_one_or_none()
        if not report:
            return {"code": 400, "message": "报告不存在", "data": None}
        return _row_to_dict(report)

    @staticmethod
    async def delete_report(
        db: AsyncSession, body: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """逻辑删除覆盖率报告"""
        report_id = body.get("id")
        result = await db.execute(
            select(NtestCoverageReportModel).where(
                NtestCoverageReportModel.id == report_id,
                NtestCoverageReportModel.enabled_flag == 1,
            )
        )
        report = result.scalar_one_or_none()
        if not report:
            return {"code": 400, "message": "报告不存在", "data": None}

        report.enabled_flag = 0
        report.updated_by = user_id
        report.updation_date = datetime.now()
        await db.flush()
        return {"code": 0, "message": "删除成功", "data": None}

    @staticmethod
    async def trigger_coverage(
        db: AsyncSession, body: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """触发覆盖率分析，创建报告记录"""
        coverage_type = body.get("coverage_type")
        old_branch = body.get("old_branch", "") or ""
        repo_id = body.get("repo_id")
        new_branch = body.get("new_branch", "")

        # Validate: incremental mode requires old_branch
        if coverage_type == 20 and not old_branch.strip():
            raise HTTPException(
                status_code=422,
                detail="增量模式下旧分支不能为空",
            )

        # Validate repo exists
        repo_result = await db.execute(
            select(NtestRepositoryModel).where(
                NtestRepositoryModel.id == repo_id,
                NtestRepositoryModel.enabled_flag == 1,
            )
        )
        repo = repo_result.scalar_one_or_none()
        if not repo:
            return {"code": 400, "message": "仓库不存在", "data": None}

        # Derive report name
        name = body.get("name") or f"report_{repo_id}_{new_branch}"

        # Create coverage report record
        report = NtestCoverageReportModel(
            name=name,
            service_id=repo.service_id,
            repo_id=repo_id,
            coverage_type=coverage_type,
            new_branches=new_branch,
            old_branches=old_branch if old_branch.strip() else None,
            package_count=0,
            class_count=0,
            method_count=0,
            coverage_rate="0.0%",
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(report)
        await db.flush()
        await db.refresh(report)
        return {"id": report.id}

    # ------------------------------------------------------------------ #
    # Task 3.3 — Coverage detail query methods                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    async def get_coverage_detail(
        db: AsyncSession, body: Dict[str, Any], user_id: int
    ) -> Any:
        """根据 el_type 返回不同层级的覆盖率详情"""
        el_type = body.get("el_type")
        report_id = body.get("report_id")

        if el_type == "report":
            # GROUP BY package_name, SUM all counter fields
            stmt = (
                select(
                    NtestCoverageDetailModel.package_name,
                    func.sum(NtestCoverageDetailModel.branch_missed).label("branch_missed"),
                    func.sum(NtestCoverageDetailModel.branch_covered).label("branch_covered"),
                    func.sum(NtestCoverageDetailModel.instruction_missed).label("instruction_missed"),
                    func.sum(NtestCoverageDetailModel.instruction_covered).label("instruction_covered"),
                    func.sum(NtestCoverageDetailModel.line_missed).label("line_missed"),
                    func.sum(NtestCoverageDetailModel.line_covered).label("line_covered"),
                    func.sum(NtestCoverageDetailModel.method_missed).label("method_missed"),
                    func.sum(NtestCoverageDetailModel.method_covered).label("method_covered"),
                    func.sum(NtestCoverageDetailModel.class_missed).label("class_missed"),
                    func.sum(NtestCoverageDetailModel.class_covered).label("class_covered"),
                )
                .where(
                    NtestCoverageDetailModel.report_id == report_id,
                    NtestCoverageDetailModel.enabled_flag == 1,
                )
                .group_by(NtestCoverageDetailModel.package_name)
            )
            result = await db.execute(stmt)
            rows = result.all()
            return [
                {
                    "package_name": r.package_name,
                    "branch_missed": r.branch_missed or 0,
                    "branch_covered": r.branch_covered or 0,
                    "instruction_missed": r.instruction_missed or 0,
                    "instruction_covered": r.instruction_covered or 0,
                    "line_missed": r.line_missed or 0,
                    "line_covered": r.line_covered or 0,
                    "method_missed": r.method_missed or 0,
                    "method_covered": r.method_covered or 0,
                    "class_missed": r.class_missed or 0,
                    "class_covered": r.class_covered or 0,
                }
                for r in rows
            ]

        elif el_type == "package":
            package_name = body.get("package_name")
            stmt = (
                select(NtestCoverageDetailModel)
                .where(
                    NtestCoverageDetailModel.report_id == report_id,
                    NtestCoverageDetailModel.package_name == package_name,
                    NtestCoverageDetailModel.enabled_flag == 1,
                )
            )
            result = await db.execute(stmt)
            rows = result.scalars().all()
            return [
                {
                    "id": r.id,
                    "class_name": r.class_name,
                    "package_name": r.package_name,
                    "branch_missed": r.branch_missed or 0,
                    "branch_covered": r.branch_covered or 0,
                    "instruction_missed": r.instruction_missed or 0,
                    "instruction_covered": r.instruction_covered or 0,
                    "line_missed": r.line_missed or 0,
                    "line_covered": r.line_covered or 0,
                    "method_missed": r.method_missed or 0,
                    "method_covered": r.method_covered or 0,
                    "class_missed": r.class_missed or 0,
                    "class_covered": r.class_covered or 0,
                }
                for r in rows
            ]

        elif el_type == "class":
            class_id = body.get("class_id")
            result = await db.execute(
                select(NtestCoverageDetailModel).where(
                    NtestCoverageDetailModel.id == class_id,
                    NtestCoverageDetailModel.enabled_flag == 1,
                )
            )
            row = result.scalar_one_or_none()
            if not row:
                return {"code": 400, "message": "类数据不存在", "data": None}
            return {
                "id": row.id,
                "class_name": row.class_name,
                "package_name": row.package_name,
                "class_file_content": row.class_file_content,
                "class_source_path": row.class_source_path,
                "class_md5": row.class_md5,
                "methods": row.methods or [],
            }

        else:
            return {"code": 400, "message": f"不支持的 el_type: {el_type}", "data": None}

    # ------------------------------------------------------------------ #
    # Task 3.4 — JaCoCo XML upload/parse method                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    async def upload_jacoco_xml(
        db: AsyncSession,
        file_bytes: bytes,
        report_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """解析 JaCoCo XML 并写入数据库"""
        parser = JaCoCoParser()

        # Validate
        if not parser.validate(file_bytes):
            raise HTTPException(status_code=400, detail="无效的 JaCoCo XML 文件")

        # Parse
        parse_result = parser.parse(file_bytes)

        # Bulk insert NtestCoverageDetailModel records (one per class)
        for pkg in parse_result.packages:
            for cls in pkg.classes:
                # Build method list
                methods_list: List[Dict[str, Any]] = []
                for method in cls.methods:
                    _mc = method.counters
                    method_entry: Dict[str, Any] = {
                        "name": method.name,
                        "params_string": method.desc,
                        "offset": method.offset,
                        "lines_covered_status": method.lines_covered_status,
                        "branch_missed": _mc["BRANCH"].missed if "BRANCH" in _mc else 0,
                        "branch_covered": _mc["BRANCH"].covered if "BRANCH" in _mc else 0,
                        "instruction_missed": _mc["INSTRUCTION"].missed if "INSTRUCTION" in _mc else 0,
                        "instruction_covered": _mc["INSTRUCTION"].covered if "INSTRUCTION" in _mc else 0,
                        "line_missed": _mc["LINE"].missed if "LINE" in _mc else 0,
                        "line_covered": _mc["LINE"].covered if "LINE" in _mc else 0,
                        "complexity_missed": _mc["COMPLEXITY"].missed if "COMPLEXITY" in _mc else 0,
                        "complexity_covered": _mc["COMPLEXITY"].covered if "COMPLEXITY" in _mc else 0,
                        "method_missed": _mc["METHOD"].missed if "METHOD" in _mc else 0,
                        "method_covered": _mc["METHOD"].covered if "METHOD" in _mc else 0,
                    }
                    methods_list.append(method_entry)

                # Class-level counters from cls.counters
                branch_c = cls.counters.get("BRANCH")
                instruction_c = cls.counters.get("INSTRUCTION")
                line_c = cls.counters.get("LINE")
                method_c = cls.counters.get("METHOD")
                class_c = cls.counters.get("CLASS")

                detail = NtestCoverageDetailModel(
                    report_id=report_id,
                    package_name=pkg.name,
                    class_name=cls.name,
                    class_file_content=cls.file_content,
                    class_source_path=cls.source_path,
                    class_md5=cls.md5,
                    methods=methods_list,
                    branch_missed=branch_c.missed if branch_c else 0,
                    branch_covered=branch_c.covered if branch_c else 0,
                    instruction_missed=instruction_c.missed if instruction_c else 0,
                    instruction_covered=instruction_c.covered if instruction_c else 0,
                    line_missed=line_c.missed if line_c else 0,
                    line_covered=line_c.covered if line_c else 0,
                    method_missed=method_c.missed if method_c else 0,
                    method_covered=method_c.covered if method_c else 0,
                    class_missed=class_c.missed if class_c else 0,
                    class_covered=class_c.covered if class_c else 0,
                    created_by=user_id,
                    updated_by=user_id,
                )
                db.add(detail)

        await db.flush()

        # Update NtestCoverageReportModel stats
        report_result = await db.execute(
            select(NtestCoverageReportModel).where(
                NtestCoverageReportModel.id == report_id,
            )
        )
        report = report_result.scalar_one_or_none()
        if report:
            report.package_count = parse_result.package_count
            report.class_count = parse_result.class_count
            report.method_count = parse_result.method_count
            report.coverage_rate = parse_result.coverage_rate
            report.updated_by = user_id
            report.updation_date = datetime.now()

        await db.flush()
        return {
            "package_count": parse_result.package_count,
            "class_count": parse_result.class_count,
            "method_count": parse_result.method_count,
            "coverage_rate": parse_result.coverage_rate,
        }

    # ------------------------------------------------------------------ #
    # JaCoCo Dump — call org.jacoco.cli.jar to pull .exec from agent      #
    # ------------------------------------------------------------------ #

    @staticmethod
    async def jacoco_dump(
        db: AsyncSession, body: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """
        通过 org.jacoco.cli.jar dump 命令从运行中的 JaCoCo agent 拉取覆盖率数据，
        然后生成 XML 报告并解析入库。

        body 参数:
          - report_id: int  (必填) 关联的覆盖率报告 ID
          - address: str    (可选) agent 地址，默认 localhost
          - port: int       (可选) agent 端口，默认 6300
          - reset: bool     (可选) dump 后是否重置 agent 数据，默认 False
        """
        report_id = body.get("report_id")
        address = body.get("address") or "localhost"
        port = int(body.get("port") or 6300)
        reset = bool(body.get("reset", False))

        if not report_id:
            raise HTTPException(status_code=422, detail="report_id 不能为空")

        # Verify report exists
        report_result = await db.execute(
            select(NtestCoverageReportModel).where(
                NtestCoverageReportModel.id == report_id,
                NtestCoverageReportModel.enabled_flag == 1,
            )
        )
        report = report_result.scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")

        try:
            jar_path = _get_jacoco_jar_path()
        except FileNotFoundError as e:
            raise HTTPException(status_code=500, detail=str(e))

        with tempfile.TemporaryDirectory() as tmpdir:
            exec_file = os.path.join(tmpdir, f"jacoco_{report_id}.exec")
            xml_file = os.path.join(tmpdir, f"jacoco_{report_id}.xml")

            # Step 1: dump .exec from running agent
            dump_cmd = [
                "java", "-jar", jar_path,
                "dump",
                "--address", address,
                "--port", str(port),
                "--destfile", exec_file,
                "--quiet",
            ]
            if reset:
                dump_cmd.append("--reset")

            proc = await asyncio.create_subprocess_exec(
                *dump_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

            if proc.returncode != 0:
                err_msg = stderr.decode("utf-8", errors="replace").strip()
                raise HTTPException(
                    status_code=502,
                    detail=f"JaCoCo dump 失败（address={address}:{port}）: {err_msg or 'unknown error'}",
                )

            if not os.path.exists(exec_file):
                raise HTTPException(
                    status_code=502,
                    detail=f"dump 命令执行成功但未生成 .exec 文件，请检查 agent 是否正在运行",
                )

            # Step 2: generate XML report from .exec
            # Note: --classfiles is not required for basic XML generation from .exec
            # The XML will contain raw counter data without source mapping
            report_cmd = [
                "java", "-jar", jar_path,
                "report", exec_file,
                "--xml", xml_file,
                "--quiet",
            ]

            proc2 = await asyncio.create_subprocess_exec(
                *report_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout2, stderr2 = await asyncio.wait_for(proc2.communicate(), timeout=60)

            if proc2.returncode != 0:
                err_msg2 = stderr2.decode("utf-8", errors="replace").strip()
                raise HTTPException(
                    status_code=502,
                    detail=f"JaCoCo report 生成失败: {err_msg2 or 'unknown error'}",
                )

            if not os.path.exists(xml_file):
                raise HTTPException(
                    status_code=502,
                    detail="report 命令执行成功但未生成 XML 文件",
                )

            # Step 3: parse XML and write to DB
            with open(xml_file, "rb") as f:
                xml_bytes = f.read()

            result = await PrecisionTestService.upload_jacoco_xml(
                db, xml_bytes, report_id, user_id
            )
            return {
                **result,
                "address": address,
                "port": port,
                "message": f"成功从 {address}:{port} 拉取覆盖率数据并解析入库",
            }
