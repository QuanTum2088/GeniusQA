<template>
	<div class="history-panel">
		<div class="history-toolbar">
			<el-button size="small" @click="reload">刷新</el-button>
		</div>

		<el-table
			v-loading="loading"
			:data="list"
			border
			stripe
			empty-text="暂无调试记录"
			style="width: 100%"
			@row-click="openDetail"
		>
			<el-table-column type="index" label="序号" width="60" align="center" />
			<el-table-column label="状态码" width="90" align="center">
				<template #default="{ row }">
					<el-tag size="small" :type="statusType(row.status_code)" effect="light">
						{{ row.status_code ?? '-' }}
					</el-tag>
				</template>
			</el-table-column>
			<el-table-column label="方法" width="90" align="center">
				<template #default="{ row }">{{ methodLabel(row) }}</template>
			</el-table-column>
			<el-table-column label="请求 URL" min-width="220" show-overflow-tooltip>
				<template #default="{ row }">{{ row.req?.url || '-' }}</template>
			</el-table-column>
			<el-table-column label="耗时" width="100" align="center">
				<template #default="{ row }">
					{{ row.response_time != null ? `${row.response_time} ms` : '-' }}
				</template>
			</el-table-column>
			<el-table-column label="时间" width="170" align="center">
				<template #default="{ row }">{{ formatTime(row.creation_date || row.create_time) }}</template>
			</el-table-column>
			<el-table-column label="操作" width="90" align="center" fixed="right">
				<template #default="{ row }">
					<el-button type="primary" link size="small" @click.stop="openDetail(row)">详情</el-button>
				</template>
			</el-table-column>
		</el-table>

		<div class="history-pagination" v-show="total > 0">
			<el-pagination
				background
				v-model:current-page="currentPage"
				v-model:page-size="pageSize"
				:page-sizes="[10, 20, 50, 100]"
				layout="total, sizes, prev, pager, next, jumper"
				:total="total"
				@size-change="load"
				@current-change="load"
			/>
		</div>

		<el-drawer
			v-model="detailVisible"
			title="调试记录详情"
			size="520px"
			destroy-on-close
			class="history-detail-drawer"
			append-to-body
		>
			<div v-if="detail" class="drawer-body">
				<div class="detail-meta">
					<el-tag :type="statusType(detail.status_code)" effect="dark">{{ detail.status_code }}</el-tag>
					<span>{{ methodLabel(detail) }}</span>
					<span class="detail-time">{{ formatTime(detail.creation_date || detail.create_time) }}</span>
				</div>
				<div class="detail-block">
					<div class="detail-label">请求 URL</div>
					<code class="detail-code">{{ detail.req?.url || '-' }}</code>
				</div>
				<div class="detail-block">
					<div class="detail-label">响应耗时</div>
					<span>{{ detail.response_time ?? '-' }} ms</span>
				</div>
				<div class="detail-block" v-if="detail.error_message">
					<div class="detail-label">错误信息</div>
					<pre class="detail-pre error">{{ detail.error_message }}</pre>
				</div>
				<div class="detail-block">
					<div class="detail-label">请求体</div>
					<pre class="detail-pre">{{ formatJson(detail.req?.body) }}</pre>
				</div>
				<div class="detail-block">
					<div class="detail-label">响应体</div>
					<pre class="detail-pre">{{ formatJson(detail.res?.body ?? detail.res) }}</pre>
				</div>
			</div>
		</el-drawer>
	</div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { req_history } from '/@/api/v1/testing/apiAutomation';

const props = defineProps<{ apiData?: any }>();

const list = ref<any[]>([]);
const total = ref(0);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const detailVisible = ref(false);
const detail = ref<any>(null);

const apiId = computed(() => {
	const info = props.apiData?.api_info || props.apiData || {};
	return Number(info.id || info.api_id || 0) || null;
});

const methodMap: Record<number, string> = { 1: 'GET', 2: 'POST', 3: 'PUT', 4: 'DELETE', 5: 'PATCH', 6: 'OPTIONS' };

const statusType = (code: number) => {
	const c = Number(code);
	if (c >= 200 && c < 300) return 'success';
	if (c >= 400) return 'danger';
	if (c >= 300) return 'warning';
	return 'info';
};

const methodLabel = (r: any) => methodMap[Number(r?.req?.method)] || r?.req?.method || 'REQ';

const formatTime = (t: any) => {
	if (!t) return '';
	return String(t).replace('T', ' ').slice(0, 19);
};

const formatJson = (v: any) => {
	if (v == null || v === '') return '-';
	if (typeof v === 'string') {
		try { return JSON.stringify(JSON.parse(v), null, 2); } catch { return v; }
	}
	try { return JSON.stringify(v, null, 2); } catch { return String(v); }
};

const parseResult = (raw: any) => {
	const data = raw?.data ?? raw ?? {};
	const content = Array.isArray(data?.content)
		? data.content
		: (Array.isArray(data) ? data : []);
	const t = Number(data?.total ?? content.length) || 0;
	return { content, total: t };
};

const load = async () => {
	loading.value = true;
	try {
		const payload: Record<string, any> = {
			page: currentPage.value,
			pageSize: pageSize.value,
		};
		if (apiId.value) payload.api_id = apiId.value;
		const r: any = await req_history(payload);
		const parsed = parseResult(r);
		list.value = parsed.content;
		total.value = parsed.total;
	} catch {
		list.value = [];
		total.value = 0;
	} finally {
		loading.value = false;
	}
};

const reload = () => {
	currentPage.value = 1;
	load();
};

const openDetail = (row: any) => {
	detail.value = row;
	detailVisible.value = true;
};

watch(apiId, () => { reload(); });
onMounted(load);
</script>

<style scoped>
.history-panel {
	height: 100%;
	display: flex;
	flex-direction: column;
	overflow: hidden;
	padding: 10px;
	box-sizing: border-box;
}
.history-toolbar {
	margin-bottom: 10px;
	flex-shrink: 0;
	display: flex;
	align-items: center;
	gap: 10px;
}
.history-pagination {
	margin-top: 12px;
	flex-shrink: 0;
}
.drawer-body {
	padding: 4px 4px 12px;
	box-sizing: border-box;
	width: 100%;
}
.detail-meta {
	display: flex;
	align-items: center;
	gap: 10px;
	margin-bottom: 16px;
	font-size: 13px;
}
.detail-time {
	color: var(--el-text-color-placeholder);
	margin-left: auto;
}
.detail-block { margin-bottom: 14px; }
.detail-label {
	font-size: 12px;
	font-weight: 600;
	color: var(--el-text-color-primary);
	margin-bottom: 6px;
}
.detail-code {
	font-size: 12px;
	word-break: break-all;
	color: #409eff;
}
.detail-pre {
	margin: 0;
	padding: 10px;
	background: var(--el-fill-color-light);
	border-radius: 6px;
	font-size: 12px;
	max-height: 240px;
	overflow: auto;
	white-space: pre-wrap;
	word-break: break-all;
}
.detail-pre.error { color: #f56c6c; }
</style>

<style>
.history-detail-drawer.el-drawer .el-drawer__body {
	padding: 16px 20px 24px !important;
	box-sizing: border-box;
	overflow-x: hidden;
	overflow-y: auto;
}
.history-detail-drawer.el-drawer .el-drawer__header {
	margin-bottom: 0 !important;
	padding: 14px 20px !important;
	border-bottom: 1px solid var(--el-border-color-lighter);
}
</style>
