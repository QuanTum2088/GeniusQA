#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import httpx
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from .model import AppUiTestRunServerModel, AppUiTestRunPhoneModel


def _server_row(r: AppUiTestRunServerModel) -> Dict[str, Any]:
    
    return {
        "id": r.id,
        "name": r.name,
        "num": r.num,
        "os": r.server_os,
        "server_os": r.server_os,
        "ip": r.ip,
        "port": r.port,
        "appium_version": r.appium_version,
        "status": r.status,
    }


def _phone_row(r: AppUiTestRunPhoneModel) -> Dict[str, Any]:
    return {
        "id": r.id,
        "name": r.name,
        "num": r.num,
        "os": r.phone_os,
        "phone_os": r.phone_os,
        "os_version": r.os_version,
        "device_id": r.device_id,
        "extends": r.extends or {},
        "screen": r.screen,
    }


class AppDeviceCenterService:
  

    # ---------- Appium server ----------
    @staticmethod
    async def server_list(
        db: AsyncSession,
        user_id: int,
        page: int,
        page_size: int,
        name: Optional[str],
        server_os: Optional[str],
        ip: Optional[str],
        port: Optional[str],
    ) -> Tuple[int, List[Dict[str, Any]]]:
        q = [
            AppUiTestRunServerModel.user_id == user_id,
            AppUiTestRunServerModel.enabled_flag == 1,
        ]
        if name:
            q.append(AppUiTestRunServerModel.name.contains(name))
        if server_os:
            q.append(AppUiTestRunServerModel.server_os == server_os)
        if ip:
            q.append(AppUiTestRunServerModel.ip.contains(ip))
        if port:
            q.append(AppUiTestRunServerModel.port == port)

        cnt = await db.scalar(select(func.count()).select_from(AppUiTestRunServerModel).where(*q))
        total = int(cnt or 0)
        offset = (page - 1) * page_size
        res = await db.execute(
            select(AppUiTestRunServerModel)
            .where(*q)
            .order_by(AppUiTestRunServerModel.num.asc(), AppUiTestRunServerModel.id.asc())
            .offset(offset)
            .limit(page_size)
        )
        rows = res.scalars().all()
        return total, [_server_row(r) for r in rows]

    @staticmethod
    async def server_get(db: AsyncSession, user_id: int, sid: int) -> AppUiTestRunServerModel:
        res = await db.execute(
            select(AppUiTestRunServerModel).where(
                AppUiTestRunServerModel.id == sid,
                AppUiTestRunServerModel.user_id == user_id,
                AppUiTestRunServerModel.enabled_flag == 1,
            )
        )
        row = res.scalar_one_or_none()
        if not row:
            raise ValueError("服务器不存在")
        return row

    @staticmethod
    async def server_add(db: AsyncSession, user_id: int, items: List[Dict[str, Any]]) -> None:
        max_num = await db.scalar(
            select(func.max(AppUiTestRunServerModel.num)).where(
                AppUiTestRunServerModel.user_id == user_id,
                AppUiTestRunServerModel.enabled_flag == 1,
            )
        )
        n = int(max_num or 0)
        for it in items:
            n += 1
            db.add(
                AppUiTestRunServerModel(
                    user_id=user_id,
                    name=it["name"],
                    num=n,
                    server_os=it["server_os"],
                    ip=it["ip"],
                    port=it.get("port") or "4723",
                    appium_version=it.get("appium_version") or "2.x",
                    status=0,
                    created_by=user_id,
                    updated_by=user_id,
                )
            )
        await db.commit()

    @staticmethod
    async def server_update(db: AsyncSession, user_id: int, sid: int, data: Dict[str, Any]) -> None:
        row = await AppDeviceCenterService.server_get(db, user_id, sid)
        await db.execute(
            update(AppUiTestRunServerModel)
            .where(AppUiTestRunServerModel.id == row.id)
            .values(
                name=data["name"],
                server_os=data["server_os"],
                ip=data["ip"],
                port=data.get("port") or "4723",
                appium_version=data.get("appium_version") or "2.x",
                updated_by=user_id,
            )
        )
        await db.commit()

    @staticmethod
    async def server_delete(db: AsyncSession, user_id: int, sid: int) -> None:
        await AppDeviceCenterService.server_get(db, user_id, sid)
        await db.execute(
            update(AppUiTestRunServerModel)
            .where(
                AppUiTestRunServerModel.id == sid,
                AppUiTestRunServerModel.user_id == user_id,
            )
            .values(enabled_flag=0, updated_by=user_id)
        )
        await db.commit()

    @staticmethod
    async def server_copy(db: AsyncSession, user_id: int, sid: int) -> Dict[str, Any]:
        row = await AppDeviceCenterService.server_get(db, user_id, sid)
        base = row.name or "server"
        new_name = f"{base}_copy"
        suffix = 1
        while True:
            exists = await db.scalar(
                select(func.count()).select_from(AppUiTestRunServerModel).where(
                    AppUiTestRunServerModel.user_id == user_id,
                    AppUiTestRunServerModel.enabled_flag == 1,
                    AppUiTestRunServerModel.name == new_name,
                )
            )
            if not exists:
                break
            suffix += 1
            new_name = f"{base}_copy{suffix}"
        max_num = await db.scalar(
            select(func.max(AppUiTestRunServerModel.num)).where(
                AppUiTestRunServerModel.user_id == user_id,
                AppUiTestRunServerModel.enabled_flag == 1,
            )
        )
        n = int(max_num or 0) + 1
        clone = AppUiTestRunServerModel(
            user_id=user_id,
            name=new_name,
            num=n,
            server_os=row.server_os,
            ip=row.ip,
            port=row.port,
            appium_version=row.appium_version,
            status=0,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(clone)
        await db.commit()
        await db.refresh(clone)
        return _server_row(clone)

    @staticmethod
    async def server_sort(db: AsyncSession, user_id: int, id_list: List[int]) -> None:
        for idx, sid in enumerate(id_list):
            await db.execute(
                update(AppUiTestRunServerModel)
                .where(
                    AppUiTestRunServerModel.id == sid,
                    AppUiTestRunServerModel.user_id == user_id,
                    AppUiTestRunServerModel.enabled_flag == 1,
                )
                .values(num=idx + 1, updated_by=user_id)
            )
        await db.commit()

    @staticmethod
    async def server_run_check(db: AsyncSession, user_id: int, sid: int) -> str:
        row = await AppDeviceCenterService.server_get(db, user_id, sid)
        url = f"http://{row.ip}:{row.port}"
        status_code: Optional[int] = None
        try:
            async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                r = await client.get(url)
                status_code = r.status_code
        except Exception:
            await db.execute(
                update(AppUiTestRunServerModel)
                .where(AppUiTestRunServerModel.id == sid)
                .values(status=1, updated_by=user_id)
            )
            await db.commit()
            raise ValueError("无法访问该 Appium 地址，请检查 IP、端口与防火墙")
        if status_code is not None and status_code > 499:
            await db.execute(
                update(AppUiTestRunServerModel)
                .where(AppUiTestRunServerModel.id == sid)
                .values(status=1, updated_by=user_id)
            )
            await db.commit()
            raise ValueError(f"服务器响应异常，HTTP {status_code}")
        await db.execute(
            update(AppUiTestRunServerModel)
            .where(AppUiTestRunServerModel.id == sid)
            .values(status=2, updated_by=user_id)
        )
        await db.commit()
        return f"连接成功，HTTP {status_code}"

    # ---------- Run phone ----------
    @staticmethod
    async def phone_list(
        db: AsyncSession,
        user_id: int,
        page: int,
        page_size: int,
        name: Optional[str],
        phone_os: Optional[str],
        os_version: Optional[str],
    ) -> Tuple[int, List[Dict[str, Any]]]:
        q = [
            AppUiTestRunPhoneModel.user_id == user_id,
            AppUiTestRunPhoneModel.enabled_flag == 1,
        ]
        if name:
            q.append(AppUiTestRunPhoneModel.name.contains(name))
        if phone_os:
            q.append(AppUiTestRunPhoneModel.phone_os == phone_os)
        if os_version:
            q.append(AppUiTestRunPhoneModel.os_version.contains(os_version))

        cnt = await db.scalar(select(func.count()).select_from(AppUiTestRunPhoneModel).where(*q))
        total = int(cnt or 0)
        offset = (page - 1) * page_size
        res = await db.execute(
            select(AppUiTestRunPhoneModel)
            .where(*q)
            .order_by(AppUiTestRunPhoneModel.num.asc(), AppUiTestRunPhoneModel.id.asc())
            .offset(offset)
            .limit(page_size)
        )
        rows = res.scalars().all()
        return total, [_phone_row(r) for r in rows]

    @staticmethod
    async def phone_get(db: AsyncSession, user_id: int, pid: int) -> AppUiTestRunPhoneModel:
        res = await db.execute(
            select(AppUiTestRunPhoneModel).where(
                AppUiTestRunPhoneModel.id == pid,
                AppUiTestRunPhoneModel.user_id == user_id,
                AppUiTestRunPhoneModel.enabled_flag == 1,
            )
        )
        row = res.scalar_one_or_none()
        if not row:
            raise ValueError("设备不存在")
        return row

    @staticmethod
    async def phone_add(db: AsyncSession, user_id: int, items: List[Dict[str, Any]]) -> None:
        max_num = await db.scalar(
            select(func.max(AppUiTestRunPhoneModel.num)).where(
                AppUiTestRunPhoneModel.user_id == user_id,
                AppUiTestRunPhoneModel.enabled_flag == 1,
            )
        )
        n = int(max_num or 0)
        for it in items:
            n += 1
            db.add(
                AppUiTestRunPhoneModel(
                    user_id=user_id,
                    name=it["name"],
                    num=n,
                    phone_os=it["phone_os"],
                    os_version=it.get("os_version") or "",
                    device_id=it["device_id"],
                    extends=it.get("extends") or {},
                    screen=it.get("screen") or "",
                    created_by=user_id,
                    updated_by=user_id,
                )
            )
        await db.commit()

    @staticmethod
    async def phone_update(db: AsyncSession, user_id: int, pid: int, data: Dict[str, Any]) -> None:
        await AppDeviceCenterService.phone_get(db, user_id, pid)
        await db.execute(
            update(AppUiTestRunPhoneModel)
            .where(AppUiTestRunPhoneModel.id == pid)
            .values(
                name=data["name"],
                phone_os=data["phone_os"],
                os_version=data.get("os_version") or "",
                device_id=data["device_id"],
                extends=data.get("extends") or {},
                screen=data.get("screen") or "",
                updated_by=user_id,
            )
        )
        await db.commit()

    @staticmethod
    async def phone_delete(db: AsyncSession, user_id: int, pid: int) -> None:
        await AppDeviceCenterService.phone_get(db, user_id, pid)
        await db.execute(
            update(AppUiTestRunPhoneModel)
            .where(AppUiTestRunPhoneModel.id == pid, AppUiTestRunPhoneModel.user_id == user_id)
            .values(enabled_flag=0, updated_by=user_id)
        )
        await db.commit()

    @staticmethod
    async def phone_copy(db: AsyncSession, user_id: int, pid: int) -> Dict[str, Any]:
        row = await AppDeviceCenterService.phone_get(db, user_id, pid)
        base = row.name or "phone"
        new_name = f"{base}_copy"
        suffix = 1
        while True:
            exists = await db.scalar(
                select(func.count()).select_from(AppUiTestRunPhoneModel).where(
                    AppUiTestRunPhoneModel.user_id == user_id,
                    AppUiTestRunPhoneModel.enabled_flag == 1,
                    AppUiTestRunPhoneModel.name == new_name,
                )
            )
            if not exists:
                break
            suffix += 1
            new_name = f"{base}_copy{suffix}"
        max_num = await db.scalar(
            select(func.max(AppUiTestRunPhoneModel.num)).where(
                AppUiTestRunPhoneModel.user_id == user_id,
                AppUiTestRunPhoneModel.enabled_flag == 1,
            )
        )
        n = int(max_num or 0) + 1
        clone = AppUiTestRunPhoneModel(
            user_id=user_id,
            name=new_name,
            num=n,
            phone_os=row.phone_os,
            os_version=row.os_version,
            device_id=row.device_id,
            extends=row.extends or {},
            screen=row.screen,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(clone)
        await db.commit()
        await db.refresh(clone)
        return _phone_row(clone)

    @staticmethod
    async def phone_sort(db: AsyncSession, user_id: int, id_list: List[int]) -> None:
        for idx, pid in enumerate(id_list):
            await db.execute(
                update(AppUiTestRunPhoneModel)
                .where(
                    AppUiTestRunPhoneModel.id == pid,
                    AppUiTestRunPhoneModel.user_id == user_id,
                    AppUiTestRunPhoneModel.enabled_flag == 1,
                )
                .values(num=idx + 1, updated_by=user_id)
            )
        await db.commit()

    @staticmethod
    def ntest_remote_url(host: str, port: str, remote_path: Optional[str]) -> str:
       
        rp = (remote_path or "").strip()
        if rp and not rp.startswith("/"):
            rp = "/" + rp
        return f"http://{str(host).strip()}:{str(port).strip()}{rp}"

    @staticmethod
    def session_capabilities_only(full_cfg: Dict[str, Any]) -> Dict[str, Any]:
        """去掉仅服务端使用的字段，得到可交给 Appium Client 的 capabilities。"""
        c = dict(full_cfg)
        for k in ("host", "port", "remote_path", "server_id", "phone_id", "device"):
            c.pop(k, None)
        return c

    @staticmethod
    def build_appium_capabilities(
        *,
        server_ip: str,
        server_port: str,
        appium_version: str,
        phone_os: str,
        os_version: str,
        device_id: str,
        app_package: str,
        app_activity: str,
        no_reset: bool = False,
        command_timeout: int = 120,
    ) -> Dict[str, Any]:
        """生成 Appium capabilities"""
        remote_path = "/wd/hub" if (appium_version or "").startswith("1") else ""
        cfg: Dict[str, Any] = {
            "host": server_ip,
            "port": server_port,
            "remote_path": remote_path,
            "newCommandTimeout": int(command_timeout),
            "noReset": no_reset,
            "platformName": phone_os,
            "platformVersion": os_version or "",
            "deviceName": device_id,
            "udid": device_id,
        }
        po = (phone_os or "").lower()
        if po == "android":
            cfg["automationName"] = "UIAutomator2"
            cfg["appPackage"] = app_package
            cfg["appActivity"] = app_activity
        else:
            cfg["automationName"] = "XCUITest"
            cfg["platformName"] = "iOS"
            cfg["xcodeOrgId"] = ""
            cfg["xcodeSigningId"] = "iPhone Developer"
        return cfg
