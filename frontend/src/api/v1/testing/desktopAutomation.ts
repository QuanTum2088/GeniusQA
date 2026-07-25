/**
 * 客户端UI自动化 API
 */
import request from '/@/utils/request';

const post = <T = any>(url: string, data?: any) =>
  request<T>({ url, method: 'post', data });

export function useDesktopAutomationApi() {
  return {
    // 元数据
    get_frameworks: () => request({ url: '/v1/desktop_automation/frameworks', method: 'get' }),
    // 菜单
    get_menu:    (data: any) => post('/v1/desktop_automation/menu', data),
    add_menu:    (data: any) => post('/v1/desktop_automation/add_menu', data),
    rename_menu: (data: any) => post('/v1/desktop_automation/rename_menu', data),
    del_menu:    (data: any) => post('/v1/desktop_automation/del_menu', data),
    copy_script: (data: any) => post('/v1/desktop_automation/copy_script', data),
    // 脚本
    get_script:  (data: any) => post('/v1/desktop_automation/get_script', data),
    save_script: (data: any) => post('/v1/desktop_automation/save_script', data),
    // 执行
    run_script:  (data: any) => post('/v1/desktop_automation/run_script', data),
    stop_script: (data: any) => post('/v1/desktop_automation/stop_script', data),
    run_status:  (data: any) => post('/v1/desktop_automation/run_status', data),
    // 结果
    result_list:   (data: any) => post('/v1/desktop_automation/result_list', data),
    result_detail: (data: any) => post('/v1/desktop_automation/result_detail', data),
    del_result:    (data: any) => post('/v1/desktop_automation/del_result', data),
  };
}

export const desktopAutomationApi = useDesktopAutomationApi();
