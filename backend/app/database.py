"""数据库引擎与会话管理"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import get_settings
from .models.db_models import Base
from .services.auth_service import migrate_legacy_trip_tasks

settings = get_settings()

async_engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)


async def init_db() -> None:
    """初始化数据库：建表 + 迁移旧 JSON 任务数据。"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 迁移历史 data/trip_tasks/*.json 到数据库（绑定 public 用户）
    async with AsyncSessionLocal() as session:
        migrated = await migrate_legacy_trip_tasks(session)
        if migrated > 0:
            print(f"📦 已迁移 {migrated} 个历史旅行任务到数据库（归属 public 用户）")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供数据库会话。"""
    async with AsyncSessionLocal() as session:
        yield session
