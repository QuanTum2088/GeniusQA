
import request from '/@/utils/request';

const postAppManagement = <T = any>(url: string, data?: any) =>
  request<T>({
    url,
    method: 'post',
    data,
  });

export function useAppManagementApi() {
  return {
    app_menu: (data: any) => postAppManagement('/v1/app_management/app_menu', data),
    get_app_script: (data: any) => postAppManagement('/v1/app_management/get_app_script', data),
    save_app_script: (data: any) => postAppManagement('/v1/app_management/save_app_script', data),
    run_app_script: (data: any) => postAppManagement('/v1/app_management/run_app_script', data),
    run_script_list: (data: any) => postAppManagement('/v1/app_management/run_script_list', data),
    add_menu: (data: any) => postAppManagement('/v1/app_management/add_menu', data),
    del_menu: (data: any) => postAppManagement('/v1/app_management/del_menu', data),
    rename_menu: (data: any) => postAppManagement('/v1/app_management/rename_menu', data),
    pid_status: (data: any) => postAppManagement('/v1/app_management/pid_status', data),
    stop_process: (data: any) => postAppManagement('/v1/app_management/stop_process', data),
    get_app_result: (data: any) => postAppManagement('/v1/app_management/get_app_result', data),
    app_result_list: (data: any) => postAppManagement('/v1/app_management/app_result_list', data),
    get_script_list: (data: any) => postAppManagement('/v1/app_management/menu_script_list', data),
    run_scripts: (data: any) => postAppManagement('/v1/app_management/run_script_list', data),
    app_result: (data: any) => postAppManagement('/v1/app_management/get_app_result', data),
    app_result_detail: (data: any) => postAppManagement('/v1/app_management/get_result_detail', data),
    get_process: (data: any) => postAppManagement('/v1/app_management/get_process', data),
    get_app_result_detail: (data: any) => postAppManagement('/v1/app_management/get_app_result_detail', data),
    get_result_list: (data: any) => postAppManagement('/v1/app_management/app_result_list', data),
    get_result_log: (data: any) => postAppManagement('/v1/app_management/get_result_list', data),
    view_script_list: (data: any) => postAppManagement('/v1/app_management/view_script_list', data),
    app_correction: (data: any) => postAppManagement('/v1/app_management/app_correction', data),
    app_menu_select: (data: any) => postAppManagement('/v1/app_management/app_menu_select', data),
    send_app_warn: (data: any) => postAppManagement('/v1/app_management/send_app_warn', data),
    del_app_result: (data: { result_id: string }) =>
      postAppManagement('/v1/app_management/del_app_result', data),

    /** APP 页面管理 */
    pageList: (data: object) => postAppManagement('/v1/app_management/page/list', data),
    pageAdd: (data: object) => postAppManagement('/v1/app_management/page/add', data),
    pageUpdate: (data: object) => postAppManagement('/v1/app_management/page/update', data),
    pageDelete: (data: { id: number }) => postAppManagement('/v1/app_management/page/delete', data),
    pageSort: (data: { id_list: number[] }) => postAppManagement('/v1/app_management/page/sort', data),
    pageCopy: (data: { id: number }) => postAppManagement('/v1/app_management/page/copy', data),
    pageElementList: (data: { page_id: number }) =>
      postAppManagement('/v1/app_management/page/element/list', data),
    pageElementAdd: (data: object) => postAppManagement('/v1/app_management/page/element/add', data),
    pageElementUpdate: (data: object) => postAppManagement('/v1/app_management/page/element/update', data),
    pageElementDelete: (data: { id: number }) =>
      postAppManagement('/v1/app_management/page/element/delete', data),
    pageElementSort: (data: { id_list: number[] }) =>
      postAppManagement('/v1/app_management/page/element/sort', data),
    pageElementImport: (data: { page_id: number; elements: object[] }) =>
      postAppManagement('/v1/app_management/page/element/import', data),
  };
}

export const appManagementApi = useAppManagementApi();
export const {
  app_menu,
  get_app_script,
  save_app_script,
  run_app_script,
  run_script_list,
  add_menu,
  del_menu,
  rename_menu,
  pid_status,
  stop_process,
  get_app_result,
  app_result_list,
  get_script_list,
  run_scripts,
  app_result,
  app_result_detail,
  get_process,
  get_app_result_detail,
  get_result_list,
  get_result_log,
  view_script_list,
  app_correction,
  app_menu_select,
  send_app_warn,
  del_app_result,
} = appManagementApi;

