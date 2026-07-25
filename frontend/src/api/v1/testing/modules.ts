/**
 * 模块管理API接口
 */
import request from '/@/utils/request';

/**
 * 模块管理 API
 */
export function useModuleApi() {
	return {
		getModuleList: (params: {
			project_id: number;
			page?: number;
			page_size?: number;
			name?: string;
			parent_id?: number;
			include_children?: boolean;
		}) =>
			request({
				url: '/v1/testcases/modules',
				method: 'GET',
				params,
			}),

		getModuleTree: (projectId: number) =>
			request({
				url: `/v1/testcases/modules/tree/${projectId}`,
				method: 'GET',
			}),

		getModuleDetail: (moduleId: number) =>
			request({
				url: `/v1/testcases/modules/${moduleId}`,
				method: 'GET',
			}),

		createModule: (data: {
			project_id: number;
			name: string;
			description?: string;
			parent_id?: number;
			sort_order?: number;
		}) =>
			request({
				url: '/v1/testcases/modules',
				method: 'POST',
				data,
			}),

		updateModule: (
			moduleId: number,
			data: {
				name?: string;
				description?: string;
				parent_id?: number;
				sort_order?: number;
			}
		) =>
			request({
				url: `/v1/testcases/modules/${moduleId}`,
				method: 'PUT',
				data,
			}),

		deleteModule: (moduleId: number) =>
			request({
				url: `/v1/testcases/modules/${moduleId}`,
				method: 'DELETE',
			}),

		moveModule: (moduleId: number, targetParentId?: number) =>
			request({
				url: `/v1/testcases/modules/${moduleId}/move`,
				method: 'PUT',
				params: {
					target_parent_id: targetParentId,
				},
			}),

		exportModules: (params: {
			project_id: number;
			module_ids?: number[];
			include_testcases?: boolean;
		}) =>
			request({
				url: '/v1/testcases/modules/export',
				method: 'POST',
				params,
			}),

		importModules: (data: {
			project_id: number;
			modules: any[];
			override?: boolean;
		}) =>
			request({
				url: '/v1/testcases/modules/import',
				method: 'POST',
				data,
			}),
	};
}

const moduleApi = useModuleApi();
export const getModuleList = moduleApi.getModuleList;
export const getModuleTree = moduleApi.getModuleTree;
export const getModuleDetail = moduleApi.getModuleDetail;
export const createModule = moduleApi.createModule;
export const updateModule = moduleApi.updateModule;
export const deleteModule = moduleApi.deleteModule;
export const moveModule = moduleApi.moveModule;
export const exportModules = moduleApi.exportModules;
export const importModules = moduleApi.importModules;
