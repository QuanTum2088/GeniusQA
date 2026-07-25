/**
 *抓包模块接口
 */
import request from '/@/utils/request';

export function useMitmproxyApi() {
  return {
    mitmproxy_start: (data: any) =>
      request({ url: '/v1/mitmproxy/mitmproxy_start', method: 'post', data }),
    mitmproxy_single_start: (data: any) =>
      request({ url: '/v1/mitmproxy/mitmproxy_single_start', method: 'post', data }),
    mitmproxy_check: (data: any) =>
      request({ url: '/v1/mitmproxy/mitmproxy_check', method: 'post', data }),
    mitmproxy_stop: (data: any) =>
      request({ url: '/v1/mitmproxy/mitmproxy_stop', method: 'post', data }),
    mitmproxy_close_agent: (data: any) =>
      request({ url: '/v1/mitmproxy/mitmproxy_close_agent', method: 'post', data }),
    mitmproxy_run_log: (data: any) =>
      request({ url: '/v1/mitmproxy/mitmproxy_run_log', method: 'post', data }),
    mitmproxy_write_api: (data: any) =>
      request({ url: '/v1/mitmproxy/mitmproxy_write_api', method: 'post', data }),
    single_write: (data: any) =>
      request({ url: '/v1/mitmproxy/single_write', method: 'post', data }),
  };
}

export const mitmproxyApi = useMitmproxyApi();

export const {
  mitmproxy_start,
  mitmproxy_single_start,
  mitmproxy_check,
  mitmproxy_stop,
  mitmproxy_close_agent,
  mitmproxy_run_log,
  mitmproxy_write_api,
  single_write,
} = mitmproxyApi;
