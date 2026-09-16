"""用户认证服务：密码加密、JWT 令牌、注册/登录、旧数据迁移"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import bcrypt
import jwt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models.db_models import RefreshToken, TripTaskRecord, User

settings = get_settings()

# 旧版 JSON 任务数据目录
_LEGACY_TASKS_DIR = Path(__file__).resolve().parents[2] / "data" / "trip_tasks"

# JWT 算法
_JWT_ALGORITHM = "HS256"


# ============ 密码 ============

def hash_password(password: str) -> str:
    """密码哈希（bcrypt）"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    """校验密码"""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("ascii"))
    except ValueError:
        return False


# ============ Access Token (JWT) ============

def create_access_token(user_id: int) -> str:
    """签发短期访问令牌（不查库）"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(hours=settings.access_token_expire_hours),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=_JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    """解码访问令牌，返回 user_id；无效返回 None"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[_JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    if payload.get("type") != "access":
        return None
    try:
        return int(payload["sub"])
    except (KeyError, ValueError):
        return None


# ============ Refresh Token（落库、SHA256 摘要、轮换） ============

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def issue_refresh_token(session: AsyncSession, user_id: int) -> str:
    """签发刷新令牌并落库（存摘要）"""
    token = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    session.add(RefreshToken(user_id=user_id, token_hash=_hash_token(token), expires_at=expires_at))
    await session.commit()
    return token


async def rotate_refresh_token(session: AsyncSession, refresh_token: str) -> Optional[tuple[int, str]]:
    """校验并轮换刷新令牌：旧 token 作废，返回 (user_id, 新token)；无效返回 None"""
    token_hash = _hash_token(refresh_token)
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    record = (await session.execute(stmt)).scalar_one_or_none()
    if record is None:
        return None
    if record.revoked or record.expires_at < datetime.utcnow():
        return None

    user_stmt = select(User).where(User.id == record.user_id)
    user = (await session.execute(user_stmt)).scalar_one_or_none()
    if user is None or not user.is_active or not user.is_loginable:
        return None

    record.revoked = True
    new_token = await issue_refresh_token(session, record.user_id)
    return record.user_id, new_token


async def revoke_refresh_token(session: AsyncSession, refresh_token: str) -> bool:
    """登出：吊销指定刷新令牌"""
    token_hash = _hash_token(refresh_token)
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    record = (await session.execute(stmt)).scalar_one_or_none()
    if record is None:
        return False
    record.revoked = True
    await session.commit()
    return True


async def revoke_all_refresh_tokens(session: AsyncSession, user_id: int) -> None:
    """吊销用户全部刷新令牌（改密后强制下线）"""
    stmt = select(RefreshToken).where(
        RefreshToken.user_id == user_id, RefreshToken.revoked == False  # noqa: E712
    )
    records = (await session.execute(stmt)).scalars().all()
    for record in records:
        record.revoked = True
    await session.commit()


# ============ 注册 / 登录 ============

class AuthError(Exception):
    """认证业务错误"""

    def __init__(self, message: str, error_code: str = "AUTH_ERROR"):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


async def register_user(session: AsyncSession, username: str, email: str, password: str) -> User:
    """注册新用户，用户名/邮箱重复时抛 AuthError"""
    stmt = select(User).where((User.username == username) | (User.email == email))
    existing = (await session.execute(stmt)).scalars().all()
    for user in existing:
        if user.username == username:
            raise AuthError("用户名已被占用", "USERNAME_TAKEN")
        if user.email == email:
            raise AuthError("邮箱已被注册", "EMAIL_TAKEN")

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        nickname=username,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate(session: AsyncSession, account: str, password: str) -> User:
    """登录校验：account 支持用户名或邮箱；失败抛 AuthError"""
    stmt = select(User).where((User.username == account) | (User.email == account))
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None or not user.is_loginable:
        raise AuthError("账号不存在", "ACCOUNT_NOT_FOUND")
    if not user.is_active:
        raise AuthError("账号已被停用", "ACCOUNT_DISABLED")
    if not verify_password(password, user.password_hash):
        raise AuthError("密码错误", "WRONG_PASSWORD")
    return user


# ============ 旧数据迁移 ============

async def _ensure_public_user(session: AsyncSession) -> User:
    """确保内置 public 保留用户存在（不可登录）"""
    stmt = select(User).where(User.username == "public")
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None:
        user = User(
            username="public",
            email="public@tripstar.local",
            password_hash=hash_password(secrets.token_urlsafe(32)),
            nickname="公共数据",
            is_loginable=False,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def migrate_legacy_trip_tasks(session: AsyncSession) -> int:
    """将旧 data/trip_tasks/*.json 任务迁移到数据库（归属 public 用户）。

    仅在 trip_tasks 表为空时执行一次；旧 JSON 文件保留在磁盘作为备份。
    """
    import json

    # 表已有数据则跳过
    count_stmt = select(func.count()).select_from(TripTaskRecord)
    count = (await session.execute(count_stmt)).scalar() or 0
    if count > 0:
        return 0

    if not _LEGACY_TASKS_DIR.exists():
        return 0

    public_user = await _ensure_public_user(session)
    migrated = 0
    for path in _LEGACY_TASKS_DIR.glob("*.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if not isinstance(payload, dict):
                continue
        except Exception as e:
            print(f"⚠️  迁移任务 {path.name} 失败: {e}")
            continue

        task_id = str(payload.get("task_id") or path.stem)
        status = str(payload.get("status", "failed"))
        # 服务重启后，未完成任务无法恢复执行，统一标记为失败
        if status not in {"completed", "failed"}:
            status = "failed"

        updated_at = datetime.fromtimestamp(path.stat().st_mtime)
        record = TripTaskRecord(
            task_id=task_id,
            user_id=public_user.id,
            plan_id=str(payload.get("plan_id", task_id)),
            status=status,
            stage=str(payload.get("stage", status)),
            progress=int(payload.get("progress", 100)),
            message=str(payload.get("message", "")),
            error=payload.get("error") if status == "failed" else None,
            result=payload.get("result"),
            request_payload=payload.get("request_payload"),
            created_at=updated_at,
            updated_at=updated_at,
        )
        if status == "failed" and not record.error:
            record.error = "服务已重启，未完成的旅行规划任务无法恢复，请重新生成。"
            record.message = record.error
        session.add(record)
        migrated += 1

    if migrated > 0:
        await session.commit()
    return migrated


def generate_task_id() -> str:
    """生成任务ID（沿用现有 8 位 uuid 逻辑）"""
    return str(uuid.uuid4())[:8]
