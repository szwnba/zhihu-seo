from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.keyword_engine import KeywordEngine

router = APIRouter()


class ClusterRequest(BaseModel):
    keywords: list[str] = Field(..., description="关键词列表")
    n_clusters: int = Field(default=5, ge=2, le=20)


class ClusterResponse(BaseModel):
    clusters: list[dict]
    total: int


@router.post("/generate", response_model=ClusterResponse)
async def generate_clusters(request: ClusterRequest):
    """对关键词进行聚类"""
    engine = KeywordEngine()
    clusters = engine.cluster_keywords(
        request.keywords,
        n_clusters=request.n_clusters,
    )
    return ClusterResponse(clusters=clusters, total=len(clusters))
