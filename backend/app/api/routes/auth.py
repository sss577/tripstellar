"""用户认证 API 路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_session
from ...models.db_models import User
from ...models.schemas import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UpdateProfileRequest,
    UserResponse,
)
from ...services import auth_service
from ...services.auth_service import AuthError
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["用户认证"])


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        nickname=user.nickname or "",
        avatar_url=user.avatar_url or "",
        created_at=user.created_at,
    )


def _auth_error_handler(e: AuthError) -> None:
    raise HTTPException(status_code=400, detail=e.message)


@router.post(
    "/register",
    summary="用户注册",
    description="注册新用户并直接返回登录态（双 token）",
)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    try:
        user = await auth_service.register_user(
            session, payload.username, payload.email, payload.password
        )
    except AuthError as e:
        _auth_error_handler(e)

    access_token = auth_service.create_access_token(user.id)
    refresh_token = await auth_service.issue_refresh_token(session, user.id)

    return AuthResponse(
        message="注册成功",
        data=TokenPair(access_token=access_token, refresh_token=refresh_token),
        user=_to_user_response(user),
    )


@router.post(
    "/login",
    summary="用户登录",
    description="用户名或邮箱 + 密码登录，返回双 token",
)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    try:
        user = await auth_service.authenticate(session, payload.account, payload.password)
    except AuthError as e:
        _auth_error_handler(e)

    access_token = auth_service.create_access_token(user.id)
    refresh_token = await auth_service.issue_refresh_token(session, user.id)

    return AuthResponse(
        message="登录成功",
        data=TokenPair(access_token=access_token, refresh_token=refresh_token),
        user=_to_user_response(user),
    )


@router.post(
    "/refresh",
    summary="刷新访问令牌",
    description="用 refresh token 换取新的双 token（旧 refresh token 同时作废）",
)
async def refresh(payload: RefreshRequest, session: AsyncSession = Depends(get_session)):
    rotated = await auth_service.rotate_refresh_token(session, payload.refresh_token)
    if rotated is None:
        raise HTTPException(status_code=401, detail="刷新令牌无效或已过期")

    user_id, new_refresh_token = rotated
    access_token = auth_service.create_access_token(user_id)
    return {
        "success": True,
        "message": "令牌已刷新",
        "data": TokenPair(access_token=access_token, refresh_token=new_refresh_token),
    }


@router.post(
    "/logout",
    summary="退出登录",
    description="吊销当前 refresh token（需要 Bearer 认证）",
)
async def logout(
    payload: LogoutRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await auth_service.revoke_refresh_token(session, payload.refresh_token)
    return {"success": True, "message": "已退出登录"}


@router.get(
    "/me",
    summary="获取当前用户",
    description="返回当前登录用户信息（需要 Bearer 认证）",
)
async def get_me(user: User = Depends(get_current_user)):
    return {
        "success": True,
        "message": "ok",
        "data": _to_user_response(user),
    }


@router.put(
    "/me",
    summary="更新用户资料",
    description="修改昵称 / 头像URL（需要 Bearer 认证）",
)
async def update_me(
    payload: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if payload.nickname is not None:
        user.nickname = payload.nickname.strip()
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url.strip()
    await session.commit()
    await session.refresh(user)
    return {
        "success": True,
        "message": "资料已更新",
        "data": _to_user_response(user),
    }


@router.put(
    "/password",
    summary="修改密码",
    description="修改密码并吊销全部 refresh token（需要 Bearer 认证）",
)
async def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not auth_service.verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")

    user.password_hash = auth_service.hash_password(payload.new_password)
    await session.commit()

    # 改密后吊销全部刷新令牌，强制其他端下线
    await auth_service.revoke_all_refresh_tokens(session, user.id)

    return {"success": True, "message": "密码已修改，请重新登录"}
