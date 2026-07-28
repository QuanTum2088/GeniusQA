<template>
	<div class="api-automation-root">
		<ApiList v-if="currentService === null" @select-service="onSelectService" />
		<ApiServiceDetail
			v-else
			:serviceId="currentService.id"
			:serviceName="currentService.name"
			:sourceType="currentService.source_type"
			:sourceAddr="currentService.source_addr"
			@back="onBack"
			@update-source="onUpdateSource"
		/>
	</div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ApiList from './api_list.vue';
import ApiServiceDetail from './api_service_detail.vue';

type ServiceInfo = {
	id: number;
	name: string;
	source_type?: string;
	source_addr?: string;
};

const currentService = ref<ServiceInfo | null>(null);

function onSelectService(service: ServiceInfo) {
	currentService.value = {
		id: service.id,
		name: service.name,
		source_type: service.source_type || '',
		source_addr: service.source_addr || '',
	};
}

function onUpdateSource(payload: { source_type?: string; source_addr?: string }) {
	if (!currentService.value) return;
	currentService.value = {
		...currentService.value,
		...(payload.source_type !== undefined ? { source_type: payload.source_type } : {}),
		...(payload.source_addr !== undefined ? { source_addr: payload.source_addr } : {}),
	};
}

function onBack() {
	currentService.value = null;
}
</script>

<style scoped>
.api-automation-root {
	position: absolute;
	inset: 0;
	display: flex;
	flex-direction: column;
	overflow: hidden;
}
</style>
