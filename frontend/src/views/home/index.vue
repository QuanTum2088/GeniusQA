<template>
  <div class="home-page">
    <div class="notice-bar">
      <el-icon class="notice-icon"><Bell /></el-icon>
      <div class="notice-track-wrap">
        <div class="notice-track">
          <span class="notice-text">🚀 GeniusQA AI全栈测试平台，提供接口自动化、双引擎UI自动化、APP自动化，支持MCP、知识库、自定义Skill管理，一站式解决方案！</span>
          <span class="notice-text">🚀 GeniusQA AI全栈测试平台，提供接口自动化、双引擎UI自动化、APP自动化，支持MCP、知识库、自定义Skill管理，一站式解决方案！</span>
        </div>
      </div>
    </div>
    <div class="page-body">
      <div class="hero-section">
        <div class="hero-content">
          <div class="hero-left">
            <div class="hero-greeting">{{ greetingText }}，{{ userInfo.nickname || userInfo.username || '管理员' }}</div>
            <div class="hero-sub">欢迎回到 GeniusQA 全栈测试平台</div>
            <div class="hero-meta">
              <span class="hero-date"><el-icon class="meta-icon"><Calendar /></el-icon>{{ currentDate }}</span>
              <span class="hero-time"><el-icon class="meta-icon"><Clock /></el-icon>{{ currentTime }}</span>
            </div>
          </div>
          <div class="hero-right">
            <div class="hero-avatar-wrap">
              <el-avatar :size="64" :src="userInfo.avatar || undefined" class="hero-avatar">
                <el-icon :size="30"><User /></el-icon>
              </el-avatar>
              <div class="hero-avatar-ring"></div>
            </div>
          </div>
        </div>
      </div>
      <el-row :gutter="16" class="stat-row">
        <el-col :xs="12" :sm="8" :md="4" v-for="(card, i) in statCards" :key="i">
          <div class="stat-card" :class="{ 'no-click': !card.path }" @click="card.path && goTo(card.path)">
            <div class="stat-card-left">
              <div class="stat-val">{{ card.value }}</div>
              <div class="stat-label">{{ card.label }}</div>
              <div class="stat-change" :class="card.changeType">
                <el-icon v-if="card.changeType === 'up'"><Top /></el-icon>
                <el-icon v-else-if="card.changeType === 'down'"><Bottom /></el-icon>
                <span>{{ card.change }}</span>
              </div>
            </div>
            <div class="stat-card-icon-wrap" :style="{ background: card.bgColor }">
              <el-icon :size="24" :style="{ color: card.iconColor }"><component :is="card.icon" /></el-icon>
            </div>
          </div>
        </el-col>
      </el-row>
      <el-row :gutter="16" class="mid-row">
        <el-col :xs="24" :md="12">
          <div class="panel">
            <div class="panel-hd">
              <span class="panel-title">执行趋势</span>
              <el-select v-model="trendDays" size="small" style="width:90px" @change="initTrendChart">
                <el-option label="近7天" :value="7" />
                <el-option label="近14天" :value="14" />
                <el-option label="近30天" :value="30" />
              </el-select>
            </div>
            <div class="chart-wrap" ref="trendChartEl" v-loading="trendLoading"></div>
          </div>
        </el-col>
        <el-col :xs="24" :md="6">
          <div class="panel">
            <div class="panel-hd">
              <span class="panel-title">测试类型分布</span>
            </div>
            <div class="chart-wrap" ref="typeChartEl" v-loading="typeLoading"></div>
          </div>
        </el-col>
        <el-col :xs="24" :md="6">
          <div class="panel recent-panel">
            <div class="panel-hd recent-tab-hd">
              <div class="recent-tabs">
                <span
                  class="recent-tab"
                  :class="{ active: recentTab === 'api' }"
                  @click="switchRecentTab('api')"
                >接口执行</span>
                <span
                  class="recent-tab"
                  :class="{ active: recentTab === 'web' }"
                  @click="switchRecentTab('web')"
                >UI执行</span>
              </div>
              <span class="more-link" @click="goTo(recentTab === 'api' ? '/api-automation/results' : '/web/result')">更多 &gt;</span>
            </div>
            <div class="recent-scroll-wrap" ref="recentScrollWrap">
              <el-empty v-if="!currentRecentList.length" description="暂无记录" :image-size="48" style="padding: 40px 0" />
              <div v-else class="recent-scroll-track" ref="recentScrollTrack">
                <template v-for="pass in 2" :key="pass">
                  <div
                    v-for="(item, i) in currentRecentList"
                    :key="`${pass}-${i}`"
                    class="recent-item"
                  >
                    <div class="recent-item-left">
                      <el-icon class="recent-type-icon" :style="{ color: recentTab === 'api' ? '#6366f1' : '#0ea5e9' }">
                        <component :is="recentTab === 'api' ? Connection : Monitor" />
                      </el-icon>
                      <div class="recent-item-info">
                        <div class="recent-item-name">{{ item.name }}</div>
                        <div class="recent-item-meta">{{ item.username || '-' }} · {{ item.time }}</div>
                      </div>
                    </div>
                    <el-tag
                      :type="item.statusTag"
                      size="small"
                      effect="light"
                    >{{ item.statusText }}</el-tag>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
      <div class="panel llm-usage-panel">
        <div class="panel-hd">
          <div class="llm-usage-hd-left">
            <span class="panel-title">
              <el-icon class="title-icon"><TrendCharts /></el-icon>
              用量统计
            </span>
            <span class="llm-usage-hint">用量仅作参考，具体以供应商的统计为准</span>
          </div>
          <div class="llm-usage-hd-right">
            <el-select v-model="llmUsageDays" size="small" style="width:96px" @change="loadLlmUsage">
              <el-option label="近7天" :value="7" />
              <el-option label="近14天" :value="14" />
              <el-option label="近30天" :value="30" />
            </el-select>
            <el-button size="small" :icon="Refresh" circle @click="loadLlmUsage" />
          </div>
        </div>
        <div class="llm-usage-tabs">
          <span
            v-for="t in llmUsageTabs"
            :key="t.key"
            class="llm-usage-tab"
            :class="{ active: llmUsageTab === t.key }"
            @click="switchLlmUsageTab(t.key)"
          >{{ t.label }}</span>
        </div>
        <div class="llm-usage-body" v-loading="llmUsageLoading">
          <template v-if="llmUsageTab === 'overview'">
            <div class="llm-usage-overview">
              <div class="llm-usage-donut-wrap">
                <div class="llm-usage-donut" ref="llmUsageDonutEl"></div>
              </div>
              <div class="llm-usage-overview-right">
                <div class="llm-usage-kicker">模型分布</div>
                <div class="llm-usage-total">{{ formatTokenCount(llmUsage.overview.total_tokens) }}</div>
                <div class="llm-usage-sub">
                  缓存 {{ formatTokenCount(llmUsage.overview.cached_tokens) }}
                  · 未缓存 {{ formatTokenCount(llmUsage.overview.uncached_tokens) }}
                </div>
                <div class="llm-usage-metrics">
                  <div class="llm-metric">
                    <div class="llm-metric-val">{{ llmUsage.overview.request_count }}</div>
                    <div class="llm-metric-label">请求数</div>
                  </div>
                  <div class="llm-metric">
                    <div class="llm-metric-val">{{ formatTokenCount(llmUsage.overview.cached_tokens) }}</div>
                    <div class="llm-metric-label">缓存命中</div>
                  </div>
                  <div class="llm-metric">
                    <div class="llm-metric-val">{{ llmUsage.overview.error_count }}</div>
                    <div class="llm-metric-label">错误数</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="llm-usage-split">
              <div class="llm-usage-col">
                <div class="llm-col-title">模型分布</div>
                <el-empty v-if="!llmUsage.by_model.length" description="暂无用量数据，聊天调用后开始累积" :image-size="48" />
                <div v-else class="llm-usage-scroll" :class="{ 'is-scrollable': llmUsage.by_model.length >= 3 }">
                  <div v-for="(m, i) in llmUsage.by_model" :key="i" class="llm-model-row">
                    <div class="llm-model-left">
                      <div class="llm-model-dot" :style="{ background: modelColor(i) }"></div>
                      <div class="llm-model-text">
                        <div class="llm-model-name">{{ m.provider ? `${m.provider} / ${m.model_name}` : m.model_name }}</div>
                        <div class="llm-model-meta">{{ m.request_count }} 次 · {{ m.error_count }} 错误</div>
                        <div class="llm-model-bar">
                          <div class="llm-model-bar-fill" :style="{ width: tokenShare(m.total_tokens) + '%', background: modelColor(i) }"></div>
                        </div>
                      </div>
                    </div>
                    <div class="llm-model-tokens">{{ formatTokenCount(m.total_tokens) }}</div>
                  </div>
                </div>
              </div>
              <div class="llm-usage-col">
                <div class="llm-col-title">请求明细</div>
                <el-empty v-if="!llmUsage.recent_requests.length" description="暂无请求记录" :image-size="48" />
                <div v-else class="llm-usage-scroll" :class="{ 'is-scrollable': llmUsage.recent_requests.length >= 3 }">
                  <div v-for="r in llmUsage.recent_requests" :key="r.id" class="llm-req-row">
                    <div class="llm-req-top">
                      <span class="llm-req-title">{{ r.source_label || r.source }} · {{ r.model_name }}</span>
                      <el-tag :type="r.status === 'success' ? 'success' : 'danger'" size="small" effect="light">
                        {{ r.status === 'success' ? '完成' : '错误' }}
                      </el-tag>
                    </div>
                    <div class="llm-req-meta">
                      {{ formatTime(r.created_at || '') }}
                      · {{ r.provider ? `${r.provider} / ` : '' }}{{ r.model_name }}
                      · {{ formatTokenCount(r.total_tokens) }} tok
                      · 缓存 {{ formatTokenCount(r.cached_tokens) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
          <template v-else-if="llmUsageTab === 'daily'">
            <div class="llm-usage-chart" ref="llmUsageDailyEl"></div>
            <el-empty v-if="!llmUsage.by_date.length" description="暂无按日数据" :image-size="48" />
          </template>
          <template v-else-if="llmUsageTab === 'category'">
            <div class="llm-usage-tab-grid">
              <div class="llm-usage-chart llm-usage-hbar" ref="llmUsageCategoryEl"></div>
              <div class="llm-usage-tab-list">
                <el-empty v-if="!llmUsage.by_category.length" description="暂无类别数据" :image-size="48" />
                <div v-else class="llm-usage-scroll" :class="{ 'is-scrollable': llmUsage.by_category.length >= 3 }">
                  <div v-for="(c, i) in llmUsage.by_category" :key="i" class="llm-model-row">
                    <div class="llm-model-left">
                      <div class="llm-model-dot" :style="{ background: modelColor(i) }"></div>
                      <div class="llm-model-text">
                        <div class="llm-model-name">{{ c.category }}</div>
                        <div class="llm-model-meta">{{ c.request_count }} 次 · {{ c.error_count }} 错误</div>
                        <div class="llm-model-bar">
                          <div class="llm-model-bar-fill" :style="{ width: tokenShare(c.total_tokens) + '%', background: modelColor(i) }"></div>
                        </div>
                      </div>
                    </div>
                    <div class="llm-model-tokens">{{ formatTokenCount(c.total_tokens) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="llm-usage-tab-grid">
              <div class="llm-usage-chart llm-usage-hbar" ref="llmUsageModelEl"></div>
              <div class="llm-usage-tab-list">
                <el-empty v-if="!llmUsage.by_model.length" description="暂无模型数据" :image-size="48" />
                <div v-else class="llm-usage-scroll" :class="{ 'is-scrollable': llmUsage.by_model.length >= 3 }">
                  <div v-for="(m, i) in llmUsage.by_model" :key="i" class="llm-model-row">
                    <div class="llm-model-left">
                      <div class="llm-model-dot" :style="{ background: modelColor(i) }"></div>
                      <div class="llm-model-text">
                        <div class="llm-model-name">{{ m.provider ? `${m.provider} / ${m.model_name}` : m.model_name }}</div>
                        <div class="llm-model-meta">{{ m.request_count }} 次 · {{ m.error_count }} 错误 · 缓存 {{ formatTokenCount(m.cached_tokens) }}</div>
                        <div class="llm-model-bar">
                          <div class="llm-model-bar-fill" :style="{ width: tokenShare(m.total_tokens) + '%', background: modelColor(i) }"></div>
                        </div>
                      </div>
                    </div>
                    <div class="llm-model-tokens">{{ formatTokenCount(m.total_tokens) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
      <div class="panel review-stats-panel">
        <div class="panel-hd">
          <span class="panel-title">
            <el-icon class="title-icon"><DataAnalysis /></el-icon>
            用例评审统计
          </span>
          <span class="more-link" @click="goTo('/reviews/statistics')">更多 &gt;</span>
        </div>
        <div class="review-stats-body" v-loading="reviewStatsLoading">
          <div class="review-num-grid">
            <div class="review-num-card" @click="goTo('/reviews/index')">
              <div class="review-num-val">{{ reviewStats.total_reviews }}</div>
              <div class="review-num-label">总评审</div>
            </div>
            <div class="review-num-card pending-card" @click="goTo('/reviews/index')">
              <div class="review-num-val">{{ reviewStats.pending_reviews }}</div>
              <div class="review-num-label">待开始</div>
            </div>
            <div class="review-num-card progress-card" @click="goTo('/reviews/index')">
              <div class="review-num-val">{{ reviewStats.in_progress_reviews }}</div>
              <div class="review-num-label">进行中</div>
            </div>
            <div class="review-num-card done-card" @click="goTo('/reviews/index')">
              <div class="review-num-val">{{ reviewStats.completed_reviews }}</div>
              <div class="review-num-label">已完成</div>
            </div>
          </div>
          <div class="review-charts">
            <div class="review-chart-item">
              <div class="review-chart-title">状态分布</div>
              <div class="review-chart-el" ref="reviewStatusChartEl"></div>
            </div>
            <div class="review-chart-item">
              <div class="review-chart-title">优先级分布</div>
              <div class="review-chart-el" ref="reviewPriorityChartEl"></div>
            </div>
          </div>
        </div>
      </div>
      <div class="panel quick-panel">
        <div class="panel-hd">
          <span class="panel-title">快速入口</span>
        </div>
        <div class="quick-grid">
          <div v-for="(entry, i) in quickEntries" :key="i" class="quick-item" @click="goTo(entry.path)">
            <div class="quick-icon-wrap" :style="{ background: entry.bgColor }">
              <el-icon :size="22" :style="{ color: entry.iconColor }"><component :is="entry.icon" /></el-icon>
            </div>
            <div class="quick-item-info">
              <div class="quick-item-name">{{ entry.name }}</div>
              <div class="quick-item-desc">{{ entry.desc }}</div>
            </div>
          </div>
        </div>
      </div>
      <el-row :gutter="16" class="bottom-row">
        <el-col :xs="24" :md="8">
          <div class="panel project-panel">
            <div class="panel-hd">
              <span class="panel-title">项目概览</span>
              <span class="more-link" @click="goTo('/projects/list')">更多 &gt;</span>
            </div>
            <div class="project-list" v-loading="projectLoading">
              <el-empty v-if="!activeProjects.length" description="暂无项目" :image-size="48" />
              <div v-for="(p, i) in activeProjects.slice(0, 5)" :key="p.id" class="project-item">
                <div class="project-rank" :class="i < 3 ? 'rank-gold' : ''">{{ i + 1 }}</div>
                <div class="project-info">
                  <div class="project-name">{{ p.name }}</div>
                  <div class="project-meta">最近活动 {{ formatTime(p.last_activity) }}</div>
                </div>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :md="8">
          <div class="panel">
            <div class="panel-hd">
              <span class="panel-title">通知中心</span>
              <el-badge :value="unreadCount" :hidden="!unreadCount" :max="99">
                <span class="more-link" @click="goTo('/notifications/histories')">更多 &gt;</span>
              </el-badge>
            </div>
            <div class="todo-list">
              <el-empty v-if="!notifications.length" description="暂无通知" :image-size="48" />
              <div v-for="(n, i) in notifications" :key="i" class="todo-item">
                <div class="todo-dot" :class="'dot-' + n.status"></div>
                <div class="todo-content">
                  <div class="todo-title">{{ n.title }}</div>
                  <div class="todo-time">{{ formatTime(n.created_at) }}</div>
                </div>
                <el-tag :type="getStatusTag(n.status)" size="small" effect="plain">{{ getStatusText(n.status) }}</el-tag>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :md="8">
          <div class="panel df-panel">
            <div class="panel-hd">
              <span class="panel-title">数据工厂统计</span>
              <span class="more-link" @click="goTo('/data-factory/tools')">更多 &gt;</span>
            </div>
            <div class="df-body" v-loading="dfStatsLoading">
              <div class="df-total-row">
                <div class="df-total-block">
                  <div class="df-total-val">{{ dfStats.total_records }}</div>
                  <div class="df-total-label">累计使用次数</div>
                </div>
                <div class="df-bar-chart" ref="dfBarChartEl"></div>
              </div>
              <div class="df-recent-title">最近使用</div>
              <div class="df-recent-list">
                <el-empty v-if="!dfStats.recent_tools.length" description="暂无记录" :image-size="36" />
                <div
                  v-for="(t, i) in dfStats.recent_tools.slice(0, 4)"
                  :key="i"
                  class="df-recent-item"
                  @click="goTo('/data-factory/tools')"
                >
                  <div class="df-recent-icon">
                    <el-icon :size="14" style="color:#6366f1"><DataAnalysis /></el-icon>
                  </div>
                  <div class="df-recent-info">
                    <div class="df-recent-name">{{ dfToolNameMap[t.tool_name] || t.tool_scenario_display || t.tool_name }}</div>
                    <div class="df-recent-meta">{{ t.tool_category_display }} · {{ formatTime(t.created_at) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>

      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts" name="home">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useUserStore } from '/@/stores/user';
import { useThemeConfig } from '/@/stores/themeConfig';
import * as echarts from 'echarts';
import { useDashboardApi } from '/@/api/v1/common/dashboard';
import { useApiAutomationApi } from '/@/api/v1/testing/apiAutomation';
import { useWebManagementApi } from '/@/api/v1/testing/webManagement';
import { getReviewStatistics } from '/@/api/v1/reviews/review';
import {
  Bell, Top, Bottom, Folder, Document, MagicStick, UserFilled,
  Connection, DataAnalysis, Collection, Monitor,
  List, TrendCharts, Files, VideoPlay, Phone, Calendar, Clock, User, Refresh
} from '@element-plus/icons-vue';
import type { LlmUsageStats } from '/@/api/v1/common/dashboard';

const router = useRouter();
const userStore = useUserStore();
const themeConfigStore = useThemeConfig();
const { userInfos: userInfo } = storeToRefs(userStore);
const { themeConfig } = storeToRefs(themeConfigStore);
const dashboardApi = useDashboardApi();
const { get_api_script_result_list } = useApiAutomationApi();
const { get_web_result_list } = useWebManagementApi();


let timer: any = null;
const currentTime = ref('');
const currentDate = ref('');
const greetingText = computed(() => {
  const h = new Date().getHours();
  if (h < 6) return '凌晨好';
  if (h < 9) return '早上好';
  if (h < 12) return '上午好';
  if (h < 14) return '中午好';
  if (h < 17) return '下午好';
  if (h < 19) return '傍晚好';
  if (h < 22) return '晚上好';
  return '夜深了';
});

const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false });
  currentDate.value = now.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' });
};


const coreStats = ref({
  projects: { total: 0, active: 0, monthly_new: 0 },
  test_cases: { total: 0, weekly_new: 0, pass_rate: 0 },
  ai_executions: { total: 0, monthly_generated: 0, success_rate: 0 },
  users: { total: 0, online: 0, monthly_active: 0 },
});

const statCards = computed(() => [
  {
    icon: Folder, label: '项目总数',
    value: coreStats.value.projects?.total ?? 0,
    change: `活跃 ${coreStats.value.projects?.active ?? 0}`,
    changeType: 'neutral',
    bgColor: '#ede9fe', iconColor: '#7c3aed',
    path: '/projects/list',
  },
  {
    icon: Document, label: '测试用例',
    value: coreStats.value.test_cases?.total ?? 0,
    change: `本周新增 ${coreStats.value.test_cases?.weekly_new ?? 0}`,
    changeType: 'up',
    bgColor: '#dbeafe', iconColor: '#2563eb',
    path: '/testing/testcases',
  },
  {
    icon: VideoPlay, label: '执行次数',
    value: apiExecTotal.value + webExecTotal.value,
    change: `API+Web`,
    changeType: 'up',
    bgColor: '#d1fae5', iconColor: '#059669',
    path: '',
  },
  {
    icon: MagicStick, label: 'AI用例执行',
    value: coreStats.value.ai_executions?.total ?? 0,
    change: `成功率 ${coreStats.value.ai_executions?.success_rate ?? 0}%`,
    changeType: 'up',
    bgColor: '#fce7f3', iconColor: '#db2777',
    path: '/ai/intelligence/browser-use/cases',
  },
  {
    icon: TrendCharts, label: '通过率',
    value: `${coreStats.value.test_cases?.pass_rate ?? 0}%`,
    change: `API+Web`,
    changeType: coreStats.value.test_cases?.pass_rate >= 80 ? 'up' : 'down',
    bgColor: '#fef3c7', iconColor: '#d97706',
    path: '',
  },
  {
    icon: UserFilled, label: '用户总数',
    value: coreStats.value.users?.total ?? 0,
    change: `在线 ${coreStats.value.users?.online ?? 0}`,
    changeType: 'neutral',
    bgColor: '#e0f2fe', iconColor: '#0284c7',
    path: '/system/user',
  },
]);


const trendChartEl = ref<HTMLElement>();
const trendLoading = ref(false);
const trendDays = ref(7);
const apiExecTotal = ref(0);
const webExecTotal = ref(0);
let trendChartInstance: echarts.ECharts | null = null;

const initTrendChart = async () => {
  trendLoading.value = true;
  try {
    const [apiRes, webRes] = await Promise.allSettled([
      get_api_script_result_list({ page: 1, pageSize: 500, search: {} }),
      get_web_result_list({ page: 1, pageSize: 500, search: {} }),
    ]);
    const apiList: any[] = apiRes.status === 'fulfilled' ? (apiRes.value?.data?.content || []) : [];
    const webList: any[] = webRes.status === 'fulfilled' ? (webRes.value?.data?.content || []) : [];
    apiExecTotal.value = apiList.length;
    webExecTotal.value = webList.length;

    const days: string[] = [];
    const dayLabels: string[] = [];
    for (let i = trendDays.value - 1; i >= 0; i--) {
      const d = new Date(); d.setDate(d.getDate() - i);
      days.push(`${d.getMonth() + 1}-${String(d.getDate()).padStart(2, '0')}`);
      dayLabels.push(`${d.getMonth() + 1}/${d.getDate()}`);
    }

    const countByDay = (list: any[], field = 'start_time') => {
      const map: Record<string, number> = {};
      days.forEach(d => { map[d] = 0; });
      list.forEach((item: any) => {
        const t = item[field] || item.creation_date || '';
        if (!t) return;
        const d = new Date(t);
        const key = `${d.getMonth() + 1}-${String(d.getDate()).padStart(2, '0')}`;
        if (map[key] !== undefined) map[key]++;
      });
      return days.map(d => map[d]);
    };

    const apiData = countByDay(apiList, 'start_time');
    const webData = countByDay(webList, 'start_time');

    const passRateByDay = () => {
      const passMap: Record<string, number> = {};
      const totalMap: Record<string, number> = {};
      days.forEach((d) => {
        passMap[d] = 0;
        totalMap[d] = 0;
      });

      apiList.forEach((item: any) => {
        const t = item.start_time || item.creation_date || '';
        if (!t) return;
        const d = new Date(t);
        const key = `${d.getMonth() + 1}-${String(d.getDate()).padStart(2, '0')}`;
        if (totalMap[key] === undefined) return;
        const result = typeof item.result === 'string'
          ? (() => { try { return JSON.parse(item.result); } catch { return null; } })()
          : item.result;
        const total = Number(result?.total || 0);
        const passed = Number(result?.pass || 0);
        if (total <= 0) return;
        totalMap[key] += total;
        passMap[key] += passed;
      });

      webList.forEach((item: any) => {
        const t = item.start_time || item.creation_date || '';
        if (!t) return;
        const d = new Date(t);
        const key = `${d.getMonth() + 1}-${String(d.getDate()).padStart(2, '0')}`;
        if (totalMap[key] === undefined) return;
        let result = item.result;
        if (typeof result === 'string') {
          try { result = JSON.parse(result); } catch { result = []; }
        }
        if (!Array.isArray(result)) return;
        result.forEach((row: any) => {
          const total = Number(row?.total || 0);
          const fail = Number(row?.run_false || 0);
          if (total <= 0) return;
          totalMap[key] += total;
          passMap[key] += Math.max(total - fail, 0);
        });
      });

      return days.map((d) => (totalMap[d] > 0 ? Math.round((passMap[d] / totalMap[d]) * 100) : 0));
    };

    const passData = passRateByDay();

    await nextTick();
    if (!trendChartEl.value) return;
    if (!trendChartInstance) trendChartInstance = echarts.init(trendChartEl.value);
    trendChartInstance.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
      legend: { data: ['执行数', '通过率'], bottom: 0, itemWidth: 12, itemHeight: 12, textStyle: { fontSize: 12 } },
      grid: { top: 16, bottom: 36, left: 40, right: 50 },
      xAxis: {
        type: 'category', data: dayLabels, boundaryGap: false,
        axisLine: { lineStyle: { color: '#e5e7eb' } },
        axisLabel: { color: '#9ca3af', fontSize: 11 },
        axisTick: { show: false },
      },
      yAxis: [
        { type: 'value', name: '次数', minInterval: 1, splitLine: { lineStyle: { color: '#f3f4f6' } }, axisLabel: { color: '#9ca3af', fontSize: 11 } },
        { type: 'value', name: '通过率', min: 0, max: 100, axisLabel: { color: '#9ca3af', fontSize: 11, formatter: '{value}%' }, splitLine: { show: false } },
      ],
      series: [
        {
          name: '执行数', type: 'line', yAxisIndex: 0,
          data: apiData.map((v, i) => v + webData[i]),
          smooth: true, symbol: 'circle', symbolSize: 6,
          itemStyle: { color: '#6366f1' },
          lineStyle: { color: '#6366f1', width: 2 },
          areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(99,102,241,0.18)' }, { offset: 1, color: 'rgba(99,102,241,0)' }] } },
        },
        {
          name: '通过率', type: 'line', yAxisIndex: 1,
          data: passData,
          smooth: true, symbol: 'circle', symbolSize: 6,
          itemStyle: { color: '#10b981' },
          lineStyle: { color: '#10b981', width: 2 },
          areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(16,185,129,0.12)' }, { offset: 1, color: 'rgba(16,185,129,0)' }] } },
        },
      ],
    });
  } catch (e) { console.error(e); } finally { trendLoading.value = false; }
};


const typeChartEl = ref<HTMLElement>();
const typeLoading = ref(false);
let typeChartInstance: echarts.ECharts | null = null;

const initTypeChart = async () => {
  typeLoading.value = true;
  try {
    const [apiRes, webRes] = await Promise.allSettled([
      get_api_script_result_list({ page: 1, pageSize: 500, search: {} }),
      get_web_result_list({ page: 1, pageSize: 500, search: {} }),
    ]);
    const apiCount = apiRes.status === 'fulfilled' ? (apiRes.value?.data?.content?.length || 0) : 0;
    const webCount = webRes.status === 'fulfilled' ? (webRes.value?.data?.content?.length || 0) : 0;
    const total = apiCount + webCount;

    const pieData = [
      { value: apiCount, name: `API测试 ${total > 0 ? Math.round(apiCount / total * 100) : 0}%`, itemStyle: { color: '#6366f1' } },
      { value: webCount, name: `UI测试 ${total > 0 ? Math.round(webCount / total * 100) : 0}%`, itemStyle: { color: '#0ea5e9' } },
    ].filter(d => d.value > 0);

    if (!pieData.length) {
      pieData.push({ value: 1, name: '暂无数据', itemStyle: { color: '#e5e7eb' } });
    }

    await nextTick();
    if (!typeChartEl.value) return;
    if (!typeChartInstance) typeChartInstance = echarts.init(typeChartEl.value);
    typeChartInstance.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}' },
      legend: { orient: 'vertical', right: 8, top: 'center', itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 11, color: '#6b7280' } },
      series: [{
        name: '测试类型', type: 'pie',
        radius: ['45%', '70%'],
        center: ['38%', '50%'],
        data: pieData,
        label: {
          show: true, position: 'center',
          formatter: () => `总数\n${total}`,
          fontSize: 13, fontWeight: 600, color: '#374151', lineHeight: 20,
        },
        labelLine: { show: false },
        emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.15)' } },
      }],
    });
  } catch (e) { console.error(e); } finally { typeLoading.value = false; }
};

const recentTab = ref<'api' | 'web'>('api');
const apiRecentList = ref<any[]>([]);
const webRecentList = ref<any[]>([]);

const currentRecentList = computed(() =>
  recentTab.value === 'api' ? apiRecentList.value : webRecentList.value
);


const mapApiStatus = (item: any) => {
  const s = item.status ?? 0;

  if (s === 1) return { statusTag: 'success', statusText: '通过' };
  if (s === 2) return { statusTag: 'danger',  statusText: '失败' };
  return { statusTag: 'warning', statusText: '运行中' };
};
const mapWebStatus = (item: any) => {
  const s = item.status ?? 0;
  if (s === 1) return { statusTag: 'success', statusText: '通过' };
  if (s === 2) return { statusTag: 'danger',  statusText: '失败' };
  return { statusTag: 'warning', statusText: '运行中' };
};

const loadRecentExecutions = async () => {
  try {
    const [apiRes, webRes] = await Promise.allSettled([
      get_api_script_result_list({ page: 1, pageSize: 20, search: {} }),
      get_web_result_list({ page: 1, pageSize: 20, search: {} }),
    ]);

    if (apiRes.status === 'fulfilled') {
      const list = apiRes.value?.data?.content || [];
      apiRecentList.value = list.map((item: any) => ({
        name: item.name || item.script_name || '未命名',
        username: item.username || '',
        time: formatTime(item.start_time || ''),
        ...mapApiStatus(item),
      }));
    }

    if (webRes.status === 'fulfilled') {
      const list = webRes.value?.data?.content || [];
      webRecentList.value = list.map((item: any) => ({
        name: item.task_name || item.name || '未命名',
        username: item.username || '',
        time: formatTime(item.start_time || ''),
        ...mapWebStatus(item),
      }));
    }
  } catch (e) { console.error(e); }
};


const recentScrollWrap = ref<HTMLElement>();
const recentScrollTrack = ref<HTMLElement>();
let scrollTimer: any = null;
let scrollPos = 0;
let scrollPaused = false;

const startScroll = () => {
  if (scrollTimer) clearInterval(scrollTimer);
  scrollPos = 0;
  if (recentScrollWrap.value) recentScrollWrap.value.scrollTop = 0;
  scrollTimer = setInterval(() => {
    if (scrollPaused || !recentScrollWrap.value || !recentScrollTrack.value) return;
    const wrap = recentScrollWrap.value;
    const track = recentScrollTrack.value;
    const halfHeight = track.scrollHeight / 2;
    if (halfHeight <= 0) return;
    scrollPos += 0.6;
    if (scrollPos >= halfHeight) scrollPos = 0;
    wrap.scrollTop = scrollPos;
  }, 16);
};

const stopScroll = () => {
  if (scrollTimer) { clearInterval(scrollTimer); scrollTimer = null; }
};

const switchRecentTab = async (tab: 'api' | 'web') => {
  recentTab.value = tab;

  stopScroll();
  scrollPos = 0;
  if (recentScrollWrap.value) recentScrollWrap.value.scrollTop = 0;
  await nextTick();
  if (currentRecentList.value.length > 0) startScroll();
};


const reviewStatsLoading = ref(false);
const reviewStats = ref({
  total_reviews: 0,
  pending_reviews: 0,
  in_progress_reviews: 0,
  completed_reviews: 0,
  cancelled_reviews: 0,
  status_distribution: {} as Record<string, number>,
  priority_distribution: {} as Record<string, number>,
});

const reviewStatusChartEl = ref<HTMLElement>();
const reviewPriorityChartEl = ref<HTMLElement>();
let reviewStatusChart: echarts.ECharts | null = null;
let reviewPriorityChart: echarts.ECharts | null = null;

const STATUS_MAP: Record<string, { label: string; color: string }> = {
  pending:     { label: '待开始', color: '#f59e0b' },
  in_progress: { label: '进行中', color: '#6366f1' },
  completed:   { label: '已完成', color: '#10b981' },
  cancelled:   { label: '已取消', color: '#ef4444' },
};
const PRIORITY_MAP: Record<string, { label: string; color: string }> = {
  low:    { label: '低',   color: '#10b981' },
  medium: { label: '中',   color: '#6366f1' },
  high:   { label: '高',   color: '#f59e0b' },
  urgent: { label: '紧急', color: '#ef4444' },
};

const initReviewCharts = () => {

  if (reviewStatusChartEl.value) {
    if (!reviewStatusChart) reviewStatusChart = echarts.init(reviewStatusChartEl.value);
    const dist = reviewStats.value.status_distribution || {};
    const pieData = Object.entries(dist)
      .filter(([, v]) => v > 0)
      .map(([k, v]) => ({
        name: STATUS_MAP[k]?.label ?? k,
        value: v,
        itemStyle: { color: STATUS_MAP[k]?.color ?? '#94a3b8' },
      }));
    if (!pieData.length) pieData.push({ name: '暂无数据', value: 1, itemStyle: { color: '#e5e7eb' } });
    reviewStatusChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: {
        orient: 'vertical', right: 4, top: 'center',
        itemWidth: 8, itemHeight: 8,
        textStyle: { fontSize: 11, color: '#6b7280' },
      },
      series: [{
        type: 'pie',
        radius: ['40%', '68%'],
        center: ['36%', '50%'],
        data: pieData,
        label: { show: false },
        emphasis: { itemStyle: { shadowBlur: 6, shadowColor: 'rgba(0,0,0,0.15)' } },
      }],
    });
  }

 
  if (reviewPriorityChartEl.value) {
    if (!reviewPriorityChart) reviewPriorityChart = echarts.init(reviewPriorityChartEl.value);
    const dist = reviewStats.value.priority_distribution || {};
    const order = ['low', 'medium', 'high', 'urgent'];
    const labels = order.map(k => PRIORITY_MAP[k]?.label ?? k);
    const values = order.map(k => dist[k] ?? 0);
    const colors = order.map(k => PRIORITY_MAP[k]?.color ?? '#94a3b8');
    reviewPriorityChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { top: 8, bottom: 28, left: 28, right: 8 },
      xAxis: {
        type: 'category', data: labels,
        axisLabel: { color: '#9ca3af', fontSize: 11 },
        axisLine: { lineStyle: { color: '#e5e7eb' } },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value', minInterval: 1,
        axisLabel: { color: '#9ca3af', fontSize: 10 },
        splitLine: { lineStyle: { color: '#f3f4f6' } },
      },
      series: [{
        type: 'bar', barMaxWidth: 32,
        data: values.map((v, i) => ({
          value: v,
          itemStyle: { color: colors[i], borderRadius: [4, 4, 0, 0] },
        })),
        label: { show: true, position: 'top', fontSize: 11, color: '#374151' },
      }],
    });
  }
};

const loadReviewStats = async () => {
  reviewStatsLoading.value = true;
  try {
    const res: any = await getReviewStatistics({});
    if (res?.data) {
      reviewStats.value = {
        total_reviews:       res.data.total_reviews       ?? 0,
        pending_reviews:     res.data.pending_reviews     ?? 0,
        in_progress_reviews: res.data.in_progress_reviews ?? 0,
        completed_reviews:   res.data.completed_reviews   ?? 0,
        cancelled_reviews:   res.data.cancelled_reviews   ?? 0,
        status_distribution:   res.data.status_distribution   ?? {},
        priority_distribution: res.data.priority_distribution ?? {},
      };
    }
  } catch (e) { console.error(e); } finally {
    reviewStatsLoading.value = false;
  }
};


const quickEntries = [
  { name: '需求管理', desc: '上传与管理需求', icon: Files, bgColor: '#ede9fe', iconColor: '#7c3aed', path: '/ai/intelligence/requirement-analysis' },
  { name: 'AI执行测试用例', desc: '智能体执行用例', icon: MagicStick, bgColor: '#d1fae5', iconColor: '#059669', path: '/ai/intelligence/browser-use/cases' },
  { name: '测试用例', desc: '管理测试用例', icon: List, bgColor: '#dbeafe', iconColor: '#2563eb', path: '/testing/testcases' },
  { name: 'API测试', desc: '接口自动化测试', icon: Connection, bgColor: '#fce7f3', iconColor: '#db2777', path: '/api-automation/index' },
  { name: 'UI测试', desc: 'UI自动化测试', icon: Monitor, bgColor: '#fef3c7', iconColor: '#d97706', path: '/web/automation' },
  { name: 'APP测试', desc: '移动端自动化', icon: Phone, bgColor: '#e0f2fe', iconColor: '#0284c7', path: '/testing/app-management/index?tab=device' },
  { name: '数据工厂', desc: '测试数据生成', icon: DataAnalysis, bgColor: '#fef9c3', iconColor: '#ca8a04', path: '/data-factory/tools' },
  { name: '用例生成', desc: 'AI生成用例', icon: TrendCharts, bgColor: '#f0fdf4', iconColor: '#16a34a', path: '/ai/intelligence/case-generation' },
];


const activeProjects = ref<any[]>([]);
const projectLoading = ref(false);

const loadProjectActivity = async () => {
  projectLoading.value = true;
  try {
    const r = await dashboardApi.getProjectActivity();
    if (r.code === 200) activeProjects.value = r.data?.active_projects || [];
  } catch {} finally { projectLoading.value = false; }
};

const notifications = ref<any[]>([]);
const unreadCount = ref(0);

const loadNotifications = async () => {
  try {
    const r = await dashboardApi.getRecentNotifications({ limit: 6 });
    if (r.code === 200) {
      notifications.value = r.data?.notifications || [];
      unreadCount.value = r.data?.unread_count || 0;
    }
  } catch {}
};

const getStatusTag = (s: string) => ({ success: 'success', failed: 'danger', pending: 'warning' }[s] || 'info');
const getStatusText = (s: string) => ({ success: '成功', failed: '失败', pending: '待处理' }[s] || '通知');


const dfStatsLoading = ref(false);
const dfStats = ref<{
  total_records: number;
  category_stats: Record<string, number>;
  recent_tools: Array<{ tool_name: string; tool_category_display: string; tool_scenario_display: string; created_at: string }>;
}>({
  total_records: 0,
  category_stats: {},
  recent_tools: [],
});

const dfBarChartEl = ref<HTMLElement>();
let dfBarChart: echarts.ECharts | null = null;

const initDfBarChart = () => {
  if (!dfBarChartEl.value) return;
  if (!dfBarChart) dfBarChart = echarts.init(dfBarChartEl.value);
  const stats = dfStats.value.category_stats || {};
  const entries = Object.entries(stats).sort((a, b) => b[1] - a[1]).slice(0, 5);
  const labels = entries.map(([k]) => dfCategoryNameMap.value[k] || k);
  const values = entries.map(([, v]) => v);
  const colors = ['#6366f1', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444'];
  dfBarChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 4, bottom: 20, left: 4, right: 4, containLabel: true },
    xAxis: {
      type: 'category', data: labels,
      axisLabel: { color: '#9ca3af', fontSize: 10, interval: 0, overflow: 'truncate', width: 48 },
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value', minInterval: 1,
      axisLabel: { color: '#9ca3af', fontSize: 10 },
      splitLine: { lineStyle: { color: '#f3f4f6' } },
    },
    series: [{
      type: 'bar', barMaxWidth: 24,
      data: values.map((v, i) => ({
        value: v,
        itemStyle: { color: colors[i % colors.length], borderRadius: [3, 3, 0, 0] },
      })),
      label: { show: true, position: 'top', fontSize: 10, color: '#6b7280' },
    }],
  });
};


const dfToolNameMap = ref<Record<string, string>>({});
const dfCategoryNameMap = ref<Record<string, string>>({});
const loadDfStats = async () => {
  dfStatsLoading.value = true;
  try {
    const { getStatistics, getToolCategories } = await import('/@/api/v1/testing/dataFactory');
    const [statsRes, catsRes] = await Promise.allSettled([getStatistics(), getToolCategories()]);

    if (catsRes.status === 'fulfilled' && catsRes.value?.data?.categories) {
      const nameMap: Record<string, string> = {};
      const catMap: Record<string, string> = {};
      for (const cat of catsRes.value.data.categories) {
        catMap[cat.category] = cat.name;
        for (const tool of (cat.tools || [])) {
          nameMap[tool.name] = tool.display_name || tool.name;
        }
      }
      dfToolNameMap.value = nameMap;
      dfCategoryNameMap.value = catMap;
    }

    if (statsRes.status === 'fulfilled' && statsRes.value?.data) {
      const d = statsRes.value.data;
      dfStats.value = {
        total_records:  d.total_records  ?? 0,
        category_stats: d.category_stats ?? {},
        recent_tools:   d.recent_tools   ?? [],
      };
    }
  } catch (e) { console.error(e); } finally {
    dfStatsLoading.value = false;
  }
};


const formatTime = (t: string) => {
  if (!t) return '';
  const d = new Date(t), now = new Date(), diff = now.getTime() - d.getTime();
  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
  return `${d.getMonth() + 1}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
};

const llmUsageLoading = ref(false);
const llmUsageDays = ref(7);
const llmUsageTab = ref<'overview' | 'daily' | 'category' | 'model'>('overview');
const llmUsageTabs = [
  { key: 'overview' as const, label: '总览' },
  { key: 'daily' as const, label: '按日期' },
  { key: 'category' as const, label: '按类别' },
  { key: 'model' as const, label: '按模型' },
];
const llmUsage = ref<LlmUsageStats>({
  tab: 'overview',
  days: 7,
  overview: {
    total_tokens: 0,
    cached_tokens: 0,
    uncached_tokens: 0,
    prompt_tokens: 0,
    completion_tokens: 0,
    cache_hit_rate: 0,
    request_count: 0,
    error_count: 0,
  },
  by_model: [],
  by_date: [],
  by_category: [],
  recent_requests: [],
});
const llmUsageDonutEl = ref<HTMLElement>();
const llmUsageDailyEl = ref<HTMLElement>();
const llmUsageCategoryEl = ref<HTMLElement>();
const llmUsageModelEl = ref<HTMLElement>();
let llmUsageDonutChart: echarts.ECharts | null = null;
let llmUsageDailyChart: echarts.ECharts | null = null;
let llmUsageCategoryChart: echarts.ECharts | null = null;
let llmUsageModelChart: echarts.ECharts | null = null;

const formatTokenCount = (n: number) => {
  const v = Number(n) || 0;
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(v >= 10_000 ? 0 : 1)}K`;
  return String(v);
};

const tokenShare = (n: number) => {
  const total = Number(llmUsage.value.overview.total_tokens) || 0;
  if (total <= 0) return 0;
  return Math.min(100, Math.round((Number(n) || 0) / total * 100));
};

const modelColor = (i: number) => {
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#84cc16'];
  return colors[i % colors.length];
};


const ensureLlmChart = (
  el: HTMLElement | undefined,
  chart: echarts.ECharts | null,
): echarts.ECharts | null => {
  if (!el) return null;
  const byDom = echarts.getInstanceByDom(el);
  if (byDom) return byDom;
  if (chart && !chart.isDisposed()) {
    try {
      chart.dispose();
    } catch {
      /* ignore */
    }
  }
  return echarts.init(el);
};

const renderActiveLlmCharts = async () => {
  await nextTick();
  // loading 结束后再等一帧，避免容器宽高为 0
  await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
  const tab = llmUsageTab.value;
  if (tab === 'overview') renderLlmUsageDonut();
  else if (tab === 'daily') renderLlmUsageDaily();
  else if (tab === 'category') renderLlmUsageCategory();
  else if (tab === 'model') renderLlmUsageModel();
  llmUsageDonutChart?.resize();
  llmUsageDailyChart?.resize();
  llmUsageCategoryChart?.resize();
  llmUsageModelChart?.resize();
};

const renderLlmUsageDonut = () => {
  llmUsageDonutChart = ensureLlmChart(llmUsageDonutEl.value, llmUsageDonutChart);
  if (!llmUsageDonutChart) return;
  const cached = llmUsage.value.overview.cached_tokens || 0;
  const uncached = llmUsage.value.overview.uncached_tokens || 0;
  const rate = llmUsage.value.overview.cache_hit_rate || 0;
  const hasData = cached + uncached > 0;
  llmUsageDonutChart.setOption({
    tooltip: {
      trigger: 'item',
      appendToBody: true,
      appendTo: typeof document !== 'undefined' ? document.body : undefined,
      confine: false,
      extraCssText: 'z-index: 9999; max-width: 280px; white-space: normal;',
      formatter: (params: any) => {
        const name = params?.name ?? '';
        const value = formatTokenCount(Number(params?.value) || 0);
        const percent = params?.percent ?? 0;
        return `${name}<br/>${value}（${percent}%）`;
      },
    },
    legend: {
      show: hasData,
      bottom: 0,
      left: 'center',
      icon: 'roundRect',
      itemWidth: 12,
      itemHeight: 10,
      itemGap: 18,
      selectedMode: true,
      textStyle: { color: '#6b7280', fontSize: 12 },
      data: ['未缓存消耗', '缓存命中'],
    },
    series: [
      {
        type: 'pie',
        radius: ['52%', '72%'],
        center: ['50%', '44%'],
        avoidLabelOverlap: true,
        label: {
          show: true,
          position: 'center',
          formatter: hasData ? `${rate}%\n命中率` : '暂无数据',
          fontSize: 16,
          fontWeight: 600,
          color: '#111827',
          lineHeight: 22,
        },
        data: hasData
          ? [
              { name: '未缓存消耗', value: uncached, itemStyle: { color: '#1e3a8a' } },
              { name: '缓存命中', value: cached, itemStyle: { color: '#93c5fd' } },
            ]
          : [{ name: '暂无', value: 1, itemStyle: { color: '#e5e7eb' } }],
      },
    ],
  }, true);
};

const renderLlmUsageDaily = () => {
  llmUsageDailyChart = ensureLlmChart(llmUsageDailyEl.value, llmUsageDailyChart);
  if (!llmUsageDailyChart) return;
  const dates = llmUsage.value.by_date.map((d) => d.date);
  const tokens = llmUsage.value.by_date.map((d) => d.total_tokens);
  const reqs = llmUsage.value.by_date.map((d) => d.request_count);
  llmUsageDailyChart.setOption({
    tooltip: { trigger: 'axis', appendToBody: true, confine: false },
    legend: { data: ['Token', '请求数'], bottom: 0 },
    grid: { top: 48, left: 56, right: 56, bottom: 40 },
    xAxis: { type: 'category', data: dates, axisLabel: { color: '#9ca3af' } },
    yAxis: [
      {
        type: 'value',
        name: 'Token',
        nameLocation: 'end',
        nameGap: 12,
        nameTextStyle: { color: '#6b7280', padding: [0, 0, 0, 0] },
        splitLine: { lineStyle: { color: '#f3f4f6' } },
        axisLabel: { color: '#9ca3af' },
      },
      {
        type: 'value',
        name: '请求',
        nameGap: 12,
        nameTextStyle: { color: '#6b7280' },
        minInterval: 1,
        splitLine: { show: false },
        axisLabel: { color: '#9ca3af' },
      },
    ],
    series: [
      { name: 'Token', type: 'bar', data: tokens, itemStyle: { color: '#6366f1', borderRadius: [4, 4, 0, 0] } },
      { name: '请求数', type: 'line', yAxisIndex: 1, data: reqs, smooth: true, itemStyle: { color: '#10b981' } },
    ],
  }, true);
};

const renderLlmUsageCategory = () => {
  llmUsageCategoryChart = ensureLlmChart(llmUsageCategoryEl.value, llmUsageCategoryChart);
  if (!llmUsageCategoryChart) return;
  const items = llmUsage.value.by_category.map((c) => ({
    name: c.category,
    value: c.total_tokens,
  }));
  const names = items.map((i) => i.name).reverse();
  const values = items.map((i) => i.value).reverse();
  llmUsageCategoryChart.setOption({
    tooltip: {
      trigger: 'axis',
      appendToBody: true,
      confine: false,
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params;
        return `${p?.name ?? ''}<br/>Token：${formatTokenCount(Number(p?.value) || 0)}`;
      },
    },
    grid: { top: 16, left: 12, right: 48, bottom: 12, containLabel: true },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#f3f4f6' } }, axisLabel: { color: '#9ca3af' } },
    yAxis: {
      type: 'category',
      data: names.length ? names : ['暂无'],
      axisLabel: { color: '#6b7280', width: 100, overflow: 'truncate' },
    },
    series: [
      {
        type: 'bar',
        data: (values.length ? values : [0]).map((v, idx) => ({
          value: v,
          itemStyle: { color: modelColor(Math.max(items.length - 1 - idx, 0)), borderRadius: [0, 4, 4, 0] },
        })),
        barMaxWidth: 22,
      },
    ],
  }, true);
};

const renderLlmUsageModel = () => {
  llmUsageModelChart = ensureLlmChart(llmUsageModelEl.value, llmUsageModelChart);
  if (!llmUsageModelChart) return;
  const items = llmUsage.value.by_model.map((m) => ({
    name: m.provider ? `${m.provider}/${m.model_name}` : m.model_name,
    value: m.total_tokens,
  }));
  const names = items.map((i) => i.name).reverse();
  const values = items.map((i) => i.value).reverse();
  llmUsageModelChart.setOption({
    tooltip: {
      trigger: 'axis',
      appendToBody: true,
      confine: false,
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params;
        return `${p?.name ?? ''}<br/>Token：${formatTokenCount(Number(p?.value) || 0)}`;
      },
    },
    grid: { top: 16, left: 12, right: 48, bottom: 12, containLabel: true },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#f3f4f6' } }, axisLabel: { color: '#9ca3af' } },
    yAxis: {
      type: 'category',
      data: names.length ? names : ['暂无'],
      axisLabel: { color: '#6b7280', width: 120, overflow: 'truncate' },
    },
    series: [
      {
        type: 'bar',
        data: (values.length ? values : [0]).map((v, idx) => ({
          value: v,
          itemStyle: { color: modelColor(Math.max(items.length - 1 - idx, 0)), borderRadius: [0, 4, 4, 0] },
        })),
        barMaxWidth: 22,
      },
    ],
  }, true);
};

const loadLlmUsage = async () => {
  llmUsageLoading.value = true;
  try {
    const r: any = await dashboardApi.getLlmUsage({ days: llmUsageDays.value, tab: llmUsageTab.value });
    if (r?.code === 200 && r.data) {
      llmUsage.value = {
        ...llmUsage.value,
        ...r.data,
        overview: { ...llmUsage.value.overview, ...(r.data.overview || {}) },
        by_model: r.data.by_model || [],
        by_date: r.data.by_date || [],
        by_category: r.data.by_category || [],
        recent_requests: r.data.recent_requests || [],
      };
    }
  } catch (e) {
    console.error(e);
  } finally {
    llmUsageLoading.value = false;
    await renderActiveLlmCharts();
  }
};

const switchLlmUsageTab = async (key: 'overview' | 'daily' | 'category' | 'model') => {
  llmUsageTab.value = key;
  await renderActiveLlmCharts();
};

const goTo = (path: string) => {
  if (!path) return;
  if (path.includes('?')) {
    const [p, qs] = path.split('?');
    const query: Record<string, string> = {};
    qs.split('&').forEach(pair => {
      const [k, v] = pair.split('=');
      if (k) query[k] = v ?? '';
    });
    router.push({ path: p, query });
  } else {
    router.push(path);
  }
};


const handleResize = () => {
  trendChartInstance?.resize();
  typeChartInstance?.resize();
  reviewStatusChart?.resize();
  reviewPriorityChart?.resize();
  dfBarChart?.resize();
  llmUsageDonutChart?.resize();
  llmUsageDailyChart?.resize();
  llmUsageCategoryChart?.resize();
  llmUsageModelChart?.resize();
};

onMounted(async () => {
  if (themeConfig.value.isLockScreen) {
    themeConfig.value.isLockScreen = false;
    themeConfig.value.lockScreenTime = 0;
  }

 
  updateTime();
  timer = setInterval(updateTime, 1000);


  await Promise.allSettled([
    (async () => {
      try { const r = await dashboardApi.getOverview(); if (r.code === 200 && r.data) coreStats.value = r.data; } catch {}
    })(),
    loadNotifications(),
    loadProjectActivity(),
    loadDfStats(),
    loadRecentExecutions(),
    loadReviewStats(),
    loadLlmUsage(),
  ]);

  await nextTick();
  setTimeout(() => {
    initTrendChart();
    initTypeChart();
    initReviewCharts();
    initDfBarChart();
    if (currentRecentList.value.length > 0) startScroll();
  }, 100);


  const wrap = recentScrollWrap.value;
  if (wrap) {
    wrap.addEventListener('mouseenter', () => { scrollPaused = true; });
    wrap.addEventListener('mouseleave', () => { scrollPaused = false; });
  }

  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
  stopScroll();
  window.removeEventListener('resize', handleResize);
  trendChartInstance?.dispose();
  typeChartInstance?.dispose();
  reviewStatusChart?.dispose();
  reviewPriorityChart?.dispose();
  dfBarChart?.dispose();
  llmUsageDonutChart?.dispose();
  llmUsageDailyChart?.dispose();
  llmUsageCategoryChart?.dispose();
  llmUsageModelChart?.dispose();
});
</script>

<style scoped lang="scss">
.home-page {
  background: var(--el-bg-color-page);
  min-height: 100vh;
}


.notice-bar {
  display: flex;
  align-items: center;
  background: var(--home-notice-bg, #eef2ff);
  border-bottom: 1px solid var(--home-notice-border, #c7d2fe);
  padding: 0 16px;
  height: 36px;
  overflow: hidden;
}
.notice-icon {
  font-size: 15px;
  color: #6366f1;
  margin-right: 10px;
  flex-shrink: 0;
}
.notice-track-wrap {
  flex: 1;
  overflow: hidden;
}
.notice-track {
  display: flex;
  width: max-content;
  animation: marquee 28s linear infinite;
}
.notice-text {
  font-size: 13px;
  color: #34d399;
  padding-right: 80px;
  white-space: nowrap;
}
@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}


.page-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}


.hero-section {
  background: var(--home-hero-bg, linear-gradient(135deg, #eef2ff 0%, #e0e7ff 50%, #dbeafe 100%));
  border-radius: 12px;
  padding: 20px 24px;
  border: 1px solid var(--home-hero-border, #c7d2fe);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.hero-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.hero-left {
  flex: 1;
  min-width: 0;
}
.hero-greeting {
  font-size: 22px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}
.hero-sub {
  font-size: 13px;
  color: #34d399;
  margin-bottom: 10px;
}
.hero-meta {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}
.hero-date, .hero-time {
  font-size: 12px;
  color: #6366f1;
  display: flex;
  align-items: center;
  gap: 4px;
}
.meta-icon {
  font-size: 12px;
}
.hero-right {
  flex-shrink: 0;
  margin-left: 20px;
}
.hero-avatar-wrap {
  position: relative;
}
.hero-avatar {
  border: 3px solid #a5b4fc;
  box-shadow: 0 0 0 5px rgba(99, 102, 241, 0.1);
}
.hero-avatar-ring {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 2px dashed #a5b4fc;
  animation: spin 12s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}


.stat-row {
  margin: 0 !important;
}
.stat-card {
  background: var(--el-bg-color);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  border: 1px solid var(--el-border-color-lighter);
  transition: all 0.2s;
  margin-bottom: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  }

  &.no-click {
    cursor: default;
    &:hover {
      transform: none;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
    }
  }
}
.stat-card-left {
  flex: 1;
  min-width: 0;
}
.stat-val {
  font-size: 26px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1.1;
  margin-bottom: 4px;
}
.stat-label {
  font-size: 13px;
  color: var(--el-text-color-regular);
  margin-bottom: 4px;
}
.stat-change {
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 2px;

  &.up { color: #10b981; }
  &.down { color: #ef4444; }
  &.neutral { color: var(--el-text-color-secondary); }
}
.stat-card-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-left: 12px;
}


.panel {
  background: var(--el-bg-color);
  border-radius: 12px;
  border: 1px solid var(--el-border-color-lighter);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}
.panel-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.more-link {
  font-size: 12px;
  color: #6366f1;
  cursor: pointer;
  &:hover { text-decoration: underline; }
}


.mid-row {
  margin: 0 !important;
  align-items: stretch !important;
}
.chart-wrap {
  height: 240px;
  padding: 8px 4px;
}
.mid-row .panel {
  height: 301px;
  display: flex;
  flex-direction: column;
}
.mid-row .chart-wrap {
  flex: 1;
  height: auto;
  min-height: 0;
}


.recent-panel {

  height: 301px;
  display: flex;
  flex-direction: column;
}
.recent-tab-hd {
  padding: 0 16px;
  height: 45px;
  flex-shrink: 0;
}
.recent-tabs {
  display: flex;
  gap: 0;
  background: var(--el-fill-color);
  border-radius: 8px;
  padding: 3px;
}
.recent-tab {
  padding: 4px 14px;
  font-size: 12px;
  font-weight: 500;
  color: var(--el-text-color-regular);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.18s;
  white-space: nowrap;
  user-select: none;

  &.active {
    background: var(--el-bg-color);
    color: #6366f1;
    font-weight: 600;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  }
  &:not(.active):hover {
    color: var(--el-text-color-primary);
  }
}
.recent-scroll-wrap {
  flex: 1;
  overflow: hidden;
  position: relative;
}
.recent-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  transition: background 0.15s;
  gap: 8px;
  cursor: default;

  &:hover { background: var(--el-fill-color-lighter); }
}
.recent-item-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}
.recent-type-icon {
  font-size: 16px;
  flex-shrink: 0;
}
.recent-item-info {
  flex: 1;
  min-width: 0;
}
.recent-item-name {
  font-size: 13px;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.recent-item-meta {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
}


.quick-panel {
  .panel-hd {
    border-bottom: 1px solid var(--el-border-color-lighter);
  }
}
.quick-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 0;
  padding: 12px 8px;

  @media (max-width: 1200px) { grid-template-columns: repeat(4, 1fr); }
  @media (max-width: 768px) { grid-template-columns: repeat(2, 1fr); }
}
.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s;
  text-align: center;

  &:hover {
    background: #f5f7ff;
    .quick-item-name { color: #6366f1; }
  }
}
.quick-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}
.quick-item-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  transition: color 0.15s;
}
.quick-item-desc {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
}


.bottom-row {
  margin: 0 !important;
}

.bottom-row .panel {
  min-height: 240px;
}


.project-list {
  padding: 4px 0;
}
.project-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  transition: background 0.15s;

  &:hover { background: var(--el-fill-color-lighter); }
}
.project-rank {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--el-fill-color);
  color: var(--el-text-color-regular);
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.rank-gold {
    background: linear-gradient(135deg, #f59e0b, #fbbf24);
    color: #fff;
  }
}
.project-info {
  flex: 1;
  min-width: 0;
}
.project-name {
  font-size: 13px;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.project-meta {
  margin-top: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}


.todo-list {
  padding: 4px 0;
}
.todo-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  transition: background 0.15s;

  &:hover { background: var(--el-fill-color-lighter); }
}
.todo-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;

  &.dot-success { background: #10b981; }
  &.dot-failed { background: #ef4444; }
  &.dot-pending { background: #f59e0b; }
  &.dot- { background: #9ca3af; }
}
.todo-content {
  flex: 1;
  min-width: 0;
}
.todo-title {
  font-size: 13px;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.todo-time {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
}


.df-panel {
  min-height: 240px;
}
.df-body {
  padding: 12px 16px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.df-total-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.df-total-block {
  flex-shrink: 0;
  text-align: center;
  background: #f5f3ff;
  border-radius: 10px;
  padding: 10px 14px;
  min-width: 72px;
}
.df-total-val {
  font-size: 26px;
  font-weight: 700;
  color: #6366f1;
  line-height: 1;
  margin-bottom: 4px;
}
.df-total-label {
  font-size: 10px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
}
.df-bar-chart {
  flex: 1;
  height: 80px;
  min-width: 0;
}
.df-recent-title {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  padding-left: 2px;
}
.df-recent-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.df-recent-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 4px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;

  &:hover { background: #f5f3ff; }
}
.df-recent-icon {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  background: #ede9fe;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.df-recent-info {
  flex: 1;
  min-width: 0;
}
.df-recent-name {
  font-size: 12px;
  color: var(--el-text-color-primary);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.df-recent-meta {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  margin-top: 1px;
}


:deep(.el-progress-bar__outer) {
  background: var(--el-fill-color);
}
:deep(.el-empty__description p) {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

@media (max-width: 768px) {
  .hero-section {
    padding: 16px;
  }
  .hero-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .hero-right {
    margin-left: 0;
    align-self: flex-end;
  }
  .hero-greeting {
    font-size: 18px;
  }
  .stat-card {
    padding: 12px;
  }
  .stat-val {
    font-size: 22px;
  }
  .stat-card-icon-wrap {
    width: 40px;
    height: 40px;
  }
  .quick-grid {
    padding: 8px 4px;
  }
  .quick-item {
    padding: 8px 4px;
  }
  .quick-icon-wrap {
    width: 40px;
    height: 40px;
  }
  .llm-usage-body {
    padding: 12px;
  }
  .llm-usage-donut-wrap,
  .llm-usage-donut {
    width: 200px;
    height: 180px;
  }
  .llm-usage-total {
    font-size: 28px;
  }
  .llm-usage-metrics {
    gap: 16px;
  }
  .llm-metric-val {
    font-size: 18px;
  }
  .review-stats-body {
    flex-direction: column;
    padding: 12px;
  }
  .review-num-grid {
    width: 100%;
    grid-template-columns: repeat(2, 1fr);
  }
  .df-total-row {
    flex-direction: column;
    align-items: stretch;
  }
  .df-total-block {
    min-width: unset;
  }
}


.llm-usage-panel {
  overflow: visible;
  .llm-usage-hd-left {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .llm-usage-hint {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
  .llm-usage-hd-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}
.llm-usage-tabs {
  display: flex;
  gap: 4px;
  padding: 0 16px 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.llm-usage-tab {
  padding: 6px 14px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  border-radius: 6px;
  cursor: pointer;
  &.active {
    color: #1d4ed8;
    background: #eff6ff;
    font-weight: 600;
  }
}
.llm-usage-body {
  padding: 16px;
  min-height: 280px;
}
.llm-usage-overview {
  display: flex;
  gap: 24px;
  align-items: center;
  margin-bottom: 20px;
}
.llm-usage-donut-wrap {
  width: 240px;
  flex-shrink: 0;
  overflow: visible;
}
.llm-usage-donut {
  width: 240px;
  height: 220px;
}
.llm-usage-overview-right {
  flex: 1;
  min-width: 0;
}
.llm-usage-kicker {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}
.llm-usage-total {
  font-size: 36px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1.2;
}
.llm-usage-sub {
  margin-top: 6px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.llm-usage-metrics {
  display: flex;
  gap: 28px;
  margin-top: 18px;
}
.llm-metric-val {
  font-size: 22px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.llm-metric-label {
  margin-top: 2px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.llm-usage-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  border-top: 1px solid var(--el-border-color-lighter);
  padding-top: 16px;
}
.llm-usage-col {
  min-width: 0;
}
.llm-col-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--el-text-color-primary);
}
.llm-usage-scroll {
  padding-right: 4px;
  &.is-scrollable {
    max-height: 186px; /* 约 3 条，超出内部滚动 */
    overflow-y: auto;
  }
  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: #d1d5db;
    border-radius: 3px;
  }
}
.llm-model-row,
.llm-req-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--el-border-color-extra-light);
}
.llm-model-left {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-width: 0;
  flex: 1;
}
.llm-model-text {
  min-width: 0;
  flex: 1;
}
.llm-model-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}
.llm-model-name,
.llm-req-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.llm-model-meta,
.llm-req-meta {
  margin-top: 2px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.llm-model-bar {
  margin-top: 6px;
  height: 6px;
  border-radius: 999px;
  background: #f3f4f6;
  overflow: hidden;
}
.llm-model-bar-fill {
  height: 100%;
  border-radius: 999px;
  min-width: 0;
  transition: width 0.2s ease;
}
.llm-model-tokens {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  flex-shrink: 0;
}
.llm-req-row {
  display: block;
}
.llm-req-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.llm-usage-chart {
  width: 100%;
  height: 300px;
}
.llm-usage-tab-grid {
  display: grid;
  grid-template-columns: minmax(280px, 1.1fr) minmax(280px, 1fr);
  gap: 20px;
  align-items: stretch;
}
.llm-usage-hbar {
  height: 280px;
  min-height: 280px;
}
.llm-usage-tab-list {
  min-width: 0;
  display: flex;
  flex-direction: column;
}
@media (max-width: 900px) {
  .llm-usage-overview {
    flex-direction: column;
    align-items: stretch;
  }
  .llm-usage-split,
  .llm-usage-tab-grid {
    grid-template-columns: 1fr;
  }
}

.review-stats-panel {
  .panel-hd {
    .panel-title {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .title-icon {
      color: #6366f1;
      font-size: 15px;
    }
  }
}
.review-stats-body {
  display: flex;
  align-items: stretch;
  gap: 0;
  padding: 14px 16px;
  min-height: 130px;
}


.review-num-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  width: 280px;
  flex-shrink: 0;
  align-content: center;

  @media (max-width: 900px) {
    width: 100%;
    grid-template-columns: repeat(2, 1fr);
  }
}
.review-num-card {
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  padding: 12px 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.18s;

  &:hover {
    border-color: #6366f1;
    background: #f5f3ff;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
  }
}
.review-num-val {
  font-size: 24px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1;
  margin-bottom: 5px;
}
.review-num-label {
  font-size: 11px;
  color: var(--el-text-color-secondary);
}
.pending-card .review-num-val  { color: #f59e0b; }
.progress-card .review-num-val { color: #6366f1; }
.done-card .review-num-val     { color: #10b981; }


.review-charts {
  flex: 1;
  display: flex;
  gap: 0;
  min-width: 0;
  padding-left: 16px;
  border-left: 1px solid var(--el-border-color-lighter);
  margin-left: 16px;

  @media (max-width: 900px) {
    display: none;
  }
}
.review-chart-item {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.review-chart-title {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
  padding-left: 2px;
}
.review-chart-el {
  flex: 1;
  min-height: 100px;
}


:deep(.el-progress-bar__outer) {
  background: var(--el-fill-color);
}
:deep(.el-empty__description p) {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

@media (max-width: 768px) {
  .hero-section {
    padding: 16px;
  }
  .hero-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .hero-right {
    margin-left: 0;
    align-self: flex-end;
  }
  .hero-greeting {
    font-size: 18px;
  }
  .stat-card {
    padding: 12px;
  }
  .stat-val {
    font-size: 22px;
  }
  .stat-card-icon-wrap {
    width: 40px;
    height: 40px;
  }
  .quick-grid {
    padding: 8px 4px;
  }
  .quick-item {
    padding: 8px 4px;
  }
  .quick-icon-wrap {
    width: 40px;
    height: 40px;
  }
  .llm-usage-body {
    padding: 12px;
  }
  .llm-usage-donut-wrap,
  .llm-usage-donut {
    width: 200px;
    height: 180px;
  }
  .llm-usage-total {
    font-size: 28px;
  }
  .llm-usage-metrics {
    gap: 16px;
  }
  .llm-metric-val {
    font-size: 18px;
  }
  .review-stats-body {
    flex-direction: column;
    padding: 12px;
  }
  .review-num-grid {
    width: 100%;
    grid-template-columns: repeat(2, 1fr);
  }
  .df-total-row {
    flex-direction: column;
    align-items: stretch;
  }
  .df-total-block {
    min-width: unset;
  }
}


[data-theme='dark'] {

  --home-notice-bg: rgba(99, 102, 241, 0.12);
  --home-notice-border: rgba(99, 102, 241, 0.25);


  --home-hero-bg: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(79,70,229,0.12) 50%, rgba(59,130,246,0.1) 100%);
  --home-hero-border: rgba(99, 102, 241, 0.2);

  .home-page {
    background: var(--el-bg-color-page);
  }


  .notice-text { color: #6ee7b7; }
  .notice-icon { color: #6ee7b7; }


  .hero-sub { color: #6ee7b7; }
  .hero-date, .hero-time { color: #818cf8; }
  .hero-avatar { border-color: rgba(165, 180, 252, 0.5); }
  .hero-avatar-ring { border-color: rgba(165, 180, 252, 0.3); }


  .stat-card {
    box-shadow: none;
    &:hover { box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3); }
    &.no-click:hover { box-shadow: none; }
  }


  .panel { box-shadow: none; }


  .recent-tab {
    color: var(--el-text-color-secondary);
    &.active {
      background: var(--el-bg-color);
      color: #818cf8;
    }
    &:not(.active):hover { color: var(--el-text-color-primary); }
  }

  
  .recent-item:hover,
  .project-item:hover,
  .todo-item:hover { background: var(--el-fill-color-light); }


  .quick-item:hover {
    background: var(--el-fill-color-light);
    .quick-item-name { color: #818cf8; }
  }


  .review-num-card {
    &:hover {
      border-color: #6366f1;
      background: rgba(99, 102, 241, 0.1);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
  }
  .review-num-val { color: var(--el-text-color-primary); }


  .df-total-block { background: rgba(99, 102, 241, 0.12); }
  .df-recent-icon { background: rgba(99, 102, 241, 0.15); }
  .df-recent-item:hover { background: rgba(99, 102, 241, 0.08); }


  .project-rank {
    background: var(--el-fill-color);
    color: var(--el-text-color-secondary);
  }
}
</style>
