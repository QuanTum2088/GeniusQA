<template>
  <div class="sc-root">

    <!-- ── Fullscreen code detail view ── -->
    <div v-if="detailScript" class="sc-fullscreen">
      <div class="sc-fullscreen__header">
        <div class="sc-fullscreen__title">
          <span class="sc-lang-badge">Python</span>
          <span style="color:#cdd6f4;font-size:15px;font-weight:600">{{ detailScript.name }}</span>
          <span v-if="detailScript.description" style="color:#6c7086;font-size:12px">{{ detailScript.description }}</span>
        </div>
        <div class="sc-fullscreen__actions">
          <el-tooltip content="ntest.get('var') / ntest.set('var', val) / ntest.env('KEY')" placement="bottom">
            <el-button type="info" link size="small" style="color:#a6adc8">API 说明</el-button>
          </el-tooltip>
          <el-button type="success" size="small" :loading="running" @click="runScript(detailScript)">
            <el-icon><ele-VideoPlay /></el-icon>&nbsp;运行
          </el-button>
          <el-button size="small" @click="saveDetail">保存</el-button>
          <el-button size="small" @click="detailScript = null">关闭</el-button>
        </div>
      </div>
      <textarea
        v-model="detailScript.code"
        class="sc-fullscreen__editor"
        spellcheck="false"
      />
      <!-- Run output -->
      <div v-if="runOutput !== null" class="sc-run-output">
        <div class="sc-run-output__header">
          <span>执行输出</span>
          <el-button link size="small" @click="runOutput = null">清除</el-button>
        </div>
        <pre class="sc-run-output__body">{{ runOutput }}</pre>
      </div>
    </div>

    <!-- ── List view ── -->
    <template v-else>
      <div class="sc-toolbar">
        <el-input
          v-model="keyword"
          placeholder="搜索脚本名称或描述"
          clearable
          style="width: 260px"
          prefix-icon="ele-Search"
        />
        <el-button type="primary" @click="openAdd">
          <el-icon><ele-Plus /></el-icon>&nbsp;新增脚本
        </el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="filteredList"
        border
        stripe
        empty-text="暂无脚本"
        style="width: 100%"
      >
        <el-table-column label="脚本名称" min-width="180">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDetail(row)">{{ row.name }}</el-button>
          </template>
        </el-table-column>
        <el-table-column label="脚本类型" width="90" align="center">
          <template #default>
            <el-tag size="small" style="background:#3776ab;border:none;color:#fff;font-weight:700">Py</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="备注" min-width="160" show-overflow-tooltip />
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <div style="display:flex;gap:4px;justify-content:center;flex-wrap:nowrap;white-space:nowrap">
              <el-button type="primary" size="small" @click="openFuncList(row)">函数列表</el-button>
              <el-button type="warning" size="small" @click="openEdit(row)">编辑</el-button>
              <el-button type="danger" size="small" @click="deleteScript(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </template>

    <!-- ── Add / Edit dialog ── -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑脚本' : '新增脚本'"
      width="720px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="脚本名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入脚本名称" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.description" placeholder="可选描述" />
        </el-form-item>
        <el-form-item label="代码">
          <div class="sc-editor-wrap">
            <div class="sc-editor-toolbar">
              <span class="sc-lang-badge">Python</span>
              <el-tooltip placement="top" :show-after="200">
                <template #content>
                  <div style="font-size:12px;line-height:1.8">
                    <b>ntest API 使用说明</b><br/>
                    <code>ntest.get('var')</code> — 读取变量<br/>
                    <code>ntest.set('var', val)</code> — 写入变量<br/>
                    <code>ntest.env('KEY')</code> — 读取环境变量
                  </div>
                </template>
                <el-icon style="cursor:pointer;color:#94a3b8"><ele-QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
            <textarea
              v-model="form.code"
              class="sc-code-editor"
              placeholder="# 在此编写 Python 脚本&#10;# ntest.set('result', 'hello')&#10;# val = ntest.get('some_var')"
              spellcheck="false"
            />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>

    <!-- ── 函数列表 dialog ── -->
    <el-dialog
      v-model="funcListVisible"
      :title="`函数列表 — ${funcListScript?.name || ''}`"
      width="760px"
      :close-on-click-modal="false"
    >
      <div style="margin-bottom:10px;display:flex;gap:8px">
        <el-input v-model="funcSearch" placeholder="输入函数名或说明查询" clearable style="width:240px" />
      </div>
      <div style="max-height:480px;overflow-y:auto">
        <el-table :data="filteredFuncs" border stripe empty-text="未解析到函数定义">
          <el-table-column prop="name" label="函数名称" width="200">
            <template #default="{ row }">
              <code style="color:#6366f1;font-weight:700">{{ row.name }}</code>
            </template>
          </el-table-column>
          <el-table-column prop="args" label="参数" width="200">
            <template #default="{ row }">
              <code style="color:#94a3b8">{{ row.args }}</code>
            </template>
          </el-table-column>
          <el-table-column prop="doc" label="说明" show-overflow-tooltip />
          <el-table-column label="操作" width="80" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="openDebugFunc(row)">调试</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- ── 函数调试 dialog ── -->
    <el-dialog
      v-model="debugFuncVisible"
      :title="`函数调试 — ${debugFunc?.name || ''}`"
      width="600px"
      :close-on-click-modal="false"
      append-to-body
      destroy-on-close
    >
      <el-descriptions :title="`${debugFunc?.name}(${debugFunc?.args})`" :column="1" border size="small">
        <template #extra>
          <el-button type="primary" :loading="running" @click="execDebugFunc">执行</el-button>
        </template>
        <el-descriptions-item label="说明" width="100px">
          <span style="white-space:pre-wrap;font-weight:600">{{ debugFunc?.doc || '—' }}</span>
        </el-descriptions-item>
        <el-descriptions-item
          v-for="(_, key) in debugFuncArgs"
          :key="key"
          :label="String(key)"
          width="100px"
        >
          <el-input v-model="debugFuncArgs[key]" />
        </el-descriptions-item>
        <el-descriptions-item label="执行结果" width="100px">
          <pre class="sc-debug-result">{{ debugFuncResult ?? '（点击执行）' }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useApiAutomationApi } from '/@/api/v1/testing/apiAutomation'

const props = defineProps<{ serviceId: number }>()

const { ntest_script_list, add_ntest_script, edit_ntest_script, del_ntest_script, run_api_script, get_api_script_result } = useApiAutomationApi()

// ─── State ────────────────────────────────────────────────────────────────────
const scriptList = ref<any[]>([])
const keyword = ref('')
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<any>(null)
const form = ref({ id: undefined as number | undefined, name: '', description: '', code: '' })

// Detail / fullscreen
const detailScript = ref<any>(null)

// Run state
const running = ref(false)
const runningId = ref<number | null>(null)
const runOutput = ref<string | null>(null)

// ─── 函数列表 state ───────────────────────────────────────────────────────────
const funcListVisible = ref(false)
const funcListScript = ref<any>(null)
const funcSearch = ref('')
const parsedFuncs = ref<{ name: string; args: string; doc: string }[]>([])

const filteredFuncs = computed(() => {
  const kw = funcSearch.value.trim().toLowerCase()
  if (!kw) return parsedFuncs.value
  return parsedFuncs.value.filter(f =>
    f.name.toLowerCase().includes(kw) || f.doc.toLowerCase().includes(kw)
  )
})

// Debug func state
const debugFuncVisible = ref(false)
const debugFunc = ref<any>(null)
const debugFuncArgs = ref<Record<string, string>>({})
const debugFuncResult = ref<string | null>(null)

const rules = {
  name: [{ required: true, message: '请输入脚本名称', trigger: 'blur' }],
}

const filteredList = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return scriptList.value
  return scriptList.value.filter(s =>
    (s.name || '').toLowerCase().includes(kw) ||
    (s.description || '').toLowerCase().includes(kw)
  )
})

// ─── Methods ──────────────────────────────────────────────────────────────────
async function loadScripts() {
  loading.value = true
  try {
    const res: any = await ntest_script_list({ api_service_id: props.serviceId })
    scriptList.value = Array.isArray(res?.data) ? res.data : []
  } catch {
    scriptList.value = []
  } finally {
    loading.value = false
  }
}

function openAdd() {
  isEdit.value = false
  form.value = { id: undefined, name: '', description: '', code: '' }
  dialogVisible.value = true
}

function openEdit(row: any) {
  isEdit.value = true
  form.value = { id: row.id, name: row.name, description: row.description || '', code: row.code || '' }
  dialogVisible.value = true
}

function openDetail(row: any) {
  // Deep copy so edits don't affect list until saved
  detailScript.value = { ...row }
  runOutput.value = null
}

async function saveDetail() {
  if (!detailScript.value) return
  saving.value = true
  try {
    await edit_ntest_script({
      id: detailScript.value.id,
      name: detailScript.value.name,
      description: detailScript.value.description,
      code: detailScript.value.code,
    })
    ElMessage.success('保存成功')
    await loadScripts()
    // Sync back to list
    const idx = scriptList.value.findIndex(s => s.id === detailScript.value.id)
    if (idx >= 0) scriptList.value[idx] = { ...detailScript.value }
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function submitForm() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (isEdit.value && form.value.id) {
      await edit_ntest_script({ id: form.value.id, name: form.value.name, description: form.value.description, code: form.value.code })
      ElMessage.success('编辑成功')
    } else {
      await add_ntest_script({ name: form.value.name, description: form.value.description, code: form.value.code, api_service_id: props.serviceId })
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    await loadScripts()
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败')
  } finally {
    saving.value = false
  }
}

async function deleteScript(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除脚本「${row.name}」？`, '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
    await del_ntest_script({ id: row.id })
    ElMessage.success('删除成功')
    await loadScripts()
  } catch {
    // cancelled
  }
}

async function runScript(row: any) {
  const code = row.code || ''
  if (!code.trim()) {
    ElMessage.warning('脚本内容为空，无法运行')
    return
  }
  if (detailScript.value) {
    running.value = true
  } else {
    runningId.value = row.id
  }
  runOutput.value = null
  try {
    // Execute via backend run_api_script with a minimal script step
    const resultId = Date.now()
    const res: any = await run_api_script({
      result_id: resultId,
      name: row.name,
      script: [
        {
          step_type: 'script',
          name: row.name,
          enable: true,
          request: { script_content: code },
          extracts: [],
          validators: [],
          children_steps: [],
        },
      ],
      config: { env_id: 0 },
    })
    const result = res?.data
    const stepResult = Array.isArray(result?.result) ? result.result[0] : null
    if (stepResult) {
      const output = stepResult.response?.body?.output || ''
      const vars = stepResult.response?.body?.vars || {}
      const lines = []
      if (output) lines.push('--- 输出 ---\n' + output)
      if (Object.keys(vars).length) lines.push('--- 变量 ---\n' + JSON.stringify(vars, null, 2))
      if (stepResult.error) lines.push('--- 错误 ---\n' + stepResult.error)
      runOutput.value = lines.join('\n') || '执行完成（无输出）'
    } else {
      runOutput.value = JSON.stringify(result, null, 2)
    }
  } catch (e: any) {
    runOutput.value = '运行失败: ' + (e?.message || String(e))
  } finally {
    running.value = false
    runningId.value = null
  }
}

// ─── 函数列表 ─────────────────────────────────────────────────────────────────
function parseFunctions(code: string): { name: string; args: string; doc: string }[] {
  const funcs: { name: string; args: string; doc: string }[] = []
  if (!code) return funcs
  // Match: def funcname(args): followed by optional docstring
  const defRe = /^def\s+(\w+)\s*\(([^)]*)\)\s*:/gm
  let m: RegExpExecArray | null
  while ((m = defRe.exec(code)) !== null) {
    const name = m[1]
    const args = m[2].trim()
    // Try to extract docstring (first string literal after def line)
    const afterDef = code.slice(m.index + m[0].length)
    const docMatch = afterDef.match(/^\s*(?:"""([\s\S]*?)"""|'''([\s\S]*?)''')/)
    const doc = docMatch ? (docMatch[1] || docMatch[2] || '').trim() : ''
    funcs.push({ name, args, doc })
  }
  return funcs
}

function openFuncList(row: any) {
  funcListScript.value = row
  funcSearch.value = ''
  parsedFuncs.value = parseFunctions(row.code || '')
  funcListVisible.value = true
}

function openDebugFunc(func: any) {
  debugFunc.value = func
  debugFuncResult.value = null
  // Build args dict from param names
  const argNames = func.args
    ? func.args.split(',').map((a: string) => a.trim().split('=')[0].trim()).filter(Boolean)
    : []
  const argsObj: Record<string, string> = {}
  for (const a of argNames) argsObj[a] = ''
  debugFuncArgs.value = argsObj
  debugFuncVisible.value = true
}

async function execDebugFunc() {
  if (!debugFunc.value || !funcListScript.value) return
  running.value = true
  debugFuncResult.value = '执行中...'
  try {
    const callCode = `${debugFunc.value.name}(${Object.values(debugFuncArgs.value).map(v => {
      try { return JSON.stringify(JSON.parse(v)) } catch { return JSON.stringify(v) }
    }).join(', ')})`
    const fullCode = `${funcListScript.value.code || ''}\n\n_result = ${callCode}\nntest.set('_result', _result)\nprint('结果:', _result)`
    const resultId = Date.now()

    await run_api_script({
      result_id: resultId,
      name: `调试: ${debugFunc.value.name}`,
      script: [{
        step_type: 'script',
        name: `调试: ${debugFunc.value.name}`,
        enable: true,
        request: { script_content: fullCode },
        extracts: [],
        validators: [],
        children_steps: [],
      }],
      config: { env_id: 0 },
    })

    // Poll for results (max 10s)
    let attempts = 0
    const poll = async (): Promise<void> => {
      attempts++
      const res: any = await get_api_script_result({ result_id: resultId })
      const list: any[] = Array.isArray(res?.data) ? res.data : []
      // Filter out the "执行结束" summary row, find the script step result
      const step = list.find((r: any) => r.name !== '执行结束' && r.name !== '执行开始')
      if (step || attempts >= 10) {
        if (!step) {
          debugFuncResult.value = '执行超时，未获取到结果'
          return
        }
        // res field contains { body: { output, vars }, code }
        const resBody = step.res?.body || step.res || {}
        const output: string = resBody.output || ''
        const vars: Record<string, any> = resBody.vars || {}
        const error: string = step.res?.error || step.error || ''
        const lines: string[] = []
        if (vars._result !== undefined) {
          lines.push('返回值:\n' + JSON.stringify(vars._result, null, 2))
        }
        if (output.trim()) {
          lines.push('输出:\n' + output.trim())
        }
        if (error) {
          lines.push('错误:\n' + error)
        }
        if (!lines.length) {
          // Show raw response for debugging
          lines.push(JSON.stringify(step.res, null, 2) || '执行完成（无输出）')
        }
        debugFuncResult.value = lines.join('\n\n')
      } else {
        await new Promise(r => setTimeout(r, 1000))
        return poll()
      }
    }
    await new Promise(r => setTimeout(r, 1200)) // wait for execution to complete
    await poll()
  } catch (e: any) {
    debugFuncResult.value = '执行失败: ' + (e?.message || String(e))
  } finally {
    running.value = false
  }
}

onMounted(loadScripts)
</script>

<style scoped>
.sc-root {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  box-sizing: border-box;
}

.sc-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

/* ── Fullscreen editor ── */
.sc-fullscreen {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1e1e2e;
  border-radius: 8px;
  overflow: hidden;
}

.sc-fullscreen__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: #181825;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.sc-fullscreen__title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sc-fullscreen__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sc-fullscreen__editor {
  flex: 1;
  width: 100%;
  padding: 16px;
  background: #1e1e2e;
  color: #cdd6f4;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.7;
  border: none;
  outline: none;
  resize: none;
  box-sizing: border-box;
  tab-size: 4;
}

/* ── Run output panel ── */
.sc-run-output {
  flex-shrink: 0;
  max-height: 200px;
  background: #11111b;
  border-top: 1px solid #313244;
  display: flex;
  flex-direction: column;
}

.sc-run-output__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 12px;
  font-size: 12px;
  color: #a6adc8;
  background: #181825;
}

.sc-run-output__body {
  flex: 1;
  overflow-y: auto;
  padding: 8px 12px;
  margin: 0;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
  color: #a6e3a1;
  white-space: pre-wrap;
  word-break: break-all;
}

/* ── Dialog editor ── */
.sc-editor-wrap {
  width: 100%;
  border: 1px solid var(--el-border-color, #dcdfe6);
  border-radius: 6px;
  overflow: hidden;
}

.sc-editor-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #2a2a3e;
  border-bottom: 1px solid #3a3a4e;
}

.sc-lang-badge {
  font-size: 11px;
  font-weight: 700;
  color: #a78bfa;
  background: rgba(167,139,250,0.15);
  padding: 1px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

.sc-code-editor {
  width: 100%;
  min-height: 280px;
  padding: 12px;
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

.sc-debug-result {
  margin: 0;
  padding: 8px;
  background: #1e1e2e;
  color: #a6e3a1;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-all;
  min-height: 60px;
  max-height: 200px;
  overflow-y: auto;
}
</style>
