<template>
	<div class="mock-panel">
		<!-- Mock 地址 -->
		<div class="mock-section">
			<div class="mock-section-title">Mock 地址</div>
			<div class="mock-addr-bar">
				<code class="mock-url">{{ mockUrl }}</code>
				<el-button size="small" plain @click="copyUrl">复制</el-button>
			</div>
			<div class="mock-hint">
				<p>如何使用：</p>
				<ol>
					<li>复制上方地址，用 Postman / 前端请求 / curl 访问后端 Mock 服务即可拿到配置的响应。</li>
					<li>接口 URL 中的环境变量（如 <code v-text="baseUrlPlaceholder"></code>）会自动剥离；地址默认指向后端（非前端 5173）。</li>
					<li>请求按「Mock 期望」从上到下匹配；都未命中时，若开启了自定义脚本则走脚本，否则返回默认提示。</li>
					<li>路径冲突时可依赖地址中的 <code>_api_id</code> 精确定位接口。</li>
				</ol>
			</div>
		</div>

		<!-- Mock 期望 -->
		<div class="mock-section">
			<div class="mock-section-header">
				<span class="mock-section-title">Mock 期望</span>
				<el-button size="small" type="primary" plain @click="openAdd">+ 新建期望</el-button>
			</div>
			<el-table :data="expects" size="small" empty-text="暂无期望" style="width:100%">
				<el-table-column prop="name" label="名称" min-width="120" show-overflow-tooltip />
				<el-table-column label="条件" min-width="200" show-overflow-tooltip>
					<template #default="{ row }">{{ formatCondition(row) }}</template>
				</el-table-column>
				<el-table-column label="状态码" width="80" align="center">
					<template #default="{ row }">{{ row.status ?? 200 }}</template>
				</el-table-column>
				<el-table-column label="操作" width="120" fixed="right">
					<template #default="{ row, $index }">
						<el-button type="primary" link size="small" @click="openEdit(row, $index)">编辑</el-button>
						<el-button type="danger" link size="small" @click="removeExpect($index)">删除</el-button>
					</template>
				</el-table-column>
			</el-table>
		</div>

		<!-- Mock 脚本（对齐报表/调试详情中的自定义脚本） -->
		<div class="mock-section">
			<div class="mock-section-header">
				<span class="mock-section-title">Mock 脚本</span>
				<div class="script-switch-wrap">
					<span class="script-switch-label">开启自定义脚本</span>
					<el-switch v-model="scriptEnabled" size="small" @change="persist" />
				</div>
			</div>
			<div v-if="scriptEnabled" class="script-editor">
				<div class="code-editor-lang">JavaScript</div>
				<textarea
					v-model="script"
					class="mock-textarea script-textarea"
					placeholder="// 在此编写 Mock 脚本&#10;// 例：mock.mockResponse({ code: 200, data: {} })"
					spellcheck="false"
					@change="persist"
				/>
			</div>
			<div v-else class="mock-hint muted">开启后可用脚本动态改写 Mock 响应（优先于未命中期望时的默认行为）。</div>
		</div>

		<!-- 新建/编辑期望 -->
		<el-dialog
			v-model="dialogVisible"
			:title="editIndex >= 0 ? '编辑 Mock 期望' : '新建 Mock 期望'"
			width="680px"
			destroy-on-close
			class="mock-expect-dialog"
			append-to-body
		>
			<el-form :model="form" label-width="96px" label-position="right">
				<el-form-item label="名称" required>
					<el-input v-model="form.name" placeholder="期望名称，如：正常天气 / 城市不存在" />
				</el-form-item>

				<!-- IP 条件 -->
				<el-form-item label="IP 条件">
					<div class="field-block">
						<div class="field-row">
							<el-switch v-model="form.ipEnabled" />
							<span class="field-tip">开启后仅对指定的 IP 地址生效</span>
						</div>
						<el-input
							v-if="form.ipEnabled"
							v-model="form.ips"
							placeholder="多个 IP 用英文逗号分隔，如 127.0.0.1,192.168.1.10"
							style="margin-top:8px"
						/>
					</div>
				</el-form-item>

				<!-- 参数条件 -->
				<el-form-item label="参数条件">
					<div class="field-block">
						<div class="field-tip" style="margin-bottom:8px">支持 query / path / header / cookie / body；多条件为「且」关系，全部满足才匹配。</div>
						<div v-for="(c, idx) in form.paramConditions" :key="idx" class="param-row">
							<el-select v-model="c.location" placeholder="位置" style="width:100px">
								<el-option v-for="opt in locationOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
							</el-select>
							<el-input
								v-model="c.name"
								:placeholder="c.location === 'body' ? '字段名或 JSONPath，如 $.city' : '参数名'"
								style="flex:1"
							/>
							<el-select v-model="c.operator" style="width:110px">
								<el-option v-for="op in operatorOptions" :key="op.value" :label="op.label" :value="op.value" />
							</el-select>
							<el-input
								v-if="!['exists', 'not_exists'].includes(c.operator)"
								v-model="c.value"
								placeholder="期望值"
								style="flex:1"
							/>
							<el-button type="danger" link @click="form.paramConditions.splice(idx, 1)">删除</el-button>
						</div>
						<el-button size="small" plain @click="addParamCondition">+ 添加参数条件</el-button>
					</div>
				</el-form-item>

				<!-- 响应状态 / 延迟 -->
				<el-form-item label="状态码">
					<el-input-number v-model="form.status" :min="100" :max="599" />
				</el-form-item>
				<el-form-item label="响应延迟">
					<div class="field-row">
						<el-input-number v-model="form.delay" :min="0" :max="60000" :step="100" />
						<span class="field-tip">毫秒，0 表示不延迟</span>
					</div>
				</el-form-item>

				<!-- 响应 Headers -->
				<el-form-item label="响应 Headers">
					<div class="field-block">
						<div v-for="(h, idx) in form.headers" :key="idx" class="param-row">
							<el-input v-model="h.key" placeholder="Header 名，如 Content-Type" style="flex:1" />
							<el-input v-model="h.value" placeholder="Header 值" style="flex:1" />
							<el-button type="danger" link @click="form.headers.splice(idx, 1)">删除</el-button>
						</div>
						<el-button size="small" plain @click="form.headers.push({ key: '', value: '' })">+ 添加 Header</el-button>
					</div>
				</el-form-item>

				<!-- 响应体 -->
				<el-form-item label="响应体">
					<textarea v-model="form.body" class="mock-textarea" placeholder='{"code":200,"data":{}}' spellcheck="false" />
				</el-form-item>
			</el-form>
			<template #footer>
				<el-button @click="dialogVisible = false">取消</el-button>
				<el-button type="primary" @click="confirm">确定</el-button>
			</template>
		</el-dialog>
	</div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { save_api } from '/@/api/v1/testing/apiAutomation';
import { getBaseApiUrl } from '/@/utils/config';

const props = defineProps<{ serviceId: number; apiData: any }>();

/** 展示用占位符文案，避免模板里写 {{ }} 触发编译错误 */
const baseUrlPlaceholder = '{{base_url}}';

const locationOptions = [
	{ label: 'query', value: 'query' },
	{ label: 'path', value: 'path' },
	{ label: 'header', value: 'header' },
	{ label: 'cookie', value: 'cookie' },
	{ label: 'body', value: 'body' },
];

const operatorOptions = [
	{ label: '等于', value: 'eq' },
	{ label: '不等于', value: 'neq' },
	{ label: '包含', value: 'contains' },
	{ label: '不包含', value: 'not_contains' },
	{ label: '正则', value: 'regex' },
	{ label: '存在', value: 'exists' },
	{ label: '不存在', value: 'not_exists' },
];

type ParamCondition = { location: string; name: string; operator: string; value: string };
type HeaderItem = { key: string; value: string };
type MockExpect = {
	name: string;
	ipEnabled: boolean;
	ips: string;
	paramConditions: ParamCondition[];
	status: number;
	delay: number;
	headers: HeaderItem[];
	body: string;
	/** 列表展示用的旧字段兼容 */
	condition?: string;
};

const info = computed(() => props.apiData?.api_info || props.apiData || {});
const apiId = computed(() => Number(info.value.id || info.value.api_id || 0));

/** 去掉 {{var}} / ${var}，并规范为以 / 开头的路径 */
const normalizePath = (raw: string) => {
	let u = String(raw || '').trim();
	u = u.replace(/\{\{[^{}]+\}\}/g, '').replace(/\$\{[^}]+\}/g, '');
	// 若整段仍是绝对 URL，只取 pathname
	try {
		if (/^https?:\/\//i.test(u)) {
			const parsed = new URL(u);
			u = parsed.pathname + (parsed.search || '');
		}
	} catch {
		/* ignore */
	}
	u = u.replace(/([^:]\/)\/+/g, '$1');
	if (!u.startsWith('/')) u = `/${u}`;
	if (u === '/') u = '/api/path';
	return u;
};

/** 后端 Mock 根：http://127.0.0.1:8100/mock/... */
const mockServerOrigin = computed(() => String(getBaseApiUrl() || window.location.origin).replace(/\/$/, ''));
const mockPath = computed(() => normalizePath(info.value.url || info.value.req?.url || ''));
const mockUrl = computed(() => {
	const base = `${mockServerOrigin.value}/mock${mockPath.value}`;
	return apiId.value ? `${base}?_api_id=${apiId.value}` : base;
});

const emptyExpect = (): MockExpect => ({
	name: '',
	ipEnabled: false,
	ips: '',
	paramConditions: [],
	status: 200,
	delay: 0,
	headers: [],
	body: '{"code":200,"data":{}}',
});

const expects = ref<MockExpect[]>([]);
const scriptEnabled = ref(false);
const script = ref('');
const dialogVisible = ref(false);
const editIndex = ref(-1);
const form = ref<MockExpect>(emptyExpect());

const loadFromApi = () => {
	const mock = info.value.mock || info.value.req?.mock || {};
	expects.value = Array.isArray(mock.expects)
		? mock.expects.map((e: any) => ({
				...emptyExpect(),
				...e,
				paramConditions: Array.isArray(e.paramConditions) ? e.paramConditions : [],
				headers: Array.isArray(e.headers) ? e.headers : [],
				ipEnabled: !!e.ipEnabled,
				ips: e.ips || '',
				status: e.status ?? 200,
				delay: e.delay ?? 0,
				body: typeof e.body === 'string' ? e.body : JSON.stringify(e.body ?? { code: 200, data: {} }, null, 2),
			}))
		: [];
	scriptEnabled.value = !!mock.scriptEnabled;
	script.value = mock.script || '';
};

watch(() => props.apiData, loadFromApi, { immediate: true, deep: true });

const buildMockPayload = () => ({
	expects: expects.value,
	scriptEnabled: scriptEnabled.value,
	script: script.value,
});

const persist = async () => {
	if (!apiId.value) return;
	try {
		const req = { ...(info.value.req || {}), mock: buildMockPayload() };
		await save_api({ id: apiId.value, url: info.value.url || mockPath.value, req });
	} catch {
		/* 静默：本地状态仍保留 */
	}
};

const formatCondition = (row: MockExpect) => {
	const parts: string[] = [];
	if (row.ipEnabled && row.ips?.trim()) parts.push(`IP∈[${row.ips.trim()}]`);
	for (const c of row.paramConditions || []) {
		if (!c.name && c.operator !== 'exists' && c.operator !== 'not_exists') continue;
		const opLabel = operatorOptions.find((o) => o.value === c.operator)?.label || c.operator;
		if (c.operator === 'exists' || c.operator === 'not_exists') {
			parts.push(`${c.location}.${c.name} ${opLabel}`);
		} else {
			parts.push(`${c.location}.${c.name} ${opLabel} ${c.value ?? ''}`);
		}
	}
	return parts.length ? parts.join(' 且 ') : '无条件（始终匹配）';
};

const copyUrl = () => {
	navigator.clipboard?.writeText(mockUrl.value).then(() => ElMessage.success('已复制 Mock 地址'));
};

const openAdd = () => {
	editIndex.value = -1;
	form.value = emptyExpect();
	dialogVisible.value = true;
};

const openEdit = (row: MockExpect, index: number) => {
	editIndex.value = index;
	form.value = {
		...emptyExpect(),
		...row,
		paramConditions: (row.paramConditions || []).map((c) => ({ ...c })),
		headers: (row.headers || []).map((h) => ({ ...h })),
	};
	dialogVisible.value = true;
};

const removeExpect = async (index: number) => {
	expects.value.splice(index, 1);
	await persist();
};

const addParamCondition = () => {
	form.value.paramConditions.push({ location: 'query', name: '', operator: 'eq', value: '' });
};

const confirm = async () => {
	if (!form.value.name?.trim()) {
		ElMessage.warning('请填写期望名称');
		return;
	}
	if (form.value.ipEnabled && !form.value.ips?.trim()) {
		ElMessage.warning('已开启 IP 条件，请填写至少一个 IP 地址');
		return;
	}
	const payload: MockExpect = {
		...form.value,
		name: form.value.name.trim(),
		paramConditions: (form.value.paramConditions || []).filter((c) => c.name?.trim() || ['exists', 'not_exists'].includes(c.operator)),
		headers: (form.value.headers || []).filter((h) => h.key?.trim()),
		condition: undefined,
	};
	payload.condition = formatCondition(payload);
	if (editIndex.value >= 0) expects.value[editIndex.value] = payload;
	else expects.value.push(payload);
	dialogVisible.value = false;
	await persist();
	ElMessage.success(editIndex.value >= 0 ? '期望已更新' : '期望已添加');
};
</script>

<style scoped>
.mock-panel {
	height: 100%;
	overflow-y: auto;
	padding: 16px;
	box-sizing: border-box;
}
.mock-section { margin-bottom: 24px; }
.mock-section-title {
	font-size: 14px;
	font-weight: 600;
	color: var(--el-text-color-primary);
	margin-bottom: 10px;
}
.mock-section-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 10px;
	gap: 12px;
}
.mock-addr-bar {
	display: flex;
	align-items: center;
	gap: 10px;
	background: var(--el-fill-color-light);
	border-radius: 6px;
	padding: 8px 12px;
}
.mock-url {
	font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
	font-size: 12px;
	color: #409eff;
	flex: 1;
	word-break: break-all;
}
.mock-hint {
	margin-top: 10px;
	padding: 10px 12px;
	background: var(--el-fill-color-lighter);
	border-radius: 6px;
	font-size: 12px;
	color: var(--el-text-color-regular);
	line-height: 1.7;
}
.mock-hint p { margin: 0 0 4px; font-weight: 600; color: var(--el-text-color-primary); }
.mock-hint ol { margin: 0; padding-left: 18px; }
.mock-hint code {
	font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
	background: var(--el-fill-color);
	padding: 0 4px;
	border-radius: 3px;
}
.mock-hint.muted { color: var(--el-text-color-placeholder); }

.script-switch-wrap { display: flex; align-items: center; gap: 8px; }
.script-switch-label { font-size: 12px; color: var(--el-text-color-regular); }
.script-editor {
	border: 1px solid var(--el-border-color);
	border-radius: 6px;
	overflow: hidden;
	background: #1e1e1e;
}
.code-editor-lang {
	font-size: 11px;
	color: #9cdcfe;
	padding: 6px 10px 0;
	opacity: 0.75;
}
.script-textarea {
	min-height: 140px;
	background: #1e1e1e !important;
	color: #d4d4d4 !important;
	border: none !important;
	border-radius: 0 !important;
}
.mock-textarea {
	width: 100%;
	min-height: 100px;
	background: var(--el-bg-color);
	border: 1px solid var(--el-border-color);
	border-radius: 4px;
	padding: 8px;
	font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
	font-size: 12px;
	color: var(--el-text-color-primary);
	resize: vertical;
	outline: none;
	box-sizing: border-box;
	line-height: 1.5;
}

.field-block { width: 100%; }
.field-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.field-tip { font-size: 12px; color: var(--el-text-color-placeholder); line-height: 1.5; }
.param-row {
	display: flex;
	align-items: center;
	gap: 8px;
	margin-bottom: 8px;
	width: 100%;
	flex-wrap: wrap;
}
</style>
