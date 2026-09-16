<template>
  <div class="login-page">
    <!-- 视频背景：鲸鲨穿过鱼群，铺满全屏循环播放（本地文件，避免外网 CDN 卡顿） -->
    <video
      ref="videoRef"
      class="login-video"
      autoplay
      muted
      loop
      playsinline
      preload="auto"
      src="/videos/whale-fish.mp4"
    ></video>
    <!-- 暗角（四角逐暗）+ 顶部/底部黑色渐变 -->
    <div class="login-overlay"></div>

    <nav class="login-navbar">
      <button class="login-brand" type="button">TripStellar</button>
      <a-select
        v-model:value="locale"
        class="login-lang-select"
        size="small"
        :aria-label="t('app.language.label')"
      >
        <a-select-option value="zh-CN">{{ t('app.language.zh') }}</a-select-option>
        <a-select-option value="ja-JP">{{ t('app.language.ja') }}</a-select-option>
        <a-select-option value="en-US">{{ t('app.language.en') }}</a-select-option>
      </a-select>
    </nav>

    <div class="login-magazine">
      <!-- 左栏：杂志封面排版 -->
      <div class="mag-cover">
        <div class="mag-meta">
          <span>{{ magazineDate }}</span>
          <span>{{ t('auth.magazine.issue') }}</span>
        </div>
        <h1 class="mag-masthead">TripStellar</h1>
        <div class="mag-rule"></div>
        <p class="mag-deck">{{ t('auth.magazine.deck') }}</p>
        <p class="mag-tagline">{{ t('auth.magazine.tagline') }}</p>
        <div class="mag-footer">
          <span>AI TRAVEL PLANNING ENGINE</span>
          <span>{{ t('auth.magazine.edition') }}</span>
        </div>
      </div>

      <!-- 右栏：登录/注册表单 -->
      <div class="login-card">
      <div class="login-head">
        <p class="login-eyebrow">{{ t('auth.brandBadge') }}</p>
        <h1 class="login-title">{{ activeTab === 'login' ? t('auth.loginTitle') : t('auth.registerTitle') }}</h1>
        <p class="login-subtitle">
          {{ activeTab === 'login' ? t('auth.loginSubtitle') : t('auth.registerSubtitle') }}
        </p>
      </div>

      <a-tabs v-model:activeKey="activeTab" class="login-tabs" :animated="false">
        <a-tab-pane key="login" :tab="t('auth.tab.login')">
          <a-form layout="vertical" class="login-form" @submit.prevent>
            <a-form-item>
              <template #label><span class="field-label">{{ t('auth.account') }}</span></template>
              <a-input
                v-model:value="loginForm.account"
                size="large"
                :placeholder="t('auth.accountPlaceholder')"
                allow-clear
                @pressEnter="handleLogin"
              />
            </a-form-item>
            <a-form-item>
              <template #label><span class="field-label">{{ t('auth.password') }}</span></template>
              <a-input-password
                v-model:value="loginForm.password"
                size="large"
                :placeholder="t('auth.passwordPlaceholder')"
                @pressEnter="handleLogin"
              />
            </a-form-item>
            <button
              type="submit"
              class="login-submit"
              :disabled="submitting"
              @click="handleLogin"
            >
              <span v-if="submitting" class="login-spinner"></span>
              {{ submitting ? t('common.loading') : t('auth.submitLogin') }}
            </button>
          </a-form>
        </a-tab-pane>

        <a-tab-pane key="register" :tab="t('auth.tab.register')">
          <a-form layout="vertical" class="login-form" @submit.prevent>
            <a-form-item>
              <template #label><span class="field-label">{{ t('auth.username') }}</span></template>
              <a-input
                v-model:value="registerForm.username"
                size="large"
                :placeholder="t('auth.usernamePlaceholder')"
                allow-clear
              />
            </a-form-item>
            <a-form-item>
              <template #label><span class="field-label">{{ t('auth.email') }}</span></template>
              <a-input
                v-model:value="registerForm.email"
                size="large"
                :placeholder="t('auth.emailPlaceholder')"
                allow-clear
              />
            </a-form-item>
            <a-form-item>
              <template #label><span class="field-label">{{ t('auth.password') }}</span></template>
              <a-input-password
                v-model:value="registerForm.password"
                size="large"
                :placeholder="t('auth.passwordPlaceholder')"
              />
            </a-form-item>
            <a-form-item>
              <template #label><span class="field-label">{{ t('auth.confirmPassword') }}</span></template>
              <a-input-password
                v-model:value="registerForm.confirmPassword"
                size="large"
                :placeholder="t('auth.confirmPasswordPlaceholder')"
                @pressEnter="handleRegister"
              />
            </a-form-item>
            <button
              type="submit"
              class="login-submit"
              :disabled="submitting"
              @click="handleRegister"
            >
              <span v-if="submitting" class="login-spinner"></span>
              {{ submitting ? t('common.loading') : t('auth.submitRegister') }}
            </button>
          </a-form>
        </a-tab-pane>
      </a-tabs>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import { login, register } from '@/services/auth'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()

const activeTab = ref<'login' | 'register'>('login')
const submitting = ref(false)

// 视频背景：autoplay 被浏览器策略拦截时主动播放
const videoRef = ref<HTMLVideoElement | null>(null)

onMounted(() => {
  videoRef.value?.play().catch(() => undefined)
})

// 杂志封面日期：按当前语言输出年月（如 2026 / 08）
const magazineDate = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  if (locale.value === 'zh-CN') return `${year} 年 ${month} 月`
  if (locale.value === 'ja-JP') return `${year} 年 ${month} 月号`
  return `${year} / ${month}`
})

const loginForm = reactive({ account: '', password: '' })
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const redirectAfterAuth = () => {
  const redirect = typeof route.query.redirect === 'string' && route.query.redirect.startsWith('/')
    ? route.query.redirect
    : '/'
  router.replace(redirect)
}

const handleLogin = async () => {
  if (submitting.value) return
  if (!loginForm.account.trim()) {
    message.error(t('auth.errors.accountRequired'))
    return
  }
  if (!loginForm.password) {
    message.error(t('auth.errors.passwordRequired'))
    return
  }

  submitting.value = true
  try {
    await login({ account: loginForm.account.trim(), password: loginForm.password })
    message.success(t('auth.loginSuccess'))
    redirectAfterAuth()
  } catch (error: any) {
    message.error(error?.message || t('auth.loginFailed'))
  } finally {
    submitting.value = false
  }
}

const handleRegister = async () => {
  if (submitting.value) return
  const username = registerForm.username.trim()
  if (username.length < 3 || username.length > 50) {
    message.error(t('auth.errors.usernameLength'))
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email.trim())) {
    message.error(t('auth.errors.emailInvalid'))
    return
  }
  if (registerForm.password.length < 8) {
    message.error(t('auth.errors.passwordLength'))
    return
  }
  if (registerForm.password !== registerForm.confirmPassword) {
    message.error(t('auth.errors.confirmMismatch'))
    return
  }

  submitting.value = true
  try {
    await register({
      username,
      email: registerForm.email.trim(),
      password: registerForm.password,
    })
    message.success(t('auth.registerSuccess'))
    redirectAfterAuth()
  } catch (error: any) {
    message.error(error?.message || t('auth.registerFailed'))
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 96px 40px 48px;
  /* 视频加载失败时的兜底背景 */
  background: linear-gradient(135deg, #0a0a0f 0%, #0d1626 45%, #08131f 100%);
  font-family: 'Outfit', 'Inter', -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
  overflow: hidden;
}

/* 视频背景：铺满全屏、循环 */
.login-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

/* 暗角（四角边缘逐暗）+ 顶部/底部黑色渐变 */
.login-overlay {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse 130% 100% at 50% 50%, transparent 42%, rgba(0, 0, 0, 0.34) 74%, rgba(0, 0, 0, 0.68) 100%),
    linear-gradient(to bottom, rgba(3, 5, 10, 0.78) 0%, transparent 22%),
    linear-gradient(to top, rgba(3, 5, 10, 0.82) 0%, transparent 26%);
}

.login-navbar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22px 28px;
  z-index: 2;
}

.login-brand {
  background: transparent;
  border: 0;
  color: #f4f8fc;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 13px;
  cursor: default;
}

.login-lang-select {
  width: 110px;
}

.login-lang-select :deep(.ant-select-selector) {
  height: 34px !important;
  padding: 0 12px !important;
  border: 1.2px solid rgba(236, 243, 250, 0.24) !important;
  background: rgba(12, 23, 32, 0.56) !important;
  border-radius: 999px !important;
  display: flex !important;
  align-items: center !important;
}

.login-lang-select :deep(.ant-select-selection-item),
.login-lang-select :deep(.ant-select-arrow) {
  color: #ecf3fa !important;
  font-size: 12px;
}

/* 杂志封面分栏：左刊头 + 右表单 */
.login-magazine {
  position: relative;
  z-index: 1;
  flex: 1;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  align-items: center;
  gap: clamp(32px, 6vw, 96px);
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 0;
}

/* 宽屏：左栏再展开一档，把登录卡片推到右侧；同时放宽整体宽度让刊头有舒展空间 */
@media (min-width: 1200px) {
  .login-magazine {
    grid-template-columns: 1.5fr 1fr;
    max-width: 1280px;
  }

  .mag-masthead {
    font-size: clamp(56px, 5vw, 84px);
  }

  /* 卡片在右栏里居中，而不是贴左，进一步右移 */
  .login-card {
    justify-self: center;
  }
}

.mag-cover {
  display: flex;
  flex-direction: column;
  min-height: 420px;
}

.mag-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #ffd699;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  padding-bottom: 18px;
  border-bottom: 1px solid rgba(236, 243, 250, 0.18);
}

.mag-masthead {
  color: #f4f8fc;
  font-family: 'Montserrat', 'Outfit', -apple-system, 'Segoe UI', sans-serif;
  /* TripStellar 比原来的 TRIP-STAR 长两个字，收小字号保证刊头在左栏内单行不折 */
  font-size: clamp(40px, 4.8vw, 74px);
  font-weight: 900;
  line-height: 0.98;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  margin: 26px 0 0;
  text-shadow: 0 6px 40px rgba(0, 0, 0, 0.55);
}

.mag-rule {
  height: 1px;
  margin: 30px 0 24px;
  background: linear-gradient(to right, transparent, rgba(255, 214, 153, 0.85), transparent);
}

.mag-deck {
  color: rgba(244, 248, 252, 0.85);
  font-family: 'Playfair Display', Georgia, 'Times New Roman', serif;
  font-style: italic;
  font-size: clamp(18px, 2vw, 23px);
  line-height: 1.55;
  margin: 0 0 18px;
  max-width: 30ch;
}

.mag-tagline {
  color: rgba(236, 243, 250, 0.55);
  font-size: 14px;
  line-height: 1.8;
  margin: 0;
  max-width: 42ch;
}

.mag-footer {
  margin-top: auto;
  padding-top: 26px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: rgba(236, 243, 250, 0.4);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.26em;
  text-transform: uppercase;
}

/* 右栏：登录表单玻璃卡片 */
.login-card {
  position: relative;
  width: 100%;
  max-width: 400px;
  padding: 36px 36px 30px;
  border-radius: 28px;
  background: rgba(5, 10, 18, 0.66);
  border: 1px solid rgba(255, 179, 71, 0.18);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
  z-index: 1;
}

.login-head {
  text-align: center;
  margin-bottom: 6px;
}

.login-eyebrow {
  color: #ffd699;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.login-title {
  color: #f4f8fc;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 0.02em;
  margin: 0 0 8px;
}

.login-subtitle {
  color: rgba(236, 243, 250, 0.55);
  font-size: 13px;
  margin: 0;
}

.login-tabs {
  margin-top: 10px;
}

.login-tabs :deep(.ant-tabs-nav) {
  margin-bottom: 20px;
}

.login-tabs :deep(.ant-tabs-tab) {
  padding: 10px 4px;
  margin: 0 14px 0 0;
}

.login-tabs :deep(.ant-tabs-tab-btn) {
  color: rgba(236, 243, 250, 0.55);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.login-tabs :deep(.ant-tabs-tab-active .ant-tabs-tab-btn) {
  color: #ffd699 !important;
}

.login-tabs :deep(.ant-tabs-ink-bar) {
  background: #ffb347;
}

.login-form :deep(.ant-form-item) {
  margin-bottom: 16px;
}

.field-label {
  color: rgba(236, 243, 250, 0.72);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
}

.login-form :deep(.ant-input-affix-wrapper),
.login-form :deep(.ant-input) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1.2px solid rgba(236, 243, 250, 0.16) !important;
  border-radius: 999px !important;
  color: #ecf3fa !important;
  padding: 6px 18px;
}

.login-form :deep(.ant-input::placeholder),
.login-form :deep(.ant-input-affix-wrapper ::placeholder) {
  color: rgba(236, 243, 250, 0.32) !important;
}

.login-form :deep(.ant-input-password-icon) {
  color: rgba(255, 214, 153, 0.65) !important;
}

.login-form :deep(.ant-form-item-label) {
  padding-bottom: 4px;
}

.login-submit {
  width: 100%;
  min-height: 44px;
  margin-top: 8px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #ffb347 0%, #ffd699 100%);
  color: #1a1035;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.login-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 30px rgba(255, 179, 71, 0.35);
}

.login-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(26, 16, 53, 0.35);
  border-top-color: #1a1035;
  border-radius: 50%;
  animation: loginSpin 0.8s linear infinite;
}

@keyframes loginSpin {
  to { transform: rotate(360deg); }
}

/* 响应式：窄屏时杂志刊头居中在上、表单移到下方 */
@media (max-width: 960px) {
  .login-page {
    padding: 84px 20px 40px;
  }

  .login-magazine {
    grid-template-columns: 1fr;
    gap: 36px;
    align-items: start;
  }

  .mag-cover {
    min-height: 0;
    text-align: center;
  }

  .mag-masthead {
    font-size: clamp(30px, 9vw, 58px);
    margin-top: 18px;
  }

  .mag-rule {
    margin: 22px auto 18px;
    width: 72%;
  }

  .mag-deck,
  .mag-tagline {
    margin-left: auto;
    margin-right: auto;
  }

  .mag-footer {
    display: none;
  }

  .login-card {
    max-width: 420px;
    margin: 0 auto;
  }
}

@media (max-width: 520px) {
  .login-page {
    padding: 76px 14px 32px;
  }

  .login-card {
    padding: 28px 22px 24px;
  }

  .login-navbar {
    padding: 16px 18px;
  }
}
</style>
