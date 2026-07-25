<template>
	<div class="repository-manager">
		<!-- 顶部操作栏 -->
		<div class="toolbar">
			<div class="toolbar-left">
				<el-input
					v-model="searchKeyword"
					placeholder="请输入仓库名称搜索"
					clearable
					style="width: 240px"
					@keyup.enter="handleSearch"
				/>
				<el-button type="primary" @click="handleSearch">搜索</el-button>
			</div>
			<div class="toolbar-right">
				<el-button type="primary" @click="openAddDialog">新增仓库</el-button>
			</div>
		</div>

		<!-- 仓库列表表格 -->
		<el-table v-loading="loading" :data="tableData" border style="width: 100%; margin-top: 12px">
			<el-table-column label="序号" type="index" width="60" align="center" />
			<el-table-column label="仓库名称" prop="name" min-width="140" />
			<el-table-column label="仓库地址" prop="html_url" min-width="200">
				<template #default="{ row }">
					<a :href="row.html_url" target="_blank" rel="noopener noreferrer">{{ row.html_url }}</a>
				</template>
			</el-table-column>
			<el-table-column label="语言" prop="lang_type" width="90" align="center">
				<template #default="{ row }">
					<el-tag size="small" :type="langTagType(row.lang_type)">{{ row.lang_type || 'java' }}</el-tag>
				</template>
			</el-table-column>
			<el-table-column label="服务地址" prop="service_host" min-width="140" show-overflow-tooltip>
				<template #default="{ row }">
					<span v-if="row.service_host">{{ row.service_host }}:{{ row.jacoco_port || 6300 }}</span>
					<span v-else style="color:#c0c4cc">未配置</span>
				</template>
			</el-table-column>
			<el-table-column label="描述" prop="description" min-width="160" show-overflow-tooltip />
			<el-table-column label="操作" width="220" align="center" fixed="right">
				<template #default="{ row }">
					<el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
					<el-button type="success" link @click="openCoverageDialog(row)">覆盖率</el-button>
					<el-button type="danger" link @click="handleDelete(row)">删除</el-button>
				</template>
			</el-table-column>
		</el-table>

		<!-- 空状态 -->
		<el-empty v-if="!loading && tableData.length === 0" description="暂无仓库" style="margin-top: 20px" />

		<!-- 分页 -->
		<div class="pagination-wrapper">
			<el-pagination
				v-model:current-page="pagination.page"
				v-model:page-size="pagination.pageSize"
				:page-sizes="[20, 50, 100]"
				:total="pagination.total"
				layout="total, sizes, prev, pager, next, jumper"
				@size-change="handleSizeChange"
				@current-change="handlePageChange"
			/>
		</div>

		<!-- 新增/编辑对话框 -->
		<el-dialog
			v-model="repoDialogVisible"
			:title="isEdit ? '编辑仓库' : '新增仓库'"
			width="560px"
			:close-on-click-modal="false"
			@closed="resetRepoForm"
		>
			<el-form ref="repoFormRef" :model="repoForm" :rules="repoFormRules" label-width="100px">
				<el-form-item label="仓库名称" prop="name">
					<el-input v-model="repoForm.name" placeholder="请输入仓库名称" maxlength="64" show-word-limit />
				</el-form-item>
				<el-form-item label="仓库地址" prop="html_url">
					<el-input v-model="repoForm.html_url" placeholder="Git 仓库 URL，如 https://github.com/..." maxlength="255" show-word-limit />
				</el-form-item>
				<el-form-item label="语言类型" prop="lang_type">
					<el-select v-model="repoForm.lang_type" placeholder="请选择语言" style="width:100%">
						<el-option label="Java" value="java" />
						<el-option label="Python" value="python" />
						<el-option label="JavaScript / TypeScript" value="javascript" />
						<el-option label="Go" value="go" />
						<el-option label="其他" value="other" />
					</el-select>
				</el-form-item>
				<!-- JaCoCo agent 配置（仅 Java 显示） -->
				<template v-if="repoForm.lang_type === 'java'">
					<el-divider content-position="left">
						<span style="font-size:12px;color:#909399">JaCoCo Agent 配置（可选，用于一键拉取覆盖率）</span>
					</el-divider>
					<el-form-item label="服务地址" prop="service_host">
						<el-input v-model="repoForm.service_host" placeholder="服务部署 IP 或域名，如 192.168.1.100" maxlength="255" />
					</el-form-item>
					<el-form-item label="Agent 端口" prop="jacoco_port">
						<el-input-number
							v-model="repoForm.jacoco_port"
							:min="1"
							:max="65535"
							placeholder="默认 6300"
							style="width:100%"
						/>
					</el-form-item>
					<el-alert
						type="info"
						:closable="false"
						style="margin-bottom:8px"
					>
						<template #default>
							Java 服务启动时需挂载 JaCoCo agent：<br />
							<code style="font-size:11px">-javaagent:jacocoagent.jar=output=tcpserver,port=6300,address=*</code>
						</template>
					</el-alert>
				</template>
				<el-form-item label="描述" prop="description">
					<el-input
						v-model="repoForm.description"
						type="textarea"
						placeholder="请输入描述（可选）"
						maxlength="500"
						show-word-limit
						:rows="3"
					/>
				</el-form-item>
			</el-form>
			<template #footer>
				<el-button @click="repoDialogVisible = false">取消</el-button>
				<el-button type="primary" :loading="saveLoading" @click="handleRepoSubmit">保存</el-button>
			</template>
		</el-dialog>

		<!-- 覆盖率触发对话框 -->
		<el-dialog
			v-model="coverageDialogVisible"
			title="触发覆盖率分析"
			width="520px"
			:close-on-click-modal="false"
			@closed="resetCoverageForm"
		>
			<el-form ref="coverageFormRef" :model="coverageForm" :rules="coverageFormRules" label-width="100px">
				<el-form-item label="新分支" prop="new_branch">
					<el-input v-model="coverageForm.new_branch" placeholder="请输入新分支名称" />
				</el-form-item>
				<el-form-item label="覆盖类型" prop="coverage_type">
					<el-select v-model="coverageForm.coverage_type" placeholder="请选择覆盖类型" style="width:100%">
						<el-option label="全量" :value="10" />
						<el-option label="增量" :value="20" />
					</el-select>
				</el-form-item>
				<el-form-item v-if="coverageForm.coverage_type === 20" label="旧分支" prop="old_branch">
					<el-input v-model="coverageForm.old_branch" placeholder="请输入旧分支名称" />
				</el-form-item>

				<!-- 仅 Java 仓库显示 dump 选项 -->
				<template v-if="currentRepo?.lang_type === 'java' || !currentRepo?.lang_type">
					<el-divider content-position="left">
						<span style="font-size:12px;color:#909399">数据采集方式</span>
					</el-divider>
					<el-form-item label="采集方式">
						<el-radio-group v-model="coverageForm.collect_mode">
							<el-radio value="manual">手动上传 XML</el-radio>
							<el-radio value="dump" :disabled="!currentRepo?.service_host">
								一键拉取（JaCoCo Agent）
								<el-tooltip v-if="!currentRepo?.service_host" content="请先在仓库配置中填写服务地址" placement="top">
									<el-icon style="margin-left:4px;color:#e6a23c"><Warning /></el-icon>
								</el-tooltip>
							</el-radio>
						</el-radio-group>
					</el-form-item>
					<template v-if="coverageForm.collect_mode === 'dump'">
						<el-form-item label="服务地址" prop="dump_address">
							<el-input v-model="coverageForm.dump_address" placeholder="服务 IP 或域名" />
						</el-form-item>
						<el-form-item label="Agent 端口" prop="dump_port">
							<el-input-number v-model="coverageForm.dump_port" :min="1" :max="65535" style="width:100%" />
						</el-form-item>
						<el-form-item label="重置数据">
							<el-switch v-model="coverageForm.dump_reset" />
							<span style="margin-left:8px;font-size:12px;color:#909399">dump 后清空 agent 中的覆盖率数据</span>
						</el-form-item>
					</template>
				</template>
			</el-form>
			<template #footer>
				<el-button @click="coverageDialogVisible = false">取消</el-button>
				<el-button type="primary" :loading="triggerLoading" @click="handleCoverageSubmit">
					{{ coverageForm.collect_mode === 'dump' ? '创建报告并拉取数据' : '创建报告' }}
				</el-button>
			</template>
		</el-dialog>
	</div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Warning } from '@element-plus/icons-vue';
import type { FormInstance, FormRules } from 'element-plus';
import { usePrecisionTestApi } from '/@/api/v1/testing/precisionTest';

const props = defineProps<{ serviceId: number }>();

const api = usePrecisionTestApi();

// ---- State ----
const loading = ref(false);
const saveLoading = ref(false);
const triggerLoading = ref(false);
const tableData = ref<any[]>([]);
const searchKeyword = ref('');

const pagination = reactive({
	page: 1,
	pageSize: 20,
	total: 0,
});

// ---- Repo dialog ----
const repoDialogVisible = ref(false);
const isEdit = ref(false);
const repoFormRef = ref<FormInstance>();
const repoForm = reactive({
	id: undefined as number | undefined,
	name: '',
	html_url: '',
	description: '',
	lang_type: 'java',
	service_host: '',
	jacoco_port: 6300,
});

const repoFormRules: FormRules = {
	name: [
		{ required: true, message: '请输入仓库名称', trigger: 'blur' },
		{ max: 64, message: '最多 64 个字符', trigger: 'blur' },
	],
	html_url: [
		{ required: true, message: '请输入仓库地址', trigger: 'blur' },
		{ max: 255, message: '最多 255 个字符', trigger: 'blur' },
	],
	lang_type: [{ required: true, message: '请选择语言类型', trigger: 'change' }],
	description: [{ max: 500, message: '最多 500 个字符', trigger: 'blur' }],
};

// ---- Coverage dialog ----
const coverageDialogVisible = ref(false);
const currentRepoId = ref<number>(0);
const currentRepo = ref<any>(null);
const coverageFormRef = ref<FormInstance>();
const coverageForm = reactive({
	new_branch: '',
	coverage_type: undefined as 10 | 20 | undefined,
	old_branch: '',
	collect_mode: 'manual' as 'manual' | 'dump',
	dump_address: '',
	dump_port: 6300,
	dump_reset: false,
});

const coverageFormRules = ref<FormRules>({
	new_branch: [{ required: true, message: '请输入新分支名称', trigger: 'blur' }],
	coverage_type: [{ required: true, message: '请选择覆盖类型', trigger: 'change' }],
});

// ---- Helpers ----
const langTagType = (lang: string) => {
	const map: Record<string, string> = {
		java: 'primary',
		python: 'success',
		javascript: 'warning',
		go: 'info',
	};
	return (map[lang] || '') as any;
};

// ---- Methods ----
const loadList = async () => {
	loading.value = true;
	try {
		const res: any = await api.repository_list({
			service_id: props.serviceId,
			name: searchKeyword.value || undefined,
			page: pagination.page,
			pageSize: pagination.pageSize,
		});
		tableData.value = res.data?.content ?? res.data?.list ?? (Array.isArray(res.data) ? res.data : []);
		pagination.total = res.data?.total ?? tableData.value.length;
	} catch (e: any) {
		ElMessage.error(e?.message || '加载仓库列表失败');
	} finally {
		loading.value = false;
	}
};

const handleSearch = () => {
	pagination.page = 1;
	loadList();
};

const handlePageChange = (page: number) => {
	pagination.page = page;
	loadList();
};

const handleSizeChange = (size: number) => {
	pagination.pageSize = size;
	pagination.page = 1;
	loadList();
};

// Add dialog
const openAddDialog = () => {
	isEdit.value = false;
	repoDialogVisible.value = true;
};

// Edit dialog
const openEditDialog = (row: any) => {
	isEdit.value = true;
	repoForm.id = row.id;
	repoForm.name = row.name;
	repoForm.html_url = row.html_url;
	repoForm.description = row.description ?? '';
	repoForm.lang_type = row.lang_type || 'java';
	repoForm.service_host = row.service_host ?? '';
	repoForm.jacoco_port = row.jacoco_port ?? 6300;
	repoDialogVisible.value = true;
};

const resetRepoForm = () => {
	repoForm.id = undefined;
	repoForm.name = '';
	repoForm.html_url = '';
	repoForm.description = '';
	repoForm.lang_type = 'java';
	repoForm.service_host = '';
	repoForm.jacoco_port = 6300;
	repoFormRef.value?.clearValidate();
};

const handleRepoSubmit = async () => {
	const valid = await repoFormRef.value?.validate().catch(() => false);
	if (!valid) return;

	saveLoading.value = true;
	try {
		const res: any = await api.repository_save({
			id: repoForm.id,
			name: repoForm.name,
			html_url: repoForm.html_url,
			description: repoForm.description,
			service_id: props.serviceId,
			lang_type: repoForm.lang_type,
			service_host: repoForm.service_host || undefined,
			jacoco_port: repoForm.jacoco_port,
		});
		if (res.code !== undefined && res.code !== 0 && res.code !== 200) {
			ElMessage.error(res.message || '保存失败');
			return;
		}
		repoDialogVisible.value = false;
		loadList();
	} catch (e: any) {
		ElMessage.error(e?.message || '保存失败');
	} finally {
		saveLoading.value = false;
	}
};

// Delete
const handleDelete = async (row: any) => {
	try {
		await ElMessageBox.confirm('是否删除该仓库？', '提示', {
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		});
	} catch {
		return;
	}

	try {
		const res: any = await api.repository_delete({ id: row.id });
		if (res.code !== undefined && res.code !== 0 && res.code !== 200) {
			ElMessage.error(res.message || '删除失败');
			return;
		}
		loadList();
	} catch (e: any) {
		ElMessage.error(e?.message || '删除失败');
	}
};

// Coverage dialog
const openCoverageDialog = (row: any) => {
	currentRepoId.value = row.id;
	currentRepo.value = row;
	// Pre-fill dump address from repo config
	coverageForm.dump_address = row.service_host ?? '';
	coverageForm.dump_port = row.jacoco_port ?? 6300;
	coverageDialogVisible.value = true;
};

const resetCoverageForm = () => {
	coverageForm.new_branch = '';
	coverageForm.coverage_type = undefined;
	coverageForm.old_branch = '';
	coverageForm.collect_mode = 'manual';
	coverageForm.dump_address = '';
	coverageForm.dump_port = 6300;
	coverageForm.dump_reset = false;
	coverageFormRef.value?.clearValidate();
};

// Dynamically add/remove old_branch rule
watch(
	() => coverageForm.coverage_type,
	(val) => {
		if (val === 20) {
			coverageFormRules.value = {
				...coverageFormRules.value,
				old_branch: [{ required: true, message: '请输入旧分支名称', trigger: 'blur' }],
			};
		} else {
			const rules = { ...coverageFormRules.value };
			delete rules.old_branch;
			coverageFormRules.value = rules;
			coverageForm.old_branch = '';
		}
	}
);

// Dynamically add dump_address rule when dump mode selected
watch(
	() => coverageForm.collect_mode,
	(val) => {
		if (val === 'dump') {
			coverageFormRules.value = {
				...coverageFormRules.value,
				dump_address: [{ required: true, message: '请输入服务地址', trigger: 'blur' }],
			};
		} else {
			const rules = { ...coverageFormRules.value };
			delete rules.dump_address;
			coverageFormRules.value = rules;
		}
	}
);

const handleCoverageSubmit = async () => {
	const valid = await coverageFormRef.value?.validate().catch(() => false);
	if (!valid) return;

	triggerLoading.value = true;
	try {
		// Step 1: create the report record
		const triggerRes: any = await api.trigger_coverage({
			repo_id: currentRepoId.value,
			new_branch: coverageForm.new_branch,
			old_branch: coverageForm.coverage_type === 20 ? coverageForm.old_branch : undefined,
			coverage_type: coverageForm.coverage_type as 10 | 20,
		});
		if (triggerRes.code !== undefined && triggerRes.code !== 0 && triggerRes.code !== 200) {
			ElMessage.error(triggerRes.message || '创建报告失败');
			return;
		}

		const newReportId = triggerRes.data?.id;

		// Step 2: if dump mode, call jacoco_dump immediately
		if (coverageForm.collect_mode === 'dump' && newReportId) {
			ElMessage.info('正在从 JaCoCo agent 拉取覆盖率数据，请稍候...');
			const dumpRes: any = await api.jacoco_dump({
				report_id: newReportId,
				address: coverageForm.dump_address,
				port: coverageForm.dump_port,
				reset: coverageForm.dump_reset,
			});
			if (dumpRes.code !== undefined && dumpRes.code !== 0 && dumpRes.code !== 200) {
				ElMessage.warning(`报告已创建（ID: ${newReportId}），但覆盖率拉取失败：${dumpRes.message || '未知错误'}。可在报告详情页手动上传 XML。`);
			} else {
				ElMessage.success(`覆盖率数据拉取成功！覆盖率：${dumpRes.data?.coverage_rate ?? '-'}`);
			}
		} else {
			ElMessage.success('报告已创建，请在覆盖率报告页上传 XML 文件');
		}

		coverageDialogVisible.value = false;
	} catch (e: any) {
		ElMessage.error(e?.message || '操作失败');
	} finally {
		triggerLoading.value = false;
	}
};

// ---- Lifecycle ----
onMounted(() => {
	loadList();
});
</script>

<style scoped lang="scss">
.repository-manager {
	padding: 16px;
}

.toolbar {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 12px;
}

.toolbar-left {
	display: flex;
	align-items: center;
	gap: 8px;
}

.pagination-wrapper {
	display: flex;
	justify-content: flex-end;
	margin-top: 16px;
}
</style>
