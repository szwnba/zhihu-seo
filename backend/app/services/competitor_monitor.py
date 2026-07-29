"""
竞品监控模块
- 竞品网站关键词布局分析
- 关键词空白发现（Keyword Gap）
- 竞品知乎引用来源追踪
- 定期监控与提醒
"""
import asyncio
import re
from typing import Optional
from urllib.parse import urlparse
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from app.services.baidu_search_volume import BaiduSearchVolume


class CompetitorMonitor:
    """竞品监控分析工具"""
    
    def __init__(self):
        self.baidu = BaiduSearchVolume()
        self.client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)
    
    async def close(self):
        await self.client.aclose()
        await self.baidu.close()
    
    async def analyze_competitor(self, domain: str) -> dict:
        """
        分析竞品网站
        
        Args:
            domain: 竞品域名 (e.g., "example.com")
            
        Returns:
            竞品分析报告
        """
        # 清理域名
        domain = domain.strip().lower()
        if not domain.startswith("http"):
            domain = f"https://{domain}"
        
        # 获取网站基本信息
        site_info = await self._get_site_info(domain)
        
        # 获取竞品关键词（通过 site: 搜索）
        keywords = await self._get_competitor_keywords(domain)
        
        # 获取竞品知乎引用
        zhihu_refs = await self._get_zhihu_references(domain)
        
        # 分析竞品内容结构
        content_structure = await self._analyze_content_structure(domain)
        
        return {
            "domain": domain,
            "analyzed_at": datetime.utcnow().isoformat(),
            "site_info": site_info,
            "keywords": keywords,
            "zhihu_references": zhihu_refs,
            "content_structure": content_structure,
            "total_keywords_found": len(keywords),
        }
    
    async def find_keyword_gap(
        self,
        my_domain: str,
        competitor_domains: list[str],
    ) -> dict:
        """
        发现关键词空白（我有但竞品没有，或竞品有但我没有的词）
        
        Args:
            my_domain: 我的域名
            competitor_domains: 竞品域名列表
            
        Returns:
            关键词空白分析
        """
        # 获取各方关键词
        my_keywords = set(
            kw["keyword"] for kw in await self._get_competitor_keywords(my_domain)
        )
        
        competitor_keywords = set()
        for domain in competitor_domains:
            kws = await self._get_competitor_keywords(domain)
            competitor_keywords.update(kw["keyword"] for kw in kws)
        
        # 计算差异
        unique_to_me = my_keywords - competitor_keywords
        unique_to_competitor = competitor_keywords - my_keywords
        shared = my_keywords & competitor_keywords
        
        return {
            "my_domain": my_domain,
            "competitor_domains": competitor_domains,
            "my_total_keywords": len(my_keywords),
            "competitor_total_keywords": len(competitor_keywords),
            "unique_to_me": list(unique_to_me)[:50],
            "unique_to_competitor": list(unique_to_competitor)[:50],
            "shared_keywords": list(shared)[:50],
            "opportunity_keywords": list(unique_to_competitor)[:20],
        }
    
    async def track_zhihu_references(
        self,
        domain: str,
        max_results: int = 20,
    ) -> list[dict]:
        """
        追踪竞品在知乎的引用来源
        
        Args:
            domain: 竞品域名
            max_results: 最大结果数
            
        Returns:
            知乎引用列表
        """
        # 使用百度搜索 site:zhihu.com + 域名
        search_query = f"site:zhihu.com {domain}"
        
        try:
            url = "https://www.baidu.com/s"
            params = {"wd": search_query, "rn": max_results}
            
            response = await self.client.get(url, params=params)
            soup = BeautifulSoup(response.text, "lxml")
            
            references = []
            results = soup.select(".result")
            
            for result in results[:max_results]:
                title_elem = result.select_one("h3 a")
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.get("href", "")
                
                # 获取摘要
                abstract_elem = result.select_one(".c-abstract")
                abstract = abstract_elem.get_text(strip=True) if abstract_elem else ""
                
                references.append({
                    "title": title,
                    "url": link,
                    "abstract": abstract,
                    "source": "zhihu",
                    "domain": domain,
                })
            
            return references
            
        except Exception as e:
            logger.error(f"Failed to track zhihu references: {e}")
            return []
    
    async def monitor_rankings(
        self,
        keywords: list[str],
        domain: str,
    ) -> list[dict]:
        """
        监控关键词排名
        
        Args:
            keywords: 要监控的关键词
            domain: 目标域名
            
        Returns:
            排名结果
        """
        results = []
        
        for keyword in keywords[:20]:  # 限制查询量
            try:
                rank = await self._check_keyword_rank(keyword, domain)
                results.append({
                    "keyword": keyword,
                    "domain": domain,
                    "rank": rank,
                    "checked_at": datetime.utcnow().isoformat(),
                })
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.warning(f"Rank check failed for '{keyword}': {e}")
        
        return results
    
    async def generate_competitor_report(
        self,
        my_domain: str,
        competitor_domains: list[str],
    ) -> dict:
        """
        生成完整的竞品分析报告
        
        Args:
            my_domain: 我的域名
            competitor_domains: 竞品域名列表
            
        Returns:
            完整竞品分析报告
        """
        # 分析每个竞品
        competitor_analyses = []
        for domain in competitor_domains:
            analysis = await self.analyze_competitor(domain)
            competitor_analyses.append(analysis)
        
        # 关键词空白分析
        keyword_gap = await self.find_keyword_gap(my_domain, competitor_domains)
        
        # 我的网站分析
        my_analysis = await self.analyze_competitor(my_domain)
        
        return {
            "report_title": f"竞品 SEO 分析报告",
            "generated_at": datetime.utcnow().isoformat(),
            "my_domain": my_domain,
            "my_analysis": my_analysis,
            "competitor_analyses": competitor_analyses,
            "keyword_gap": keyword_gap,
            "recommendations": self._generate_recommendations(
                my_analysis, competitor_analyses, keyword_gap
            ),
        }
    
    async def _get_site_info(self, domain: str) -> dict:
        """获取网站基本信息"""
        try:
            response = await self.client.get(domain, timeout=10.0)
            soup = BeautifulSoup(response.text, "lxml")
            
            title = soup.title.get_text(strip=True) if soup.title else ""
            
            meta_desc = ""
            meta_elem = soup.select_one("meta[name='description']")
            if meta_elem:
                meta_desc = meta_elem.get("content", "")
            
            return {
                "title": title,
                "description": meta_desc,
                "url": domain,
            }
        except Exception:
            return {"title": "", "description": "", "url": domain}
    
    async def _get_competitor_keywords(self, domain: str) -> list[dict]:
        """获取竞品关键词"""
        keywords = []
        
        try:
            # 通过百度搜索 site: 指令
            search_query = f"site:{domain.replace('https://', '').replace('http://', '')}"
            
            url = "https://www.baidu.com/s"
            params = {"wd": search_query, "rn": 50}
            
            response = await self.client.get(url, params=params)
            soup = BeautifulSoup(response.text, "lxml")
            
            results = soup.select(".result")
            
            for result in results:
                title_elem = result.select_one("h3 a")
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 从标题提取关键词
                words = re.findall(r"[\u4e00-\u9fff]+", title)
                for word in words:
                    if len(word) >= 4:
                        keywords.append({
                            "keyword": word,
                            "source": "title",
                            "url": title_elem.get("href", ""),
                        })
            
            # 去重
            seen = set()
            unique = []
            for kw in keywords:
                if kw["keyword"] not in seen:
                    seen.add(kw["keyword"])
                    unique.append(kw)
            
            return unique[:30]
            
        except Exception as e:
            logger.error(f"Failed to get competitor keywords: {e}")
            return []
    
    async def _get_zhihu_references(self, domain: str) -> list[dict]:
        """获取知乎引用"""
        return await self.track_zhihu_references(domain)
    
    async def _analyze_content_structure(self, domain: str) -> dict:
        """分析竞品内容结构"""
        try:
            response = await self.client.get(domain, timeout=10.0)
            soup = BeautifulSoup(response.text, "lxml")
            
            # 统计内容结构
            headings = {
                "h1": len(soup.select("h1")),
                "h2": len(soup.select("h2")),
                "h3": len(soup.select("h3")),
                "h4": len(soup.select("h4")),
            }
            
            # 导航链接
            nav_links = []
            for link in soup.select("nav a, .nav a, .menu a, header a")[:20]:
                text = link.get_text(strip=True)
                href = link.get("href", "")
                if text and len(text) < 50:
                    nav_links.append({"text": text, "url": href})
            
            return {
                "headings": headings,
                "navigation": nav_links,
                "has_blog": bool(soup.select(".blog, .post, .article")),
                "has_sitemap": bool(soup.select("a[href*='sitemap']")),
            }
            
        except Exception:
            return {"headings": {}, "navigation": [], "has_blog": False}
    
    async def _check_keyword_rank(
        self,
        keyword: str,
        domain: str,
        max_pages: int = 5,
    ) -> int:
        """检查关键词排名（返回 0 表示未进前 50）"""
        clean_domain = domain.replace("https://", "").replace("http://", "").strip("/")
        
        for page in range(max_pages):
            try:
                url = "https://www.baidu.com/s"
                params = {
                    "wd": keyword,
                    "rn": 10,
                    "pn": page * 10,
                }
                
                await asyncio.sleep(0.5)
                response = await self.client.get(url, params=params)
                soup = BeautifulSoup(response.text, "lxml")
                
                results = soup.select(".result")
                
                for i, result in enumerate(results):
                    title_elem = result.select_one("h3 a")
                    if title_elem:
                        href = title_elem.get("href", "")
                        if clean_domain in href:
                            return page * 10 + i + 1
                
            except Exception:
                continue
        
        return 0  # 未找到
    
    @staticmethod
    def _generate_recommendations(
        my_analysis: dict,
        competitor_analyses: list[dict],
        keyword_gap: dict,
    ) -> list[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于关键词空白的建议
        if keyword_gap.get("unique_to_competitor"):
            count = len(keyword_gap["unique_to_competitor"])
            recommendations.append(
                f"发现 {count} 个竞品有但你没有的关键词，建议优先布局前 20 个"
            )
        
        # 基于竞品结构的建议
        for analysis in competitor_analyses:
            structure = analysis.get("content_structure", {})
            if structure.get("has_blog"):
                recommendations.append(
                    f"竞品 {analysis['domain']} 有博客/内容中心，建议建立类似的内容体系"
                )
        
        # 通用建议
        recommendations.extend([
            "建立支柱页 + 长尾文章的内容集群结构",
            "每周更新 2-3 篇高质量长尾文章",
            "在知乎高赞回答中植入你的网站链接，形成流量闭环",
            "监控竞品关键词变化，及时调整内容策略",
        ])
        
        return recommendations
