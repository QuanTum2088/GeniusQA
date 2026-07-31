<template>
	<el-drawer
		v-model="visible"
		title="对话配置"
		direction="rtl"
		size="420px"
		:append-to-body="true"
		class="chat-settings-drawer"
	>
		<div class="drawer-body">
			<section class="settings-section">
				<div class="section-header">
					<span class="section-title">项目</span>
					<span class="section-desc">对话关联的项目上下文</span>
				</div>
				<el-select
					v-model="selectedProjectId"
					placeholder="选择项目"
					style="width: 100%"
					@change="emit('project-change')"
				>
					<el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
				</el-select>
			</section>

			<section class="settings-section">
				<div class="section-header row">
					<div>
						<span class="section-title">知识库</span>
						<span class="section-desc">检索项目知识增强回答</span>
					</div>
					<el-switch v-model="useKnowledgeBase" />
				</div>
				<el-select
					v-model="selectedKnowledgeBaseId"
					placeholder="知识库来源"
					clearable
					style="width: 100%"
					:disabled="!useKnowledgeBase"
				>
					<el-option
						v-for="kb in knowledgeBases"
						:key="kb.id"
						:label="kb.name"
						:value="Number(kb.id)"
					/>
				</el-select>
			</section>

			<section class="settings-section">
				<div class="section-header row">
					<div>
						<span class="section-title">MCP</span>
						<span class="section-desc">启用 MCP 工具调用</span>
					</div>
					<el-switch v-model="useMcp" />
				</div>
				<el-select
					v-model="selectedMcpConfigId"
					placeholder="MCP 配置"
					clearable
					style="width: 100%"
					:disabled="!useMcp"
				>
					<el-option v-for="m in mcpConfigs" :key="m.id" :label="m.name" :value="m.id" />
				</el-select>
			</section>

			<section class="settings-section">
				<div class="section-header">
					<span class="section-title">调用模式</span>
					<span class="section-desc">智能由模型决策；直连指定工具执行</span>
				</div>
				<el-radio-group v-model="toolMode" class="mode-group">
					<el-radio-button label="smart">智能</el-radio-button>
					<el-radio-button label="direct">直连</el-radio-button>
				</el-radio-group>
			</section>

			<!-- 后续新配置项按 section 追加即可 -->
		</div>

		<template #footer>
			<div class="drawer-footer">
				<el-button @click="visible = false">关闭</el-button>
			</div>
		</template>
	</el-drawer>
</template>

<script setup lang="ts">
defineOptions({ name: 'ChatSettingsDrawer' })

export interface ChatSettingsOption {
	id: number | string
	name: string
}

defineProps<{
	projects: Array<{ id: number; name: string }>
	knowledgeBases: ChatSettingsOption[]
	mcpConfigs: ChatSettingsOption[]
}>()

const emit = defineEmits<{
	(e: 'project-change'): void
}>()

const visible = defineModel<boolean>('visible', { default: false })
const selectedProjectId = defineModel<number | null>('selectedProjectId', { default: null })
const useKnowledgeBase = defineModel<boolean>('useKnowledgeBase', { default: false })
const selectedKnowledgeBaseId = defineModel<number | null>('selectedKnowledgeBaseId', { default: null })
const useMcp = defineModel<boolean>('useMcp', { default: false })
const selectedMcpConfigId = defineModel<number | null>('selectedMcpConfigId', { default: null })
const toolMode = defineModel<'smart' | 'direct'>('toolMode', { default: 'smart' })
</script>

<style scoped lang="scss">
.drawer-body {
	display: flex;
	flex-direction: column;
	gap: 20px;
	padding: 0 4px 8px;
}

.settings-section {
	padding: 16px;
	border: 1px solid var(--el-border-color-lighter);
	border-radius: 10px;
	background: var(--el-fill-color-blank);
}

.section-header {
	margin-bottom: 12px;

	&.row {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 12px;
	}
}

.section-title {
	display: block;
	font-size: 15px;
	font-weight: 600;
	color: var(--el-text-color-primary);
	line-height: 1.3;
}

.section-desc {
	display: block;
	margin-top: 4px;
	font-size: 12px;
	color: var(--el-text-color-secondary);
	line-height: 1.4;
}

.mode-group {
	width: 100%;

	:deep(.el-radio-button) {
		flex: 1;
	}

	:deep(.el-radio-button__inner) {
		width: 100%;
	}
}

.drawer-footer {
	display: flex;
	justify-content: flex-end;
}
</style>
