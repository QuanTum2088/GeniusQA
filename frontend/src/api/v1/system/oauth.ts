import request from '/@/utils/request';

/**
 * OAuth 第三方登录 API
 */

// OAuth 提供商类型
export type OAuthProvider = 'gitee' | 'github' | 'qq' | 'google' | 'wechat' | 'microsoft' | 'dingtalk' | 'feishu';

// OAuth 用户信息
export interface OAuthUserInfo {
  id: number;
  username: string;
  nickname: string;
  email?: string;
  avatar?: string;
  user_type: number;
  status: number;
}

// OAuth 登录响应
export interface OAuthLoginResponse {
  access_token: string;
  refresh_token: string;
  expire: number;
  user_info: OAuthUserInfo;
}

// 授权 URL 响应
export interface AuthorizeUrlResponse {
  authorize_url: string;
}

/**
 * OAuth API
 */
export function useOAuthApi() {
  return {
    /**
     * 获取支持的 OAuth 提供商列表
     */
    getProviders: () => {
      return request({
        url: '/v1/oauth/providers',
        method: 'GET',
      });
    },

    /**
     * 获取 OAuth 授权 URL
     * @param provider OAuth 提供商
     * @param state 状态参数（可选，用于防止 CSRF 攻击）
     */
    getAuthorizeUrl: (provider: OAuthProvider, state?: string) => {
      return request({
        url: `/v1/oauth/${provider}/authorize`,
        method: 'GET',
        params: state ? { state } : undefined,
      });
    },

    /**
     * OAuth 回调处理
     * @param provider OAuth 提供商
     * @param code 授权码
     * @param state 状态参数（可选）
     */
    callback: (provider: OAuthProvider, code: string, state?: string) => {
      return request({
        url: `/v1/oauth/${provider}/callback`,
        method: 'POST',
        data: {
          code,
          state,
        },
      });
    },
  };
}
