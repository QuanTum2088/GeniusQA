/**
 * 客户端UI自动化 API
 */
import request from '/@/utils/request';

const post = <T = any>(url: string, data?: any) =>
  request<T>({ url, method: 'post', data });

export function useDesktopAutomationApi() {
  return {
    // 元数据
    get_frameworks: () => request({ url: '/v1/Ntesterc_desk/frameworks', method: 'get' }),
    // 菜单
    get_menu:    (data: any) => post('/v1/Ntesterc_desk/menu', data),
    add_menu:    (data: any) => post('/v1/Ntesterc_desk/add_menu', data),
    rename_menu: (data: any) => post('/v1/Ntesterc_desk/rename_menu', data),
    del_menu:    (data: any) => post('/v1/Ntesterc_desk/del_menu', data),
    copy_script: (data: any) => post('/v1/Ntesterc_desk/copy_script', data),
    // 脚本
    get_script:  (data: any) => post('/v1/Ntesterc_desk/get_script', data),
    save_script: (data: any) => post('/v1/Ntesterc_desk/save_script', data),
    // 执行
    run_script:  (data: any) => post('/v1/Ntesterc_desk/run_script', data),
    stop_script: (data: any) => post('/v1/Ntesterc_desk/stop_script', data),
    run_status:  (data: any) => post('/v1/Ntesterc_desk/run_status', data),
    // 结果
    result_list:   (data: any) => post('/v1/Ntesterc_desk/result_list', data),
    result_detail: (data: any) => post('/v1/Ntesterc_desk/result_detail', data),
    del_result:    (data: any) => post('/v1/Ntesterc_desk/del_result', data),
  };
}

export const desktopAutomationApi = useDesktopAutomationApi();
