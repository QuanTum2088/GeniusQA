<template>
  <img
    v-if="imgBase"
    :src="imgBase"
    :width="width"
    :height="height"
    class="captcha-img"
    alt="验证码"
    title="点击刷新"
    @click="refreshCode"
  />
  <div
    v-else
    class="captcha-placeholder"
    :style="{ width: width + 'px', height: height + 'px' }"
    @click="refreshCode"
  >
    点击刷新
  </div>
</template>

<script setup lang="ts">
interface Props {
  width?: number;
  height?: number;
  imgBase?: string;
}

withDefaults(defineProps<Props>(), {
  width: 120,
  height: 40,
  imgBase: '',
});

const emit = defineEmits<{
  (e: 'refresh'): void;
}>();

const refreshCode = () => {
  emit('refresh');
};

defineExpose({
  refreshCode,
});
</script>

<style scoped lang="scss">
.captcha-img {
  cursor: pointer;
  border-radius: 4px;
  vertical-align: middle;
  display: block;
  object-fit: cover;
  background: #f5f7fa;

  &:hover {
    opacity: 0.85;
  }
}

.captcha-placeholder {
  cursor: pointer;
  border-radius: 4px;
  background: #f5f7fa;
  color: #909399;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
}
</style>
