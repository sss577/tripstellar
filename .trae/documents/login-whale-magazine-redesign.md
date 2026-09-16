# 登录页重构：鲸鱼吞鱼群视频背景 + 杂志封面排版

## Summary

重构 `frontend/src/views/Login.vue`：全屏循环播放"鲸鲨穿过鱼群"水下视频作为背景，画面上叠加暗角（四角逐暗）与顶/底黑色渐变；前景改为**左右分栏杂志封面排版**——左侧超大刊头 + 杂志元素（期号/日期/引导语/分割线），右侧为现有登录/注册表单（玻璃拟态卡片延续现有风格）。登录/注册业务逻辑**完全不动**。

## 素材决策（已验证可用）

主选视频（St Helena 鲸鲨在鱼群中游弋，1080p，16 秒，适合循环）：

```
https://cdn.pixabay.com/video/2020/02/16/32451-392248983_large.mp4
```

- HTTP 200，`video/mp4`，9.9 MB，Pixabay Content License（免费商用、无需署名）
- 备选（若主选失效时替换 source 即可）：
  - 蓝鲸水下：`https://cdn.pixabay.com/video/2022/05/21/117702-713017028_large.mp4`（6.8 MB，已验证 200）
  - 鲸鲨特写：`https://cdn.pixabay.com/video/2022/07/27/125737-735655957_large.mp4`（6.0 MB，已验证 200）

## Current State Analysis

- [Login.vue](file:///c:\Users\29484\PycharmProjects\TripStar\frontend\src\views\Login.vue)：当前为深色渐变背景 + 居中 420px 玻璃卡片（登录/注册双 Tab + 语言选择器顶栏）；登录逻辑 `handleLogin/handleRegister`、`redirectAfterAuth` 已稳定运行
- 项目无本地视频资产；Landing 页远端图片（creative-tim）证明远端资源模式可行
- 设计风格基线：深色底（#0a0a0f 系）、金色强调（#FFD699 / #FFB347）、999px 胶囊、玻璃卡片 `rgba(12,23,32,0.72) + blur(22px)`、Montserrat 字体（global.css）
- i18n 三语结构：`auth.*` 段已有键，直接追加 `auth.magazine.*`

## Proposed Changes

### 1. `frontend/src/views/Login.vue`（核心改动）

**模板结构**（替换现有 `login-page` 内部骨架，script 逻辑零改动）：

```html
<div class="login-page">
  <!-- 视频背景：铺满全屏、循环 -->
  <video class="login-video" autoplay muted loop playsinline preload="auto"
         src="https://cdn.pixabay.com/video/2020/02/16/32451-392248983_large.mp4" />
  <!-- 暗角 + 顶/底黑色渐变，单层多背景实现 -->
  <div class="login-overlay"></div>

  <nav class="login-navbar"><!-- 保留现有 brand + 语言选择器 --></nav>

  <div class="login-magazine">
    <!-- 左栏：杂志封面排版 -->
    <div class="mag-cover">
      <div class="mag-meta">
        <span>{{ magazineDate }}</span>
        <span>{{ t('auth.magazine.issue') }}</span>
      </div>
      <h1 class="mag-masthead">TRIPSTAR</h1>
      <div class="mag-rule"></div>
      <p class="mag-deck">{{ t('auth.magazine.deck') }}</p>
      <p class="mag-tagline">{{ t('auth.magazine.tagline') }}</p>
      <div class="mag-footer">
        <span>AI TRAVEL PLANNING ENGINE</span>
        <span>{{ t('auth.magazine.edition') }}</span>
      </div>
    </div>

    <!-- 右栏：登录表单（保留现有 a-tabs 双 Tab 表单整体结构） -->
    <div class="login-card"><!-- 现有 login-head + login-tabs 结构原样迁入 --></div>
  </div>
</div>
```

**script 仅新增**：`magazineDate` 计算属性（按 locale 输出 `2026 / 08` 格式的年月，杂志封面日期风）；其余 handleLogin/handleRegister/表单校验全部保留。

**样式要点**：

- `.login-video`：`position:absolute; inset:0; width:100%; height:100%; object-fit:cover; z-index:0`；`.login-page` 保留现有深色渐变作视频加载失败兜底，`overflow:hidden`
- `.login-overlay`（暗角 + 顶/底渐变，一层多背景）：
  ```css
  background:
    radial-gradient(ellipse 130% 100% at 50% 50%, transparent 42%, rgba(0,0,0,0.34) 74%, rgba(0,0,0,0.68) 100%),
    linear-gradient(to bottom, rgba(3,5,10,0.78) 0%, transparent 22%),
    linear-gradient(to top, rgba(3,5,10,0.82) 0%, transparent 26%);
  ```
  radial 椭圆实现"四角边缘逐暗"，两条 linear 分别压暗顶部与底部
- `.login-magazine`：`position:relative; z-index:1; flex:1; display:grid; grid-template-columns: 1.2fr 1fr; gap`，整体在页面垂直居中、max-width 1200px
- 杂志左栏：
  - `.mag-masthead`：Montserrat 900、`clamp(64px, 9vw, 130px)`、uppercase、`letter-spacing: 0.02em`、白色、`text-shadow` 提升在视频上的可读性；换行 `TRIP-` / `STAR`（`white-space:pre-line`）
  - `.mag-meta`：两端对齐小字（日期左、期号右），11px、`letter-spacing:0.3em`、金色 #FFD699
  - `.mag-rule`：金色细线（1px，渐变透明两端）
  - `.mag-deck`：衬线斜体（`'Playfair Display', Georgia, 'Times New Roman', serif`——本地无 Playfair 时回退系统衬线，不新增网络字体依赖），18-22px、白 75%
  - `.mag-tagline`：正体小段引导语，白 55%
  - `.mag-footer`：贴左栏底部的两端对齐小字（10px、letter-spacing 0.26em、白 40%）
- 右栏 `.login-card`：沿用现有玻璃卡片样式，背景加深为 `rgba(5,10,18,0.66)`（视频上更清晰），backdrop-filter blur 22px 保留，max-width 400px 垂直自居中
- `prefers-reduced-motion: reduce` 时暂停视频（`.login-video { animation: none }` + JS `video.pause()` 兜底可不做，仅 CSS `@media` 内联处理播放属增强项——用 `autoplay` 失败兜底：视频 `error` 时 overlay 深色渐变背景已是全屏可用状态）
- **响应式**（≤960px）：`grid-template-columns: 1fr`，杂志刊头缩到 `clamp(44px, 12vw, 80px)` 居中显示，表单移到下方，`mag-footer` 隐藏；≤520px 沿用现有卡片内边距收缩

### 2. i18n 三语新增 `auth.magazine` 段

- `frontend/src/i18n/locales/zh.json`：
  ```json
  "magazine": {
    "issue": "VOL. 01 · 创刊号",
    "deck": "把每一次出发，都排进目录。",
    "tagline": "鲸吞山海的旅程，从这一页开始。登录后，你的专属旅行计划将永久存档。",
    "edition": "TRIP PLANNING ISSUE"
  }
  ```
- `en.json` / `ja.json` 同结构翻译（deck：英文衬线斜体气质 / 日文同风格）

## Assumptions & Decisions

- 视频为 Pixabay 免费商用素材，直链长期稳定（CDN 无签名、无过期参数）；不下载到 public/（用户已选在线直链方案）
- 杂志刊头 `TRIPSTAR` 保持英文（杂志刊头惯例），装饰性小字（AI TRAVEL PLANNING ENGINE 等）固定英文；deck/tagline 走 i18n
- 不引入新字体文件；衬线用系统回退栈，刊头沿用项目 Montserrat
- 业务逻辑（登录/注册/重定向/校验/message 提示）与表单组件结构零改动，仅重排布局与背景
- 暗角/渐变用单层 div 多背景实现，不加多余 DOM

## Verification steps

1. `npm run dev` 启动前端（后端已在跑），浏览器访问 `http://localhost:5173/login`
2. 截图检查：视频铺满全屏且循环、四角渐暗、顶部/底部黑渐变、左刊头右表单分栏、金色点缀
3. 功能回归：登录/注册/Tab 切换/语言切换/Enter 提交均正常，登录成功仍跳 redirect
4. 缩窄窗口到 960px / 520px 验证响应式换行
5. `npm run build`（vue-tsc）通过
