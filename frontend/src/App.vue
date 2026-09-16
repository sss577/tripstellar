<template>
  <div id="app">
    <a-layout style="min-height: 100vh">
      <!-- <a-layout-header v-if="!isLandingRoute" class="app-header">
        <div class="header-inner">
          <div class="header-brand" @click="$router.push('/')">
            <div class="brand-logo">
              <span class="logo-icon"></span>
              <div class="logo-ring"></div>
            </div>
            <div class="brand-text-group">
              <span class="brand-text">{{ t('app.brand') }}</span>
              <span class="brand-sub">{{ t('app.subBrand') }}</span>
            </div>
          </div>
          <div class="header-right">
            <a-select
              v-model:value="locale"
              class="lang-select"
              size="small"
              :aria-label="t('app.language.label')"
            >
              <a-select-option value="zh-CN">{{ t('app.language.zh') }}</a-select-option>
              <a-select-option value="ja-JP">{{ t('app.language.ja') }}</a-select-option>
              <a-select-option value="en-US">{{ t('app.language.en') }}</a-select-option>
            </a-select>
            <div class="header-badge">
              <span class="badge-dot"></span>
              <span>{{ t('app.badge') }}</span>
            </div>
          </div>
        </div>
      </a-layout-header> -->
      <a-layout-content style="padding: 0">
        <router-view />
      </a-layout-content>
      <!-- <a-layout-footer v-if="!isLandingRoute" class="app-footer">
        <div class="footer-inner">
          <div class="footer-left">
            <span class="footer-brand">{{ t('app.footerBrand') }}</span>
            <span class="footer-copy">{{ t('app.footerCopy', { year }) }}</span>
          </div>
          <div class="footer-right">
            <span class="footer-tech">{{ t('app.footerTech') }}</span>
          </div>
        </div>
      </a-layout-footer> -->
    </a-layout>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { setAppLocale, type AppLocale } from '@/i18n'

const { t, locale } = useI18n()

watch(
  locale,
  (nextLocale) => {
    setAppLocale(nextLocale as AppLocale)
    document.title = t('app.title')
  },
  { immediate: true }
)
</script>

<style>
/* 字体族已在 index.html 预加载，此处只声明字栈，避免重复请求 */
* {
  box-sizing: border-box;
}

#app {
  font-family: var(--ts-font-sans);
  font-size: 15px;
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--ts-paper);
  color: var(--ts-ink-2);
  font-feature-settings: 'kern' 1, 'liga' 1;
  text-rendering: optimizeLegibility;
}

.app-header {
  background: rgba(250, 248, 244, 0.88) !important;
  padding: 0 48px !important;
  height: 72px !important;
  line-height: 72px !important;
  border-bottom: 1px solid var(--ts-rule);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(20px);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: opacity 0.3s var(--ts-ease);
}

.header-brand:hover {
  opacity: 0.72;
}

.brand-logo {
  position: relative;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon {
  font-size: 28px;
  z-index: 1;
  filter: drop-shadow(0 0 8px rgba(176, 67, 31, 0.35));
}

.logo-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1px solid var(--ts-rule-strong);
  animation: ringPulse 3s ease-in-out infinite;
}

@keyframes ringPulse {
  0%, 100% { transform: scale(1); opacity: 0.4; }
  50% { transform: scale(1.15); opacity: 0.8; }
}

.brand-text-group {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.brand-text {
  font-family: var(--ts-font-serif);
  color: var(--ts-ink);
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.brand-sub {
  color: var(--ts-ink-3);
  font-size: 11px;
  font-weight: 400;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.lang-select {
  width: 120px;
}

.lang-select .ant-select-selector {
  background: var(--ts-card) !important;
  border: 1px solid var(--ts-rule) !important;
  border-radius: var(--ts-r-sm) !important;
  color: var(--ts-ink-2) !important;
}

.lang-select .ant-select-selection-item {
  color: var(--ts-ink-2) !important;
  font-size: 12px;
}

.lang-select .ant-select-arrow {
  color: var(--ts-ink-3) !important;
}

.header-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: 1px solid var(--ts-rule-strong);
  color: var(--ts-accent);
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  padding: 6px 16px;
  border-radius: var(--ts-r-sm);
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
  line-height: 1.2;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--ts-accent);
  animation: dotBlink 2s ease-in-out infinite;
}

@keyframes dotBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

.app-footer {
  background: var(--ts-paper-2) !important;
  padding: 24px 48px !important;
  border-top: 1px solid var(--ts-rule);
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: var(--ts-measure);
  margin: 0 auto;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.footer-brand {
  font-family: var(--ts-font-serif);
  color: var(--ts-ink);
  font-size: 15px;
  font-weight: 700;
}

.footer-copy {
  color: var(--ts-ink-3);
  font-size: 12px;
}

.footer-right {
  display: flex;
  align-items: center;
}

.footer-tech {
  color: var(--ts-ink-3);
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 400;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
</style>
