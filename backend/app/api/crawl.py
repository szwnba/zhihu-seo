from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.services.zhihu_crawler import ZhihuCrawler

router = APIRouter()


class CrawlRequest(BaseModel):
    bookmark_url: str = Field(..., description="知乎收藏夹 URL")
    min_votes: int = Field(default=100, ge=0, description="最小赞同数阈值")
    max_pages: int = Field(default=10, ge=1, le=50, description="最大分页数")
    cookie: str = Field(default="", description="知乎 Cookie（可选）")


class CrawlResponse(BaseModel):
    task_id: int
    status: str
    message: str
    total_answers: int = 0


@router.post("/bookmark", response_model=CrawlResponse)
async def start_bookmark_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """启动知乎收藏夹爬取任务"""
    async def do_crawl():
        crawler = ZhihuCrawler(cookie=request.cookie)
        try:
            results = await crawler.crawl_bookmark_collection(
                request.bookmark_url,
                min_votes=request.min_votes,
                max_pages=request.max_pages,
            )
            return results
        finally:
            await crawler.close()
    
    # 立即执行（简化版，实际应使用后台任务队列）
    results = await do_crawl()
    
    return CrawlResponse(
        task_id=1,
        status="completed",
        message="Crawl completed",
        total_answers=len(results),
    )


@router.get("/task/{task_id}")
async def get_crawl_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
):
    """获取爬取任务状态"""
    return {"task_id": task_id, "status": "completed"}
