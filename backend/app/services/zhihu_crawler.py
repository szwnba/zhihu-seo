"""
知乎爬虫模块（增强版）
- 收藏夹抓取
- 高赞回答提取
- 问题详情获取
- 登录态支持（Cookie）
- 反爬策略（随机延迟、User-Agent轮换、IP代理）
- 自动重试机制
"""
import asyncio
import json
import os
import random
import re
import time
from typing import Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import settings


# User-Agent 池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]


class ZhihuCrawler:
    """知乎数据爬虫（增强版）"""
    
    def __init__(
        self,
        cookie: str = "",
        proxy: str = "",
        min_delay: float = 1.5,
        max_delay: float = 4.0,
        max_retries: int = 3,
    ):
        self.cookie = cookie
        self.proxy = proxy
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self._request_count = 0
        self._last_request_time = 0
        
        # 创建客户端
        headers = self._build_headers()
        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
            follow_redirects=True,
            proxies={"http://": proxy, "https://": proxy} if proxy else None,
        )
    
    def _build_headers(self) -> dict:
        """构建请求头"""
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
        
        if self.cookie:
            headers["Cookie"] = self.cookie
        
        return headers
    
    async def close(self):
        await self.client.aclose()
    
    async def _smart_delay(self):
        """智能延迟"""
        now = time.time()
        elapsed = now - self._last_request_time
        
        # 随机延迟
        delay = random.uniform(self.min_delay, self.max_delay)
        
        # 每 10 次请求增加额外延迟
        if self._request_count > 0 and self._request_count % 10 == 0:
            delay += random.uniform(3, 6)
            logger.info(f"Taking a longer break after {self._request_count} requests")
        
        if elapsed < delay:
            await asyncio.sleep(delay - elapsed)
        
        self._last_request_time = time.time()
        self._request_count += 1
    
    async def _get(self, url: str, params: dict = None) -> Optional[str]:
        """发送 GET 请求（带重试）"""
        for attempt in range(self.max_retries):
            try:
                await self._smart_delay()
                
                # 每次请求轮换 User-Agent
                self.client.headers["User-Agent"] = random.choice(USER_AGENTS)
                
                response = await self.client.get(url, params=params)
                
                # 检查是否被反爬
                if response.status_code == 429:
                    wait_time = random.uniform(10, 30)
                    logger.warning(f"Rate limited, waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                    continue
                
                if response.status_code == 403:
                    logger.warning("Access forbidden, may need login")
                    return None
                
                response.raise_for_status()
                return response.text
                
            except httpx.TimeoutException:
                logger.warning(f"Timeout (attempt {attempt + 1}/{self.max_retries})")
                await asyncio.sleep(random.uniform(2, 5))
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e}")
                if e.response.status_code in [500, 502, 503]:
                    await asyncio.sleep(random.uniform(3, 7))
                    continue
                return None
            except Exception as e:
                logger.error(f"Request failed: {e}")
                await asyncio.sleep(random.uniform(1, 3))
        
        return None
    
    async def crawl_bookmark_collection(
        self,
        collection_url: str,
        min_votes: int = 100,
        max_pages: int = 10,
        progress_callback=None,
    ) -> list[dict]:
        """爬取知乎收藏夹内容"""
        answers = []
        
        for page in range(1, max_pages + 1):
            logger.info(f"Crawling bookmark page {page}")
            
            params = {"page": page}
            html = await self._get(collection_url, params=params)
            
            if not html:
                break
            
            soup = BeautifulSoup(html, "lxml")
            items = soup.select(".zm-item")
            
            if not items:
                break
            
            for item in items:
                try:
                    answer_data = await self._parse_collection_item(item, min_votes)
                    if answer_data:
                        answers.append(answer_data)
                except Exception as e:
                    logger.warning(f"Failed to parse item: {e}")
                    continue
            
            if progress_callback:
                progress_callback(page, len(answers))
            
            # 检查是否有下一页
            next_btn = soup.select_one(".zu-button-next")
            if not next_btn or "disabled" in str(next_btn):
                break
        
        logger.info(f"Total answers collected: {len(answers)}")
        return answers
    
    async def _parse_collection_item(self, item, min_votes: int) -> Optional[dict]:
        """解析收藏夹中的单个回答"""
        vote_elem = item.select_one(".zm-item-vote-count")
        if not vote_elem:
            return None
        
        votes_text = vote_elem.get_text(strip=True)
        votes = self._parse_votes(votes_text)
        
        if votes < min_votes:
            return None
        
        title_elem = item.select_one(".zm-item-title a")
        if not title_elem:
            return None
        
        question_title = title_elem.get_text(strip=True)
        question_url = title_elem.get("href", "")
        if question_url and not question_url.startswith("http"):
            question_url = f"https://www.zhihu.com{question_url}"
        
        content_elem = item.select_one(".zm-item-rich-text")
        content = content_elem.get_text(strip=True) if content_elem else ""
        
        author_elem = item.select_one(".author-link")
        author = author_elem.get_text(strip=True) if author_elem else "匿名用户"
        
        answer_link = item.select_one(".js-collapse-body a")
        answer_url = answer_link.get("href", "") if answer_link else ""
        if answer_url and not answer_url.startswith("http"):
            answer_url = f"https://www.zhihu.com{answer_url}"
        
        return {
            "title": question_title,
            "content": content,
            "votes": votes,
            "author": author,
            "question_url": question_url,
            "answer_url": answer_url,
        }
    
    async def crawl_question_answers(
        self,
        question_url: str,
        min_votes: int = 100,
        max_answers: int = 50,
    ) -> list[dict]:
        """爬取问题下的高赞回答（通过 API）"""
        answers = []
        question_id = self._extract_question_id(question_url)
        
        if not question_id:
            return answers
        
        offset = 0
        limit = 20
        
        while len(answers) < max_answers:
            api_url = f"{settings.ZHIHU_API_URL}/questions/{question_id}/answers"
            params = {
                "include": "content,voteup_count,author,question",
                "limit": limit,
                "offset": offset,
                "sort_by": "default",
            }
            
            try:
                await self._smart_delay()
                self.client.headers["User-Agent"] = random.choice(USER_AGENTS)
                
                response = await self.client.get(api_url, params=params)
                data = response.json()
                
                if "data" not in data or not data["data"]:
                    break
                
                for item in data["data"]:
                    votes = item.get("voteup_count", 0)
                    if votes < min_votes:
                        continue
                    
                    content_html = item.get("content", "")
                    content_text = BeautifulSoup(content_html, "lxml").get_text(strip=True)
                    
                    author_info = item.get("author", {})
                    author_name = author_info.get("name", "匿名用户")
                    
                    question_info = item.get("question", {})
                    question_title = question_info.get("title", "")
                    
                    answers.append({
                        "title": question_title,
                        "content": content_text,
                        "votes": votes,
                        "author": author_name,
                        "question_url": question_url,
                        "answer_url": f"{question_url}/answer/{item.get('id', '')}",
                    })
                
                paging = data.get("paging", {})
                if paging.get("is_end", True):
                    break
                
                offset += limit
                
            except Exception as e:
                logger.error(f"Failed to fetch answers: {e}")
                break
        
        return answers[:max_answers]
    
    async def crawl_from_cookie_file(self, cookie_path: str) -> bool:
        """从文件加载 Cookie"""
        try:
            if os.path.exists(cookie_path):
                with open(cookie_path, "r") as f:
                    self.cookie = f.read().strip()
                self.client.headers["Cookie"] = self.cookie
                logger.info(f"Loaded cookie from {cookie_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to load cookie: {e}")
        return False
    
    @staticmethod
    def _parse_votes(votes_text: str) -> int:
        """解析赞同数字符串"""
        votes_text = votes_text.strip()
        if not votes_text:
            return 0
        
        match = re.match(r"([\d.]+)\s*K", votes_text, re.IGNORECASE)
        if match:
            return int(float(match.group(1)) * 1000)
        
        match = re.match(r"([\d.]+)\s*W", votes_text, re.IGNORECASE)
        if match:
            return int(float(match.group(1)) * 10000)
        
        try:
            return int(votes_text)
        except ValueError:
            return 0
    
    @staticmethod
    def _extract_question_id(url: str) -> Optional[str]:
        """从 URL 中提取问题 ID"""
        match = re.search(r"/question/(\d+)", url)
        if match:
            return match.group(1)
        
        match = re.search(r"question/(\d+)", url)
        if match:
            return match.group(1)
        
        return None


# 便捷函数
async def crawl_zhihu_bookmark(
    url: str,
    min_votes: int = 100,
    max_pages: int = 10,
    cookie: str = "",
) -> list[dict]:
    """便捷函数：爬取知乎收藏夹"""
    crawler = ZhihuCrawler(cookie=cookie)
    try:
        results = await crawler.crawl_bookmark_collection(
            url, min_votes=min_votes, max_pages=max_pages
        )
        return results
    finally:
        await crawler.close()
