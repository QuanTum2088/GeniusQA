/**
 * 小程序自动化 API
 */
import request from '/@/utils/request';

const post = <T = any>(url: string, data?: any) =>
  request<T>({ url, method: 'post', data });

export function useMiniAutomationApi() {
  return {
    // 元数据
    get_frameworks: () => request({ url: '/v1/miniprogram_automation/frameworks', method: 'get' }),
    get_platforms:  () => request({ url: '/v1/miniprogram_automation/platforms',  method: 'get' }),
    // 菜单
    get_menu:    (data: any) => post('/v1/miniprogram_automation/menu', data),
    add_menu:    (data: any) => post('/v1/miniprogram_automation/add_menu', data),
    rename_menu: (data: any) => post('/v1/miniprogram_automation/rename_menu', data),
    del_menu:    (data: any) => post('/v1/miniprogram_automation/del_menu', data),
    copy_script: (data: any) => post('/v1/miniprogram_automation/copy_script', data),
    // 脚本
    get_script:  (data: any) => post('/v1/miniprogram_automation/get_script', data),
    save_script: (data: any) => post('/v1/miniprogram_automation/save_script', data),
    // 执行
    run_script:  (data: any) => post('/v1/miniprogram_automation/run_script', data),
    stop_script: (data: any) => post('/v1/miniprogram_automation/stop_script', data),
    run_status:  (data: any) => post('/v1/miniprogram_automation/run_status', data),
    // 结果
    result_list:   (data: any) => post('/v1/miniprogram_automation/result_list', data),
    result_detail: (data: any) => post('/v1/miniprogram_automation/result_detail', data),
    del_result:    (data: any) => post('/v1/miniprogram_automation/del_result', data),
  };
}

export const miniAutomationApi = useMiniAutomationApi();
