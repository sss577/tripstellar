<template>
  <div class="profile-page">
    <div class="profile-bg-shade"></div>

    <nav class="profile-navbar">
      <button class="profile-brand" type="button" @click="goHome">TripStellar</button>
      <div class="profile-nav-actions">
        <button type="button" class="profile-back-btn" @click="goHome">
          {{ t('profile.back') }}
        </button>
        <button type="button" class="profile-logout-btn" @click="handleLogout">
          {{ t('nav.user.logout') }}
        </button>
      </div>
    </nav>

    <div class="profile-container">
      <!-- 用户信息卡 -->
      <section class="profile-card profile-hero-card">
        <div class="profile-avatar">
          <img v-if="avatarPreview" :src="avatarPreview" alt="avatar" @error="avatarPreview = ''" />
          <span v-else class="avatar-fallback">{{ avatarFallback }}</span>
        </div>
        <div class="profile-hero-info">
          <h2 class="profile-nickname">{{ authState.user?.nickname || authState.user?.username }}</h2>
          <p class="profile-username">@{{ authState.user?.username }}</p>
          <div class="profile-meta">
            <span class="meta-item">
              <span class="meta-label">{{ t('profile.email') }}</span>
              <span class="meta-value">{{ authState.user?.email }}</span>
            </span>
            <span class="meta-item">
              <span class="meta-label">{{ t('profile.joinedAt') }}</span>
              <span class="meta-value">{{ joinedAtText }}</span>
            </span>
          </div>
        </div>
      </section>

      <!-- 修改资料 -->
      <section class="profile-card">
        <h3 class="profile-section-title">{{ t('profile.sectionInfo') }}</h3>
        <a-form layout="vertical" class="profile-form" @submit.prevent>
          <a-form-item>
            <template #label><span class="field-label">{{ t('profile.nickname') }}</span></template>
            <a-input
              v-model:value="profileForm.nickname"
              size="large"
              :placeholder="t('profile.nicknamePlaceholder')"
              allow-clear
            />
          </a-form-item>
          <a-form-item>
            <template #label><span class="field-label">{{ t('profile.avatarUrl') }}</span></template>
            <a-input
              v-model:value="profileForm.avatar_url"
              size="large"
              :placeholder="t('profile.avatarUrlPlaceholder')"
              allow-clear
            />
          </a-form-item>
          <button
            type="submit"
            class="profile-submit"
            :disabled="savingProfile"
            @click="handleSaveProfile"
          >
            {{ savingProfile ? t('common.loading') : t('profile.save') }}
          </button>
        </a-form>
      </section>

      <!-- 修改密码 -->
      <section class="profile-card">
        <h3 class="profile-section-title">{{ t('profile.sectionPassword') }}</h3>
        <a-form layout="vertical" class="profile-form" @submit.prevent>
          <a-form-item>
            <template #label><span class="field-label">{{ t('profile.oldPassword') }}</span></template>
            <a-input-password v-model:value="passwordForm.oldPassword" size="large" />
          </a-form-item>
          <a-form-item>
            <template #label><span class="field-label">{{ t('profile.newPassword') }}</span></template>
            <a-input-password v-model:value="passwordForm.newPassword" size="large" />
          </a-form-item>
          <a-form-item>
            <template #label><span class="field-label">{{ t('profile.confirmNewPassword') }}</span></template>
            <a-input-password
              v-model:value="passwordForm.confirmPassword"
              size="large"
              @pressEnter="handleChangePassword"
            />
          </a-form-item>
          <button
            type="submit"
            class="profile-submit profile-submit-outline"
            :disabled="changingPassword"
            @click="handleChangePassword"
          >
            {{ changingPassword ? t('common.loading') : t('profile.submitPassword') }}
          </button>
        </a-form>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import { authState, changePassword, logout, updateProfile } from '@/services/auth'

const router = useRouter()
const { t } = useI18n()

const savingProfile = ref(false)
const changingPassword = ref(false)
const avatarPreview = ref('')

const profileForm = reactive({ nickname: '', avatar_url: '' })
const passwordForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })

const avatarFallback = computed(() => {
  const name = authState.user?.nickname || authState.user?.username || '?'
  return name.slice(0, 1).toUpperCase()
})

const joinedAtText = computed(() => {
  const raw = authState.user?.created_at
  if (!raw) return ''
  const date = new Date(raw)
  return Number.isNaN(date.getTime()) ? raw : date.toLocaleDateString()
})

watch(
  () => authState.user,
  (user) => {
    profileForm.nickname = user?.nickname || ''
    profileForm.avatar_url = user?.avatar_url || ''
    avatarPreview.value = user?.avatar_url || ''
  },
  { immediate: true }
)

watch(
  () => profileForm.avatar_url,
  (value) => {
    avatarPreview.value = value.trim()
  }
)

const goHome = () => router.push('/')

const handleLogout = async () => {
  try {
    await logout()
    message.success(t('nav.user.loggedOut'))
  } catch {
    // 后端吊销失败不影响本地登出
  }
  router.push('/login')
}

const handleSaveProfile = async () => {
  if (savingProfile.value) return
  savingProfile.value = true
  try {
    await updateProfile({
      nickname: profileForm.nickname.trim(),
      avatar_url: profileForm.avatar_url.trim(),
    })
    message.success(t('profile.saved'))
  } catch (error: any) {
    message.error(error?.message || t('profile.saveFailed'))
  } finally {
    savingProfile.value = false
  }
}

const handleChangePassword = async () => {
  if (changingPassword.value) return
  if (!passwordForm.oldPassword) {
    message.error(t('profile.errors.oldPasswordRequired'))
    return
  }
  if (passwordForm.newPassword.length < 8) {
    message.error(t('profile.errors.newPasswordLength'))
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    message.error(t('profile.errors.confirmMismatch'))
    return
  }

  changingPassword.value = true
  try {
    await changePassword(passwordForm.oldPassword, passwordForm.newPassword)
    message.success(t('profile.passwordChanged'))
    router.replace('/login')
  } catch (error: any) {
    message.error(error?.message || t('profile.passwordChangeFailed'))
  } finally {
    changingPassword.value = false
  }
}

onMounted(() => {
  // 守卫已保证登录态，这里仅做兜底
  if (!authState.user) {
    router.replace('/login')
  }
})
</script>

<style scoped>
.profile-page {
  position: relative;
  min-height: 100vh;
  padding: 0 20px 80px;
  background: var(--ts-paper);
  font-family: var(--ts-font-sans);
  overflow: hidden;
}

/* 去掉暖调光晕，改为极淡的纸面渐变 */
.profile-bg-shade {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 70% 50% at 78% 0%, rgba(26, 24, 20, 0.035), transparent 68%),
    radial-gradient(ellipse 60% 45% at 12% 100%, rgba(176, 67, 31, 0.035), transparent 68%);
  pointer-events: none;
}

.profile-navbar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: var(--ts-measure-narrow);
  margin: 0 auto;
  padding: 44px 0 22px;
  border-bottom: 1px solid var(--ts-rule-strong);
  z-index: 2;
}

.profile-brand {
  background: transparent;
  border: 0;
  color: var(--ts-ink);
  font-family: var(--ts-font-serif);
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  font-size: 16px;
  cursor: pointer;
  transition: color 0.25s var(--ts-ease);
}

.profile-brand:hover {
  color: var(--ts-accent);
}

.profile-back-btn {
  border: 1px solid var(--ts-rule-strong);
  background: transparent;
  color: var(--ts-ink-2);
  border-radius: var(--ts-r-sm);
  padding: 0 16px;
  min-height: 32px;
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
  cursor: pointer;
  transition: border-color 0.25s var(--ts-ease), color 0.25s var(--ts-ease);
}

.profile-back-btn:hover {
  border-color: var(--ts-accent);
  color: var(--ts-accent);
}

.profile-nav-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.profile-logout-btn {
  border: 1px solid var(--ts-rule-strong);
  background: transparent;
  color: var(--ts-danger);
  border-radius: var(--ts-r-sm);
  padding: 0 16px;
  min-height: 32px;
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
  cursor: pointer;
  transition: border-color 0.25s var(--ts-ease), background 0.25s var(--ts-ease);
}

.profile-logout-btn:hover {
  border-color: var(--ts-danger);
  background: rgba(166, 58, 43, 0.06);
}

.profile-container {
  position: relative;
  max-width: var(--ts-measure-narrow);
  margin: 32px auto 0;
  display: flex;
  flex-direction: column;
  gap: 0;
  z-index: 1;
}

.profile-card {
  padding: 32px 0 36px;
  border-radius: 0;
  background: transparent;
  border: 0;
  border-bottom: 1px solid var(--ts-rule);
  box-shadow: none;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

.profile-hero-card {
  display: flex;
  align-items: center;
  gap: 24px;
}

.profile-avatar {
  width: 84px;
  height: 84px;
  border-radius: 0;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--ts-ink);
  border: 1px solid var(--ts-rule-strong);
  box-shadow: none;
  overflow: hidden;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-fallback {
  color: var(--ts-paper);
  font-family: var(--ts-font-serif);
  font-size: 34px;
  font-weight: 700;
}

.profile-hero-info {
  min-width: 0;
}

.profile-nickname {
  color: var(--ts-ink);
  font-family: var(--ts-font-serif);
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin: 0 0 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-username {
  color: var(--ts-ink-3);
  font-family: var(--ts-font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin: 0 0 18px;
}

.profile-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px 32px;
  padding-top: 16px;
  border-top: 1px solid var(--ts-rule);
}

.meta-item {
  display: inline-flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.meta-label {
  color: var(--ts-ink-3);
  font-family: var(--ts-font-mono);
  font-size: 11px;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
}

.meta-value {
  color: var(--ts-ink);
  font-family: var(--ts-font-mono);
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-section-title {
  color: var(--ts-ink);
  font-family: var(--ts-font-serif);
  font-size: 21px;
  font-weight: 700;
  letter-spacing: -0.005em;
  margin: 0 0 22px;
}

.profile-form :deep(.ant-form-item) {
  margin-bottom: 16px;
}

.profile-form :deep(.ant-input-affix-wrapper),
.profile-form :deep(.ant-input) {
  background: transparent !important;
  border: 0 !important;
  border-bottom: 1px solid var(--ts-rule-strong) !important;
  border-radius: 0 !important;
  color: var(--ts-ink) !important;
  padding: 6px 0;
  box-shadow: none !important;
}

.profile-form :deep(.ant-input-affix-wrapper:focus-within),
.profile-form :deep(.ant-input:focus) {
  border-bottom-color: var(--ts-accent) !important;
  box-shadow: none !important;
}

.profile-form :deep(.ant-input::placeholder),
.profile-form :deep(.ant-input-affix-wrapper ::placeholder) {
  color: var(--ts-ink-4) !important;
}

.profile-form :deep(.ant-input-password-icon) {
  color: var(--ts-ink-3) !important;
}

.profile-form :deep(.ant-form-item-label) {
  padding-bottom: 4px;
}

.field-label {
  color: var(--ts-ink-3);
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
}

.profile-submit {
  width: 100%;
  min-height: 50px;
  margin-top: 10px;
  border: 1px solid var(--ts-accent);
  border-radius: 0;
  background: var(--ts-accent);
  color: var(--ts-paper);
  font-family: var(--ts-font-mono);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
  cursor: pointer;
  transition: background 0.25s var(--ts-ease), border-color 0.25s var(--ts-ease);
}

.profile-submit:hover:not(:disabled) {
  transform: none;
  background: var(--ts-accent-deep);
  border-color: var(--ts-accent-deep);
  box-shadow: none;
}

.profile-submit:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.profile-submit-outline {
  background: transparent;
  border: 1px solid var(--ts-rule-strong);
  color: var(--ts-ink-2);
}

.profile-submit-outline:hover:not(:disabled) {
  background: var(--ts-paper-2);
  border-color: var(--ts-ink-3);
  box-shadow: none;
}

@media (max-width: 520px) {
  .profile-hero-card {
    flex-direction: column;
    text-align: center;
  }

  .profile-meta {
    justify-content: center;
  }

  .profile-card {
    padding: 24px 0 28px;
  }

  .profile-page {
    padding: 0 16px 64px;
  }
}
</style>
