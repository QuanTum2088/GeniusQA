/**
 * API v1 统一导出
 */

// 系统管理模块
export { useAuthApi } from './system/auth';
export { useUserApi } from './system/user';
export { useRoleApi } from './system/role';
export { useMenuApi } from './system/menu';
export { useDeptApi } from './system/dept';
export { useDictTypeApi, useDictDataApi, useDictApi } from './system/dict';
export { usePermissionApi } from './system/permission';
export { useLogApi } from './system/log';
export { useOAuthApi } from './system/oauth';
export { useCodeGeneratorApi } from './system/codeGenerator';

// 通用模块
export { useFileApi } from './common/file';
export { useHealthApi } from './common/health';
export { useDashboardApi, dashboardApi } from './common/dashboard';

// 监控模块
export { useServerMonitorApi } from './monitor/server';
export { useOnlineUserApi } from './monitor/online';

// 项目管理模块
export {
  useProjectApi,
  getProjectList,
  getProjectDetail,
  createProject,
  updateProject,
  deleteProject,
} from './projects/project';
export { useProjectPlatformApi } from './projects/platform';

// AI 模块
export { useAssistantApi } from './ai/assistant';
export { useSkillsApi, skillsApi } from './ai/skills';
export { useLLMConfigApi } from './ai/llmConfig';
export { useAiKnowledgeConfigApi, aiKnowledgeConfigApi } from './ai/knowledgeConfig';
export { useConversationApi } from './ai/conversation';
export {
  useRequirementDocumentApi,
  useAiModelConfigApi,
  usePromptConfigApi,
  useGenerationTaskApi,
  useAiIntelligenceProjectApi,
  useTestcaseTemplateApi,
  useAiCaseApi,
  useAiExecutionRecordApi,
  useFigmaConfigApi,
  useAiTestSuiteApi,
  useAiTestReportApi,
} from './ai/intelligence';

// 测试模块
export { useDataFactoryApi } from './testing/dataFactory';
export { useModuleApi } from './testing/modules';
export { useTestcaseApi } from './testing/testcases';
export { useApiAutomationApi } from './testing/apiAutomation';
export { useUiAutomationApi } from './testing/uiAutomation';
export { useTaskSchedulerApi } from './testing/taskScheduler';
export { usePerformanceApi } from './testing/performance';
export { useMitmproxyApi } from './testing/mitmproxy';
export { usePrecisionTestApi } from './testing/precisionTest';
export { useCloudDeviceApi } from './testing/cloudDevice';
export { useCloudDeviceCompatApi } from './testing/cloudDeviceCompat';
export { useAppManagementApi } from './testing/appManagement';
export { useAppManagementDeviceApi } from './testing/appManagementDevice';
export { useWebManagementApi } from './testing/webManagement';
export { useDesktopAutomationApi } from './testing/desktopAutomation';
export { useMiniAutomationApi } from './testing/miniprogramAutomation';

// 评审模块
export { useReviewApi } from './reviews/review';

// 通知模块
export {
  useNotificationConfigApi,
  useNotificationHistoryApi,
  useTaskNotificationApi,
  useNotificationSendApi,
  notificationConfigApi,
  notificationHistoryApi,
  taskNotificationApi,
  notificationSendApi,
} from './notifications/notification';
