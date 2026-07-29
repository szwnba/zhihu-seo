from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional

from app.models.user import User, PlanTier
from app.services.auth import get_current_user, require_plan
from app.services.competitor_monitor import CompetitorMonitor

router = APIRouter()


class AnalyzeRequest(BaseModel):
    domain: str = Field(..., description="竞品域名")


class KeywordGapRequest(BaseModel):
    my_domain: str = Field(..., description="我的域名")
    competitor_domains: list[str] = Field(..., description="竞品域名列表")


@router.post("/analyze")
async def analyze_competitor(
    request: AnalyzeRequest,
    current_user: User = Depends(require_plan(PlanTier.PRO)),
):
    """分析竞品网站"""
    monitor = CompetitorMonitor()
    try:
        result = await monitor.analyze_competitor(request.domain)
        return result
    finally:
        await monitor.close()


@router.post("/keyword-gap")
async def find_keyword_gap(
    request: KeywordGapRequest,
    current_user: User = Depends(require_plan(PlanTier.PRO)),
):
    """发现关键词空白"""
    monitor = CompetitorMonitor()
    try:
        result = await monitor.find_keyword_gap(
            request.my_domain,
            request.competitor_domains,
        )
        return result
    finally:
        await monitor.close()


@router.get("/zhihu-references")
async def get_zhihu_references(
    domain: str = Query(..., description="竞品域名"),
    current_user: User = Depends(require_plan(PlanTier.PRO)),
):
    """追踪竞品知乎引用"""
    monitor = CompetitorMonitor()
    try:
        result = await monitor.track_zhihu_references(domain)
        return {"references": result, "total": len(result)}
    finally:
        await monitor.close()


@router.post("/report")
async def generate_report(
    request: KeywordGapRequest,
    current_user: User = Depends(require_plan(PlanTier.PRO)),
):
    """生成竞品分析报告"""
    monitor = CompetitorMonitor()
    try:
        result = await monitor.generate_competitor_report(
            request.my_domain,
            request.competitor_domains,
        )
        return result
    finally:
        await monitor.close()
