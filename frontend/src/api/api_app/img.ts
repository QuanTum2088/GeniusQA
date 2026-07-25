import axios from '@/utils/axios.ts';

enum API {
	IMG_LIST = '/api/v1/Ntesterc_app/img_list',
	IMG_SELECT = '/api/v1/Ntesterc_app/img_select',
	DELETE_IMG = '/api/v1/Ntesterc_app/delete_img',
	EDIT_IMG = '/api/v1/Ntesterc_app/edit_img',
}

export const img_list = (params: any) => axios.post(API.IMG_LIST, params);
export const img_select = (params: any) => axios.post(API.IMG_SELECT, params);
export const delete_img = (params: any) => axios.post(API.DELETE_IMG, params);
export const edit_img = (params: any) => axios.post(API.EDIT_IMG, params);

