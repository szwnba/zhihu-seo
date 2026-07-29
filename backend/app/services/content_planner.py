"""
内容矩阵规划器
- 基于关键词聚类生成内容矩阵
- 支柱页 + 长尾文章结构
- 内部链接建议
- SEO 流量预估
"""
import json
from typing import Optional

from loguru import logger

from app.services.keyword_engine import KeywordEngine


class ContentPlanner:
    """内容矩阵规划器"""
    
    def __init__(self):
        self.keyword_engine = KeywordEngine()
    
    def generate_matrix(
        self,
        keywords: list[dict],
        clusters: list[dict],
        target_domain: str = "",
    ) -> dict:
        """
        生成完整的内容矩阵方案
        
        Args:
            keywords: 关键词列表
            clusters: 聚类结果
            target_domain: 目标域名
            
        Returns:
            内容矩阵方案
        """
        matrix = {
            "summary": self._generate_summary(keywords, clusters),
            "pillar_pages": [],
            "content_clusters": [],
            "internal_link_map": [],
            "priority_queue": [],
            "seo_forecast": self._forecast_traffic(keywords),
        }
        
        # 为每个聚类生成内容方案
        for cluster in clusters:
            cluster_plan = self._plan_cluster_content(cluster, target_domain)
            matrix["content_clusters"].append(cluster_plan)
            
            # 添加支柱页
            if cluster_plan["pillar_page"]:
                matrix["pillar_pages"].append(cluster_plan["pillar_page"])
            
            # 添加内部链接
            matrix["internal_link_map"].extend(cluster_plan["internal_links"])
        
        # 生成优先级队列
        matrix["priority_queue"] = self._generate_priority_queue(matrix["content_clusters"])
        
        return matrix
    
    def _plan_cluster_content(
        self,
        cluster: dict,
        target_domain: str = "",
    ) -> dict:
        """为单个聚类规划内容"""
        cluster_name = cluster.get("name", "")
        keywords = cluster.get("keywords", [])
        
        if not keywords:
            return {
                "cluster_name": cluster_name,
                "pillar_page": None,
                "articles": [],
                "internal_links": [],
            }
        
        # 选择核心词（第一个或权重最高的）
        pillar_keyword = keywords[0]
        
        # 生成支柱页
        pillar_page = {
            "title": f"{pillar_keyword}完全指南：从入门到精通",
            "target_keyword": pillar_keyword,
            "word_count_target": 5000,
            "content_type": "pillar",
            "description": f"关于{pillar_keyword}的全面深度指南，覆盖所有关键知识点",
        }
        
        # 为每个关键词生成文章
        articles = []
        for i, kw in enumerate(keywords[:15]):  # 最多15篇
            article = {
                "title": f"{kw}：深度解析与实操建议",
                "target_keyword": kw,
                "word_count_target": 2000 + (i * 200),
                "content_type": "supporting",
                "priority": max(1, 10 - i),
                "description": f"深入探讨{kw}的核心要点和实践方法",
            }
            articles.append(article)
        
        # 内部链接结构
        internal_links = []
        for article in articles:
            # 每篇文章链接回支柱页
            internal_links.append({
                "from": article["target_keyword"],
                "to": pillar_keyword,
                "link_type": "to_pillar",
                "anchor_text": f"{pillar_keyword}指南",
            })
            
            # 相关文章互相链接
            for other in articles:
                if other["target_keyword"] != article["target_keyword"]:
                    internal_links.append({
                        "from": article["target_keyword"],
                        "to": other["target_keyword"],
                        "link_type": "cross_link",
                        "anchor_text": other["target_keyword"],
                    })
        
        return {
            "cluster_name": cluster_name,
            "pillar_page": pillar_page,
            "articles": articles,
            "internal_links": internal_links[:50],  # 限制数量
        }
    
    def _generate_summary(self, keywords: list, clusters: list) -> dict:
        """生成内容矩阵摘要"""
        total_keywords = len(keywords)
        total_clusters = len(clusters)
        
        # 计算预估总文章数
        total_articles = sum(
            len(c.get("keywords", [])) + 1 for c in clusters
        )
        
        return {
            "total_keywords": total_keywords,
            "total_clusters": total_clusters,
            "estimated_articles": min(total_articles, 200),
            "estimated_pillar_pages": total_clusters,
            "content_depth": "deep" if total_keywords > 50 else "medium" if total_keywords > 20 else "basic",
        }
    
    def _generate_priority_queue(self, content_clusters: list) -> list[dict]:
        """生成内容优先级队列"""
        queue = []
        
        for cluster in content_clusters:
            # 支柱页优先级最高
            if cluster.get("pillar_page"):
                queue.append({
                    "keyword": cluster["pillar_page"]["target_keyword"],
                    "title": cluster["pillar_page"]["title"],
                    "priority": 10,
                    "type": "pillar",
                    "reason": "主题支柱页，建立领域权威",
                })
            
            # 文章按优先级排序
            for article in cluster.get("articles", []):
                queue.append({
                    "keyword": article["target_keyword"],
                    "title": article["title"],
                    "priority": article.get("priority", 5),
                    "type": "supporting",
                    "reason": f"支持「{cluster['cluster_name']}」主题",
                })
        
        # 按优先级排序
        queue.sort(key=lambda x: x["priority"], reverse=True)
        
        # 添加排名
        for i, item in enumerate(queue):
            item["rank"] = i + 1
        
        return queue[:100]  # 最多100个
    
    def _forecast_traffic(self, keywords: list) -> dict:
        """预估 SEO 流量"""
        total_search_volume = sum(
            kw.get("search_volume", 0) for kw in keywords
        )
        
        # 简化的流量预估模型
        # 假设：排名第一获得 30% 点击率，排名第二 15%，第三 10%
        estimated_monthly_traffic = int(total_search_volume * 0.15)  # 保守估计
        
        return {
            "total_search_volume": total_search_volume,
            "estimated_monthly_traffic": estimated_monthly_traffic,
            "assumptions": [
                "平均搜索量基于关键词预估",
                "点击率假设为 15%（排名靠前位置）",
                "实际流量受内容质量、域名权重等因素影响",
            ],
            "timeline_months": {
                "month_1": int(estimated_monthly_traffic * 0.1),
                "month_3": int(estimated_monthly_traffic * 0.4),
                "month_6": int(estimated_monthly_traffic * 0.7),
                "month_12": estimated_monthly_traffic,
            },
        }
    
    def generate_seo_report(
        self,
        keywords: list[dict],
        clusters: list[dict],
        target_domain: str = "",
    ) -> dict:
        """
        生成完整的 SEO 分析报告
        
        Args:
            keywords: 关键词列表
            clusters: 聚类结果
            target_domain: 目标域名
            
        Returns:
            SEO 报告
        """
        # 竞争度分析
        competition_analysis = []
        for kw in keywords[:50]:
            evaluation = self.keyword_engine.evaluate_competition(
                kw.get("keyword", ""),
                kw.get("search_volume", 0),
            )
            competition_analysis.append({
                "keyword": kw.get("keyword"),
                "search_volume": kw.get("search_volume"),
                **evaluation,
            })
        
        # 内容矩阵
        content_matrix = self.generate_matrix(keywords, clusters, target_domain)
        
        return {
            "report_title": f"知乎 SEO 关键词分析报告 - {target_domain or '未指定域名'}",
            "total_keywords": len(keywords),
            "total_clusters": len(clusters),
            "competition_analysis": competition_analysis,
            "content_matrix": content_matrix,
            "top_opportunities": self._find_opportunities(keywords),
        }
    
    def _find_opportunities(self, keywords: list) -> list[dict]:
        """发现 SEO 机会（高搜索量 + 低竞争）"""
        opportunities = []
        
        for kw in keywords:
            volume = kw.get("search_volume", 0)
            competition = kw.get("competition_score", 50)
            
            # 机会分数 = 搜索量 / (竞争度 + 1)
            opportunity_score = volume / (competition + 1)
            
            if volume > 100 and competition < 50:
                opportunities.append({
                    "keyword": kw.get("keyword"),
                    "search_volume": volume,
                    "competition_score": competition,
                    "opportunity_score": round(opportunity_score, 2),
                })
        
        # 按机会分数排序
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        return opportunities[:20]


# 便捷函数
def generate_content_matrix(
    keywords: list[dict],
    clusters: list[dict],
    target_domain: str = "",
) -> dict:
    """便捷函数：生成内容矩阵"""
    planner = ContentPlanner()
    return planner.generate_matrix(keywords, clusters, target_domain)
