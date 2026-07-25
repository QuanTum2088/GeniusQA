#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

import logging
from typing import Dict, Type

from app.core.oauth.base_oauth_service import BaseOAuthService
from app.core.oauth.providers import (
    GiteeOAuthService,
    GitHubOAuthService,
    QQOAuthService,
    GoogleOAuthService,
    WeChatOAuthService,
    MicrosoftOAuthService,
    DingTalkOAuthService,
    FeishuOAuthService,
)

logger = logging.getLogger(__name__)

# OAuth 提供商映射
OAUTH_PROVIDERS: Dict[str, Type[BaseOAuthService]] = {
    'gitee': GiteeOAuthService,
    'github': GitHubOAuthService,
    'qq': QQOAuthService,
    'google': GoogleOAuthService,
    'wechat': WeChatOAuthService,
    'microsoft': MicrosoftOAuthService,
    'dingtalk': DingTalkOAuthService,
    'feishu': FeishuOAuthService,
}


class OAuthService:
    """OAuth 服务类"""

    @staticmethod
    def get_provider_service(provider: str) -> Type[BaseOAuthService]:
        """
        获取 OAuth 提供商服务类
        
        Args:
            provider: 提供商名称
        
        Returns:
            Type[BaseOAuthService]: 提供商服务类
        
        Raises:
            ValueError: 不支持的提供商
        """
        if provider not in OAUTH_PROVIDERS:
            raise ValueError(f"不支持的 OAuth 提供商: {provider}")
        
        return OAUTH_PROVIDERS[provider]

    @staticmethod
    def get_supported_providers() -> list:
        """
        获取支持的 OAuth 提供商列表
        
        Returns:
            list: 提供商名称列表
        """
        return list(OAUTH_PROVIDERS.keys())
