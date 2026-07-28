<template>
	<el-drawer
		v-model="drawerVisible"
		direction="rtl"
		size="580px"
		class="scene-debug-drawer"
		:close-on-click-modal="false"
		destroy-on-close
		@open="onOpen"
		@closed="onClosed"
	>
		<!-- ── 标题栏：场景名 + JMX 脚本 ── -->
		<template #header>
			<div class="dbg-header">
				<el-icon class="dbg-header-icon"><ele-Connection /></el-icon>
				<div class="dbg-header-info">
					<span class="dbg-scene-name">{{ scene?.name ?? '—' }}</span>
					<span class="dbg-jmx-name">
						<el-icon style="font-size:12px;margin-right:3px;vertical-align:-1px"><ele-Document /></el-icon>
						{{ scene?.script_name ?? '—' }}
					</span>
				</div>
			</div>
		</template>

		<!-- ── 工作流主体 ── -->
		<div class="dbg-flow">

			<!-- 全局进度条（sticky 悬浮） -->
			<div class="dbg-progress">
				<div class="dbg-progress-track">
					<div class="dbg-progress-fill" :style="{ width: progressPct + '%' }" />
				</div>
				<span class="dbg-progress-pct">{{ progressPct }}%</span>
			</div>

			<!-- 步骤列表 -->
			<div class="dbg-steps">
				<template v-for="(item, idx) in visibleItems" :key="item.id">
					<div class="dbg-step" :class="`status-${item.status}`">

						<!-- 左侧：指示器 + 连接线 -->
						<div class="step-track">
							<div class="step-dot">
								<!-- 待核实 -->
								<span v-if="item.status === 'pending'" class="dot-pending" />
								<!-- 核实中 -->
								<span v-else-if="item.status === 'checking'" class="dot-checking" />
								<!-- 通过 -->
								<el-icon v-else-if="item.passed !== false" class="dot-pass"><ele-CircleCheck /></el-icon>
								<!-- 失败 -->
								<el-icon v-else class="dot-fail"><ele-CircleClose /></el-icon>
							</div>
							<!-- 连接线（最后一项不显示） -->
							<div v-if="idx < visibleItems.length - 1" class="step-line" />
						</div>

						<!-- 右侧：内容 -->
						<div class="step-body">
							<!-- 步骤名称 -->
							<span class="step-label">{{ item.label }}</span>

							<!-- 结果区 -->
							<span class="step-result">
								<!-- 待核实 -->
								<span v-if="item.status === 'pending'" class="res-pending">待核实</span>

								<!-- 核实中 -->
								<span v-else-if="item.status === 'checking'" class="res-checking">
									<span class="checking-dots">{{ dots }}</span>
									<span class="checking-tip">核实中</span>
								</span>

								<!-- 完成：纯数值 -->
								<template v-else-if="item.type === 'value'">
									<span class="res-value">{{ item.resultText }}</span>
									<span v-if="item.remark" class="res-remark">（{{ item.remark }}）</span>
								</template>

								<!-- 完成：校验结果 ✓/✗ -->
								<template v-else-if="item.type === 'check'">
									<el-icon v-if="item.passed" class="res-pass"><ele-CircleCheck /></el-icon>
									<el-icon v-else class="res-fail"><ele-CircleClose /></el-icon>
									<span v-if="item.remark" class="res-remark" :class="{ 'remark-error': !item.passed }">
										（{{ item.remark }}）
									</span>
								</template>

								<!-- 完成：URL + 校验 -->
								<template v-else-if="item.type === 'mixed'">
									<span class="res-value res-url">{{ item.resultText }}</span>
									<el-icon v-if="item.passed" class="res-pass"><ele-CircleCheck /></el-icon>
									<el-icon v-else class="res-fail"><ele-CircleClose /></el-icon>
									<span v-if="item.remark" class="res-remark" :class="{ 'remark-error': !item.passed }">
										（{{ item.remark }}）
									</span>
								</template>
							</span>
						</div>
					</div>
				</template>
			</div>

			<!-- 完成提示 -->
			<transition name="notice-fade">
				<div v-if="allDone" class="dbg-notice" :class="{ 'has-error': hasError }">
					<el-icon><ele-InfoFilled /></el-icon>
					<span v-if="hasError">核实发现异常，请确认错误信息后再决定是否启动。</span>
					<span v-else>以上信息核实无误，点击「确定」将直接启动压测脚本。</span>
				</div>
			</transition>
		</div>

		<!-- ── 页脚 ── -->
		<template #footer>
			<div class="dbg-footer">
				<el-button @click="drawerVisible = false">取消</el-button>
				<el-button
					type="primary"
					:disabled="!allDone"
					@click="handleConfirm"
				>
					<el-icon><ele-VideoPlay /></el-icon>确定（启动压测）
				</el-button>
			</div>
		</template>
	</el-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

// ── Props / Emits ─────────────────────────────────────────────
const props = withDefaults(defineProps<{
	modelValue: boolean;
	scene?: any;
}>(), {
	modelValue: false,
	scene: null,
});

const emit = defineEmits<{
	(e: 'update:modelValue', val: boolean): void;
	(e: 'confirm', scene: any): void;
}>();

const drawerVisible = computed({
	get: () => props.modelValue,
	set: (v) => emit('update:modelValue', v),
});

// ── 类型 ──────────────────────────────────────────────────────
type ItemStatus = 'pending' | 'checking' | 'done' | 'error';
type ItemType   = 'value' | 'check' | 'mixed';

interface DebugItem {
	id:          string;
	label:       string;
	type:        ItemType;
	status:      ItemStatus;
	resultText?: string;
	passed?:     boolean;
	remark?:     string;
	hidden:      boolean;
	delay:       number;   // 模拟耗时 ms
}

// ── 动画 dots ─────────────────────────────────────────────────
const dotCount = ref(1);
const dots = computed(() => '. '.repeat(dotCount.value).trimEnd());
let dotTimer: ReturnType<typeof setInterval>  | null = null;
let checkTimer: ReturnType<typeof setTimeout> | null = null;

// ── 状态 ──────────────────────────────────────────────────────
const items     = ref<DebugItem[]>([]);
const curIdx    = ref(-1);

const visibleItems = computed(() => items.value.filter(i => !i.hidden));
const allDone      = computed(() => visibleItems.value.length > 0
	&& visibleItems.value.every(i => i.status === 'done' || i.status === 'error'));
const hasError     = computed(() => items.value.some(i => i.status === 'error'));

const progressPct  = computed(() => {
	const v = visibleItems.value;
	if (!v.length) return 0;
	const done = v.filter(i => i.status === 'done' || i.status === 'error').length;
	return Math.round((done / v.length) * 100);
});

// ── 构建条目 ──────────────────────────────────────────────────
const buildItems = (scene: any): DebugItem[] => {
	const cfg         = scene?.configs?.find((c: any) => c.active) ?? scene?.configs?.[0] ?? {};
	const distributed = !!cfg.distributed;
	const workers     = cfg.worker_count ?? 0;
	const threads     = cfg.threads      ?? 0;
	const rampUp      = cfg.ramp_up      ?? 0;
	const startDelay  = cfg.start_delay  ?? 0;
	const loopCount   = cfg.loop_count   ?? 0;
	const forever     = !!cfg.forever;
	const duration    = cfg.duration     ?? 0;

	const durationText = forever && duration
		? `持续执行 ${Math.round(duration / 60)} 分钟`
		: loopCount ? `循环 ${loopCount} 次` : '—';

	const workerText   = distributed
		? (workers > 0 ? String(workers) : '0')
		: '1';
	const workerRemark = !distributed ? '单机模式' : workers === 0 ? '未配置 slave，按单机处理' : undefined;

	// Mock 数据（实际应从后端/JMX 解析）
	const backendOn  = true;
	const influxUrl  = 'http://192.168.10.100:8086';
	const influxOk   = true;
	const hasFile    = true;
	const fileName   = 'users_prod.csv';
	const distOk     = true;
	const connOk     = true;
	const startOk    = true;

	return [
		{
			id: 'api_url', label: '压测接口', type: 'value', status: 'pending', hidden: false, delay: 600,
			resultText: 'https://api.geniusqa.com/v2/user/login（用户登录接口）',
		},
		{
			id: 'threads', label: '单节点线程数', type: 'value', status: 'pending', hidden: false, delay: 350,
			resultText: String(threads),
		},
		{
			id: 'workers', label: '启动 Worker 数量', type: 'value', status: 'pending', hidden: false, delay: 350,
			resultText: workerText, remark: workerRemark,
		},
		{
			id: 'ramp_up', label: 'Ramp-up 时间', type: 'value', status: 'pending', hidden: false, delay: 350,
			resultText: `${rampUp} 秒`,
		},
		{
			id: 'duration', label: '压测持续时间', type: 'value', status: 'pending', hidden: false, delay: 350,
			resultText: durationText,
		},
		{
			id: 'start_delay', label: '启动延迟时间', type: 'value', status: 'pending', hidden: false, delay: 350,
			resultText: `${startDelay} 秒`,
		},
		{
			id: 'data_file', label: '引用数据文件', type: 'value', status: 'pending', hidden: false, delay: 700,
			resultText: hasFile ? fileName : '无',
		},
		{
			id: 'backend', label: '启用后端监听器', type: 'check', status: 'pending', hidden: false, delay: 800,
			passed: backendOn, remark: 'InfluxDB 时序数据库',
		},
		{
			id: 'influxdb', label: 'InfluxDB URL', type: 'mixed', status: 'pending',
			hidden: !backendOn, delay: 1800,
			resultText: influxUrl, passed: influxOk,
			remark: influxOk ? '地址访问正常' : '地址不可达，请检查网络',
		},
		{
			id: 'dist_method', label: '数据文件分发方式', type: 'value', status: 'pending',
			hidden: !distributed, delay: 500,
			resultText: '共享分发',
		},
		{
			id: 'dist_status', label: '文件分发状态', type: 'check', status: 'pending',
			hidden: !distributed, delay: 1600,
			passed: distOk, remark: distOk ? '' : 'slave-2 磁盘空间不足',
		},
		{
			id: 'clean_jmeter', label: '清理 JMeter 进程', type: 'check', status: 'pending', hidden: false, delay: 1000,
			passed: true, remark: 'ssh_kill_jmeter.sh',
		},
		{
			id: 'clean_logs', label: '清理日志数据文件', type: 'check', status: 'pending', hidden: false, delay: 900,
			passed: true, remark: 'ssh_remove_csv_log',
		},
		{
			id: 'server_conn', label: '服务器连接', type: 'check', status: 'pending', hidden: false, delay: 1400,
			passed: connOk, remark: connOk ? 'Master ↔ Slave 互联互通' : '连接异常，请检查 SSH 配置',
		},
		{
			id: 'jmeter_start', label: 'JMeter 启动', type: 'check', status: 'pending', hidden: false, delay: 1800,
			passed: startOk, remark: startOk
				? (distributed ? '分布式启动正常' : '单机启动正常')
				: '启动失败，请查看日志',
		},
	];
};

// ── 序列推进 ──────────────────────────────────────────────────
const advance = () => {
	// 找下一个未隐藏、未完成的条目
	let next = curIdx.value + 1;
	while (next < items.value.length && items.value[next].hidden) next++;

	if (next >= items.value.length) {
		curIdx.value = items.value.length;
		stopTimers();
		return;
	}

	curIdx.value = next;
	items.value[next].status = 'checking';

	checkTimer = setTimeout(() => {
		const it = items.value[next];
		if (it.type === 'check' || it.type === 'mixed') {
			it.status = it.passed ? 'done' : 'error';
		} else {
			it.status = 'done';
		}
		advance();
	}, items.value[next].delay);
};

const startDots = () => {
	dotCount.value = 1;
	dotTimer = setInterval(() => { dotCount.value = (dotCount.value % 3) + 1; }, 360);
};

const stopTimers = () => {
	if (dotTimer)   { clearInterval(dotTimer);  dotTimer   = null; }
	if (checkTimer) { clearTimeout(checkTimer); checkTimer = null; }
};

// ── Drawer 生命周期 ───────────────────────────────────────────
const onOpen = () => {
	if (!props.scene) return;
	items.value  = buildItems(props.scene);
	curIdx.value = -1;
	startDots();
	checkTimer = setTimeout(advance, 400);
};

const onClosed = () => {
	stopTimers();
	items.value  = [];
	curIdx.value = -1;
};

const handleConfirm = () => {
	emit('confirm', props.scene);
	drawerVisible.value = false;
};
</script>

<style scoped lang="scss">
// ── 标题栏 ───────────────────────────────────────────────────
.dbg-header {
	display: flex;
	align-items: center;
	gap: 10px;

	.dbg-header-icon {
		font-size: 20px;
		color: var(--el-color-primary);
		flex-shrink: 0;
	}

	.dbg-header-info {
		display: flex;
		flex-direction: column;
		gap: 2px;
		min-width: 0;
	}

	.dbg-scene-name {
		font-size: 15px;
		font-weight: 600;
		color: var(--el-text-color-primary);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.dbg-jmx-name {
		font-size: 12px;
		color: var(--el-text-color-secondary);
		display: flex;
		align-items: center;
	}
}

// ── 全局进度条（sticky 悬浮） ─────────────────────────────────
.dbg-progress {
	position: sticky;
	top: -16px;          // 抵消 drawer body 的 padding-top: 16px
	z-index: 20;
	margin: -4px -20px 0; // 向两侧延伸，盖住侧边 padding
	padding: 8px 20px 12px;
	background: var(--el-bg-color);
	display: flex;
	align-items: center;
	gap: 10px;

	.dbg-progress-track {
		flex: 1;
		height: 7px;
		background: var(--el-fill-color-light);
		border-radius: 4px;
		overflow: hidden;

		.dbg-progress-fill {
			height: 100%;
			background: var(--el-color-primary);
			border-radius: 4px;
			transition: width 0.4s ease;
		}
	}

	.dbg-progress-pct {
		font-size: 12px;
		font-weight: 600;
		color: var(--el-color-primary);
		min-width: 34px;
		text-align: right;
		white-space: nowrap;
	}
}

// ── 工作流主体 ───────────────────────────────────────────────
.dbg-flow {
	padding: 4px 0 0;
}

.dbg-steps {
	display: flex;
	flex-direction: column;
}

// ── 单个步骤 ─────────────────────────────────────────────────
.dbg-step {
	display: flex;
	align-items: flex-start;
	gap: 12px;
	min-height: 40px;

	// 待核实：整体淡化
	&.status-pending {
		opacity: 0.36;
	}

	// 核实中：高亮步骤名
	&.status-checking {
		.step-label { color: var(--el-color-primary); font-weight: 500; }
		.step-dot .dot-checking { animation: pulse 1s ease-in-out infinite; }
	}

	// 错误行
	&.status-error {
		.step-label { color: var(--el-color-danger); }
	}
}

// 左轨道（指示器 + 连接线）
.step-track {
	display: flex;
	flex-direction: column;
	align-items: center;
	flex-shrink: 0;
	width: 22px;
	padding-top: 10px;
}

.step-dot {
	width: 20px;
	height: 20px;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;

	.dot-pending {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		border: 2px solid var(--el-border-color);
		background: transparent;
		display: block;
	}

	.dot-checking {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		background: var(--el-color-primary);
		display: block;
	}

	.dot-pass {
		font-size: 18px;
		color: var(--el-color-success);
	}

	.dot-fail {
		font-size: 18px;
		color: var(--el-color-danger);
	}
}

// 步骤间连接线
.step-line {
	width: 2px;
	flex: 1;
	min-height: 16px;
	background: var(--el-border-color-lighter);
	margin: 3px 0 0;
}

// 右侧内容
.step-body {
	flex: 1;
	display: flex;
	align-items: baseline;
	gap: 10px;
	padding: 8px 0 10px;
	border-bottom: 1px dashed var(--el-border-color-extra-light);
	flex-wrap: wrap;
	min-width: 0;
}

.dbg-step:last-child .step-body {
	border-bottom: none;
}

.step-label {
	white-space: nowrap;
	font-size: 13.5px;
	color: var(--el-text-color-primary);
	flex-shrink: 0;
}

.step-result {
	display: flex;
	align-items: center;
	gap: 5px;
	flex-wrap: wrap;
	min-width: 0;
	font-size: 13px;
}

// 结果具体样式
.res-pending {
	color: var(--el-text-color-placeholder);
	font-size: 12px;
}

.res-checking {
	display: flex;
	align-items: center;
	gap: 6px;
}

.checking-dots {
	font-size: 15px;
	font-weight: 700;
	letter-spacing: 3px;
	color: var(--el-color-primary);
	min-width: 26px;
	display: inline-block;
}

.checking-tip {
	font-size: 12px;
	color: var(--el-color-primary-light-3);
}

.res-value {
	color: var(--el-text-color-primary);
	font-weight: 500;
	word-break: break-all;
}

.res-url {
	font-size: 12.5px;
	word-break: break-all;
}

.res-pass {
	font-size: 16px;
	color: var(--el-color-success);
}

.res-fail {
	font-size: 16px;
	color: var(--el-color-danger);
}

.res-remark {
	font-size: 12px;
	color: var(--el-text-color-secondary);

	&.remark-error { color: var(--el-color-danger); }
}

// ── 完成提示 ─────────────────────────────────────────────────
.dbg-notice {
	margin-top: 16px;
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 10px 14px;
	border-radius: 6px;
	background: var(--el-color-success-light-9);
	border: 1px solid var(--el-color-success-light-5);
	font-size: 13px;
	color: #529b2e;

	&.has-error {
		background: var(--el-color-warning-light-9);
		border-color: var(--el-color-warning-light-5);
		color: var(--el-color-warning-dark-2);
	}

	.el-icon { font-size: 16px; flex-shrink: 0; }
}

.notice-fade-enter-active { transition: opacity 0.45s, transform 0.4s; }
.notice-fade-enter-from   { opacity: 0; transform: translateY(8px); }

// ── 页脚 ─────────────────────────────────────────────────────
.dbg-footer {
	display: flex;
	justify-content: flex-end;
	gap: 10px;
}

// ── 动画 ─────────────────────────────────────────────────────
@keyframes pulse {
	0%, 100% { transform: scale(1);   opacity: 1; }
	50%       { transform: scale(1.5); opacity: 0.6; }
}
</style>

<!-- 全局修复 el-drawer 内边距 -->
<style lang="scss">
.scene-debug-drawer {
	.el-drawer__header {
		margin-bottom: 0 !important;
		padding: 12px 20px 12px !important;
		border-bottom: 1px solid var(--el-border-color-lighter);
	}
	.el-drawer__body {
		padding: 16px 20px !important;
		overflow-y: auto;
	}
	.el-drawer__footer {
		padding: 12px 20px !important;
		border-top: 1px solid var(--el-border-color-lighter);
	}
}
</style>
