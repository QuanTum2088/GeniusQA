import request from '/@/utils/request';

const post = <T = any>(url: string, data?: object) =>
	request<T>({ url, method: 'post', data });

const base = '/v1/app_management/device';

/** APP 设备中心 API */
export function useAppManagementDeviceApi() {
	return {
		serverList: (data: object) => post(`${base}/server/list`, data),
		serverDetail: (data: { id: number }) => post(`${base}/server/detail`, data),
		serverAdd: (data: { data_list: object[] }) => post(`${base}/server/add`, data),
		serverUpdate: (data: object) => post(`${base}/server/update`, data),
		serverDelete: (data: { id: number }) => post(`${base}/server/delete`, data),
		serverCopy: (data: { id: number }) => post(`${base}/server/copy`, data),
		serverSort: (data: { id_list: number[] }) => post(`${base}/server/sort`, data),
		serverRun: (data: { id: number }) => post(`${base}/server/run`, data),

		phoneList: (data: object) => post(`${base}/phone/list`, data),
		phoneDetail: (data: { id: number }) => post(`${base}/phone/detail`, data),
		phoneAdd: (data: { data_list: object[] }) => post(`${base}/phone/add`, data),
		phoneUpdate: (data: object) => post(`${base}/phone/update`, data),
		phoneDelete: (data: { id: number }) => post(`${base}/phone/delete`, data),
		phoneCopy: (data: { id: number }) => post(`${base}/phone/copy`, data),
		phoneSort: (data: { id_list: number[] }) => post(`${base}/phone/sort`, data),
	};
}

export const appManagementDeviceApi = useAppManagementDeviceApi();
