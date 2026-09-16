import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import './styles/global.css'
import App from './App.vue'
import Landing from './views/Landing.vue'
import Result from './views/Result.vue'
import Login from './views/Login.vue'
import Profile from './views/Profile.vue'
import { i18n } from './i18n'
import { authState, initAuth } from './services/auth'
import { AUTH_EXPIRED_EVENT } from './services/api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Landing',
      component: Landing
    },
    {
      path: '/result',
      name: 'Result',
      component: Result
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/profile',
      name: 'Profile',
      component: Profile
    }
  ]
})

// 路由守卫：强制登录（/login 之外的所有页面均需登录态）
// 先启动登录态恢复，守卫等待其完成，避免整页刷新时误判踢回登录页
const authReady = initAuth()

router.beforeEach(async (to) => {
  await authReady.catch(() => undefined)

  if (to.path === '/login') {
    // 已登录访问登录页 → 回首页
    if (authState.user) return { path: '/' }
    return true
  }
  if (!authState.user) {
    return {
      path: '/login',
      query: to.fullPath && to.fullPath !== '/' ? { redirect: to.fullPath } : undefined,
    }
  }
  return true
})

const app = createApp(App)

app.use(router)
app.use(Antd)
app.use(i18n)

app.mount('#app')

// 令牌彻底失效（refresh 也失败）时跳转登录页
if (typeof window !== 'undefined') {
  window.addEventListener(AUTH_EXPIRED_EVENT, () => {
    const current = router.currentRoute.value
    if (current.path !== '/login') {
      router.push({ path: '/login', query: current.path !== '/' ? { redirect: current.fullPath } : undefined })
    }
  })
}
