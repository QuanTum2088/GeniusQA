<template>
  <div class="skill-page">
    <div class="skill-toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">Skill 管理</h2>
        <el-select v-model="projectId" placeholder="选择项目" style="width: 220px" @change="onProjectChange">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>
      <div class="toolbar-actions">
        <el-button type="success" @click="openEditDialog()">新建 Skill</el-button>
        <el-button type="primary" @click="openGitDialog">Git 导入</el-button>
        <el-upload :show-file-list="false" accept=".zip" :before-upload="onUploadZip">
          <el-button>上传 ZIP</el-button>
        </el-upload>
      </div>
    </div>

    <div class="skill-filters">
      <el-input
        v-model="query.search"
        clearable
        placeholder="搜索技能名称"
        style="width: 220px"
        @keyup.enter="loadSkills"
      />
      <el-input
        v-model="query.scenario_category"
        clearable
        placeholder="场景分类"
        style="width: 220px"
        @keyup.enter="loadSkills"
      />
      <el-button type="primary" @click="loadSkills">查询</el-button>
      <el-button @click="resetQuery">重置</el-button>
    </div>

    <div v-loading="loading" class="skill-grid-wrap">
      <div v-if="!projectId" class="skill-empty">请先选择项目</div>
      <div v-else-if="!rows.length" class="skill-empty">暂无 Skill，可新建、Git 导入或上传 ZIP</div>
      <div v-else class="skill-grid">
        <article v-for="s in rows" :key="s.id" class="skill-card">
          <header class="skill-card__head">
            <div class="skill-card__identity">
              <h3 class="skill-card__name" :title="s.name">{{ s.name }}</h3>
              <div class="skill-card__tags">
                <el-tag size="small" type="info">{{ s.scenario_category || '未分类' }}</el-tag>
                <el-tag size="small">{{ s.source_type || '-' }}</el-tag>
              </div>
            </div>
            <el-switch
              v-model="s.is_active"
              inline-prompt
              active-text="开"
              inactive-text="关"
              @change="onToggleActive(s)"
            />
          </header>

          <p class="skill-card__desc" :title="s.description || ''">
            {{ s.description || '暂无描述' }}
          </p>

          <div class="skill-card__meta">
            <div class="meta-row" :title="s.entry_command || ''">
              <span class="meta-label">命令</span>
              <span class="meta-value">{{ s.entry_command || '-' }}</span>
            </div>
            <div class="meta-row" :title="s.allowed_tools || ''">
              <span class="meta-label">工具</span>
              <span class="meta-value">{{ s.allowed_tools || '-' }}</span>
            </div>
          </div>

          <footer class="skill-card__foot">
            <div class="foot-main">
              <el-button type="primary" size="small" @click="onRun(s)">执行</el-button>
              <el-dropdown
                v-if="hasQuickActions(s) || manifestCache[s.id]?.loading"
                trigger="click"
                @command="(cmd) => onQuickCommand(s, cmd)"
              >
                <el-button size="small">快捷执行 ▾</el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <template v-if="manifestCache[s.id]?.loading">
                      <el-dropdown-item disabled>加载中…</el-dropdown-item>
                    </template>
                    <template v-else>
                      <el-dropdown-item
                        v-for="qa in quickActionsForSkill(s)"
                        :key="qa.key"
                        :command="`qa:${qa.key}`"
                      >
                        {{ qa.title }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        v-for="(t, idx) in manifestCache[s.id]?.templates || []"
                        :key="t.name"
                        :command="`tpl:${t.name}`"
                        :divided="idx === 0 && quickActionsForSkill(s).length > 0"
                      >
                        {{ templateLabel(t.name) }}
                      </el-dropdown-item>
                    </template>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button link type="primary" @click="openEditDialog(s)">编辑</el-button>
              <el-button link type="primary" @click="onViewContent(s)">查看内容</el-button>
            </div>
            <el-button link type="danger" class="foot-delete" @click="onDelete(s)">删除</el-button>
          </footer>
        </article>
      </div>
    </div>

    <div class="pager">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[12, 24, 48, 96]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadSkills"
        @size-change="loadSkills"
      />
    </div>

    <el-dialog v-model="gitDialogVisible" title="Git 导入 Skill" width="560px">
      <el-form label-width="90px">
        <el-form-item label="仓库地址">
          <el-input v-model="gitForm.repo_url" placeholder="https://github.com/... 或 https://gitee.com/..." />
        </el-form-item>
        <el-form-item label="技能名">
          <el-input v-model="gitForm.name" placeholder="可选，不填自动生成" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="gitForm.scenario_category" placeholder="如 agent-browser-skill" />
        </el-form-item>
        <el-form-item label="执行命令">
          <el-input v-model="gitForm.entry_command" placeholder="默认 python main.py" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="gitDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="gitSubmitting" @click="submitGitImport">导入</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="contentDialogVisible" title="Skill 内容" width="860px">
      <el-input v-model="skillContent" type="textarea" :rows="26" readonly />
    </el-dialog>

    <el-dialog v-model="editDialogVisible" :title="editForm.id ? '编辑 Skill' : '新建 Skill'" width="620px">
      <el-form label-width="100px">
        <el-form-item label="技能名称">
          <el-input v-model="editForm.name" placeholder="如 agent-browser-skill" />
        </el-form-item>
        <el-form-item label="技能描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="请输入技能描述" />
        </el-form-item>
        <el-form-item label="场景分类">
          <el-input v-model="editForm.scenario_category" placeholder="如 agent-browser-skill" />
        </el-form-item>
        <el-form-item label="来源类型">
          <el-select v-model="editForm.source_type" style="width: 100%">
            <el-option label="builtin" value="builtin" />
            <el-option label="github" value="github" />
            <el-option label="gitee" value="gitee" />
            <el-option label="upload" value="upload" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库URL">
          <el-input v-model="editForm.repo_url" placeholder="可选，来源为 git 时填写" />
        </el-form-item>
        <el-form-item label="技能目录">
          <el-input v-model="editForm.skill_path" placeholder="本地技能目录路径（可选）" />
        </el-form-item>
        <el-form-item label="执行命令">
          <el-input v-model="editForm.entry_command" placeholder="如 python main.py / node run.js" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editSubmitting" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="runDialogVisible" title="执行 Skill" width="760px">
      <el-form label-width="110px">
        <el-form-item label="目标技能">
          <el-input :model-value="`${runTarget?.name || ''} (#${runTarget?.id || ''})`" readonly />
        </el-form-item>
        <el-form-item label="执行方式">
          <el-switch v-model="runForm.asyncMode" active-text="后台任务(job)" inactive-text="同步执行" />
        </el-form-item>
        <el-form-item v-if="runForm.asyncMode" label="runner">
          <el-select v-model="runForm.runnerType" style="width: 100%">
            <el-option label="local（本机）" value="local" />
            <el-option label="docker（推荐生产）" value="docker" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="runManifest.allowed_tools" label="allowed-tools">
          <el-input :model-value="runManifest.allowed_tools" type="textarea" :rows="3" readonly />
        </el-form-item>
        <el-form-item v-if="(runManifest.templates || []).length" label="templates">
          <el-table :data="runManifest.templates" size="small" max-height="180">
            <el-table-column prop="name" label="文件名" min-width="160" show-overflow-tooltip />
            <el-table-column prop="relative_path" label="相对路径" min-width="220" show-overflow-tooltip />
            <el-table-column prop="size" label="大小" width="90" />
          </el-table>
        </el-form-item>
        <el-form-item v-if="(runManifest.templates || []).length" label="模板选择">
          <el-select v-model="runForm.templateName" clearable filterable placeholder="可选：选择一个模板执行" style="width: 100%">
            <el-option v-for="t in runManifest.templates" :key="t.name" :label="t.name" :value="t.name" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="runForm.templateName" label="模板参数">
          <el-input
            v-model="runForm.templateArgsText"
            type="textarea"
            :rows="3"
            placeholder='JSON 数组，例如: ["https://example.com","./output"]'
          />
        </el-form-item>
        <el-form-item label="session_id">
          <el-input v-model="runForm.session_id" placeholder="可选；填写后可复用会话上下文" />
        </el-form-item>
        <el-collapse v-model="runAdvancedOpen" class="run-advanced">
          <el-collapse-item title="高级编排（JSON，可覆盖上方模板参数）" name="adv">
            <el-input
              v-model="runForm.argumentsText"
              type="textarea"
              :rows="8"
              placeholder='例如: {"command":"npx agent-browser open https://example.com"} 会与模板合并，同名键以本 JSON 为准'
            />
          </el-collapse-item>
        </el-collapse>
      </el-form>
      <template #footer>
        <el-button @click="runDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="runSubmitting" @click="submitRun">开始执行</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="resultDrawerVisible" class="result-drawer" title="执行结果详情" size="62%">
      <div class="result-content">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="skill">{{ runResult.skill_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="skill_id">{{ runResult.skill_id ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="job_id">{{ runResult.job_id ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="session_id">{{ runResult.session_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="return_code">{{ runResult.return_code ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="runResult.ok ? 'success' : 'danger'">{{ runResult.ok ? '成功' : '失败' }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <div class="result-block">
        <div class="result-title">stdout</div>
        <el-input :model-value="runResult.stdout || ''" type="textarea" :rows="10" readonly />
      </div>
      <div class="result-block">
        <div class="result-title">stderr</div>
        <el-input :model-value="runResult.stderr || ''" type="textarea" :rows="8" readonly />
      </div>

      <el-row :gutter="12" class="result-files">
        <el-col :span="12">
          <el-card>
            <template #header>screenshots ({{ (runResult.screenshots || []).length }})</template>
            <el-table :data="runResult.screenshots || []" size="small" max-height="240">
              <el-table-column prop="name" label="文件名" min-width="140" show-overflow-tooltip />
              <el-table-column prop="relative_path" label="相对路径" min-width="180" show-overflow-tooltip />
              <el-table-column prop="size" label="大小" width="90" />
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button link type="primary" @click="openArtifact(row)">预览</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>artifacts ({{ (runResult.artifacts || []).length }})</template>
            <el-table :data="runResult.artifacts || []" size="small" max-height="240">
              <el-table-column prop="name" label="文件名" min-width="140" show-overflow-tooltip />
              <el-table-column prop="relative_path" label="相对路径" min-width="180" show-overflow-tooltip />
              <el-table-column prop="size" label="大小" width="90" />
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button link type="primary" @click="downloadArtifact(row)">下载</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { UploadRawFile } from 'element-plus';
import { useProjectApi } from '/@/api/v1/projects/project';
import { skillsApi } from '/@/api/v1/ai/skills';
import { Session } from '/@/utils/storage';
import { getApiBaseUrl } from '/@/utils/config';

const projectApi = useProjectApi();

const loading = ref(false);
const projects = ref<Array<{ id: number; name: string }>>([]);
const projectId = ref<number | null>(null);
const rows = ref<any[]>([]);
const total = ref(0);
const query = reactive({
  search: '',
  scenario_category: '',
  page: 1,
  page_size: 12,
});
const manifestCache = reactive<Record<number, { templates: any[]; loading: boolean; loaded: boolean }>>({});

const gitDialogVisible = ref(false);
const gitSubmitting = ref(false);
const gitForm = reactive({
  repo_url: '',
  name: '',
  scenario_category: '',
  entry_command: '',
});

const contentDialogVisible = ref(false);
const skillContent = ref('');
const editDialogVisible = ref(false);
const editSubmitting = ref(false);
const editForm = reactive<any>({
  id: undefined,
  name: '',
  description: '',
  scenario_category: '',
  source_type: 'builtin',
  repo_url: '',
  skill_path: '',
  entry_command: '',
});
const runDialogVisible = ref(false);
const runSubmitting = ref(false);
const runTarget = ref<any>(null);
const runForm = reactive({
  asyncMode: true,
  runnerType: 'docker',
  session_id: '',
  templateName: '',
  templateArgsText: '[]',
  argumentsText: '{}',
});
const runAdvancedOpen = ref<string[]>(['adv']);
const runManifest = reactive<any>({
  allowed_tools: '',
  templates: [],
});
const resultDrawerVisible = ref(false);
const runResult = reactive<any>({
  ok: false,
  job_id: null,
  skill_name: '',
  skill_id: null,
  session_id: '',
  return_code: null,
  stdout: '',
  stderr: '',
  screenshots: [],
  artifacts: [],
});

const apiBaseUrl = getApiBaseUrl();

const fetchSse = async (url: string, onEvent: (evt: { event: string; data: any }) => void, timeoutMs = 15000) => {
  const token = Session.get('token');
  const ctl = new AbortController();
  const timer = window.setTimeout(() => ctl.abort('timeout'), timeoutMs);
  const resp = await fetch(url, {
    method: 'GET',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}`, token: `${token}` } : {}),
      Accept: 'text/event-stream',
    },
    signal: ctl.signal,
  });
  if (!resp.ok || !resp.body) {
    clearTimeout(timer);
    throw new Error(`SSE连接失败: ${resp.status}`);
  }
  const reader = resp.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buf = '';
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      clearTimeout(timer);
      window.setTimeout(() => ctl.abort('timeout'), timeoutMs);
      buf += decoder.decode(value, { stream: true });
      const parts = buf.split('\n\n');
      buf = parts.pop() || '';
      for (const part of parts) {
        const lines = part.split('\n').filter(Boolean);
        let event = 'message';
        let dataStr = '';
        for (const line of lines) {
          if (line.startsWith('event:')) event = line.slice(6).trim();
          if (line.startsWith('data:')) dataStr += line.slice(5).trim();
        }
        let data: any = dataStr;
        try {
          data = dataStr ? JSON.parse(dataStr) : {};
        } catch {
          // keep raw
        }
        onEvent({ event, data });
      }
    }
  } finally {
    clearTimeout(timer);
  }
};

const artifactUrl = (kind: 'screenshots' | 'artifacts', id: number) => {
  if (!projectId.value) return '';
  return `${apiBaseUrl}${skillsApi.artifactDownloadUrl(projectId.value, id)}`;
};

const openArtifact = (row: any) => {
  // screenshots: open in new tab
  if (!row?.id) {
    ElMessage.warning('同步执行的截图未入库，暂不支持下载/预览接口');
    return;
  }
  const url = artifactUrl('screenshots', Number(row.id));
  if (url) window.open(url, '_blank');
};

const downloadArtifact = (row: any) => {
  if (!row?.id) {
    ElMessage.warning('同步执行的产物未入库，暂不支持下载接口');
    return;
  }
  const url = artifactUrl('artifacts', Number(row.id));
  if (url) window.open(url, '_blank');
};

const pollJobUntilDone = async (jobId: number) => {
  if (!projectId.value) return;
  for (let i = 0; i < 120; i += 1) {
    const r: any = await skillsApi.job(projectId.value, jobId);
    const d = r?.data || {};
    runResult.return_code = d.return_code ?? null;
    runResult.stderr = d.stderr || runResult.stderr;
    runResult.stdout = d.stdout || runResult.stdout;
    if (['succeeded', 'failed', 'cancelled'].includes(String(d.status || ''))) {
      runResult.ok = d.status === 'succeeded';
      const arts: any = await skillsApi.jobArtifacts(projectId.value, jobId);
      const items = arts?.data?.items || [];
      runResult.screenshots = items.filter((x: any) => x.kind === 'screenshots');
      runResult.artifacts = items.filter((x: any) => x.kind === 'artifacts');
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
};

const templateLabel = (fileName: string) =>
  String(fileName || '')
    .replace(/\.(sh|js|bash)$/i, '')
    .replace(/[-_]/g, ' ');

const loadProjects = async () => {
  const res: any = await projectApi.getList({ page: 1, page_size: 100 });
  projects.value = res?.data?.items || [];
  if (!projectId.value && projects.value.length) {
    projectId.value = projects.value[0].id;
  }
};

const ensureManifest = async (skillId: number) => {
  if (!projectId.value) return;
  const cur = manifestCache[skillId];
  if (cur?.loaded || cur?.loading) return;
  manifestCache[skillId] = { templates: [], loading: true, loaded: false };
  try {
    const res: any = await skillsApi.manifest(projectId.value, skillId);
    manifestCache[skillId] = {
      templates: res?.data?.templates || [],
      loading: false,
      loaded: true,
    };
  } catch {
    manifestCache[skillId] = { templates: [], loading: false, loaded: true };
  }
};

const prefetchManifestsForRows = async () => {
  const chunk = 8;
  for (let i = 0; i < rows.value.length; i += chunk) {
    const slice = rows.value.slice(i, i + chunk);
    await Promise.all(slice.map((s: any) => ensureManifest(s.id)));
  }
};

const loadSkills = async () => {
  if (!projectId.value) return;
  loading.value = true;
  try {
    const res: any = await skillsApi.list(projectId.value, query);
    rows.value = res?.data?.items || [];
    total.value = res?.data?.total || 0;
    for (const k of Object.keys(manifestCache)) delete manifestCache[Number(k)];
  } finally {
    loading.value = false;
  }
  void prefetchManifestsForRows();
};

const onProjectChange = () => {
  query.page = 1;
  loadSkills();
};

const resetQuery = () => {
  query.search = '';
  query.scenario_category = '';
  query.page = 1;
  loadSkills();
};

const openGitDialog = () => {
  gitForm.repo_url = '';
  gitForm.name = '';
  gitForm.scenario_category = '';
  gitForm.entry_command = '';
  gitDialogVisible.value = true;
};

const submitGitImport = async () => {
  if (!projectId.value) return;
  if (!gitForm.repo_url.trim()) {
    ElMessage.warning('请填写仓库地址');
    return;
  }
  gitSubmitting.value = true;
  try {
    const res: any = await skillsApi.importGit(projectId.value, gitForm);
    const count = res?.data?.count ?? 0;
    ElMessage.success(`导入成功（创建 ${count} 个 skill）`);
    gitDialogVisible.value = false;
    await loadSkills();
  } finally {
    gitSubmitting.value = false;
  }
};

const onUploadZip = async (file: UploadRawFile) => {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目');
    return false;
  }
  try {
    await skillsApi.importUpload(projectId.value, file as unknown as File);
    ElMessage.success('上传导入成功');
    await loadSkills();
  } catch (e: any) {
    ElMessage.error(e?.message || '上传导入失败');
  }
  return false;
};

const openEditDialog = (row?: any) => {
  if (row) {
    editForm.id = row.id;
    editForm.name = row.name || '';
    editForm.description = row.description || '';
    editForm.scenario_category = row.scenario_category || '';
    editForm.source_type = row.source_type || 'builtin';
    editForm.repo_url = row.repo_url || '';
    editForm.skill_path = row.skill_path || '';
    editForm.entry_command = row.entry_command || '';
  } else {
    editForm.id = undefined;
    editForm.name = '';
    editForm.description = '';
    editForm.scenario_category = '';
    editForm.source_type = 'builtin';
    editForm.repo_url = '';
    editForm.skill_path = '';
    editForm.entry_command = '';
  }
  editDialogVisible.value = true;
};

const submitEdit = async () => {
  if (!projectId.value) return;
  if (!editForm.name.trim()) {
    ElMessage.warning('请填写技能名称');
    return;
  }
  editSubmitting.value = true;
  try {
    const payload = {
      name: editForm.name.trim(),
      description: editForm.description,
      scenario_category: editForm.scenario_category,
      source_type: editForm.source_type,
      repo_url: editForm.repo_url,
      skill_path: editForm.skill_path,
      entry_command: editForm.entry_command,
    };
    if (editForm.id) {
      await skillsApi.update(projectId.value, editForm.id, payload);
      ElMessage.success('更新成功');
    } else {
      await skillsApi.create(projectId.value, payload);
      ElMessage.success('创建成功');
    }
    editDialogVisible.value = false;
    await loadSkills();
  } finally {
    editSubmitting.value = false;
  }
};

const onToggleActive = async (row: any) => {
  if (!projectId.value) return;
  try {
    await skillsApi.update(projectId.value, row.id, { is_active: row.is_active });
    ElMessage.success('状态已更新');
  } catch (e: any) {
    row.is_active = !row.is_active;
    ElMessage.error(e?.message || '更新失败');
  }
};

const onDelete = async (row: any) => {
  if (!projectId.value) return;
  await ElMessageBox.confirm(`确认删除技能 "${row.name}" 吗？`, '提示', { type: 'warning' });
  await skillsApi.remove(projectId.value, row.id);
  ElMessage.success('删除成功');
  await loadSkills();
};

const onRun = (row: any) => {
  runTarget.value = row;
  runForm.asyncMode = true;
  runForm.session_id = '';
  runForm.templateName = '';
  runForm.templateArgsText = '[]';
  runForm.argumentsText = '{}';
  runAdvancedOpen.value = ['adv'];
  runManifest.allowed_tools = row.allowed_tools || '';
  runManifest.templates = [];
  if (projectId.value) {
    skillsApi.manifest(projectId.value, row.id).then((res: any) => {
      runManifest.allowed_tools = res?.data?.allowed_tools || runManifest.allowed_tools;
      runManifest.templates = res?.data?.templates || [];
    }).catch(() => {});
  }
  runDialogVisible.value = true;
};

const quickRunTemplate = async (row: any, templateName: string) => {
  runTarget.value = row;
  runForm.session_id = '';
  runForm.templateName = templateName;
  runForm.templateArgsText = defaultTemplateArgs(templateName);
  runForm.argumentsText = '{}';
  runAdvancedOpen.value = [];
  runManifest.allowed_tools = row.allowed_tools || '';
  runManifest.templates = [];
  if (projectId.value) {
    try {
      const res: any = await skillsApi.manifest(projectId.value, row.id);
      runManifest.allowed_tools = res?.data?.allowed_tools || runManifest.allowed_tools;
      runManifest.templates = res?.data?.templates || [];
    } catch {
      /* ignore */
    }
  }
  runDialogVisible.value = true;
};

const quickRunCommand = (row: any, command: string, title?: string) => {
  runTarget.value = row;
  runForm.session_id = '';
  runForm.templateName = '';
  runForm.templateArgsText = '[]';
  runForm.argumentsText = JSON.stringify({ command }, null, 2);
  runAdvancedOpen.value = ['adv'];
  runManifest.allowed_tools = row.allowed_tools || '';
  runManifest.templates = [];
  if (projectId.value) {
    skillsApi
      .manifest(projectId.value, row.id)
      .then((res: any) => {
        runManifest.allowed_tools = res?.data?.allowed_tools || runManifest.allowed_tools;
        runManifest.templates = res?.data?.templates || [];
      })
      .catch(() => {});
  }
  ElMessage.info(title ? `已填入命令：${title}` : '已填入命令');
  runDialogVisible.value = true;
};

const defaultTemplateArgs = (templateName: string) => {
  const n = String(templateName || '').toLowerCase();
  if (n.includes('form-automation')) return '["https://example.com/form"]';
  if (n.includes('authenticated-session')) return '["https://example.com/login"]';
  if (n.includes('capture-workflow')) return '["https://example.com","./output"]';
  return '[]';
};

const quickActionsForSkill = (row: any) => {
  const name = String(row?.name || '').toLowerCase();
  const allowed = String(row?.allowed_tools || '').toLowerCase();
  const res: Array<{ key: string; title: string; command: string }> = [];

  const isAgentBrowser = name.includes('agent-browser') || allowed.includes('agent-browser');
  const isPlaywright = name.includes('playwright') || allowed.includes('playwright');

  if (isAgentBrowser) {
    res.push(
      { key: 'ab_help', title: 'agent-browser 帮助', command: 'npx agent-browser --help' },
      { key: 'ab_install', title: '安装 Chromium', command: 'npx agent-browser install' },
      { key: 'ab_open_snapshot', title: '打开+快照', command: 'npx agent-browser open https://example.com && npx agent-browser snapshot -i' },
      { key: 'ab_screenshot', title: '打开+截图', command: 'npx agent-browser open https://example.com && npx agent-browser screenshot --full' },
    );
  }

  // Playwright skill style (node run.js "inline-code")
  if (isPlaywright) {
    res.push({
      key: 'pw_example',
      title: 'Playwright 示例截图',
      command:
        'node run.js "const dir = process.env.SCREENSHOT_DIR || \\"./media/screenshots\\"; const { chromium } = require(\\"playwright\\"); const browser = await chromium.launch({ headless: true }); const page = await browser.newPage(); await page.goto(\\"https://example.com\\"); await page.screenshot({ path: dir + \\"/example.png\\", fullPage: true }); console.log(\\"saved\\", dir + \\"/example.png\\"); await browser.close();"'
    });
  }

  return res;
};

const hasQuickActions = (row: any) =>
  quickActionsForSkill(row).length > 0 || (manifestCache[row.id]?.templates || []).length > 0;

const onQuickCommand = (row: any, cmd: string) => {
  if (!cmd) return;
  if (cmd.startsWith('qa:')) {
    const key = cmd.slice(3);
    const qa = quickActionsForSkill(row).find((x) => x.key === key);
    if (qa) quickRunCommand(row, qa.command, qa.title);
    return;
  }
  if (cmd.startsWith('tpl:')) {
    quickRunTemplate(row, cmd.slice(4));
  }
};

const submitRun = async () => {
  if (!projectId.value || !runTarget.value) return;
  let base: Record<string, any> = {};
  let override: Record<string, any> = {};
  if (runForm.templateName) {
    try {
      const raw = (runForm.templateArgsText || '').trim();
      const parsed = raw ? JSON.parse(raw) : [];
      if (!Array.isArray(parsed)) {
        ElMessage.error('模板参数必须是 JSON 数组');
        return;
      }
      base = { template: runForm.templateName, template_args: parsed };
    } catch {
      ElMessage.error('模板参数必须是合法 JSON 数组');
      return;
    }
  }
  try {
    const raw = (runForm.argumentsText || '').trim();
    override = raw ? JSON.parse(raw) : {};
  } catch {
    ElMessage.error('高级编排 JSON 格式不正确');
    return;
  }
  const argsObj = { ...base, ...override };
  runSubmitting.value = true;
  try {
    // Async job mode (production-like)
    if (runForm.asyncMode) {
      const res: any = await skillsApi.executeActionAsync(projectId.value, runTarget.value.id, {
        action_name: runForm.templateName ? `template:${runForm.templateName}` : 'command',
        arguments: argsObj,
        session_id: runForm.session_id || undefined,
        runner_type: runForm.runnerType,
      });
      const jobId = Number(res?.data?.job_id);
      runResult.job_id = jobId || null;
      runResult.ok = true;
      runResult.skill_name = runTarget.value?.name || '';
      runResult.skill_id = runTarget.value?.id ?? null;
      runResult.session_id = runForm.session_id || '';
      runResult.return_code = null;
      runResult.stdout = '';
      runResult.stderr = '';
      runResult.screenshots = [];
      runResult.artifacts = [];
      runDialogVisible.value = false;
      resultDrawerVisible.value = true;
      ElMessage.success(`已入队 job #${jobId}`);

      const streamUrl = `${apiBaseUrl}${skillsApi.jobStreamUrl(projectId.value, jobId)}`;
      void fetchSse(streamUrl, (evt) => {
        if (evt.event === 'log') {
          runResult.stdout = `${runResult.stdout || ''}${evt.data?.message || ''}\n`;
        } else if (evt.event === 'done') {
          const status = evt.data?.status;
          runResult.ok = status === 'succeeded';
          runResult.return_code = evt.data?.return_code ?? null;
        }
      }).catch(() => {
        ElMessage.warning('实时日志连接超时，任务继续在后台执行，可稍后自动刷新状态');
      });
      void pollJobUntilDone(jobId);
      return;
    }

    // Sync mode (dev)
    const res: any = await skillsApi.execute(projectId.value, runTarget.value.id, {
      arguments: argsObj,
      session_id: runForm.session_id || undefined,
    });
    const data = res?.data || {};
    runResult.job_id = null;
    runResult.ok = !!data.ok;
    runResult.skill_name = data.skill_name || runTarget.value?.name || '';
    runResult.skill_id = data.skill_id ?? runTarget.value?.id ?? null;
    runResult.session_id = data.session_id || '';
    runResult.return_code = data.return_code ?? null;
    runResult.stdout = data.stdout || '';
    runResult.stderr = data.stderr || '';
    runResult.screenshots = Array.isArray(data.screenshots) ? data.screenshots : [];
    runResult.artifacts = Array.isArray(data.artifacts) ? data.artifacts : [];
    const ok = !!runResult.ok;
    const out = String(runResult.stdout || '').slice(0, 120);
    ElMessage[ok ? 'success' : 'error'](ok ? `执行成功${out ? `: ${out}` : ''}` : '执行失败');
    runDialogVisible.value = false;
    resultDrawerVisible.value = true;
  } finally {
    runSubmitting.value = false;
  }
};

const onViewContent = async (row: any) => {
  if (!projectId.value) return;
  const res: any = await skillsApi.content(projectId.value, row.id);
  skillContent.value = res?.data?.content || '';
  contentDialogVisible.value = true;
};

onMounted(async () => {
  await loadProjects();
  await loadSkills();
});
</script>

<style scoped>
.skill-page {
  padding: 16px 20px 24px;
}
.skill-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}
.toolbar-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}
.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.toolbar-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.skill-filters {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.skill-grid-wrap {
  min-height: 220px;
}
.skill-empty {
  padding: 48px 16px;
  text-align: center;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  background: var(--el-fill-color-blank);
  border: 1px dashed var(--el-border-color);
  border-radius: 10px;
}
.skill-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 14px;
}
.skill-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  background: var(--el-bg-color);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.skill-card:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}
.skill-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.skill-card__identity {
  min-width: 0;
  flex: 1;
}
.skill-card__name {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.3;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.skill-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.skill-card__desc {
  margin: 0;
  min-height: 40px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--el-text-color-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.skill-card__meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--el-fill-color-light);
}
.meta-row {
  display: flex;
  gap: 8px;
  min-width: 0;
  font-size: 12px;
  line-height: 1.4;
}
.meta-label {
  flex: 0 0 32px;
  color: var(--el-text-color-secondary);
}
.meta-value {
  min-width: 0;
  color: var(--el-text-color-regular);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.skill-card__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-extra-light);
}
.foot-main {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
  flex-wrap: nowrap;
}
.foot-main :deep(.el-button + .el-button) {
  margin-left: 0;
}
.foot-delete {
  flex-shrink: 0;
}
.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
.run-advanced {
  width: 100%;
}
.run-advanced :deep(.el-collapse-item__header) {
  font-size: 13px;
}
.result-block {
  margin-top: 16px;
}
.result-title {
  margin-bottom: 8px;
  font-weight: 600;
}
.result-files {
  margin-top: 16px;
}
.result-content {
  padding: 12px 18px 20px;
}
:deep(.result-drawer .el-drawer__header) {
  margin-bottom: 0;
  padding: 16px 20px 12px;
}
:deep(.result-drawer .el-drawer__body) {
  padding: 0 8px 16px;
}
@media (max-width: 768px) {
  .skill-grid {
    grid-template-columns: 1fr;
  }
}
</style>

