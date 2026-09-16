<template>
  <div class="home-container">
    <!-- 动态星空粒子背景 -->
    <div class="starfield">
      <div v-for="n in 60" :key="n" class="star" :style="starStyle(n)"></div>
    </div>

    <!-- 渐变光晕装饰 -->
    <div class="glow glow-1"></div>
    <div class="glow glow-2"></div>
    <div class="glow glow-3"></div>

    <!-- 页面主内容 -->
    <div class="page-content">
      <!-- Hero 区域 -->
      <div class="hero-section">
        <div class="hero-badge">
          <span>{{ t('home.heroBadge') }}</span>
        </div>
        <h1 class="hero-title">
          <span class="title-line">{{ t('home.titleLine1') }}</span>
          <span class="title-line title-accent">{{ t('home.titleLine2') }}</span>
        </h1>
        <p class="hero-desc">{{ t('home.heroDesc') }}</p>
      </div>

      <!-- 表单主体 — 玻璃拟态卡片 -->
      <div class="glass-card">
        <a-form
          :model="formData"
          layout="vertical"
          @finish="handleSubmit"
        >
          <!-- Step 1: 目的地与日期 -->
          <div class="step-section">
            <div class="step-indicator">
              <span class="step-num">01</span>
              <span class="step-label">{{ t('home.step1') }}</span>
              <div class="step-line"></div>
            </div>

            <div class="fields-grid fields-4">
              <a-form-item name="city" :rules="formRules.city">
                <template #label>
                  <span class="field-label">{{ t('home.cityLabel') }}</span>
                </template>
                <a-input
                  v-model:value="formData.city"
                  :placeholder="t('home.cityPlaceholder')"
                  size="large"
                  class="dark-input"
                />
              </a-form-item>

              <a-form-item name="start_date" :rules="formRules.startDate">
                <template #label>
                  <span class="field-label">{{ t('home.startDateLabel') }}</span>
                </template>
                <a-date-picker
                  v-model:value="formData.start_date"
                  style="width: 100%"
                  size="large"
                  class="dark-input"
                  :placeholder="t('home.startDatePlaceholder')"
                />
              </a-form-item>

              <a-form-item name="end_date" :rules="formRules.endDate">
                <template #label>
                  <span class="field-label">{{ t('home.endDateLabel') }}</span>
                </template>
                <a-date-picker
                  v-model:value="formData.end_date"
                  style="width: 100%"
                  size="large"
                  class="dark-input"
                  :placeholder="t('home.endDatePlaceholder')"
                />
              </a-form-item>

              <a-form-item>
                <template #label>
                  <span class="field-label">{{ t('home.travelDaysLabel') }}</span>
                </template>
                <div class="days-chip">
                  <span class="days-number">{{ formData.travel_days }}</span>
                  <span class="days-text">{{ t('home.travelDaysUnit') }}</span>
                </div>
              </a-form-item>
            </div>
          </div>

          <!-- Step 2: 偏好设置 -->
          <div class="step-section">
            <div class="step-indicator">
              <span class="step-num">02</span>
              <span class="step-label">{{ t('home.step2') }}</span>
              <div class="step-line"></div>
            </div>

            <div class="fields-grid fields-2">
              <a-form-item name="transportation">
                <template #label>
                  <span class="field-label">{{ t('home.transportationLabel') }}</span>
                </template>
                <a-select v-model:value="formData.transportation" size="large" class="dark-select">
                  <a-select-option value="公共交通">{{ t('home.transportation.public') }}</a-select-option>
                  <a-select-option value="自驾">{{ t('home.transportation.drive') }}</a-select-option>
                  <a-select-option value="步行">{{ t('home.transportation.walk') }}</a-select-option>
                  <a-select-option value="混合">{{ t('home.transportation.mixed') }}</a-select-option>
                </a-select>
              </a-form-item>

              <a-form-item name="accommodation">
                <template #label>
                  <span class="field-label">{{ t('home.accommodationLabel') }}</span>
                </template>
                <a-select v-model:value="formData.accommodation" size="large" class="dark-select">
                  <a-select-option value="经济型酒店">{{ t('home.accommodation.budget') }}</a-select-option>
                  <a-select-option value="舒适型酒店">{{ t('home.accommodation.comfort') }}</a-select-option>
                  <a-select-option value="豪华酒店">{{ t('home.accommodation.luxury') }}</a-select-option>
                  <a-select-option value="民宿">{{ t('home.accommodation.homestay') }}</a-select-option>
                </a-select>
              </a-form-item>
            </div>

            <a-form-item name="preferences">
              <template #label>
                <span class="field-label">{{ t('home.interestsLabel') }}</span>
              </template>
              <div class="interest-grid">
                <a-checkbox-group v-model:value="formData.preferences" class="interest-group">
                  <label
                    v-for="item in interestOptions"
                    :key="item.value"
                    class="interest-card"
                    :class="{ active: formData.preferences.includes(item.value) }"
                    @click.prevent="togglePreference(item.value)"
                  >
                    <span class="interest-name">{{ t(item.labelKey) }}</span>
                  </label>
                </a-checkbox-group>
              </div>
            </a-form-item>
          </div>

          <!-- Step 3: 额外需求 -->
          <div class="step-section">
            <div class="step-indicator">
              <span class="step-num">03</span>
              <span class="step-label">{{ t('home.step3') }}</span>
              <div class="step-line"></div>
            </div>

            <a-form-item name="free_text_input">
              <a-textarea
                v-model:value="formData.free_text_input"
                :placeholder="t('home.specialNeedsPlaceholder')"
                :rows="3"
                size="large"
                class="dark-textarea"
              />
            </a-form-item>
          </div>

          <!-- 提交按钮 -->
          <a-form-item>
            <button
              type="submit"
              class="submit-btn"
              :class="{ loading: loading }"
              :disabled="loading"
            >
              <span v-if="!loading" class="btn-content">
                <span>{{ t('home.submit') }}</span>
              </span>
              <span v-else class="btn-content">
                <span class="btn-spinner"></span>
                <span>{{ t('home.submitting') }}</span>
              </span>
            </button>
          </a-form-item>

          <!-- 加载进度 -->
          <div v-if="loading" class="progress-section">
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: loadingProgress + '%' }"></div>
            </div>
            <p class="progress-text">{{ loadingStatus }}</p>
          </div>
        </a-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import { generateTripPlan } from '@/services/api'
import { getCurrentLocale } from '@/i18n'
import type { TripFormData, TripTaskEvent } from '@/types'
import type { Dayjs } from 'dayjs'

const router = useRouter()
const { t } = useI18n()
const loading = ref(false)
const loadingProgress = ref(0)
const loadingStatus = ref('')

const getStageStatusText = (stage: TripTaskEvent['stage']) => {
  if (stage === 'submitted' || stage === 'initializing') return t('home.loading.initializing')
  if (stage === 'attraction_search') return t('home.loading.searchingAttractions')
  if (stage === 'weather_search') return t('home.loading.queryingWeather')
  if (stage === 'hotel_search') return t('home.loading.recommendingHotels')
  if (stage === 'planning') return t('home.loading.generatingPlan')
  if (stage === 'graph_building') return t('home.loading.generatingPlan')
  if (stage === 'completed') return t('home.loading.done')
  return t('home.loading.initializing')
}

const interestOptions = [
  { value: '历史文化', labelKey: 'home.interests.history' },
  { value: '自然风光', labelKey: 'home.interests.nature' },
  { value: '美食', labelKey: 'home.interests.food' },
  { value: '购物', labelKey: 'home.interests.shopping' },
  { value: '艺术', labelKey: 'home.interests.art' },
  { value: '休闲', labelKey: 'home.interests.leisure' },
]

const formRules = computed(() => ({
  city: [{ required: true, message: t('home.cityRequired') }],
  startDate: [{ required: true, message: t('home.startDateRequired') }],
  endDate: [{ required: true, message: t('home.endDateRequired') }],
}))

type HomeFormData = Omit<TripFormData, 'start_date' | 'end_date'> & {
  start_date: Dayjs | null
  end_date: Dayjs | null
}

const formData = reactive<HomeFormData>({
  city: '',
  start_date: null,
  end_date: null,
  travel_days: 1,
  transportation: '公共交通',
  accommodation: '经济型酒店',
  preferences: [],
  free_text_input: ''
})

const togglePreference = (value: string) => {
  const idx = formData.preferences.indexOf(value)
  if (idx === -1) {
    formData.preferences.push(value)
  } else {
    formData.preferences.splice(idx, 1)
  }
}

// 星空粒子随机样式
const starStyle = (_n: number) => {
  const size = Math.random() * 3 + 1
  return {
    width: size + 'px',
    height: size + 'px',
    top: Math.random() * 100 + '%',
    left: Math.random() * 100 + '%',
    animationDelay: Math.random() * 5 + 's',
    animationDuration: (Math.random() * 3 + 2) + 's',
  }
}

// 监听日期变化,自动计算旅行天数
watch([() => formData.start_date, () => formData.end_date], ([start, end]) => {
  if (start && end) {
    const days = end.diff(start, 'day') + 1
    if (days > 0 && days <= 30) {
      formData.travel_days = days
    } else if (days > 30) {
      message.warning(t('home.messages.travelDaysTooLong'))
      formData.end_date = null
    } else {
      message.warning(t('home.messages.endDateEarlier'))
      formData.end_date = null
    }
  }
})

const handleSubmit = async () => {
  if (!formData.start_date || !formData.end_date) {
    message.error(t('home.messages.selectDate'))
    return
  }

  loading.value = true
  loadingProgress.value = 5
  loadingStatus.value = t('home.loading.initializing')

  try {
    sessionStorage.removeItem('tripPlan')
    sessionStorage.removeItem('graphData')
    sessionStorage.removeItem('planId')

    const requestData: TripFormData = {
      city: formData.city,
      start_date: formData.start_date.format('YYYY-MM-DD'),
      end_date: formData.end_date.format('YYYY-MM-DD'),
      travel_days: formData.travel_days,
      transportation: formData.transportation,
      accommodation: formData.accommodation,
      preferences: formData.preferences,
      free_text_input: formData.free_text_input,
      language: getCurrentLocale(),
    }

    const response = await generateTripPlan(requestData, {
      onTaskEvent: (event) => {
        if (Number.isFinite(event.progress)) {
          loadingProgress.value = Math.max(0, Math.min(100, event.progress))
        }
        loadingStatus.value = event.message || getStageStatusText(event.stage)
      }
    })

    loadingProgress.value = 100
    loadingStatus.value = t('home.loading.done')

    if (response.success && response.data) {
      const planId = response.plan_id || ''
      // 保存到sessionStorage
      sessionStorage.setItem('tripPlan', JSON.stringify(response.data))
      // 保存知识图谱数据
      if (response.graph_data) {
        sessionStorage.setItem('graphData', JSON.stringify(response.graph_data))
      }
      if (planId) {
        sessionStorage.setItem('planId', planId)
      }

      message.success(t('home.messages.generateSuccess'))

      // 短暂延迟后跳转
      setTimeout(() => {
        if (planId) {
          router.push({ path: '/result', query: { plan_id: planId } })
        } else {
          router.push('/result')
        }
      }, 500)
    } else {
      sessionStorage.removeItem('tripPlan')
      sessionStorage.removeItem('graphData')
      sessionStorage.removeItem('planId')
      message.error(response.message || t('home.messages.generateFailed'))
    }
  } catch (error: any) {
    sessionStorage.removeItem('tripPlan')
    sessionStorage.removeItem('graphData')
    sessionStorage.removeItem('planId')
    message.error(error.message || t('home.messages.generateRetry'))
  } finally {
    setTimeout(() => {
      loading.value = false
      loadingProgress.value = 0
      loadingStatus.value = ''
    }, 1000)
  }
}
</script>

<style scoped>
/* ===== 奶油暖调主题 - 首页 ===== */

.home-container {
  min-height: 100vh;
  background: linear-gradient(160deg, #FBF6EF 0%, #F7EDDF 45%, #F9F1E6 100%);
  padding: 60px 24px 80px;
  position: relative;
  overflow: hidden;
}

/* 星空粒子 */
.starfield {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.star {
  position: absolute;
  background: #D9B48F;
  border-radius: 50%;
  opacity: 0;
  animation: twinkle linear infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0; }
  50% { opacity: 0.5; }
}

/* 渐变光晕 */
.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
}

.glow-1 {
  width: 500px;
  height: 500px;
  top: -150px;
  left: -100px;
  background: rgba(196, 112, 63, 0.1);
}

.glow-2 {
  width: 400px;
  height: 400px;
  top: 40%;
  right: -80px;
  background: rgba(232, 168, 124, 0.12);
}

.glow-3 {
  width: 350px;
  height: 350px;
  bottom: -80px;
  left: 30%;
  background: rgba(180, 140, 100, 0.08);
}

/* 页面内容 */
.page-content {
  max-width: 900px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

/* Hero 区域 */
.hero-section {
  text-align: center;
  margin-bottom: 56px;
  animation: fadeUp 0.8s ease-out;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(196, 112, 63, 0.08);
  border: 1px solid rgba(196, 112, 63, 0.25);
  padding: 8px 20px;
  border-radius: 24px;
  color: #A65A2E;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 28px;
  letter-spacing: 0.05em;
}

.hero-title {
  margin: 0 0 20px;
  line-height: 1.15;
}

.title-line {
  display: block;
  font-size: 52px;
  font-weight: 800;
  color: #3E3229;
  letter-spacing: -0.02em;
}

.title-accent {
  background: linear-gradient(135deg, #C4703F 0%, #A65A2E 55%, #8A7B6C 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  font-size: 17px;
  color: #8A7B6C;
  margin: 0;
  font-weight: 500;
  letter-spacing: 0.02em;
}

/* 奶油玻璃卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(24px);
  border: 1px solid #EDE3D6;
  border-radius: 24px;
  padding: 48px;
  box-shadow:
    0 24px 80px rgba(62, 50, 41, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  animation: fadeUp 0.8s ease-out 0.2s both;
}

/* Step 分区 */
.step-section {
  margin-bottom: 40px;
}

.step-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.step-num {
  font-size: 14px;
  font-weight: 700;
  color: #A65A2E;
  background: rgba(196, 112, 63, 0.12);
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 0.05em;
  flex-shrink: 0;
}

.step-label {
  font-size: 18px;
  font-weight: 600;
  color: #3E3229;
  letter-spacing: 0.02em;
}

.step-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(196, 112, 63, 0.35) 0%, transparent 100%);
}

/* 字段网格 */
.fields-grid {
  display: grid;
  gap: 20px;
}

.fields-4 {
  grid-template-columns: 1.5fr 1fr 1fr 0.8fr;
}

.fields-2 {
  grid-template-columns: 1fr 1fr;
}

/* 表单标签 */
.field-label {
  font-size: 13px;
  font-weight: 500;
  color: #8A7B6C;
  letter-spacing: 0.04em;
}

/* 奶油输入框 */
.dark-input.ant-input,
.dark-input.ant-picker {
  background: #FFFFFF !important;
  border: 1px solid #E3D5C2 !important;
  border-radius: 12px !important;
  color: #3E3229 !important;
  transition: all 0.3s ease;
}

.dark-input.ant-input::placeholder,
:deep(.dark-input .ant-picker-input > input::placeholder) {
  color: rgba(138, 123, 108, 0.5) !important;
}

.dark-input.ant-input:hover,
.dark-input.ant-picker:hover {
  border-color: rgba(196, 112, 63, 0.45) !important;
  background: #FFFFFF !important;
}

.dark-input.ant-input:focus,
.dark-input.ant-picker-focused {
  border-color: #C4703F !important;
  background: #FFFFFF !important;
  box-shadow: 0 0 0 3px rgba(196, 112, 63, 0.14) !important;
}

.dark-input.ant-input:-webkit-autofill {
  -webkit-box-shadow: 0 0 0 1000px #FBF6EF inset !important;
  -webkit-text-fill-color: #3E3229 !important;
}

:deep(.dark-input .ant-picker-suffix),
:deep(.dark-input .ant-picker-clear) {
  color: #B4A694 !important;
}

:deep(.dark-input .ant-picker-input > input) {
  color: #3E3229 !important;
}

:deep(.dark-input .ant-picker-input > input:-webkit-autofill) {
  -webkit-box-shadow: 0 0 0 1000px #FBF6EF inset !important;
  -webkit-text-fill-color: #3E3229 !important;
}

/* 奶油选择框 */
.dark-select :deep(.ant-select-selector) {
  background: #FFFFFF !important;
  border: 1px solid #E3D5C2 !important;
  border-radius: 12px !important;
  color: #3E3229 !important;
  transition: all 0.3s ease;
}

.dark-select :deep(.ant-select-selection-item) {
  color: #3E3229 !important;
}

.dark-select :deep(.ant-select-arrow) {
  color: #B4A694 !important;
}

.dark-select:hover :deep(.ant-select-selector) {
  border-color: rgba(196, 112, 63, 0.45) !important;
}

.dark-select :deep(.ant-select-focused .ant-select-selector) {
  border-color: #C4703F !important;
  box-shadow: 0 0 0 3px rgba(196, 112, 63, 0.14) !important;
}

/* 天数芯片 */
.days-chip {
  display: flex;
  align-items: center; /* Changed from baseline to center */
  justify-content: center;
  gap: 4px;
  height: 48px; /* Matched to dark-input's large size */
  padding: 0 20px;
  background: linear-gradient(135deg, #E8A87C 0%, #C4703F 100%);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(196, 112, 63, 0.28);
}

.days-number {
  font-size: 22px;
  font-weight: 800;
  color: white;
  line-height: 1; /* Reset line-height to fix vertical shift */
}

.days-text {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.2; /* Better alignment with number */
  margin-top: 4px; /* Slight visual tweak offset */
}

/* 兴趣标签卡片 */
.interest-grid {
  width: 100%;
}

.interest-group {
  display: grid !important;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  width: 100%;
}

.interest-group :deep(.ant-checkbox-wrapper) {
  display: none !important;
}

.interest-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  background: #FFFFFF;
  border: 1px solid #EDE3D6;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
}

.interest-card:hover {
  border-color: rgba(196, 112, 63, 0.45);
  background: #FDF8F1;
  transform: translateY(-2px);
}

.interest-card.active {
  border-color: #C4703F;
  background: rgba(196, 112, 63, 0.1);
  box-shadow: 0 0 20px rgba(196, 112, 63, 0.12);
}

.interest-name {
  font-size: 13px;
  font-weight: 500;
  color: #6B5B4C;
}

.interest-card.active .interest-name {
  color: #A65A2E;
}

/* 奶油文本域 */
.dark-textarea :deep(.ant-input) {
  background: #FFFFFF !important;
  border: 1px solid #E3D5C2 !important;
  border-radius: 12px !important;
  color: #3E3229 !important;
  transition: all 0.3s ease;
}

.dark-textarea :deep(.ant-input::placeholder) {
  color: rgba(138, 123, 108, 0.5) !important;
}

.dark-textarea :deep(.ant-input:hover) {
  border-color: rgba(196, 112, 63, 0.45) !important;
}

.dark-textarea :deep(.ant-input:focus) {
  border-color: #C4703F !important;
  box-shadow: 0 0 0 3px rgba(196, 112, 63, 0.14) !important;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  height: 60px;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  font-family: inherit;
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, #E8A87C 0%, #C4703F 55%, #A65A2E 100%);
  background-size: 200% 200%;
  color: #FFF8F0;
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease;
  box-shadow: 0 8px 32px rgba(196, 112, 63, 0.28);
  animation: gradientShift 4s ease infinite;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(196, 112, 63, 0.36);
}

.submit-btn:active {
  transform: translateY(0);
}

.submit-btn.loading {
  background: #E8D9C6;
  box-shadow: none;
  cursor: wait;
  animation: none;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.btn-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(196, 112, 63, 0.25);
  border-top-color: #C4703F;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 进度条 */
.progress-section {
  margin-top: 24px;
  animation: fadeUp 0.4s ease-out;
}

.progress-track {
  width: 100%;
  height: 6px;
  background: #EDE3D6;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #E8A87C, #C4703F, #A65A2E);
  border-radius: 3px;
  transition: width 0.5s ease;
  box-shadow: 0 0 12px rgba(196, 112, 63, 0.35);
}

.progress-text {
  margin-top: 12px;
  text-align: center;
  color: #A65A2E;
  font-size: 15px;
  font-weight: 500;
}

/* 动画 */
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Ant Design 表单标签适配 */
:deep(.ant-form-item-label > label) {
  color: #8A7B6C !important;
}

:deep(.ant-form-item-explain-error) {
  color: #C4553A !important;
}

/* 响应式 */
@media (max-width: 768px) {
  .home-container {
    padding: 32px 16px;
  }

  .glass-card {
    padding: 28px 20px;
  }

  .title-line {
    font-size: 36px;
  }

  .fields-4 {
    grid-template-columns: 1fr;
  }

  .fields-2 {
    grid-template-columns: 1fr;
  }

  .interest-group {
    grid-template-columns: repeat(3, 1fr) !important;
  }
}
</style>
