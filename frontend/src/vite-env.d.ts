/// <reference types="vite/client" />

// 让 IDE 的 TypeScript 服务识别 .vue 单文件组件模块
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
