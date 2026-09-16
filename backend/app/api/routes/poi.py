"""POI相关API路由"""

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from ...database import AsyncSessionLocal
from ...models.db_models import AttractionPhotoCache
from ...services.amap_service import get_amap_service

router = APIRouter(prefix="/poi", tags=["POI"])

# 景点图片缓存有效期（天）：过期后重新走签名引擎获取，防止直链失效
PHOTO_CACHE_TTL_DAYS = 7


def _normalize_photo_key(name: str) -> str:
    """景点名归一化为缓存键（去首尾空白并合并内部空白）。"""
    return " ".join((name or "").split())


async def _get_cached_photo(name: str) -> str:
    """读取未过期的景点图片缓存；未命中或已过期返回空串。"""
    key = _normalize_photo_key(name)
    if not key:
        return ""
    try:
        async with AsyncSessionLocal() as session:
            record = await session.get(AttractionPhotoCache, key)
            if record is None or not record.photo_url:
                return ""
            if record.updated_at and (
                datetime.utcnow() - record.updated_at > timedelta(days=PHOTO_CACHE_TTL_DAYS)
            ):
                return ""
            return record.photo_url
    except Exception as e:
        print(f"⚠️ 读取景点图片缓存失败 ({name}): {e}")
        return ""


async def _save_photo_cache(name: str, photo_url: str) -> None:
    """写入/刷新景点图片缓存。"""
    key = _normalize_photo_key(name)
    if not key or not photo_url:
        return
    try:
        async with AsyncSessionLocal() as session:
            record = await session.get(AttractionPhotoCache, key)
            if record is None:
                session.add(AttractionPhotoCache(name=key, photo_url=photo_url))
            else:
                record.photo_url = photo_url
                record.updated_at = datetime.utcnow()
            await session.commit()
    except Exception as e:
        print(f"⚠️ 写入景点图片缓存失败 ({name}): {e}")


class POIDetailResponse(BaseModel):
    """POI详情响应"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.get(
    "/detail/{poi_id}",
    response_model=POIDetailResponse,
    summary="获取POI详情",
    description="根据POI ID获取详细信息,包括图片"
)
async def get_poi_detail(poi_id: str):
    """
    获取POI详情
    
    Args:
        poi_id: POI ID
        
    Returns:
        POI详情响应
    """
    try:
        amap_service = get_amap_service()
        
        # 调用高德地图POI详情API
        result = amap_service.get_poi_detail(poi_id)
        
        return POIDetailResponse(
            success=True,
            message="获取POI详情成功",
            data=result
        )
        
    except Exception as e:
        print(f"❌ 获取POI详情失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取POI详情失败: {str(e)}"
        )


@router.get(
    "/search",
    summary="搜索POI",
    description="根据关键词搜索POI"
)
async def search_poi(keywords: str, city: str = "北京"):
    """
    搜索POI

    Args:
        keywords: 搜索关键词
        city: 城市名称

    Returns:
        搜索结果
    """
    try:
        amap_service = get_amap_service()
        result = amap_service.search_poi(keywords, city)

        return {
            "success": True,
            "message": "搜索成功",
            "data": result
        }

    except Exception as e:
        print(f"❌ 搜索POI失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"搜索POI失败: {str(e)}"
        )


@router.get(
    "/photo",
    summary="获取景点图片",
    description="根据景点名称从小红书获取图片（带本地缓存，命中缓存不再调用签名引擎）"
)
async def get_attraction_photo(name: str, city: Optional[str] = None, refresh: bool = False):
    """
    获取景点图片

    Args:
        name: 景点名称
        city: 所在城市（仅作标识，实际不影响搜索关键词）
        refresh: 为 True 时跳过缓存，强制重新调用签名引擎搜图

    Returns:
        图片URL
    """
    try:
        # 1. 优先读本地缓存（SQLite），命中则无需再调用签名引擎
        if not refresh:
            cached_url = await _get_cached_photo(name)
            if cached_url:
                return {
                    "success": True,
                    "message": "获取图片成功（缓存）",
                    "data": {
                        "name": name,
                        "photo_url": cached_url,
                        "cached": True,
                    }
                }

        from ...services.xhs_service import get_photo_from_xhs

        # 为了避免同名的流行歌曲（如许嵩的《断桥残雪》）、小说或人名干扰
        # 强制带上前缀“景点”，能够绝对限定搜索范围在旅游打卡贴内
        query_kw = f"{name} 风景"
        photo_url = await get_photo_from_xhs(query_kw)

        if not photo_url:
            # 兜底：交由前端展示默认占位图
            print(f"⚠️ 无法为 {name} 找到对应的小红书景点图片，返回空")
            photo_url = ""
        else:
            # 2. 搜到后写入缓存，下次直接命中
            await _save_photo_cache(name, photo_url)

        return {
            "success": True,
            "message": "获取图片成功",
            "data": {
                "name": name,
                "photo_url": photo_url,
                "cached": False,
            }
        }

    except Exception as e:
        print(f"❌ 获取景点图片失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取景点图片失败: {str(e)}"
        )

