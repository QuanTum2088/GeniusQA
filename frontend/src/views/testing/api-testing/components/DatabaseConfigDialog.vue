<template>
  <el-dialog
    v-model="visible"
    title="数据库配置管理"
    width="900px"
    @close="handleClose"
  >
    <div class="database-config-manager">
      <div class="toolbar">
        <el-button type="primary" @click="showEditDialog(null)">
          <el-icon><ele-Plus /></el-icon>
          新增配置
        </el-button>
      </div>

      <el-table :data="configs" style="width: 100%">
        <el-table-column prop="name" label="配置名称" min-width="150" />
        <el-table-column prop="db_type" label="数据库类型" width="120" />
        <el-table-column label="连接信息" min-width="250">
          <template #default="{ row }">
            {{ row.host }}:{{ row.port }}/{{ row.database_name }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="success" size="small" @click="testConnection(row.id)">
              测试
            </el-button>
            <el-button type="primary" size="small" @click="showEditDialog(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="showEdit"
      :title="editingConfig ? '编辑配置' : '新增配置'"
      width="600px"
      append-to-body
    >
      <el-form :model="formData" label-width="120px">
        <el-form-item label="配置名称" required>
          <el-input v-model="formData.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="数据库类型" required>
          <el-select v-model="formData.db_type">
            <el-option label="MySQL" value="mysql" />
            <el-option label="PostgreSQL" value="postgresql" />
            <el-option label="MongoDB" value="mongodb" />
            <el-option label="Redis" value="redis" />
          </el-select>
        </el-form-item>
        <el-form-item label="主机地址" required>
          <el-input v-model="formData.host" placeholder="如：localhost" />
        </el-form-item>
        <el-form-item label="端口" required>
          <el-input-number v-model="formData.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="数据库名">
          <el-input v-model="formData.database_name" placeholder="数据库名称" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="formData.username" placeholder="数据库用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="数据库密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="配置描述"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getDatabaseConfigs,
  createDatabaseConfig,
  updateDatabaseConfig,
  deleteDatabaseConfig,
  testDatabaseConnection
} from '/@/api/v1/testing/operations'

const props = defineProps<{
  modelValue: boolean
  projectId?: number
}>()

const emit = defineEmits(['update:modelValue', 'refresh'])

const visible = ref(false)
const configs = ref<any[]>([])
const showEdit = ref(false)
const editingConfig = ref<any>(null)
const formData = ref({
  name: '',
  db_type: 'mysql',
  host: 'localhost',
  port: 3306,
  database_name: '',
  username: '',
  password: '',
  description: '',
  is_active: true
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadConfigs()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const loadConfigs = async () => {
  if (!props.projectId) return
  
  try {
    const res = await getDatabaseConfigs({
      project_id: props.projectId,
      page: 1,
      page_size: 100
    })
    configs.value = res.data.items || []
  } catch (error) {
    ElMessage.error('加载配置列表失败')
  }
}

const showEditDialog = (config: any) => {
  if (config) {
    editingConfig.value = config
    formData.value = {
      name: config.name,
      db_type: config.db_type,
      host: config.host,
      port: config.port,
      database_name: config.database_name || '',
      username: config.username || '',
      password: config.password || '',
      description: config.description || '',
      is_active: config.is_active
    }
  } else {
    editingConfig.value = null
    formData.value = {
      name: '',
      db_type: 'mysql',
      host: 'localhost',
      port: 3306,
      database_name: '',
      username: '',
      password: '',
      description: '',
      is_active: true
    }
  }
  showEdit.value = true
}

const handleSave = async () => {
  if (!formData.value.name || !formData.value.host) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    const data = {
      ...formData.value,
      project_id: props.projectId!
    }

    if (editingConfig.value) {
      await updateDatabaseConfig(editingConfig.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createDatabaseConfig(data)
      ElMessage.success('创建成功')
    }

    showEdit.value = false
    loadConfigs()
    emit('refresh')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定要删除这个配置吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteDatabaseConfig(id)
      ElMessage.success('删除成功')
      loadConfigs()
      emit('refresh')
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const testConnection = async (id: number) => {
  try {
    const res = await testDatabaseConnection(id)
    if (res.data.success) {
      ElMessage.success(res.data.message)
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (error) {
    ElMessage.error('测试连接失败')
  }
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped lang="scss">
.database-config-manager {
  .toolbar {
    margin-bottom: 15px;
  }
}
</style>
