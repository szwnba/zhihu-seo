from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.models.user import User, PlanTier
from app.services.auth import get_current_user, require_plan
from app.services.baidu_search_volume import BaiduSearchVolume

router = APIRouter()


class VolumeRequest(BaseModel):
    keywords: list[str] = Field(..., description="关键词列表")


@router.get("/volume")
async def get_search_volume(
    keyword: str = Query(..., description="查询关键词"),
    current_user: User = Depends(get_current_user),
):
    """获取单个关键词搜索量"""
    baidu = BaiduSearchVolume()
    try:
        result = await baidu.get_search_volume(keyword)
        return result
    finally:
        await baidu.close()


@router.post("/batch-volume")
async def batch_search_volumes(
    request: VolumeRequest,
    current_user: User = Depends(get_current_user),
):
    """批量获取搜索量"""
    baidu = BaiduSearchVolume()
    try:
        results = await baidu.batch_get_search_volumes(request.keywords)
        return {"results": results, "total": len(results)}
    finally:
        await baidu.close()


@router.get("/related")
async def get_related_keywords(
    keyword: str = Query(..., description="种子关键词"),
    current_user: User = Depends(get_current_user),
):
    """获取相关关键词"""
    baidu = BaiduSearchVolume()
    try:
        related = await baidu.get_related_keywords(keyword)
        return {"keyword": keyword, "related": related}
    finally:
        await baidu.close()


@router.get("/analyze")
async def analyze_keyword(
    keyword: str = Query(..., description="要分析的关键词"),
    current_user: User = Depends(require_plan(PlanTier.PRO)),
):
    """综合分析关键词（搜索量 + 竞争度 + 相关词）"""
    baidu = BaiduSearchVolume()
    try:
        result = await baidu.analyze_keyword(keyword)
        return result
    finally:
        await baidu.close()


@router.get("/competitors")
async def get_competitor_count(
    keyword: str = Query(..., description="关键词"),
    current_user: User = Depends(get_current_user),
):
    """获取竞争对手数量"""
    baidu = BaiduSearchVolume()
    try:
        count = await baidu.get_competitor_count(keyword)
        return {"keyword": keyword, "competitor_count": count}
    finally:
        await baidu.close()
