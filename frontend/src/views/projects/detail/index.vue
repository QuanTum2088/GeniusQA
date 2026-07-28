<template>
  <div class="project-detail-container">
    <!-- 页面头部 -->
    <el-page-header @back="handleBack" style="margin-bottom: 20px">
      <template #content>
        <span class="page-title">项目详情</span>
      </template>
    </el-page-header>

    <el-row :gutter="20" v-loading="loading">
      <!-- 左侧：项目基本信息 -->
      <el-col :span="16">
        <!-- 项目概览 -->
        <el-card shadow="hover" style="margin-bottom: 20px">
          <template #header>
            <div class="card-header">
              <span>项目概览</span>
              <el-button
                type="primary"
                size="small"
                @click="handleEdit"
                v-auth="'projects:list:edit'"
              >
                <el-icon><ele-Edit /></el-icon>
                编辑项目
              </el-button>
            </div>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="项目名称">
              {{ projectInfo.name }}
            </el-descriptions-item>
            <el-descriptions-item label="项目状态">
              <el-tag :type="getStatusType(projectInfo.status)">
                {{ getStatusText(projectInfo.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="项目负责人" :span="2">
              {{ projectInfo.owner_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="项目描述" :span="2">
              {{ projectInfo.description || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="本机工作目录" :span="2">
              {{ projectInfo.workspace_path || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDateTime(projectInfo.creation_date) }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间">
              {{ formatDateTime(projectInfo.updation_date) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 项目统计 -->
        <el-card shadow="hover" style="margin-bottom: 20px">
          <template #header>
            <span>项目统计</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-icon" style="background: #ecf5ff; color: #409eff;">
                  <el-icon :size="32"><ele-User /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ projectInfo.member_count || 0 }}</div>
                  <div class="stat-label">项目成员</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-icon" style="background: #f0f9ff; color: #67c23a;">
                  <el-icon :size="32"><ele-Setting /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ projectInfo.environment_count || 0 }}</div>
                  <div class="stat-label">项目环境</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-icon" style="background: #fef0f0; color: #f56c6c;">
                  <el-icon :size="32"><ele-Document /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">0</div>
                  <div class="stat-label">测试用例</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 项目成员 -->
        <el-card shadow="hover" style="margin-bottom: 20px">
          <template #header>
            <div class="card-header">
              <span>项目成员</span>
              <el-button
                type="primary"
                size="small"
                @click="handleManageMembers"
                v-auth="'projects:member:manage'"
              >
                <el-icon><ele-Plus /></el-icon>
                管理成员
              </el-button>
            </div>
          </template>
          
          <el-table :data="memberList" style="width: 100%">
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="nickname" label="昵称" width="120" />
            <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
            <el-table-column prop="role" label="角色" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="getRoleType(row.role)" size="small">
                  {{ getRoleText(row.role) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="creation_date" label="加入时间" width="180" align="center">
              <template #default="{ row }">
                {{ formatDateTime(row.creation_date) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 项目环境 -->
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>项目环境</span>
              <el-button
                type="primary"
                size="small"
                @click="handleManageEnvironments"
                v-auth="'projects:environment:manage'"
              >
                <el-icon><ele-Plus /></el-icon>
                管理环境
              </el-button>
            </div>
          </template>
          
          <el-table :data="environmentList" style="width: 100%">
            <el-table-column prop="name" label="环境名称" width="150" />
            <el-table-column prop="base_url" label="基础URL" min-width="200" show-overflow-tooltip />
            <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
            <el-table-column prop="is_default" label="默认" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="row.is_default ? 'success' : 'info'" size="small">
                  {{ row.is_default ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="creation_date" label="创建时间" width="180" align="center">
              <template #default="{ row }">
                {{ formatDateTime(row.creation_date) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：快速操作 -->
      <el-col :span="8">
        <!-- 快速操作 -->
        <el-card shadow="hover" style="margin-bottom: 20px">
          <template #header>
            <span>快速操作</span>
          </template>
          
          <div class="quick-actions">
            <el-button
              type="primary"
              style="width: 100%; margin-bottom: 10px"
              @click="handleManageMembers"
              v-auth="'projects:member:manage'"
            >
              <el-icon><ele-User /></el-icon>
              成员管理
            </el-button>
            <el-button
              type="success"
              style="width: 100%; margin-bottom: 10px"
              @click="handleManageEnvironments"
              v-auth="'projects:environment:manage'"
            >
              <el-icon><ele-Setting /></el-icon>
              环境管理
            </el-button>
            <el-button
              type="warning"
              style="width: 100%; margin-bottom: 10px"
              @click="handleEdit"
              v-auth="'projects:list:edit'"
            >
              <el-icon><ele-Edit /></el-icon>
              编辑项目
            </el-button>
            <el-button
              type="danger"
              style="width: 100%"
              @click="handleDelete"
              v-auth="'projects:list:delete'"
            >
              <el-icon><ele-Delete /></el-icon>
              删除项目
            </el-button>
          </div>
        </el-card>

        <!-- 最近活动 -->
        <el-card shadow="hover">
          <template #header>
            <span>最近活动</span>
          </template>
          
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in recentActivities"
              :key="index"
              :timestamp="activity.time"
              placement="top"
            >
              <el-card>
                <p>{{ activity.content }}</p>
                <p class="activity-user">{{ activity.user }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          
          <el-empty
            v-if="recentActivities.length === 0"
            description="暂无活动记录"
            :image-size="80"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑项目对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑项目"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        <el-form-item label="本机工作目录" prop="workspace_path">
          <el-input
            v-model="formData.workspace_path"
            placeholder="本机绝对路径，如 E:\code\my-app（写出 .mcp.json 依赖）"
          />
        </el-form-item>
        <el-form-item label="项目状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态">
            <el-option label="活跃" value="active" />
            <el-option label="暂停" value="paused" />
            <el-option label="已完成" value="completed" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 成员管理对话框 -->
    <MemberManage
      v-model="memberDialogVisible"
      :project-id="projectId"
      :project-name="projectInfo.name"
      @refresh="loadProjectDetail"
    />

    <!-- 环境管理对话框 -->
    <EnvironmentManage
      v-model="envDialogVisible"
      :project-id="projectId"
      :project-name="projectInfo.name"
      @refresh="loadProjectDetail"
    />
  </div>
</template>

<script setup lang="ts" name="projectsDetail">
import { ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus';
import { useProjectApi } from '/@/api/v1/projects/project';
import MemberManage from '../components/MemberManage.vue';
import EnvironmentManage from '../components/EnvironmentManage.vue';

const route = useRoute();
const router = useRouter();
const projectApi = useProjectApi();

const projectId = ref<number>(Number(route.params.id));
const loading = ref(false);

// 项目信息
const projectInfo = ref<any>({});
const memberList = ref<any[]>([]);
const environmentList = ref<any[]>([]);
const recentActivities = ref<any[]>([]);

// 编辑对话框
const editDialogVisible = ref(false);
const formRef = ref<FormInstance>();
const formData = reactive({
  name: '',
  description: '',
  workspace_path: '',
  status: 'active',
});
const submitLoading = ref(false);

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur' },
  ],
};

// 成员管理对话框
const memberDialogVisible = ref(false);

// 环境管理对话框
const envDialogVisible = ref(false);

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    paused: 'warning',
    completed: 'info',
    archived: 'info',
  };
  return typeMap[status] || '';
};

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    active: '活跃',
    paused: '暂停',
    completed: '已完成',
    archived: '已归档',
  };
  return textMap[status] || status;
};

// 获取角色类型
const getRoleType = (role: string) => {
  const typeMap: Record<string, string> = {
    owner: 'danger',
    admin: 'warning',
    developer: 'primary',
    tester: 'success',
    viewer: 'info',
  };
  return typeMap[role] || '';
};

// 获取角色文本
const getRoleText = (role: string) => {
  const textMap: Record<string, string> = {
    owner: '负责人',
    admin: '管理员',
    developer: '开发者',
    tester: '测试人员',
    viewer: '查看者',
  };
  return textMap[role] || role;
};

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

// 加载项目详情
const loadProjectDetail = async () => {
  loading.value = true;
  try {
    const res = await projectApi.getDetail(projectId.value);
    if (res.code === 200) {
      projectInfo.value = res.data;
    }
  } catch (error) {
    console.error('加载项目详情失败:', error);
    ElMessage.error('加载项目详情失败');
  } finally {
    loading.value = false;
  }
};

// 加载成员列表
const loadMembers = async () => {
  try {
    const res = await projectApi.getMemberList(projectId.value);
    if (res.code === 200) {
      memberList.value = res.data;
    }
  } catch (error) {
    console.error('加载成员列表失败:', error);
  }
};

// 加载环境列表
const loadEnvironments = async () => {
  try {
    const res = await projectApi.getEnvironmentList(projectId.value);
    if (res.code === 200) {
      environmentList.value = res.data;
    }
  } catch (error) {
    console.error('加载环境列表失败:', error);
  }
};

// 加载最近活动（模拟数据）
const loadRecentActivities = () => {
  // TODO: 后续可以从后端获取真实的活动记录
  recentActivities.value = [
    {
      time: formatDateTime(projectInfo.value.creation_date),
      content: '项目创建',
      user: projectInfo.value.owner_name || '系统',
    },
  ];
};

// 返回列表
const handleBack = () => {
  router.push('/projects/list');
};

// 编辑项目
const handleEdit = () => {
  formData.name = projectInfo.value.name;
  formData.description = projectInfo.value.description;
  formData.workspace_path = projectInfo.value.workspace_path || '';
  formData.status = projectInfo.value.status;
  editDialogVisible.value = true;
};

// 提交编辑
const handleSubmit = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return;
    
    submitLoading.value = true;
    try {
      const data = {
        name: formData.name,
        description: formData.description,
        workspace_path: formData.workspace_path || null,
        status: formData.status,
      };
      
      await projectApi.update(projectId.value, data);
      ElMessage.success('更新成功');
      editDialogVisible.value = false;
      loadProjectDetail();
    } catch (error: any) {
      const errorMsg = error?.response?.data?.message || error?.message || '操作失败';
      ElMessage.error(errorMsg);
    } finally {
      submitLoading.value = false;
    }
  });
};

// 删除项目
const handleDelete = () => {
  ElMessageBox.confirm(`确定要删除项目"${projectInfo.value.name}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await projectApi.delete(projectId.value);
      ElMessage.success('删除成功');
      router.push('/projects/list');
    } catch (error: any) {
      console.error('删除失败:', error);
      // 显示后端返回的错误信息
      const errorMessage = error?.response?.data?.message || error?.message || '删除失败';
      ElMessage.error(errorMessage);
    }
  });
};

// 管理成员
const handleManageMembers = () => {
  memberDialogVisible.value = true;
};

// 管理环境
const handleManageEnvironments = () => {
  envDialogVisible.value = true;
};

// 初始化
onMounted(() => {
  loadProjectDetail();
  loadMembers();
  loadEnvironments();
  
  // 延迟加载活动记录，等待项目信息加载完成
  setTimeout(() => {
    loadRecentActivities();
  }, 500);
});
</script>

<style scoped lang="scss">
.project-detail-container {
  padding: 15px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  
  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
  }
  
  .stat-content {
    flex: 1;
    
    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      line-height: 1;
      margin-bottom: 8px;
    }
    
    .stat-label {
      font-size: 14px;
      color: #909399;
    }
  }
}

.quick-actions {
  .el-button {
    justify-content: flex-start;
    
    .el-icon {
      margin-right: 8px;
    }
  }
}

.activity-user {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}
</style>
