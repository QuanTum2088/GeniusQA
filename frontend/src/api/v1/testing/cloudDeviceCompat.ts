import request from '/@/utils/request';

/** 云设备 */
export function useCloudDeviceCompatApi() {
  return {
    get_device_list: (data: any) =>
      request({ url: '/v1/cloud_device/device_list', method: 'post', data }),
    devices_install: (data: any) =>
      request({ url: '/v1/cloud_device/device_install', method: 'post', data }),
    devices_uninstall: (data: any) =>
      request({ url: '/v1/cloud_device/device_uninstall', method: 'post', data }),
    device_info_list: (data: any) =>
      request({ url: '/v1/cloud_device/device_info_list', method: 'post', data }),
    use_device: (data: any) =>
      request({ url: '/v1/cloud_device/use_device', method: 'post', data }),
    stop_device: (data: any) =>
      request({ url: '/v1/cloud_device/stop_device', method: 'post', data }),
    get_device_log: (data: any) =>
      request({ url: '/v1/cloud_device/get_device_log', method: 'post', data }),
    get_history_list: (data: any) =>
      request({ url: '/v1/cloud_device/get_history_list', method: 'post', data }),
    device_install_app: (data: any) =>
      request({ url: '/v1/cloud_device/device_install_app', method: 'post', data }),
    direct_install_app: (data: any) =>
      request({ url: '/v1/cloud_device/direct_install_app', method: 'post', data }),
    app_view_device: (data: any) =>
      request({ url: '/v1/cloud_device/app_view_device', method: 'post', data }),
    add_device: (data: any) =>
      request({ url: '/v1/cloud_device/add_device', method: 'post', data }),
    device_performance: (data: any) =>
      request({ url: '/v1/cloud_device/device_performance', method: 'post', data }),
  };
}

export const cloudDeviceCompatApi = useCloudDeviceCompatApi();

export const {
  get_device_list,
  devices_install,
  devices_uninstall,
  device_info_list,
  use_device,
  stop_device,
  get_device_log,
  get_history_list,
  device_install_app,
  direct_install_app,
  app_view_device,
  add_device,
  device_performance,
} = cloudDeviceCompatApi;
