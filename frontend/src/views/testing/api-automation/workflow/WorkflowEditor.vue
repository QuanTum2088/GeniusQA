<template>
  <div class="wfe-root">
    <div class="wfe-toolbar">
      <div class="wfe-toolbar-left">
        <el-button text @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <!-- Global mode: editable name -->
        <template v-if="isGlobalMode">
          <el-input
            v-model="globalName"
            size="small"
            placeholder="工作流名称"
            style="width:200px"
          />
          <el-tag type="info" size="small">全局工作流</el-tag>
        </template>
        <!-- Case-bound mode: show case name -->
        <template v-else>
          <span class="wfe-case-name">{{ caseData?.name || '加载中...' }}</span>
        </template>
      </div>

      <div class="wfe-toolbar-right">
        <span v-if="isDirty" class="wfe-dirty-badge">有未保存的修改</span>
        <el-button size="small" @click="autoLayout">整理布局</el-button>
        <el-dropdown trigger="click" @command="addNode">
          <el-button size="small">
            添加节点
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <template v-for="group in addNodeGroups" :key="group.name">
                <el-dropdown-item disabled style="font-size:11px;color:#94a3b8;padding:4px 16px">
                  {{ group.name }}
                </el-dropdown-item>
                <el-dropdown-item v-for="item in group.items" :key="item.type" :command="item.type">
                  {{ item.label }}
                </el-dropdown-item>
              </template>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="primary" size="small" :loading="saving" @click="saveCase">保存</el-button>
        <el-button type="success" size="small" :icon="VideoPlay" @click="openRunDialog">运行</el-button>
      </div>
    </div>

    <!-- Save-as dialog (global mode first save) -->
    <el-dialog v-model="saveAsDialogVisible" title="保存工作流为用例" width="440px" :close-on-click-modal="false">
      <el-form label-width="80px">
        <el-form-item label="用例名称" required>
          <el-input v-model="saveAsForm.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="所属服务" required>
          <el-select v-model="saveAsForm.serviceId" placeholder="请选择服务" style="width:100%" @change="onSaveAsServiceChange">
            <el-option v-for="svc in serviceList" :key="svc.id" :label="svc.name" :value="svc.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属套件" required>
          <el-select v-model="saveAsForm.suiteId" placeholder="请先选择服务" style="width:100%">
            <el-option v-for="s in saveAsSuiteList" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveAsDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="confirmSaveAs">保存</el-button>
      </template>
    </el-dialog>

    <!-- Run dialog -->
    <el-dialog v-model="runDialogVisible" title="执行工作流" width="400px" :close-on-click-modal="false">
      <el-form label-width="80px">
        <el-form-item label="执行环境" required>
          <el-select v-model="runForm.env_id" placeholder="请选择环境" style="width:100%">
            <el-option v-for="env in envList" :key="env.id" :label="env.name" :value="env.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="runDialogVisible = false">取消</el-button>
        <el-button type="success" :loading="running" @click="confirmRun">
          <el-icon><VideoPlay /></el-icon>&nbsp;开始执行
        </el-button>
      </template>
    </el-dialog>

    <!-- Main content -->
    <div class="wfe-body" v-loading="loading">
      <div class="wfe-canvas-area">
        <WorkflowCanvas
          :nodes="nodes"
          :selected-id="selectedNodeId"
          @select="onSelect"
          @move="onMove"
          @delete="onDelete"
          @copy="onCopy"
          @add-after="onAddAfter"
          @add-before="onAddBefore"
          @add-branch="onAddBranch"
          @connect="onConnect"
        />
      </div>
      <div class="wfe-panel-area" :class="{ open: panelVisible }">
        <WorkflowConfigPanel
          :visible="panelVisible"
          :node="selectedNode"
          :service-id="serviceId"
          @close="panelVisible = false"
          @save="saveCase"
        />
      </div>
    </div>

    <!-- Type picker -->
    <Teleport to="body">
      <div v-if="typePicker" class="wf-type-picker-overlay" @click.self="typePicker = null">
        <div class="wf-type-picker">
          <div class="wf-type-picker__title">选择节点类型</div>
          <div class="wf-type-picker__group">逻辑</div>
          <div class="wf-type-picker__item" @click="onPickType('loop')"><span class="wf-type-picker__dot" style="background:#ef6820" />循环控制</div>
          <div class="wf-type-picker__item" @click="onPickType('if')"><span class="wf-type-picker__dot" style="background:#ee46bc" />条件分支</div>
          <div class="wf-type-picker__group">步骤</div>
          <div class="wf-type-picker__item" @click="onPickType('api')"><span class="wf-type-picker__dot" style="background:#6366f1" />HTTP 请求</div>
          <div class="wf-type-picker__item" @click="onPickType('script')"><span class="wf-type-picker__dot" style="background:#7b4d12" />代码执行</div>
          <div class="wf-type-picker__item" @click="onPickType('sql')"><span class="wf-type-picker__dot" style="background:#783887" />数据库操作</div>
          <div class="wf-type-picker__item" @click="onPickType('wait')"><span class="wf-type-picker__dot" style="background:#10b981" />等待控制</div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, ArrowDown, VideoPlay } from '@element-plus/icons-vue'
import { useApiAutomationApi } from '/@/api/v1/testing/apiAutomation'
import { flattenSteps, rebuildScript, safeCloneScript, computeLayout } from './useWorkflowLayout'
import { DEFAULT_STEP, genId, ADD_NODE_MENU, NODE_WIDTH } from './types'
import type { WorkflowNode, StepType } from './types'
import WorkflowCanvas from './WorkflowCanvas.vue'
import WorkflowConfigPanel from './WorkflowConfigPanel.vue'

const NODE_W = NODE_WIDTH

const route = useRoute()
const router = useRouter()
const {
  api_case_list, add_api_case, edit_api_case,
  run_api_case, api_env, api_suite_list,
  api_service_list,
} = useApiAutomationApi()

// ─── Mode detection ───────────────────────────────────────────────────────────
// Global mode: no caseId in route (standalone menu)
// Case-bound mode: caseId present (from case management)
const rawCaseId = computed(() => Number(route.params.caseId) || 0)
const isGlobalMode = computed(() => rawCaseId.value === 0)
const caseId = computed(() => rawCaseId.value)
const suiteId = computed(() => Number(route.query.suiteId) || 0)
const serviceId = computed(() => Number(route.query.serviceId) || Number(route.params.serviceId) || 0)

// ─── State ────────────────────────────────────────────────────────────────────
const caseData = ref<any>(null)
const nodes = ref<WorkflowNode[]>([])
const selectedNodeId = ref<string | null>(null)
const panelVisible = ref(false)
const saving = ref(false)
const loading = ref(false)
const isDirty = ref(false)
let originalScriptJson = ''

// Global mode: editable workflow name
const globalName = ref('新建工作流')

const selectedNode = computed(() => nodes.value.find(n => n.id === selectedNodeId.value) ?? null)

const addNodeGroups = computed(() => {
  const map = new Map<string, typeof ADD_NODE_MENU>()
  for (const item of ADD_NODE_MENU) {
    if (!map.has(item.group)) map.set(item.group, [])
    map.get(item.group)!.push(item)
  }
  return Array.from(map.entries()).map(([name, items]) => ({ name, items }))
})

// ─── Load ─────────────────────────────────────────────────────────────────────
async function loadCase() {
  if (isGlobalMode.value) {
    // Global mode: start with empty canvas
    loading.value = false
    await nextTick()
    dirtyTrackingEnabled = true
    return
  }

  loading.value = true
  try {
    let found: any = null

    if (suiteId.value) {
      const res: any = await api_case_list({ suite_id: suiteId.value })
      const raw = res?.data
      const list: any[] = Array.isArray(raw) ? raw : (Array.isArray(raw?.content) ? raw.content : [])
      found = list.find((c: any) => c.id === caseId.value)
    } else if (serviceId.value) {
      const suitesRes: any = await api_suite_list({ api_service_id: serviceId.value })
      const suites: any[] = Array.isArray(suitesRes?.data) ? suitesRes.data : []
      for (const suite of suites) {
        if (found) break
        try {
          const res: any = await api_case_list({ suite_id: suite.id })
          const raw = res?.data
          const list: any[] = Array.isArray(raw) ? raw : (Array.isArray(raw?.content) ? raw.content : [])
          found = list.find((c: any) => c.id === caseId.value)
        } catch { /* skip */ }
      }
    } else {
      ElMessage.error('请从用例管理页进入工作流编辑器，或在 URL 中提供 suiteId 参数')
      loading.value = false
      return
    }

    if (!found) { ElMessage.error('用例不存在'); router.back(); return }
    caseData.value = found
    const script: any[] = Array.isArray(found.script) ? found.script : []
    originalScriptJson = JSON.stringify(safeCloneScript(script))
    const flat = flattenSteps(script)
    computeLayout(flat, { startX: 60, startY: 200 })
    nodes.value = flat
    isDirty.value = false
    // Enable dirty tracking only after next tick so initial render doesn't trigger it
    await nextTick()
    dirtyTrackingEnabled = true
  } catch (e: any) {
    ElMessage.error(e?.message || '加载用例失败')
  } finally {
    loading.value = false
  }
}

// ─── Save ─────────────────────────────────────────────────────────────────────

// Save-as dialog state (global mode, first save)
const saveAsDialogVisible = ref(false)
const serviceList = ref<any[]>([])
const saveAsSuiteList = ref<any[]>([])
const saveAsForm = ref({ name: '', serviceId: null as number | null, suiteId: null as number | null })

async function onSaveAsServiceChange(svcId: number) {
  saveAsForm.value.suiteId = null
  try {
    const res: any = await api_suite_list({ api_service_id: svcId })
    saveAsSuiteList.value = Array.isArray(res?.data) ? res.data : []
  } catch { saveAsSuiteList.value = [] }
}

async function saveCase() {
  if (isGlobalMode.value && !caseData.value) {
    // First save in global mode: show save-as dialog
    try {
      const r: any = await api_service_list({})
      serviceList.value = Array.isArray(r?.data) ? r.data : (Array.isArray(r?.data?.content) ? r.data.content : [])
    } catch { serviceList.value = [] }
    saveAsForm.value = { name: globalName.value || '新建工作流', serviceId: null, suiteId: null }
    saveAsDialogVisible.value = true
    return
  }

  if (!caseData.value) return
  saving.value = true
  try {
    const script = safeCloneScript(rebuildScript(nodes.value))
    await edit_api_case({ id: caseData.value.id, script, name: isGlobalMode.value ? globalName.value : undefined })
    originalScriptJson = JSON.stringify(script)
    dirtyTrackingEnabled = false
    isDirty.value = false
    await nextTick()
    dirtyTrackingEnabled = true
    ElMessage.success('保存成功')
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function confirmSaveAs() {
  if (!saveAsForm.value.name || !saveAsForm.value.suiteId) {
    ElMessage.warning('请填写用例名称并选择套件')
    return
  }
  saving.value = true
  try {
    const script = safeCloneScript(rebuildScript(nodes.value))
    const res: any = await add_api_case({
      name: saveAsForm.value.name,
      suite_id: saveAsForm.value.suiteId!,
      script,
    })
    const newCase = res?.data
    if (newCase) {
      caseData.value = newCase
      globalName.value = saveAsForm.value.name
    }
    originalScriptJson = JSON.stringify(script)
    isDirty.value = false
    saveAsDialogVisible.value = false
    ElMessage.success('保存成功')
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// ─── Run ──────────────────────────────────────────────────────────────────────
const runDialogVisible = ref(false)
const running = ref(false)
const runForm = ref<any>({ env_id: null })
const envList = ref<any[]>([])

async function openRunDialog() {
  // In global mode, save first if not yet saved
  if (isGlobalMode.value && !caseData.value) {
    ElMessage.warning('请先保存工作流再执行')
    return
  }
  if (isDirty.value) await saveCase()
  if (!caseData.value) return
  try {
    const r: any = await api_env({})
    envList.value = r?.data || []
  } catch { envList.value = [] }
  runForm.value = { env_id: envList.value[0]?.id ?? null }
  runDialogVisible.value = true
}

async function confirmRun() {
  if (!runForm.value.env_id) { ElMessage.warning('请选择执行环境'); return }
  if (!caseData.value) return
  running.value = true
  try {
    const res: any = await run_api_case({
      case_ids: [caseData.value.id],
      env_id: runForm.value.env_id,
      name: `工作流执行_${caseData.value.name || globalName.value}`,
    })
    runDialogVisible.value = false
    const resultId = res?.data?.result_id ?? res?.data?.id ?? ''
    ElMessage.success(resultId ? `执行已提交，结果ID: ${resultId}` : '执行已提交')
  } catch (e: any) {
    ElMessage.error(e?.message || '执行失败')
  } finally {
    running.value = false
  }
}

// ─── Node operations ──────────────────────────────────────────────────────────
function onSelect(nodeId: string) { selectedNodeId.value = nodeId; panelVisible.value = true }

function onMove(nodeId: string, x: number, y: number) {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) { node.x = x; node.y = y; isDirty.value = true }
}

async function onDelete(nodeId: string) {
  try {
    await ElMessageBox.confirm('确认删除该节点及其所有子节点？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
    const toRemove = new Set<string>()
    const collect = (id: string) => { toRemove.add(id); nodes.value.filter(n => n.parentId === id).forEach(c => collect(c.id)) }
    collect(nodeId)
    const target = nodes.value.find(n => n.id === nodeId)
    if (target?.parentId) {
      const parent = nodes.value.find(n => n.id === target.parentId)
      if (parent) parent.step.children_steps = parent.step.children_steps.filter(s => s !== target.step)
    }
    nodes.value = nodes.value.filter(n => !toRemove.has(n.id))
    if (selectedNodeId.value && toRemove.has(selectedNodeId.value)) { selectedNodeId.value = null; panelVisible.value = false }
    isDirty.value = true
  } catch { /* cancelled */ }
}

function onCopy(nodeId: string) {
  const source = nodes.value.find(n => n.id === nodeId)
  if (!source) return
  const newStep = safeCloneScript([source.step])[0]
  newStep._uid = undefined
  const newNode: WorkflowNode = { id: genId(), step: newStep, x: source.x + 20, y: source.y + 20, parentId: source.parentId, branchType: source.branchType, depth: source.depth }
  nodes.value.splice(nodes.value.indexOf(source) + 1, 0, newNode)
  selectedNodeId.value = newNode.id; panelVisible.value = true; isDirty.value = true
}

function onAddAfter(nodeId: string) { showTypePicker(nodeId, 'after') }
function onAddBefore(nodeId: string) { showTypePicker(nodeId, 'before') }
function onAddBranch(nodeId: string, branch: string) { showTypePicker(nodeId, branch) }

const typePicker = ref<{ nodeId: string; mode: string } | null>(null)
function showTypePicker(nodeId: string, mode: string) { typePicker.value = { nodeId, mode } }
function onPickType(type: StepType) {
  if (!typePicker.value) return
  const { nodeId, mode } = typePicker.value
  typePicker.value = null
  _doAddNode(nodeId, mode, type)
}

function _doAddNode(nodeId: string, mode: string, type: StepType) {
  const source = nodes.value.find(n => n.id === nodeId)
  const step = DEFAULT_STEP(type)
  const newNode: WorkflowNode = { id: genId(), step, x: source ? source.x + NODE_W + 80 : 100, y: source ? source.y : 200, parentId: null, branchType: 'main', depth: 0 }

  if (mode === 'after') {
    newNode.parentId = source?.parentId ?? null; newNode.branchType = source?.branchType ?? 'main'; newNode.depth = source?.depth ?? 0
    nodes.value.splice(nodes.value.findIndex(n => n.id === nodeId) + 1, 0, newNode)
  } else if (mode === 'before') {
    newNode.parentId = source?.parentId ?? null; newNode.branchType = source?.branchType ?? 'main'; newNode.depth = source?.depth ?? 0
    newNode.x = source ? source.x - NODE_W - 80 : 100
    nodes.value.splice(nodes.value.findIndex(n => n.id === nodeId), 0, newNode)
  } else if (mode === 'if' || mode === 'else') {
    newNode.parentId = nodeId; newNode.branchType = mode as WorkflowNode['branchType']; newNode.depth = (source?.depth ?? 0) + 1
    newNode.x = source ? source.x + NODE_W + 120 : 300
    const existing = nodes.value.filter(n => n.parentId === nodeId && n.branchType === mode)
    newNode.y = (source ? source.y + (mode === 'else' ? 100 : -100) : 200) + existing.length * 100
    if (source) source.step.children_steps.push(step)
    nodes.value.push(newNode)
  } else if (mode === 'loop') {
    newNode.parentId = nodeId; newNode.branchType = 'loop'; newNode.depth = (source?.depth ?? 0) + 1
    const existing = nodes.value.filter(n => n.parentId === nodeId && n.branchType === 'loop')
    newNode.x = source ? source.x + NODE_W + 80 + existing.length * (NODE_W + 40) : 300
    newNode.y = source ? source.y : 200
    if (source) source.step.children_steps.push(step)
    nodes.value.push(newNode)
  }
  selectedNodeId.value = newNode.id; panelVisible.value = true; isDirty.value = true
}

function onConnect(fromId: string, port: string, toId: string) {
  const from = nodes.value.find(n => n.id === fromId)
  const to = nodes.value.find(n => n.id === toId)
  if (!from || !to || fromId === toId) return
  if (port === 'if' || port === 'else') {
    to.parentId = fromId; to.branchType = port as WorkflowNode['branchType']; to.depth = from.depth + 1
    if (!from.step.children_steps.includes(to.step)) from.step.children_steps.push(to.step)
  } else if (port === 'loop') {
    to.parentId = fromId; to.branchType = 'loop'; to.depth = from.depth + 1
    if (!from.step.children_steps.includes(to.step)) from.step.children_steps.push(to.step)
  } else {
    to.parentId = from.parentId; to.branchType = from.branchType; to.depth = from.depth
    const fromIdx = nodes.value.findIndex(n => n.id === fromId)
    const toIdx = nodes.value.findIndex(n => n.id === toId)
    if (toIdx !== fromIdx + 1) { nodes.value.splice(toIdx, 1); nodes.value.splice(nodes.value.findIndex(n => n.id === fromId) + 1, 0, to) }
  }
  isDirty.value = true
}

function addNode(type: StepType) {
  const step = DEFAULT_STEP(type)
  const newNode: WorkflowNode = { id: genId(), step, x: 80 + Math.random() * 200, y: 80 + Math.random() * 200, parentId: null, branchType: 'main', depth: 0 }
  nodes.value.push(newNode); selectedNodeId.value = newNode.id; panelVisible.value = true; isDirty.value = true
}

function autoLayout() { computeLayout(nodes.value, { startX: 60, startY: 200 }); isDirty.value = true }

// ─── Dirty detection ──────────────────────────────────────────────────────────
let dirtyTrackingEnabled = false

// Watch only the nodes array length/identity changes (shallow), not deep step content
// Deep watching causes stack overflow with many nodes due to nested children_steps
watch(() => nodes.value.length, () => {
  if (dirtyTrackingEnabled) isDirty.value = true
})

// For step content changes, we rely on explicit isDirty = true calls in handlers
// The config panel's @save event also triggers saveCase directly

onBeforeRouteLeave(async (_to, _from, next) => {
  if (!isDirty.value) { next(); return }
  try {
    await ElMessageBox.confirm('有未保存的修改，确认离开？', '提示', { type: 'warning', confirmButtonText: '离开', cancelButtonText: '取消' })
    next()
  } catch { next(false) }
})

function onBeforeUnload(e: BeforeUnloadEvent) { if (isDirty.value) { e.preventDefault(); e.returnValue = '' } }

onMounted(() => { loadCase(); window.addEventListener('beforeunload', onBeforeUnload) })
onUnmounted(() => { window.removeEventListener('beforeunload', onBeforeUnload) })
</script>

<style scoped>
.wfe-root { display: flex; flex-direction: column; height: 100%; min-height: 0; background: var(--el-bg-color-page, #f5f7fa); }
.wfe-toolbar { display: flex; align-items: center; justify-content: space-between; padding: 8px 16px; background: var(--el-bg-color); border-bottom: 1px solid var(--el-border-color-light); flex-shrink: 0; gap: 12px; }
.wfe-toolbar-left { display: flex; align-items: center; gap: 8px; min-width: 0; }
.wfe-case-name { font-size: 15px; font-weight: 600; color: var(--el-text-color-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.wfe-toolbar-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.wfe-dirty-badge { font-size: 12px; color: var(--el-color-warning); background: var(--el-color-warning-light-9); padding: 2px 8px; border-radius: 10px; border: 1px solid var(--el-color-warning-light-5); white-space: nowrap; }
.wfe-body { flex: 1; display: flex; min-height: 0; position: relative; overflow: hidden; }
.wfe-canvas-area { flex: 1; min-width: 0; height: 100%; overflow: hidden; }
.wfe-panel-area { width: 0; height: 100%; position: relative; transition: width 0.25s ease; overflow: hidden; flex-shrink: 0; }
.wfe-panel-area.open { width: 420px; }
</style>

<style>
.wf-type-picker-overlay { position: fixed; inset: 0; z-index: 9999; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.15); }
.wf-type-picker { background: var(--el-bg-color, #fff); border: 1px solid var(--el-border-color-light, #e2e8f0); border-radius: 12px; padding: 12px 0 8px; min-width: 180px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); }
.wf-type-picker__title { font-size: 12px; font-weight: 700; color: var(--el-text-color-secondary, #64748b); padding: 0 16px 8px; border-bottom: 1px solid var(--el-border-color-lighter, #f0f0f0); margin-bottom: 4px; }
.wf-type-picker__group { font-size: 11px; font-weight: 700; color: var(--el-text-color-placeholder, #94a3b8); padding: 6px 16px 2px; letter-spacing: 0.5px; }
.wf-type-picker__item { display: flex; align-items: center; gap: 10px; padding: 8px 16px; font-size: 13px; color: var(--el-text-color-primary, #1e293b); cursor: pointer; transition: background 0.12s; }
.wf-type-picker__item:hover { background: var(--el-fill-color-light, #f8fafc); }
.wf-type-picker__dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
</style>
