<template>
	<el-dialog :model-value="modelValue" title="测试用例详情" width="800px" @close="handleClose">
		<div v-loading="loading">
			<el-descriptions :column="2" border>
				<el-descriptions-item label="用例ID">{{ detail.id }}</el-descriptions-item>
				<el-descriptions-item label="用例标题">{{ detail.title }}</el-descriptions-item>
				<el-descriptions-item label="优先级">
					<el-tag v-if="detail.priority === 'critical'" type="danger">紧急</el-tag>
					<el-tag v-else-if="detail.priority === 'high'" type="warning">高</el-tag>
					<el-tag v-else-if="detail.priority === 'medium'" type="info">中</el-tag>
					<el-tag v-else type="success">低</el-tag>
				</el-descriptions-item>
				<el-descriptions-item label="状态">
					<el-tag v-if="detail.status === 'active'" type="success">激活</el-tag>
					<el-tag v-else-if="detail.status === 'draft'" type="info">草稿</el-tag>
					<el-tag v-else type="danger">已废弃</el-tag>
				</el-descriptions-item>
				<el-descriptions-item label="测试类型">{{ getTestTypeLabel(detail.test_type) }}</el-descriptions-item>
				<el-descriptions-item label="作者">{{ detail.author_name || '-' }}</el-descriptions-item>
				<el-descriptions-item label="指派人">{{ detail.assignee_name || '-' }}</el-descriptions-item>
				<el-descriptions-item label="创建时间">{{ formatDateTime(detail.creation_date) }}</el-descriptions-item>
				<el-descriptions-item label="标签" :span="2">
					<el-tag v-for="tag in detail.tags" :key="tag" style="margin-right: 5px">{{ tag }}</el-tag>
					<span v-if="!detail.tags || detail.tags.length === 0">-</span>
				</el-descriptions-item>
				<el-descriptions-item label="用例描述" :span="2">
					<div style="white-space: pre-wrap">{{ detail.description || '-' }}</div>
				</el-descriptions-item>
				<el-descriptions-item label="前置条件" :span="2">
					<div style="white-space: pre-wrap">{{ detail.preconditions || '-' }}</div>
				</el-descriptions-item>
				<el-descriptions-item label="预期结果" :span="2">
					<div style="white-space: pre-wrap">{{ detail.expected_result || '-' }}</div>
				</el-descriptions-item>
			</el-descriptions>

			<el-divider content-position="left">测试步骤</el-divider>

			<el-table :data="detail.steps" border style="width: 100%">
				<el-table-column label="步骤" width="80" align="center">
					<template #default="{ row }">
						{{ row.step_number }}
					</template>
				</el-table-column>
				<el-table-column label="操作" prop="action" min-width="200" />
				<el-table-column label="预期结果" prop="expected" min-width="200" />
			</el-table>

			<el-empty v-if="!detail.steps || detail.steps.length === 0" description="暂无测试步骤" :image-size="100" />
		</div>

		<template #footer>
			<el-button @click="handleClose">关闭</el-button>
		</template>
	</el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { getTestCaseDetail } from '/@/api/v1/testing/testcases';

const props = defineProps({
	modelValue: {
		type: Boolean,
		default: false,
	},
	testcaseId: {
		type: Number,
		required: true,
	},
});

const emit = defineEmits(['update:modelValue']);

const loading = ref(false);
const detail = ref<any>({});

// 获取详情
const getDetail = async () => {
	loading.value = true;
	try {
		const res = await getTestCaseDetail(props.testcaseId);
		if (res.code === 200) {
			detail.value = res.data;
		}
	} catch (error) {
		console.error('获取详情失败:', error);
		ElMessage.error('获取详情失败');
	} finally {
		loading.value = false;
	}
};

// 获取测试类型标签
const getTestTypeLabel = (type: string) => {
	const typeMap: Record<string, string> = {
		functional: '功能测试',
		integration: '集成测试',
		api: 'API测试',
		ui: 'UI测试',
		performance: '性能测试',
		security: '安全测试',
	};
	return typeMap[type] || type;
};

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
	if (!dateTime) return '-';
	const date = new Date(dateTime);
	const year = date.getFullYear();
	const month = String(date.getMonth() + 1).padStart(2, '0');
	const day = String(date.getDate()).padStart(2, '0');
	const hours = String(date.getHours()).padStart(2, '0');
	const minutes = String(date.getMinutes()).padStart(2, '0');
	const seconds = String(date.getSeconds()).padStart(2, '0');
	return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

// 关闭
const handleClose = () => {
	emit('update:modelValue', false);
};

// 监听对话框打开
watch(
	() => props.modelValue,
	(val) => {
		if (val) {
			getDetail();
		}
	},
	{ immediate: true }  // 立即执行
);
</script>
