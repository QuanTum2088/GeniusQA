<template>
	<div class="coverage-detail-viewer" v-loading="loading">
		<!-- 顶部操作栏 -->
		<div class="viewer-header">
			<!-- Breadcrumb navigation -->
			<el-breadcrumb separator="/" class="breadcrumb">
				<el-breadcrumb-item
					v-for="(node, idx) in breadcrumb"
					:key="idx"
					:class="{ 'breadcrumb-clickable': idx < breadcrumb.length - 1 }"
					@click="idx < breadcrumb.length - 1 && navigateBreadcrumb(idx)"
				>
					<span>{{ elTypeIcon(node.el_type) }} {{ node.label }}</span>
				</el-breadcrumb-item>
			</el-breadcrumb>

			<!-- 上传 XML 按钮（方案 A：手动上传） -->
			<div class="header-actions">
				<el-upload
					:show-file-list="false"
					accept=".xml"
					:before-upload="handleXmlUpload"
				>
					<el-button type="primary" :loading="uploadLoading" size="small">
						<el-icon><Upload /></el-icon>
						上传覆盖率 XML
					</el-button>
				</el-upload>
				<el-tooltip content="支持 JaCoCo XML / Cobertura XML 格式" placement="bottom">
					<el-icon style="color:#909399;cursor:help"><QuestionFilled /></el-icon>
				</el-tooltip>
			</div>
		</div>

		<!-- CodeView (shown when el_type === 'method') -->
		<div v-if="showCodeView" class="code-view-wrapper">
			<CodeView
				ref="codeViewRef"
				:content="codeContent"
				:linesCoveredStatus="linesCoveredStatus"
			/>
		</div>

		<!-- Drill-down table -->
		<div v-else>
			<!-- Package level table (el_type === 'report') -->
			<el-table
				v-if="currentElType === 'report'"
				:data="tableData"
				border
				style="width: 100%; margin-top: 12px"
			>
				<el-table-column label="包名" prop="package_name" min-width="200">
					<template #default="{ row }">
						<el-link type="primary" @click="drillPackage(row)">{{ row.package_name }}</el-link>
					</template>
				</el-table-column>
				<el-table-column label="指令覆盖率" min-width="150">
					<template #default="{ row }">
						<CoverageBar :missed="row.instruction_missed" :covered="row.instruction_covered" />
					</template>
				</el-table-column>
				<el-table-column label="分支覆盖率" min-width="150">
					<template #default="{ row }">
						<CoverageBar :missed="row.branch_missed" :covered="row.branch_covered" />
					</template>
				</el-table-column>
				<el-table-column label="行覆盖率" min-width="150">
					<template #default="{ row }">
						<CoverageBar :missed="row.line_missed" :covered="row.line_covered" />
					</template>
				</el-table-column>
				<el-table-column label="方法覆盖率" min-width="150">
					<template #default="{ row }">
						<CoverageBar :missed="row.method_missed" :covered="row.method_covered" />
					</template>
				</el-table-column>
				<el-table-column label="类覆盖率" min-width="150">
					<template #default="{ row }">
						<CoverageBar :missed="row.class_missed" :covered="row.class_covered" />
					</template>
				</el-table-column>
			</el-table>

			<!-- Class level table (el_type === 'package') -->
			<el-table
				v-else-if="currentElType === 'package'"
				:data="tableData"
				border
				style="width: 100%; margin-top: 12px"
			>
				<el-table-column label="类名" prop="class_name" min-width="200">
					<template #default="{ row }">
						<el-link type="primary" @click="drillClass(row)">{{ row.class_name }}</el-link>
					</template>
				</el-table-column>
				<el-table-column label="指令覆盖率" min-width="150">
					<template #default="{ row }">
						<CoverageBar :missed="row.instruction_missed" :covered="row.instruction_covered" />
					</template>
				</el-table-column>
				<el-table-column label="分支覆盖率" min-width="150">
					<template #default="{ row }">
						<CoverageBar :missed="row.branch_missed" :covered="row.branch_covered" />
					</template>
				</el-table-column>
				<el-table-column label="行覆盖率" min-width="150">
					<template #default="{ row }">
						<CoverageBar :missed="row.line_missed" :covered="row.line_covered" />
					</template>
				</el-table-column>
				<el-table-column label="方法覆盖率" min-width="150">
					<template #default="{ row }">
						<CoverageBar :missed="row.method_missed" :covered="row.method_covered" />
					</template>
				</el-table-column>
			</el-table>

			<!-- Method level table (el_type === 'class') -->
			<el-table
				v-else-if="currentElType === 'class'"
				:data="tableData"
				border
				style="width: 100%; margin-top: 12px"
			>
				<el-table-column label="方法名" prop="name" min-width="200">
					<template #default="{ row }">
						<el-link type="primary" @click="drillMethod(row)">{{ row.name }}</el-link>
					</template>
				</el-table-column>
				<el-table-column label="指令覆盖率" min-width="150">
					<template #default="{ row }">
						<CoverageBar :missed="row.instruction_missed" :covered="row.instruction_covered" />
					</template>
				</el-table-column>
				<el-table-column label="分支覆盖率" min-width="150">
					<template #default="{ row }">
						<CoverageBar :missed="row.branch_missed" :covered="row.branch_covered" />
					</template>
				</el-table-column>
				<el-table-column label="行覆盖率" min-width="150">
					<template #default="{ row }">
						<CoverageBar :missed="row.line_missed" :covered="row.line_covered" />
					</template>
				</el-table-column>
			</el-table>

			<el-empty
				v-if="!loading && tableData.length === 0"
				description="暂无数据"
				style="margin-top: 20px"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Upload, QuestionFilled } from '@element-plus/icons-vue';
import { usePrecisionTestApi } from '/@/api/v1/testing/precisionTest';
import CodeView from './CodeView.vue';

// ---- Inline CoverageBar component ----
const CoverageBar = {
	props: {
		missed: { type: Number, default: 0 },
		covered: { type: Number, default: 0 },
	},
	setup(props: { missed: number; covered: number }) {
		const pct = (covered: number, missed: number) => {
			const total = covered + missed;
			if (total === 0) return 0;
			return Math.round((covered / total) * 100 * 100) / 100;
		};
		return { pct };
	},
	template: `
		<div v-if="(missed + covered) === 0">n/a</div>
		<div v-else style="display:flex; align-items:center; gap:4px; min-width:120px">
			<div style="display:flex; flex:1; height:12px; border-radius:2px; overflow:hidden"
				 :title="\`\${covered}/\${covered+missed}\`">
				<div :style="{ width: pct(covered, missed) + '%', background: '#67c23a' }"></div>
				<div :style="{ width: pct(missed, covered) + '%', background: '#f56c6c' }"></div>
			</div>
			<span style="font-size:12px; white-space:nowrap">{{ pct(covered, missed) }}%</span>
		</div>
	`,
};

// ---- Types ----
type ElType = 'report' | 'package' | 'class' | 'method';

interface BreadcrumbNode {
	label: string;
	el_type: ElType;
	package_name?: string;
	class_id?: number;
	method_offset?: number;
}

// ---- Setup ----
const route = useRoute();
const api = usePrecisionTestApi();

const reportId = computed(() => Number(route.params.reportId));

// ---- State ----
const loading = ref(false);
const reportName = ref('');
const tableData = ref<any[]>([]);
const breadcrumb = ref<BreadcrumbNode[]>([]);
const currentElType = ref<ElType>('report');

// CodeView state
const showCodeView = ref(false);
const codeContent = ref('');
const linesCoveredStatus = ref<Record<number, 0 | 1 | 2>>({});
const currentMethodOffset = ref(0);
const classFileContent = ref('');
const codeViewRef = ref<InstanceType<typeof CodeView> | null>(null);

// Upload state
const uploadLoading = ref(false);

// ---- Upload XML handler ----
const handleXmlUpload = async (file: File): Promise<false> => {
	uploadLoading.value = true;
	try {
		const formData = new FormData();
		formData.append('file', file);
		formData.append('report_id', String(reportId.value));
		const res: any = await api.upload_xml(formData);
		if (res.code !== undefined && res.code !== 0 && res.code !== 200) {
			ElMessage.error(res.message || '上传失败');
		} else {
			const d = res.data;
			ElMessage.success(
				`上传成功！覆盖率 ${d?.coverage_rate ?? '-'}，共 ${d?.package_count ?? 0} 个包、${d?.class_count ?? 0} 个类、${d?.method_count ?? 0} 个方法`
			);
			// Reload package list to show fresh data
			await loadPackages();
		}
	} catch (e: any) {
		ElMessage.error(e?.message || '上传失败');
	} finally {
		uploadLoading.value = false;
	}
	// Return false to prevent el-upload's default upload behavior
	return false;
};
// ---- Helpers ----
const elTypeIcon = (elType: ElType): string => {
	const icons: Record<ElType, string> = {
		report: '📋',
		package: '📦',
		class: '📄',
		method: '⚙️',
	};
	return icons[elType] ?? '';
};

// ---- Data loading ----
const loadPackages = async () => {
	loading.value = true;
	try {
		const res: any = await api.coverage_detail({
			report_id: reportId.value,
			el_type: 'report',
		});
		const data = res?.data;
		tableData.value = Array.isArray(data) ? data : (data?.list ?? data?.content ?? []);
		currentElType.value = 'report';
	} catch (e: any) {
		ElMessage.error(e?.message || '加载包列表失败');
	} finally {
		loading.value = false;
	}
};

const loadClasses = async (packageName: string) => {
	loading.value = true;
	try {
		const res: any = await api.coverage_detail({
			report_id: reportId.value,
			el_type: 'package',
			package_name: packageName,
		});
		const data = res?.data;
		tableData.value = Array.isArray(data) ? data : (data?.list ?? data?.content ?? []);
		currentElType.value = 'package';
	} catch (e: any) {
		ElMessage.error(e?.message || '加载类列表失败');
	} finally {
		loading.value = false;
	}
};

const loadMethods = async (classId: number) => {
	loading.value = true;
	try {
		const res: any = await api.coverage_detail({
			report_id: reportId.value,
			el_type: 'class',
			class_id: classId,
		});
		const data = res?.data;
		// Store class file content for CodeView
		classFileContent.value = data?.class_file_content ?? '';
		const methods = data?.methods ?? (Array.isArray(data) ? data : []);
		tableData.value = methods;
		currentElType.value = 'class';
	} catch (e: any) {
		ElMessage.error(e?.message || '加载方法列表失败');
	} finally {
		loading.value = false;
	}
};

// ---- Drill-down actions ----
const drillPackage = (row: any) => {
	const packageName: string = row.package_name;
	breadcrumb.value.push({
		label: packageName,
		el_type: 'package',
		package_name: packageName,
	});
	showCodeView.value = false;
	loadClasses(packageName);
};

const drillClass = (row: any) => {
	const className: string = row.class_name;
	breadcrumb.value.push({
		label: className,
		el_type: 'class',
		class_id: row.id,
	});
	showCodeView.value = false;
	loadMethods(row.id);
};

const drillMethod = async (row: any) => {
	const methodName: string = row.name;
	breadcrumb.value.push({
		label: methodName,
		el_type: 'method',
		method_offset: row.offset,
	});

	// Parse lines_covered_status JSON
	let parsedStatus: Record<number, 0 | 1 | 2> = {};
	try {
		if (row.lines_covered_status) {
			parsedStatus = JSON.parse(row.lines_covered_status);
		}
	} catch {
		parsedStatus = {};
	}

	codeContent.value = classFileContent.value;
	linesCoveredStatus.value = parsedStatus;
	currentMethodOffset.value = row.offset ?? 0;
	currentElType.value = 'method';
	showCodeView.value = true;

	await nextTick();
	codeViewRef.value?.locationEl(currentMethodOffset.value);
};

// ---- Breadcrumb navigation ----
const navigateBreadcrumb = async (idx: number) => {
	// Truncate breadcrumb to the clicked node
	breadcrumb.value = breadcrumb.value.slice(0, idx + 1);
	showCodeView.value = false;

	const node = breadcrumb.value[idx];
	currentElType.value = node.el_type;

	if (node.el_type === 'report') {
		await loadPackages();
	} else if (node.el_type === 'package' && node.package_name) {
		await loadClasses(node.package_name);
	} else if (node.el_type === 'class' && node.class_id !== undefined) {
		await loadMethods(node.class_id);
	}
};

// ---- Lifecycle ----
onMounted(async () => {
	loading.value = true;
	try {
		// Load report metadata
		const reportRes: any = await api.coverage_report_get({ id: reportId.value });
		const reportData = reportRes?.data;
		reportName.value = reportData?.name ?? `Report #${reportId.value}`;

		// Initialize breadcrumb with report node
		breadcrumb.value = [
			{
				label: reportName.value,
				el_type: 'report',
			},
		];
	} catch (e: any) {
		ElMessage.error(e?.message || '加载报告信息失败');
		reportName.value = `Report #${reportId.value}`;
		breadcrumb.value = [{ label: reportName.value, el_type: 'report' }];
	} finally {
		loading.value = false;
	}

	// Load package list
	await loadPackages();
});
</script>

<style scoped lang="scss">
.coverage-detail-viewer {
	padding: 16px;
}

.viewer-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 16px;
	gap: 12px;
}

.breadcrumb {
	font-size: 14px;
	flex: 1;

	.breadcrumb-clickable {
		cursor: pointer;

		span {
			color: #409eff;

			&:hover {
				text-decoration: underline;
			}
		}
	}
}

.header-actions {
	display: flex;
	align-items: center;
	gap: 8px;
	flex-shrink: 0;
}

.code-view-wrapper {
	margin-top: 12px;
}
</style>
