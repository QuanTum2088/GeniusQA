<template>
	<div class="doc-panel-wrap">
		<template v-if="docInfo">
			<div class="doc-header">
				<div class="doc-header-left">
					<span class="doc-method-badge" :style="{ background: methodColor }">{{ methodName }}</span>
					<span class="doc-path" :title="docInfo.url">{{ docInfo.url }}</span>
				</div>
				<el-tag v-if="docInfo.name" size="small" effect="plain" type="info">{{ docInfo.name }}</el-tag>
			</div>

			<div v-if="docInfo.description" class="doc-desc-block">{{ docInfo.description }}</div>

			<div v-if="docInfo.parameters.length" class="doc-section">
				<div class="doc-section-title">请求参数</div>
				<el-table :data="docInfo.parameters" border stripe size="small" empty-text="暂无请求参数">
					<el-table-column prop="name" label="参数名" min-width="140" show-overflow-tooltip>
						<template #default="{ row }"><span class="doc-param-name">{{ row.name }}</span></template>
					</el-table-column>
					<el-table-column label="位置" width="100" align="center">
						<template #default="{ row }">
							<span class="doc-in-badge" :class="'in-' + row.in">{{ row.in }}</span>
						</template>
					</el-table-column>
					<el-table-column label="类型" width="110" align="center">
						<template #default="{ row }"><span class="doc-type">{{ row.type || '-' }}</span></template>
					</el-table-column>
					<el-table-column label="必填" width="80" align="center">
						<template #default="{ row }">
							<el-tag v-if="row.required" size="small" type="danger" effect="plain">必填</el-tag>
							<span v-else class="doc-optional">可选</span>
						</template>
					</el-table-column>
					<el-table-column prop="description" label="说明" min-width="180" show-overflow-tooltip>
						<template #default="{ row }">{{ row.description || '-' }}</template>
					</el-table-column>
				</el-table>
			</div>

			<div v-if="showBodySection" class="doc-section">
				<div class="doc-section-title">Body 参数</div>
				<div v-if="docInfo.requestBodyType" class="doc-content-type">
					Content-Type: <code>{{ docInfo.requestBodyType }}</code>
				</div>
				<el-table
					v-if="docInfo.bodyFields.length"
					:data="docInfo.bodyFields"
					border
					stripe
					size="small"
					empty-text="暂无 Body 参数"
				>
					<el-table-column prop="name" label="字段名" min-width="140" show-overflow-tooltip>
						<template #default="{ row }"><span class="doc-param-name">{{ row.name }}</span></template>
					</el-table-column>
					<el-table-column label="类型" width="110" align="center">
						<template #default="{ row }"><span class="doc-type">{{ row.type || '-' }}</span></template>
					</el-table-column>
					<el-table-column label="必填" width="80" align="center">
						<template #default="{ row }">
							<el-tag v-if="row.required" size="small" type="danger" effect="plain">必填</el-tag>
							<span v-else class="doc-optional">可选</span>
						</template>
					</el-table-column>
					<el-table-column prop="description" label="说明" min-width="180" show-overflow-tooltip>
						<template #default="{ row }">{{ row.description || '-' }}</template>
					</el-table-column>
				</el-table>
				<div v-else-if="docInfo.requestBodyRaw" class="doc-raw-schema">
					<pre class="doc-pre">{{ docInfo.requestBodyRaw }}</pre>
				</div>
			</div>

			<div v-if="docInfo.responses.length" class="doc-section">
				<div class="doc-section-title">返回响应</div>
				<div v-for="resp in docInfo.responses" :key="resp.code" class="doc-response-item">
					<div class="doc-response-header">
						<el-tag
							size="small"
							:type="resp.code >= 200 && resp.code < 300 ? 'success' : resp.code >= 400 ? 'danger' : 'warning'"
							effect="light"
						>{{ resp.code }}</el-tag>
						<span class="doc-response-desc">{{ resp.description || '-' }}</span>
						<span v-if="resp.contentType" class="doc-response-ct">{{ resp.contentType }}</span>
					</div>
					<el-table
						v-if="resp.fields.length"
						:data="resp.fields"
						border
						stripe
						size="small"
						style="margin-top: 8px"
					>
						<el-table-column prop="name" label="字段名" min-width="140" show-overflow-tooltip>
							<template #default="{ row }"><span class="doc-param-name">{{ row.name }}</span></template>
						</el-table-column>
						<el-table-column label="类型" width="110" align="center">
							<template #default="{ row }"><span class="doc-type">{{ row.type || '-' }}</span></template>
						</el-table-column>
						<el-table-column prop="description" label="说明" min-width="180" show-overflow-tooltip>
							<template #default="{ row }">{{ row.description || '-' }}</template>
						</el-table-column>
					</el-table>
					<div v-else-if="resp.example" class="doc-raw-schema">
						<pre class="doc-pre">{{ resp.example }}</pre>
					</div>
				</div>
			</div>
		</template>

		<div v-else class="doc-empty">
			<el-icon style="font-size:36px;color:#dcdfe6"><Document /></el-icon>
			<p>暂无接口文档，请先拉取 Swagger / Apifox 文档</p>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Document } from '@element-plus/icons-vue';

const props = defineProps<{ apiData: any }>();

const METHOD_MAP: Record<number, { label: string; color: string }> = {
	1: { label: 'GET', color: '#67C23A' },
	2: { label: 'POST', color: '#409EFF' },
	3: { label: 'PUT', color: '#E6A23C' },
	4: { label: 'DELETE', color: '#F56C6C' },
	5: { label: 'PATCH', color: '#8E44AD' },
	6: { label: 'OPTIONS', color: '#909399' },
};

const BODY_IN = new Set(['body', 'formdata', 'formData']);

const schemaType = (v: any): string => {
	if (!v || typeof v !== 'object') return '-';
	if (v.type) return v.type;
	if (v.$ref) return String(v.$ref).split('/').pop() || '-';
	if (v.items) return `array<${schemaType(v.items)}>`;
	return '-';
};

const fieldsFromSchema = (schema: any): any[] => {
	if (!schema || typeof schema !== 'object') return [];
	const target = schema.properties
		? schema
		: (schema.items?.properties ? schema.items : null);
	if (!target?.properties) return [];
	const required: string[] = Array.isArray(target.required) ? target.required : (Array.isArray(schema.required) ? schema.required : []);
	return Object.entries(target.properties).map(([k, v]: any) => ({
		name: k,
		type: schemaType(v),
		required: required.includes(k),
		description: v?.description || '',
	}));
};

const docInfo = computed(() => {
	const info = props.apiData?.api_info || props.apiData || {};
	const doc = info.document;
	if (!doc) return null;

	const method = info.req?.method ?? 2;
	const allParams: any[] = Array.isArray(doc.parameters) ? doc.parameters : [];

	const parameters: any[] = [];
	const bodyFromParams: any[] = [];

	for (const p of allParams) {
		const loc = String(p.in || 'query');
		const row = {
			name: p.name || '-',
			in: loc,
			type: p.schema?.type || p.type || schemaType(p.schema) || '-',
			required: !!p.required,
			description: p.description || '',
		};
		if (BODY_IN.has(loc) || BODY_IN.has(loc.toLowerCase())) {
			bodyFromParams.push(row);
		} else {
			parameters.push(row);
		}
	}

	let requestBodyType = '';
	let bodyFields: any[] = [];
	let requestBodyRaw = '';
	let hasRequestBody = false;

	if (doc.requestBody) {
		hasRequestBody = true;
		const content = doc.requestBody.content || {};
		const ct = Object.keys(content)[0] || '';
		requestBodyType = ct || (doc.requestBody.required ? 'application/json' : '');
		const schema = ct ? (content[ct]?.schema || {}) : {};
		bodyFields = fieldsFromSchema(schema);
		if (!bodyFields.length && Object.keys(schema).length) {
			requestBodyRaw = JSON.stringify(schema, null, 2);
		}
	}

	// Swagger2 / formData：参数里的 body/formData 归入 Body
	if (!bodyFields.length && bodyFromParams.length) {
		bodyFields = bodyFromParams.map((p) => ({
			name: p.name,
			type: p.type,
			required: p.required,
			description: p.description,
		}));
		if (!requestBodyType) {
			const hasFile = bodyFromParams.some((p) => String(p.type).toLowerCase() === 'file');
			requestBodyType = hasFile ? 'multipart/form-data' : 'application/x-www-form-urlencoded';
		}
		hasRequestBody = true;
	}

	const responses: any[] = [];
	if (doc.responses) {
		for (const [code, resp] of Object.entries(doc.responses as Record<string, any>)) {
			const content = resp.content || {};
			const ct = Object.keys(content)[0] || '';
			const schema = ct ? (content[ct]?.schema || {}) : (resp.schema || {});
			const fields = fieldsFromSchema(schema);
			let example = '';
			if (!fields.length && schema && Object.keys(schema).length) {
				example = JSON.stringify(schema, null, 2);
			}
			responses.push({
				code: Number(code) || code,
				description: resp.description || '',
				contentType: ct,
				fields,
				example,
			});
		}
	}

	return {
		name: info.name || doc.summary || doc.operationId || '',
		url: info.url || '',
		method,
		description: doc.description || doc.summary || '',
		parameters,
		bodyFields,
		requestBodyType,
		requestBodyRaw,
		hasRequestBody,
		responses,
	};
});

const showBodySection = computed(() => {
	const d = docInfo.value;
	if (!d) return false;
	return d.hasRequestBody || d.bodyFields.length > 0 || !!d.requestBodyRaw;
});

const methodName = computed(() => METHOD_MAP[docInfo.value?.method ?? 2]?.label || 'GET');
const methodColor = computed(() => METHOD_MAP[docInfo.value?.method ?? 2]?.color || '#409EFF');
</script>

<style scoped>
.doc-panel-wrap {
	height: 100%;
	overflow-y: auto;
	background: var(--el-bg-color);
	box-sizing: border-box;
}
.doc-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 12px;
	padding: 14px 20px;
	background: var(--el-fill-color-light);
	border-bottom: 1px solid var(--el-border-color);
}
.doc-header-left {
	display: flex;
	align-items: center;
	gap: 10px;
	min-width: 0;
	flex: 1;
}
.doc-method-badge {
	display: inline-block;
	padding: 3px 10px;
	border-radius: 4px;
	color: #fff;
	font-size: 12px;
	font-weight: 700;
	letter-spacing: .5px;
	flex-shrink: 0;
}
.doc-path {
	font-family: Consolas, Monaco, monospace;
	font-size: 14px;
	color: var(--el-text-color-primary);
	word-break: break-all;
}
.doc-desc-block {
	padding: 10px 20px;
	font-size: 13px;
	line-height: 1.6;
	color: var(--el-text-color-regular);
	background: var(--el-color-warning-light-9);
	border-bottom: 1px solid var(--el-color-warning-light-5);
}
.doc-section {
	padding: 16px 20px;
	border-bottom: 1px solid var(--el-border-color-lighter);
}
.doc-section:last-child { border-bottom: none; }
.doc-section-title {
	font-size: 13px;
	font-weight: 600;
	color: var(--el-text-color-primary);
	margin-bottom: 12px;
	padding-left: 8px;
	border-left: 3px solid #409eff;
}
.doc-content-type {
	font-size: 12px;
	color: var(--el-text-color-placeholder);
	margin-bottom: 10px;
}
.doc-content-type code {
	background: var(--el-fill-color-light);
	padding: 1px 6px;
	border-radius: 3px;
	font-family: Consolas, Monaco, monospace;
	color: var(--el-text-color-regular);
}
.doc-param-name {
	font-family: Consolas, Monaco, monospace;
	font-size: 12px;
	color: #e6a23c;
	font-weight: 600;
}
.doc-type {
	font-family: Consolas, Monaco, monospace;
	font-size: 12px;
	color: #67c23a;
}
.doc-optional {
	color: var(--el-text-color-placeholder);
	font-size: 12px;
}
.doc-in-badge {
	display: inline-block;
	padding: 1px 6px;
	border-radius: 3px;
	font-size: 11px;
	font-weight: 500;
}
.in-query { background: var(--el-color-primary-light-9); color: #409eff; }
.in-path { background: var(--el-color-warning-light-9); color: #e6a23c; }
.in-header { background: var(--el-color-success-light-9); color: #67c23a; }
.in-cookie { background: var(--el-color-danger-light-9); color: #f56c6c; }
.doc-response-item { margin-bottom: 16px; }
.doc-response-item:last-child { margin-bottom: 0; }
.doc-response-header {
	display: flex;
	align-items: center;
	gap: 8px;
	flex-wrap: wrap;
}
.doc-response-desc {
	font-size: 13px;
	color: var(--el-text-color-regular);
}
.doc-response-ct {
	margin-left: auto;
	font-size: 11px;
	color: var(--el-text-color-placeholder);
	font-family: Consolas, Monaco, monospace;
}
.doc-raw-schema {
	background: #1e1e1e;
	border-radius: 6px;
	overflow: hidden;
	margin-top: 8px;
}
.doc-pre {
	margin: 0;
	padding: 12px 14px;
	font-family: Consolas, Monaco, monospace;
	font-size: 12px;
	color: #d4d4d4;
	white-space: pre-wrap;
	word-break: break-all;
	line-height: 1.6;
}
.doc-empty {
	height: 100%;
	min-height: 220px;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	color: var(--el-text-color-placeholder);
	gap: 8px;
	font-size: 13px;
}
</style>
