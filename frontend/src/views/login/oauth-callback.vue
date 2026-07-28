<template>
  <!-- OAuth 回调功能已禁用 -->
</template>

<script setup lang="ts" name="oauthCallback">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';

// 第三方登录回调已禁用，直接跳转到登录页
const router = useRouter();
onMounted(() => {
  router.replace('/login');
});
</script>
