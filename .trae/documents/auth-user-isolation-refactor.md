# 登录模块与用户级历史规划隔离重构计划

## Summary

为 TripStar 引入完整的用户认证体系（强制登录），实现：
1. 用户注册/登录/登出/资料管理（后端 JWT 双 token + SQLite 持久化）
2. 历史规划按用户隔离存储（任务从 JSON 文件迁移到数据库，带 `user_id` 归属）
3. 前端登录/注册页、路由守卫、NavBar 用户菜单、个人资料页（符合现有深色玻璃拟态 + 金色点缀风格）
4. 旧 `data/trip_tasks/*.json` 数据迁移到内置 `public` 用户名下

## Current State Analysis（基于实际探索）

- **后端**：FastAPI（`backend/app/api/main.py`），路由 `trip/poi/map/chat/settings` 挂在 `/api` 下；**无任何认证、无数据库**
- **任务存储**：`backend/app/api/routes/trip.py` 用内存 dict + `backend/data/trip_tasks/{task_id}.json` 文件持久化；`GET /api/trip/history` 返回**全局所有人**的已完成任务（`_load_history_items` 按 mtime 倒序）
- **任务流**：`POST /api/trip/plan` 返回 task_id → 前端 WebSocket `/api/trip/ws/{task_id}` 订阅进度 → 完成后 Result.vue 通过 `GET /api/trip/status/{task_id}` 拉取结果（或 sessionStorage）
- **前端**：Vue3 + ant-design-vue 4 + vue-router 4（仅 `/`=Landing、`/result`=Result 两个路由）+ vue-i18n（zh/ja/en）+ axios；**未安装 pinia**
- **前端风格**：Outfit 字体、深色渐变（#0a0a0f→#15132b→#1a1035）、金色系强调色（#FFD699/#FFB347）、圆角胶囊按钮（999px）、半透明玻璃面板（rgba(12,23,32,0.56)）、`a-modal` 弹窗（见 [NavBar.vue](file:///c:/Users/29484/PycharmProjects/TripStar/frontend/src/components/NavBar.vue) 设置弹窗样式）
- **token 传递现状**：`api.ts` 的 axios 实例无 Authorization 头；WebSocket 原生 API 无法带 header，需要用 query 参数传 token

## 技术选型（已确认）

| 组件 | 选择 |
|---|---|
| ORM | SQLAlchemy 2.0 (async) + aiosqlite（单文件 `backend/tripstar.db`） |
| 密码 | passlib[bcrypt] |
| 令牌 | PyJWT；Access 2h（不查库）+ Refresh 14d（落库、SHA256 摘要、轮换） |
| 登录模式 | **强制登录**：前端所有路由守卫；后端 `/api/trip/*` 全部要求 Bearer token |
| 旧数据 | 启动时迁移到内置 `public` 用户（不可登录的保留账户），普通用户不可见 |

## Proposed Changes

### A. 后端 — 新增文件

#### 1. `backend/app/database.py`
- `async_engine = create_async_engine(settings.database_url)`、`AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)`
- `async def init_db()`：`async with engine.begin(): await conn.run_sync(Base.metadata.create_all)`，随后调用旧数据迁移
- `async def get_session() -> AsyncGenerator`（FastAPI 依赖）

#### 2. `backend/app/models/db_models.py`
SQLAlchemy 2.0 声明式（`Mapped[]`/`mapped_column`）：

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] (pk)
    username: Mapped[str] (String(50), unique, index)
    email: Mapped[str] (String(255), unique, index)
    password_hash: Mapped[str] (String(255))
    nickname: Mapped[str] (String(50), default="")
    avatar_url: Mapped[str] (String(500), default="")
    is_active: Mapped[bool] (default True)
    is_loginable: Mapped[bool] (default True)   # public 账户为 False，禁止登录
    created_at / updated_at: Mapped[datetime]

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id, user_id (FK users.id, ondelete CASCADE, index)
    token_hash: Mapped[str] (String(64), unique)  # SHA256 hex
    expires_at: Mapped[datetime]
    revoked: Mapped[bool] (default False)
    created_at: Mapped[datetime]

class TripTaskRecord(Base):
    __tablename__ = "trip_tasks"
    task_id: Mapped[str] (String(32), pk)          # 沿用现有 8 位 uuid 逻辑
    user_id: Mapped[int] (FK users.id, index)      # 用户隔离核心字段
    plan_id: Mapped[str] (String(32))
    status: Mapped[str]                            # processing/completed/failed
    stage: Mapped[str]; progress: Mapped[int]
    message: Mapped[str]; error: Mapped[str | None]
    result: Mapped[dict | None] (JSON 列)          # TripPlanResponse.model_dump()
    request_payload: Mapped[dict | None] (JSON 列)
    created_at / updated_at: Mapped[datetime]      # updated_at 替代文件 mtime 排序
```

#### 3. `backend/app/services/auth_service.py`
- `hash_password / verify_password`（bcrypt）
- `create_access_token(user_id)`：JWT payload `{sub: str(user_id), exp, type: "access"}`，HS256 + `settings.secret_key`
- `issue_refresh_token(session, user_id)`：`secrets.token_urlsafe(48)`，库存 SHA256 摘要；`rotate_refresh_token`（旧 revoked + 发新）
- `register_user / authenticate(account, password)`：account 支持用户名或邮箱；校验唯一性（返回业务错误码而非 500）
- `migrate_legacy_trip_tasks(session)`：若 `trip_plans` 表为空且 `backend/data/trip_tasks/*.json` 存在 → 确保 `public` 用户存在（username=`public`, email=`public@tripstar.local`, 随机密码, `is_loginable=False`）→ 逐个 JSON 导入为 `TripTaskRecord(user_id=public.id)`，复用 trip.py 现有的字段映射逻辑（status 非终态的按"服务已重启"规则标记 failed）

#### 4. `backend/app/api/deps.py`
- `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)`
- `async def get_current_user(token, session) -> User`：解码 JWT → 查库 → 校验 `is_active`；失败抛 `HTTPException(401, "未登录或令牌已失效")`

#### 5. `backend/app/api/routes/auth.py`
`APIRouter(prefix="/auth", tags=["用户认证"])`，响应统一 `{success, message, data}`：

| 方法 | 路径 | 鉴权 | 说明 |
|---|---|---|---|
| POST | `/api/auth/register` | 否 | username/email/password（Pydantic 校验：用户名 3-50、密码≥8、EmailStr） |
| POST | `/api/auth/login` | 否 | account(用户名或邮箱)+password → TokenPair + UserResponse |
| POST | `/api/auth/refresh` | 否 | refresh_token → 新 TokenPair（轮换） |
| POST | `/api/auth/logout` | 是 | 提交 refresh_token → revoked |
| GET | `/api/auth/me` | 是 | 当前用户信息 |
| PUT | `/api/auth/me` | 是 | 修改 nickname / avatar_url |
| PUT | `/api/auth/password` | 是 | old_password + new_password，改密后吊销全部 refresh token |

### B. 后端 — 修改文件

#### 6. `backend/app/models/schemas.py`（追加）
沿用现有中文 Field 风格追加：`RegisterRequest / LoginRequest / TokenPair / UserResponse / UpdateProfileRequest / ChangePasswordRequest / LogoutRequest`。

#### 7. `backend/app/api/routes/trip.py`（重构存储层）
- 保留内存 `_tasks` dict + `subscribers`（WebSocket 广播仍需），但**持久化改为写 `TripTaskRecord` 表**；删除 `_persist_task_state/_load_task_from_disk/_load_persisted_tasks` 等文件 IO
- `POST /plan`：加 `user: User = Depends(get_current_user)`，创建任务时写入 `user_id`
- `GET /history`：加鉴权，改为 `SELECT ... WHERE user_id=:uid AND status='completed' ORDER BY updated_at DESC LIMIT :limit`，返回结构不变（`_build_history_item` 字段映射逻辑保留，数据源换成 DB 行）
- `GET /status/{task_id}` / `WS /ws/{task_id}`：加鉴权 + **归属校验**（`task.user_id != current_user.id` → 404/1008，防止越权访问他人任务）；WebSocket 用 `?token=` query 参数解析 JWT（accept 前校验，失败 close code=1008）
- 启动预加载：从 DB 加载最近 N=200 条任务恢复内存态（替代 `_load_persisted_tasks`）

#### 8. `backend/app/api/main.py`
- 注册 `auth.router`；`startup_event` 中 `await init_db()`（含旧数据迁移）；CORS 已配好无需改

#### 9. `backend/app/config.py` + `backend/.env.example`
Settings 新增：`secret_key: str = ""`（为空时启动打印警告并自动生成随机值，重启后旧 token 失效——仅开发态）、`database_url: str = "sqlite+aiosqlite:///./tripstar.db"`、`access_token_expire_hours: int = 2`、`refresh_token_expire_days: int = 14`；`print_config` 打印数据库状态。

#### 10. `backend/requirements.txt`（追加）
`sqlalchemy>=2.0`、`aiosqlite>=0.20`、`passlib[bcrypt]>=1.7.4`、`pyjwt>=2.8`、`email-validator>=2.0`

> 注：`/api/poi`、`/api/map`、`/api/chat`、`/api/settings` 保持现状（无状态工具接口，前端强制登录后天然带 token），不在本次范围内加锁。

### C. 前端 — 新增文件

#### 11. `frontend/src/services/auth.ts`（无 pinia，用组合式响应式状态）
- localStorage 键：`tripstar.auth.access_token` / `tripstar.auth.refresh_token` / `tripstar.auth.user`
- `export const authState = reactive<{ user: UserInfo | null; ready: boolean }>`
- `login / register / logout / fetchMe / updateProfile / changePassword` API 封装
- `initAuth()`：应用启动时若有 access_token 则 `GET /api/auth/me` 恢复用户态

#### 12. `frontend/src/views/Login.vue`（路由 `/login`）
- 登录/注册双 Tab（a-tabs），字段：登录=account+password；注册=username+email+password+确认密码
- **风格对齐 Landing**：全屏深色渐变背景（#0a0a0f→#15132b→#1a1035）+ 顶部 TripStar 品牌字（复用 `.landing-brand` 视觉）+ 居中玻璃卡片（rgba(12,23,32,0.56)、999px 圆角输入框/胶囊主按钮、金色 #FFD699 强调、Outfit 字体），错误用 `message.error`，与 NavBar 设置弹窗同一设计语言
- 成功后 `router.replace(route.query.redirect || '/')`

#### 13. `frontend/src/views/Profile.vue`（路由 `/profile`）
- 用户信息卡（头像 URL 预览 + nickname/username/email 只读展示）+ 修改资料表单 + 修改密码表单（a-form，风格同上）
- 顶部复用 NavBar，"返回"回 Landing

#### 14. `frontend/src/router/guards.ts`（或直接写在 main.ts）
`router.beforeEach`：`/login` 之外的任意路由，未登录（无 token 或 me 失败）→ `redirect: { path: '/login', query: { redirect: to.fullPath } }`；已登录访问 `/login` → 跳 `/`

### D. 前端 — 修改文件

#### 15. `frontend/src/main.ts`
- 注册路由 `/login`、`/profile`；挂载全局守卫；`app.mount` 前 `await initAuth()`（守卫需要知道用户态，避免闪烁）

#### 16. `frontend/src/services/api.ts`
- 请求拦截器：从 localStorage 读 access_token，注入 `Authorization: Bearer`
- 响应拦截器：捕获 401 → 尝试一次 `POST /api/auth/refresh`（防并发重入：模块级 `refreshing` Promise）→ 重放原请求；refresh 也失败 → 清空 authState 并 `router.push('/login')`
- WebSocket URL（`generateTripPlan` 内）：拼接 `?token=${accessToken}`

#### 17. `frontend/src/components/NavBar.vue`
- 右侧新增用户区：头像/昵称（a-dropdown：个人资料、退出登录），CTA 按钮（`home.nav.cta`）改为滚动到表单（已登录语义更合适）或保留；登录页不渲染 NavBar（由 Login.vue 自带品牌头）
- 退出登录调 `logout()` → 清 storage → 跳 `/login`

#### 18. `frontend/src/i18n/locales/{zh,en,ja}.json`
追加 `auth.*`（登录/注册/资料/改密/各校验文案）与 `profile.*`、`nav.user.*` 键，三语同步。

#### 19. `frontend/src/types/index.ts`
追加 `UserInfo / TokenPair / LoginPayload / RegisterPayload / UpdateProfilePayload`。

#### 20. `frontend/src/views/Landing.vue`
- 历史列表逻辑不变（`getTripHistory` 后端已按用户过滤）；空态文案 `home.history.empty` 改为"登录后生成的计划会保存在这里"
- 无需其他改动（401 由拦截器统一处理）

## Assumptions & Decisions

1. **强制登录**：前端所有路由受守卫保护；后端仅锁 `/api/trip/*` 与 auth 相关写接口，`poi/map/chat/settings` 保持公开（工具型无状态接口）
2. **旧数据**：迁移到 `public` 保留账户（`is_loginable=False` 无法登录），普通登录用户不可见 → 用户间完全隔离；旧 JSON 文件保留在磁盘作为备份但不 再读取
3. **无 pinia**：项目未安装，用 `services/auth.ts` 的模块级 reactive 状态（与现有 `services/api.ts` 导出函数的模式一致），不引入新状态库
4. **WebSocket 鉴权**：无法带 header，采用 `?token=` query 传 access_token
5. **secret_key 未配置时**自动随机生成（开发友好，重启失效）；生产建议在 .env 固定配置
6. **头像**仅支持 URL 填写（不做上传），保持范围最小

## Verification

1. **后端**：激活 .venv → `uvicorn app.api.main:app --port 8000`，检查启动日志出现"数据库初始化完成/迁移 N 个历史任务"
2. **API 冒烟**（curl 或 /docs）：
   - register 两个账号 A、B → login A 拿 token
   - A 提交 `/api/trip/plan`（带 Bearer）→ 等 completed → `/api/trip/history` 只见 A 的记录
   - login B → `/api/trip/history` 为空（隔离验证）
   - 无 token 访问 `/api/trip/history` → 401；A 的 token 访问 B 的 task_id `/api/trip/status` → 404
   - refresh 轮换：旧 refresh_token 二次使用 → 401
3. **前端**：`npm run dev` → 访问 `/` 未登录自动跳 `/login`；注册→登录→生成规划→历史列表仅显示本账号；退出登录后 sessionStorage 清理、回到登录页
4. **构建**：`cd frontend && npm run build`（vue-tsc 通过，无类型错误）
5. **回归**：WebSocket 进度条在带 token 后正常推送；Result 页从历史打开、直接访问 `?plan_id=` 均正常
