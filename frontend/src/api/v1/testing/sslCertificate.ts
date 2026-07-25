/**
 * SSL证书管理API
 */
import request from '/@/utils/request';

export interface SSLCertificate {
  id?: number;
  project_id: number;
  name: string;
  cert_type: 'CA' | 'CLIENT';
  domain?: string;
  ca_cert?: string;
  client_cert?: string;
  client_key?: string;
  passphrase?: string;
  is_active: boolean;
  description?: string;
  creation_date?: string;
  updation_date?: string;
}

export interface SSLCertificateCreate {
  project_id: number;
  name: string;
  cert_type: 'CA' | 'CLIENT';
  domain?: string;
  ca_cert?: string;
  client_cert?: string;
  client_key?: string;
  passphrase?: string;
  is_active?: boolean;
  description?: string;
}

export interface SSLCertificateUpdate {
  name?: string;
  domain?: string;
  ca_cert?: string;
  client_cert?: string;
  client_key?: string;
  passphrase?: string;
  is_active?: boolean;
  description?: string;
}

export function useSslCertificateApi() {
  return {
    create(data: SSLCertificateCreate) {
      return request({
        url: '/v1/api_testing/ssl-certificates',
        method: 'post',
        data,
      });
    },
    list(params: { project_id: number; page?: number; page_size?: number }) {
      return request({
        url: '/v1/api_testing/ssl-certificates',
        method: 'get',
        params,
      });
    },
    get(id: number) {
      return request({
        url: `/v1/api_testing/ssl-certificates/${id}`,
        method: 'get',
      });
    },
    update(id: number, data: SSLCertificateUpdate) {
      return request({
        url: `/v1/api_testing/ssl-certificates/${id}`,
        method: 'put',
        data,
      });
    },
    delete(id: number) {
      return request({
        url: `/v1/api_testing/ssl-certificates/${id}`,
        method: 'delete',
      });
    },
    toggle(id: number) {
      return request({
        url: `/v1/api_testing/ssl-certificates/${id}/toggle`,
        method: 'put',
      });
    },
  };
}

export const sslCertificateApi = useSslCertificateApi();
