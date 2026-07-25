<template>
  <div class="script-step-form">
    <!-- Public script selector -->
    <el-form-item label="引用公共脚本" style="margin-bottom: 8px">
      <el-select
        v-model="req.script_id"
        placeholder="引用公共脚本（可选）"
        clearable
        style="width: 100%"
      >
        <el-option
          v-for="s in publicScripts"
          :key="s.id"
          :label="s.name"
          :value="s.id"
        />
      </el-select>
      <div v-if="req.script_id" style="font-size:11px;color:#94a3b8;margin-top:4px">
        公共脚本将在内联代码之前执行
      </div>
    </el-form-item>

    <!-- Code editor -->
    <div class="script-toolbar">
      <span class="script-lang">Python</span>
      <el-tooltip placement="top" :show-after="200">
        <template #content>
          <div style="font-size:12px;line-height:1.8">
            <b>ntest API 使用说明</b><br/>
            <code>ntest.get('var')</code> — 读取变量<br/>
            <code>ntest.set('var', val)</code> — 写入变量<br/>
            <code>ntest.env('KEY')</code> — 读取环境变量
          </div>
        </template>
        <el-button type="info" link size="small">API 说明</el-button>
      </el-tooltip>
    </div>
    <textarea
      v-model="req.script_content"
      class="script-editor"
      placeholder="# 示例：
# token = ntest.get('token')
# ntest.set('new_var', token + '_suffix')
# print('调试输出')
"
      spellcheck="false"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useApiAutomationApi } from '/@/api/v1/testing/apiAutomation'

const props = defineProps<{ step: any; serviceId?: number }>()

const { ntest_script_list } = useApiAutomationApi()

const publicScripts = ref<{ id: number; name: string }[]>([])

const req = computed(() => {
  if (!props.step.request) props.step.request = { script_content: '', script_id: undefined }
  if (!('script_id' in props.step.request)) props.step.request.script_id = undefined
  return props.step.request
})

onMounted(async () => {
  if (!props.serviceId) return
  try {
    const res: any = await ntest_script_list({ api_service_id: props.serviceId })
    publicScripts.value = Array.isArray(res?.data) ? res.data.map((s: any) => ({ id: s.id, name: s.name })) : []
  } catch {
    publicScripts.value = []
  }
})
</script>

<style scoped>
.script-step-form { display: flex; flex-direction: column; gap: 4px; }
.script-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  background: #1e1e2e; border-radius: 6px 6px 0 0; padding: 4px 10px;
}
.script-lang { font-size: 11px; color: #a6adc8; font-family: monospace; }
.script-editor {
  width: 100%; min-height: 140px; padding: 10px 12px;
  background: #1e1e2e; color: #cdd6f4;
  border: none; border-radius: 0 0 6px 6px;
  font-family: 'Fira Code', 'Consolas', monospace; font-size: 13px;
  line-height: 1.6; resize: vertical; outline: none;
  box-sizing: border-box;
}
</style>
