import request from '/@/utils/request';

export function useProjectPlatformApi() {
  return {
    mcp: {
      list: (projectId: number, params?: Record<string, any>) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/mcp-configs`, method: 'get', params }),
      create: (projectId: number, data: any) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/mcp-configs`, method: 'post', data }),
      update: (projectId: number, id: number, data: any) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/mcp-configs/${id}`, method: 'put', data }),
      remove: (projectId: number, id: number) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/mcp-configs/${id}`, method: 'delete' }),
      test: (projectId: number, id: number) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/mcp-configs/${id}/test`, method: 'post' }),
      tools: (projectId: number, id: number) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/mcp-configs/${id}/tools`, method: 'get' }),
      call: (
        projectId: number,
        id: number,
        data: { name: string; arguments?: Record<string, any> },
      ) =>
        request({
          url: `/v1/Ntesterc_project/${projectId}/mcp-configs/${id}/call`,
          method: 'post',
          data,
        }),
      importFromFile: (projectId: number, data?: { path?: string; scope?: string }) =>
        request({
          url: `/v1/Ntesterc_project/${projectId}/mcp-configs/import`,
          method: 'post',
          data: data || {},
        }),
      syncFiles: (projectId: number) =>
        request({
          url: `/v1/Ntesterc_project/${projectId}/mcp-configs/sync-files`,
          method: 'post',
        }),
      export: (
        projectId: number,
        data: { format: 'n-tester' | 'claude' | 'cursor'; scope?: string; write?: boolean },
      ) =>
        request({
          url: `/v1/Ntesterc_project/${projectId}/mcp-configs/export`,
          method: 'post',
          data,
        }),
    },
    skills: {
      list: (projectId: number, params?: Record<string, any>) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/skills`, method: 'get', params }),
      create: (projectId: number, data: any) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/skills`, method: 'post', data }),
      update: (projectId: number, id: number, data: any) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/skills/${id}`, method: 'put', data }),
      remove: (projectId: number, id: number) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/skills/${id}`, method: 'delete' }),
      content: (projectId: number, id: number) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/skills/${id}/content`, method: 'get' }),
      execute: (projectId: number, id: number, data?: { arguments?: Record<string, any>; session_id?: string }) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/skills/${id}/execute`, method: 'post', data: data || {} }),
      importGit: (projectId: number, data: any) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/skills/import/git`, method: 'post', data }),
      importUpload: (projectId: number, file: File, params?: { scenario_category?: string; entry_command?: string }) => {
        const fd = new FormData();
        fd.append('file', file);
        return request({
          url: `/v1/Ntesterc_project/${projectId}/skills/import/upload`,
          method: 'post',
          params,
          data: fd,
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      },
    },
    apiKeys: {
      list: (projectId: number, params?: Record<string, any>) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/api-keys`, method: 'get', params }),
      create: (projectId: number, data: any) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/api-keys`, method: 'post', data }),
      update: (projectId: number, id: number, data: any) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/api-keys/${id}`, method: 'put', data }),
      remove: (projectId: number, id: number) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/api-keys/${id}`, method: 'delete' }),
      test: (projectId: number, id: number) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/api-keys/${id}/test`, method: 'post' }),
      regenerate: (projectId: number, id: number) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/api-keys/${id}/regenerate`, method: 'post' }),
    },
    knowledge: {
      globalConfig: {
        get: (projectId: number) =>
          request({ url: `/v1/Ntesterc_project/${projectId}/knowledge/global-config`, method: 'get' }),
        save: (projectId: number, data: any) =>
          request({ url: `/v1/Ntesterc_project/${projectId}/knowledge/global-config`, method: 'put', data }),
      },
      testEmbedding: (projectId: number, data: any) =>
        request({
          url: `/v1/Ntesterc_project/${projectId}/knowledge/test-embedding`,
          method: 'post',
          data,
        }),
      systemStatus: (projectId: number) =>
        request({ url: `/v1/Ntesterc_project/${projectId}/knowledge/system-status`, method: 'get' }),
      bases: {
        list: (projectId: number, params?: Record<string, any>) =>
          request({ url: `/v1/Ntesterc_project/${projectId}/knowledge-bases`, method: 'get', params }),
        create: (projectId: number, data: any) =>
          request({ url: `/v1/Ntesterc_project/${projectId}/knowledge-bases`, method: 'post', data }),
        update: (projectId: number, kbId: string | number, data: any) =>
          request({
            url: `/v1/Ntesterc_project/${projectId}/knowledge-bases/${kbId}`,
            method: 'put',
            data,
          }),
        remove: (projectId: number, kbId: string | number) =>
          request({
            url: `/v1/Ntesterc_project/${projectId}/knowledge-bases/${kbId}`,
            method: 'delete',
          }),
        stats: (projectId: number, kbId: string | number) =>
          request({
            url: `/v1/Ntesterc_project/${projectId}/knowledge-bases/${kbId}/statistics`,
            method: 'get',
          }),
        vectorStatus: (projectId: number, kbId: string | number) =>
          request({
            url: `/v1/Ntesterc_project/${projectId}/knowledge-bases/${kbId}/vector-status`,
            method: 'get',
          }),
      },
      documents: {
        list: (projectId: number, kbId: string | number, params?: Record<string, any>) =>
          request({
            url: `/v1/Ntesterc_project/${projectId}/knowledge-bases/${kbId}/documents`,
            method: 'get',
            params,
          }),
        chunks: (projectId: number, kbId: string | number, docId: string | number) =>
          request({
            url: `/v1/Ntesterc_project/${projectId}/knowledge-bases/${kbId}/documents/${docId}/chunks`,
            method: 'get',
          }),
        upload: (projectId: number, kbId: string | number, file: File) => {
          const fd = new FormData();
          fd.append('file', file);
          return request({
            url: `/v1/Ntesterc_project/${projectId}/knowledge-bases/${kbId}/documents`,
            method: 'post',
            data: fd,
            headers: { 'Content-Type': 'multipart/form-data' },
          });
        },
        remove: (projectId: number, kbId: string | number, docId: string | number) =>
          request({
            url: `/v1/Ntesterc_project/${projectId}/knowledge-bases/${kbId}/documents/${docId}`,
            method: 'delete',
          }),
      },
      query: (projectId: number, kbId: string | number, data: { query: string; top_k?: number }) =>
        request({
          url: `/v1/Ntesterc_project/${projectId}/knowledge-bases/${kbId}/query`,
          method: 'post',
          data,
        }),
    },
  };
}

export const projectPlatformApi = useProjectPlatformApi();
