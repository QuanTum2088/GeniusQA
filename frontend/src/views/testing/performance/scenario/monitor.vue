<template>
	<div class="scene-monitor">

		<!-- 压测进度条 -->
		<div class="monitor-progress-section">
			<div v-if="scene" class="monitor-progress-header">
				<span class="monitor-scene-name">{{ currentScene.name }}</span>
				<el-tag
					:type="statusTagType(currentScene.status)"
					size="small"
					:effect="currentScene.status === 'running' ? 'dark' : 'light'"
					style="margin-left: 10px; flex-shrink: 0"
				>{{ statusLabel(currentScene.status) }}</el-tag>
				<el-button
					type="danger"
					size="small"
					plain
					style="margin-left:auto; flex-shrink: 0"
					:disabled="currentScene.status !== 'running'"
					@click="handleForceStop"
				>
					<el-icon><ele-VideoPause /></el-icon>强制停止
				</el-button>
			</div>

			<!-- 进度轨道行（flex，bar + suffix 始终同行对齐） -->
			<div class="monitor-progress-bar-row">
				<!-- 联调/启动阶段进度条 -->
				<template v-if="execState">
					<div class="stage-bar-area">
						<div class="stage-track">
							<div class="stage-fill" :style="{ width: execState.progress + '%' }"></div>
						</div>
					<!-- 阶段标签与分割线同处一个 flex 流，分割线落在文字实际边界上，不再用固定百分比定位 -->
						<div class="stage-bar-seg-labels">
							<!-- 阶段标签与分割线同处一个 flex 流，分割线落在文字实际边界上，不再用固定百分比定位 -->
						<span v-for="(s, i) in execState.stages" :key="i" style="display:contents">
								<span
									class="stage-seg-label"
									:class="{ 'seg-done': s.done, 'seg-active': s.active, 'seg-wait': !s.done && !s.active }"
								>{{ s.label }}</span>
								<el-tooltip
									v-if="i < execState.stages.length - 1"
									:content="s.label"
									placement="top"
									:show-after="0"
									:teleported="true"
								>
									<div class="stage-pin" :class="{ 'pin-done': s.done, 'pin-active': s.active }"></div>
								</el-tooltip>
							</span>
						</div>
					</div>
					<span class="monitor-progress-suffix">
						<template v-if="execState.progress >= 100">
							<el-icon :size="20" style="color:#67c23a;font-weight:700"><ele-CircleCheck /></el-icon>
						</template>
						<template v-else>
							<span style="color:#409eff;font-weight:700;font-size:15px">{{ execState.progress }}%</span>
						</template>
					</span>
				</template>

				<!-- 正式压测进度条 -->
				<template v-else>
					<el-progress
						:percentage="currentScene.progress ?? 0"
						:color="progressColor(currentScene.status)"
						:stroke-width="14"
						:show-text="false"
						class="monitor-progress-bar"
					/>
					<span class="monitor-progress-suffix">
						<template v-if="currentScene.status === 'running'">
							<span style="color:#409eff;font-weight:700;font-size:15px">{{ currentScene.progress }}%</span>
						</template>
						<template v-else-if="currentScene.status === 'completed'">
							<el-icon :size="20" style="color:#67c23a;font-weight:700"><ele-CircleCheck /></el-icon>
						</template>
						<template v-else-if="currentScene.status === 'failed' || currentScene.status === 'cancelled'">
							<span style="color:#f56c6c;font-weight:700;font-size:15px">{{ currentScene.progress ?? 0 }}%</span>
						</template>
						<template v-else>
							<span style="color:#909399;font-weight:700;font-size:15px">{{ currentScene.progress ?? 0 }}%</span>
						</template>
					</span>
				</template>
			</div>
		</div>

		<!-- 控制台 + 指标看板 -->
		<div class="monitor-body">
			<!-- 左侧：控制台输出 60% -->
			<div class="monitor-console-wrap">
				<PerfConsole
					:logs="consoleLogs"
					title="压测执行日志（实时）"
					empty-text="暂无输出，启动压测后将在此显示实时日志..."
				>
					<template #actions>
						<el-button size="small" @click="consoleLogs = []">
							<el-icon><ele-Delete /></el-icon>清空
						</el-button>
					</template>
				</PerfConsole>
			</div>

			<!-- 右侧：实时指标看板 40% -->
			<div class="monitor-metrics-wrap" :class="{ 'metrics-dark': monitorDark }">
				<div class="metrics-header">
					<span><el-icon><ele-DataLine /></el-icon>实时监控指标</span>
					<el-tooltip :content="monitorDark ? '切换亮色' : '切换深色'" placement="top" :show-after="300">
						<el-button class="theme-toggle-btn" size="small" text circle @click="monitorDark = !monitorDark">
							<el-icon>
								<ele-Sunny v-if="monitorDark" />
								<ele-Moon v-else />
							</el-icon>
						</el-button>
					</el-tooltip>
				</div>
				<draggable
					class="metrics-charts-list"
					v-model="monitorMetrics"
					item-key="title"
					handle=".panel-title-handle"
					:animation="180"
					ghost-class="metric-drag-ghost"
					chosen-class="metric-drag-chosen"
				>
					<template #item="{ element: m }">
						<MetricChart
							:title="m.title"
							:unit="m.unit"
							:series="m.series"
							:time-labels="monitorTimeLabels"
							:dark-mode="monitorDark"
							:chart-height="220"
							:area="m.area"
							@expand="handleChartExpand"
						/>
					</template>
				</draggable>
			</div>
		</div>

		<!-- Top 5 错误统计 -->
		<div class="monitor-errors-wrap" :class="{ 'errors-dark': monitorDark }">
			<div class="errors-header">
				<span class="errors-header-title">Top 5 Errors by Sampler（实时）</span>
				<el-tooltip content="放大查看" placement="top" :show-after="400">
					<el-button class="errors-expand-btn" size="small" text circle @click="openErrorsExpand">
						<el-icon><ele-FullScreen /></el-icon>
					</el-button>
				</el-tooltip>
			</div>
			<div class="errors-table-scroll">
				<el-table ref="errorsSmallTableRef" :data="top5Errors" size="small" class="errors-table" border :show-header="true" empty-text="No data">
					<el-table-column label="Sample（接口）" prop="sampler" min-width="200" header-align="center">
						<template #default="{ row }">
							<span class="sampler-name">{{ row.sampler }}</span>
						</template>
					</el-table-column>
					<el-table-column label="#Samples" prop="samples" width="80" align="center" header-align="center" />
					<el-table-column label="#Errors" prop="errors" width="70" align="center" header-align="center">
						<template #default="{ row }">
							<span class="total-errors">{{ row.errors }}</span>
						</template>
					</el-table-column>
					<el-table-column label="Error 1" min-width="160" header-align="center">
						<template #default="{ row }">
							<span v-if="row.top[0]" class="error-msg">{{ row.top[0].error }}</span>
						</template>
					</el-table-column>
					<el-table-column label="Count" width="60" align="center" header-align="center">
						<template #default="{ row }">
							<span v-if="row.top[0]" class="error-count">{{ row.top[0].count }}</span>
						</template>
					</el-table-column>
					<el-table-column label="Error 2" min-width="160" header-align="center">
						<template #default="{ row }">
							<span v-if="row.top[1]" class="error-msg">{{ row.top[1].error }}</span>
						</template>
					</el-table-column>
					<el-table-column label="Count" width="60" align="center" header-align="center">
						<template #default="{ row }">
							<span v-if="row.top[1]" class="error-count">{{ row.top[1].count }}</span>
						</template>
					</el-table-column>
					<el-table-column label="Error 3" min-width="160" header-align="center">
						<template #default="{ row }">
							<span v-if="row.top[2]" class="error-msg">{{ row.top[2].error }}</span>
						</template>
					</el-table-column>
					<el-table-column label="Count" width="60" align="center" header-align="center">
						<template #default="{ row }">
							<span v-if="row.top[2]" class="error-count">{{ row.top[2].count }}</span>
						</template>
					</el-table-column>
					<el-table-column label="Error 4" min-width="160" header-align="center">
						<template #default="{ row }">
							<span v-if="row.top[3]" class="error-msg">{{ row.top[3].error }}</span>
						</template>
					</el-table-column>
					<el-table-column label="Count" width="60" align="center" header-align="center">
						<template #default="{ row }">
							<span v-if="row.top[3]" class="error-count">{{ row.top[3].count }}</span>
						</template>
					</el-table-column>
					<el-table-column label="Error 5" min-width="160" header-align="center">
						<template #default="{ row }">
							<span v-if="row.top[4]" class="error-msg">{{ row.top[4].error }}</span>
						</template>
					</el-table-column>
					<el-table-column label="Count" width="60" align="center" header-align="center">
						<template #default="{ row }">
							<span v-if="row.top[4]" class="error-count">{{ row.top[4].count }}</span>
						</template>
					</el-table-column>
				</el-table>
			</div>
		</div>

		<!-- 放大图表 Dialog -->
		<el-dialog
			v-model="expandVisible"
			width="75%"
			destroy-on-close
			class="expand-chart-dialog"
		>
			<MetricChart
				v-if="expandConfig"
				:title="expandConfig!.title"
				:unit="expandConfig!.unit"
				:series="expandConfig!.series"
				:time-labels="expandConfig!.timeLabels"
				:dark-mode="monitorDark"
				:expandable="false"
				:chart-height="480"
				:area="expandConfig!.area"
			/>
		</el-dialog>

		<!-- Top5 Errors 放大抽屉（从底部滑出） -->
		<el-drawer
			v-model="errorsExpandVisible"
			direction="btt"
			:size="errorsDrawerSizePx"
			destroy-on-close
			class="errors-expand-drawer"
			:class="{ 'errors-expand-dark': monitorDark }"
		>
			<template #header>
				<span class="errors-dialog-header-title">Top 5 Errors by Sampler（详情）</span>
			</template>
			<el-table :data="top5Errors" size="small" class="errors-table-full" border :show-header="true" empty-text="No data" style="width: 100%">
				<el-table-column label="Sample（接口）" prop="sampler" min-width="180" header-align="center">
					<template #default="{ row }">
						<span class="sampler-name">{{ row.sampler }}</span>
					</template>
				</el-table-column>
				<el-table-column label="#Samples" prop="samples" width="90" align="center" header-align="center" />
				<el-table-column label="#Errors" prop="errors" width="80" align="center" header-align="center">
					<template #default="{ row }">
						<span class="total-errors">{{ row.errors }}</span>
					</template>
				</el-table-column>
				<el-table-column label="Error 1" min-width="130" header-align="center">
					<template #default="{ row }">
						<span v-if="row.top[0]" class="error-msg-full">{{ row.top[0].error }}</span>
					</template>
				</el-table-column>
				<el-table-column label="Count" width="60" align="center" header-align="center">
					<template #default="{ row }">
						<span v-if="row.top[0]" class="error-count">{{ row.top[0].count }}</span>
					</template>
				</el-table-column>
				<el-table-column label="Error 2" min-width="130" header-align="center">
					<template #default="{ row }">
						<span v-if="row.top[1]" class="error-msg-full">{{ row.top[1].error }}</span>
					</template>
				</el-table-column>
				<el-table-column label="Count" width="60" align="center" header-align="center">
					<template #default="{ row }">
						<span v-if="row.top[1]" class="error-count">{{ row.top[1].count }}</span>
					</template>
				</el-table-column>
				<el-table-column label="Error 3" min-width="130" header-align="center">
					<template #default="{ row }">
						<span v-if="row.top[2]" class="error-msg-full">{{ row.top[2].error }}</span>
					</template>
				</el-table-column>
				<el-table-column label="Count" width="60" align="center" header-align="center">
					<template #default="{ row }">
						<span v-if="row.top[2]" class="error-count">{{ row.top[2].count }}</span>
					</template>
				</el-table-column>
				<el-table-column label="Error 4" min-width="130" header-align="center">
					<template #default="{ row }">
						<span v-if="row.top[3]" class="error-msg-full">{{ row.top[3].error }}</span>
					</template>
				</el-table-column>
				<el-table-column label="Count" width="60" align="center" header-align="center">
					<template #default="{ row }">
						<span v-if="row.top[3]" class="error-count">{{ row.top[3].count }}</span>
					</template>
				</el-table-column>
				<el-table-column label="Error 5" min-width="130" header-align="center">
					<template #default="{ row }">
						<span v-if="row.top[4]" class="error-msg-full">{{ row.top[4].error }}</span>
					</template>
				</el-table-column>
				<el-table-column label="Count" width="60" align="center" header-align="center">
					<template #default="{ row }">
						<span v-if="row.top[4]" class="error-count">{{ row.top[4].count }}</span>
					</template>
				</el-table-column>
			</el-table>
		</el-drawer>

	</div>
</template>

<script setup lang="ts" name="SceneMonitor">
/* eslint-disable vue/no-mutating-props */
import { ref, computed, onUnmounted } from 'vue';
import { ElMessageBox } from 'element-plus';
import PerfConsole from '../components/PerfConsole.vue';
import MetricChart from '../components/MetricChart.vue';
import draggable from 'vuedraggable';
import { usePerformanceApi } from '/@/api/v1/testing/performance';
import { applyStageEvent } from '/@/utils/perfExecState';

const perfApi = usePerformanceApi();

// 接收父组件传入的当前监控场景（null 表示无任务，使用占位默认值保持 UI 完整显示）
const props = defineProps<{
	scene: any | null;
	execState?: {
		stages: { label: string; done: boolean; active: boolean }[];
		progress: number;
	} | null;
}>();

const emit = defineEmits<{
	'exec-done': [];
	'force-stop': [sceneId: number];
}>();

// scene 为 null 时兜底，保证所有字段不会 undefined
const currentScene = computed(() => props.scene ?? { name: '--', status: 'pending', progress: 0 });

// ======================== 联调/启动阶段进度条 ========================

const statusLabel = (status: string) => {
	const map: Record<string, string> = {
		debug: '待联调', pending: '待开始', running: '进行中', completed: '已完成', cancelled: '已取消', failed: '失败',
	};
	return map[status] ?? status;
};

const statusTagType = (status: string): '' | 'success' | 'warning' | 'danger' | 'info' => {
	const map: Record<string, '' | 'success' | 'warning' | 'danger' | 'info'> = {
		debug: 'info', pending: 'warning', running: '', completed: 'success', cancelled: 'info', failed: 'danger',
	};
	return map[status] ?? '';
};

const progressColor = (status: string) => {
	const map: Record<string, string> = {
		running: '#409eff', completed: '#67c23a', failed: '#f56c6c', cancelled: '#f56c6c',
	};
	return map[status] ?? '#409eff';
};

// ======================== 控制台日志 ========================

const consoleLogs = ref<{ time: string; text: string; level: string }[]>([]);

// ======================== 实时监控 SSE ========================

let _monitorAbortCtrl: AbortController | null = null;
const _isMonitoring = ref(false);
// 追踪已接收的 Redis 日志绝对偏移量，断线重连时携带以跳过历史日志，避免重复展示
const _logOffsetRef = ref(0);

const _addLog = (text: string, level?: string) => {
	const now = new Date();
	const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
	// 根据文本内容推断日志级别
	let lv = level;
	if (!lv) {
		const t = (text ?? '').toLowerCase();
		if ((text ?? '').startsWith('启动命令：')) lv = 'success';
		else if (/\berror\b/.test(t) || t.includes('exception')) lv = 'error';
		else if (t.includes('warn')) lv = 'warn';
		else lv = 'info';
	}
	consoleLogs.value.push({ time, text, level: lv });
};

const _handleMonitorEvent = (evt: any) => {
	if (evt.type === 'connected') {
		_addLog(evt.message || '已连接实时监控，等待日志数据...', 'info');
		// 用后端携带的实际读取起始偏移校准本地计数，防止任何客户端侧误差导致下次重连重放日志
		if (evt.start_offset !== undefined) {
			_logOffsetRef.value = evt.start_offset;
		}
		// 中途加入监控（如页面刷新重连）：用后端携带的当前阶段状态"补跳" execState，
		// 避免从 Stage1 重新显示，与手动启动时的连续体验保持一致
		if (props.execState && evt.stage_state) {
			const kind = evt.stage_state.kind === 'done' ? 'stage_done' : 'stage_start';
			applyStageEvent(props.execState, { type: kind, stage: evt.stage_state.stage, message: evt.stage_state.message }, true);
		}
	} else if (evt.type === 'log') {
		_logOffsetRef.value++;
		_addLog(evt.message ?? '');
	} else if (evt.type === 'progress') {
		// 直接修改父组件传入的 scene 对象（与父组件共享同一响应式引用）
		if (props.scene) props.scene.progress = evt.value ?? 0;
		// 仅当 execState 确实处于最后一个阶段（JMeter 已进入后台运行）时，才将真实进度
		// 映射进整体进度；Stage1/2 执行期间后端恒定推送 value=0，若不加此判断会用固定的
		// preWeight 覆盖当前阶段本该展示的进度值，导致进度条与阶段勾选状态不同步
		if (props.execState) {
			const stages = props.execState.stages;
			const lastStage = stages[stages.length - 1];
			if (lastStage?.active) {
				const preWeight = Math.max(0, (stages.length - 1) * 3);
				props.execState.progress = preWeight + Math.round((evt.value ?? 0) * (100 - preWeight) / 100);
			}
		}
	} else if (evt.type === 'done') {
		if (props.scene) {
			const statusMap: Record<number, string> = { 3: 'completed', 4: 'cancelled', 5: 'failed' };
			props.scene.status = statusMap[evt.status] ?? 'completed';
			if (evt.status === 3) props.scene.progress = 100;
			// 取消(4)和失败(5)保留 progress 事件已更新的当前值，不覆盖
		}
		const logType = evt.status === 3 ? 'success' : (evt.status === 4 ? 'warning' : 'error');
		_addLog(evt.message || '压测已完成', logType);
		// 标记所有阶段完成，进度 100%，通知父组件清除 execState
		if (props.execState) {
			props.execState.stages.forEach(s => { s.done = true; s.active = false; });
			props.execState.progress = 100;
		}
		emit('exec-done');
	} else if (evt.type === 'error') {
		_addLog(evt.message || '压测异常', 'error');
		// terminal=true：业务终态错误（场景不存在/未联调），通知父组件刷新；
		// 否则为瞬时异常（网络抖动等），SSE 将由后端自动重试，不修改场景状态，
		// 避免父组件以 offset=0 重连导致 Stage1/2/3 日志重复显示。
		if (evt.terminal) {
			emit('exec-done');
		}
	} else if (evt.type === 'cancelled' || evt.type === 'stopped') {
		if (props.scene) props.scene.status = 'cancelled';
		_addLog(evt.message || '压测已停止', 'warning');
		emit('exec-done');
	} else if (evt.type === 'stage_start' || evt.type === 'stage_done') {
		// 定时任务触发的运行由 monitor_sse 补发的结构化阶段事件驱动 execState，
		// 与手动启动（index.vue 直连 /execute 原始流）复用同一套推进逻辑；
		// 该事件的 message 与 jobs.py 转发的 log 事件文本重复，此处只更新进度条，不再重复写控制台
		if (props.execState) {
			applyStageEvent(props.execState, evt, true);
		}
	} else if (evt.type === 'metric') {
		_pushMetricPoint(evt);
	} else if (evt.type === 'top_errors') {
		top5Errors.value = evt.items ?? [];
	}
	// type === 'ping'：心跳保活，无需处理
};

const handleForceStop = () => {
	if (currentScene.value.status !== 'running') return;
	ElMessageBox.confirm(
		`确认立即停止「${currentScene.value.name}」的压测任务？`,
		'强制停止',
		{ type: 'warning', confirmButtonText: '立即停止', cancelButtonText: '取消', confirmButtonClass: 'el-button--danger' }
	).then(() => {
		emit('force-stop', currentScene.value.id);
	}).catch(() => {});
};

/**
 * 启动实时监控 SSE 连接（由父组件 index.vue 通过 ref 调用）。
 * @param scenarioId 压测场景 ID
 * @param initOffset 断线续传起点（默认从 0 开始）
 * consoleLogs 不会自动清空，只能通过"清空"按钮手动清除。
 */
const startMonitor = async (scenarioId: number, initOffset = 0) => {
	stopMonitor();
	_logOffsetRef.value = initOffset;
	_resetMetrics();
	_monitorAbortCtrl = new AbortController();
	_isMonitoring.value = true;

	try {
		const resp = await perfApi.monitorScenarioStream(scenarioId, initOffset, _monitorAbortCtrl.signal);
		if (!resp.ok || !resp.body) {
			_addLog(`连接失败（HTTP ${resp.status}）`, 'error');
			return;
		}
		const reader = resp.body.getReader();
		const decoder = new TextDecoder();
		let buffer = '';

		while (true) {
			const { done, value } = await reader.read();
			if (done) break;
			buffer += decoder.decode(value, { stream: true });
			const lines = buffer.split('\n');
			buffer = lines.pop() ?? '';
			for (const line of lines) {
				if (!line.startsWith('data: ')) continue;
				try { _handleMonitorEvent(JSON.parse(line.slice(6))); } catch { /* 忽略单行 JSON 解析异常 */ }
			}
		}
	} catch (e: any) {
		if (e?.name === 'AbortError') return;
		_addLog(`连接异常：${e?.message ?? String(e)}`, 'error');
	} finally {
		_isMonitoring.value = false;
	}
};

/** 停止实时监控 SSE 连接。*/
const stopMonitor = () => {
	_monitorAbortCtrl?.abort();
	_monitorAbortCtrl = null;
	_isMonitoring.value = false;
};

onUnmounted(() => { stopMonitor(); });

// ======================== 实时监控指标看板 ========================

const monitorDark = ref(true);
const expandVisible = ref(false);
const expandConfig = ref<{ title: string; unit: string; series: any[]; timeLabels: string[]; area: boolean } | null>(null);
const errorsExpandVisible = ref(false);
const errorsSmallTableRef = ref<any>(null);
const errorsDrawerSizePx = ref('300px');

const openErrorsExpand = () => {
	const smallEl = errorsSmallTableRef.value?.$el as HTMLElement | undefined;
	if (smallEl) {
		const tableH = smallEl.offsetHeight;
		const drawerHeaderH = 56;
		const t = drawerHeaderH + tableH;
		const maxH = Math.round(window.innerHeight * 0.9);
		errorsDrawerSizePx.value = Math.min(t, maxH) + 'px';
	}
	errorsExpandVisible.value = true;
};

const handleChartExpand = (cfg: { title: string; unit: string; series: any[]; timeLabels: string[]; area: boolean }) => {
	expandConfig.value = cfg;
	expandVisible.value = true;
};

// 时间轴：随 metric 事件实时滚动追加，初始为空（无历史数据可回放，见 monitor_sse 说明）
const monitorTimeLabels = ref<string[]>([]);

// 滚动窗口大小：按当前默认 5s 推送间隔计算约 5 分钟数据量；实际推送频率与后端
// JMETER_LOG_POLL_INTERVAL 一致（可配置），窗口仅用于控制图表展示点数，非采集精度
const _METRIC_WINDOW = 60;

// 图例按 sampler（JMeter label，兼容单机/分布式——分布式时 result.jtl 本就只在 master 上，
// 已是汇总后的按 sampler 明细）动态生成，不再用笼统的"整体"；QPS 按 success/failure 拆两条线；
// 并发线程数后端仅解析 summariser 的全局 Active 计数，无法按线程组拆分，保留单曲线但如实标注
const monitorMetrics = ref([
	{ title: 'QPS', unit: '次/秒', series: [] as { name: string; data: number[] }[], area: false },
	{ title: '平均响应时间（RT）', unit: 'ms', series: [] as { name: string; data: number[] }[], area: false },
	// 活跃线程组图表用面积图（折线下方填充），其余样式与其他图表保持一致
	{ title: '并发线程数', unit: '个', series: [{ name: '全部线程组', data: [] as number[] }], area: true },
	{ title: '错误率', unit: '%', series: [] as { name: string; data: number[] }[], area: false },
]);

/** 取或创建指定名称的序列，新建时用 0 补齐此前已推送的时间点，保持与 timeLabels 等长。*/
const _ensureSeries = (chart: { series: { name: string; data: number[] }[] }, name: string) => {
	let s = chart.series.find(x => x.name === name);
	if (!s) {
		const priorLen = Math.max(0, monitorTimeLabels.value.length - 1);
		s = { name, data: new Array(priorLen).fill(0) };
		chart.series.push(s);
	}
	return s;
};

/** 将实时指标快照按 sampler 动态追加进各图表，并裁剪到滚动窗口大小。*/
const _pushMetricPoint = (evt: any) => {
	monitorTimeLabels.value.push(evt.time ?? '');

	const [qpsChart, rtChart, threadsChart, errChart] = monitorMetrics.value;
	threadsChart.series[0].data.push(evt.threads ?? 0);

	const labels = evt.labels ?? {};
	const touched = new Set<string>();
	Object.keys(labels).forEach(label => {
		const m = labels[label] ?? {};
		const okSeries  = _ensureSeries(qpsChart, `${label}-success`);
		const errSeries = _ensureSeries(qpsChart, `${label}-failure`);
		okSeries.data.push(m.qps_ok ?? 0);
		errSeries.data.push(m.qps_err ?? 0);
		touched.add(okSeries.name);
		touched.add(errSeries.name);

		const rtSeries = _ensureSeries(rtChart, label);
		rtSeries.data.push(m.avg_rt ?? 0);
		touched.add(rtSeries.name);

		const errRateSeries = _ensureSeries(errChart, label);
		errRateSeries.data.push(m.err_rate ?? 0);
		touched.add(errRateSeries.name);
	});
	// 本轮未出现的既有 sampler 序列补 0，保持所有序列长度与 timeLabels 一致
	[qpsChart, rtChart, errChart].forEach(chart => {
		chart.series.forEach(s => { if (!touched.has(s.name)) s.data.push(0); });
	});

	if (monitorTimeLabels.value.length > _METRIC_WINDOW) {
		monitorTimeLabels.value.shift();
		monitorMetrics.value.forEach(m => m.series.forEach(s => s.data.shift()));
	}
};

/** 重置 4 个指标图表与 Top5 Errors，避免残留上一个场景的展示数据。*/
const _resetMetrics = () => {
	monitorTimeLabels.value = [];
	monitorMetrics.value[0].series = [];
	monitorMetrics.value[1].series = [];
	monitorMetrics.value[2].series = [{ name: '全部线程组', data: [] }];
	monitorMetrics.value[3].series = [];
	top5Errors.value = [];
};

const top5Errors = ref<any[]>([]);

const clearLogs = () => { consoleLogs.value = []; _logOffsetRef.value = 0; };

defineExpose({ startMonitor, stopMonitor, addExternalLog: _addLog, clearLogs, isMonitoring: _isMonitoring, logOffset: _logOffsetRef });
</script>

<style scoped lang="scss">
.scene-monitor {

	.monitor-progress-section {
		padding: 4px 0 6px;
		border-bottom: 1px solid var(--el-border-color-light);
		margin-bottom: 8px;

		.monitor-progress-header {
			display: flex;
			align-items: center;
			margin-bottom: 4px;

			.monitor-scene-name {
				font-size: 14px;
				font-weight: 600;
				color: var(--el-text-color-primary);
				white-space: nowrap;
				overflow: hidden;
				text-overflow: ellipsis;
				max-width: 40%;
			}

		}

		.monitor-progress-bar-row {
			display: flex;
			align-items: center;
			gap: 12px;

			.monitor-progress-bar {
				flex: 1;
			}

			.monitor-progress-suffix {
				flex-shrink: 0;
				width: 52px;
				display: flex;
				align-items: center;
				justify-content: center;
			}

			// stage 轨道（flex:1 与 suffix 同行对齐）
			.stage-bar-area {
				flex: 1;
				position: relative;

				.stage-track {
					height: 14px;
					background: var(--el-fill-color-darker, #e4e7ed);
					border-radius: 7px;
					overflow: hidden;

					.stage-fill {
						height: 100%;
						background: var(--el-color-primary);
						border-radius: 7px;
						transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
					}
				}

				// 阶段标签行：前两个 stage 由文字内容撑开宽度，最后一个 stage 占剩余空间居中；
				// 分割线（.stage-pin）作为该 flex 行内的普通子项与标签交替排列，天然落在
				// 文字实际渲染的边界处，不再需要按固定百分比单独定位，避免与文字重叠
				.stage-bar-seg-labels {
					position: absolute;
					top: 0;
					left: 0;
					right: 0;
					height: 14px;
					pointer-events: none;
					z-index: 2;
					display: flex;
					align-items: center;

					.stage-seg-label {
						font-size: 11px;
						font-weight: 600;
						white-space: nowrap;
						line-height: 14px;
						padding: 0 5px;
						flex-shrink: 0; // 前面的 stage 标签不压缩，宽度由文字撑开

						// 最后一个 stage 占剩余空间，文字居中
						&:last-child {
							flex: 1 1 0;
							text-align: center;
							flex-shrink: 1;
							overflow: hidden;
							text-overflow: ellipsis;
						}

						&.seg-done {
							color: rgba(255, 255, 255, 0.92);
							text-shadow: 0 0 4px rgba(0, 0, 0, 0.35);
						}
						&.seg-active {
							color: rgba(0, 0, 0, 0.82);
							text-shadow: 0 0 4px rgba(255, 255, 255, 0.9), 0 0 6px rgba(255, 255, 255, 0.6);
						}
						&.seg-wait {
							color: rgba(0, 0, 0, 0.45);
							text-shadow: 0 0 3px rgba(255, 255, 255, 0.7);
						}
					}

					// 阶段分割线：与标签同处 flex 流，靠 height 22px > 容器 14px 自然
					// 上下各溢出 4px，不再依赖绝对定位百分比坐标
					.stage-pin {
						flex-shrink: 0;
						height: 22px;
						width: 18px;
						cursor: default;
						display: flex;
						justify-content: center;
						align-items: stretch;
						pointer-events: auto; // 覆盖父级 pointer-events:none，恢复 hover 提示交互

						&::after {
							content: '';
							width: 2px;
							background: #c8ccd4;
							transition: background 0.3s;
						}

						&.pin-done::after { background: rgba(255, 255, 255, 0.88); }

						&.pin-active::after {
							background: #f0a020;
							animation: pin-pulse 1.2s ease-in-out infinite;
						}
					}
				}
			}
		}
	}

	.monitor-body {
		display: grid;
		grid-template-columns: 60% 1fr;
		// 高度由右列内容决定：metrics-header(38px) + 4×chart(222px) + 3×gap(10px) = 956px
		height: 956px;
		gap: 14px;

		.monitor-console-wrap {
			min-width: 0;
			height: 100%;
			display: flex;
			flex-direction: column;
			overflow: hidden;
		}

		.monitor-metrics-wrap {
			flex: 1;
			min-width: 0;
			display: flex;
			flex-direction: column;
			gap: 0;

			&.metrics-dark {
				.metrics-header {
					background: #111217;
					color: #7ec8e3;
					border-color: #1e2028;

					.theme-toggle-btn {
						color: #7ec8e3 !important;
						&:hover {
							color: #b0dff0 !important;
							background: rgba(255, 255, 255, 0.08) !important;
						}
					}
				}
			}

			.metrics-header {
				position: relative;
				display: flex;
				align-items: center;
				justify-content: center;
				padding: 8px 14px;
				font-size: 13.5px;
				font-weight: 600;
				color: var(--el-text-color-primary);
				background: var(--el-fill-color-light);
				border: 1px solid var(--el-border-color);
				border-radius: 6px;
				flex-shrink: 0;

				span {
					display: flex;
					align-items: center;
					gap: 6px;
				}

				.theme-toggle-btn {
					position: absolute;
					right: 8px;
					top: 50%;
					transform: translateY(-50%);
					color: var(--el-text-color-secondary);
					:deep(.el-icon) {
						font-size: 17px !important;
					}
				}
			}

			.metrics-charts-list {
				display: flex;
				flex-direction: column;
				gap: 10px;
				overflow-y: auto;
				padding: 0;
			}
		}
	}

	.monitor-errors-wrap {
		margin-top: 14px;
		border: 1px solid var(--e-border-color);
		border-radius: 8px;
		overflow: hidden;
		background: var(--el-fill-color-blank);

		--e-cell-bg: var(--el-fill-color-blank);
		--e-cell-color: var(--el-text-color-primary);
		--e-header-bg: var(--el-fill-color-light);
		--e-header-color: var(--el-text-color-secondary);
		--e-border-color: var(--el-border-color);
		--e-hover-bg: var(--el-fill-color-light);
		--e-row-alt-bg: var(--el-fill-color-lighter);

		&.errors-dark {
			border-color: #32333a;
			background: #181b1f;

			--e-cell-bg: #181b1f;
			--e-cell-color: #d8d9da;
			--e-header-bg: #22252b;
			--e-header-color: #9fa7b3;
			--e-border-color: #32333a;
			--e-hover-bg: rgba(255, 255, 255, 0.06);
			--e-row-alt-bg: rgba(255, 255, 255, 0.04);

			.errors-header {
				background: #111217;
				color: #7ec8e3;
				border-bottom-color: #1e2028;
			}

			.errors-expand-btn {
				color: #7ec8e3 !important;
				&:hover { color: #b0dff0 !important; background: rgba(255,255,255,0.08) !important; }
			}
		}

		.errors-header {
			position: relative;
			display: flex;
			align-items: center;
			justify-content: center;
			padding: 11px 40px 11px 14px;
			font-size: 13.5px;
			font-weight: 600;
			color: var(--el-text-color-primary);
			background: var(--el-fill-color-light);
			border-bottom: 1px solid var(--el-border-color);
		}

		.errors-header-title {
			display: flex;
			align-items: center;
			gap: 6px;
		}

		.errors-expand-btn {
			position: absolute;
			right: 8px;
			top: 50%;
			transform: translateY(-50%);
			color: var(--el-text-color-secondary) !important;
			&:hover { color: var(--el-text-color-primary) !important; background: var(--el-fill-color-dark) !important; }
		}

		.errors-table-scroll {
			overflow-x: auto;
		}

		:deep(.errors-table) {
			--el-table-border-color: var(--e-border-color);
			--el-table-border: 1px solid var(--e-border-color);
			--el-table-row-hover-bg-color: var(--e-hover-bg);
			--el-table-header-bg-color: var(--e-header-bg);
			--el-table-bg-color: var(--e-cell-bg);
			--el-table-tr-bg-color: var(--e-cell-bg);
			--el-table-text-color: var(--e-cell-color);
			--el-table-header-text-color: var(--e-header-color);
		}

		:deep(.errors-table td.el-table__cell) {
			background-color: var(--e-cell-bg) !important;
			color: var(--e-cell-color) !important;
			border-bottom-color: var(--e-border-color) !important;
			border-right-color: var(--e-border-color) !important;
		}

		:deep(.errors-table .el-table__row:nth-child(even) td.el-table__cell) {
			background-color: var(--e-row-alt-bg) !important;
		}

		:deep(.errors-table th.el-table__cell) {
			background-color: var(--e-header-bg) !important;
			color: var(--e-header-color) !important;
			border-bottom-color: var(--e-border-color) !important;
			border-right-color: var(--e-border-color) !important;
			text-align: center !important;
		}

		:deep(.errors-table .hover-row > td.el-table__cell) {
			background-color: var(--e-hover-bg) !important;
		}

		:deep(.errors-table.el-table--border::before),
		:deep(.errors-table.el-table--border::after),
		:deep(.errors-table.el-table--border .el-table__inner-wrapper::after),
		:deep(.errors-table .el-table__inner-wrapper::before),
		:deep(.errors-table .el-table__border-left-patch),
		:deep(.errors-table .el-table__border-right-patch),
		:deep(.errors-table .el-table__border-bottom-patch) {
			background-color: var(--e-border-color) !important;
		}

		:deep(.errors-table) {
			.total-errors { color: #f56c6c; font-weight: 600; }
			.error-count { color: #e6a23c; }
			.sampler-name {
				display: block;
				white-space: normal;
				word-break: break-all;
				max-width: 240px;
				font-size: 12px;
			}
			.error-msg {
				font-size: 12px;
				white-space: normal;
				word-break: break-all;
				max-width: 280px;
				display: block;
			}
		}
	}
}

@keyframes pin-pulse {
	0%, 100% { opacity: 1; }
	50%       { opacity: 0.35; }
}
</style>

<style lang="scss">
/* 图表拖拽排序 */
.metric-drag-ghost { opacity: 0.25; }
.metric-drag-chosen { opacity: 0.9; box-shadow: 0 4px 16px rgba(0,0,0,0.18); }

/* 放大图表弹窗：隐藏头部，仅保留图表内容 */
.expand-chart-dialog {
	.el-dialog__header { display: none; }
	.el-dialog__body { padding: 0 !important; }
}

/* ─── errors-expand-drawer 全局样式（el-drawer 使用 teleport，必须非 scoped） ─── */
.errors-expand-drawer {
  overflow: hidden;

  .el-drawer__header {
    position: relative !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 10px 48px !important;
    margin-bottom: 0 !important;
    border-bottom: 1px solid var(--el-border-color) !important;
    background: var(--el-fill-color-light) !important;
    overflow: hidden !important;
  }

  .el-drawer__header > :first-child {
    text-align: center !important;
  }

  .el-drawer__close-btn {
    position: absolute !important;
    right: 12px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    color: var(--el-text-color-regular) !important;
    font-size: 20px !important;
  }

  .el-drawer__body {
    padding: 0;
    overflow: hidden;
  }

  .errors-dialog-header-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .errors-table-full th.el-table__cell {
    text-align: center !important;
  }
  .errors-table-full .el-table__row:nth-child(even) td.el-table__cell {
    background-color: var(--el-fill-color-lighter) !important;
  }
  .errors-table-full .total-errors { color: #f56c6c; font-weight: 600; }
  .errors-table-full .error-count   { color: #e6a23c; }
  .errors-table-full .sampler-name  {
    display: block; white-space: normal; word-break: break-all; font-size: 12px;
  }
  .errors-table-full .error-msg-full {
    font-size: 12.5px; white-space: normal; word-break: break-all; display: block;
  }
}

.errors-expand-drawer.errors-expand-dark {
  background-color: #181b1f !important;

  .el-drawer__header {
    background: #111217 !important;
    border-bottom-color: #1e2028 !important;
  }

  .el-drawer__close-btn { color: #9fa7b3 !important; }
  .errors-dialog-header-title { color: #d8d9da !important; }

  .el-drawer__body {
    background: #181b1f;
    overflow: hidden;
  }

  .el-drawer__body {
    --el-table-border-color: #32333a;
    --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.06);
  }

  .errors-table-full td.el-table__cell {
    background-color: #181b1f !important;
    color: #d8d9da !important;
    border-bottom-color: #32333a !important;
    border-right-color: #32333a !important;
  }

  .errors-table-full .el-table__row:nth-child(even) td.el-table__cell {
    background-color: #1f2128 !important;
  }

  .errors-table-full th.el-table__cell {
    background-color: #22252b !important;
    color: #9fa7b3 !important;
    border-bottom-color: #32333a !important;
    border-right-color: #32333a !important;
    text-align: center !important;
  }

  .errors-table-full {
    --el-table-bg-color: #181b1f;
    --el-table-tr-bg-color: #181b1f;
    --el-table-header-bg-color: #22252b;
    background-color: #181b1f !important;
  }

  .errors-table-full .el-table__inner-wrapper {
    background-color: #181b1f !important;
  }

  .errors-table-full.el-table--border::before,
  .errors-table-full.el-table--border::after,
  .errors-table-full.el-table--border .el-table__inner-wrapper::after,
  .errors-table-full .el-table__inner-wrapper::before,
  .errors-table-full .el-table__border-left-patch,
  .errors-table-full .el-table__border-right-patch,
  .errors-table-full .el-table__border-bottom-patch {
    background-color: #32333a !important;
  }

  .errors-table-full .hover-row > td.el-table__cell {
    background-color: rgba(255, 255, 255, 0.06) !important;
  }
}
</style>
