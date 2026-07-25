<template>
  <el-dialog
    v-model="visible"
    title="SSL证书管理"
    width="900px"
    @close="handleClose"
  >
    <div class="ssl-certificate-manager">
      <div class="toolbar">
        <el-button type="primary" @click="handleAdd">
          <el-icon><ele-Plus /></el-icon>
          添加证书
        </el-button>
      </div>
      
      <el-table :data="certificates" style="width: 100%; margin-top: 15px">
        <el-table-column prop="name" label="证书名称" min-width="150" />
        <el-table-column prop="cert_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.cert_type === 'CA' ? 'success' : 'primary'">
              {{ row.cert_type === 'CA' ? 'CA证书' : '客户端证书' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="domain" label="适用域名" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.domain || '全部' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="handleToggle(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 添加/编辑证书对话框 -->
    <el-dialog
      v-model="showEditDialog"
      :title="editForm.id ? '编辑证书' : '添加证书'"
      width="700px"
      append-to-body
    >
      <el-form :model="editForm" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="证书类型" prop="cert_type">
          <el-radio-group v-model="editForm.cert_type" :disabled="!!editForm.id">
            <el-radio label="CA">CA证书</el-radio>
            <el-radio label="CLIENT">客户端证书</el-radio>
          </el-radio-group>
          <div style="margin-top: 5px; font-size: 12px; color: #909399;">
            <span v-if="editForm.cert_type === 'CA'">用于验证服务器证书（自签名或内部CA）</span>
            <span v-else>用于双向SSL认证，向服务器证明客户端身份</span>
          </div>
        </el-form-item>
        
        <el-form-item label="证书名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入证书名称" />
        </el-form-item>
        
        <el-form-item label="适用域名" prop="domain">
          <el-input v-model="editForm.domain" placeholder="例如: *.example.com 或 api.example.com">
            <template #append>
              <el-tooltip content="支持通配符，如 *.example.com 匹配所有子域名；留空则匹配所有域名" placement="top">
                <el-icon><ele-QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
          </el-input>
        </el-form-item>
        
        <!-- CA证书字段 -->
        <template v-if="editForm.cert_type === 'CA'">
          <el-form-item label="CA证书" prop="ca_cert">
            <el-input
              v-model="editForm.ca_cert"
              type="textarea"
              :rows="8"
              placeholder="-----BEGIN CERTIFICATE-----&#10;...&#10;-----END CERTIFICATE-----"
            />
            <div style="margin-top: 5px;">
              <el-button size="small" @click="handleUploadFile('ca_cert')">
                <el-icon><ele-Upload /></el-icon>
                从文件上传
              </el-button>
            </div>
          </el-form-item>
        </template>
        
        <!-- 客户端证书字段 -->
        <template v-if="editForm.cert_type === 'CLIENT'">
          <el-form-item label="客户端证书" prop="client_cert">
            <el-input
              v-model="editForm.client_cert"
              type="textarea"
              :rows="6"
              placeholder="-----BEGIN CERTIFICATE-----&#10;...&#10;-----END CERTIFICATE-----"
            />
            <div style="margin-top: 5px;">
              <el-button size="small" @click="handleUploadFile('client_cert')">
                <el-icon><ele-Upload /></el-icon>
                从文件上传 (.crt, .pem)
              </el-button>
            </div>
          </el-form-item>
          
          <el-form-item label="客户端私钥" prop="client_key">
            <el-input
              v-model="editForm.client_key"
              type="textarea"
              :rows="6"
              placeholder="-----BEGIN PRIVATE KEY-----&#10;...&#10;-----END PRIVATE KEY-----"
            />
            <div style="margin-top: 5px;">
              <el-button size="small" @click="handleUploadFile('client_key')">
                <el-icon><ele-Upload /></el-icon>
                从文件上传 (.key, .pem)
              </el-button>
            </div>
          </el-form-item>
          
          <el-form-item label="私钥密码">
            <el-input
              v-model="editForm.passphrase"
              type="password"
              placeholder="如果私钥有密码保护，请输入密码"
              show-password
            />
          </el-form-item>
        </template>
        
        <el-form-item label="描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入证书描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 隐藏的文件上传input -->
    <input
      ref="fileInput"
      type="file"
      style="display: none"
      @change="handleFileSelected"
      accept=".pem,.crt,.key,.cer"
    />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useSslCertificateApi } from '/@/api/v1/testing/sslCertificate'

const sslCertificateApi = useSslCertificateApi()

const props = defineProps<{
  modelValue: boolean
  projectId?: number
}>()

const emit = defineEmits(['update:modelValue', 'success'])

const visible = ref(false)
const showEditDialog = ref(false)
const loading = ref(false)
const formRef = ref()
const fileInput = ref<HTMLInputElement>()
const currentUploadField = ref<string>('')

const certificates = ref<any[]>([])

const editForm = ref({
  id: undefined,
  name: '',
  cert_type: 'CA',
  domain: '',
  ca_cert: '',
  client_cert: '',
  client_key: '',
  passphrase: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入证书名称', trigger: 'blur' }],
  cert_type: [{ required: true, message: '请选择证书类型', trigger: 'change' }],
  ca_cert: [
    {
      validator: (rule: any, value: any, callback: any) => {
        if (editForm.value.cert_type === 'CA' && !value) {
          callback(new Error('请输入CA证书内容'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  client_cert: [
    {
      validator: (rule: any, value: any, callback: any) => {
        if (editForm.value.cert_type === 'CLIENT' && !value) {
          callback(new Error('请输入客户端证书内容'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  client_key: [
    {
      validator: (rule: any, value: any, callback: any) => {
        if (editForm.value.cert_type === 'CLIENT' && !value) {
          callback(new Error('请输入客户端私钥内容'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadCertificates()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 加载证书列表
const loadCertificates = async () => {
  if (!props.projectId) return
  
  try {
    const res = await sslCertificateApi.list({ project_id: props.projectId })
    certificates.value = res.data.items || []
  } catch (error) {
    console.error('加载证书列表失败:', error)
    ElMessage.error('加载证书列表失败')
  }
}

// 添加证书
const handleAdd = () => {
  editForm.value = {
    id: undefined,
    name: '',
    cert_type: 'CA',
    domain: '',
    ca_cert: '',
    client_cert: '',
    client_key: '',
    passphrase: '',
    description: ''
  }
  showEditDialog.value = true
}

// 编辑证书
const handleEdit = async (row: any) => {
  try {
    // 获取证书详情（包含证书内容）
    const res = await sslCertificateApi.get(row.id)
    editForm.value = { ...res.data }
    showEditDialog.value = true
  } catch (error) {
    ElMessage.error('加载证书详情失败')
  }
}

// 切换证书状态
const handleToggle = async (row: any) => {
  try {
    await sslCertificateApi.toggle(row.id)
    ElMessage.success(row.is_active ? '已启用' : '已禁用')
    emit('success')
  } catch (error) {
    // 恢复原状态
    row.is_active = !row.is_active
    ElMessage.error('操作失败')
  }
}

// 删除证书
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除证书 "${row.name}" 吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await sslCertificateApi.delete(row.id)
    ElMessage.success('删除成功')
    await loadCertificates()
    emit('success')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 上传文件
const handleUploadFile = (field: string) => {
  currentUploadField.value = field
  fileInput.value?.click()
}

// 文件选择后
const handleFileSelected = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  try {
    const text = await file.text()
    
    // 根据字段设置内容
    if (currentUploadField.value === 'ca_cert') {
      editForm.value.ca_cert = text
    } else if (currentUploadField.value === 'client_cert') {
      editForm.value.client_cert = text
    } else if (currentUploadField.value === 'client_key') {
      editForm.value.client_key = text
    }
    
    ElMessage.success('文件读取成功')
  } catch (error) {
    ElMessage.error('文件读取失败')
  }
  
  // 清空input，允许重复选择同一文件
  target.value = ''
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    const data = {
      ...editForm.value,
      project_id: props.projectId
    }
    
    if (editForm.value.id) {
      await sslCertificateApi.update(editForm.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await sslCertificateApi.create(data)
      ElMessage.success('创建成功')
    }
    
    showEditDialog.value = false
    await loadCertificates()
    emit('success')
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped lang="scss">
.ssl-certificate-manager {
  .toolbar {
    display: flex;
    justify-content: flex-end;
  }
}
</style>
