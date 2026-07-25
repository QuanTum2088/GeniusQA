#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from __future__ import annotations
from typing import Any, Dict, List, Tuple
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from .model import AppMenuModel, AppUiElementModel, AppUiPageModel


def _page_row(r: AppUiPageModel) -> Dict[str, Any]:
    return {
        "id": r.id,
        "module_menu_id": r.module_menu_id,
        "name": r.name,
        "num": r.num,
        "remark": r.remark or "",
        "activity": r.activity or "",
        "package_name": r.package_name or "",
    }


def _element_row(r: AppUiElementModel) -> Dict[str, Any]:
    return {
        "id": r.id,
        "page_id": r.page_id,
        "name": r.name,
        "locate_type": r.locate_type,
        "locate_value": r.locate_value,
        "num": r.num,
    }


class AppPageService:
    @staticmethod
    async def _assert_module_menu(db: AsyncSession, user_id: int, menu_id: int) -> AppMenuModel:
        res = await db.execute(
            select(AppMenuModel).where(
                AppMenuModel.id == menu_id,
                AppMenuModel.user_id == user_id,
                AppMenuModel.enabled_flag == 1,
                AppMenuModel.type.in_((0, 1)),
            )
        )
        row = res.scalar_one_or_none()
        if not row:
            raise ValueError("模块不存在或无权访问（请选择左侧文件夹或根目录下的模块节点）")
        return row

    @staticmethod
    async def _assert_page(db: AsyncSession, user_id: int, page_id: int) -> AppUiPageModel:
        res = await db.execute(
            select(AppUiPageModel).where(
                AppUiPageModel.id == page_id,
                AppUiPageModel.user_id == user_id,
                AppUiPageModel.enabled_flag == 1,
            )
        )
        row = res.scalar_one_or_none()
        if not row:
            raise ValueError("页面不存在")
        return row

    @staticmethod
    async def page_list(
        db: AsyncSession,
        user_id: int,
        module_menu_id: int,
        page: int,
        page_size: int,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        await AppPageService._assert_module_menu(db, user_id, module_menu_id)
        q = [
            AppUiPageModel.user_id == user_id,
            AppUiPageModel.enabled_flag == 1,
            AppUiPageModel.module_menu_id == module_menu_id,
        ]
        cnt = await db.scalar(select(func.count()).select_from(AppUiPageModel).where(*q))
        total = int(cnt or 0)
        offset = (page - 1) * page_size
        res = await db.execute(
            select(AppUiPageModel)
            .where(*q)
            .order_by(AppUiPageModel.num.asc(), AppUiPageModel.id.asc())
            .offset(offset)
            .limit(page_size)
        )
        rows = res.scalars().all()
        return total, [_page_row(r) for r in rows]

    @staticmethod
    async def page_add(db: AsyncSession, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        await AppPageService._assert_module_menu(db, user_id, int(data["module_menu_id"]))
        max_num = await db.scalar(
            select(func.max(AppUiPageModel.num)).where(
                AppUiPageModel.user_id == user_id,
                AppUiPageModel.module_menu_id == int(data["module_menu_id"]),
                AppUiPageModel.enabled_flag == 1,
            )
        )
        n = int(max_num or 0) + 1
        row = AppUiPageModel(
            user_id=user_id,
            module_menu_id=int(data["module_menu_id"]),
            name=data["name"],
            num=n,
            remark=data.get("remark") or "",
            activity=data.get("activity") or None,
            package_name=data.get("package_name") or None,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return _page_row(row)

    @staticmethod
    async def page_update(db: AsyncSession, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        row = await AppPageService._assert_page(db, user_id, int(data["id"]))
        await db.execute(
            update(AppUiPageModel)
            .where(AppUiPageModel.id == row.id)
            .values(
                name=data["name"],
                remark=data.get("remark") or "",
                activity=data.get("activity") or None,
                package_name=data.get("package_name") or None,
                updated_by=user_id,
            )
        )
        await db.commit()
        await db.refresh(row)
        return _page_row(row)

    @staticmethod
    async def page_delete(db: AsyncSession, user_id: int, page_id: int) -> None:
        row = await AppPageService._assert_page(db, user_id, page_id)
        await db.execute(
            update(AppUiElementModel)
            .where(AppUiElementModel.page_id == row.id, AppUiElementModel.user_id == user_id)
            .values(enabled_flag=0, updated_by=user_id)
        )
        await db.execute(
            update(AppUiPageModel).where(AppUiPageModel.id == row.id).values(enabled_flag=0, updated_by=user_id)
        )
        await db.commit()

    @staticmethod
    async def page_sort(db: AsyncSession, user_id: int, id_list: List[int]) -> None:
        for idx, pid in enumerate(id_list):
            await db.execute(
                update(AppUiPageModel)
                .where(
                    AppUiPageModel.id == pid,
                    AppUiPageModel.user_id == user_id,
                    AppUiPageModel.enabled_flag == 1,
                )
                .values(num=idx + 1, updated_by=user_id)
            )
        await db.commit()

    @staticmethod
    async def page_copy(db: AsyncSession, user_id: int, page_id: int) -> Dict[str, Any]:
        src = await AppPageService._assert_page(db, user_id, page_id)
        base = (src.name or "页面") + "_副本"
        name = base
        suf = 1
        while True:
            exists = await db.scalar(
                select(func.count())
                .select_from(AppUiPageModel)
                .where(
                    AppUiPageModel.user_id == user_id,
                    AppUiPageModel.module_menu_id == src.module_menu_id,
                    AppUiPageModel.name == name,
                    AppUiPageModel.enabled_flag == 1,
                )
            )
            if not exists:
                break
            suf += 1
            name = f"{base}{suf}"
        max_num = await db.scalar(
            select(func.max(AppUiPageModel.num)).where(
                AppUiPageModel.user_id == user_id,
                AppUiPageModel.module_menu_id == src.module_menu_id,
                AppUiPageModel.enabled_flag == 1,
            )
        )
        clone = AppUiPageModel(
            user_id=user_id,
            module_menu_id=src.module_menu_id,
            name=name,
            num=int(max_num or 0) + 1,
            remark=src.remark,
            activity=src.activity,
            package_name=src.package_name,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(clone)
        await db.flush()
        eres = await db.execute(
            select(AppUiElementModel).where(
                AppUiElementModel.page_id == src.id,
                AppUiElementModel.user_id == user_id,
                AppUiElementModel.enabled_flag == 1,
            )
        )
        for e in eres.scalars().all():
            db.add(
                AppUiElementModel(
                    user_id=user_id,
                    page_id=int(clone.id),
                    name=e.name,
                    locate_type=e.locate_type,
                    locate_value=e.locate_value,
                    num=e.num,
                    created_by=user_id,
                    updated_by=user_id,
                )
            )
        await db.commit()
        await db.refresh(clone)
        return _page_row(clone)

    @staticmethod
    async def element_list(db: AsyncSession, user_id: int, page_id: int) -> List[Dict[str, Any]]:
        await AppPageService._assert_page(db, user_id, page_id)
        res = await db.execute(
            select(AppUiElementModel)
            .where(
                AppUiElementModel.page_id == page_id,
                AppUiElementModel.user_id == user_id,
                AppUiElementModel.enabled_flag == 1,
            )
            .order_by(AppUiElementModel.num.asc(), AppUiElementModel.id.asc())
        )
        return [_element_row(r) for r in res.scalars().all()]

    @staticmethod
    async def element_add(db: AsyncSession, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        await AppPageService._assert_page(db, user_id, int(data["page_id"]))
        max_num = await db.scalar(
            select(func.max(AppUiElementModel.num)).where(
                AppUiElementModel.user_id == user_id,
                AppUiElementModel.page_id == int(data["page_id"]),
                AppUiElementModel.enabled_flag == 1,
            )
        )
        n = int(max_num or 0) + 1
        row = AppUiElementModel(
            user_id=user_id,
            page_id=int(data["page_id"]),
            name=data["name"],
            locate_type=data.get("locate_type") or "id",
            locate_value=data["locate_value"],
            num=n,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return _element_row(row)

    @staticmethod
    async def element_update(db: AsyncSession, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        res = await db.execute(
            select(AppUiElementModel).where(
                AppUiElementModel.id == int(data["id"]),
                AppUiElementModel.user_id == user_id,
                AppUiElementModel.enabled_flag == 1,
            )
        )
        row = res.scalar_one_or_none()
        if not row:
            raise ValueError("元素不存在")
        await AppPageService._assert_page(db, user_id, int(row.page_id))
        await db.execute(
            update(AppUiElementModel)
            .where(AppUiElementModel.id == row.id)
            .values(
                name=data["name"],
                locate_type=data.get("locate_type") or "id",
                locate_value=data["locate_value"],
                updated_by=user_id,
            )
        )
        await db.commit()
        await db.refresh(row)
        return _element_row(row)

    @staticmethod
    async def element_delete(db: AsyncSession, user_id: int, element_id: int) -> None:
        res = await db.execute(
            select(AppUiElementModel).where(
                AppUiElementModel.id == element_id,
                AppUiElementModel.user_id == user_id,
                AppUiElementModel.enabled_flag == 1,
            )
        )
        row = res.scalar_one_or_none()
        if not row:
            raise ValueError("元素不存在")
        await db.execute(
            update(AppUiElementModel)
            .where(AppUiElementModel.id == element_id)
            .values(enabled_flag=0, updated_by=user_id)
        )
        await db.commit()

    @staticmethod
    async def element_sort(db: AsyncSession, user_id: int, id_list: List[int]) -> None:
        for idx, eid in enumerate(id_list):
            await db.execute(
                update(AppUiElementModel)
                .where(
                    AppUiElementModel.id == eid,
                    AppUiElementModel.user_id == user_id,
                    AppUiElementModel.enabled_flag == 1,
                )
                .values(num=idx + 1, updated_by=user_id)
            )
        await db.commit()

    @staticmethod
    async def element_import_bulk(
        db: AsyncSession, user_id: int, page_id: int, items: List[Dict[str, Any]]
    ) -> int:
        await AppPageService._assert_page(db, user_id, page_id)
        max_num = await db.scalar(
            select(func.max(AppUiElementModel.num)).where(
                AppUiElementModel.user_id == user_id,
                AppUiElementModel.page_id == page_id,
                AppUiElementModel.enabled_flag == 1,
            )
        )
        n = int(max_num or 0)
        count = 0
        for it in items:
            n += 1
            db.add(
                AppUiElementModel(
                    user_id=user_id,
                    page_id=page_id,
                    name=str(it["name"]).strip(),
                    locate_type=str(it.get("locate_type") or "id").strip() or "id",
                    locate_value=str(it["locate_value"]).strip(),
                    num=n,
                    created_by=user_id,
                    updated_by=user_id,
                )
            )
            count += 1
        await db.commit()
        return count
