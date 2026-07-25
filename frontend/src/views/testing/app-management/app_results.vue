<template>
  <div class="result-list-container">
    <el-card shadow="hover" :body-style="{ paddingBottom: '0' }">
      <el-form :inline="true" :model="searchParams.search">
        <el-form-item label="任务名称">
          <el-input
            v-model="searchParams.search.task_name__icontaints"
            placeholder="请输入任务名称"
            clearable
            style="width: 220px"
            @keyup.enter="get_result_list_data"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="get_result_list_data">搜索</el-button>
          <el-button icon="Refresh" @click="reset_search">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" style="margin-top: 8px">
      <el-table
        v-loading="loading"
        :data="table_data"
        border
        stripe
        empty-text="暂无数据"
        :fit="true"
        table-layout="auto"
        style="width: 100%"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="task_name" label="任务名称" min-width="120" show-overflow-tooltip />
        <el-table-column prop="device_list" label="设备详情" width="120" align="center">
          <template #default="{ row }">
            <el-popover placement="top" :width="350" trigger="hover">
              <div>
                <el-steps direction="vertical" :active="99">
                  <el-step v-for="device in row.device_list" :key="device.deviceid">
                    <template #title>
                      <span>{{ device.name }}</span>
                      <span style="float: right">{{ '(系统：' + device.os_type + ' ' + device.version + ')' }}</span>
                    </template>
                  </el-step>
                </el-steps>
              </div>
              <template #reference>
                <el-button type="primary" size="small" plain>设备详情</el-button>
              </template>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column label="任务状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMeta(row.status).tagType">{{ statusMeta(row.status).text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="通过率" width="160" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.percent || 0" :color="customColors" :stroke-width="10" />
          </template>
        </el-table-column>
        <el-table-column prop="username" label="执行人" width="100" align="center" />
        <el-table-column label="开始时间" width="170" align="center">
          <template #default="{ row }">
            {{ row.start_time ? String(row.start_time).replace('T', ' ') : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="结束时间" width="170" align="center">
          <template #default="{ row }">
            {{ row.end_time ? String(row.end_time).replace('T', ' ') : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" align="center" fixed="right">
          <template #default="{ row }">
            <span class="action-cell">
              <el-button
                v-if="statusMeta(row.status).isRunning"
                type="danger"
                size="small"
                @click="stop_run(row.result_id)"
              >停止</el-button>

              <el-button type="primary" size="small" @click="view_result(row)">查看详情</el-button>

              <el-button
                v-if="statusMeta(row.status).canViewReport"
                type="primary"
                size="small"
                plain
                @click="view_report(row.result_id)"
              >查看报告</el-button>

              <el-button
                v-if="statusMeta(row.status).canRerun"
                type="info"
                size="small"
                @click="rerun(row)"
              >重跑</el-button>

              <el-button
                v-else
                type="info"
                size="small"
                disabled
                title="执行中可先停止"
              >重跑</el-button>

              <el-button type="danger" size="small" @click="del_run(row)">删除</el-button>
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-show="total > 0"
          background
          v-model:current-page="searchParams.currentPage"
          v-model:page-size="searchParams.pageSize"
          :page-sizes="[10, 25, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="get_result_list_data"
          @current-change="get_result_list_data"
        />
      </div>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { useAppManagementApi } from "/@/api/v1/testing/appManagement";
import { getExecutionStatusMeta } from "/@/utils/executionStatus";

const route = useRoute();
const router = useRouter();

const { app_result_list, run_scripts, stop_process, del_app_result } = useAppManagementApi();

const table_data = ref<any[]>([]);
const loading = ref(false);
const customColors = ref<any>([
  { color: "#ea2e2e", percentage: 99.99 },
  { color: "#81d36f", percentage: 100 }
]);

const searchParams = ref({
  currentPage: 1,
  pageSize: 10,
  search: {
    task_name__icontaints: ""
  }
});

const total = ref<number>(0);
const statusMeta = (status: number) => getExecutionStatusMeta(status);

const get_result_list_data = async () => {
  loading.value = true;
  try {
    const res: any = await app_result_list(searchParams.value);
    const raw = res?.data;
    const list = Array.isArray(raw?.content) ? raw.content : (Array.isArray(raw) ? raw : []);
    table_data.value = list.map((r: any) => ({
      ...r,
      status: r.status ?? (r.end_time ? 1 : 0),
    }));
    total.value = typeof raw?.total === 'number' ? raw.total : list.length;
  } catch (error) {
    console.error('获取结果列表失败:', error);
    table_data.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

const reset_search = () => {
  searchParams.value.currentPage = 1;
  searchParams.value.pageSize = 10;
  searchParams.value.search.task_name__icontaints = '';
  get_result_list_data();
};

const view_report = async (result_id: any) => {
  router.push({
    path: '/app_report',
    query: { result_id: result_id }
  });
};

const view_result = async (data: any) => {
  const basePath = route.path.replace(/\/results\/?$/, "/automation");
  router.push({ path: basePath, query: { result_id: data.result_id } });
};

const stop_run = async (result_id: string) => {
  try {
    await stop_process({ result_id });
    ElMessage.success('已停止执行');
    await get_result_list_data();
  } catch (e: any) {
    ElMessage.error(e?.message || '停止失败');
  }
};

const rerun = async (row: any) => {
  try {
    if (!row?.script_list?.length || !row?.device_list?.length) {
      ElMessage.warning('无法重跑：缺少脚本或设备信息');
      return;
    }
    await run_scripts({
      task_name: row.task_name,
      device_list: row.device_list,
      script_list: row.script_list,
      result_id: Date.now(),
    });
    ElMessage.success('已发起重跑');
    await get_result_list_data();
  } catch (e: any) {
    ElMessage.error(e?.message || '重跑失败');
  }
};

const del_run = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      '确认删除该执行记录？若正在执行将先停止进程再删除，该操作不可恢复。',
      '提示',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      },
    );
    await del_app_result({ result_id: String(row.result_id) });
    ElMessage.success('删除成功');
    await get_result_list_data();
  } catch (e: any) {
    if (e === 'cancel' || e === 'close') return;
    ElMessage.error(e?.message || '删除失败');
  }
};

onMounted(() => {
  get_result_list_data();
});
</script>

<style scoped>
.result-list-container {
  padding: 10px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.action-cell {
  white-space: nowrap;
}
</style>
