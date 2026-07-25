<template>
	<div class="coverage-report-list">
		<!-- 顶部搜索栏 -->
		<div class="toolbar">
			<div class="toolbar-left">
				<el-input
					v-model="searchKeyword"
					placeholder="请输入项目名称搜索"
					clearable
					style="width: 240px"
					@keyup.enter="handleSearch"
				/>
				<el-button type="primary" @click="handleSearch">搜索</el-button>
			</div>
		</div>

		<!-- 报告列表表格 -->
		<el-table v-loading="loading" :data="tableData" border style="width: 100%; margin-top: 12px">
			<el-table-column label="序号" type="index" width="60" align="center" />
			<el-table-column label="项目名称" prop="name" min-width="160">
				<template #default="{ row }">
					<el-link type="primary" @click="handleNavigate(row)">{{ row.name }}</el-link>
				</template>
			</el-table-column>
			<el-table-column label="覆盖类型" prop="coverage_type" width="100" align="center">
				<template #default="{ row }">
					<el-tag v-if="row.coverage_type === 10" type="success">全量</el-tag>
					<el-tag v-else-if="row.coverage_type === 20" type="warning">增量</el-tag>
					<span v-else>-</span>
				</template>
			</el-table-column>
			<el-table-column label="覆盖率" prop="coverage_rate" width="100" align="center" />
			<el-table-column label="新分支" prop="new_branches" min-width="120" />
			<el-table-column label="旧分支" prop="old_branches" min-width="120" />
			<el-table-column label="新 Commit ID" prop="new_last_commit_id" min-width="160" show-overflow-tooltip />
			<el-table-column label="旧 Commit ID" prop="old_last_commit_id" min-width="160" show-overflow-tooltip />
			<el-table-column label="操作" width="100" align="center" fixed="right">
				<template #default="{ row }">
					<el-button type="danger" link @click="handleDelete(row)">删除</el-button>
				</template>
			</el-table-column>
		</el-table>

		<!-- 空状态 -->
		<el-empty v-if="!loading && tableData.length === 0" description="暂无报告" style="margin-top: 20px" />

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
	</div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { usePrecisionTestApi } from '/@/api/v1/testing/precisionTest';

const props = defineProps<{ serviceId: number }>();

const router = useRouter();
const api = usePrecisionTestApi();

// ---- State ----
const loading = ref(false);
const tableData = ref<any[]>([]);
const searchKeyword = ref('');

const pagination = reactive({
	page: 1,
	pageSize: 20,
	total: 0,
});

// ---- Methods ----
const loadList = async () => {
	loading.value = true;
	try {
		const res: any = await api.coverage_report_list({
			service_id: props.serviceId,
			name: searchKeyword.value || undefined,
			page: pagination.page,
			pageSize: pagination.pageSize,
		});
		const data = res?.data;
		tableData.value = data?.content ?? data?.list ?? (Array.isArray(data) ? data : []);
		pagination.total = data?.total ?? tableData.value.length;
	} catch (e: any) {
		ElMessage.error(e?.message || '加载报告列表失败');
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

const handleNavigate = (row: any) => {
	router.push({ path: '/testing/precision-test/coverage/' + row.id });
};

const handleDelete = async (row: any) => {
	try {
		await ElMessageBox.confirm('是否删除该报告？', '提示', {
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		});
	} catch {
		return; // user cancelled
	}

	try {
		const res: any = await api.coverage_report_delete({ id: row.id });
		if (res.code !== undefined && res.code !== 0 && res.code !== 200) {
			ElMessage.error(res.message || '删除失败');
			return;
		}
		loadList();
	} catch (e: any) {
		ElMessage.error(e?.message || '删除失败');
	}
};

// ---- Lifecycle ----
onMounted(() => {
	loadList();
});
</script>

<style scoped lang="scss">
.coverage-report-list {
	padding: 16px;
}

.toolbar {
	display: flex;
	align-items: center;
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
