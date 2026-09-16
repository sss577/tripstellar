"""POI相关API路由"""

import httpx
from datetime import datetime, timedelta
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from typing import List, Optional
from ...database import AsyncSessionLocal
from ...models.db_models import AttractionPhotoCache
from ...services.amap_service import get_amap_service

router = APIRouter(prefix="/poi", tags=["POI"])

# 缓存记录有效期（天）。图片字节已落库，这里的含义从"图片还能不能用"
# 变成"多久去小红书重抓一次"，所以可以放心设长
PHOTO_CACHE_TTL_DAYS = 30

# 前端统一从这个本站接口取图，不再直连小红书 CDN：
# ① 小红书直链只有数小时有效期，过期即 403；
# ② 直链是 http，站点部署到 HTTPS 后会被浏览器按混合内容拦截
PHOTO_FILE_PATH = "/api/poi/photo/file"


def _normalize_photo_key(name: str) -> str:
    """景点名归一化为缓存键（去首尾空白并合并内部空白）。"""
    return " ".join((name or "").split())


def _photo_file_url(key: str) -> str:
    """本站图片接口地址（相对路径，由前端补上 API 前缀）。"""
    return f"{PHOTO_FILE_PATH}?name={quote(key)}"


async def _read_photo_cache(key: str) -> tuple[str, bytes | None, str]:
    """读取未过期的缓存，返回 (原始直链, 图片字节, 内容类型)；未命中返回空值。"""
    if not key:
        return "", None, ""
    try:
        async with AsyncSessionLocal() as session:
            record = await session.get(AttractionPhotoCache, key)
            if record is None:
                return "", None, ""
            if record.updated_at and (
                datetime.utcnow() - record.updated_at > timedelta(days=PHOTO_CACHE_TTL_DAYS)
            ):
                return "", None, ""
            return record.photo_url or "", record.photo_data, record.content_type or ""
    except Exception as e:
        print(f"⚠️ 读取景点图片缓存失败 ({key}): {e}")
        return "", None, ""


async def _save_photo_cache(
    key: str, photo_url: str, photo_data: bytes | None, content_type: str
) -> None:
    """写入/刷新景点图片缓存；photo_data 为空时不覆盖已存的字节。"""
    if not key:
        return
    try:
        async with AsyncSessionLocal() as session:
            record = await session.get(AttractionPhotoCache, key)
            if record is None:
                session.add(
                    AttractionPhotoCache(
                        name=key,
                        photo_url=photo_url or "",
                        photo_data=photo_data,
                        content_type=content_type or "",
                    )
                )
            else:
                if photo_url:
                    record.photo_url = photo_url
                if photo_data:
                    record.photo_data = photo_data
                    record.content_type = content_type or ""
                record.updated_at = datetime.utcnow()
            await session.commit()
    except Exception as e:
        print(f"⚠️ 写入景点图片缓存失败 ({key}): {e}")


async def _download_photo(url: str) -> tuple[bytes, str]:
    """下载图片字节。小红书直链给的是 http，这里统一走 https，
    否则站点部署到 HTTPS 后前端会因混合内容被浏览器拦截。"""
    if not url:
        return b"", ""
    safe_url = "https://" + url[len("http://") :] if url.startswith("http://") else url
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get(
                safe_url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Referer": "https://www.xiaohongshu.com/",
                },
            )
            if resp.status_code == 200 and resp.content:
                ctype = resp.headers.get("content-type", "").split(";")[0].strip()
                return resp.content, ctype or "image/webp"
            print(f"⚠️ 下载景点图片失败：HTTP {resp.status_code} {safe_url[:80]}")
    except Exception as e:
        print(f"⚠️ 下载景点图片异常: {e}")
    return b"", ""


async def _fetch_and_cache_photo(key: str) -> bool:
    """去小红书抓一次图片并把字节落库，成功返回 True。"""
    try:
        from ...services.xhs_service import get_photo_from_xhs

        # 加"风景"前缀，避开同名歌曲 / 小说 / 人名
        photo_url = await get_photo_from_xhs(f"{key} 风景")
        if not photo_url:
            print(f"⚠️ 未找到 {key} 的小红书图片")
            return False

        photo_data, content_type = await _download_photo(photo_url)
        await _save_photo_cache(key, photo_url, photo_data or None, content_type)
        if not photo_data:
            # 字节没拿到，只留了链接：本次仍算失败，前端会回退到名称占位图
            return False
        return True
    except Exception as e:
        print(f"❌ 抓取景点图片失败 ({key}): {e}")
        return False


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
    summary="获取景点图片地址",
    description="确保该景点图片已缓存，返回本站图片接口地址（前端直接交给 <img> 使用）"
)
async def get_attraction_photo(name: str, city: Optional[str] = None, refresh: bool = False):
    """
    获取景点图片地址

    Args:
        name: 景点名称
        city: 所在城市（仅作标识，实际不影响搜索关键词）
        refresh: 为 True 时忽略已有缓存，强制重新去小红书抓一次

    Returns:
        本站图片接口地址；抓不到时返回空串，由前端展示名称占位图
    """
    key = _normalize_photo_key(name)
    if not key:
        return {
            "success": True,
            "message": "景点名为空",
            "data": {"name": name, "photo_url": "", "cached": False},
        }

    if not refresh:
        _, cached_data, _ = await _read_photo_cache(key)
        if cached_data:
            return {
                "success": True,
                "message": "获取图片成功（缓存）",
                "data": {"name": name, "photo_url": _photo_file_url(key), "cached": True},
            }

    ok = await _fetch_and_cache_photo(key)
    return {
        "success": True,
        "message": "获取图片成功" if ok else "未找到对应图片",
        "data": {
            "name": name,
            "photo_url": _photo_file_url(key) if ok else "",
            "cached": False,
        },
    }


@router.get(
    "/photo/file",
    summary="景点图片字节流",
    description="直接回图片内容。字节缓存在库里，因此不依赖小红书直链是否过期"
)
async def get_attraction_photo_file(name: str, city: Optional[str] = None, refresh: bool = False):
    """按景点名返回图片字节流。"""
    key = _normalize_photo_key(name)
    if not key:
        raise HTTPException(status_code=404, detail="景点名为空")

    photo_data: bytes | None = None
    content_type = ""
    if not refresh:
        _, photo_data, content_type = await _read_photo_cache(key)
    if not photo_data:
        await _fetch_and_cache_photo(key)
        _, photo_data, content_type = await _read_photo_cache(key)

    if not photo_data:
        raise HTTPException(status_code=404, detail=f"未找到 {name} 的图片")

    return Response(
        content=photo_data,
        media_type=content_type or "image/webp",
        # 字节已落库，可以放心让浏览器缓存一天，减少重复请求
        headers={"Cache-Control": "public, max-age=86400"},
    )

