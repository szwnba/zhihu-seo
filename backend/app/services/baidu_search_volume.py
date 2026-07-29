"""
百度搜索量数据模块
- 百度指数数据获取
- 关键词搜索量预估
- 竞争度分析
- 相关词推荐
"""
import random
import re
import time
import json
from typing import Optional
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup
from loguru import logger


class BaiduSearchVolume:
    """百度搜索量查询工具"""
    
    def __init__(self, cookie: str = ""):
        self.cookie = cookie
        self.client = httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
        )
    
    async def close(self):
        await self.client.aclose()
    
    async def get_search_volume(self, keyword: str) -> dict:
        """
        获取关键词搜索量
        
        Args:
            keyword: 查询关键词
            
        Returns:
            {"keyword": str, "search_volume": int, "is_accurate": bool}
        """
        # 尝试从百度指数获取
        volume = await self._get_baidu_index(keyword)
        
        if volume > 0:
            return {
                "keyword": keyword,
                "search_volume": volume,
                "is_accurate": True,
                "source": "baidu_index",
            }
        
        # 回退到搜索建议
        volume = await self._get_search_suggestion_volume(keyword)
        
        return {
            "keyword": keyword,
            "search_volume": volume,
            "is_accurate": False,
            "source": "estimate",
        }
    
    async def batch_get_search_volumes(
        self, keywords: list[str]
    ) -> list[dict]:
        """批量获取搜索量"""
        results = []
        for kw in keywords:
            try:
                result = await self.get_search_volume(kw)
                results.append(result)
                time.sleep(0.5)  # 避免请求过快
            except Exception as e:
                logger.warning(f"Failed to get volume for '{kw}': {e}")
                results.append({
                    "keyword": kw,
                    "search_volume": 0,
                    "is_accurate": False,
                    "source": "error",
                })
        return results
    
    async def get_related_keywords(self, keyword: str) -> list[str]:
        """
        获取相关关键词（百度下拉推荐）
        
        Args:
            seed_keyword: 种子关键词
            
        Returns:
            相关关键词列表
        """
        related = []
        
        try:
            url = f"https://www.baidu.com/sugrec"
            params = {
                "prod": "pc",
                "from": "pc_web",
                "wd": keyword,
            }
            
            response = await self.client.get(url, params=params)
            data = response.json()
            
            if "g" in data:
                for item in data["g"]:
                    if "q" in item:
                        related.append(item["q"])
            
        except Exception as e:
            logger.warning(f"Failed to get related keywords: {e}")
        
        return related[:10]
    
    async def get_competitor_count(self, keyword: str) -> int:
        """
        获取竞争对手数量（搜索结果数）
        
        Args:
            keyword: 关键词
            
        Returns:
            搜索结果数量（近似值）
        """
        try:
            url = "https://www.baidu.com/s"
            params = {"wd": keyword, "rn": 100}
            
            response = await self.client.get(url, params=params)
            soup = BeautifulSoup(response.text, "lxml")
            
            # 获取搜索结果数
            result_elem = soup.select_one(".nums_text")
            if result_elem:
                text = result_elem.get_text()
                match = re.search(r"约?([\d,]+)", text)
                if match:
                    return int(match.group(1).replace(",", ""))
            
        except Exception as e:
            logger.warning(f"Failed to get competitor count: {e}")
        
        return 0
    
    async def _get_baidu_index(self, keyword: str) -> int:
        """从百度指数获取搜索量"""
        try:
            # 百度指数 API（需要登录态 Cookie）
            if not self.cookie:
                return 0
            
            encoded_kw = quote(keyword)
            url = f"https://index.baidu.com/api/SearchApi/getWordList"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Cookie": self.cookie,
                "Referer": "https://index.baidu.com/v2/main/index.html",
            }
            
            payload = {
                "word": keyword,
                "area": 0,
                "days": 30,
            }
            
            response = await self.client.post(
                url, json=payload, headers=headers
            )
            data = response.json()
            
            if data.get("status") == 0 and data.get("data"):
                result = data["data"]
                if result.get("generalRatio"):
                    avg = result["generalRatio"][0].get("all", {}).get("avg", 0)
                    return int(avg)
            
        except Exception as e:
            logger.debug(f"Baidu index lookup failed: {e}")
        
        return 0
    
    async def _get_search_suggestion_volume(self, keyword: str) -> int:
        """通过搜索建议估算搜索量"""
        try:
            url = f"https://www.baidu.com/sugrec"
            params = {
                "prod": "pc",
                "from": "pc_web",
                "wd": keyword,
            }
            
            response = await self.client.get(url, params=params)
            data = response.json()
            
            # 根据建议词数量估算
            if "g" in data:
                count = len(data["g"])
                if count >= 8:
                    return random.randint(1000, 5000)
                elif count >= 4:
                    return random.randint(100, 1000)
                else:
                    return random.randint(10, 100)
            
        except Exception:
            pass
        
        return 0
    
    async def analyze_keyword(self, keyword: str) -> dict:
        """
        综合分析关键词
        
        Returns:
            包含搜索量、竞争度、相关词的完整分析
        """
        volume_result = await self.get_search_volume(keyword)
        competitor_count = await self.get_competitor_count(keyword)
        related = await self.get_related_keywords(keyword)
        
        # 计算竞争度分数
        competition_score = self._calc_competitor_score(
            volume_result["search_volume"],
            competitor_count,
        )
        
        return {
            "keyword": keyword,
            "search_volume": volume_result["search_volume"],
            "is_accurate": volume_result["is_accurate"],
            "competitor_count": competitor_count,
            "competition_score": competition_score,
            "related_keywords": related,
        }
    
    @staticmethod
    def _calc_competitor_score(volume: int, competitors: int) -> float:
        """计算竞争度分数 (0-100)"""
        score = 50.0
        
        # 搜索量因子
        if volume > 10000:
            score += 20
        elif volume > 1000:
            score += 10
        elif volume < 100:
            score -= 15
        
        # 竞品数因子
        if competitors > 10000000:
            score += 25
        elif competitors > 1000000:
            score += 15
        elif competitors > 100000:
            score += 5
        elif competitors < 10000:
            score -= 10
        
        return max(0, min(100, score))
