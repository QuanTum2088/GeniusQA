#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

import logging

from fastapi import APIRouter, HTTPException, Request

from app.api.v1.Ntesterc_module.Ntesterc_oauth.schema import (
    OAuthCallbackSchema,
    OAuthLoginResponseSchema,
    AuthorizeUrlResponse,
    OAuthUserInfo,
)
from app.api.v1.Ntesterc_module.Ntesterc_oauth.service import OAuthService
from app.common.response import success_response

logger = logging.getLogger(__name__)

router = APIRouter(tags=["OAuth 第三方登录"])


@router.get("/{provider}/authorize", summary="获取 OAuth 授权 URL")
async def get_oauth_authorize_url(provider: str, state: str = None):
    """
    获取 OAuth 授权 URL (通用接口)
    
    Args:
        provider: OAuth 提供商 (gitee/github/qq/google/wechat/microsoft/dingtalk/feishu)
        state: 状态参数（可选，用于防止 CSRF 攻击）
    
    前端应该将用户重定向到此 URL
    """
    try:
        # 获取提供商服务
        service_class = OAuthService.get_provider_service(provider)
        
        # 获取授权 URL
        authorize_url = service_class.get_authorize_url(state)
        
        # 使用统一响应格式包装
        return success_response(data={"authorize_url": authorize_url})
    
    except ValueError as e:
        logger.warning(f"获取 {provider} 授权 URL 失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取 {provider} 授权 URL 异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取授权 URL 失败: {str(e)}")


@router.post("/{provider}/callback", summary="OAuth 回调处理")
async def oauth_callback(
    request: Request,
    provider: str,
    data: OAuthCallbackSchema
):
    """
    处理 OAuth 回调 (通用接口)
    
    Args:
        provider: OAuth 提供商 (gitee/github/qq/google/wechat/microsoft/dingtalk/feishu)
        data: 回调数据（包含 code 和 state）
    
    前端在授权后会获得 code，将 code 发送到此接口完成登录
    """
    try:
        # 获取提供商服务
        service_class = OAuthService.get_provider_service(provider)
        
        # 获取客户端 IP 和 User-Agent
        ip_address = request.client.host
        user_agent = request.headers.get('user-agent', '')
        
        # 处理 OAuth 登录
        user, access_token, refresh_token, expire_time = await service_class.handle_oauth_login(
            code=data.code,
            ip_address=ip_address,
            user_agent=user_agent,
            login_type=provider
        )
        
        # 构造返回数据
        user_info = {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "avatar": user.avatar,
            "user_type": user.user_type,
            "status": user.status,
        }
        
        logger.info(f"{provider.capitalize()} OAuth 登录成功: {user.username}")
        
        # 使用统一响应格式包装
        return success_response(data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expire": expire_time,
            "user_info": user_info,
        })
    
    except ValueError as e:
        logger.warning(f"{provider.capitalize()} OAuth 登录失败: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"{provider.capitalize()} OAuth 登录异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="登录失败，请稍后重试")


@router.get("/providers", summary="获取支持的 OAuth 提供商列表")
async def get_oauth_providers():
    """
    获取支持的 OAuth 提供商列表
    
    Returns:
        list: 提供商名称列表
    """
    providers = OAuthService.get_supported_providers()
    return success_response(data=providers)
