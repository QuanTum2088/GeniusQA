/**
 * 数据工厂API接口
 */
import request from '/@/utils/request';

/**
 * 工具分类
 */
export interface ToolCategory {
	category: string;
	name: string;
	scenario: string;
	icon: string;
	tools: Tool[];
}

/**
 * 工具定义
 */
export interface Tool {
	name: string;
	display_name: string;
	description: string;
	scenario: string;
	icon: string;
}

/**
 * 工具执行结果
 */
export interface ToolExecuteResult {
	result: any;
	record_id?: number;
	created_at?: string;
}

/**
 * 工具使用记录
 */
export interface ToolRecord {
	id: number;
	tool_name: string;
	tool_category: string;
	tool_scenario: string;
	input_data: Record<string, any>;
	output_data: any;
	is_saved: boolean;
	tags: string[];
	creation_date: string;
	updation_date: string;
}

/**
 * 使用统计
 */
export interface Statistics {
	total_records: number;
	category_stats: Record<string, number>;
	scenario_stats: Record<string, number>;
	recent_tools: Array<{
		tool_name: string;
		tool_category_display: string;
		tool_scenario_display: string;
		created_at: string;
	}>;
}

/**
 * 批量生成结果
 */
export interface BatchGenerateResult {
	results: any[];
	count: number;
	tool_name: string;
	tool_category: string;
	success_count: number;
	failed_count: number;
}

/**
 * 数据工厂 API
 */
export function useDataFactoryApi() {
	return {
		getToolCategories: () =>
			request({
				url: '/v1/data-factory/categories',
				method: 'GET',
			}),

		executeTool: (data: {
			tool_name: string;
			tool_category: string;
			tool_scenario: string;
			input_data: Record<string, any>;
			is_saved?: boolean;
			tags?: string[];
		}) =>
			request({
				url: '/v1/data-factory/execute',
				method: 'POST',
				data,
			}),

		batchGenerate: (data: {
			tool_name: string;
			tool_category: string;
			tool_scenario: string;
			count: number;
			input_data: Record<string, any>;
			is_saved?: boolean;
			tags?: string[];
		}) =>
			request({
				url: '/v1/data-factory/batch-generate',
				method: 'POST',
				data,
			}),

		getRecordList: (params: {
			page?: number;
			page_size?: number;
			tool_category?: string;
			tool_name?: string;
		}) =>
			request({
				url: '/v1/data-factory/records',
				method: 'GET',
				params,
			}),

		getRecordDetail: (id: number) =>
			request({
				url: `/v1/data-factory/records/${id}`,
				method: 'GET',
			}),

		deleteRecord: (id: number) =>
			request({
				url: `/v1/data-factory/records/${id}`,
				method: 'DELETE',
			}),

		batchDeleteRecords: (ids: number[]) =>
			request({
				url: '/v1/data-factory/records/batch-delete',
				method: 'POST',
				data: { ids },
			}),

		getStatistics: () =>
			request({
				url: '/v1/data-factory/statistics',
				method: 'GET',
			}),

		getTagList: () =>
			request({
				url: '/v1/data-factory/tags',
				method: 'GET',
			}),
	};
}

const dataFactoryApi = useDataFactoryApi();
export const getToolCategories = dataFactoryApi.getToolCategories;
export const executeTool = dataFactoryApi.executeTool;
export const batchGenerate = dataFactoryApi.batchGenerate;
export const getRecordList = dataFactoryApi.getRecordList;
export const getRecordDetail = dataFactoryApi.getRecordDetail;
export const deleteRecord = dataFactoryApi.deleteRecord;
export const batchDeleteRecords = dataFactoryApi.batchDeleteRecords;
export const getStatistics = dataFactoryApi.getStatistics;
export const getTagList = dataFactoryApi.getTagList;
