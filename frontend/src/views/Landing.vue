<template>
  <div class="landing-page">
    <div class="lower-shade" :style="lowerShadeStyle"></div>
    <NavBar over-hero @brand-click="scrollToTop" @cta-click="scrollToForm" />

    <div class="wrapper">
      <div class="page-header section-dark landing-header">
        <!-- 背景：环极星轨照片。外层走滚动视差，内层做常驻的缓慢推镜 -->
        <div class="hero-media" :style="heroMediaStyle" aria-hidden="true">
          <div class="hero-media-img">
            <!-- 沿同心圆轨道绕极点运行的星点层 -->
            <canvas ref="starCanvasRef" class="hero-stars"></canvas>
          </div>
        </div>
        <div class="hero-vignette" aria-hidden="true"></div>
        <!-- 偶尔划过的流星 -->
        <span class="hero-meteor" aria-hidden="true"></span>
        <span class="hero-meteor hero-meteor-2" aria-hidden="true"></span>
        <div class="hero-frame" aria-hidden="true"></div>
        <div class="filter"></div>
        <div class="hero-rail" aria-hidden="true">
          <span class="hero-rail-text">{{ t('home.heroRail') }}</span>
        </div>
        <div class="content-center" :style="heroContentStyle">
          <div class="container">
            <div class="hero-masthead">
              <span class="hero-masthead-name">{{ t('home.heroMasthead') }}</span>
              <span class="hero-masthead-line"></span>
              <span class="hero-masthead-issue">{{ t('home.heroIssue') }}</span>
            </div>
            <div class="title-brand">
              <h1 class="presentation-title">
                TripStellar
              </h1>
            </div>
            <h2 class="presentation-subtitle text-center">{{ t('home.titleLine') }}</h2>
            <p class="hero-footnote">{{ t('home.heroFootnote') }}</p>
            <button type="button" class="hero-scroll" @click="scrollToForm">
              <span>{{ t('home.heroScroll') }}</span>
              <span class="hero-scroll-line" aria-hidden="true"></span>
            </button>
          </div>
        </div>
        <div class="moving-clouds" :style="movingCloudsStyle"></div>
        <div class="fog-low" :style="fogLowStyle">
          <img src="https://demos.creative-tim.com/paper-kit-2/assets/img/clouds.png" alt="fog" />
        </div>
        <div class="fog-low right" :style="fogLowRightStyle">
          <img src="https://demos.creative-tim.com/paper-kit-2/assets/img/clouds.png" alt="fog" />
        </div>
        <div class="hero-bottom-shade" :style="heroBottomShadeStyle"></div>
      </div>
    </div>

    <section ref="formRef" class="form-section">
      <div class="form-panel" :style="[formRevealStyle, { minHeight: panelHeight === 'auto' ? 'auto' : panelHeight + 'px' }]" ref="panelRef">
        <a-form v-show="!loading" :model="formData" layout="vertical" @finish="handleSubmit">
          <div class="step">
            <div class="step-head">
              <span>01</span>
              <h3>{{ t('home.step1') }}</h3>
            </div>

            <!-- 多城市动态列表 -->
            <div class="city-list">
              <div v-for="(cs, idx) in formData.cities" :key="idx" class="city-row">
                <a-form-item class="city-row-name" :rules="[{ required: true, message: t('home.cityRequired') }]">
                  <template #label>
                    <span class="field-label">{{ t('home.cityNLabel', { n: idx + 1 }) }}</span>
                  </template>
                  <a-input
                    v-model:value="cs.city"
                    :placeholder="t('home.cityPlaceholder')"
                    size="large"
                    class="field-input"
                  />
                </a-form-item>
                <a-form-item class="city-row-days">
                  <template #label>
                    <span class="field-label">{{ t('home.cityStayDays') }}</span>
                  </template>
                  <a-input-number
                    v-model:value="cs.days"
                    :min="1"
                    :max="15"
                    size="large"
                    class="field-input"
                    style="width: 100%"
                  />
                </a-form-item>
                <button
                  v-if="formData.cities.length > 1"
                  type="button"
                  class="city-remove-btn"
                  @click="removeCity(idx)"
                >×</button>
              </div>
              <button type="button" class="city-add-btn" @click="addCity">
                + {{ t('home.addCity') }}
              </button>
            </div>

            <!-- 日期与天数 -->
            <div class="grid grid-date">
              <a-form-item name="start_date" :rules="formRules.startDate">
                <template #label>
                  <span class="field-label">{{ t('home.startDateLabel') }}</span>
                </template>
                <a-date-picker
                  v-model:value="formData.start_date"
                  style="width: 100%"
                  size="large"
                  class="field-input"
                  :placeholder="t('home.startDatePlaceholder')"
                />
              </a-form-item>

              <a-form-item>
                <template #label>
                  <span class="field-label">{{ t('home.travelDaysLabel') }}</span>
                </template>
                <div class="days-chip">
                  <span class="days-number">{{ totalDays }}</span>
                  <span class="days-unit">{{ t('home.travelDaysUnit') }}</span>
                </div>
              </a-form-item>
            </div>
          </div>

          <div class="step">
            <div class="step-head">
              <span>02</span>
              <h3>{{ t('home.step2') }}</h3>
            </div>
            <div class="grid grid2">
              <a-form-item name="transportation">
                <template #label>
                  <span class="field-label">{{ t('home.transportationLabel') }}</span>
                </template>
                <a-select v-model:value="formData.transportation" size="large" class="field-select">
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
                <a-select v-model:value="formData.accommodation" size="large" class="field-select">
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
                    class="interest-pill"
                    :class="{ active: formData.preferences.includes(item.value) }"
                    @click.prevent="togglePreference(item.value)"
                  >
                    {{ t(item.labelKey) }}
                  </label>
                </a-checkbox-group>
              </div>
            </a-form-item>
          </div>

          <div class="step">
            <div class="step-head">
              <span>03</span>
              <h3>{{ t('home.step3') }}</h3>
            </div>
            <a-form-item name="free_text_input">
              <div class="field-textarea">
                <a-textarea
                  v-model:value="formData.free_text_input"
                  :placeholder="t('home.specialNeedsPlaceholder')"
                  :rows="4"
                  size="large"
                  class="special-textarea"
                />
              </div>
            </a-form-item>
          </div>

          <a-form-item>
            <button type="submit" class="btn btn-danger btn-round submit-btn" :class="{ loading }" :disabled="loading">
              <span v-if="!loading">{{ t('home.submit') }}</span>
              <span v-else class="loading-row">
                <i class="spinner"></i>
                {{ t('home.submitting') }}
              </span>
            </button>
          </a-form-item>
        </a-form>

        <!-- Node Loading Stepper -->
        <div v-show="loading" class="stepper-wrapper">
          <div class="stepper-header">
            <h2 class="stepper-title">{{ t('home.loading.planCode', { code: planCode }) }}</h2>
            <p class="stepper-subtitle">{{ t('home.loading.preparing') }}</p>
          </div>
          
          <div class="stepper-container">
            <!-- Step 1: Searching Attractions -->
            <div class="step-node" :class="{ active: loadingProgress >= 0 && loadingProgress <= 30, completed: loadingProgress > 30 }">
              <div class="node-icon">
                <i v-if="loadingProgress >= 0 && loadingProgress <= 30" class="spinner-small"></i>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
              </div>
              <p class="node-text">{{ loadingProgress > 30 ? t('home.loading.searchedAttractions') : t('home.loading.searchingAttractions') }}</p>
            </div>
            <div class="step-divider" :class="{ completed: loadingProgress > 30 }"></div>

            <!-- Step 2: Weather -->
            <div class="step-node" :class="{ active: loadingProgress > 30 && loadingProgress <= 50, completed: loadingProgress > 50 }">
              <div class="node-icon">
                <i v-if="loadingProgress > 30 && loadingProgress <= 50" class="spinner-small"></i>
                <svg v-else width="20px" height="20px" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                  <path d="M10.5 1.5V3.1M3.6 10H2M5.4512 4.95137L4.31982 3.82M15.5498 4.95137L16.6812 3.82M19 10H17.4M6.50007 10.0001C6.50007 7.79093 8.29093 6.00007 10.5001 6.00007C12.0061 6.00007 13.3177 6.83235 14.0001 8.06206M6 22C3.79086 22 2 20.2091 2 18C2 15.7909 3.79086 14 6 14C6.46419 14 6.90991 14.0791 7.32442 14.2245C8.04061 12.3396 9.86387 11 12 11C14.1361 11 15.9594 12.3396 16.6756 14.2245C17.0901 14.0791 17.5358 14 18 14C20.2091 14 22 15.7909 22 18C22 20.2091 20.2091 22 18 22C13.3597 22 9.87921 22 6 22Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <p class="node-text">{{ loadingProgress > 50 ? t('home.loading.queriedWeather') : t('home.loading.queryingWeather') }}</p>
            </div>
            <div class="step-divider" :class="{ completed: loadingProgress > 50 }"></div>

            <!-- Step 3: Hotels -->
            <div class="step-node" :class="{ active: loadingProgress > 50 && loadingProgress <= 70, completed: loadingProgress > 70 }">
              <div class="node-icon">
                <i v-if="loadingProgress > 50 && loadingProgress <= 70" class="spinner-small"></i>
                <svg v-else fill="currentColor" width="25px" height="25px" viewBox="0 0 24 24" version="1.1" xml:space="preserve" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                    <g id="Layer_Grid"/><g id="Layer_2">
                    <path d="M21,8c0-2.2-1.8-4-4-4H7C4.8,4,3,5.8,3,8v3.8c-0.6,0.5-1,1.3-1,2.2v2.7V17v2c0,0.6,0.4,1,1,1s1-0.4,1-1v-1h16v1   c0,0.6,0.4,1,1,1s1-0.4,1-1v-2v-0.3V14c0-0.9-0.4-1.7-1-2.2V8z M5,8c0-1.1,0.9-2,2-2h10c1.1,0,2,0.9,2,2v3h-1v-1c0-1.7-1.3-3-3-3   h-1c-0.8,0-1.5,0.3-2,0.8C11.5,7.3,10.8,7,10,7H9c-1.7,0-3,1.3-3,3v1H5V8z M16,10v1h-3v-1c0-0.6,0.4-1,1-1h1C15.6,9,16,9.4,16,10z    M11,10v1H8v-1c0-0.6,0.4-1,1-1h1C10.6,9,11,9.4,11,10z M20,16H4v-2c0-0.6,0.4-1,1-1h3h3h2h3h3c0.6,0,1,0.4,1,1V16z"/></g>
                </svg>
              </div>
              <p class="node-text">{{ loadingProgress > 70 ? t('home.loading.recommendedHotels') : t('home.loading.recommendingHotels') }}</p>
            </div>
            <div class="step-divider" :class="{ completed: loadingProgress > 70 }"></div>

            <!-- Step 4: Planning -->
            <div class="step-node" :class="{ active: loadingProgress > 70 && loadingProgress < 100, completed: loadingProgress >= 100 }">
              <div class="node-icon">
                <i v-if="loadingProgress > 70 && loadingProgress < 100" class="spinner-small"></i>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
              </div>
              <p class="node-text">{{ loadingProgress >= 100 ? t('home.loading.done') : t('home.loading.generatingPlan') }}</p>
            </div>
          </div>
          
          <div class="stepper-footer">
            <h3>{{ loadingStatus }}</h3>
            <p v-if="loadingProgress < 100">{{ t('home.loading.workingTogether') }}</p>
            <p v-else>{{ t('home.loading.donePrepare') }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="history-section">
      <div class="history-panel">
        <div class="history-head">
          <div>
            <p class="history-eyebrow">{{ t('home.history.eyebrow') }}</p>
            <h3 class="history-title">{{ t('home.history.title') }}</h3>
          </div>
          <a-button type="link" class="history-refresh" @click="loadHistoryPlans">
            {{ t('home.history.refresh') }}
          </a-button>
        </div>

        <div v-if="historyLoading" class="history-loading">
          {{ t('common.loading') }}
        </div>
        <a-empty v-else-if="historyPlans.length === 0" :description="t('home.history.empty')" />
        <div v-else class="history-list">
          <button
            v-for="item in historyPlans"
            :key="item.plan_id"
            type="button"
            class="history-item"
            @click="openHistoryPlan(item.plan_id)"
          >
            <div class="history-item-main">
              <div class="history-route">
                <span class="history-city">{{ item.city }}</span>
                <span class="history-date">{{ item.start_date }} {{ t('common.to') }} {{ item.end_date }}</span>
              </div>
              <p class="history-meta">
                <span>Plan ID: {{ item.plan_id }}</span>
                <span>{{ item.travel_days }}{{ t('home.travelDaysUnit') }}</span>
                <span>{{ t('home.history.updatedAt') }} {{ formatHistoryTime(item.updated_at) }}</span>
              </p>
              <p v-if="item.overall_suggestions" class="history-summary">{{ item.overall_suggestions }}</p>
            </div>
            <span class="history-open">{{ t('home.history.open') }}</span>
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import { generateTripPlan, getTripHistory } from '@/services/api'
import { getCurrentLocale } from '@/i18n'
import NavBar from '@/components/NavBar.vue'
import type { TripFormData, TripTaskEvent, TripHistoryItem, CityStay } from '@/types'
import type { Dayjs } from 'dayjs'

type LandingFormData = {
  cities: Array<{ city: string; days: number }>
  start_date: Dayjs | null
  transportation: string
  accommodation: string
  preferences: string[]
  free_text_input: string
}

const router = useRouter()
const { t } = useI18n()

const loading = ref(false)
const loadingProgress = ref(0)
const loadingStatus = ref('')
const scrollY = ref(0)
const formRef = ref<HTMLElement | null>(null)
const panelRef = ref<HTMLElement | null>(null)
const panelHeight = ref<number | string>('auto')
const fogEnabled = ref(true)
const planCode = ref('')
const historyLoading = ref(false)
const historyPlans = ref<TripHistoryItem[]>([])

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
  startDate: [{ required: true, message: t('home.startDateRequired') }],
}))

const formData = reactive<LandingFormData>({
  cities: [{ city: '', days: 2 }],
  start_date: null,
  transportation: '公共交通',
  accommodation: '经济型酒店',
  preferences: [],
  free_text_input: '',
})

const totalDays = computed(() => formData.cities.reduce((sum, cs) => sum + (cs.days || 1), 0))

const computedEndDate = computed(() => {
  if (!formData.start_date) return null
  return formData.start_date.add(totalDays.value - 1, 'day')
})

const addCity = () => {
  if (formData.cities.length >= 5) return
  formData.cities.push({ city: '', days: 2 })
}

const removeCity = (index: number) => {
  if (formData.cities.length <= 1) return
  formData.cities.splice(index, 1)
}

const heroProgress = computed(() => Math.min(scrollY.value / 320, 1))
const toneProgress = computed(() => Math.min(Math.max((scrollY.value - 20) / 360, 0), 1))
/* 视频层的视差：铺满并放大 1.14 倍留出位移余量，滚动时缓慢上移 */
const heroMediaStyle = computed(() => ({
  transform: `translate3d(0, ${Math.max(-scrollY.value * 0.08, -120)}px, 0) scale(1.14)`,
}))
/* 星轨视频上不再叠白色云雾，否则会把星空糊成灰白 */
const movingCloudsStyle = computed(() => ({
  backgroundImage: "url('https://demos.creative-tim.com/paper-kit-2/assets/img/clouds.png')",
  opacity: '0',
}))
const fogLowStyle = computed(() => ({
  opacity: '0',
}))
const fogLowRightStyle = computed(() => ({
  opacity: '0',
}))
const heroContentStyle = computed(() => ({
  opacity: `${1 - heroProgress.value * 0.95}`,
  transform: `translate3d(0, ${-heroProgress.value * 46}px, 0)`,
}))
const heroBottomShadeStyle = computed(() => ({
  /* 底部纸色渐隐压到很低，避免把地平线的暖光洗掉；滚动时再逐步加强 */
  opacity: `${(0.1 + toneProgress.value * 0.66) * (fogEnabled.value ? 1 : 0)}`,
}))
const lowerShadeStyle = computed(() => ({
  opacity: `${(0.34 + toneProgress.value * 0.52) * (fogEnabled.value ? 1 : 0)}`,
}))
const formRevealStyle = computed(() => {
  const progress = Math.min(Math.max((scrollY.value - 80) / 340, 0), 1)
  return {
    opacity: `${0.2 + progress * 0.8}`,
    transform: `translate3d(0, ${(1 - progress) * 56}px, 0)`,
  }
})

const togglePreference = (value: string) => {
  const index = formData.preferences.indexOf(value)
  if (index === -1) formData.preferences.push(value)
  else formData.preferences.splice(index, 1)
}

const onScroll = () => {
  scrollY.value = window.scrollY || 0
}
const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' })
const scrollToForm = () => {
  if (formRef.value) {
    const y = formRef.value.getBoundingClientRect().top + window.scrollY - 65
    window.scrollTo({ top: y, behavior: 'smooth' })
  }
}

const formatHistoryTime = (value: string) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

const openHistoryPlan = (planId: string) => {
  if (!planId) return
  sessionStorage.removeItem('tripPlan')
  sessionStorage.removeItem('graphData')
  sessionStorage.setItem('planId', planId)
  router.push({ path: '/result', query: { plan_id: planId } })
}

const loadHistoryPlans = async () => {
  historyLoading.value = true
  try {
    historyPlans.value = await getTripHistory(8)
  } catch (error: any) {
    historyPlans.value = []
    message.error(error.message || t('home.history.loadFailed'))
  } finally {
    historyLoading.value = false
  }
}

/* ===== 星轨极点自转 =====
   为什么不直接旋转照片：这张图的星轨极点在原图约 (63%, 44%) 处，偏离画面中心。
   绕它转满一圈，图片必须放大到 2.16 倍才能保证四个角始终被覆盖，
   而原图只有 1555px 宽，放大到这个程度会明显发虚。
   所以改成在照片之上叠一层程序生成的星点，让它们沿各自的同心圆轨道绕极点运行——
   轨道与照片里已有的星轨同心，视觉上就是"星轨在实时生长"。 */
const starCanvasRef = ref<HTMLCanvasElement | null>(null)
/** 星轨汇聚的极点，坐标是原图内的相对位置 */
const STAR_POLE = { x: 0.63, y: 0.44 }
const HERO_IMAGE_W = 1555
const HERO_IMAGE_H = 1012
/** 绕极点转一整圈所需的秒数，越大越慢 */
const STAR_SPIN_SECONDS = 240
/** 目标帧率：自转很慢，30 帧足够，省一半开销 */
const STAR_FPS = 30
/** 原图中的地平线高度（相对位置）：再往下是树与地面，不落星点 */
const STAR_HORIZON = 0.86
/** 地平线前的渐隐起点，避免星点在树梢处硬闪 */
const STAR_HORIZON_FADE = 0.8

type OrbitStar = {
  radius: number
  phase: number
  size: number
  glow: number
  /** 闪烁角速度：让星点有明暗呼吸，肉眼立刻能看出这层是活的 */
  twinkleSpeed: number
}

let orbitStars: OrbitStar[] = []
let starSprite: HTMLCanvasElement | null = null
let starRafId = 0
let starElapsed = 0
let starLastFrameTs = 0
let starLastTickTs = 0

/** 背景图在元素内的映射，换算规则与 background-size: cover / background-position: center bottom 完全一致 */
const heroImageMapping = (w: number, h: number) => {
  const scale = Math.max(w / HERO_IMAGE_W, h / HERO_IMAGE_H)
  const renderedW = HERO_IMAGE_W * scale
  const renderedH = HERO_IMAGE_H * scale
  return {
    renderedW,
    renderedH,
    offsetX: (w - renderedW) / 2, // background-position: center
    offsetY: h - renderedH, // background-position: bottom
  }
}

/** 原图坐标下的极点 → 元素内 CSS 像素 */
const poleInHost = (w: number, h: number) => {
  const map = heroImageMapping(w, h)
  return {
    x: map.offsetX + STAR_POLE.x * map.renderedW,
    y: map.offsetY + STAR_POLE.y * map.renderedH,
  }
}

/** 预渲染单颗星的光晕贴图：比每帧为每颗星新建径向渐变快得多 */
const buildStarSprite = () => {
  const size = 32
  const sprite = document.createElement('canvas')
  sprite.width = size
  sprite.height = size
  const ctx = sprite.getContext('2d')
  if (!ctx) return null
  const r = size / 2
  const gradient = ctx.createRadialGradient(r, r, 0, r, r, r)
  // 亮核收得很紧、外圈衰减很快，读起来是"一颗星"而不是一团光斑
  gradient.addColorStop(0, 'rgba(255, 255, 255, 1)')
  gradient.addColorStop(0.12, 'rgba(255, 255, 255, 0.88)')
  gradient.addColorStop(0.3, 'rgba(212, 232, 255, 0.32)')
  gradient.addColorStop(0.62, 'rgba(160, 195, 255, 0.07)')
  gradient.addColorStop(1, 'rgba(140, 180, 255, 0)')
  ctx.fillStyle = gradient
  ctx.beginPath()
  ctx.arc(r, r, r, 0, Math.PI * 2)
  ctx.fill()
  return sprite
}

/** 撒点：半径取平方根分布，保证单位面积上的星数均匀，不会全挤在极点附近 */
const seedOrbitStars = (maxRadius: number) => {
  // 星点只做点缀，密度压到原来的三分之一左右
  const count = Math.round(Math.min(Math.max(maxRadius * 0.08, 60), 130))
  orbitStars = Array.from({ length: count }, () => ({
    radius: maxRadius * (0.07 + Math.sqrt(Math.random()) * 0.93),
    phase: Math.random() * Math.PI * 2,
    size: 1.2 + Math.random() * 1.4,
    glow: 0.5 + Math.random() * 0.5,
    twinkleSpeed: 0.5 + Math.random() * 1.4,
  }))
}

const renderOrbitStars = () => {
  const canvas = starCanvasRef.value
  const ctx = canvas?.getContext('2d')
  if (!canvas || !ctx) return

  const w = canvas.offsetWidth
  const h = canvas.offsetHeight
  if (!w || !h) return

  // 尺寸变化（含设备像素比变化）时重建画布并重新撒点
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  const pixelW = Math.round(w * dpr)
  const pixelH = Math.round(h * dpr)
  if (canvas.width !== pixelW || canvas.height !== pixelH) {
    canvas.width = pixelW
    canvas.height = pixelH
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    orbitStars = []
  }

  const map = heroImageMapping(w, h)
  const pole = poleInHost(w, h)
  if (orbitStars.length === 0) {
    seedOrbitStars(
      Math.max(
        Math.hypot(pole.x, pole.y),
        Math.hypot(w - pole.x, pole.y),
        Math.hypot(pole.x, h - pole.y),
        Math.hypot(w - pole.x, h - pole.y)
      )
    )
  }

  if (!starSprite) starSprite = buildStarSprite()
  const sprite = starSprite
  if (!sprite) return

  const omega = (Math.PI * 2) / STAR_SPIN_SECONDS

  ctx.clearRect(0, 0, w, h)
  // 叠加混合：星点重叠处自然变亮
  ctx.globalCompositeOperation = 'lighter'
  for (const star of orbitStars) {
    const angle = star.phase + omega * starElapsed
    const x = pole.x + star.radius * Math.cos(angle)
    const y = pole.y + star.radius * Math.sin(angle)
    if (x < -24 || y < -24 || x > w + 24 || y > h + 24) continue

    // 折算回原图坐标做地平线裁剪：树与地面不落星点，临界处渐隐
    const imageY = (y - map.offsetY) / map.renderedH
    if (imageY >= STAR_HORIZON) continue
    const fade =
      imageY <= STAR_HORIZON_FADE
        ? 1
        : 1 - (imageY - STAR_HORIZON_FADE) / (STAR_HORIZON - STAR_HORIZON_FADE)

    // 闪烁：0.62~1.0 之间呼吸，让「这层在动」一眼可见
    const twinkle = 0.81 + 0.19 * Math.sin(starElapsed * star.twinkleSpeed * 2 + star.phase * 3)

    const half = star.size * 3
    ctx.globalAlpha = star.glow * fade * twinkle
    ctx.drawImage(sprite, x - half, y - half, half * 2, half * 2)
  }
  ctx.globalAlpha = 1
  ctx.globalCompositeOperation = 'source-over'
}

const starTick = (now: number) => {
  starRafId = window.requestAnimationFrame(starTick)
  // hero 滚出视口后完全停算，回到视口内再接着走（不会跳帧）
  if (scrollY.value > window.innerHeight) {
    starLastTickTs = now
    starLastFrameTs = now
    return
  }
  if (now - starLastTickTs < 1000 / STAR_FPS) return
  starElapsed += starLastFrameTs ? (now - starLastFrameTs) / 1000 : 0
  starLastFrameTs = now
  starLastTickTs = now
  renderOrbitStars()
}

const startOrbitStars = () => {
  if (!starCanvasRef.value || starRafId) return
  // 注：这里不再因 prefers-reduced-motion 而冻结。
  // 之前命中该设置时只画一帧静止画面，静止的星点和照片自带的亮点没有区别，
  // 会被当成"没有效果"。效果本身是本页的明确需求，所以始终运行动画。
  starLastFrameTs = 0
  starLastTickTs = 0
  starRafId = window.requestAnimationFrame(starTick)
}

const stopOrbitStars = () => {
  if (starRafId) {
    window.cancelAnimationFrame(starRafId)
    starRafId = 0
  }
}

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
  void loadHistoryPlans()
  startOrbitStars()
})
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  stopOrbitStars()
})

const handleSubmit = async () => {
  // 校验：至少一个城市名非空
  const validCities = formData.cities.filter(cs => cs.city.trim())
  if (validCities.length === 0) {
    message.error(t('home.atLeastOneCity'))
    return
  }
  if (!formData.start_date) {
    message.error(t('home.messages.selectDate'))
    return
  }
  if (totalDays.value > 30) {
    message.warning(t('home.messages.travelDaysTooLong'))
    return
  }

  if (panelRef.value) {
    panelHeight.value = panelRef.value.offsetHeight
  }

  loading.value = true
  loadingProgress.value = 5
  loadingStatus.value = t('home.loading.initializing')
  planCode.value = ''

  try {
    sessionStorage.removeItem('tripPlan')
    sessionStorage.removeItem('graphData')
    sessionStorage.removeItem('planId')

    const citiesPayload: CityStay[] = validCities.map(cs => ({ city: cs.city.trim(), days: cs.days || 1 }))
    const endDate = computedEndDate.value!

    const requestData: TripFormData = {
      city: citiesPayload[0].city,
      cities: citiesPayload,
      start_date: formData.start_date.format('YYYY-MM-DD'),
      end_date: endDate.format('YYYY-MM-DD'),
      travel_days: totalDays.value,
      transportation: formData.transportation,
      accommodation: formData.accommodation,
      preferences: formData.preferences,
      free_text_input: formData.free_text_input,
      language: getCurrentLocale(),
    }

    const response = await generateTripPlan(requestData, {
      onTaskCreated: (task) => {
        planCode.value = task.plan_id || task.task_id
        loadingProgress.value = 5
        loadingStatus.value = t('home.loading.initializing')
      },
      onTaskEvent: (event) => {
        if (event.plan_id) planCode.value = event.plan_id
        if (Number.isFinite(event.progress)) {
          loadingProgress.value = Math.max(0, Math.min(100, event.progress))
        }
        loadingStatus.value = event.message || getStageStatusText(event.stage)
      }
    })

    loadingProgress.value = 100
    loadingStatus.value = t('home.loading.done')

    if (response.success && response.data) {
      const planId = response.plan_id || planCode.value
      sessionStorage.setItem('tripPlan', JSON.stringify(response.data))
      if (response.graph_data) sessionStorage.setItem('graphData', JSON.stringify(response.graph_data))
      if (planId) sessionStorage.setItem('planId', planId)
      message.success(t('home.messages.generateSuccess'))
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
      panelHeight.value = 'auto'
    }, 1000)
  }
}
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  background: var(--ts-paper);
  color: var(--ts-ink-2);
  position: relative;
  isolation: isolate;
  overflow-x: hidden; /* 防止水平溢出导致的出界感 */
}

.lower-shade {
  position: fixed;
  inset: 0% 0 -1px 0;
  z-index: 0;
  pointer-events: none;
  background: rgba(236, 236, 233, 0.6);
  transition: opacity 0.18s linear;
}

.lower-shade::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: -28px;
  height: 28px;
  background: linear-gradient(to bottom, rgba(236, 236, 233, 0), rgba(236, 236, 233, 0.94));
}

.landing-header {
  /* 确保 hero 区域占满全屏高度，背景图不重复 */
  height: 100vh;
  min-height: 100vh;
  position: relative;
  display: block;
  /* 夜空兜底色：视频未加载/被拦截时，浅色文字仍然可读 */
  background-color: #0b1020;
  background-image: none !important;
  overflow: hidden;
  z-index: 1;
  /* 浅色文字压在星空上时的深色底晕，保证小字可读。
     背景由浅色照片改为夜空视频后，光晕方向也从纸色翻成墨色 */
  --hero-halo: 0 0 10px rgba(6, 8, 14, 0.9), 0 0 28px rgba(6, 8, 14, 0.62);
}

/* 背景层：外层负责滚动视差（transform 由 computed 注入），
   内层负责常驻的缓慢推镜——拆成两层，两个 transform 才不会互相覆盖 */
.hero-media {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  will-change: transform;
}

.hero-media-img {
  position: absolute;
  /* 不再向外扩，让 cover 以最小放大倍数呈现，尽量多露出画面内容 */
  inset: 0;
  background-image: url('/images/hero-night-sky.jpg');
  background-size: cover;
  /* 底部对齐：地平线与树的剪影永远落在画面底边，裁掉的只是上方空白夜空 */
  background-position: center bottom;
  background-repeat: no-repeat;
  /* 夜空略提亮避免死黑，略降对比压住高感噪点 */
  filter: brightness(1.12) contrast(0.96);
  /* 以底边为原点，推镜时地平线不动，只有天空在呼吸 */
  transform-origin: center bottom;
  animation: hero-drift 38s ease-in-out infinite alternate;
  will-change: transform;
}

/* 极慢的推近，幅度压到 6%，只做"呼吸"不做"放大" */
@keyframes hero-drift {
  from {
    transform: scale(1);
  }
  to {
    transform: scale(1.06);
  }
}

/* 星点层：画在与背景图同一个元素里，所以推镜时星点和星轨始终保持对齐 */
.hero-stars {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* 流星：偶尔划过，给星空一点"活着"的感觉 */
.hero-meteor {
  position: absolute;
  top: 10%;
  left: 16%;
  z-index: 2;
  width: 190px;
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.95) 100%);
  box-shadow: 0 0 10px rgba(170, 210, 255, 0.8);
  opacity: 0;
  pointer-events: none;
  /* 以尾端为原点旋转，飞行方向与倾斜角一致 */
  transform-origin: right center;
  animation: meteor-fall 17s linear infinite;
}

.hero-meteor-2 {
  top: 26%;
  left: 56%;
  width: 130px;
  animation-delay: 9.5s;
  animation-duration: 23s;
}

@keyframes meteor-fall {
  0% {
    opacity: 0;
    transform: translate3d(0, 0, 0) rotate(31deg) scaleX(0.25);
  }
  2% {
    opacity: 1;
    transform: translate3d(70px, 42px, 0) rotate(31deg) scaleX(1);
  }
  7% {
    opacity: 0;
    transform: translate3d(560px, 336px, 0) rotate(31deg) scaleX(1);
  }
  100% {
    opacity: 0;
    transform: translate3d(560px, 336px, 0) rotate(31deg) scaleX(1);
  }
}

/* 蒙版层：① 四边暗角（把星空压成背景，视线收拢到画面中心的星轨）
            ② 文字行再压一层深色，托住浅色的刊头与标题 */
.hero-vignette {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  background:
    radial-gradient(
      62% 80% at 50% 48%,
      rgba(6, 8, 14, 0) 0%,
      rgba(6, 8, 14, 0.16) 44%,
      rgba(6, 8, 14, 0.4) 72%,
      rgba(6, 8, 14, 0.76) 100%
    ),
    radial-gradient(
      58% 34% at 50% 44%,
      rgba(6, 8, 14, 0.5) 0%,
      rgba(6, 8, 14, 0.22) 58%,
      rgba(6, 8, 14, 0) 100%
    );
}

/* 刊物细线框：夜空底上改用浅线，multiply 在暗底会直接消失 */
.hero-frame {
  position: absolute;
  inset: 88px 28px 28px;
  z-index: 2;
  pointer-events: none;
  border: 1px solid rgba(250, 248, 244, 0.2);
}

/* 竖排刊头 */
.hero-rail {
  position: absolute;
  z-index: 4;
  left: 48px;
  top: 50%;
  transform: translateY(-50%);
  writing-mode: vertical-rl;
  pointer-events: none;
}

.hero-rail-text {
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.44em;
  text-transform: uppercase;
  color: rgba(250, 248, 244, 0.86);
  /* 竖排刊头落在画面左侧暗角上，同样给一层深色光晕 */
  text-shadow: var(--hero-halo);
  /* 起首加一个朱砂小方点，像杂志页码的标记 */
  border-top: 6px solid var(--ts-accent);
  padding-top: 12px;
}

.landing-header .filter {
  z-index: 2;
}

.landing-header .filter::after {
  background: linear-gradient(
    180deg,
    rgba(6, 8, 14, 0.3) 0%,
    rgba(6, 8, 14, 0) 42%,
    rgba(6, 8, 14, 0.18) 100%
  ) !important;
}

.history-section {
  position: relative;
  z-index: 1;
  padding: 0 24px 96px;
}

/* 杂志目录式：无卡片、无阴影，仅靠发丝线与编号分栏 */
.history-panel {
  max-width: var(--ts-measure);
  margin: 0 auto;
  background: transparent;
  border: 0;
  border-top: 1px solid var(--ts-rule-strong);
  border-radius: 0;
  padding: 32px 0 0;
  box-shadow: none;
  backdrop-filter: none;
}

.history-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.history-eyebrow {
  margin: 0 0 8px;
  color: var(--ts-ink-3);
  font-family: var(--ts-font-mono);
  font-size: 11px;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
}

.history-title {
  margin: 0;
  color: var(--ts-ink);
  font-family: var(--ts-font-serif);
  font-size: 30px;
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: -0.01em;
}

.history-refresh {
  padding-inline: 0;
  font-family: var(--ts-font-mono) !important;
  font-size: 11px !important;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
}

.history-loading {
  color: var(--ts-ink-3);
  padding: 16px 0;
}

.history-list {
  display: block;
  counter-reset: ts-index;
}

.history-item {
  width: 100%;
  border: 0;
  border-top: 1px solid var(--ts-rule);
  border-radius: 0;
  background: transparent;
  color: inherit;
  padding: 20px 8px 20px 0;
  text-align: left;
  display: flex;
  align-items: flex-start;
  gap: 20px;
  cursor: pointer;
  transition: background 0.25s var(--ts-ease), padding 0.25s var(--ts-ease);
}

.history-item::before {
  counter-increment: ts-index;
  content: counter(ts-index, decimal-leading-zero);
  flex: none;
  width: 30px;
  padding-top: 6px;
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.1em;
  color: var(--ts-ink-4);
  transition: color 0.25s var(--ts-ease);
}

.history-item:hover {
  background: var(--ts-paper-2);
  padding-left: 12px;
  padding-right: 12px;
}

.history-item:hover::before {
  color: var(--ts-accent);
}

.history-item-main {
  min-width: 0;
  flex: 1;
}

.history-route {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 12px;
}

.history-city {
  color: var(--ts-ink);
  font-family: var(--ts-font-serif);
  font-size: 21px;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.history-date {
  color: var(--ts-ink-3);
  font-family: var(--ts-font-mono);
  font-size: 12px;
  letter-spacing: 0.04em;
}

.history-meta {
  margin: 10px 0 0;
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  color: var(--ts-ink-4);
  font-family: var(--ts-font-mono);
  font-size: 11px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.history-summary {
  margin: 12px 0 0;
  color: var(--ts-ink-2);
  font-size: 14px;
  line-height: 1.75;
  max-width: 62ch;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.history-open {
  flex: none;
  color: var(--ts-ink-3);
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
  white-space: nowrap;
  padding-top: 6px;
  border-bottom: 1px solid transparent;
  transition: color 0.25s var(--ts-ease), border-color 0.25s var(--ts-ease);
}

.history-item:hover .history-open {
  color: var(--ts-accent);
  border-bottom-color: var(--ts-accent-line);
}

.landing-header .content-center {
  margin-top: 0 !important;
  height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 内容垂直居中，确保在 .filter::after 霁罩和 hero-bottom-shade 之上 */
  position: relative;
  z-index: 3;
}

.landing-header .content-center .container {
  transform: translate3d(0, 24px, 0);
  max-width: 760px;
}

/* moving-clouds: 依赖 global.css 的定位 (bottom:0, width:250em, cloudLoop 80s) */
/* .landing-header .moving-clouds {
  transition: opacity 0.2s ease;
  pointer-events: none;
  z-index: 2;
} */

/* fog-low: 依赖 global.css 的定位 (margin-left:-35%, width:110%, bottom:0) */
.fog-low {
  pointer-events: none;
  z-index: 2;
  transition: opacity 0.2s ease;
  opacity: 0.38;
  /* margin-bottom: -35px; */
}

.fog-low.right {
  opacity: 0.5;
}

/* fog-low.right: 依赖 global.css 的 margin-left:30%; opacity:1 */

/* ---- Hero 刊头排版 ---- */

.hero-masthead {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  width: fit-content;
  margin: 0 auto 30px;
  padding-bottom: 16px;
  /* 与内容等宽的发丝线，做出杂志刊头的压线框感 */
  border-bottom: 1px solid rgba(250, 248, 244, 0.24);
}

.hero-masthead-name,
.hero-masthead-issue {
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
  color: rgba(250, 248, 244, 0.88);
  text-shadow: var(--hero-halo);
  white-space: nowrap;
}

.hero-masthead-line {
  width: 56px;
  height: 1px;
  background: rgba(250, 248, 244, 0.42);
  box-shadow: 0 0 8px rgba(6, 8, 14, 0.8);
}

.landing-header .title-brand {
  max-width: none;
  color: var(--ts-paper);
}

.landing-header .presentation-title {
  font-family: var(--ts-font-serif);
  font-size: clamp(48px, 8.4vw, 128px);
  font-weight: 700;
  font-style: normal;
  line-height: 0.98;
  letter-spacing: -0.015em;
  color: #f7f5f0;
  background: none;
  background-image: none;
  -webkit-background-clip: border-box;
  background-clip: border-box;
  -webkit-text-fill-color: currentColor;
  /* 大标题只加一层极淡的深色晕，避免糊边，同时让字口从星空里浮起来 */
  text-shadow: 0 0 34px rgba(6, 8, 14, 0.6);
}

.landing-header .presentation-subtitle {
  max-width: 620px;
  margin-top: 22px;
  color: rgba(250, 248, 244, 0.88);
  font-family: var(--ts-font-sans);
  font-size: clamp(14px, 1.6vw, 17px);
  font-weight: 500;
  line-height: 1.85;
  letter-spacing: 0.06em;
  justify-self: center;
  text-shadow: var(--hero-halo);
}

.hero-footnote {
  margin: 26px 0 0;
  text-align: center;
  color: rgba(250, 248, 244, 0.8);
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  text-shadow: var(--hero-halo);
}

.hero-scroll {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin: 44px auto 0;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
  color: rgba(250, 248, 244, 0.86);
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
  text-shadow: var(--hero-halo);
  transition: color 0.3s var(--ts-ease);
}

.hero-scroll:hover {
  color: #ffb347;
}

.hero-scroll-line {
  display: block;
  width: 1px;
  box-shadow: 0 0 10px rgba(6, 8, 14, 0.85);
  height: 34px;
  background: currentColor;
  opacity: 0.5;
  transition: transform 0.4s var(--ts-ease), opacity 0.4s var(--ts-ease);
}

.hero-scroll:hover .hero-scroll-line {
  transform: scaleY(1.35);
  opacity: 1;
}

.hero-bottom-shade {
  position: absolute;
  inset: auto 0 0 0;
  height: 42%;
  z-index: 1;
  pointer-events: none;
  /* 夜空 → 下面浅色纸张的过渡：底部留一层微亮的地平线雾，避免生硬切断 */
  background: linear-gradient(
    to top,
    rgba(236, 236, 233, 0.92) 0%,
    rgba(236, 236, 233, 0.32) 46%,
    rgba(236, 236, 233, 0) 100%
  );
  transition: opacity 0.18s linear;
}


.form-section {
  margin-top: -96px;
  padding: 0 20px 96px;
  position: relative;
  z-index: 3;
}

.form-panel {
  max-width: 900px;
  margin: 0 auto;
  border: 1px solid var(--ts-rule);
  border-top: 2px solid var(--ts-ink);
  border-radius: 0;
  background: var(--ts-card);
  backdrop-filter: none;
  box-shadow: var(--ts-shadow);
  padding: 36px 40px 32px;
  transition: 0.25s var(--ts-ease);
}

.step {
  margin-bottom: 36px;
}

/* 编号索引 + 衬线栏目标题 + 发丝分隔线 */
.step-head {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--ts-rule);
}

.step-head span {
  flex: none;
  color: var(--ts-accent);
  font-family: var(--ts-font-mono);
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.16em;
  line-height: 1;
  transform: translateY(-2px);
}

.step-head h3 {
  margin: 0;
  font-family: var(--ts-font-serif);
  font-size: 23px;
  font-weight: 700;
  color: var(--ts-ink);
  line-height: 1.3;
  letter-spacing: -0.005em;
}

.grid {
  display: grid;
  gap: 4px 24px;
}

.grid4 {
  grid-template-columns: 1.5fr 1fr 1fr 0.8fr;
}

.grid-date {
  grid-template-columns: 1fr 0.6fr;
  margin-top: 4px;
}

.grid2 {
  grid-template-columns: 1fr 1fr;
}

.city-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.city-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.city-row-name {
  flex: 2;
  margin-bottom: 0;
}

.city-row-days {
  flex: 0.8;
  margin-bottom: 0;
}

.city-remove-btn {
  flex-shrink: 0;
  width: 36px;
  height: 40px;
  margin-bottom: 0;
  border: 1px solid var(--ts-rule-strong);
  border-radius: var(--ts-r-sm);
  background: transparent;
  color: var(--ts-ink-3);
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  transition: border-color 0.25s var(--ts-ease), color 0.25s var(--ts-ease),
    background 0.25s var(--ts-ease);
  display: flex;
  align-items: center;
  justify-content: center;
}

.city-remove-btn:hover {
  border-color: var(--ts-danger);
  color: var(--ts-danger);
  background: rgba(166, 58, 43, 0.05);
}

.city-add-btn {
  align-self: flex-start;
  margin-top: 6px;
  padding: 8px 16px;
  border: 1px dashed var(--ts-rule-strong);
  border-radius: var(--ts-r-sm);
  background: transparent;
  color: var(--ts-ink-2);
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
  cursor: pointer;
  transition: border-color 0.25s var(--ts-ease), color 0.25s var(--ts-ease),
    background 0.25s var(--ts-ease);
}

.city-add-btn:hover {
  border-color: var(--ts-accent);
  border-style: solid;
  background: var(--ts-accent-soft);
  color: var(--ts-accent);
}

.field-label {
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
  color: var(--ts-ink-3);
}

.field-input.ant-input,
.field-input.ant-input-lg,
.field-input.ant-input-number,
.field-input.ant-input-number-lg,
.field-input.ant-picker,
.field-select :deep(.ant-select-selector),
.field-textarea :deep(textarea),
.field-textarea :deep(.ant-input),
.field-textarea.ant-input,
.special-textarea.ant-input {
  border: 0 !important;
  border-bottom: 1px solid var(--ts-rule-strong) !important;
  border-radius: 0 !important;
  background: transparent !important;
  background-color: transparent !important;
  background-image: none !important;
  color: var(--ts-ink) !important;
  box-shadow: none !important;
  transition: border-color 0.25s var(--ts-ease);
}

/* 浏览器自动填充（Autofill）背景色修复 */
:deep(.field-input.ant-input:-webkit-autofill),
:deep(.field-input.ant-input:-webkit-autofill:hover),
:deep(.field-input.ant-input:-webkit-autofill:focus),
:deep(.field-input.ant-input:-webkit-autofill:active),
:deep(.field-input .ant-picker-input > input:-webkit-autofill),
:deep(.field-textarea textarea:-webkit-autofill),
:deep(.special-textarea:-webkit-autofill) {
  -webkit-box-shadow: 0 0 0 1000px var(--ts-card) inset !important;
  -webkit-text-fill-color: var(--ts-ink) !important;
  transition: background-color 5000s ease-in-out 0s !important;
}

.field-input.ant-input-number :deep(.ant-input-number-input),
.field-input.ant-input-number :deep(.ant-input-number-handler-wrap) {
  color: var(--ts-ink) !important;
}

.field-input.ant-input::placeholder,
:deep(.field-input .ant-picker-input > input::placeholder),
.field-textarea :deep(textarea::placeholder),
.field-textarea.ant-input::placeholder {
  color: var(--ts-ink-4) !important;
}

.field-input.ant-input:hover,
.field-input.ant-picker:hover,
.field-select:hover :deep(.ant-select-selector),
.field-textarea :deep(textarea:hover),
.field-textarea.ant-input:hover {
  border-bottom-color: var(--ts-ink-3) !important;
}

.field-input.ant-input:focus,
.field-input.ant-picker-focused,
.field-textarea :deep(textarea:focus),
.field-textarea.ant-input:focus {
  border-bottom-color: var(--ts-accent) !important;
  box-shadow: none !important;
  background: transparent !important;
  outline: none !important;
}

.field-select:focus-within :deep(.ant-select-selector),
.field-select.ant-select-focused :deep(.ant-select-selector) {
  border-bottom-color: var(--ts-accent) !important;
}

:deep(.field-input .ant-picker-input > input),
.field-select :deep(.ant-select-selection-item),
:deep(.field-input .ant-picker-suffix),
:deep(.field-input .ant-picker-clear),
.field-select :deep(.ant-select-arrow) {
  color: var(--ts-ink) !important;
}

.days-chip {
  min-height: 40px;
  border-radius: 0;
  border: 0;
  border-bottom: 1px solid var(--ts-accent);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
}

.days-number {
  color: var(--ts-ink);
  font-family: var(--ts-font-serif);
  font-size: 26px;
  line-height: 1;
  font-weight: 700;
}

.days-unit {
  font-family: var(--ts-font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: var(--ts-tracking-caps);
  color: var(--ts-ink-3);
  font-weight: 500;
}

.interest-grid {
  width: 100%;
}

.interest-group {
  display: grid !important;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  width: 100%;
}

.interest-group :deep(.ant-checkbox-wrapper) {
  display: none !important;
}

.interest-pill {
  min-height: 42px;
  border-radius: 0;
  border: 1px solid var(--ts-rule);
  background: transparent;
  color: var(--ts-ink-2);
  font-size: 12px;
  letter-spacing: 0.02em;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  user-select: none;
  transition: border-color 0.3s var(--ts-ease), color 0.3s var(--ts-ease),
    background 0.3s var(--ts-ease);
}

.interest-pill:hover {
  background: var(--ts-paper-2);
  border-color: var(--ts-rule-strong);
  box-shadow: none;
}

.interest-pill:active {
  transform: translateY(1px);
  box-shadow: none;
}

.interest-pill.active {
  border-color: var(--ts-accent);
  background: var(--ts-accent-soft);
  color: var(--ts-accent);
  font-weight: 600;
}

.interest-pill.active:hover {
  background: rgba(176, 67, 31, 0.16);
  border-color: var(--ts-accent);
}

.submit-btn {
  width: 100%;
  min-height: 52px;
  border-radius: 0;
  background-color: var(--ts-accent) !important;
  background-image: none !important;
  border-color: var(--ts-accent) !important;
  color: var(--ts-paper) !important;
  box-shadow: none !important;
  font-family: var(--ts-font-mono);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
  cursor: pointer;
  transition: background 0.25s var(--ts-ease);
}

.submit-btn:hover,
.submit-btn:focus {
  background-color: var(--ts-accent-deep) !important;
  border-color: var(--ts-accent-deep) !important;
  color: var(--ts-paper) !important;
}

.submit-btn.loading {
  background: var(--ts-ink-4) !important;
  cursor: wait;
}

.loading-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  border: 2px solid rgba(250, 248, 244, 0.4);
  border-top-color: var(--ts-paper);
  animation: spin 0.8s linear infinite;
}

.spinner-small {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2.5px solid var(--ts-accent-line);
  border-top-color: var(--ts-accent);
  animation: spin 0.8s linear infinite;
}

/* 节点动画相关样式 */
.stepper-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 480px;
  animation: fadeIn 0.4s ease;
  padding: 30px 20px;
  box-sizing: border-box;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.stepper-header {
  text-align: center;
  margin-bottom: 50px;
}

.stepper-title {
  font-family: var(--ts-font-mono);
  font-size: 15px;
  font-weight: 500;
  color: var(--ts-ink);
  margin-bottom: 10px;
  letter-spacing: var(--ts-tracking-caps);
  text-transform: uppercase;
}

.stepper-subtitle {
  font-size: 14px;
  color: var(--ts-ink-3);
}

.stepper-container {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  width: 100%;
  max-width: 680px;
  margin: 0 auto 50px auto;
}

.step-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100px;
  z-index: 2;
}

.node-icon {
  width: 52px;
  height: 52px;
  border-radius: 0;
  background: var(--ts-paper-2);
  border: 1px solid var(--ts-rule);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
  color: var(--ts-ink-4);
  transition: border-color 0.35s var(--ts-ease), background 0.35s var(--ts-ease),
    color 0.35s var(--ts-ease);
}

.step-node.active .node-icon {
  border-color: var(--ts-accent);
  background: var(--ts-accent-soft);
  color: var(--ts-accent);
  box-shadow: none;
}

.step-node.completed .node-icon {
  background: var(--ts-ink);
  border-color: var(--ts-ink);
  color: var(--ts-paper);
  box-shadow: none;
}

.node-text {
  font-family: var(--ts-font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--ts-ink-4);
  text-align: center;
  transition: color 0.35s var(--ts-ease);
  line-height: 1.5;
}

.step-node.active .node-text {
  color: var(--ts-accent);
}

.step-node.completed .node-text {
  color: var(--ts-ink);
}

.step-divider {
  flex: 1;
  height: 1px;
  background: var(--ts-rule);
  margin-top: 26px;
  border-radius: 0;
  position: relative;
  overflow: hidden;
}

.step-divider::after {
  content: '';
  position: absolute;
  top: 0; left: 0; bottom: 0; width: 0%;
  background: var(--ts-ink);
  transition: width 0.45s var(--ts-ease);
}

.step-divider.completed::after {
  width: 100%;
}

.stepper-footer {
  text-align: center;
  margin-top: 10px;
}

.stepper-footer h3 {
  font-family: var(--ts-font-serif);
  font-size: 22px;
  font-weight: 700;
  color: var(--ts-ink);
  margin-bottom: 10px;
}

.stepper-footer p {
  font-size: 14px;
  color: var(--ts-ink-3);
}

:deep(.ant-form-item-label > label) {
  color: transparent !important;
}

:deep(.ant-form-item-explain-error) {
  color: var(--ts-danger) !important;
}

/* @keyframes cloudLoop {
  from {
    transform: translate3d(0, 0, 0);
  }
  to {
    transform: translate3d(-50%, 0, 0);
  }
} */

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1080px) {
  .grid4 {
    grid-template-columns: 1fr 1fr;
  }

  .interest-group {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 991px) {
  .hero-frame {
    inset: 76px 16px 16px;
  }

  .hero-rail {
    display: none;
  }

  .hero-masthead {
    gap: 10px;
    margin-bottom: 20px;
  }

  .form-section {
    padding: 0 14px 80px;
  }

  .form-panel {
    padding: 26px 20px 22px;
  }

  .grid4,
  .grid2,
  .grid-date {
    grid-template-columns: 1fr;
  }

  .history-section {
    padding: 0 16px 72px;
  }

  .history-title {
    font-size: 26px;
  }

  .step-head h3 {
    font-size: 20px;
  }
}

@media (max-width: 520px) {
  .landing-header .presentation-title {
    font-size: clamp(38px, 13vw, 60px);
  }

  .landing-header .presentation-subtitle {
    font-size: 13px;
    padding: 0 10px;
    line-height: 1.8;
  }

  .landing-header .content-center .container {
    transform: translate3d(0, 12px, 0);
  }

  .hero-masthead-name {
    display: none;
  }

  .hero-footnote {
    font-size: 9px;
    letter-spacing: 0.08em;
  }

  .hero-scroll {
    margin-top: 32px;
  }

  .interest-group {
    grid-template-columns: repeat(2, 1fr);
  }

  .history-item {
    gap: 12px;
  }

  .history-item::before {
    width: 22px;
  }

  .history-city {
    font-size: 18px;
  }

  .step-head {
    gap: 12px;
  }
}
</style>
