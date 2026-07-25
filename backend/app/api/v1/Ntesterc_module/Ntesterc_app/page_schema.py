#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from typing import List, Optional
from pydantic import BaseModel, Field


class PageListBody(BaseModel):
    module_menu_id: int = Field(..., ge=1)
    currentPage: int = Field(default=1, ge=1)
    pageSize: int = Field(default=20, ge=1, le=200)


class PageAddBody(BaseModel):
    module_menu_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=255)
    remark: Optional[str] = None
    activity: Optional[str] = Field(default=None, max_length=512)
    package_name: Optional[str] = Field(default=None, max_length=255)


class PageIdBody(BaseModel):
    id: int = Field(..., ge=1)


class PageUpdateBody(PageIdBody):
    name: str = Field(..., min_length=1, max_length=255)
    remark: Optional[str] = None
    activity: Optional[str] = Field(default=None, max_length=512)
    package_name: Optional[str] = Field(default=None, max_length=255)


class PageSortBody(BaseModel):
    id_list: List[int] = Field(..., min_length=1)


class ElementListBody(BaseModel):
    page_id: int = Field(..., ge=1)


class ElementAddBody(BaseModel):
    page_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=255)
    locate_type: str = Field(default="id", max_length=64)
    locate_value: str = Field(..., min_length=1)


class ElementIdBody(BaseModel):
    id: int = Field(..., ge=1)


class ElementUpdateBody(ElementIdBody):
    name: str = Field(..., min_length=1, max_length=255)
    locate_type: str = Field(default="id", max_length=64)
    locate_value: str = Field(..., min_length=1)


class ElementSortBody(BaseModel):
    id_list: List[int] = Field(..., min_length=1)


class ElementImportItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    locate_type: str = Field(default="id", max_length=64)
    locate_value: str = Field(..., min_length=1)


class ElementImportBody(BaseModel):
    page_id: int = Field(..., ge=1)
    elements: List[ElementImportItem] = Field(..., min_length=1, max_length=500)
