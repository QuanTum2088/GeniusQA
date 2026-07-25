/**
 * 测试用例管理API
 */
import request from '/@/utils/request';

/**
 * 测试用例 API
 */
export function useTestcaseApi() {
	return {
		createTestCase: (projectId: number, data: any) =>
			request({
				url: `/v1/Ntesterc_testcases?project_id=${projectId}`,
				method: 'POST',
				data,
			}),

		getTestCaseList: (params: any) =>
			request({
				url: '/v1/Ntesterc_testcases',
				method: 'GET',
				params,
			}),

		getTestCaseDetail: (id: number) =>
			request({
				url: `/v1/Ntesterc_testcases/${id}`,
				method: 'GET',
			}),

		updateTestCase: (id: number, data: any) =>
			request({
				url: `/v1/Ntesterc_testcases/${id}`,
				method: 'PUT',
				data,
			}),

		deleteTestCase: (id: number) =>
			request({
				url: `/v1/Ntesterc_testcases/${id}`,
				method: 'DELETE',
			}),

		createVersion: (data: any) =>
			request({
				url: '/v1/Ntesterc_testcases/versions',
				method: 'POST',
				data,
			}),

		getVersionList: (params: any) =>
			request({
				url: '/v1/Ntesterc_testcases/versions',
				method: 'GET',
				params,
			}),

		getVersionDetail: (id: number) =>
			request({
				url: `/v1/Ntesterc_testcases/versions/${id}`,
				method: 'GET',
			}),

		updateVersion: (id: number, data: any) =>
			request({
				url: `/v1/Ntesterc_testcases/versions/${id}`,
				method: 'PUT',
				data,
			}),

		deleteVersion: (id: number) =>
			request({
				url: `/v1/Ntesterc_testcases/versions/${id}`,
				method: 'DELETE',
			}),

		associateTestCases: (data: any) =>
			request({
				url: '/v1/Ntesterc_testcases/versions/associate',
				method: 'POST',
				data,
			}),

		importTestCasesFromExcel: (file: File, project_id: number, module_id?: number) => {
			const formData = new FormData();
			formData.append('file', file);
			formData.append('project_id', project_id.toString());
			if (module_id) {
				formData.append('module_id', module_id.toString());
			}
			return request({
				url: '/v1/Ntesterc_testcases/import-from-excel',
				method: 'POST',
				data: formData,
				headers: { 'Content-Type': 'multipart/form-data' },
			});
		},

		exportTestCasesToExcel: (params: any) =>
			request({
				url: '/v1/Ntesterc_testcases/export-to-excel',
				method: 'GET',
				params,
				responseType: 'blob',
			}),
	};
}

const testcaseApi = useTestcaseApi();
export const createTestCase = testcaseApi.createTestCase;
export const getTestCaseList = testcaseApi.getTestCaseList;
export const getTestCaseDetail = testcaseApi.getTestCaseDetail;
export const updateTestCase = testcaseApi.updateTestCase;
export const deleteTestCase = testcaseApi.deleteTestCase;
export const createVersion = testcaseApi.createVersion;
export const getVersionList = testcaseApi.getVersionList;
export const getVersionDetail = testcaseApi.getVersionDetail;
export const updateVersion = testcaseApi.updateVersion;
export const deleteVersion = testcaseApi.deleteVersion;
export const associateTestCases = testcaseApi.associateTestCases;
export const importTestCasesFromExcel = testcaseApi.importTestCasesFromExcel;
export const exportTestCasesToExcel = testcaseApi.exportTestCasesToExcel;
