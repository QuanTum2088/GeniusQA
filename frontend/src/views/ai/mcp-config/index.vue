<template>
	<div class="page-wrap">
		<el-card shadow="hover" class="toolbar">
			<el-form :inline="true">
				<el-form-item label="项目">
					<el-select v-model="projectId" placeholder="选择项目" style="width: 220px" @change="onProjectChange">
						<el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
					</el-select>
				</el-form-item>
				<el-form-item label="作用域">
					<el-select v-model="searchForm.scope" clearable placeholder="全部" style="width: 140px" @change="load">
						<el-option label="项目私有" value="local" />
						<el-option label="项目共享" value="project" />
						<el-option label="全局" value="user" />
					</el-select>
				</el-form-item>
				<el-form-item label="搜索">
					<el-input v-model="searchForm.search" clearable placeholder="配置名称" style="width: 180px" @keyup.enter="load" />
				</el-form-item>
				<el-form-item>
					<div class="toolbar-actions">
						<el-button type="primary" @click="load">刷新</el-button>
						<el-button type="success" @click="openCreate">新建</el-button>
						<el-button @click="doImport">导入文件</el-button>
						<el-button @click="doSync">同步平台文件</el-button>
						<el-dropdown trigger="click" @command="doExport">
							<el-button>
								导出到客户端
								<el-icon class="el-icon--right"><ele-ArrowDown /></el-icon>
							</el-button>
							<template #dropdown>
								<el-dropdown-menu>
									<el-dropdown-item command="claude">导出 Claude Code</el-dropdown-item>
									<el-dropdown-item command="cursor">导出 Cursor</el-dropdown-item>
									<el-dropdown-item command="n-tester" divided>重写 GeniusQA 文件</el-dropdown-item>
								</el-dropdown-menu>
							</template>
						</el-dropdown>
					</div>
				</el-form-item>
			</el-form>
			<div v-if="currentWorkspace" class="ws-hint">
				本机工作目录：{{ currentWorkspace }}
				<span class="ws-tip">本地 / 项目作用域依赖此路径，默认写入 .n-tester/mcp.json）</span>
			</div>
			<div v-else class="ws-hint warn">
				未配置本机工作目录。请到「项目管理」编辑项目并填写。
			</div>
		</el-card>

		<el-card shadow="hover" class="table-card">
			<el-table v-loading="loading" :data="rows" stripe>
				<el-table-column prop="name" label="名称" min-width="120" />
				<el-table-column label="作用域" width="110">
					<template #default="{ row }">
						<el-tag size="small" :type="scopeTagType(row.scope)">{{ scopeLabel(row.scope) }}</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="transport" label="协议" width="130" />
				<el-table-column label="地址" min-width="220" show-overflow-tooltip>
					<template #default="{ row }">
						<span v-if="row.transport === 'stdio'">{{ row.command }} {{ (row.args || []).join(' ') }}</span>
						<span v-else>{{ row.url }}</span>
					</template>
				</el-table-column>
				<el-table-column label="连接状态" width="110">
					<template #default="{ row }">
						<el-tag size="small" :type="row.is_connected ? 'success' : 'info'">
							{{ row.is_connected ? '已连接' : '未连接' }}
						</el-tag>
					</template>
				</el-table-column>
				<el-table-column label="鉴权" width="100">
					<template #default="{ row }">{{ row.auth_type || 'none' }}</template>
				</el-table-column>
				<el-table-column label="启用" width="90">
					<template #default="{ row }">
						<el-switch v-model="row.is_enabled" @change="() => patchRow(row)" />
					</template>
				</el-table-column>
				<el-table-column label="操作" width="300" fixed="right">
					<template #default="{ row }">
						<el-button size="small" type="primary" @click="testRow(row)">测试</el-button>
						<el-button size="small" type="success" @click="openTools(row)">工具</el-button>
						<el-button size="small" type="warning" @click="editRow(row)">编辑</el-button>
						<el-button size="small" type="danger" @click="removeRow(row)">删除</el-button>
					</template>
				</el-table-column>
			</el-table>
			<div class="pager" v-if="total > 0">
				<el-pagination
					v-model:current-page="searchForm.page"
					v-model:page-size="searchForm.page_size"
					:total="total"
					layout="total, prev, pager, next"
					@current-change="load"
				/>
			</div>
		</el-card>

		<el-dialog v-model="dlg" :title="editId ? '编辑 MCP' : '新建 MCP'" width="720px" destroy-on-close @closed="resetForm">
			<el-form :model="form" label-width="110px">
				<el-form-item label="名称" required>
					<el-input v-model="form.name" placeholder="mcpServers 中的 key" />
				</el-form-item>
				<el-form-item label="作用域" required>
					<el-radio-group v-model="form.scope">
						<el-radio-button label="local">项目私有</el-radio-button>
						<el-radio-button label="project">项目共享</el-radio-button>
						<el-radio-button label="user">全局</el-radio-button>
					</el-radio-group>
				</el-form-item>

				
				<el-form-item label="写入位置">
					<el-input :model-value="scopeWritePath" readonly />
					<div class="form-tip">{{ scopeHint }}</div>
				</el-form-item>

				<template v-if="form.scope === 'local' || form.scope === 'project'">
					<el-form-item label="本机工作目录" required>
						<el-input :model-value="currentWorkspace || ''" readonly placeholder="未配置" />
						<div v-if="!currentWorkspace" class="form-tip warn-tip">
							请先到「项目管理」编辑当前项目并填写本机工作目录，否则无法保存并同步文件。
						</div>
						<div v-else class="form-tip">来自当前项目配置，保存时用于定位文件。</div>
					</el-form-item>
				</template>

				<el-alert
					v-if="form.scope === 'project'"
					type="info"
					:closable="false"
					show-icon
					style="margin: 0 0 14px 110px; width: calc(100% - 110px)"
					title="项目共享写入 {workspace}/.n-tester/mcp.json，可随 Git 提交。需要 Claude/Cursor 时请用「导出到客户端」。"
				/>
				<el-alert
					v-else-if="form.scope === 'local'"
					type="info"
					:closable="false"
					show-icon
					style="margin: 0 0 14px 110px; width: calc(100% - 110px)"
					title="项目私有仅当前用户可见，写入 ~/.n-tester/mcp.json 的项目工作目录"
				/>
				<el-alert
					v-else
					type="info"
					:closable="false"
					show-icon
					style="margin: 0 0 14px 110px; width: calc(100% - 110px)"
					title="全局配置写入 ~/.n-tester/mcp.json，对你的所有项目可见；运行时以数据库为准。"
				/>

				<el-form-item label="协议" required>
					<el-radio-group v-model="form.transport">
						<el-radio-button label="stdio">stdio</el-radio-button>
						<el-radio-button label="streamable-http">HTTP</el-radio-button>
						<el-radio-button label="sse">SSE</el-radio-button>
					</el-radio-group>
				</el-form-item>

				<template v-if="form.transport === 'stdio'">
					<el-form-item label="命令" required>
						<el-input v-model="form.command" placeholder="如 npx / node / python" />
					</el-form-item>
					<el-form-item label="参数">
						<el-input
							v-model="argsText"
							type="textarea"
							:rows="2"
							placeholder="每行一个参数，如&#10;-y&#10;@modelcontextprotocol/server-filesystem&#10;/path"
						/>
					</el-form-item>
					<el-form-item label="环境变量">
						<div class="kv-list">
							<div v-for="(row, idx) in envRows" :key="'e' + idx" class="kv-row">
								<el-input v-model="row.key" placeholder="KEY" style="width: 160px" />
								<el-input v-model="row.value" placeholder="value" style="flex: 1" />
								<el-button text type="danger" @click="envRows.splice(idx, 1)">删</el-button>
							</div>
							<el-button size="small" @click="envRows.push({ key: '', value: '' })">添加</el-button>
						</div>
					</el-form-item>
				</template>

				<template v-else>
					<el-form-item label="URL" required>
						<el-input v-model="form.url" placeholder="https://..." />
					</el-form-item>
					<el-form-item label="请求头">
						<div class="kv-list">
							<div v-for="(row, idx) in headerRows" :key="'h' + idx" class="kv-row">
								<el-input v-model="row.key" placeholder="Header" style="width: 160px" />
								<el-input v-model="row.value" placeholder="value" style="flex: 1" />
								<el-button text type="danger" @click="headerRows.splice(idx, 1)">删</el-button>
							</div>
							<el-button size="small" @click="headerRows.push({ key: '', value: '' })">添加</el-button>
						</div>
					</el-form-item>
					<el-form-item label="鉴权">
						<el-select v-model="form.auth_type" style="width: 180px">
							<el-option label="无" value="none" />
							<el-option label="Bearer Token" value="bearer" />
							<el-option label="API Key" value="api_key" />
						</el-select>
					</el-form-item>
					<el-form-item v-if="form.auth_type === 'bearer'" label="Token">
						<el-input
							v-model="form.auth_config.token"
							type="password"
							show-password
							:placeholder="form.scope === 'project' ? '可填真实 token，文件中会写成 ${MCP_TOKEN}' : 'Bearer token'"
						/>
					</el-form-item>
					<template v-if="form.auth_type === 'api_key'">
						<el-form-item label="Header 名">
							<el-input v-model="form.auth_config.header_name" placeholder="X-API-Key" />
						</el-form-item>
						<el-form-item label="API Key">
							<el-input
								v-model="form.auth_config.api_key"
								type="password"
								show-password
								:placeholder="form.scope === 'project' ? '文件中可写成 ${MCP_API_KEY}' : 'API Key'"
							/>
						</el-form-item>
					</template>
				</template>

				<el-form-item label="备注">
					<el-input v-model="form.description" type="textarea" :rows="2" />
				</el-form-item>
				<el-form-item label="启用">
					<el-switch v-model="form.is_enabled" />
				</el-form-item>
			</el-form>
			<template #footer>
				<el-button @click="dlg = false">取消</el-button>
				<el-button type="primary" :loading="saving" @click="submit">保存</el-button>
			</template>
		</el-dialog>

		<el-dialog v-model="toolsDlg" title="MCP 工具列表" width="780px" destroy-on-close>
			<el-alert v-if="toolsErr" :title="toolsErr" type="error" show-icon :closable="false" style="margin-bottom: 10px" />
			<el-table v-loading="toolsLoading" :data="tools" size="small" max-height="520">
				<el-table-column prop="name" label="名称" min-width="220" />
				<el-table-column prop="description" label="描述" min-width="260" show-overflow-tooltip />
				<el-table-column label="参数" min-width="240">
					<template #default="{ row }">
						<el-text type="info">{{ formatSchema(row.input_schema) }}</el-text>
					</template>
				</el-table-column>
			</el-table>
			<template #footer>
				<el-button @click="toolsDlg = false">关闭</el-button>
			</template>
		</el-dialog>
	</div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useProjectApi } from '/@/api/v1/projects/project';
import { projectPlatformApi } from '/@/api/v1/projects/platform';

type Kv = { key: string; value: string };

const projectApi = useProjectApi();
const projectId = ref<number | null>(null);
const projects = ref<{ id: number; name: string; workspace_path?: string }[]>([]);
const loading = ref(false);
const saving = ref(false);
const rows = ref<any[]>([]);
const total = ref(0);
const dlg = ref(false);
const editId = ref<number | null>(null);
const toolsDlg = ref(false);
const toolsLoading = ref(false);
const toolsErr = ref('');
const tools = ref<any[]>([]);
const headerRows = ref<Kv[]>([]);
const envRows = ref<Kv[]>([]);
const argsText = ref('');

const searchForm = reactive({ search: '', scope: '' as string, page: 1, page_size: 20 });

const form = reactive({
	name: '',
	scope: 'local',
	url: '',
	transport: 'streamable-http',
	command: 'npx',
	args: [] as string[],
	env: {} as Record<string, string>,
	headers: {} as Record<string, string>,
	auth_type: 'none',
	auth_config: { token: '', api_key: '', header_name: 'X-API-Key' } as Record<string, string>,
	description: '',
	is_enabled: true,
});

const currentWorkspace = computed(() => {
	const p = projects.value.find((x) => x.id === projectId.value);
	return (p?.workspace_path || '').trim();
});

const scopeWritePath = computed(() => {
	const ws = currentWorkspace.value || '{workspace}';
	if (form.scope === 'project') return `${ws}/.n-tester/mcp.json`;
	if (form.scope === 'local') return `~/.n-tester/mcp.json → projects[${ws}].mcpServers`;
	return `~/.n-tester/mcp.json → mcpServers（全局）`;
});

const scopeHint = computed(() => {
	if (form.scope === 'project') return '项目共享：写入仓库 .n-tester/mcp.json，团队可见，可进 Git';
	if (form.scope === 'local') return '项目私有：仅本人可见，写入本机 ~/.n-tester 下该项目节点';
	return '全局：本人所有项目可见，不绑定项目工作目录；聊天调用以数据库为准';
});

function scopeLabel(s: string) {
	return ({ local: '项目私有', project: '项目共享', user: '全局' } as any)[s] || s || '全局';
}
function scopeTagType(s: string) {
	return ({ local: 'warning', project: 'success', user: 'info' } as any)[s] || 'info';
}

function kvToObj(list: Kv[]) {
	const o: Record<string, string> = {};
	for (const r of list) {
		const k = (r.key || '').trim();
		if (k) o[k] = r.value ?? '';
	}
	return o;
}
function objToKv(obj: Record<string, any> | null | undefined): Kv[] {
	if (!obj || typeof obj !== 'object') return [];
	return Object.entries(obj).map(([key, value]) => ({ key, value: String(value ?? '') }));
}

async function loadProjects() {
	try {
		const res: any = await projectApi.getList({ page: 1, page_size: 50 });
		if (res?.code === 200 && res.data?.items) {
			projects.value = res.data.items;
			const stored = localStorage.getItem('defaultProjectId');
			if (stored && projects.value.some((p) => p.id === Number(stored))) {
				projectId.value = Number(stored);
			} else if (projects.value.length) {
				projectId.value = projects.value[0].id;
				localStorage.setItem('defaultProjectId', String(projectId.value));
			}
		}
	} catch (e: any) {
		ElMessage.error(e?.message || '获取项目列表失败');
	}
}

function onProjectChange() {
	if (projectId.value) localStorage.setItem('defaultProjectId', String(projectId.value));
	load();
}

async function load() {
	if (!projectId.value) return;
	loading.value = true;
	try {
		const res: any = await projectPlatformApi.mcp.list(projectId.value, {
			search: searchForm.search,
			scope: searchForm.scope || undefined,
			page: searchForm.page,
			page_size: searchForm.page_size,
		});
		if (res?.code === 200 && res.data) {
			rows.value = res.data.items || [];
			total.value = res.data.total || 0;
		}
	} finally {
		loading.value = false;
	}
}

function openCreate() {
	editId.value = null;
	resetForm();
	dlg.value = true;
}

function editRow(row: any) {
	editId.value = row.id;
	form.name = row.name;
	form.scope = row.scope || 'user';
	form.url = row.url || '';
	form.transport = row.transport || 'streamable-http';
	form.command = row.command || 'npx';
	form.description = row.description || '';
	form.is_enabled = row.is_enabled;
	form.auth_type = row.auth_type || 'none';
	form.auth_config = {
		token: row.auth_config?.token || '',
		api_key: row.auth_config?.api_key || '',
		header_name: row.auth_config?.header_name || 'X-API-Key',
	};
	argsText.value = Array.isArray(row.args) ? row.args.join('\n') : '';
	headerRows.value = objToKv(row.headers);
	envRows.value = objToKv(row.env);
	dlg.value = true;
}

function resetForm() {
	form.name = '';
	form.scope = 'local';
	form.url = '';
	form.transport = 'streamable-http';
	form.command = 'npx';
	form.description = '';
	form.is_enabled = true;
	form.auth_type = 'none';
	form.auth_config = { token: '', api_key: '', header_name: 'X-API-Key' };
	argsText.value = '';
	headerRows.value = [];
	envRows.value = [];
}

function buildPayload() {
	const args = argsText.value
		.split(/\r?\n/)
		.map((s) => s.trim())
		.filter(Boolean);
	return {
		name: form.name,
		scope: form.scope,
		transport: form.transport,
		url: form.transport === 'stdio' ? '' : form.url,
		command: form.transport === 'stdio' ? form.command : '',
		args: form.transport === 'stdio' ? args : [],
		env: form.transport === 'stdio' ? kvToObj(envRows.value) : {},
		headers: form.transport === 'stdio' ? {} : kvToObj(headerRows.value),
		auth_type: form.transport === 'stdio' ? 'none' : form.auth_type,
		auth_config:
			form.transport === 'stdio'
				? {}
				: {
						token: form.auth_config.token,
						api_key: form.auth_config.api_key,
						header_name: form.auth_config.header_name || 'X-API-Key',
				  },
		description: form.description,
		is_enabled: form.is_enabled,
	};
}

async function submit() {
	if (!projectId.value) return;
	if (!form.name.trim()) {
		ElMessage.warning('请填写名称');
		return;
	}
	if (form.transport === 'stdio' && !form.command.trim()) {
		ElMessage.warning('stdio 请填写命令');
		return;
	}
	if (form.transport !== 'stdio' && !form.url.trim()) {
		ElMessage.warning('请填写 URL');
		return;
	}
	if ((form.scope === 'local' || form.scope === 'project') && !currentWorkspace.value) {
		ElMessage.warning('当前作用域需要先配置项目的本机工作目录');
		return;
	}
	saving.value = true;
	try {
		const payload = buildPayload();
		const res: any = editId.value
			? await projectPlatformApi.mcp.update(projectId.value, editId.value, payload)
			: await projectPlatformApi.mcp.create(projectId.value, payload);
		if (res?.code === 200) {
			const warn = res.data?.file_sync?.warning;
			ElMessage.success(warn ? `已保存（文件同步警告: ${warn}）` : editId.value ? '已保存' : '已创建');
			dlg.value = false;
			load();
		}
	} catch (e: any) {
		ElMessage.error(e?.response?.data?.detail || e?.message || '保存失败');
	} finally {
		saving.value = false;
	}
}

async function patchRow(row: any) {
	if (!projectId.value) return;
	await projectPlatformApi.mcp.update(projectId.value, row.id, { is_enabled: row.is_enabled });
}

async function testRow(row: any) {
	if (!projectId.value) return;
	try {
		const res: any = await projectPlatformApi.mcp.test(projectId.value, row.id);
		if (res?.code === 200) {
			const ok = !!res.data?.ok;
			row.is_connected = ok;
			row.connection_status = ok ? 'connected' : 'disconnected';
			if (ok) ElMessage.success(res.message || '连接成功');
			else ElMessage.error(res.message || '连接失败');
		}
	} catch (e: any) {
		row.is_connected = false;
		row.connection_status = 'disconnected';
		ElMessage.error(e?.message || '测试失败');
	}
}

function formatSchema(schema: any): string {
	if (!schema) return '-';
	try {
		const props = schema.properties || schema?.json_schema?.properties;
		if (!props || typeof props !== 'object') return JSON.stringify(schema).slice(0, 120);
		const keys = Object.keys(props);
		return keys.length ? keys.join(', ') : '-';
	} catch {
		return '-';
	}
}

async function openTools(row: any) {
	if (!projectId.value) return;
	toolsDlg.value = true;
	toolsLoading.value = true;
	toolsErr.value = '';
	tools.value = [];
	try {
		const res: any = await projectPlatformApi.mcp.tools(projectId.value, row.id);
		if (res?.code === 200 && res.data?.tools) tools.value = res.data.tools;
		else toolsErr.value = res?.message || '获取失败';
	} catch (e: any) {
		toolsErr.value = e?.message || '获取工具列表失败';
	} finally {
		toolsLoading.value = false;
	}
}

async function removeRow(row: any) {
	if (!projectId.value) return;
	await ElMessageBox.confirm('确定删除该配置？将同步从本地文件移除。', '提示', { type: 'warning' });
	const res: any = await projectPlatformApi.mcp.remove(projectId.value, row.id);
	if (res?.code === 200) {
		ElMessage.success('已删除');
		load();
	}
}

async function doImport() {
	if (!projectId.value) return;
	try {
		const res: any = await projectPlatformApi.mcp.importFromFile(projectId.value, { scope: 'project' });
		if (res?.code === 200) {
			ElMessage.success(res.message || '导入完成');
			load();
		}
	} catch (e: any) {
		ElMessage.error(e?.response?.data?.detail || e?.message || '导入失败');
	}
}

async function doSync() {
	if (!projectId.value) return;
	try {
		const res: any = await projectPlatformApi.mcp.syncFiles(projectId.value);
		if (res?.code === 200) {
			const n = res.data?.synced?.length || 0;
			const skip = res.data?.skipped?.length || 0;
			ElMessage.success(res.message || `已同步 ${n} 项` + (skip ? `，跳过 ${skip}` : ''));
		}
	} catch (e: any) {
		ElMessage.error(e?.response?.data?.detail || e?.message || '同步失败');
	}
}

async function doExport(format: 'claude' | 'cursor' | 'n-tester') {
	if (!projectId.value) return;
	const label = ({ claude: 'Claude Code', cursor: 'Cursor', 'n-tester': 'GeniusQA' } as const)[format];
	try {
		await ElMessageBox.confirm(
			format === 'n-tester'
				? '将把当前可见 MCP 写入 GeniusQA 配置（~/.n-tester/mcp.json 及项目 .n-tester/mcp.json）。'
				: `将按 ${label} 格式写入对应客户端配置文件（按需导出，不影响平台默认文件）。`,
			`导出到 ${label}`,
			{ type: 'info', confirmButtonText: '导出', cancelButtonText: '取消' },
		);
		const res: any = await projectPlatformApi.mcp.export(projectId.value, { format, write: true });
		if (res?.code === 200) {
			const paths = (res.data?.written || []).map((x: any) => x.path).filter(Boolean);
			ElMessage.success(
				paths.length ? `${res.message || '导出完成'}：${paths.join('；')}` : res.message || '导出完成',
			);
		}
	} catch (e: any) {
		if (e === 'cancel' || e === 'close') return;
		ElMessage.error(e?.response?.data?.detail || e?.message || '导出失败');
	}
}

onMounted(async () => {
	await loadProjects();
	await load();
});
</script>

<style scoped>
.page-wrap {
	padding: 12px;
}
.toolbar {
	margin-bottom: 12px;
}
.toolbar-actions {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 8px;
}
.toolbar-actions :deep(.el-button + .el-button) {
	margin-left: 0;
}
.pager {
	margin-top: 12px;
	display: flex;
	justify-content: flex-end;
}
.ws-hint {
	margin-top: 4px;
	font-size: 12px;
	color: var(--el-text-color-secondary);
}
.ws-hint.warn {
	color: var(--el-color-warning);
}
.ws-tip {
	margin-left: 8px;
	opacity: 0.8;
}
.form-tip {
	font-size: 12px;
	color: var(--el-text-color-secondary);
	line-height: 1.4;
	margin-top: 4px;
}
.form-tip.warn-tip {
	color: var(--el-color-warning);
}
.kv-list {
	width: 100%;
}
.kv-row {
	display: flex;
	gap: 8px;
	align-items: center;
	margin-bottom: 6px;
}
</style>
