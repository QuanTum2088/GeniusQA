<template>
  <div class="login">
    <LoginLeftView />

    <div class="right-wrap">
      <div class="login-toolbar">
        <div class="theme-colors">
          <span
            v-for="c in themePresets"
            :key="c.color"
            class="theme-dot"
            :style="{ background: c.color }"
            :class="{ active: isActiveTheme(c.color) }"
            :title="c.name"
            @click="switchTheme(c)"
          >
            <el-icon v-if="isActiveTheme(c.color)" class="theme-dot-check"><ele-Check /></el-icon>
          </span>
          <el-color-picker
            v-model="getThemeConfig.primary"
            size="small"
            class="theme-custom-picker"
            title="自定义颜色"
            @change="onColorPickerChange"
          />
        </div>
        <el-tooltip :content="getThemeConfig.isIsDark ? '切换浅色' : '切换深色'" placement="bottom">
          <button type="button" class="dark-toggle" @click="toggleDark($event)">
            <el-icon v-if="getThemeConfig.isIsDark"><ele-Sunny /></el-icon>
            <el-icon v-else><ele-Moon /></el-icon>
          </button>
        </el-tooltip>
      </div>

      <div class="login-wrap">
        <div class="form">
          <h3 class="title">欢迎回来 <span class="wave" aria-hidden="true">👋</span></h3>
          <p class="sub-title">输入您的账号和密码登录系统</p>

          <div v-if="!state.isScan" class="form-body">
            <Account />
            <OAuth />
          </div>
          <Scan v-else />
        </div>
      </div>

      <div class="login-copyright">
        <span>GeniusQA</span>
        <span class="sep">|</span>
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">粤ICP备202698015号</a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" name="loginIndex">
import { computed, defineAsyncComponent, onMounted, reactive } from 'vue';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
import { NextLoading } from '/@/utils/loading';
import { onAddDarkChange, onColorPickerChange } from '/@/layout/navBars/topBar/settings/index';
import { getHexColor } from '/@/utils/theme';

const Account = defineAsyncComponent(() => import('/@/views/login/component/account.vue'));
const Scan = defineAsyncComponent(() => import('/@/views/login/component/scan.vue'));
const OAuth = defineAsyncComponent(() => import('/@/views/login/component/oauth.vue'));
const LoginLeftView = defineAsyncComponent(() => import('/@/views/login/component/LoginLeftView.vue'));

const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);
const state = reactive({ isScan: false });
const getThemeConfig = computed(() => themeConfig.value);

const themePresets = [
  { color: '#0741ef', name: '默认蓝' },
  { color: 'hsl(245 82% 67%)', name: '紫罗兰' },
  { color: 'hsl(231 98% 65%)', name: '天蓝色' },
  { color: 'hsl(161 90% 43%)', name: '浅绿色' },
  { color: 'hsl(181 84% 32%)', name: '深绿色' },
  { color: 'hsl(42 84% 61%)', name: '柠檬黄' },
  { color: 'hsl(18 89% 40%)', name: '橙黄色' },
  { color: 'hsl(347 77% 60%)', name: '樱花粉' },
];

const switchTheme = (preset: { color: string }) => {
  onColorPickerChange(preset.color);
};

const isActiveTheme = (color: string) => {
  return getHexColor(color) === getThemeConfig.value.primary;
};

const toggleDark = (e: MouseEvent) => {
  const isDark = getThemeConfig.value.isIsDark;
  const nextTheme = isDark ? 'light' : 'dark';

  if (!document.startViewTransition) {
    onAddDarkChange(nextTheme);
    return;
  }

  const transition = document.startViewTransition(() => {
    onAddDarkChange(nextTheme);
  });

  transition.ready.then(() => {
    const { clientX, clientY } = e;
    const radius = Math.hypot(
      Math.max(clientX, innerWidth - clientX),
      Math.max(clientY, innerHeight - clientY)
    );
    document.documentElement.animate(
      {
        clipPath: [
          `circle(0% at ${clientX}px ${clientY}px)`,
          `circle(${radius}px at ${clientX}px ${clientY}px)`,
        ],
      },
      {
        duration: 500,
        easing: 'ease-in-out',
        pseudoElement: '::view-transition-new(root)',
      }
    );
  });
};

onMounted(() => {
  // 确保默认/缓存的 primary 写入 CSS 变量（避免色点已选中但按钮仍是 Element 默认蓝）
  if (getThemeConfig.value.primary) {
    onColorPickerChange(getThemeConfig.value.primary);
  }
  NextLoading.done();
});
</script>

<style scoped lang="scss">
.login {
  box-sizing: border-box;
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: var(--el-bg-color);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

.right-wrap {
  position: relative;
  flex: 1;
  height: 100%;
  background: var(--el-bg-color);
}

.login-toolbar {
  position: fixed;
  top: 20px;
  right: 24px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 24px;
  background: var(--el-bg-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.theme-colors {
  display: flex;
  align-items: center;
  gap: 6px;
}

.theme-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.15s, box-shadow 0.15s;

  &:hover {
    transform: scale(1.12);
  }

  &.active {
    box-shadow: 0 0 0 2px var(--el-bg-color), 0 0 0 3.5px currentColor;
  }

  .theme-dot-check {
    color: #fff;
    font-size: 12px;
  }
}

.theme-custom-picker {
  :deep(.el-color-picker__trigger) {
    width: 22px;
    height: 22px;
    padding: 0;
    border: none;
    border-radius: 50%;
  }

  :deep(.el-color-picker__color) {
    border: none;
    border-radius: 50%;
  }

  :deep(.el-color-picker__icon) {
    display: none;
  }
}

.dark-toggle {
  width: 28px;
  height: 28px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: var(--el-text-color-regular);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: color 0.2s, background 0.2s;

  &:hover {
    color: var(--el-color-primary);
    background: var(--el-fill-color-light);
  }
}

.login-wrap {
  position: absolute;
  top: 49%;
  right: 0;
  left: 0;
  width: 440px;
  margin: 0 auto;
  padding: 0 5px;
  opacity: 0;
  transform: translateY(-50%) translateX(24px);
  animation: slideInRight 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

.form {
  box-sizing: border-box;
  padding: 24px 0 40px;

  .title {
    margin: 0;
    font-size: 34px;
    font-weight: 600;
    line-height: 1.3;
    color: var(--el-text-color-primary);
    letter-spacing: -0.02em;

    .wave {
      display: inline-block;
      margin-left: 2px;
      font-size: 30px;
      line-height: 1;
      transform-origin: 70% 70%;
      animation: wave-hand 2.4s ease-in-out infinite;
    }
  }

  .sub-title {
    margin: 10px 0 0;
    font-size: 14px;
    line-height: 1.5;
    color: var(--el-text-color-regular);
  }

  .form-body {
    margin-top: 28px;
  }

  :deep(.login-content-form) {
    margin-top: 0;
  }

  :deep(.el-input__wrapper) {
    border-radius: 8px;
    box-shadow: none !important;
    border: 1px solid var(--el-border-color);
    transition: border-color 0.2s;

    &:hover {
      border-color: var(--el-color-primary-light-3);
    }

    &.is-focus {
      border-color: var(--el-color-primary);
    }
  }

  :deep(.el-form-item) {
    margin-bottom: 20px;
  }

  :deep(.el-input) {
    --el-input-height: 40px;
  }

  :deep(.login-content-submit) {
    width: 100%;
    height: 40px;
    margin-top: 8px;
    border: 0;
    border-radius: 8px;
    font-size: 15px;
    font-weight: 500;
    letter-spacing: 2px;
  }

  :deep(.oauth-login) {
    margin-top: 8px;
  }
}

.login-copyright {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);

  a {
    color: inherit;
    text-decoration: none;

    &:hover {
      color: var(--el-color-primary);
    }
  }

  .sep {
    opacity: 0.5;
  }
}

@media (max-width: 1024px) {
  .login {
    .login-wrap {
      position: relative;
      top: auto;
      width: min(440px, 100%);
      margin: 12vh auto 0;
      opacity: 1;
      transform: none;
      animation: none;
    }

    .login-copyright {
      position: static;
      margin: 32px 0 24px;
    }
  }
}

@media (max-width: 768px) {
  .right-wrap {
    box-sizing: border-box;
    width: 100%;
    padding: 0 24px;
  }

  .login-wrap {
    width: 100%;
  }

  .login-toolbar {
    top: 12px;
    right: 12px;
    padding: 4px 8px;
    gap: 4px;
  }

  .theme-dot {
    width: 18px;
    height: 18px;
  }

  .theme-custom-picker {
    :deep(.el-color-picker__trigger) {
      width: 18px;
      height: 18px;
    }
  }

  .dark-toggle {
    width: 24px;
    height: 24px;
    font-size: 14px;
  }

  .form .title {
    font-size: 28px;
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateY(-50%) translateX(24px);
  }
  to {
    opacity: 1;
    transform: translateY(-50%) translateX(0);
  }
}

@keyframes wave-hand {
  0%,
  60%,
  100% {
    transform: rotate(0deg);
  }
  10%,
  30% {
    transform: rotate(14deg);
  }
  20%,
  40% {
    transform: rotate(-8deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .form .title .wave {
    animation: none;
  }
}

:global(::view-transition-new(root)),
:global(::view-transition-old(root)) {
  animation: none;
  mix-blend-mode: normal;
}
:global(::view-transition-new(root)) {
  z-index: 9999;
}
:global(::view-transition-old(root)) {
  z-index: 1;
}
</style>
