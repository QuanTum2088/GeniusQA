/**
 * 前置/后置操作相关API
 */
import request from '/@/utils/request';

/**
 * 前置/后置操作 API
 */
export function useOperationsApi() {
	return {
		getPublicScripts: (params: {
			project_id: number;
			page?: number;
			page_size?: number;
		}) =>
			request({
				url: '/v1/Ntesterc_api_testing/public-scripts',
				method: 'GET',
				params,
			}),

		createPublicScript: (data: {
			project_id: number;
			name: string;
			description?: string;
			script_type?: string;
			script_content: string;
			category?: string;
			is_active?: boolean;
		}) =>
			request({
				url: '/v1/Ntesterc_api_testing/public-scripts',
				method: 'POST',
				data,
			}),

		updatePublicScript: (id: number, data: any) =>
			request({
				url: `/v1/Ntesterc_api_testing/public-scripts/${id}`,
				method: 'PUT',
				data,
			}),

		deletePublicScript: (id: number) =>
			request({
				url: `/v1/Ntesterc_api_testing/public-scripts/${id}`,
				method: 'DELETE',
			}),

		getPublicScriptDetail: (id: number) =>
			request({
				url: `/v1/Ntesterc_api_testing/public-scripts/${id}`,
				method: 'GET',
			}),

		getDatabaseConfigs: (params: {
			project_id: number;
			page?: number;
			page_size?: number;
		}) =>
			request({
				url: '/v1/Ntesterc_api_testing/database-configs',
				method: 'GET',
				params,
			}),

		createDatabaseConfig: (data: {
			project_id: number;
			name: string;
			description?: string;
			db_type: string;
			host: string;
			port: number;
			database_name?: string;
			username?: string;
			password?: string;
			connection_params?: any;
			is_active?: boolean;
		}) =>
			request({
				url: '/v1/Ntesterc_api_testing/database-configs',
				method: 'POST',
				data,
			}),

		updateDatabaseConfig: (id: number, data: any) =>
			request({
				url: `/v1/Ntesterc_api_testing/database-configs/${id}`,
				method: 'PUT',
				data,
			}),

		deleteDatabaseConfig: (id: number) =>
			request({
				url: `/v1/Ntesterc_api_testing/database-configs/${id}`,
				method: 'DELETE',
			}),

		getDatabaseConfigDetail: (id: number) =>
			request({
				url: `/v1/Ntesterc_api_testing/database-configs/${id}`,
				method: 'GET',
			}),

		testDatabaseConnection: (id: number) =>
			request({
				url: `/v1/Ntesterc_api_testing/database-configs/${id}/test`,
				method: 'POST',
			}),
	};
}

const operationsApi = useOperationsApi();
export const getPublicScripts = operationsApi.getPublicScripts;
export const createPublicScript = operationsApi.createPublicScript;
export const updatePublicScript = operationsApi.updatePublicScript;
export const deletePublicScript = operationsApi.deletePublicScript;
export const getPublicScriptDetail = operationsApi.getPublicScriptDetail;
export const getDatabaseConfigs = operationsApi.getDatabaseConfigs;
export const createDatabaseConfig = operationsApi.createDatabaseConfig;
export const updateDatabaseConfig = operationsApi.updateDatabaseConfig;
export const deleteDatabaseConfig = operationsApi.deleteDatabaseConfig;
export const getDatabaseConfigDetail = operationsApi.getDatabaseConfigDetail;
export const testDatabaseConnection = operationsApi.testDatabaseConnection;
