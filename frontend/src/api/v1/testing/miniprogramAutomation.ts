/**
 * 小程序自动化 API
 */
import request from '/@/utils/request';

const post = <T = any>(url: string, data?: any) =>
  request<T>({ url, method: 'post', data });

export function useMiniAutomationApi() {
  return {
    // 元数据
    get_frameworks: () => request({ url: '/v1/Ntesterc_mini/frameworks', method: 'get' }),
    get_platforms:  () => request({ url: '/v1/Ntesterc_mini/platforms',  method: 'get' }),
    // 菜单
    get_menu:    (data: any) => post('/v1/Ntesterc_mini/menu', data),
    add_menu:    (data: any) => post('/v1/Ntesterc_mini/add_menu', data),
    rename_menu: (data: any) => post('/v1/Ntesterc_mini/rename_menu', data),
    del_menu:    (data: any) => post('/v1/Ntesterc_mini/del_menu', data),
    copy_script: (data: any) => post('/v1/Ntesterc_mini/copy_script', data),
    // 脚本
    get_script:  (data: any) => post('/v1/Ntesterc_mini/get_script', data),
    save_script: (data: any) => post('/v1/Ntesterc_mini/save_script', data),
    // 执行
    run_script:  (data: any) => post('/v1/Ntesterc_mini/run_script', data),
    stop_script: (data: any) => post('/v1/Ntesterc_mini/stop_script', data),
    run_status:  (data: any) => post('/v1/Ntesterc_mini/run_status', data),
    // 结果
    result_list:   (data: any) => post('/v1/Ntesterc_mini/result_list', data),
    result_detail: (data: any) => post('/v1/Ntesterc_mini/result_detail', data),
    del_result:    (data: any) => post('/v1/Ntesterc_mini/del_result', data),
  };
}

export const miniAutomationApi = useMiniAutomationApi();
