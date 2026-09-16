"""FastAPI 认证依赖"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models.db_models import User
from ..services.auth_service import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """解析 Bearer Token 并返回当前用户；失败返回 401"""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未登录或令牌已失效",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_error

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_error

    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user
