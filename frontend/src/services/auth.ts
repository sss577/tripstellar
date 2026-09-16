// 用户认证服务：状态管理 + API 封装（无 pinia，模块级响应式状态）

import { reactive } from 'vue'
import apiClient, {
  AUTH_EXPIRED_EVENT,
  clearAuthTokens,
  getAccessToken,
  getRefreshToken,
  setAuthTokens,
} from './api'
import type { LoginPayload, RegisterPayload, TokenPair, UpdateProfilePayload, UserInfo } from '@/types'

interface AuthApiResponse {
  success: boolean
  message?: string
  data?: TokenPair
  user?: UserInfo
}

interface UserApiResponse {
  success: boolean
  message?: string
  data?: UserInfo
}

export const authState = reactive<{
  user: UserInfo | null
  ready: boolean
}>({
  user: null,
  ready: false,
})

const extractError = (error: any, fallback: string): string =>
  error?.response?.data?.detail || error?.message || fallback

const applyAuthResult = (body: AuthApiResponse): UserInfo | null => {
  if (body.data?.access_token && body.data?.refresh_token) {
    setAuthTokens(body.data.access_token, body.data.refresh_token)
  }
  authState.user = body.user ?? authState.user
  return authState.user
}

/** 登录（用户名或邮箱） */
export async function login(payload: LoginPayload): Promise<UserInfo> {
  try {
    const response = await apiClient.post<AuthApiResponse>('/api/auth/login', payload)
    const user = applyAuthResult(response.data)
    if (!user) throw new Error('登录响应缺少用户信息')
    return user
  } catch (error: any) {
    throw new Error(extractError(error, '登录失败'))
  }
}

/** 注册（成功后直接进入登录态） */
export async function register(payload: RegisterPayload): Promise<UserInfo> {
  try {
    const response = await apiClient.post<AuthApiResponse>('/api/auth/register', payload)
    const user = applyAuthResult(response.data)
    if (!user) throw new Error('注册响应缺少用户信息')
    return user
  } catch (error: any) {
    throw new Error(extractError(error, '注册失败'))
  }
}

/** 退出登录：立即清空本地登录态；后端吊销 refresh token 失败或超时均不阻塞登出 */
export async function logout(): Promise<void> {
  const refreshToken = getRefreshToken()
  const accessToken = getAccessToken()

  // 先清本地登录态，确保 UI 立即响应（不被挂起的网络请求阻塞）
  clearAuthTokens()
  authState.user = null

  if (refreshToken) {
    // fire-and-forget 吊销请求：携带原 token，5 秒超时，结果一律忽略
    void apiClient
      .post(
        '/api/auth/logout',
        { refresh_token: refreshToken },
        {
          timeout: 5000,
          ...(accessToken ? { headers: { Authorization: `Bearer ${accessToken}` } } : {}),
        }
      )
      .catch(() => undefined)
  }
}

/** 拉取当前用户信息 */
export async function fetchMe(): Promise<UserInfo | null> {
  if (!getAccessToken()) return null
  try {
    const response = await apiClient.get<UserApiResponse>('/api/auth/me')
    authState.user = response.data?.data ?? null
    return authState.user
  } catch {
    return null
  }
}

/** 更新用户资料（昵称 / 头像URL） */
export async function updateProfile(payload: UpdateProfilePayload): Promise<UserInfo> {
  try {
    const response = await apiClient.put<UserApiResponse>('/api/auth/me', payload)
    const user = response.data?.data
    if (!user) throw new Error('更新资料响应缺少用户信息')
    authState.user = user
    return user
  } catch (error: any) {
    throw new Error(extractError(error, '更新资料失败'))
  }
}

/** 修改密码（成功后吊销全部登录态） */
export async function changePassword(oldPassword: string, newPassword: string): Promise<void> {
  try {
    await apiClient.put('/api/auth/password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    clearAuthTokens()
    authState.user = null
  } catch (error: any) {
    throw new Error(extractError(error, '修改密码失败'))
  }
}

/** 应用启动时恢复登录态 */
export async function initAuth(): Promise<void> {
  await fetchMe()
  authState.ready = true
}

// 令牌彻底失效（refresh 也失败）时清空用户态
if (typeof window !== 'undefined') {
  window.addEventListener(AUTH_EXPIRED_EVENT, () => {
    authState.user = null
  })
}
