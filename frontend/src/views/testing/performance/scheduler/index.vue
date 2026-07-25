<template>
	<div class="perf-scheduler-container">
		<el-card shadow="hover">
			<div class="page-content-layout">
			<!-- 工具栏 -->
			<div class="toolbar">
				<div class="toolbar-left">
					<el-input
						v-model="query.name"
						placeholder="搜索任务名称"
						clearable
						style="width: 280px"
						@keyup.enter="handleQuery"
						@clear="handleQuery"
					>
						<template #prefix><el-icon><ele-Search /></el-icon></template>
					</el-input>
					<el-select v-model="query.task_status" placeholder="任务状态" clearable style="width: 130px" @change="handleQuery">
						<el-option v-for="item in taskStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
					</el-select>
					<el-select v-model="query.is_active" placeholder="启用状态" clearable style="width: 120px" @change="handleQuery">
						<el-option label="启用" :value="1" />
						<el-option label="禁用" :value="0" />
					</el-select>
					<el-button type="primary" @click="handleQuery">
						<el-icon><ele-Search /></el-icon>查询
					</el-button>
					<el-button @click="resetQuery">
						<el-icon><ele-RefreshRight /></el-icon>重置
					</el-button>
				</div>
				<div class="toolbar-right">
					<el-button type="primary" @click="openCreateDialog">
						<el-icon><ele-Plus /></el-icon>新建定时任务
					</el-button>
					<el-button :loading="statusRefreshing" @click="handleRefreshStatus">
						<el-icon><ele-Refresh /></el-icon>刷新
					</el-button>
				</div>
			</div>

			<!-- 列表 -->
			<div ref="tableWrapRef" class="table-wrap">
			<el-table v-loading="loading" :data="taskList" border stripe style="width: 100%" :height="tableHeight">
				<el-table-column prop="id" label="任务ID" width="90" align="center" />
				<el-table-column prop="name" label="任务名称" min-width="150" show-overflow-tooltip />
				<el-table-column label="场景编号" width="140" align="center">
					<template #default="{ row }">
						<el-tooltip content="点击跳转压测场景列表" placement="top" :show-after="300">
							<span class="scene-no-link" @click="handleGotoScene(row)">{{ row.scenario_code || '-' }}</span>
						</el-tooltip>
					</template>
				</el-table-column>
				<el-table-column prop="script_name" label="场景脚本" min-width="150" show-overflow-tooltip />
				<el-table-column label="启用状态" width="100" align="center">
					<template #default="{ row }">
						<el-switch
							v-model="row.is_active"
							:active-value="1"
							:inactive-value="0"
							:disabled="row.task_status === 1 || row.task_status === 2"
							@change="handleActiveChange(row)"
						/>
					</template>
				</el-table-column>
				<el-table-column label="任务状态" width="110" align="center">
					<template #default="{ row }">
						<el-tag :type="getStatusType(row.task_status)" size="small" :effect="row.task_status === 1 ? 'dark' : 'light'">
							{{ getStatusLabel(row.task_status) }}
						</el-tag>
					</template>
				</el-table-column>
        <el-table-column label="创建时间" width="175" align="center">
					<template #default="{ row }"><span style="white-space:nowrap">{{ formatDt(row.creation_date) }}</span></template>
				</el-table-column>
				<el-table-column label="计划执行时间" width="175" align="center">
					<template #default="{ row }"><span style="white-space:nowrap">{{ formatDt(row.plan_time) }}</span></template>
				</el-table-column>
				<el-table-column label="结束时间" width="175" align="center">
					<template #default="{ row }"><span style="white-space:nowrap">{{ formatDt(row.end_time) }}</span></template>
				</el-table-column>
				<el-table-column prop="operator_name" label="创建人" width="100" align="center" show-overflow-tooltip />
				<el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip>
				<template #default="{ row }">
						<span :style="row.task_status === 4 ? 'color:var(--el-color-danger)' : ''">{{ row.remark || '-' }}</span>
					</template>
				</el-table-column>
				<el-table-column label="操作" width="160" fixed="right" align="center" class-name="operation-col">
					<template #default="{ row }">
						<div class="action-btns">
							<!-- 进行中：仅取消 -->
							<template v-if="row.task_status === 1">
								<el-button type="warning" size="small" text style="font-weight:600" @click="handleCancel(row)">
									<el-icon><ele-CircleClose /></el-icon>取消
								</el-button>
							</template>
							<!-- 待触发(0) / 已取消(3) / 失败(4)：编辑 + 删除 -->
							<template v-else-if="row.task_status === 0 || row.task_status === 3 || row.task_status === 4">
								<el-button type="primary" size="small" text style="font-weight:600" @click="openEditDialog(row)">
									<el-icon><ele-Edit /></el-icon>编辑
								</el-button>
								<el-button type="danger" size="small" text style="font-weight:600" @click="handleDelete(row)">
									<el-icon><ele-Delete /></el-icon>删除
								</el-button>
							</template>
							<!-- 已结束(2)：结果报告 -->
							<template v-else-if="row.task_status === 2">
								<el-button type="success" size="small" text style="font-weight:600" @click="handleViewReport(row)">
									<el-icon><ele-DataLine /></el-icon>结果报告
								</el-button>
							</template>
						</div>
					</template>
				</el-table-column>
			</el-table>
			</div><!-- /table-wrap -->

			<!-- 分页 -->
			<div class="pagination">
				<el-pagination
					v-model:current-page="query.page"
					v-model:page-size="query.page_size"
					:page-sizes="[10, 20, 50]"
					:total="total"
					layout="total, sizes, prev, pager, next, jumper"
					@size-change="handleQuery"
					@current-change="handleQuery"
				/>
			</div>
			</div><!-- /page-content-layout -->
		</el-card>

		<!-- 新建 / 编辑 抽屉 -->
		<el-drawer
			v-model="dialogVisible"
			:title="dialogMode === 'create' ? '新建定时任务' : '编辑定时任务'"
			direction="rtl"
			:size="drawerSize"
			:append-to-body="true"
			class="perf-scheduler-drawer"
			destroy-on-close
			@close="resetForm"
		>
			<el-form
				ref="formRef"
				:model="form"
				:rules="rules"
				label-width="120px"
				size="default"
				hide-required-asterisk
				class="scheduler-form"
			>
				<el-form-item prop="scenario_id">
					<template #label>
						<span class="label-txt"><span class="label-star">*</span>关联压测场景</span>
					</template>
					<el-select
						v-model="form.scenario_id"
						placeholder="请选择压测场景（排除待联调、运行中、耗时未知）"
						clearable
						style="width: 100%"
						filterable
						:loading="scenarioLoading"
						@change="handleSceneChange"
					>
						<el-option
							v-for="s in availableScenes"
							:key="s.id"
							:label="`${s.code}：${s.script_name}`"
							:value="s.id"
						/>
					</el-select>
				</el-form-item>

				<el-form-item prop="name">
					<template #label>
						<span class="label-txt"><span class="label-star">*</span>任务名称</span>
					</template>
					<el-input v-model="form.name" placeholder="请输入任务名称，最多100个字符" maxlength="100" show-word-limit clearable />
				</el-form-item>

				<el-form-item>
					<template #label>
						<span class="label-txt">启用状态</span>
					</template>
					<el-switch
						v-model="form.is_active"
						:active-value="1"
						:inactive-value="0"
						inline-prompt
						active-text="启用"
						inactive-text="禁用"
					/>
					<span class="form-hint">禁用后即使到达计划时间也不会触发执行</span>
				</el-form-item>

				<el-form-item prop="plan_time">
					<template #label>
						<span class="label-txt"><span class="label-star">*</span>计划执行时间</span>
					</template>
					<!--
						teleported=true：面板挂载到 body，不受抽屉 overflow 裁剪；
						placement="bottom-start"：优先向下展开，空间不足时 Popper 自动 flip 向上。
					-->
					<el-date-picker
						v-model="form.plan_time"
						type="datetime"
						placeholder="请选择计划执行时间"
						format="YYYY-MM-DD HH:mm:ss"
						value-format="YYYY-MM-DDTHH:mm:ss"
						placement="bottom-start"
						:teleported="true"
						:disabled-date="disabledDate"
						:disabled-hours="disabledHours"
						:disabled-minutes="disabledMinutes"
						:disabled-seconds="disabledSeconds"
						popper-class="scheduler-dt-popper"
						style="width: 100%"
					/>
				</el-form-item>

				<el-form-item>
					<template #label>
						<span class="label-txt">备注</span>
					</template>
					<el-input
						v-model="form.remark"
						type="textarea"
						:rows="3"
						placeholder="选填，最多500个字符"
						maxlength="500"
						show-word-limit
					/>
				</el-form-item>
			</el-form>
			<template #footer>
				<el-button size="default" @click="dialogVisible = false">取 消</el-button>
				<el-button size="default" type="primary" :loading="submitLoading" @click="handleSubmit">确 定</el-button>
			</template>
		</el-drawer>
	</div>
</template>

<script setup lang="ts" name="PerformanceScheduler">
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus';
import { usePerformanceApi } from '/@/api/v1/testing/performance';
import { useDictCache } from '/@/utils/dictCache';
import { usePerfSchedulerWatcher } from '/@/stores/perfSchedulerWatcher';

const router = useRouter();
const perfApi = usePerformanceApi();
const { getDictOptions } = useDictCache();
const schedWatcher = usePerfSchedulerWatcher();

// 表格包裹层 ref，ResizeObserver 动态更新 height
const tableWrapRef = ref<HTMLElement | null>(null);
const tableHeight = ref(500);

// 检测系统滚动条高度（Windows ~17px，Mac overlay 为 0），修正横向滚动条遮挡末行问题
const SCROLLBAR_SIZE: number = (() => {
	const div = document.createElement('div');
	div.style.cssText = 'width:100px;height:100px;overflow:scroll;position:absolute;top:-9999px;visibility:hidden';
	document.body.appendChild(div);
	const size = div.offsetHeight - div.clientHeight;
	document.body.removeChild(div);
	return size;
})();

let _resizeObserver: ResizeObserver | null = null;
// 更新表格高度：取包裹层高度并扣除横向滚动条占用
const updateTableHeight = () => {
	if (tableWrapRef.value) {
		tableHeight.value = tableWrapRef.value.clientHeight - SCROLLBAR_SIZE;
	}
};

// ======================== 常量映射 ========================
const taskStatusOptions = ref<{ label: string; value: number; tagType: string }[]>([]);

const getStatusLabel = (s: number) => taskStatusOptions.value.find(o => o.value === s)?.label ?? String(s);

const getStatusType = (s: number): '' | 'success' | 'warning' | 'danger' | 'info' => {
	const map: Record<number, '' | 'success' | 'warning' | 'danger' | 'info'> = {
		0: 'warning',  // 待触发（浅黄）
		1: '',         // 进行中（primary 蓝）
		2: 'success',  // 已结束（绿）
		3: 'info',     // 已取消（灰）
		4: 'danger',   // 失败（红）
	};
	return map[s] ?? 'info';
};

const formatDt = (val: string | null) => {
	if (!val) return '-';
	return val.replace('T', ' ').substring(0, 19);
};

// 禁用今天之前的日期
const disabledDate = (t: Date) => {
	const today = new Date(); today.setHours(0, 0, 0, 0);
	return t.getTime() < today.getTime();
};

// 当前选中日期是否是今天（用于时/分/秒限制）
const _isSelectedToday = () => {
	if (!form.plan_time) return true;
	const s = new Date(form.plan_time.replace('T', ' '));
	const n = new Date();
	return s.getFullYear() === n.getFullYear() && s.getMonth() === n.getMonth() && s.getDate() === n.getDate();
};

const disabledHours = () => {
	if (!_isSelectedToday()) return [];
	const h = new Date().getHours();
	return Array.from({ length: h }, (_, i) => i);
};

const disabledMinutes = (hour: number) => {
	if (!_isSelectedToday()) return [];
	const n = new Date();
	if (hour > n.getHours()) return [];
	if (hour < n.getHours()) return Array.from({ length: 60 }, (_, i) => i);
	return Array.from({ length: n.getMinutes() }, (_, i) => i);
};

const disabledSeconds = (hour: number, minute: number) => {
	if (!_isSelectedToday()) return [];
	const n = new Date();
	if (hour > n.getHours()) return [];
	if (hour < n.getHours()) return Array.from({ length: 60 }, (_, i) => i);
	if (minute > n.getMinutes()) return [];
	if (minute < n.getMinutes()) return Array.from({ length: 60 }, (_, i) => i);
	return Array.from({ length: n.getSeconds() + 1 }, (_, i) => i);
};

// ======================== 列表 ========================
const loading = ref(false);
const statusRefreshing = ref(false);
const taskList = ref<any[]>([]);
const total = ref(0);

const query = reactive({
	name: '',
	task_status: undefined as number | undefined,
	is_active: undefined as number | undefined,
	page: 1,
	page_size: 20,
});

const handleQuery = async () => {
	loading.value = true;
	try {
		const params: any = { page: query.page, page_size: query.page_size };
		if (query.name) params.name = query.name;
		if (query.task_status !== undefined) params.task_status = query.task_status;
		if (query.is_active !== undefined) params.is_active = query.is_active;
		const res = await perfApi.getSchedulerList(params);
		taskList.value = res.data?.items ?? [];
		total.value = res.data?.total ?? 0;
		schedWatcher.updateTasks(taskList.value);
		_schedulePlanTimeouts();
		_startRunningPollIfNeeded();
	} catch (e) {
		ElMessage.error('获取定时任务列表失败');
	} finally {
		loading.value = false;
	}
};

const resetQuery = () => {
	query.name = '';
	query.task_status = undefined;
	query.is_active = undefined;
	query.page = 1;
	handleQuery();
};

// 刷新：重新加载列表即可，无需单独接口
const handleRefreshStatus = async () => {
	statusRefreshing.value = true;
	await handleQuery();
	statusRefreshing.value = false;
	ElMessage.success('任务状态已刷新');
};

// ======================== 精准状态更新（无轮询）========================
// 策略：
//   0→1（待触发→进行中）：在每条待触发任务的 plan_time 精准设 setTimeout，到点后单次刷新
//   1→2/4（进行中→已结束/失败）：进行中时启动轮询（最长10分钟），任务离开进行中后自动停止
//   1→2（场景正常结束）：场景页检测到压测结束后，通过 store.notifySchedulerRefresh 触发刷新
const _planTimeouts: ReturnType<typeof setTimeout>[] = [];
let _runningPollTimer: ReturnType<typeof setInterval> | null = null;

function _clearPlanTimeouts() {
	_planTimeouts.forEach(t => clearTimeout(t));
	_planTimeouts.length = 0;
}

function _stopRunningPoll() {
	if (_runningPollTimer) { clearInterval(_runningPollTimer); _runningPollTimer = null; }
}

// 有任务处于进行中(1)时，每8秒轮询一次，直到全部离开进行中或超时10分钟
function _startRunningPollIfNeeded() {
	if (_runningPollTimer) return;
	if (!taskList.value.some((t: any) => t.task_status === 1)) return;
	const deadline = Date.now() + 10 * 60 * 1000;
	_runningPollTimer = setInterval(async () => {
		await handleQuery();
		if (!taskList.value.some((t: any) => t.task_status === 1) || Date.now() > deadline) {
			_stopRunningPoll();
		}
	}, 8000);
}

// 对当前列表中所有待触发+已启用的任务，分别在 plan_time 时刻安排一次刷新
function _schedulePlanTimeouts() {
	_clearPlanTimeouts();
	const now = Date.now();
	for (const task of taskList.value) {
		if (task.task_status !== 0 || !task.is_active || !task.plan_time) continue;
		const planMs = new Date(task.plan_time).getTime();
		// +3s 给后端 APScheduler 处理留缓冲
		const delay = Math.max(0, planMs - now + 3000);
		_planTimeouts.push(setTimeout(async () => {
			await handleQuery();
			_startRunningPollIfNeeded();
		}, delay));
	}
}

// 场景页压测结束后通知此页刷新（进行中→已结束/取消/失败）
watch(() => schedWatcher.pendingRefresh, (val) => {
	if (val) {
		handleQuery();
		schedWatcher.pendingRefresh = false;
	}
});

onUnmounted(() => { _clearPlanTimeouts(); _stopRunningPoll(); _resizeObserver?.disconnect(); });

// ======================== 启用状态切换 ========================
const handleActiveChange = async (row: any) => {
	// 开启时校验：计划时间不能早于当前时间
	if (row.is_active === 1 && row.plan_time && new Date(row.plan_time).getTime() <= Date.now()) {
		row.is_active = 0;
		ElMessage.warning('计划开始时间已过期，请修改后再启用');
		return;
	}
	try {
		await perfApi.updateScheduler({ id: row.id, is_active: row.is_active });
		ElMessage.success(row.is_active ? `「${row.name}」已启用` : `「${row.name}」已禁用`);
		await handleQuery();
	} catch (e) {
		// 回滚开关
		row.is_active = row.is_active === 1 ? 0 : 1;
		ElMessage.error('操作失败，请重试');
	}
};

// ======================== 取消任务 ========================
const handleCancel = (row: any) => {
	ElMessageBox.confirm(
		`确认取消定时任务「${row.name}」？取消后任务状态将变为已取消。`,
		'取消定时任务',
		{ type: 'warning', confirmButtonText: '确认取消', cancelButtonText: '返回', confirmButtonClass: 'el-button--danger' }
	).then(async () => {
		try {
			await perfApi.cancelScheduler({ id: row.id });
			ElMessage.success('定时任务已取消');
			handleQuery();
		} catch (e: any) {
			ElMessage.error(e?.response?.data?.detail ?? '取消失败');
		}
	}).catch(() => {});
};

// ======================== 删除 ========================
const handleDelete = (row: any) => {
	ElMessageBox.confirm(
		`确认删除定时任务「${row.name}」？`,
		'删除确认',
		{ type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消', confirmButtonClass: 'el-button--danger' }
	).then(async () => {
		try {
			await perfApi.deleteScheduler(row.id);
			ElMessage.success('删除成功');
			handleQuery();
		} catch (e: any) {
			ElMessage.error(e?.response?.data?.detail ?? '删除失败');
		}
	}).catch(() => {});
};

// ======================== 结果报告 ========================
const handleViewReport = (row: any) => {
	router.push({ path: '/performance/report', query: { scenario_id: row.scenario_id } });
};

// ======================== 跳转压测场景 ========================
const handleGotoScene = (row: any) => {
	router.push({ path: '/performance/scenario', query: { scene_no: row.scenario_code } });
};

// ======================== 场景下拉数据 ========================
const scenarioLoading = ref(false);
const availableScenes = ref<any[]>([]);

const loadSceneOptions = async () => {
	scenarioLoading.value = true;
	try {
		// 过滤规则：排除待联调(0)、运行中(2)、循环次数耗时未知的场景
		const res = await perfApi.getScenarioList({ page: 1, page_size: 100 });
		availableScenes.value = (res.data?.items ?? []).filter((s: any) =>
			s.status !== 0 && s.status !== 2 && !s.has_unknown_times
		);
	} catch (e) {
		ElMessage.error('加载场景列表失败');
	} finally {
		scenarioLoading.value = false;
	}
};

// 选中场景后自动填充任务名称（格式：定时任务-场景名称），仅新建时且名称未手动输入时生效
const handleSceneChange = (sceneId: number) => {
	if (dialogMode.value !== 'create') return;
	const scene = availableScenes.value.find((s: any) => s.id === sceneId);
	if (scene) {
		form.name = `定时任务-${scene.name}`;
	}
};

// ======================== 新建 / 编辑 弹窗 ========================
const drawerSize = computed(() => Math.max(420, Math.floor(window.innerWidth / 3)) + 'px');
const dialogVisible = ref(false);
const dialogMode = ref<'create' | 'edit'>('create');
const submitLoading = ref(false);
const formRef = ref<FormInstance>();
const editId = ref<number | null>(null);

const defaultForm = () => ({
	name: '',
	scenario_id: undefined as number | undefined,
	is_active: 1,
	plan_time: '',
	remark: '',
});

const form = reactive(defaultForm());

const rules = {
	name: [
		{ required: true, message: '请输入任务名称', trigger: 'blur' },
		{ max: 100, message: '任务名称不能超过 100 个字符', trigger: 'blur' },
	],
	scenario_id: [{ required: true, message: '请选择关联压测场景', trigger: 'change' }],
	plan_time:   [{ required: true, message: '请选择计划执行时间', trigger: 'change' }],
};

const openCreateDialog = async () => {
	dialogMode.value = 'create';
	editId.value = null;
	Object.assign(form, defaultForm());
	dialogVisible.value = true;
	await loadSceneOptions();
};

const openEditDialog = async (row: any) => {
	dialogMode.value = 'edit';
	editId.value = row.id;
	form.name        = row.name;
	form.scenario_id = row.scenario_id;
	form.is_active   = row.is_active;
	form.plan_time   = row.plan_time;
	// 系统自动写入的失败原因不回填到备注输入框，避免用户保存时重复写入
	const sysPrefix = '[自动触发失败]';
	form.remark = (row.remark && row.remark.startsWith(sysPrefix)) ? '' : (row.remark ?? '');
	dialogVisible.value = true;
	await loadSceneOptions();
};

const resetForm = () => {
	formRef.value?.resetFields();
	Object.assign(form, defaultForm());
	editId.value = null;
};

const handleSubmit = () => {
	formRef.value?.validate(async (valid: boolean) => {
		if (!valid) return;
		submitLoading.value = true;
		try {
			if (dialogMode.value === 'create') {
				await perfApi.addScheduler({
					name:        form.name,
					scenario_id: form.scenario_id,
					is_active:   form.is_active,
					plan_time:   form.plan_time,
					remark:      form.remark || undefined,
				});
				ElMessage.success('定时任务创建成功');
			} else {
				await perfApi.updateScheduler({
					id:          editId.value,
					name:        form.name,
					scenario_id: form.scenario_id,
					is_active:   form.is_active,
					plan_time:   form.plan_time,
					remark:      form.remark || undefined,
				});
				ElMessage.success('定时任务更新成功');
			}
			dialogVisible.value = false;
			handleQuery();
		} catch (e: any) {
			ElMessage.error(e?.response?.data?.detail ?? '操作失败，请重试');
		} finally {
			submitLoading.value = false;
		}
	});
};

// ======================== 初始化 ========================
onMounted(async () => {
	const statusOpts = await getDictOptions('perf_scheduler_status').catch(() => []);
	taskStatusOptions.value = (statusOpts as any[]).map(o => ({
		label: o.label,
		value: Number(o.value),
		tagType: o.raw?.list_class ?? '',
	}));
	handleQuery();
	// 初始化高度，并注册 ResizeObserver 响应容器尺寸变化
	updateTableHeight();
	if (tableWrapRef.value) {
		_resizeObserver = new ResizeObserver(updateTableHeight);
		_resizeObserver.observe(tableWrapRef.value);
	}
});
</script>

<style scoped lang="scss">
.perf-scheduler-container {
	height: 100%;
	box-sizing: border-box;
	padding: 10px 10px 20px 10px;
	display: flex;
	flex-direction: column;
	overflow: hidden;

	:deep(.el-card) {
		flex: 1;
		min-height: 0;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	:deep(.el-card__body) {
		flex: 1;
		min-height: 0;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		padding: 10px 10px 20px 10px;
	}

	// 内容布局容器：工具栏 + 表格包裹 + 分页 纵向排列
	.page-content-layout {
		height: 100%;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	// 表格包裹层：吸收剩余高度，el-table 的 max-height 由此计算
	.table-wrap {
		flex: 1;
		min-height: 0;
		overflow: hidden;
	}

	:deep(.el-button > span) {
		display: inline-flex !important;
		align-items: center !important;
		line-height: 1 !important;
	}

	.toolbar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16px;

		.toolbar-left {
			display: flex;
			align-items: center;
			gap: 10px;
			flex-wrap: wrap;
		}

		.toolbar-right {
			display: flex;
			align-items: center;
			gap: 10px;
		}
	}

	.scene-no-link {
		color: var(--el-color-primary);
		cursor: pointer;
		font-size: 13.5px;

		&:hover {
			text-decoration: underline;
		}
	}

	:deep(.el-tag) {
		font-size: 13px;
		padding: 0 8px;
	}

	:deep(.el-table) {
		font-size: 13.5px;

		.el-table__header th {
			font-size: 13.5px;
			background-color: var(--el-fill-color-light);

			.cell {
				display: inline-flex;
				align-items: center;
				justify-content: center;
				white-space: nowrap;
			}
		}

		.el-table__cell {
			padding: 11px 0;
		}

		td.operation-col {
			background-color: var(--el-fill-color-light) !important;
		}
	}

	.action-btns {
		display: flex;
		align-items: center;
		justify-content: center;
		flex-wrap: nowrap;

		:deep(.el-button) {
			padding: 0 6px;
			font-weight: 600;

			.el-icon {
				margin-right: 2px;
			}
		}
	}

	.pagination {
		margin-top: 16px;
		display: flex;
		justify-content: flex-end;
	}

}

// ---- 抽屉表单 ----
.scheduler-form {
	padding: 24px 20px 0;

	:deep(.el-form-item__label) {
		display: flex !important;
		align-items: center;
		padding-right: 8px !important;
		font-size: 13.5px;

		.label-txt {
			flex: 1;
			text-align: right;

			.label-star {
				color: var(--el-color-danger);
				margin-right: 2px;
			}
		}

	}

	:deep(.el-form-item) {
		margin-bottom: 14px;
	}

	:deep(.el-input__inner),
	:deep(.el-textarea__inner) {
		font-size: 13.5px;
	}

	:deep(.el-select__selected-item),
	:deep(.el-select__input) {
		font-size: 13.5px;
	}

	:deep(.el-input__inner::placeholder),
	:deep(.el-textarea__inner::placeholder) {
		font-size: 13.5px;
	}

	:deep(.el-select__placeholder) {
		font-size: 13.5px;
	}

	:deep(.el-divider) {
		margin-top: 36px;
		margin-bottom: 36px;
	}

	:deep(.el-switch__label) {
		color: var(--el-color-white);
	}

	.form-hint {
		margin-left: 10px;
		font-size: 13.5px;
		color: var(--el-text-color-placeholder);
		line-height: 1;
	}
}
</style>

<style lang="scss">
.perf-scheduler-container .el-button > span {
	display: inline-flex !important;
	align-items: center !important;
	line-height: 1 !important;
}

// 抽屉底部按钮区域（drawer 传送至 body，需非 scoped 规则）
.el-drawer.perf-scheduler-drawer .el-drawer__footer {
	padding: 16px 24px;
	border-top: 1px solid var(--el-border-color-lighter);
	display: flex;
	justify-content: flex-end;
	gap: 12px;
}

// 修复 datetime picker 时间列滚轮回弹问题：
// 时间列（小时/分钟/秒）的滚轮事件会冒泡到 body，触发 Popper 重定位导致列重置；
// overscroll-behavior: contain 阻止冒泡，使滚轮事件在 spinner 内自我消化。
.scheduler-dt-popper {
	.el-time-spinner__list {
		overscroll-behavior: contain;
	}
}
</style>