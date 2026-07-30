<template>
  <div class="login-left-view">
    <div class="logo">
      <img :src="logos.mini" alt="Logo" class="logo-img" />
      <h1 class="logo-title">{{ getThemeConfig.globalTitle }}</h1>
    </div>

    <div class="left-img">
      <LoginAnimatedIllustration />
    </div>

    <div class="text-wrap">
      <h1>全栈自动化测试平台</h1>
      <p>接口 · UI · APP · AI 测试一体化，让质量交付更高效</p>
    </div>

    <div class="geometric-decorations" aria-hidden="true">
      <div class="geo-element circle-outline"></div>
      <div class="geo-element square-rotated"></div>
      <div class="geo-element circle-small"></div>
      <div class="geo-element square-bottom-right"></div>
      <div class="geo-element bg-bubble"></div>
      <div class="geo-element circle-top-right" :class="{ dark: getThemeConfig.isIsDark }"></div>
      <div class="geo-element dot dot-top-left"></div>
      <div class="geo-element dot dot-top-right"></div>
      <div class="geo-element dot dot-center-right"></div>
      <div class="squares-group">
        <i class="geo-element square square-a"></i>
        <i class="geo-element square square-b"></i>
        <i class="geo-element square square-c"></i>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" name="LoginLeftView">
import { computed, defineAsyncComponent } from 'vue';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
import { logos } from '/@/config/assets';

const LoginAnimatedIllustration = defineAsyncComponent(
  () => import('/@/views/login/component/LoginAnimatedIllustration.vue')
);

const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);
const getThemeConfig = computed(() => themeConfig.value);
</script>

<style lang="scss" scoped>
.login-left-view {
  position: relative;
  box-sizing: border-box;
  width: 65vw;
  height: 100%;
  padding: 20px 24px;
  overflow: hidden;
  background: color-mix(in srgb, var(--el-color-primary-light-9) 72%, #ffffff);

  .logo {
    position: relative;
    z-index: 20;
    display: flex;
    align-items: center;
    gap: 10px;

    .logo-img {
      width: 40px;
      height: 40px;
      object-fit: contain;
    }

    .logo-title {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      letter-spacing: 0.2px;
    }
  }

  .left-img {
    position: absolute;
    inset: 0 0 12%;
    z-index: 10;
    width: min(420px, 42%);
    margin: auto;
    animation: slideInLeft 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
  }

  .text-wrap {
    position: absolute;
    bottom: 72px;
    left: 0;
    z-index: 12;
    width: 100%;
    text-align: center;
    animation: slideInLeft 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;

    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    p {
      margin: 10px 0 0;
      font-size: 14px;
      line-height: 1.6;
      color: var(--el-text-color-regular);
    }
  }

  .geo-element {
    position: absolute;
    pointer-events: none;
  }

  .circle-outline {
    top: 10%;
    left: 25%;
    width: 42px;
    height: 42px;
    border: 2px solid var(--el-color-primary-light-7);
    border-radius: 50%;
  }

  .square-rotated {
    top: 50%;
    left: 16%;
    width: 56px;
    height: 56px;
    background: color-mix(in srgb, var(--el-color-primary-light-8) 70%, transparent);
    transform: rotate(-25deg);
  }

  .circle-small {
    bottom: 26%;
    left: 30%;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--el-color-primary-light-7);
  }

  .square-bottom-right {
    right: 10%;
    bottom: 10%;
    width: 48px;
    height: 48px;
    background: var(--el-color-primary-light-8);
    transform: rotate(45deg);
  }

  .bg-bubble {
    top: -120px;
    right: -120px;
    width: 360px;
    height: 360px;
    border-radius: 50%;
    background: color-mix(in srgb, var(--el-color-primary-light-8) 28%, transparent);
  }

  .circle-top-right {
    top: 3%;
    right: 3%;
    z-index: 30;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    pointer-events: none;
    background: color-mix(in srgb, var(--el-color-primary-light-7) 55%, var(--el-bg-color));
    transition: box-shadow 0.3s, transform 0.3s;

    &::after {
      content: '';
      position: absolute;
      inset: 0;
      border-radius: 50%;
      background: linear-gradient(to right, #fcbb04, #fffc00);
      opacity: 0.85;
    }

    &.dark {
      box-shadow: inset 0 0 22px #333;
      transform: rotate(-48deg);

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 14px;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: color-mix(in srgb, var(--el-color-primary-light-9) 70%, #111);
      }

      &::after {
        display: none;
      }
    }
  }

  .dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--el-color-primary-light-7);
  }

  .dot-top-left {
    top: 140px;
    left: 100px;
  }

  .dot-top-right {
    top: 140px;
    right: 120px;
  }

  .dot-center-right {
    top: 46%;
    right: 22%;
    background: var(--el-color-primary-light-8);
  }

  .squares-group {
    position: absolute;
    bottom: 18px;
    left: 20px;
    width: 140px;
    height: 140px;

    .square {
      position: absolute;
      display: block;
      border-radius: 8px;
    }

    .square-a {
      top: 12px;
      left: 30px;
      width: 50px;
      height: 50px;
      background: color-mix(in srgb, var(--el-color-primary) 30%, transparent);
    }

    .square-b {
      top: 30px;
      left: 48px;
      width: 70px;
      height: 70px;
      background: color-mix(in srgb, var(--el-color-primary) 15%, transparent);
    }

    .square-c {
      top: 66px;
      left: 86px;
      width: 32px;
      height: 32px;
      background: color-mix(in srgb, var(--el-color-primary) 45%, transparent);
    }
  }
}

[data-theme='dark'] .login-left-view {
  background: color-mix(in srgb, var(--el-color-primary-light-9) 35%, #0b0d12);
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-28px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@media (max-width: 1024px) {
  .login-left-view {
    width: auto;
    height: auto;
    padding: 0;
    background: transparent !important;

    .left-img,
    .text-wrap,
    .geometric-decorations {
      display: none;
    }

    .logo {
      position: fixed;
      top: 16px;
      left: 20px;
      z-index: 1000;
    }
  }
}

@media (max-width: 768px) {
  .login-left-view {
    display: none;
  }
}
</style>