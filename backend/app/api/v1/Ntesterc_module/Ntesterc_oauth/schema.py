#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from typing import Optional

from pydantic import BaseModel


class OAuthCallbackSchema(BaseModel):
    """OAuth 回调请求参数 (通用)"""
    code: str
    state: Optional[str] = None


class OAuthUserInfo(BaseModel):
    """OAuth 用户信息"""
    id: int
    username: str
    nickname: str
    email: Optional[str] = None
    avatar: Optional[str] = None
    user_type: int
    status: int


class OAuthLoginResponseSchema(BaseModel):
    """OAuth 登录响应"""
    access_token: str
    refresh_token: str
    expire: int
    user_info: OAuthUserInfo


class AuthorizeUrlResponse(BaseModel):
    """授权 URL 响应"""
    authorize_url: str
