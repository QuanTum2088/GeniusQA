/**
 * AI智能化模块接口
 */
import request from '/@/utils/request';

export const requirementDocumentApi = {
  list: (params?: any) =>
    request({ 
      url: '/v1/ai_intelligence/requirement-documents', 
      method: 'get', 
      params 
    }),
  upload: (data: FormData) =>
    request({
      url: '/v1/ai_intelligence/requirement-documents',
      method: 'post',
      data,
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  get: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/requirement-documents/${id}`, 
      method: 'get' 
    }),
  update: (id: number, data: any) =>
    request({ 
      url: `/v1/ai_intelligence/requirement-documents/${id}`, 
      method: 'put', 
      data 
    }),
  delete: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/requirement-documents/${id}`, 
      method: 'delete' 
    }),
  analyze: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/requirement-documents/${id}/analyze`, 
      method: 'post' 
    }),
  getAnalysis: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/requirement-documents/${id}/analysis`, 
      method: 'get' 
    }),
};

export function useRequirementDocumentApi() {
  return requirementDocumentApi;
}

export const aiModelConfigApi = {
  list: (params?: any) =>
    request({ 
      url: '/v1/ai_intelligence/ai-model-configs', 
      method: 'get', 
      params 
    }),
  create: (data: any) =>
    request({ 
      url: '/v1/ai_intelligence/ai-model-configs', 
      method: 'post', 
      data 
    }),
  get: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/ai-model-configs/${id}`, 
      method: 'get' 
    }),
  update: (id: number, data: any) =>
    request({ 
      url: `/v1/ai_intelligence/ai-model-configs/${id}`, 
      method: 'put', 
      data 
    }),
  delete: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/ai-model-configs/${id}`, 
      method: 'delete' 
    }),
};

export function useAiModelConfigApi() {
  return aiModelConfigApi;
}

export const promptConfigApi = {
  list: (params?: any) =>
    request({ 
      url: '/v1/ai_intelligence/prompt-configs', 
      method: 'get', 
      params 
    }),
  create: (data: any) =>
    request({ 
      url: '/v1/ai_intelligence/prompt-configs', 
      method: 'post', 
      data 
    }),
  get: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/prompt-configs/${id}`, 
      method: 'get' 
    }),
  update: (id: number, data: any) =>
    request({ 
      url: `/v1/ai_intelligence/prompt-configs/${id}`, 
      method: 'put', 
      data 
    }),
  delete: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/prompt-configs/${id}`, 
      method: 'delete' 
    }),
};

export function usePromptConfigApi() {
  return promptConfigApi;
}

export const generationTaskApi = {
  list: (params?: any) =>
    request({ 
      url: '/v1/ai_intelligence/generation-tasks', 
      method: 'get', 
      params 
    }),
  create: (data: any) =>
    request({ 
      url: '/v1/ai_intelligence/generation-tasks', 
      method: 'post', 
      data 
    }),
  get: (taskId: string) =>
    request({ 
      url: `/v1/ai_intelligence/generation-tasks/${taskId}`, 
      method: 'get' 
    }),
  stream: (taskId: string) => `/v1/ai_intelligence/generation-tasks/${taskId}/stream`,
  saveToTestcases: (taskId: string, data: any) =>
    request({
      url: `/v1/ai_intelligence/generation-tasks/${taskId}/save-to-testcases`,
      method: 'post',
      data,
    }),
  delete: (taskId: string) =>
    request({ url: `/v1/ai_intelligence/generation-tasks/${taskId}`, method: 'delete' }),
  batchDelete: (taskIds: string[]) =>
    request({
      url: '/v1/ai_intelligence/generation-tasks/batch-delete',
      method: 'post',
      data: taskIds,
    }),
};

export function useGenerationTaskApi() {
  return generationTaskApi;
}

export const projectApi = {
  getSubProjects: (projectId: number, params?: any) =>
    request({
      url: `/v1/ai_intelligence/projects/${projectId}/sub-projects`,
      method: 'get',
      params,
    }),
};

export function useAiIntelligenceProjectApi() {
  return projectApi;
}

export const testcaseTemplateApi = {
  list: (params?: any) =>
    request({ 
      url: '/v1/ai_intelligence/testcase-templates', 
      method: 'get', 
      params 
    }),
  get: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/testcase-templates/${id}`, 
      method: 'get' 
    }),
  create: (data: any) =>
    request({ 
      url: '/v1/ai_intelligence/testcase-templates', 
      method: 'post', 
      data 
    }),
  update: (id: number, data: any) =>
    request({ 
      url: `/v1/ai_intelligence/testcase-templates/${id}`, 
      method: 'put', 
      data 
    }),
  delete: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/testcase-templates/${id}`, 
      method: 'delete' 
    }),
  export: (id: number) =>
    request({
      url: `/v1/ai_intelligence/testcase-templates/${id}/export`,
      method: 'get',
      responseType: 'blob',
    }),
  import: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request({
      url: '/v1/ai_intelligence/testcase-templates/import',
      method: 'post',
      data: formData,
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  preview: (id: number, sampleData: any) =>
    request({
      url: `/v1/ai_intelligence/testcase-templates/${id}/preview`,
      method: 'post',
      data: sampleData,
    }),
};

export function useTestcaseTemplateApi() {
  return testcaseTemplateApi;
}

export const aiCaseApi = {
  list: (params?: any) =>
    request({ 
      url: '/v1/ai_intelligence/ai-cases', 
      method: 'get', 
      params 
    }),
  create: (data: any) =>
    request({ 
      url: '/v1/ai_intelligence/ai-cases', 
      method: 'post', 
      data 
    }),
  get: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/ai-cases/${id}`, 
      method: 'get' 
    }),
  update: (id: number, data: any) =>
    request({ 
      url: `/v1/ai_intelligence/ai-cases/${id}`, 
      method: 'put', 
      data 
    }),
  delete: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/ai-cases/${id}`, 
      method: 'delete' 
    }),
  batchDelete: (case_ids: number[]) =>
    request({
      url: '/v1/ai_intelligence/ai-cases/batch-delete',
      method: 'post',
      data: { case_ids },
    }),
  execute: (id: number, headless: boolean = false) =>
    request({
      url: `/v1/ai_intelligence/ai-cases/${id}/execute`,
      method: 'post',
      params: { headless },
    }),
  batchExecute: (data: {
    task_name: string;
    execution_mode: string;
    parallel_count: number;
    case_ids: number[];
  }) => request({ 
    url: '/v1/ai_intelligence/ai-cases/batch-execute', 
    method: 'post', 
    data 
  }),
  importFromModules: (data: { project_id: number; module_ids: number[] }) =>
    request({
      url: '/v1/ai_intelligence/ai-cases/import-from-modules',
      method: 'post',
      data,
    }),
  importFromExcel: (file: File, project_id?: number, module_id?: number) => {
    const formData = new FormData();
    formData.append('file', file);
    if (project_id) {
      formData.append('project_id', project_id.toString());
    }
    if (module_id) {
      formData.append('module_id', module_id.toString());
    }
    return request({
      url: '/v1/ai_intelligence/ai-cases/import-from-excel',
      method: 'post',
      data: formData,
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export function useAiCaseApi() {
  return aiCaseApi;
}

export const aiExecutionRecordApi = {
  list: (params?: any) =>
    request({ 
      url: '/v1/ai_intelligence/ai-execution-records', 
      method: 'get', 
      params 
    }),
  create: (data: any) =>
    request({ 
      url: '/v1/ai_intelligence/ai-execution-records', 
      method: 'post', 
      data 
    }),
  get: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/ai-execution-records/${id}`, 
      method: 'get' 
    }),
  delete: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/ai-execution-records/${id}`, 
      method: 'delete' 
    }),
  getStatus: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/ai-execution-records/${id}/status`, 
      method: 'get' 
    }),
};

export function useAiExecutionRecordApi() {
  return aiExecutionRecordApi;
}

export const figmaConfigApi = {
  list: (params?: any) =>
    request({ 
      url: '/v1/ai_intelligence/figma-configs', 
      method: 'get', 
      params 
    }),
  create: (data: any) =>
    request({ 
      url: '/v1/ai_intelligence/figma-configs', 
      method: 'post', 
      data 
    }),
  get: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/figma-configs/${id}`, 
      method: 'get' 
    }),
  update: (id: number, data: any) =>
    request({ 
      url: `/v1/ai_intelligence/figma-configs/${id}`, 
      method: 'put', 
      data 
    }),
  delete: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/figma-configs/${id}`, 
      method: 'delete' 
    }),
  extract: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/figma-configs/${id}/extract`, 
      method: 'post' 
    }),
  extractWithMode: (
    configId: number,
    mode: 'simple' | 'complete',
    forceRefresh: boolean = false,
  ) =>
    request({
      url: `/v1/ai_intelligence/figma-configs/${configId}/extract-with-mode`,
      method: 'post',
      params: { extraction_mode: mode, force_refresh: forceRefresh },
    }),
  getTaskStatus: (taskId: string) =>
    request({ 
      url: `/v1/ai_intelligence/figma-extraction-tasks/${taskId}`, 
      method: 'get' 
    }),
  getLatestTask: (configId: number) =>
    request({
      url: `/v1/ai_intelligence/figma-configs/${configId}/latest-task`,
      method: 'get',
    }),
  preview: (configId: number) =>
    request({ 
      url: `/v1/ai_intelligence/figma-configs/${configId}/preview`, 
      method: 'get' 
    }),
  getRateLimitStatus: (configId: number) =>
    request({
      url: `/v1/ai_intelligence/figma-configs/${configId}/rate-limit-status`,
      method: 'get',
    }),
  getCacheInfo: (configId: number) =>
    request({
      url: `/v1/ai_intelligence/figma-configs/${configId}/cache-info`,
      method: 'get',
    }),
  getCachedData: (configId: number) =>
    request({
      url: `/v1/ai_intelligence/figma-configs/${configId}/cached-data`,
      method: 'get',
    }),
  clearCache: (configId: number) =>
    request({ url: `/v1/ai_intelligence/figma-configs/${configId}/cache`, method: 'delete' }),
  checkUpdates: (configId: number) =>
    request({
      url: `/v1/ai_intelligence/figma-configs/${configId}/check-updates`,
      method: 'get',
    }),
};

export function useFigmaConfigApi() {
  return figmaConfigApi;
}

export const aiTestSuiteApi = {
  list: (params?: any) =>
    request({ 
      url: '/v1/ai_intelligence/ai-test-suites', 
      method: 'get', 
      params 
    }),
  create: (data: any) =>
    request({ 
      url: '/v1/ai_intelligence/ai-test-suites', 
      method: 'post', 
      data 
    }),
  get: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/ai-test-suites/${id}`, 
      method: 'get' 
    }),
  update: (id: number, data: any) =>
    request({ 
      url: `/v1/ai_intelligence/ai-test-suites/${id}`, 
      method: 'put', 
      data 
    }),
  delete: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/ai-test-suites/${id}`, 
      method: 'delete' 
    }),
  execute: (id: number, data: { execution_name?: string; execution_mode: string }) =>
    request({ 
      url: `/v1/ai_intelligence/ai-test-suites/${id}/execute`, 
      method: 'post', 
      data 
    }),
  getExecutions: (params?: any) =>
    request({ 
      url: '/v1/ai_intelligence/ai-test-suite-executions', 
      method: 'get', 
      params 
    }),
  getExecutionDetail: (id: number) =>
    request({ 
      url: `/v1/ai_intelligence/ai-test-suite-executions/${id}`, 
      method: 'get' 
    }),
};

export function useAiTestSuiteApi() {
  return aiTestSuiteApi;
}

export const aiTestReportApi = {
  list: (params?: any) =>
    request({ 
      url: '/v1/ai_intelligence/ai-test-reports', 
      method: 'get', 
      params 
    }),
  create: (data: any) =>
    request({ 
      url: '/v1/ai_intelligence/ai-test-reports', 
      method: 'post', 
      data 
    }),
  delete: (reportId: string) =>
    request({ 
      url: `/v1/ai_intelligence/ai-test-reports/${reportId}`, 
      method: 'delete' 
    }),
};

export function useAiTestReportApi() {
  return aiTestReportApi;
}
