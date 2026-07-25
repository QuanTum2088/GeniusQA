/**
 * AI助手模块API接口
 */
import request from '/@/utils/request';

/**
 * 助手类型
 */
export type AssistantType = 'chatbot' | 'workflow' | 'agent';

/**
 * 消息角色
 */
export type MessageRole = 'user' | 'assistant';

/**
 * AI助手配置
 */
export interface AssistantConfig {
	id: number;
	name: string;
	dify_api_key: string;
	dify_base_url: string;
	assistant_type: AssistantType;
	is_active: boolean;
	created_by: number;
	creation_date: string;
	updation_date: string;
}

/**
 * 对话
 */
export interface Conversation {
	id: number;
	user_id: number;
	assistant_config_id: number;
	conversation_id?: string;
	title?: string;
	creation_date: string;
	updation_date: string;
	assistant_config?: AssistantConfig;
	message_count?: number;
	last_message?: string;
	last_message_time?: string;
}

/**
 * 消息
 */
export interface Message {
	id: number;
	conversation_id: number;
	role: MessageRole;
	content: string;
	created_at: string;
}

/**
 * 聊天响应
 */
export interface ChatResponse {
	message: string;
	conversation_id?: string;
	message_id?: string;
}

/**
 * 助手统计
 */
export interface AssistantStatistics {
	total_configs: number;
	active_configs: number;
	total_conversations: number;
	total_messages: number;
	type_distribution: Record<string, number>;
	config_type_distribution: Record<string, number>;
	daily_message_count: Array<{ date: string; count: number }>;
	config_stats: Array<any>;
	recent_conversations: Conversation[];
	usage_stats: {
		today: number;
		this_week: number;
		this_month: number;
	};
}

/**
 * AI助手 API
 */
export function useAssistantApi() {
	return {
		getConfigList: (params: {
			page?: number;
			page_size?: number;
		}) =>
			request({
				url: '/v1/Ntesterc_assistant/configs',
				method: 'GET',
				params,
			}),

		getConfigDetail: (id: number) =>
			request({
				url: `/v1/Ntesterc_assistant/configs/${id}`,
				method: 'GET',
			}),

		createConfig: (data: {
			name: string;
			dify_api_key: string;
			dify_base_url: string;
			assistant_type?: string;
		}) =>
			request({
				url: '/v1/Ntesterc_assistant/configs',
				method: 'POST',
				data,
			}),

		updateConfig: (
			id: number,
			data: {
				name?: string;
				dify_api_key?: string;
				dify_base_url?: string;
				assistant_type?: string;
				is_active?: boolean;
			}
		) =>
			request({
				url: `/v1/Ntesterc_assistant/configs/${id}`,
				method: 'PUT',
				data,
			}),

		deleteConfig: (id: number) =>
			request({
				url: `/v1/Ntesterc_assistant/configs/${id}`,
				method: 'DELETE',
			}),

		getConversationList: (params: {
			page?: number;
			page_size?: number;
			assistant_config_id?: number;
		}) =>
			request({
				url: '/v1/Ntesterc_assistant/conversations',
				method: 'GET',
				params,
			}),

		getConversationDetail: (id: number) =>
			request({
				url: `/v1/Ntesterc_assistant/conversations/${id}`,
				method: 'GET',
			}),

		createConversation: (data: {
			assistant_config_id: number;
			title?: string;
		}) =>
			request({
				url: '/v1/Ntesterc_assistant/conversations',
				method: 'POST',
				data,
			}),

		updateConversation: (
			id: number,
			data: {
				title?: string;
			}
		) =>
			request({
				url: `/v1/Ntesterc_assistant/conversations/${id}`,
				method: 'PUT',
				data,
			}),

		deleteConversation: (id: number) =>
			request({
				url: `/v1/Ntesterc_assistant/conversations/${id}`,
				method: 'DELETE',
			}),

		getMessageList: (
			conversationId: number,
			params?: {
				page?: number;
				page_size?: number;
			}
		) =>
			request({
				url: `/v1/Ntesterc_assistant/conversations/${conversationId}/messages`,
				method: 'GET',
				params,
			}),

		getConversationMessages: (
			conversationId: number,
			params?: {
				page?: number;
				page_size?: number;
			}
		) =>
			request({
				url: `/v1/Ntesterc_assistant/conversations/${conversationId}/messages`,
				method: 'GET',
				params,
			}),

		sendMessage: (
			conversationId: number,
			data: {
				content: string;
			}
		) =>
			request({
				url: `/v1/Ntesterc_assistant/conversations/${conversationId}/messages`,
				method: 'POST',
				data,
			}),

		chatWithDify: (data: {
			assistant_config_id: number;
			conversation_id?: number;
			message: string;
			user_id?: number;
		}) =>
			request({
				url: '/v1/Ntesterc_assistant/chat',
				method: 'POST',
				data,
			}),

		getStatistics: () =>
			request({
				url: '/v1/Ntesterc_assistant/statistics',
				method: 'GET',
			}),
	};
}

const assistantApi = useAssistantApi();
export const getConfigList = assistantApi.getConfigList;
export const getConfigDetail = assistantApi.getConfigDetail;
export const createConfig = assistantApi.createConfig;
export const updateConfig = assistantApi.updateConfig;
export const deleteConfig = assistantApi.deleteConfig;
export const getConversationList = assistantApi.getConversationList;
export const getConversationDetail = assistantApi.getConversationDetail;
export const createConversation = assistantApi.createConversation;
export const updateConversation = assistantApi.updateConversation;
export const deleteConversation = assistantApi.deleteConversation;
export const getMessageList = assistantApi.getMessageList;
export const getConversationMessages = assistantApi.getConversationMessages;
export const sendMessage = assistantApi.sendMessage;
export const chatWithDify = assistantApi.chatWithDify;
export const getStatistics = assistantApi.getStatistics;
