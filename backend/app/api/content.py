from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.models.user import User, PlanTier
from app.services.auth import get_current_user, require_plan
from app.services.content_planner import ContentPlanner

router = APIRouter()


class MatrixRequest(BaseModel):
    keywords: list[dict] = Field(..., description="关键词列表")
    clusters: list[dict] = Field(..., description="聚类结果")
    target_domain: str = Field(default="", description="目标域名")


class ReportRequest(BaseModel):
    keywords: list[dict] = Field(..., description="关键词列表")
    clusters: list[dict] = Field(..., description="聚类结果")
    target_domain: str = Field(default="", description="目标域名")


@router.post("/matrix")
async def generate_matrix(
    request: MatrixRequest,
    current_user: User = Depends(get_current_user),
):
    """生成内容矩阵"""
    planner = ContentPlanner()
    matrix = planner.generate_matrix(
        request.keywords,
        request.clusters,
        request.target_domain,
    )
    return matrix


@router.post("/report")
async def generate_report(
    request: ReportRequest,
    current_user: User = Depends(require_plan(PlanTier.PRO)),
):
    """生成 SEO 分析报告"""
    planner = ContentPlanner()
    report = planner.generate_seo_report(
        request.keywords,
        request.clusters,
        request.target_domain,
    )
    return report


@router.get("/health")
async def content_health():
    return {"status": "ok", "module": "content"}
