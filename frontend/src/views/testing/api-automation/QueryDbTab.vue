<template>
  <div class="qdb-root">
    <!-- Left panel: DB selector + tree -->
    <div class="qdb-left">
      <div class="qdb-left__header">
        <el-select
          v-model="selectedDbId"
          placeholder="请选择数据库连接"
          clearable
          style="width:100%"
          @change="onDbChange"
        >
          <el-option v-for="db in dbList" :key="db.id" :label="db.name" :value="db.id" />
        </el-select>
      </div>
      <div v-if="selectedDbId" class="qdb-left__tree">
        <el-tree
          ref="treeRef"
          :data="treeData"
          :props="{ label: 'name', isLeaf: 'isLeaf' }"
          lazy
          :load="loadNode"
          node-key="name"
          highlight-current
          @node-click="onNodeClick"
        >
          <template #default="{ node, data }">
            <span class="qdb-tree-node">
              <el-icon v-if="data.type === 'database'" style="color:#f59e0b"><ele-Coin /></el-icon>
              <el-icon v-else style="color:#6366f1"><ele-Grid /></el-icon>
              <span>{{ data.name }}</span>
            </span>
          </template>
        </el-tree>
      </div>
      <div v-else class="qdb-left__empty">请先选择数据库连接</div>
    </div>

    <!-- Divider -->
    <div class="qdb-divider" />

    <!-- Right panel: SQL editor + results -->
    <div class="qdb-right">
      <!-- SQL editor area -->
      <div class="qdb-editor-wrap">
        <div class="qdb-editor-toolbar">
          <span class="qdb-lang-badge">SQL</span>
          <el-button
            type="primary"
            size="small"
            :loading="executing"
            @click="execute"
          >
            <el-icon><ele-CaretRight /></el-icon>&nbsp;执行
          </el-button>
          <el-button size="small" @click="sql = ''">清空</el-button>
        </div>
        <textarea
          v-model="sql"
          class="qdb-editor"
          placeholder="SELECT * FROM table_name LIMIT 20;"
          spellcheck="false"
        />
      </div>

      <!-- Result tabs -->
      <div class="qdb-results">
        <el-tabs
          v-if="resultTabs.length"
          v-model="activeTab"
          type="card"
          closable
          @tab-remove="removeTab"
        >
          <el-tab-pane
            v-for="tab in resultTabs"
            :key="tab.name"
            :label="tab.title"
            :name="tab.name"
          >
            <div v-if="tab.error" class="qdb-result-error">{{ tab.error }}</div>
            <el-table
              v-else
              :data="tab.rows"
              border
              stripe
              size="small"
              empty-text="暂无数据"
              style="width:100%"
              :max-height="280"
            >
              <el-table-column
                v-for="col in tab.columns"
                :key="col"
                :prop="col"
                :label="col"
                show-overflow-tooltip
                min-width="120"
              />
            </el-table>
          </el-tab-pane>
        </el-tabs>
        <div v-else class="qdb-results__empty">执行 SQL 后结果将显示在此处</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useApiAutomationApi } from '/@/api/v1/testing/apiAutomation'

defineProps<{ serviceId: number }>()

const { api_db_list, get_db_databases, get_db_tables, execute_db_query } = useApiAutomationApi()

interface ResultTab {
  name: string
  title: string
  columns: string[]
  rows: any[]
  error?: string
}

const dbList = ref<any[]>([])
const selectedDbId = ref<number | null>(null)
const treeData = ref<any[]>([])
const treeRef = ref<any>(null)
const sql = ref('')
const executing = ref(false)
const resultTabs = ref<ResultTab[]>([])
const activeTab = ref('')
let tabCounter = 0

async function loadDbList() {
  try {
    const res: any = await api_db_list({})
    const raw = res?.data
    dbList.value = Array.isArray(raw) ? raw : (Array.isArray(raw?.rows) ? raw.rows : [])
  } catch {
    dbList.value = []
  }
}

function onDbChange(val: number | null) {
  treeData.value = []
  if (!val) return
  // Tree will lazy-load on expand; seed with root call
  loadRootDatabases()
}

async function loadRootDatabases() {
  if (!selectedDbId.value) return
  try {
    const res: any = await get_db_databases({ db_id: selectedDbId.value })
    treeData.value = Array.isArray(res?.data) ? res.data : []
  } catch (e: any) {
    ElMessage.error(e?.message || '获取数据库列表失败')
    treeData.value = []
  }
}

async function loadNode(node: any, resolve: (data: any[]) => void) {
  if (node.level === 0) {
    // Root — already loaded via loadRootDatabases
    resolve(treeData.value)
    return
  }
  if (node.data?.type === 'database' && selectedDbId.value) {
    try {
      const res: any = await get_db_tables({ db_id: selectedDbId.value, database: node.data.name })
      resolve(Array.isArray(res?.data) ? res.data : [])
    } catch {
      resolve([])
    }
  } else {
    resolve([])
  }
}

function onNodeClick(data: any) {
  if (data.type === 'table') {
    const stmt = `SELECT * FROM ${data.name} LIMIT 20;\n`
    sql.value = sql.value ? sql.value + '\n' + stmt : stmt
  }
}

async function execute() {
  if (!selectedDbId.value) {
    ElMessage.warning('请先选择数据库连接')
    return
  }
  if (!sql.value.trim()) {
    ElMessage.warning('请输入 SQL 语句')
    return
  }
  executing.value = true
  try {
    const res: any = await execute_db_query({ db_id: selectedDbId.value, sql: sql.value.trim() })
    const rows: any[] = Array.isArray(res?.data) ? res.data : []
    const columns = rows.length > 0 ? Object.keys(rows[0]) : []
    tabCounter++
    const tab: ResultTab = {
      name: `result-${tabCounter}`,
      title: `结果 ${tabCounter}`,
      columns,
      rows,
    }
    resultTabs.value.push(tab)
    activeTab.value = tab.name
  } catch (e: any) {
    ElMessage.error(e?.message || '执行失败')
  } finally {
    executing.value = false
  }
}

function removeTab(name: string) {
  const idx = resultTabs.value.findIndex(t => t.name === name)
  if (idx < 0) return
  resultTabs.value.splice(idx, 1)
  if (activeTab.value === name) {
    const next = resultTabs.value[idx] || resultTabs.value[idx - 1]
    activeTab.value = next?.name ?? ''
  }
}

onMounted(loadDbList)
</script>

<style scoped>
.qdb-root {
  display: flex;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

/* ── Left panel ── */
.qdb-left {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--el-border-color-light, #e2e8f0);
  overflow: hidden;
}

.qdb-left__header {
  padding: 10px 10px 6px;
  flex-shrink: 0;
}

.qdb-left__tree {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.qdb-left__empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--el-text-color-placeholder, #94a3b8);
  padding: 20px;
  text-align: center;
}

.qdb-tree-node {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
}

/* ── Divider ── */
.qdb-divider {
  width: 4px;
  background: var(--el-border-color-lighter, #f0f0f0);
  flex-shrink: 0;
}

/* ── Right panel ── */
.qdb-right {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* SQL editor */
.qdb-editor-wrap {
  flex-shrink: 0;
  border-bottom: 1px solid var(--el-border-color-light, #e2e8f0);
}

.qdb-editor-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #2a2a3e;
}

.qdb-lang-badge {
  font-size: 11px;
  font-weight: 700;
  color: #a78bfa;
  background: rgba(167,139,250,0.15);
  padding: 1px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

.qdb-editor {
  width: 100%;
  height: 160px;
  padding: 10px 12px;
  background: #1e1e2e;
  color: #cdd6f4;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  border: none;
  outline: none;
  resize: vertical;
  box-sizing: border-box;
  tab-size: 4;
}

/* Results */
.qdb-results {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 8px;
}

.qdb-results__empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 13px;
  color: var(--el-text-color-placeholder, #94a3b8);
}

.qdb-result-error {
  padding: 12px;
  color: var(--el-color-danger);
  font-size: 13px;
  font-family: monospace;
  background: var(--el-color-danger-light-9, #fef0f0);
  border-radius: 4px;
}
</style>
