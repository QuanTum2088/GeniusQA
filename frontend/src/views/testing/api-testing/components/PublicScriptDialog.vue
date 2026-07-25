<template>
  <el-dialog
    v-model="visible"
    title="公共脚本管理"
    width="900px"
    @close="handleClose"
  >
    <div class="public-script-manager">
      <div class="toolbar">
        <el-button type="primary" @click="showEditDialog(null)">
          <el-icon><ele-Plus /></el-icon>
          新增脚本
        </el-button>
      </div>

      <el-table :data="scripts" style="width: 100%">
        <el-table-column prop="name" label="脚本名称" min-width="150" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="script_type" label="类型" width="100" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
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
      :title="editingScript ? '编辑脚本' : '新增脚本'"
      width="700px"
      append-to-body
    >
      <el-form :model="formData" label-width="100px">
        <el-form-item label="脚本名称" required>
          <el-input v-model="formData.name" placeholder="请输入脚本名称" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="formData.category" placeholder="如：认证、工具等" />
        </el-form-item>
        <el-form-item label="脚本类型">
          <el-select v-model="formData.script_type">
            <el-option label="Python" value="python" />
            <el-option label="JavaScript" value="javascript" />
          </el-select>
        </el-form-item>
        <el-form-item label="脚本内容" required>
          <el-input
            v-model="formData.script_content"
            type="textarea"
            :rows="12"
            placeholder="编写脚本内容"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="脚本功能描述"
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
  getPublicScripts,
  createPublicScript,
  updatePublicScript,
  deletePublicScript
} from '/@/api/v1/testing/operations'

const props = defineProps<{
  modelValue: boolean
  projectId?: number
}>()

const emit = defineEmits(['update:modelValue', 'refresh'])

const visible = ref(false)
const scripts = ref<any[]>([])
const showEdit = ref(false)
const editingScript = ref<any>(null)
const formData = ref({
  name: '',
  category: '',
  script_type: 'python',
  script_content: '',
  description: '',
  is_active: true
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadScripts()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

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
    ElMessage.error('加载脚本列表失败')
  }
}

const showEditDialog = (script: any) => {
  if (script) {
    editingScript.value = script
    formData.value = {
      name: script.name,
      category: script.category || '',
      script_type: script.script_type,
      script_content: script.script_content,
      description: script.description || '',
      is_active: script.is_active
    }
  } else {
    editingScript.value = null
    formData.value = {
      name: '',
      category: '',
      script_type: 'python',
      script_content: '',
      description: '',
      is_active: true
    }
  }
  showEdit.value = true
}

const handleSave = async () => {
  if (!formData.value.name || !formData.value.script_content) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    const data = {
      ...formData.value,
      project_id: props.projectId!
    }

    if (editingScript.value) {
      await updatePublicScript(editingScript.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createPublicScript(data)
      ElMessage.success('创建成功')
    }

    showEdit.value = false
    loadScripts()
    emit('refresh')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定要删除这个脚本吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deletePublicScript(id)
      ElMessage.success('删除成功')
      loadScripts()
      emit('refresh')
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped lang="scss">
.public-script-manager {
  .toolbar {
    margin-bottom: 15px;
  }

  :deep(textarea) {
    font-family: 'Courier New', monospace;
    font-size: 13px;
  }
}
</style>
