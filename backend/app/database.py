"""数据库引擎与会话管理"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import get_settings
from .models.db_models import Base
from .services.auth_service import migrate_legacy_trip_tasks

settings = get_settings()

async_engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)


async def _ensure_photo_cache_columns(conn) -> None:
    """给已存在的库补上图片字节缓存字段。

    create_all 只建新表、不会给旧表加列，所以这里显式 ALTER。
    补列之后，此前只存了链接的记录会在下次访问时自动重抓并补齐字节。
    """
    if not settings.database_url.startswith("sqlite"):
        return
    try:
        result = await conn.exec_driver_sql("PRAGMA table_info(attraction_photo_cache)")
        columns = {row[1] for row in result.fetchall()}
        if not columns:
            return
        if "photo_data" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE attraction_photo_cache ADD COLUMN photo_data BLOB"
            )
            print("🖼️ 已为 attraction_photo_cache 补充 photo_data 字段")
        if "content_type" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE attraction_photo_cache "
                "ADD COLUMN content_type VARCHAR(64) NOT NULL DEFAULT ''"
            )
            print("🖼️ 已为 attraction_photo_cache 补充 content_type 字段")
    except Exception as e:
        print(f"⚠️ 补充图片缓存字段失败（不影响启动）: {e}")


async def init_db() -> None:
    """初始化数据库：建表 + 补列 + 迁移旧 JSON 任务数据。"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _ensure_photo_cache_columns(conn)

    # 迁移历史 data/trip_tasks/*.json 到数据库（绑定 public 用户）
    async with AsyncSessionLocal() as session:
        migrated = await migrate_legacy_trip_tasks(session)
        if migrated > 0:
            print(f"📦 已迁移 {migrated} 个历史旅行任务到数据库（归属 public 用户）")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供数据库会话。"""
    async with AsyncSessionLocal() as session:
        yield session
