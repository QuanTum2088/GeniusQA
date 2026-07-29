<template>
  <div class="sql-step-form">
    <el-form label-width="80px" size="small">
      <el-form-item label="数据库">
        <el-select
          v-model="req.db_id"
          placeholder="请选择数据库配置"
          style="width:100%"
          filterable
          @visible-change="(open: boolean) => { if (open) loadDbList() }"
        >
          <el-option v-for="db in dbList" :key="db.id" :label="db.name" :value="db.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="SQL 语句">
        <el-input
          v-model="req.sql"
          type="textarea"
          :rows="4"
          placeholder="SELECT * FROM table WHERE id = ${var_name}"
          style="font-family: monospace; font-size: 12px"
        />
      </el-form-item>
      <el-form-item label="结果变量">
        <el-input v-model="req.variable_name" placeholder="将查询结果存入变量名（可选）" style="width:200px" />
        <span style="font-size:11px;color:var(--el-text-color-placeholder);margin-left:8px">
          单行结果存为 Dict，多行存为 List
        </span>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { apiAutomationApi } from '/@/api/v1/testing/apiAutomation'
import { onDbListChanged } from '../../composables/dbListSync'

const props = defineProps<{ step: any }>()

const dbList = ref<any[]>([])

const req = computed(() => {
  if (!props.step.request) props.step.request = { db_id: null, sql: '', variable_name: '' }
  return props.step.request
})

const loadDbList = async () => {
  try {
    const r: any = await apiAutomationApi.api_db_list()
    const raw = r?.data
    dbList.value = Array.isArray(raw) ? raw : (Array.isArray(raw?.content) ? raw.content : [])
  } catch {
    dbList.value = []
  }
}

let offDbListSync: (() => void) | null = null
onMounted(() => {
  loadDbList()
  offDbListSync = onDbListChanged(loadDbList)
})
onBeforeUnmount(() => {
  offDbListSync?.()
  offDbListSync = null
})
</script>

<style scoped>
.sql-step-form { padding: 4px 0; }
</style>
