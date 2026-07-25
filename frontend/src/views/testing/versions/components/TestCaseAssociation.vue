<template>
	<el-dialog :model-value="modelValue" title="关联测试用例" width="900px" :close-on-click-modal="false" @close="handleClose">
		<div class="association-container">
			<!-- 项目选择 -->
			<el-form :inline="true">
				<el-form-item label="选择项目">
					<el-select v-model="selectedProjectId" placeholder="请选择项目" @change="handleProjectChange" style="width: 300px">
						<el-option v-for="project in projectList" :key="project.id" :label="project.name" :value="project.id" />
					</el-select>
				</el-form-item>
			</el-form>

			<!-- 测试用例列表 -->
			<el-table
				ref="tableRef"
				:data="testcaseList"
				v-loading="loading"
				@selection-change="handleSelectionChange"
				max-height="400"
				style="width: 100%"
			>
				<el-table-column type="selection" width="55" />
				<el-table-column prop="id" label="ID" width="80" />
				<el-table-column prop="title" label="用例标题" min-width="200" show-overflow-tooltip />
				<el-table-column prop="priority" label="优先级" width="100">
					<template #default="{ row }">
						<el-tag v-if="row.priority === 'critical'" type="danger" size="small">紧急</el-tag>
						<el-tag v-else-if="row.priority === 'high'" type="warning" size="small">高</el-tag>
						<el-tag v-else-if="row.priority === 'medium'" type="info" size="small">中</el-tag>
						<el-tag v-else type="success" size="small">低</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="status" label="状态" width="100">
					<template #default="{ row }">
						<el-tag v-if="row.status === 'active'" type="success" size="small">激活</el-tag>
						<el-tag v-else-if="row.status === 'draft'" type="info" size="small">草稿</el-tag>
						<el-tag v-else type="danger" size="small">已废弃</el-tag>
					</template>
				</el-table-column>
			</el-table>

			<div class="selected-info">
				已选择 <span class="count">{{ selectedTestCases.length }}</span> 个测试用例
			</div>
		</div>

		<template #footer>
			<el-button @click="handleClose">取消</el-button>
			<el-button type="primary" @click="handleSubmit" :loading="submitting" :disabled="!selectedProjectId">确定</el-button>
		</template>
	</el-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { getProjectList } from '/@/api/v1/projects/project';
import { getTestCaseList, associateTestCases } from '/@/api/v1/testing/testcases';

const props = defineProps({
	modelValue: {
		type: Boolean,
		default: false,
	},
	versionId: {
		type: Number,
		required: true,
	},
});

const emit = defineEmits(['update:modelValue']);

const tableRef = ref();
const loading = ref(false);
const submitting = ref(false);
const projectList = ref<any[]>([]);
const testcaseList = ref<any[]>([]);
const selectedProjectId = ref<number | null>(null);
const selectedTestCases = ref<any[]>([]);

// 获取项目列表
const getProjects = async () => {
	try {
		const res = await getProjectList({ page: 1, page_size: 100 });
		if (res.code === 200) {
			projectList.value = res.data.items || [];
			// 如果只有一个项目，自动选中
			if (projectList.value.length === 1) {
				selectedProjectId.value = projectList.value[0].id;
				getTestCases();
			}
		}
	} catch (error) {
		console.error('获取项目列表失败:', error);
	}
};

// 获取测试用例列表
const getTestCases = async () => {
	if (!selectedProjectId.value) return;

	loading.value = true;
	try {
		const res = await getTestCaseList({
			project_id: selectedProjectId.value,
			page: 1,
			page_size: 1000, // 获取所有用例
		});
		if (res.code === 200) {
			testcaseList.value = res.data.items || [];
		}
	} catch (error) {
		console.error('获取测试用例列表失败:', error);
		ElMessage.error('获取测试用例列表失败');
	} finally {
		loading.value = false;
	}
};

// 项目切换
const handleProjectChange = () => {
	selectedTestCases.value = [];
	getTestCases();
};

// 选择变化
const handleSelectionChange = (selection: any[]) => {
	selectedTestCases.value = selection;
};

// 提交
const handleSubmit = async () => {
	if (selectedTestCases.value.length === 0) {
		ElMessage.warning('请至少选择一个测试用例');
		return;
	}

	submitting.value = true;
	try {
		const res = await associateTestCases({
			version_id: props.versionId,
			testcase_ids: selectedTestCases.value.map((item) => item.id),
		});

		if (res.code === 200) {
			ElMessage.success('关联成功');
			handleClose();
		}
	} catch (error) {
		console.error('关联失败:', error);
		ElMessage.error('关联失败');
	} finally {
		submitting.value = false;
	}
};

// 关闭
const handleClose = () => {
	emit('update:modelValue', false);
};

onMounted(() => {
	getProjects();
});
</script>

<style scoped lang="scss">
.association-container {
	.selected-info {
		margin-top: 15px;
		padding: 10px;
		background-color: #f5f7fa;
		border-radius: 4px;
		text-align: center;

		.count {
			color: #409eff;
			font-weight: bold;
			font-size: 18px;
		}
	}
}
</style>
