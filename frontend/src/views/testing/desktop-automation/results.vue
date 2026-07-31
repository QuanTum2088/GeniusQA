<template>
  <div class="page-container">
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchParams.search">
        <el-form-item label="任务名称">
          <el-input v-model="searchParams.search.task_name" placeholder="请输入任务名称" clearable style="width:220px" />
        </el-form-item>
        <el-form-item label="执行框架">
          <el-select v-model="searchParams.search.framework" clearable placeholder="全部" style="width:140px">
            <el-option v-for="f in frameworks" :key="f" :label="f" :value="f" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属项目">
          <el-select v-model="searchParams.search.project_id" clearable placeholder="全部项目" style="width:160px">
            <el-option v-for="p in projectList" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">
            <el-icon><ele-Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><ele-Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top:8px">
      <el-table v-loading="loading" :data="tableList" border stripe empty-text="暂无数据">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column label="任务名称" prop="task_name" min-width="160" show-overflow-tooltip />
        <el-table-column label="执行框架" prop="framework" width="130" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="light">{{ row.framework }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="执行状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.script_status)" size="small">
              {{ getStatusText(row.script_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="通过率" width="160" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="getPercent(row.script_status)"
              :color="[{color:'#f56c6c',percentage:99.99},{color:'#67c23a',percentage:100}]"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column label="开始时间" prop="start_time" width="170" align="center" />
        <el-table-column label="结束时间" prop="end_time" width="170" align="center">
          <template #default="{ row }">{{ row.end_time || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="success" size="small" @click="viewDetail(row)">详情</el-button>
              <el-button type="danger" size="small" @click="deleteResult(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top:12px">
        <el-pagination
          v-show="total > 0"
          background
          v-model:current-page="searchParams.page"
          v-model:page-size="searchParams.pageSize"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="loadList"
          @current-change="loadList"
        />
      </div>
    </el-card>

    <!-- 详情抽屉 -->
    <el-drawer v-model="showDetail" title="执行详情" direction="rtl" size="520px" destroy-on-close>
      <template #header>
        <div>
          <div style="font-size:15px;font-weight:600">{{ detailRow?.task_name }}</div>
          <div style="font-size:12px;color:var(--el-text-color-secondary);margin-top:2px">
            框架：{{ detailRow?.framework }} · {{ detailRow?.start_time }}
          </div>
        </div>
      </template>

      <!-- 汇总 -->
      <div class="result-summary" v-if="detailSummary">
        <div class="summary-item"><div class="sv">{{ detailSummary.total }}</div><div class="sl">总步骤</div></div>
        <div class="summary-item pass"><div class="sv">{{ detailSummary.passed }}</div><div class="sl">通过</div></div>
        <div class="summary-item fail"><div class="sv">{{ detailSummary.fail }}</div><div class="sl">失败</div></div>
        <div class="summary-item rate"><div class="sv">{{ detailSummary.percent }}%</div><div class="sl">通过率</div></div>
      </div>
      <el-progress v-if="detailSummary"
        :percentage="detailSummary.percent"
        :color="[{color:'#f56c6c',percentage:99.99},{color:'#67c23a',percentage:100}]"
        :stroke-width="8" :show-text="false" style="margin-bottom:16px" />

      <!-- 步骤时间线 -->
      <div v-loading="detailLoading">
        <el-timeline>
          <el-timeline-item
            v-for="(item, i) in detailSteps"
            :key="i"
            :type="item.status === 1 ? 'success' : item.status === 0 ? 'danger' : 'primary'"
            :timestamp="item.create_time"
            placement="top"
          >
            <div class="step-result-header">
              <el-icon :style="{ color: item.status === 1 ? '#67c23a' : '#f56c6c' }">
                <Check v-if="item.status === 1" /><Close v-else />
              </el-icon>
              <span style="font-size:13px;font-weight:500;margin-left:4px">{{ item.name }}</span>
            </div>
            <div v-if="item.log" style="font-size:12px;color:var(--el-text-color-secondary);margin-top:4px;padding-left:20px">
              {{ item.log }}
            </div>
            <div v-if="item.before_img || item.after_img" style="display:flex;margin-top:8px;padding-left:20px;gap:8px">
              <el-image v-if="item.before_img" :src="item.before_img" :preview-src-list="[item.before_img]"
                fit="cover" style="width:100px;height:70px;border-radius:4px" />
              <el-image v-if="item.after_img" :src="item.after_img" :preview-src-list="[item.after_img]"
                fit="cover" style="width:100px;height:70px;border-radius:4px" />
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Check, Close } from '@element-plus/icons-vue';
import { useDesktopAutomationApi } from '/@/api/v1/testing/desktopAutomation';
import { getProjectList } from '/@/api/v1/projects/project';

const api = useDesktopAutomationApi();

const loading = ref(false);
const tableList = ref<any[]>([]);
const total = ref(0);
const frameworks = ref(['pywinauto', 'pyautogui', 'winappdriver']);
const projectList = ref<any[]>([]);

const searchParams = ref({
  page: 1, pageSize: 10,
  search: { task_name: '', framework: '', project_id: null as number | null },
});

const loadProjects = async () => {
  try {
    const res: any = await getProjectList({ page: 1, page_size: 100 });
    projectList.value = res.data?.content || res.data?.items || res.data || [];
  } catch { projectList.value = []; }
};

const loadList = async () => {
  loading.value = true;
  try {
    const res: any = await api.result_list(searchParams.value);
    tableList.value = res.data?.content || [];
    total.value = res.data?.total || 0;
  } finally {
    loading.value = false;
  }
};

const resetSearch = () => {
  searchParams.value = { page: 1, pageSize: 10, search: { task_name: '', framework: '', project_id: null } };
  loadList();
};

const getStatusType = (ss: any[]) => {
  if (!ss?.length) return 'info';
  const last = ss[ss.length - 1];
  if (last?.stopped) return 'warning';
  if (last?.status === 'finished') return last.fail > 0 ? 'danger' : 'success';
  return 'warning';
};
const getStatusText = (ss: any[]) => {
  if (!ss?.length) return '未知';
  const last = ss[ss.length - 1];
  if (last?.stopped) return '已停止';
  if (last?.status === 'finished') return last.fail > 0 ? '有失败' : '全部通过';
  return '执行中';
};
const getPercent = (ss: any[]) => {
  if (!ss?.length) return 0;
  return ss[ss.length - 1]?.percent || 0;
};

// ── 详情 ──────────────────────────────────────────────────
const showDetail = ref(false);
const detailRow = ref<any>(null);
const detailLoading = ref(false);
const detailSteps = ref<any[]>([]);
const detailSummary = ref<any>(null);

const viewDetail = async (row: any) => {
  detailRow.value = row;
  showDetail.value = true;
  detailLoading.value = true;
  try {
    const res: any = await api.result_detail({ result_id: row.result_id });
    detailSteps.value = res.data || [];
    const steps = detailSteps.value.filter((s: any) => !['开始执行', '执行结束', '执行异常'].includes(s.name));
    const passed = steps.filter((s: any) => s.status === 1).length;
    const fail = steps.filter((s: any) => s.status === 0).length;
    const total = steps.length;
    detailSummary.value = { total, passed, fail, percent: total > 0 ? Math.round(passed / total * 100) : 0 };
  } finally {
    detailLoading.value = false;
  }
};

const deleteResult = (row: any) => {
  ElMessageBox.confirm(`确认删除执行记录「${row.task_name}」？此操作不可恢复`, '提示', { type: 'warning' })
    .then(async () => {
      await api.del_result({ result_id: row.result_id });
      ElMessage.success('删除成功');
      await loadList();
    });
};

onMounted(() => {
  loadProjects();
  loadList();
});
</script>

<style scoped lang="scss">
.page-container { padding: 16px; }
.table-actions {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}
.table-actions :deep(.el-button + .el-button) { margin-left: 0; }
.search-card { margin-bottom: 0; }
.result-summary {
  display: flex; gap: 12px; margin-bottom: 14px;
  .summary-item {
    flex: 1; text-align: center; background: var(--el-fill-color-light);
    border-radius: 8px; padding: 10px 6px;
    .sv { font-size: 22px; font-weight: 700; color: var(--el-text-color-primary); }
    .sl { font-size: 11px; color: var(--el-text-color-secondary); margin-top: 2px; }
    &.pass .sv { color: #67c23a; }
    &.fail .sv { color: #f56c6c; }
    &.rate .sv { color: var(--el-color-primary); }
  }
}
.step-result-header { display: flex; align-items: center; }
</style>
