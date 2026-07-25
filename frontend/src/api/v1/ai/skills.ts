import request from '/@/utils/request';

export function useSkillsApi() {
  return {
    list: (projectId: number, params?: Record<string, any>) =>
      request({ 
        url: `/v1/Ntesterc_skills/projects/${projectId}`, 
        method: 'GET', 
        params 
      }),
    create: (projectId: number, data: any) =>
      request({ 
        url: `/v1/Ntesterc_skills/projects/${projectId}`, 
        method: 'POST', 
        data 
      }),
    update: (projectId: number, skillId: number, data: any) =>
      request({ 
        url: `/v1/Ntesterc_skills/projects/${projectId}/${skillId}`, 
        method: 'PUT', 
        data 
      }),
    remove: (projectId: number, skillId: number) =>
      request({ 
        url: `/v1/Ntesterc_skills/projects/${projectId}/${skillId}`, 
        method: 'DELETE' 
      }),
    content: (projectId: number, skillId: number) =>
      request({ 
        url: `/v1/Ntesterc_skills/projects/${projectId}/${skillId}/content`, 
        method: 'GET' 
      }),
    manifest: (projectId: number, skillId: number) =>
      request({ 
        url: `/v1/Ntesterc_skills/projects/${projectId}/${skillId}/manifest`, 
        method: 'GET' 
      }),
    execute: (projectId: number, skillId: number, data?: { arguments?: Record<string, any>; session_id?: string }) =>
      request({ 
        url: `/v1/Ntesterc_skills/projects/${projectId}/${skillId}/execute`, 
        method: 'POST', 
        data: data || {} 
      }),
    executeActionAsync: (
      projectId: number,
      skillId: number,
      data?: { action_name?: string; arguments?: Record<string, any>; session_id?: string; runner_type?: string }
    ) => request({ url: `/v1/Ntesterc_skills/projects/${projectId}/${skillId}/actions/execute`, method: 'POST', data: data || {} }),
    job: (projectId: number, jobId: number) =>
      request({ 
        url: `/v1/Ntesterc_skills/projects/${projectId}/jobs/${jobId}`, 
        method: 'GET' 
      }),
    jobArtifacts: (projectId: number, jobId: number) =>
      request({ 
        url: `/v1/Ntesterc_skills/projects/${projectId}/jobs/${jobId}/artifacts`, 
        method: 'GET' 
      }),
    jobStreamUrl: (projectId: number, jobId: number) => `/v1/Ntesterc_skills/projects/${projectId}/jobs/${jobId}/stream`,
    artifactDownloadUrl: (projectId: number, artifactId: number) =>
      `/v1/Ntesterc_skills/projects/${projectId}/artifacts/${artifactId}/download`,
    importGit: (projectId: number, data: any) =>
      request({ 
        url: `/v1/Ntesterc_skills/projects/${projectId}/import/git`, 
        method: 'POST', 
        data 
      }),
    importUpload: (projectId: number, file: File, params?: { scenario_category?: string; entry_command?: string }) => {
      const fd = new FormData();
      fd.append('file', file);
      return request({
        url: `/v1/Ntesterc_skills/projects/${projectId}/import/upload`,
        method: 'POST',
        params,
        data: fd,
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
  };
}

export const skillsApi = useSkillsApi();

