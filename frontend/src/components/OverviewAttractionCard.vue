<template>
  <div class="swiper-slide" :class="{ 'swiper-slide-active': active }" @mouseenter="emit('hover')" @focusin="emit('hover')">
    <div class="swiper-slide-img">
      <img :src="imageSrc" :alt="item.name" loading="lazy" @error="emit('image-error', $event)" />
      <svg data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 120" preserveAspectRatio="none">
        <path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" class="shape-fill"></path>
        <path d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" opacity=".5" class="shape-fill"></path>
        <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" class="shape-fill"></path>
      </svg>
    </div>
    <div class="swiper-slide-content">
      <div>
        <h2>{{ item.name }}</h2>
        <p>{{ item.description || item.address || t('common.noData') }}</p>
        <a class="show-more" href="#" target="_self" @click.prevent="emit('select-day', item.dayArrayIndex)">
          <svg fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17.25 8.25L21 12m0 0l-3.75 3.75M21 12H3"></path>
          </svg>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

type OverviewAttractionItem = {
  name: string
  address: string
  visit_duration: number
  description: string
  dayArrayIndex: number
}

defineProps<{
  item: OverviewAttractionItem
  imageSrc: string
  active: boolean
}>()

const emit = defineEmits<{
  (e: 'hover'): void
  (e: 'select-day', dayArrayIndex: number): void
  (e: 'image-error', event: Event): void
}>()

const { t } = useI18n()
</script>

<style scoped lang="scss">
/* 字体统一由 global.css 令牌层提供，此处不再重复 @import */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: var(--ts-font-sans);
}
body {
  background: var(--ts-paper);
}
main {
  position: relative;
  width: calc(min(90rem, 90%));
  margin: 0 auto;
  display: flex;
  align-items: center;
  min-height: 100vh;
  min-height: 100svh;
  column-gap: 3rem;
  padding-block: min(20vh, 3rem);
}
.swiper {
  width: 100%;
  padding: 1.875rem 0;
}
.swiper-slide {
  width: 10.75rem;
  height: 25rem;
  display: flex;
  flex-direction: column;
  justify-content: end;
  align-items: self-start;
  box-shadow: none;
  border: 1px solid var(--ts-rule);
  border-radius: 0;
  background-color: var(--ts-card);
  overflow: hidden;
  position: relative;
  transition: border-color 0.4s var(--ts-ease);

  &:hover {
    box-shadow: none;
    border-color: var(--ts-rule-strong);
  }

  &-img {
    position: relative;
    width: 100%;
    height: 18rem;
    flex-shrink: 0;
    overflow: hidden;
    line-height: 0;
    background-color: var(--ts-paper-3);

    img {
      width: 100%;
      height: 100%;
      position: absolute;
      inset: 0;
      object-fit: cover;
      z-index: 0;
      transition: transform 0.7s var(--ts-ease);
    }

    svg {
      position: absolute;
      bottom: -1px;
      left: 0;
      display: block;
      width: calc(300% + 1.3px);
      height: 5rem;
      transform: scaleY(-1);
      z-index: 1;
    }
    .shape-fill {
      fill: var(--ts-card);
    }
  }

  &-content {
    position: relative;
    z-index: 2;
    background: var(--ts-card);
    border-radius: 0;
    padding: 0 1.4rem;
    flex: 1;
    display: flex;
    flex-direction: column;
    width: 100%;

    > div {
      // transform: translateY(-0.75rem);
    }

    h2 {
      color: var(--ts-ink);
      font-family: var(--ts-font-serif);
      font-weight: 700;
      font-size: 1.25rem;
      line-height: 1.35;
      margin-bottom: 0.5rem;
      text-transform: none;
      letter-spacing: -0.005em;
      white-space: nowrap;
      text-overflow: ellipsis;
    }

    p {
      color: var(--ts-ink-2) !important;
      line-height: 1.7;
      font-size: 0.85rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .show-more {
      width: 2.5rem;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--ts-accent);
      border-radius: 0;
      box-shadow: none;
      margin-top: 1em;
      margin-bottom: 0.9em;
      height: 0;
      opacity: 0;
      overflow: hidden;
      transition: opacity 0.3s var(--ts-ease), height 0.3s var(--ts-ease);
      margin-left: auto;

      &:hover {
        background: var(--ts-accent-deep);
      }

      svg {
        width: 1.5rem;
        color: var(--ts-paper);
      }
    }
  }
}

/* 当前选中（焦点）卡的视觉强调 */
.swiper-slide-active {
  box-shadow: none;
  border-color: var(--ts-rule-strong);
}

/* 悬停仅做轻微推近，保持克制的编辑式节奏 */
.swiper-slide:hover img {
  transform: scale(1.04);
}

.swiper-slide:hover .show-more {
  opacity: 1;
  height: 2.5rem;
}

.swiper-slide:hover p {
  display: block;
  overflow: visible;
}

.swiper-3d .swiper-slide-shadow-left,
.swiper-3d .swiper-slide-shadow-right {
  background-image: none;
}

@media screen and (min-width: 93.75rem) {
  .swiper {
    width: 85%;
  }
}
</style>
