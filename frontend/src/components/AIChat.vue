<template>
  <div class="ai-chat-floating">
    <div class="container-ai-input">
      <div v-for="index in 15" :key="`chat-area-${index}`" class="area"></div>
      <div class="container-wrap" :class="{ open: chatOpen }">
        <div class="card">
          <div class="background-blur-balls">
            <div class="balls">
              <span class="ball rosa"></span>
              <span class="ball violet"></span>
              <span class="ball green"></span>
              <span class="ball cyan"></span>
            </div>
          </div>
          <div
            class="content-card"
            :class="{ clickable: !chatOpen }"
            ref="launcherRef"
            @click="openChatPanel"
            @pointermove="handleLauncherPointerMove"
            @pointerleave="resetLauncherTilt"
          >
            <div class="background-blur-card">
              <div class="launcher-mark">
                <span class="launcher-star" aria-hidden="true">
                  <span class="launcher-star-roll">
                    <span class="launcher-star-face">
                      <span class="launcher-star-flow"></span>
                      <span class="launcher-star-spec"></span>
                    </span>
                  </span>
                </span>
                <span class="launcher-pulse" aria-hidden="true"></span>
              </div>
            </div>
          </div>
          <div
            class="launcher-hint"
            :class="{ visible: launcherHintVisible }"
            role="button"
            tabindex="0"
            @click.stop="openChatPanel"
            @keydown.enter.prevent="openChatPanel"
            @keydown.space.prevent="openChatPanel"
          >
            <span class="launcher-hint-tail" aria-hidden="true"></span>
            <span class="launcher-hint-dot" aria-hidden="true"></span>
            <span class="launcher-hint-text">{{ t(launcherHintKey) }}</span>
          </div>
          <div class="container-ai-chat" @click.stop>
            <div class="chat">
              <div class="chat-head">
                <span class="chat-head-mark" aria-hidden="true"></span>
                <span class="chat-head-title">{{ t('result.chat.title') }}</span>
                <button type="button" class="chat-close-btn" @click.stop="closeChatPanel">×</button>
              </div>
              <div class="chat-bot">
                <div class="chat-history" ref="chatMessagesRef">
                  <div v-if="chatHistory.length === 0" class="chat-empty">
                    <p class="chat-empty-lead">{{ t('result.chat.welcome') }}</p>
                    <div class="chat-suggestions">
                      <button
                        v-for="question in quickQuestions"
                        :key="question.labelKey"
                        type="button"
                        class="chat-suggestion"
                        :disabled="chatLoading || !tripPlan"
                        @click="sendQuickQuestion(t(question.questionKey))"
                      >
                        <span class="chat-suggestion-text">{{ t(question.labelKey) }}</span>
                        <span class="chat-suggestion-arrow" aria-hidden="true">→</span>
                      </button>
                    </div>
                  </div>
                  <div
                    v-for="(msg, idx) in chatHistory"
                    :key="`chat-${idx}`"
                    class="chat-msg"
                    :class="msg.role"
                  >
                    {{ msg.content }}
                  </div>
                  <div v-if="chatLoading" class="chat-msg assistant typing">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                  </div>
                </div>
                <textarea
                  v-model="chatInput"
                  :placeholder="chatPlaceholder"
                  name="chat_bot"
                  id="chat_bot"
                  :disabled="chatLoading || !tripPlan"
                  @keydown.enter.exact.prevent="sendChatMessage"
                ></textarea>
              </div>
              <div class="options">
                <div class="btns-add">
                  <button type="button" disabled>
                    <svg
                      viewBox="0 0 24 24"
                      height="20"
                      width="20"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M7 8v8a5 5 0 1 0 10 0V6.5a3.5 3.5 0 1 0-7 0V15a2 2 0 0 0 4 0V8"
                        stroke-width="2"
                        stroke-linejoin="round"
                        stroke-linecap="round"
                        stroke="currentColor"
                        fill="none"
                      ></path>
                    </svg>
                  </button>
                  <button type="button" disabled>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="20"
                      height="20"
                      viewBox="0 0 24 24"
                    >
                      <path
                        fill="none"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M4 5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1zm0 10a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1zm10 0a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1zm0-8h6m-3-3v6"
                      ></path>
                    </svg>
                  </button>
                  <button type="button" disabled>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="20"
                      height="20"
                      viewBox="0 0 24 24"
                    >
                      <path
                        fill="currentColor"
                        d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10s-4.477 10-10 10m-2.29-2.333A17.9 17.9 0 0 1 8.027 13H4.062a8.01 8.01 0 0 0 5.648 6.667M10.03 13c.151 2.439.848 4.73 1.97 6.752A15.9 15.9 0 0 0 13.97 13zm9.908 0h-3.965a17.9 17.9 0 0 1-1.683 6.667A8.01 8.01 0 0 0 19.938 13M4.062 11h3.965A17.9 17.9 0 0 1 9.71 4.333A8.01 8.01 0 0 0 4.062 11m5.969 0h3.938A15.9 15.9 0 0 0 12 4.248A15.9 15.9 0 0 0 10.03 11m4.259-6.667A17.9 17.9 0 0 1 15.973 11h3.965a8.01 8.01 0 0 0-5.648-6.667"
                      ></path>
                    </svg>
                  </button>
                </div>
                <button
                  type="button"
                  class="btn-submit"
                  :disabled="chatLoading || !chatInput.trim() || !tripPlan"
                  @click="sendChatMessage"
                >
                  <i>
                    <svg viewBox="0 0 512 512">
                      <path
                        d="M473 39.05a24 24 0 0 0-25.5-5.46L47.47 185h-.08a24 24 0 0 0 1 45.16l.41.13l137.3 58.63a16 16 0 0 0 15.54-3.59L422 80a7.07 7.07 0 0 1 10 10L226.66 310.26a16 16 0 0 0-3.59 15.54l58.65 137.38c.06.2.12.38.19.57c3.2 9.27 11.3 15.81 21.09 16.25h1a24.63 24.63 0 0 0 23-15.46L478.39 64.62A24 24 0 0 0 473 39.05"
                        fill="currentColor"
                      ></path>
                    </svg>
                  </i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import type { ChatMessage, TripPlan } from '@/types'
import { getRuntimeApiBaseUrl } from '@/services/api'

const props = defineProps<{
  tripPlan: TripPlan | null
}>()

const { t } = useI18n()
const chatOpen = ref(false)
const chatInput = ref('')
const chatHistory = ref<ChatMessage[]>([])
const chatLoading = ref(false)
const chatMessagesRef = ref<HTMLElement | null>(null)

// ===== 启动器互动 =====
const launcherRef = ref<HTMLElement | null>(null)
const launcherHintVisible = ref(false)
/** 气泡文案保存成 i18n key，切换语言时可即时更新 */
const launcherHintKey = ref('result.chat.greetEvening')
let hintShowTimer: number | null = null
let hintHideTimer: number | null = null

/** 首次提示延时 / 气泡停留时长 / 两轮提示之间的间隔（毫秒） */
const HINT_FIRST_DELAY = 1500
const HINT_VISIBLE_MS = 7000
const HINT_REPEAT_INTERVAL = 45000
/** 关闭面板后重新开始问候的间隔 */
const HINT_RESUME_DELAY = 8000

/** 按当前时间挑选问候语（早/中/下午/晚） */
const pickGreetingKey = () => {
  const hour = new Date().getHours()
  if (hour >= 5 && hour < 11) return 'result.chat.greetMorning'
  if (hour >= 11 && hour < 14) return 'result.chat.greetNoon'
  if (hour >= 14 && hour < 18) return 'result.chat.greetAfternoon'
  return 'result.chat.greetEvening'
}

/** 机器人跟随光标：把指针在启动器内的相对位置换算成 -1~1，再写成 CSS 变量驱动倾斜 */
const handleLauncherPointerMove = (event: PointerEvent) => {
  const el = launcherRef.value
  if (!el || chatOpen.value) return
  const rect = el.getBoundingClientRect()
  if (!rect.width || !rect.height) return
  const nx = Math.max(-1, Math.min(1, ((event.clientX - rect.left) / rect.width - 0.5) * 2))
  const ny = Math.max(-1, Math.min(1, ((event.clientY - rect.top) / rect.height - 0.5) * 2))
  el.style.setProperty('--bot-ry', `${(nx * 13).toFixed(2)}deg`)
  el.style.setProperty('--bot-rx', `${(-ny * 9).toFixed(2)}deg`)
  el.style.setProperty('--bot-tx', `${(nx * 7).toFixed(2)}px`)
  el.style.setProperty('--bot-ty', `${(ny * 7).toFixed(2)}px`)
}

/** 指针离开后回到正位 */
const resetLauncherTilt = () => {
  const el = launcherRef.value
  if (!el) return
  el.style.setProperty('--bot-ry', '0deg')
  el.style.setProperty('--bot-rx', '0deg')
  el.style.setProperty('--bot-tx', '0px')
  el.style.setProperty('--bot-ty', '0px')
}

const clearLauncherHintTimers = () => {
  if (hintShowTimer !== null) {
    window.clearTimeout(hintShowTimer)
    hintShowTimer = null
  }
  if (hintHideTimer !== null) {
    window.clearTimeout(hintHideTimer)
    hintHideTimer = null
  }
}

/** 展示一次问候气泡：每次按当下时间刷新文案，停留数秒后收起并安排下一轮 */
const showLauncherHint = () => {
  if (chatOpen.value) return
  launcherHintKey.value = pickGreetingKey()
  launcherHintVisible.value = true
  hintHideTimer = window.setTimeout(() => {
    hintHideTimer = null
    launcherHintVisible.value = false
    scheduleLauncherHint(HINT_REPEAT_INTERVAL)
  }, HINT_VISIBLE_MS)
}

/** 延时若干毫秒后再展示一次气泡 */
const scheduleLauncherHint = (delay: number) => {
  clearLauncherHintTimers()
  hintShowTimer = window.setTimeout(() => {
    hintShowTimer = null
    showLauncherHint()
  }, delay)
}

/** 收起气泡并停止提示循环（打开面板、组件卸载时调用） */
const dismissLauncherHint = () => {
  clearLauncherHintTimers()
  launcherHintVisible.value = false
}

onMounted(() => {
  scheduleLauncherHint(HINT_FIRST_DELAY)
})

onBeforeUnmount(clearLauncherHintTimers)

const quickQuestions = [
  {
    labelKey: 'result.chat.quickPriceLabel',
    questionKey: 'result.chat.quickPriceQuestion',
  },
  {
    labelKey: 'result.chat.quickSuitabilityLabel',
    questionKey: 'result.chat.quickSuitabilityQuestion',
  },
  {
    labelKey: 'result.chat.quickMealLabel',
    questionKey: 'result.chat.quickMealQuestion',
  },
]

const chatPlaceholder = computed(() => {
  if (!props.tripPlan) return t('result.noTripPlanDesc')
  return t('result.chat.placeholder')
})

const scrollChatToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

watch(chatOpen, (open) => {
  if (open) {
    scrollChatToBottom()
    dismissLauncherHint()
    resetLauncherTilt()
  } else {
    // 关闭面板后隔一会儿继续问候
    scheduleLauncherHint(HINT_RESUME_DELAY)
  }
})

const openChatPanel = () => {
  if (!chatOpen.value) {
    chatOpen.value = true
  }
}

const closeChatPanel = () => {
  chatOpen.value = false
}

const sendQuickQuestion = (q: string) => {
  chatInput.value = q
  void sendChatMessage()
}

const sendChatMessage = async () => {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value || !props.tripPlan) return

  chatHistory.value.push({ role: 'user', content: text })
  chatInput.value = ''
  chatLoading.value = true
  scrollChatToBottom()

  try {
    const apiBase = getRuntimeApiBaseUrl()
    const res = await axios.post(`${apiBase}/api/chat/ask`, {
      message: text,
      trip_plan: props.tripPlan,
      history: chatHistory.value.slice(0, -1),
    })

    if (res.data.success) {
      chatHistory.value.push({ role: 'assistant', content: res.data.reply })
    } else {
      chatHistory.value.push({ role: 'assistant', content: t('result.chat.replyFallback') })
    }
  } catch (err) {
    console.error('Chat error:', err)
    chatHistory.value.push({ role: 'assistant', content: t('result.chat.networkError') })
  } finally {
    chatLoading.value = false
    scrollChatToBottom()
  }
}
</script>

<style scoped lang="scss">
.ai-chat-floating {
  position: fixed;
  left: 8px;
  bottom: 8px;
  z-index: 1000;
  /* 面板与气泡底色：比纯白更暗、更中性的纸面，降低大面积白底的亮度与暖调 */
  --ai-chat-surface: #f4f3f0;
  /* 组件按 1260×1100 的画布设计，这里统一缩放；调大数值即可整体放大机器人、气泡与面板 */
  transform: scale(0.36);
}

.container-ai-input {
  --perspective: 1000px;
  --translateY: 45px;
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  transform-style: preserve-3d;
}

.container-wrap {
  display: flex;
  align-items: center;
  justify-items: center;
  position: absolute;
  left: 0;
  bottom: 0;
  z-index: 9;
  transform-style: preserve-3d;
  cursor: default;
  padding: 4px;
  transition: all 0.3s ease;
}

.container-wrap:hover {
  padding: 0;
  /* 悬停时机器人轻微放大（变量由内层 transform 消费） */
  --bot-scale: 1.06;
}

/* 点击反馈：按下时轻微压扁，展开面板时不参与 */
.container-wrap:not(.open):active {
  transform: scale(0.94, 1.06);
}

.container-wrap:after {
  content: "";
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translateX(-50%) translateY(-50%);
  width: 12rem;
  height: 12rem;
  background-color: transparent;
  border: 0;
  border-radius: 0;
  transition: all 0.3s var(--ts-ease);
}

.container-wrap.open .launcher-mark {
  opacity: 0;
  pointer-events: none;
}

.container-wrap.open .content-card {
  width: 1260px;
  height: 1100px;
}

.container-wrap.open .background-blur-balls {
  border-radius: 0;
}

/* 面板展开时收起启动器光晕，避免在面板外圈留下暖色残影 */
.container-wrap.open .balls {
  opacity: 0;
}

/* 展开面板时恢复纸色底，避免启动器光晕从面板边缘漏出 */
.container-wrap.open:after,
.container-wrap.open .background-blur-balls {
  background-color: var(--ai-chat-surface);
}

.container-wrap.open .content-card::after {
  opacity: 0;
}

.container-wrap.open .container-ai-chat {
  opacity: 1;
  visibility: visible;
  z-index: 99999;
  pointer-events: auto;
}

.card {
  width: 100%;
  height: 100%;
  position: relative;
  transform-style: preserve-3d;
  will-change: transform;
  transition: all 0.6s var(--ts-ease);
  border-radius: 0;
  display: flex;
  align-items: flex-end;
  transform: translateZ(50px);
  justify-content: flex-start;
  /* Paper Kit 主题的 .card 自带白底和投影，会在机器人身后留下一个白色方块，这里显式清掉。
     启动器的暖色光晕由 .background-blur-balls 负责，展开时的纸色底也由它承担 */
  background-color: transparent;
  box-shadow: none;
}

.card:hover {
  box-shadow: none;
}

/* 主题的 .card:hover 会把卡片下移 10px，在启动器上表现为机器人往下跳一下，这里复位 */
.card:not(.card-plain):hover {
  transform: translateZ(50px);
}

/* 只保留一层暖色光晕垫在机器人身后，不再有实心底板 */
.background-blur-balls {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  z-index: -10;
  border-radius: 0;
  transition: all 0.3s var(--ts-ease);
  background-color: transparent;
  overflow: hidden;
}
/* 原来的四团暖色光晕会在启动器身后围出一圈方形光斑，已停用 */
.balls {
  display: none;
}

.background-blur-balls .ball {
  width: 6rem;
  height: 6rem;
  position: absolute;
  border-radius: 50%;
  filter: blur(30px);
  opacity: 0.14;
}

.background-blur-balls .ball.violet {
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--ts-accent);
}

.background-blur-balls .ball.green {
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--ts-accent-deep);
}

.background-blur-balls .ball.rosa {
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  background-color: var(--ts-accent);
}

.background-blur-balls .ball.cyan {
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  background-color: var(--ts-accent-deep);
}

.content-card {
  position: relative;
  width: 12rem;
  height: 12rem;
  display: flex;
  border-radius: 0;
  transition: all 0.3s var(--ts-ease);
  /* 允许机器人光圈与投影溢出，避免被裁切 */
  overflow: visible;
  /* 入场：从下方弹入并轻微回弹 */
  animation: robot-enter 0.9s var(--ts-ease) both;
}

.content-card.clickable {
  cursor: pointer;
}

.background-blur-card {
  width: 100%;
  height: 100%;
  background: transparent;
  backdrop-filter: none;
}

/* 启动器：彩色四角星（呼吸浮动 + 悬停跟随光标倾斜） */
.launcher-mark {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 160px;
  height: 160px;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  animation: robot-float 4.2s ease-in-out infinite;
  transition: opacity 0.3s var(--ts-ease);
  /* 给内层的倾斜变换一个景深，让跟随光标的转动有立体感 */
  perspective: 520px;
}

/* 光标跟随的载体：位移 + 倾斜 + 悬停放大，全部由 CSS 变量拼装。
   缓动用长尾缓出，指针移动时是「滑」过去而不是「跳」过去 */
.launcher-star {
  position: relative;
  display: block;
  width: 100%;
  height: 100%;
  transform: translate3d(var(--bot-tx, 0px), var(--bot-ty, 0px), 0)
    rotateX(var(--bot-rx, 0deg)) rotateY(var(--bot-ry, 0deg)) scale(var(--bot-scale, 1));
  transition: transform 0.42s cubic-bezier(0.16, 1, 0.3, 1), filter 0.5s var(--ts-ease);
  will-change: transform;
  /* 立体投影：filter 落在遮罩之外，投影跟着星形轮廓走。
     只留一层很轻的接触阴影，避免星星底下糊出一块暗斑 */
  filter: drop-shadow(0 5px 12px rgba(24, 20, 16, 0.16));
}

/* 星形遮罩：内部所有图层都会被裁成四角星 */
.launcher-star-face {
  position: absolute;
  inset: 0;
  display: block;
  overflow: hidden;
  /* 四角星路径遮罩定义在使用它的同一条规则里：变量一旦丢失，mask 会整条失效退化成方块 */
  --star-mask: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 0C12 6.6 17.4 12 24 12C17.4 12 12 17.4 12 24C12 17.4 6.6 12 0 12C6.6 12 12 6.6 12 0Z' fill='%23000'/%3E%3C/svg%3E");
  -webkit-mask: var(--star-mask) center / contain no-repeat;
  mask: var(--star-mask) center / contain no-repeat;
  animation: robot-breathe 5.6s ease-in-out infinite;
}

/* ① 彩色本体：锥形渐变缓慢旋转，颜色在星形内流动 */
.launcher-star-flow {
  position: absolute;
  inset: -30%;
  display: block;
  background: conic-gradient(
    from 0deg,
    #ff3d5a 0deg,
    #ff8a4a 36deg,
    #c86bff 64deg,
    #4a8cff 96deg,
    #34d1c4 138deg,
    #3ed98b 180deg,
    #a8d94a 224deg,
    #ffc247 272deg,
    #ff7a5c 324deg,
    #ff3d5a 360deg
  );
  animation: star-flow 18s linear infinite;
}

/* ② 高光面：左上受光，叠加出釉面质感 */
.launcher-star-spec {
  position: absolute;
  inset: 0;
  display: block;
  background: radial-gradient(
    circle at 34% 26%,
    rgba(255, 255, 255, 0.9) 0%,
    rgba(255, 255, 255, 0.3) 32%,
    rgba(255, 255, 255, 0) 60%
  );
  mix-blend-mode: screen;
}

/* ④ 悬停滚动：整体绕 Z 轴滚 90°。
   独立成层，用对称缓动做出「滚」的手感，与上层的「跟随光标」缓动互不干扰 */
.launcher-star-roll {
  position: absolute;
  inset: 0;
  display: block;
  transform: rotate(var(--star-roll, 0deg));
  transition: transform 0.62s cubic-bezier(0.65, 0, 0.35, 1);
  will-change: transform;
}

.container-wrap:hover .launcher-star-roll {
  --star-roll: 90deg;
}

@keyframes star-flow {
  to {
    transform: rotate(360deg);
  }
}

/* 右下角强调色呼吸点，暗示「可以问我」 */
.launcher-pulse {
  position: absolute;
  right: 34px;
  bottom: 34px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: var(--ts-accent);
  box-shadow: 0 0 0 4px var(--ts-card);
  animation: robot-pulse 2.4s ease-in-out infinite;
}

.container-wrap:hover .launcher-star {
  filter: drop-shadow(0 7px 16px rgba(24, 20, 16, 0.2))
    drop-shadow(0 0 22px rgba(255, 170, 90, 0.42));
}

.container-wrap:hover .launcher-pulse {
  background-color: var(--ts-accent-deep);
  animation-duration: 1.4s;
}

/* 启动器右侧的问候气泡：定时出现、自动收起、点击即可对话 */
.launcher-hint {
  position: absolute;
  left: calc(100% + 20px);
  bottom: 72px;
  display: inline-flex;
  align-items: center;
  gap: 16px;
  padding: 18px 32px;
  background: var(--ai-chat-surface);
  border: 1px solid var(--ts-rule-strong);
  color: var(--ts-ink);
  font-family: var(--ts-font-sans);
  font-size: 44px;
  font-weight: 700;
  letter-spacing: 0.02em;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transform: translateX(-14px) scale(0.94);
  transform-origin: left bottom;
  transition: opacity 0.45s var(--ts-ease), transform 0.45s var(--ts-ease),
    border-color 0.25s var(--ts-ease), color 0.25s var(--ts-ease);
}

.launcher-hint.visible {
  opacity: 1;
  transform: translateX(0) scale(1);
  pointer-events: auto;
  cursor: pointer;
}

.launcher-hint.visible:hover {
  border-color: var(--ts-accent);
  color: var(--ts-accent);
}

/* 指向机器人的气泡尖角 */
.launcher-hint-tail {
  position: absolute;
  left: -13px;
  bottom: 22px;
  width: 26px;
  height: 26px;
  background: var(--ai-chat-surface);
  border-left: 1px solid var(--ts-rule-strong);
  border-bottom: 1px solid var(--ts-rule-strong);
  transform: rotate(45deg);
  transition: border-color 0.25s var(--ts-ease);
}

.launcher-hint.visible:hover .launcher-hint-tail {
  border-left-color: var(--ts-accent);
  border-bottom-color: var(--ts-accent);
}

.launcher-hint-text {
  min-width: 0;
}

.launcher-hint-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--ts-accent);
  flex: none;
  animation: robot-pulse 2.4s ease-in-out infinite;
}

@keyframes robot-enter {
  0% {
    opacity: 0;
    transform: translateY(34px) scale(0.55);
  }
  62% {
    opacity: 1;
    transform: translateY(-8px) scale(1.05);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes robot-float {
  0%,
  100% {
    transform: translate(-50%, -50%) translateY(0);
  }
  50% {
    transform: translate(-50%, -50%) translateY(-10px);
  }
}

@keyframes robot-breathe {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.022);
  }
}

@keyframes robot-pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(0.72);
    opacity: 0.55;
  }
}

.container-ai-chat {
  position: absolute;
  width: 100%;
  height: 100%;
  padding: 32px;
  opacity: 0;
  pointer-events: none;
}

/* 面板页眉：栏目名 + 关闭，像刊物页眉一样把整块内容框住 */
.chat-head {
  flex: none;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 26px 26px 20px;
  border-bottom: 1px solid var(--ts-rule);
}

.chat-head-mark {
  width: 26px;
  height: 26px;
  flex: none;
  background: conic-gradient(from 0deg, #ff3d5a, #ffc247, #3ed98b, #4a8cff, #ff3d5a);
  /* 同一份四角星路径，页眉标记与启动器共用形状 */
  --star-mask: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 0C12 6.6 17.4 12 24 12C17.4 12 12 17.4 12 24C12 17.4 6.6 12 0 12C6.6 12 12 6.6 12 0Z' fill='%23000'/%3E%3C/svg%3E");
  -webkit-mask: var(--star-mask) center / contain no-repeat;
  mask: var(--star-mask) center / contain no-repeat;
}

.chat-head-title {
  flex: 1;
  min-width: 0;
  font-family: var(--ts-font-serif);
  font-size: 34px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--ts-ink);
}

.container-ai-chat .chat-close-btn {
  position: static;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border: none;
  border-radius: 0;
  background: transparent;
  color: var(--ts-ink-3);
  font-size: 44px;
  line-height: 1;
  cursor: pointer;
  transition: color 0.25s var(--ts-ease);
}

.container-ai-chat .chat-close-btn:hover {
  color: var(--ts-accent);
}

.container-wrap .card .chat {
  display: flex;
  flex-direction: column;
  border-radius: 0;
  border: 1px solid var(--ts-rule);
  width: 100%;
  height: 100%;
  padding: 0;
  overflow: hidden;
  background-color: var(--ai-chat-surface);
}

.container-wrap .card .chat .chat-bot {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
  min-height: 0;
  padding: 18px 26px 0;
  transition: all 0.3s ease;
}

.card .chat .chat-bot .chat-history {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  border-radius: 0;
  padding: 12px 2px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  background: transparent;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--ts-rule-strong);
    border-radius: 0;
  }
}

.card .chat .chat-bot .chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 30px;
  padding-bottom: 20px;
  color: var(--ts-ink-2);
}

/* 欢迎语：正文无衬线 + 高对比墨色，缩小后依旧清晰 */
.card .chat .chat-bot .chat-empty-lead {
  margin: 0;
  font-family: var(--ts-font-sans);
  font-size: 52px;
  font-weight: 600;
  line-height: 1.65;
  letter-spacing: 0.01em;
  color: var(--ts-ink);
}

.card .chat .chat-bot .chat-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  width: 100%;
}

/* 快捷问题：浅色药丸标签 + 深朱砂文字，悬停才填色，避免整块重色压住画面 */
.card .chat .chat-bot .chat-suggestion {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  border: 1px solid var(--ts-accent-line);
  border-radius: 0;
  padding: 20px 34px;
  font-family: var(--ts-font-sans);
  font-size: 46px;
  font-weight: 600;
  line-height: 1.2;
  letter-spacing: 0.01em;
  background-color: var(--ts-accent-soft);
  color: var(--ts-accent-deep);
  cursor: pointer;
  transition: background 0.25s var(--ts-ease), border-color 0.25s var(--ts-ease),
    color 0.25s var(--ts-ease);
}

.card .chat .chat-bot .chat-suggestion-arrow {
  font-size: 40px;
  line-height: 1;
  color: var(--ts-accent-deep);
  transition: transform 0.25s var(--ts-ease), color 0.25s var(--ts-ease);
}

.card .chat .chat-bot .chat-suggestion:hover {
  background-color: var(--ts-accent);
  border-color: var(--ts-accent);
  color: var(--ts-paper);
}

.card .chat .chat-bot .chat-suggestion:hover .chat-suggestion-arrow {
  color: var(--ts-paper);
  transform: translateX(5px);
}

.card .chat .chat-bot .chat-suggestion:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.card .chat .chat-bot .chat-suggestion:disabled .chat-suggestion-arrow {
  color: var(--ts-ink-4);
}

.card .chat .chat-bot .chat-msg {
  max-width: 92%;
  font-size: 44px;
  font-weight: 500;
  line-height: 1.65;
  border-radius: 0;
  border-left: 2px solid var(--ts-rule-strong);
  padding: 8px 20px;
  color: var(--ts-ink-2);
  background: transparent;
  white-space: pre-wrap;
  word-break: break-word;
}

.card .chat .chat-bot .chat-msg.user {
  margin-left: auto;
  background-color: transparent;
  border-left: 2px solid var(--ts-accent);
  color: var(--ts-ink);
  font-weight: 600;
  opacity: 1;
  filter: alpha(opacity=100);
}

.card .chat .chat-bot .chat-msg.assistant {
  margin-right: auto;
}

.card .chat .chat-bot .chat-msg.typing {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  width: fit-content;
}

.card .chat .chat-bot .chat-msg.typing .dot {
  width: 10px;
  height: 10px;
  border-radius: 0;
  background-color: var(--ts-accent);
  border-color: var(--ts-accent);
  color: var(--ts-paper);
  opacity: 1;
  filter: alpha(opacity=100);
  animation: aiChatDotPulse 1.4s infinite ease-in-out both;
}

.card .chat .chat-bot .chat-msg.typing .dot:nth-child(2) {
  animation-delay: 0.16s;
}

.card .chat .chat-bot .chat-msg.typing .dot:nth-child(3) {
  animation-delay: 0.32s;
}

.card .chat .chat-bot textarea {
  background-color: transparent;
  border-radius: 0;
  border: none;
  border-bottom: 1px solid var(--ts-rule-strong);
  width: 100%;
  min-height: 156px;
  max-height: 178px;
  color: var(--ts-ink);
  font-family: var(--ts-font-sans);
  font-size: 48px;
  font-weight: 500;
  padding: 10px 0;
  resize: none;
  outline: none;
  transition: border-color 0.25s var(--ts-ease);

  &::-webkit-scrollbar {
    width: 6px;
    height: 10px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--ts-rule-strong);
    border-radius: 0;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: var(--ts-ink-4);
    cursor: pointer;
  }

  &::placeholder {
    color: var(--ts-ink-3);
    transition: color 0.3s var(--ts-ease);
  }
  &:focus {
    border-bottom-color: var(--ts-accent);
  }
  &:focus::placeholder {
    color: var(--ts-ink-2);
  }
}

.card .chat .options {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: 18px 26px 22px;

  & button {
    transition: all 0.3s ease;
  }
}

.card .chat .options .btns-add {
  display: flex;
  gap: 16px;

  & button {
    display: flex;
    color: var(--ts-ink-3);
    background-color: transparent;
    border: none;
    cursor: pointer;
    transition: color 0.25s var(--ts-ease);

    & svg {
      width: 32px;
      height: 32px;
    }

    &:hover {
      transform: none;
      color: var(--ts-accent);
    }
  }
}

.card .chat .options .btn-submit {
  display: flex;
  padding: 15px;
  background-color: var(--ts-accent);
  border-color: var(--ts-accent);
  color: var(--ts-paper);
  opacity: 1;
  filter: alpha(opacity=100);
  border-radius: 0;
  box-shadow: none;
  cursor: pointer;
  border: none;
  outline: none;
  opacity: 0.85;
  transition: background 0.15s var(--ts-ease), opacity 0.15s var(--ts-ease);

  & i {
    width: 60px;
    height: 60px;
    padding: 6px;
    background: transparent;
    border-radius: 0;
    backdrop-filter: none;
    color: var(--ts-paper);
  }
  & svg {
    transition: color 0.3s var(--ts-ease);
  }
  &:hover {
    opacity: 1;
    background-color: var(--ts-accent-deep);
    & svg {
      color: var(--ts-paper);
      filter: none;
    }
  }

  &:focus svg {
    color: var(--ts-paper);
    filter: none;
    transform: none;
  }

  &:active {
    transform: none;
    opacity: 0.9;
  }
}

/* 禁用态：不靠整体透明，改成描边空心，避免变成一块发灰的粉块 */
.card .chat .options .btn-submit:disabled {
  background-color: transparent;
  box-shadow: inset 0 0 0 1px var(--ts-rule-strong);
  cursor: not-allowed;

  & i {
    color: var(--ts-ink-4);
  }
}

@keyframes aiChatDotPulse {
  0%, 80%, 100% {
    transform: scale(0.4);
    opacity: 0.4;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.area:nth-child(15):hover ~ .container-wrap .card,
.area:nth-child(15):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(-15deg) rotateY(15deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}
.area:nth-child(14):hover ~ .container-wrap .card,
.area:nth-child(14):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(-15deg) rotateY(7deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}
.area:nth-child(13):hover ~ .container-wrap .card,
.area:nth-child(13):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(-15deg) rotateY(0)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}
.area:nth-child(12):hover ~ .container-wrap .card,
.area:nth-child(12):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(-15deg) rotateY(-7deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}
.area:nth-child(11):hover ~ .container-wrap .card,
.area:nth-child(11):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(-15deg) rotateY(-15deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(10):hover ~ .container-wrap .card,
.area:nth-child(10):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(0) rotateY(15deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}
.area:nth-child(9):hover ~ .container-wrap .card,
.area:nth-child(9):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(0) rotateY(7deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}
.area:nth-child(8):hover ~ .container-wrap .card,
.area:nth-child(8):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(0) rotateY(0)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}
.area:nth-child(7):hover ~ .container-wrap .card,
.area:nth-child(7):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(0) rotateY(-7deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}
.area:nth-child(6):hover ~ .container-wrap .card,
.area:nth-child(6):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(0) rotateY(-15deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(5):hover ~ .container-wrap .card,
.area:nth-child(5):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(15deg) rotateY(15deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}
.area:nth-child(4):hover ~ .container-wrap .card,
.area:nth-child(4):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(15deg) rotateY(7deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}
.area:nth-child(3):hover ~ .container-wrap .card,
.area:nth-child(3):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(15deg) rotateY(0)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}
.area:nth-child(2):hover ~ .container-wrap .card,
.area:nth-child(2):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(15deg) rotateY(-7deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}
.area:nth-child(1):hover ~ .container-wrap .card,
.area:nth-child(1):hover ~ .container-wrap .eyes .eye {
  transform: perspective(var(--perspective)) rotateX(15deg) rotateY(-15deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(15):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(15):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(-10deg) rotateY(8deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(14):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(14):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(-10deg) rotateY(4deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(13):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(13):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(-10deg) rotateY(0deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(12):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(12):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(-10deg) rotateY(-4deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(11):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(11):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(-10deg) rotateY(-8deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(10):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(10):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(0deg) rotateY(8deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(9):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(9):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(0deg) rotateY(4deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(8):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(8):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(0deg) rotateY(0deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(7):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(7):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(0deg) rotateY(-4deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(6):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(6):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(0deg) rotateY(-8deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(5):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(5):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(10deg) rotateY(8deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(4):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(4):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(10deg) rotateY(4deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(3):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(3):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(10deg) rotateY(0deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(2):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(2):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(10deg) rotateY(-4deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

.area:nth-child(1):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .options
  button,
.area:nth-child(1):hover
  ~ .container-wrap
  .card
  .container-ai-chat
  .chat
  .chat-bot {
  transform: perspective(var(--perspective)) rotateX(10deg) rotateY(-8deg)
    translateZ(var(--translateY)) scale3d(1, 1, 1);
}

@keyframes rotate-background-balls {
  from {
    transform: translateX(-50%) translateY(-50%) rotate(360deg);
  }
  to {
    transform: translateX(-50%) translateY(-50%) rotate(0);
  }
}

@media (max-width: 768px) {
  .ai-chat-floating {
    left: 12px;
    bottom: 12px;
    width: 220px;
    height: 220px;
  }

  .container-wrap.open .content-card {
    width: 300px;
    height: 220px;
  }

  .container-wrap:after {
    width: 6.5rem;
    height: 6rem;
  }

  .container-wrap:hover:after {
    height: 6.5rem;
  }

  .content-card {
    width: 6.5rem;
    height: 6.5rem;
  }

  /* 小屏放宽：允许问候文案换行，避免气泡横向溢出 */
  .launcher-hint {
    left: calc(100% + 10px);
    bottom: 46px;
    gap: 10px;
    max-width: 560px;
    padding: 12px 22px;
    font-size: 32px;
    font-weight: 700;
    letter-spacing: 0.02em;
    line-height: 1.5;
    white-space: normal;
  }

  .launcher-hint-tail {
    left: -11px;
    bottom: 18px;
    width: 22px;
    height: 22px;
  }

  .launcher-hint-dot {
    width: 14px;
    height: 14px;
  }
}

/* ===== 编辑式杂志风覆盖：关闭随鼠标位置变化的 3D 倾斜，保持纸面平铺 ===== */
.area:hover ~ .container-wrap .card {
  transform: translateZ(50px) !important;
}

.area:hover ~ .container-wrap .eyes .eye {
  transform: none !important;
}

.area:hover ~ .container-wrap .card .container-ai-chat .chat .options button,
.area:hover ~ .container-wrap .card .container-ai-chat .chat .chat-bot {
  transform: none !important;
}
</style>
