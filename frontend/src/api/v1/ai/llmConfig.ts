import request from '/@/utils/request'

/**
 * LLM 配置 API
 */
export function useLLMConfigApi() {
  return {

    getList: (params?: {
      provider?: string
      is_active?: boolean
    }) => {
      return request({
        url: '/v1/Ntesterc_ai/llm-config',
        method: 'GET',
        params
      })
    },


    getDefault: () => {
      return request({
        url: '/v1/Ntesterc_ai/llm-config/default',
        method: 'GET'
      })
    },


    getDetail: (id: number) => {
      return request({
        url: `/v1/Ntesterc_ai/llm-config/${id}`,
        method: 'GET'
      })
    },


    create: (data: LLMConfigCreateData) => {
      return request({
        url: '/v1/Ntesterc_ai/llm-config',
        method: 'POST',
        data
      })
    },


    update: (id: number, data: LLMConfigUpdateData) => {
      return request({
        url: `/v1/Ntesterc_ai/llm-config/${id}`,
        method: 'PUT',
        data
      })
    },


    delete: (id: number) => {
      return request({
        url: `/v1/Ntesterc_ai/llm-config/${id}`,
        method: 'DELETE'
      })
    },


    setDefault: (id: number) => {
      return request({
        url: `/v1/Ntesterc_ai/llm-config/${id}/set-default`,
        method: 'POST'
      })
    },


    test: (data: LLMConfigTestData) => {
      return request({
        url: '/v1/Ntesterc_ai/llm-config/test',
        method: 'POST',
        data
      })
    }
  }
}


export type LLMProvider = 'openai' | 'azure_openai' | 'anthropic' | 'ollama' | 'custom'


export interface LLMConfigData {
  id: number
  config_name: string
  name: string
  provider: LLMProvider
  model_name: string
  api_key: string
  base_url?: string
  system_prompt?: string
  temperature: number
  max_tokens: number
  supports_vision: boolean
  context_limit: number
  is_default: boolean
  is_active: boolean
  creation_date?: string
  created_by?: number
  updation_date?: string
  updated_by?: number
}


export interface LLMConfigCreateData {
  config_name: string
  name: string
  provider: LLMProvider
  model_name: string
  api_key: string
  base_url?: string
  system_prompt?: string
  temperature?: number
  max_tokens?: number
  supports_vision?: boolean
  context_limit?: number
  is_default?: boolean
  is_active?: boolean
}


export interface LLMConfigUpdateData {
  config_name?: string
  name?: string
  provider?: LLMProvider
  model_name?: string
  api_key?: string
  base_url?: string
  system_prompt?: string
  temperature?: number
  max_tokens?: number
  supports_vision?: boolean
  context_limit?: number
  is_default?: boolean
  is_active?: boolean
}


export interface LLMConfigTestData {
  config_id?: number
  config_name?: string
  name?: string
  provider?: LLMProvider
  api_key?: string
  base_url?: string
  test_message?: string
}


export interface LLMConfigTestResponse {
  success: boolean
  message: string
  response?: string
  error?: string
  latency?: number
}
