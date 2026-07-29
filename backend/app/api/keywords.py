from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

from app.services.keyword_engine import KeywordEngine

router = APIRouter()


class ExtractRequest(BaseModel):
    text: str = Field(..., description="要提取关键词的文本")
    top_k: int = Field(default=20, ge=5, le=100)
    method: str = Field(default="tfidf", description="提取方法: tfidf 或 textrank")


class ExtractResponse(BaseModel):
    keywords: list[dict]
    total: int


@router.post("/extract", response_model=ExtractResponse)
async def extract_keywords(request: ExtractRequest):
    """从文本中提取关键词"""
    engine = KeywordEngine()
    keywords = engine.extract_keywords(
        request.text,
        top_k=request.top_k,
        method=request.method,
    )
    return ExtractResponse(keywords=keywords, total=len(keywords))


@router.post("/extract-long-tail")
async def extract_long_tail(text: str = Query(..., description="输入文本")):
    """提取长尾关键词"""
    engine = KeywordEngine()
    keywords = engine.extract_long_tail_keywords(text)
    return {"keywords": keywords, "total": len(keywords)}


@router.get("/evaluate")
async def evaluate_keyword(keyword: str = Query(..., description="要评估的关键词")):
    """评估关键词竞争度"""
    engine = KeywordEngine()
    result = engine.evaluate_competition(keyword)
    return {"keyword": keyword, **result}
