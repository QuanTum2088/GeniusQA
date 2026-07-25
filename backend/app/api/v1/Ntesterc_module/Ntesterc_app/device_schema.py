#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ServerListBody(BaseModel):
    currentPage: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1, le=200)
    name: Optional[str] = None
    os: Optional[str] = None  
    server_os: Optional[str] = None
    ip: Optional[str] = None
    port: Optional[str] = None


class ServerIdBody(BaseModel):
    id: int = Field(..., ge=1)


class ServerAddItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    server_os: str = Field(..., min_length=1, max_length=16)
    ip: str = Field(..., min_length=1, max_length=64)
    port: str = Field(default="4723", max_length=16)
    appium_version: str = Field(default="2.x", max_length=16)


class ServerAddBody(BaseModel):
    data_list: List[ServerAddItem] = Field(..., min_length=1)


class ServerUpdateBody(ServerIdBody):
    name: str = Field(..., min_length=1, max_length=255)
    server_os: str = Field(..., min_length=1, max_length=16)
    ip: str = Field(..., min_length=1, max_length=64)
    port: str = Field(default="4723", max_length=16)
    appium_version: str = Field(default="2.x", max_length=16)


class ServerSortBody(BaseModel):
    id_list: List[int] = Field(..., min_length=1)


class PhoneListBody(BaseModel):
    currentPage: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1, le=200)
    name: Optional[str] = None
    os: Optional[str] = None  
    phone_os: Optional[str] = None
    os_version: Optional[str] = None


class PhoneIdBody(BaseModel):
    id: int = Field(..., ge=1)


class PhoneAddItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone_os: str = Field(..., min_length=1, max_length=16)
    os_version: str = Field(default="", max_length=255)
    device_id: str = Field(..., min_length=1, max_length=255)
    screen: str = Field(default="", max_length=64)
    extends: Optional[Dict[str, Any]] = None


class PhoneAddBody(BaseModel):
    data_list: List[PhoneAddItem] = Field(..., min_length=1)


class PhoneUpdateBody(PhoneIdBody):
    name: str = Field(..., min_length=1, max_length=255)
    phone_os: str = Field(..., min_length=1, max_length=16)
    os_version: str = Field(default="", max_length=255)
    device_id: str = Field(..., min_length=1, max_length=255)
    screen: str = Field(default="", max_length=64)
    extends: Optional[Dict[str, Any]] = None


class PhoneSortBody(BaseModel):
    id_list: List[int] = Field(..., min_length=1)
