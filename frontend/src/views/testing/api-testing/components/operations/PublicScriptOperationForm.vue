<template>
  <div class="public-script-operation-form">
    <el-form-item label="选择脚本">
      <el-select
        v-model="localValue.script_id"
        placeholder="选择公共脚本"
        filterable
        @change="emitChange"
      >
        <el-option
          v-for="script in scripts"
          :key="script.id"
          :label="script.name"
          :value="script.id"
        >
          <div style="display: flex; justify-content: space-between;">
            <span>{{ script.name }}</span>
            <span style="color: #909399; font-size: 12px;">{{ script.category }}</span>
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
        管理脚本
      </el-button>
    </el-form-item>

    <div v-if="selectedScript" class="script-preview">
      <div class="preview-header">脚本预览：</div>
      <pre>{{ selectedScript.script_content }}</pre>
    </div>

    <!-- 公共脚本管理对话框 -->
    <PublicScriptDialog
      v-model="showManageDialog"
      :project-id="projectId"
      @refresh="loadScripts"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { getPublicScripts } from '/@/api/v1/testing/operations'
import PublicScriptDialog from '../PublicScriptDialog.vue'

const props = defineProps<{
  modelValue: any
  projectId?: number
}>()

const emit = defineEmits(['update:modelValue'])

const localValue = ref({
  script_id: props.modelValue?.script_id || null
})

const scripts = ref<any[]>([])
const showManageDialog = ref(false)

const selectedScript = computed(() => {
  return scripts.value.find(s => s.id === localValue.value.script_id)
})

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    localValue.value = {
      script_id: newVal.script_id || null
    }
  }
}, { deep: true })

const emitChange = () => {
  emit('update:modelValue', {
    ...props.modelValue,
    ...localValue.value
  })
}

const loadScripts = async () => {
  if (!props.projectId) return
  
  try {
    const res = await getPublicScripts({
      project_id: props.projectId,
      page: 1,
      page_size: 100
    })
    scripts.value = res.data.items || []
  } catch (error) {
    console.error('加载公共脚本失败:', error)
  }
}

onMounted(() => {
  loadScripts()
})
</script>

<style scoped lang="scss">
.public-script-operation-form {
  .script-preview {
    margin-top: 15px;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 4px;

    .preview-header {
      font-size: 12px;
      color: #909399;
      margin-bottom: 8px;
    }

    pre {
      margin: 0;
      font-family: 'Courier New', monospace;
      font-size: 12px;
      color: #303133;
      white-space: pre-wrap;
      word-break: break-all;
      max-height: 200px;
      overflow-y: auto;
    }
  }
}
</style>
