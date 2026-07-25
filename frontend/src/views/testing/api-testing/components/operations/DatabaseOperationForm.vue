<template>
  <div class="database-operation-form">
    <el-form-item label="数据库配置">
      <el-select
        v-model="localValue.db_config_id"
        placeholder="选择数据库配置"
        filterable
        @change="emitChange"
      >
        <el-option
          v-for="config in configs"
          :key="config.id"
          :label="config.name"
          :value="config.id"
        >
          <div style="display: flex; justify-content: space-between;">
            <span>{{ config.name }}</span>
            <span style="color: #909399; font-size: 12px;">{{ config.db_type }}</span>
          </div>
        </el-option>
      </el-select>
      <el-button
        type="primary"
        text
        style="margin-left: 10px;"
        @click="showManageDialog = true"
      >
        <el-icon><ele-Setting /></el-icon>
        管理配置
      </el-button>
    </el-form-item>

    <el-form-item label="SQL语句">
      <el-input
        v-model="localValue.sql"
        type="textarea"
        :rows="6"
        placeholder="输入SQL语句，可以使用 {{variable}} 引用环境变量&#10;例如：SELECT * FROM users WHERE id = {{user_id}}"
        @input="emitChange"
      />
    </el-form-item>

    <el-form-item label="保存结果到">
      <el-input
        v-model="localValue.save_to_var"
        placeholder="变量名（可选），如：query_result"
        @input="emitChange"
      />
      <div class="form-tip">
        <el-icon><ele-InfoFilled /></el-icon>
        <span>查询结果将保存到指定的环境变量中</span>
      </div>
    </el-form-item>

    <!-- 数据库配置管理对话框 -->
    <DatabaseConfigDialog
      v-model="showManageDialog"
      :project-id="projectId"
      @refresh="loadConfigs"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getDatabaseConfigs } from '/@/api/v1/testing/operations'
import DatabaseConfigDialog from '../DatabaseConfigDialog.vue'

const props = defineProps<{
  modelValue: any
  projectId?: number
}>()

const emit = defineEmits(['update:modelValue'])

const localValue = ref({
  db_config_id: props.modelValue?.db_config_id || null,
  sql: props.modelValue?.sql || '',
  save_to_var: props.modelValue?.save_to_var || ''
})

const configs = ref<any[]>([])
const showManageDialog = ref(false)

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    localValue.value = {
      db_config_id: newVal.db_config_id || null,
      sql: newVal.sql || '',
      save_to_var: newVal.save_to_var || ''
    }
  }
}, { deep: true })

const emitChange = () => {
  emit('update:modelValue', {
    ...props.modelValue,
    ...localValue.value
  })
}

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
    console.error('加载数据库配置失败:', error)
  }
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped lang="scss">
.database-operation-form {
  :deep(textarea) {
    font-family: 'Courier New', monospace;
    font-size: 13px;
  }

  .form-tip {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-top: 8px;
    font-size: 12px;
    color: #909399;

    .el-icon {
      font-size: 14px;
    }
  }
}
</style>
