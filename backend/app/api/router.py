from fastapi import APIRouter

from app.api import crawl, keywords, clusters, content, health, auth, competitor, baidu

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(crawl.router, prefix="/crawl", tags=["crawl"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
api_router.include_router(clusters.router, prefix="/clusters", tags=["clusters"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(competitor.router, prefix="/competitor", tags=["competitor"])
api_router.include_router(baidu.router, prefix="/baidu", tags=["baidu"])
