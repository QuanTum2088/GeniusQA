<template>
  <div class="api-step-form">
    <el-form-item label="选择接口">
      <el-cascader
        v-model="selectedPath"
        :options="apiTree"
        :props="{ value: 'id', label: 'name', children: 'children', checkStrictly: false, emitPath: true }"
        placeholder="请选择接口"
        filterable
        clearable
        style="width: 100%"
        @change="onSelect"
      >
        <template #default="{ data }">
          <span style="display:flex;align-items:center;gap:6px">
            <el-tag v-if="data.method_name" size="small" :color="methodColor(data.method_name)"
              style="color:#fff;border:none;font-size:10px;padding:0 4px;height:16px;line-height:16px">
              {{ data.method_name }}
            </el-tag>
            {{ data.name }}
          </span>
        </template>
      </el-cascader>
    </el-form-item>
    <div v-if="step.request?.api_id" class="api-selected-info">
      <el-tag size="small" type="info">ID: {{ step.request.api_id }}</el-tag>
      <span class="api-name">{{ step.name }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiAutomationApi } from '/@/api/v1/testing/apiAutomation'

const props = defineProps<{ step: any; serviceId?: number }>()

const apiTree = ref<any[]>([])
const selectedPath = ref<any[]>([])

const METHOD_COLORS: Record<string, string> = {
  GET: '#10b981', POST: '#6366f1', PUT: '#f59e0b',
  DELETE: '#ef4444', PATCH: '#0ea5e9',
}
const methodColor = (m: string) => METHOD_COLORS[m?.toUpperCase()] || '#94a3b8'

const onSelect = (path: any[]) => {
  if (!path?.length) return
  const lastId = path[path.length - 1]
  // Find leaf node iteratively
  const findNode = (nodes: any[], id: number): any => {
    const stack = [...nodes]
    while (stack.length) {
      const n = stack.pop()
      if (n.id === id) return n
      if (n.children?.length) stack.push(...n.children)
    }
    return null
  }
  const node = findNode(apiTree.value, lastId)
  if (node && !node.children?.length) {
    if (!props.step.request) props.step.request = {}
    props.step.request.api_id = node.api_id || node.id
    if (!props.step.name) props.step.name = node.name
  }
}

onMounted(async () => {
  try {
    const r: any = await apiAutomationApi.api_tree({
      search: props.serviceId ? { api_service_id: props.serviceId } : {}
    })
    apiTree.value = Array.isArray(r?.data) ? r.data : []

    // Restore selectedPath from saved api_id
    const savedId = props.step.request?.api_id
    if (savedId) {
      const path = findPath(apiTree.value, savedId)
      if (path) selectedPath.value = path
    }
  } catch { apiTree.value = [] }
})

/** Find the path of ids from root to the node with matching api_id or id — iterative BFS */
function findPath(nodes: any[], targetId: number): number[] | null {
  const queue: Array<{ node: any; path: number[] }> = nodes.map(n => ({ node: n, path: [n.id] }))
  while (queue.length) {
    const { node, path } = queue.shift()!
    if (node.api_id === targetId || node.id === targetId) return path
    if (node.children?.length) {
      for (const child of node.children) {
        queue.push({ node: child, path: [...path, child.id] })
      }
    }
  }
  return null
}
</script>

<style scoped>
.api-step-form { padding: 4px 0; }
.api-selected-info { display: flex; align-items: center; gap: 8px; margin-top: 4px; font-size: 12px; }
.api-name { color: var(--el-text-color-regular); }
</style>
