import request from '/@/utils/request';

const postPrecisionTest = <T = any>(url: string, data?: any) => {
  return request<T>({
    url,
    method: 'post',
    data,
  });
};

export function usePrecisionTestApi() {
  return {
    repository_list: (data: { service_id: number; name?: string; page?: number; pageSize?: number }) =>
      postPrecisionTest('/v1/precision_test/repository/list', data),
    repository_save: (data: {
      id?: number;
      name: string;
      html_url: string;
      description?: string;
      service_id: number;
      service_host?: string;
      jacoco_port?: number;
      lang_type?: string;
    }) => postPrecisionTest('/v1/precision_test/repository/save', data),
    repository_delete: (data: { id: number }) =>
      postPrecisionTest('/v1/precision_test/repository/delete', data),


    coverage_report_list: (data: { service_id: number; name?: string; page?: number; pageSize?: number }) =>
      postPrecisionTest('/v1/precision_test/coverage/report/list', data),
    coverage_report_get: (data: { id: number }) =>
      postPrecisionTest('/v1/precision_test/coverage/report/get', data),
    coverage_report_delete: (data: { id: number }) =>
      postPrecisionTest('/v1/precision_test/coverage/report/delete', data),

    coverage_detail: (data: {
      report_id: number;
      el_type: 'report' | 'package' | 'class' | 'method';
      package_name?: string;
      class_id?: number;
    }) => postPrecisionTest('/v1/precision_test/coverage/detail', data),


    trigger_coverage: (data: {
      repo_id: number;
      new_branch: string;
      old_branch?: string;
      coverage_type: 10 | 20;
    }) => postPrecisionTest('/v1/precision_test/trigger_coverage', data),

    upload_xml: (formData: FormData) =>
      request({
        url: '/v1/precision_test/coverage/upload_xml',
        method: 'post',
        data: formData,
        headers: { 'Content-Type': 'multipart/form-data' },
      }),


    jacoco_dump: (data: {
      report_id: number;
      address?: string;
      port?: number;
      reset?: boolean;
    }) => postPrecisionTest('/v1/precision_test/coverage/jacoco_dump', data),
  };
}
