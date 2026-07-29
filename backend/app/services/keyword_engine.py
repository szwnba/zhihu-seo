"""
关键词提取与聚类引擎
- 中文分词 (jieba)
- 关键词提取 (TF-IDF + TextRank)
- 关键词聚类 (K-Means)
- 竞争度评估
"""
import re
from collections import Counter
from typing import Optional

import jieba
import jieba.analyse
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from loguru import logger

from app.core.config import settings


# 停用词列表（中文 + 英文常见停用词）
STOP_WORDS = set([
    # 中文停用词
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "被",
    "把", "让", "又", "什么", "怎么", "如何", "为什么", "哪", "哪个",
    "可以", "这个", "那个", "这些", "那些", "还是", "但是", "因为", "所以",
    "如果", "虽然", "或者", "以及", "而且", "不过", "然后", "只是", "一样",
    "应该", "可能", "需要", "已经", "还是", "还有", "这是", "那是", "哪个",
    "怎样", "怎么样", "多少", "哪里", "什么时候", "谁", "哪样", "怎么",
    # 英文停用词
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "just",
    "because", "but", "and", "or", "if", "while", "about", "up", "it",
    "its", "this", "that", "these", "those", "i", "me", "my", "myself",
    "we", "our", "ours", "you", "your", "he", "him", "his", "she", "her",
])


class KeywordEngine:
    """关键词提取与聚类引擎"""
    
    def __init__(self):
        # 配置 jieba
        jieba.setLogLevel(jieba.logging.INFO)
        # 添加自定义词典（SEO 相关词汇）
        self._add_custom_words()
    
    def _add_custom_words(self):
        """添加 SEO 和营销相关自定义词汇"""
        custom_words = [
            "搜索引擎优化", "长尾关键词", "关键词挖掘", "内容矩阵",
            "SEO", "SEM", "流量", "转化率", "点击率", "排名",
            "百度指数", "竞争度", "搜索量", "关键词密度",
            "内链", "外链", "权重", "收录", "快照",
            "知乎", "小红书", "抖音", "B站", "公众号",
            "独立站", "内容营销", "用户画像", "痛点分析",
            "话题热度", "热门话题", "趋势分析", "蓝海词",
        ]
        for word in custom_words:
            jieba.add_word(word)
    
    def extract_keywords(
        self,
        text: str,
        top_k: int = 20,
        method: str = "tfidf",
        allow_pos: tuple = ("n", "nr", "ns", "nt", "nz", "v", "vn", "eng"),
    ) -> list[dict]:
        """
        从文本中提取关键词
        
        Args:
            text: 输入文本
            top_k: 返回前 K 个关键词
            method: 提取方法 ("tfidf" 或 "textrank")
            allow_pos: 允许的词性
            
        Returns:
            [{"keyword": str, "weight": float, "pos": str}, ...]
        """
        if not text or len(text.strip()) < 10:
            return []
        
        # 清洗文本
        cleaned_text = self._clean_text(text)
        
        if method == "textrank":
            return self._extract_textrank(cleaned_text, top_k, allow_pos)
        else:
            return self._extract_tfidf(cleaned_text, top_k, allow_pos)
    
    def _extract_tfidf(
        self, text: str, top_k: int, allow_pos: tuple
    ) -> list[dict]:
        """使用 TF-IDF 提取关键词"""
        keywords = jieba.analyse.extract_tags(
            text,
            topK=top_k * 2,  # 多取一些用于过滤
            withWeight=True,
            allowPOS=allow_pos,
        )
        
        results = []
        for word, weight in keywords:
            if word.lower() in STOP_WORDS or len(word) < 2:
                continue
            pos = self._get_word_pos(word)
            results.append({
                "keyword": word,
                "weight": round(weight, 4),
                "pos": pos,
            })
            if len(results) >= top_k:
                break
        
        return results
    
    def _extract_textrank(
        self, text: str, top_k: int, allow_pos: tuple
    ) -> list[dict]:
        """使用 TextRank 提取关键词"""
        keywords = jieba.analyse.textrank(
            text,
            topK=top_k * 2,
            withWeight=True,
            allowPOS=allow_pos,
        )
        
        results = []
        for word, weight in keywords:
            if word.lower() in STOP_WORDS or len(word) < 2:
                continue
            pos = self._get_word_pos(word)
            results.append({
                "keyword": word,
                "weight": round(weight, 4),
                "pos": pos,
            })
            if len(results) >= top_k:
                break
        
        return results
    
    def extract_long_tail_keywords(
        self,
        text: str,
        min_length: int = 4,
        max_length: int = 20,
    ) -> list[dict]:
        """
        提取长尾关键词（短语级别）
        
        Args:
            text: 输入文本
            min_length: 最小词长（字符数）
            max_length: 最大词长（字符数）
            
        Returns:
            长尾关键词列表
        """
        if not text:
            return []
        
        cleaned = self._clean_text(text)
        
        # 使用 jieba 分词
        words = list(jieba.cut(cleaned))
        
        # 过滤停用词和短词
        filtered = [
            w for w in words
            if w not in STOP_WORDS
            and len(w.strip()) >= 2
            and not w.isdigit()
        ]
        
        # 生成 2-4 gram 短语
        phrases = []
        for n in range(2, 5):
            for i in range(len(filtered) - n + 1):
                phrase = "".join(filtered[i:i + n])
                if min_length <= len(phrase) <= max_length:
                    phrases.append(phrase)
        
        # 统计频率
        phrase_counts = Counter(phrases)
        
        # 过滤低频短语（至少出现 2 次）
        results = []
        for phrase, count in phrase_counts.most_common(100):
            if count < 2:
                continue
            results.append({
                "keyword": phrase,
                "frequency": count,
                "length": len(phrase),
            })
        
        return results[:50]
    
    def cluster_keywords(
        self,
        keywords: list[str],
        n_clusters: int = 5,
    ) -> list[dict]:
        """
        对关键词进行聚类
        
        Args:
            keywords: 关键词列表
            n_clusters: 聚类数量
            
        Returns:
            [{"cluster_id": int, "name": str, "keywords": [...]}, ...]
        """
        if len(keywords) < n_clusters:
            n_clusters = max(1, len(keywords) // 2)
        
        # 分词并向量化
        vectorizer = TfidfVectorizer(
            tokenizer=lambda x: list(jieba.cut(x)),
            token_pattern=None,
            max_features=5000,
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(keywords)
        except Exception as e:
            logger.error(f"Vectorization failed: {e}")
            return [{"cluster_id": 0, "name": "全部", "keywords": keywords}]
        
        # K-Means 聚类
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10,
        )
        labels = kmeans.fit_predict(tfidf_matrix)
        
        # 组织结果
        clusters = {}
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(keywords[i])
        
        results = []
        for cluster_id, words in clusters.items():
            # 选择 TF-IDF 权重最高的词作为聚类名称
            center = kmeans.cluster_centers_[cluster_id]
            top_idx = center.argsort()[-3:][::-1]
            feature_names = vectorizer.get_feature_names_out()
            cluster_name = "-".join([feature_names[i] for i in top_idx if i < len(feature_names)])
            
            results.append({
                "cluster_id": int(cluster_id),
                "name": cluster_name or f"主题{cluster_id + 1}",
                "keywords": words,
                "keyword_count": len(words),
            })
        
        return sorted(results, key=lambda x: x["keyword_count"], reverse=True)
    
    def evaluate_competition(
        self,
        keyword: str,
        search_volume: int = 0,
    ) -> dict:
        """
        评估关键词竞争度
        
        Args:
            keyword: 关键词
            search_volume: 搜索量
            
        Returns:
            {"score": float, "tier": str, "suggestion": str}
        """
        # 基于关键词特征评估竞争度
        score = 50.0  # 基础分
        
        # 长度因子：越长尾竞争越低
        length = len(keyword)
        if length >= 10:
            score -= 15
        elif length >= 6:
            score -= 5
        elif length <= 3:
            score += 15
        
        # 搜索量因子
        if search_volume > 10000:
            score += 20
        elif search_volume > 1000:
            score += 10
        elif search_volume > 100:
            score += 0
        else:
            score -= 10
        
        # 商业意图词加分（竞争更高）
        commercial_words = ["购买", "价格", "推荐", "最好", "排名", "对比", "评测"]
        for word in commercial_words:
            if word in keyword:
                score += 5
        
        # 限制范围
        score = max(0, min(100, score))
        
        # 分级
        if score >= 70:
            tier = "high"
            suggestion = "竞争激烈，建议寻找更细分的长尾词"
        elif score >= 40:
            tier = "medium"
            suggestion = "中等竞争，有一定机会"
        else:
            tier = "low"
            suggestion = "竞争较低，建议优先布局"
        
        return {
            "score": round(score, 1),
            "tier": tier,
            "suggestion": suggestion,
        }
    
    def generate_content_matrix(
        self,
        clusters: list[dict],
        target_domain: str = "",
    ) -> dict:
        """
        基于关键词聚类生成内容矩阵
        
        Args:
            clusters: 聚类结果
            target_domain: 目标域名
            
        Returns:
            内容矩阵方案
        """
        matrix = {
            "pillar_pages": [],
            "supporting_articles": [],
            "internal_links": [],
        }
        
        for cluster in clusters:
            # 每个聚类生成一个支柱页
            pillar = {
                "title": f"{cluster['name']} - 完整指南",
                "target_keyword": cluster["keywords"][0] if cluster["keywords"] else "",
                "cluster_id": cluster["cluster_id"],
                "estimated_articles": max(3, len(cluster["keywords"]) // 2),
            }
            matrix["pillar_pages"].append(pillar)
            
            # 为每个关键词生成文章
            for kw in cluster["keywords"][:10]:
                article = {
                    "title": f"{kw}：深入解析与实战指南",
                    "target_keyword": kw,
                    "cluster_id": cluster["cluster_id"],
                    "pillar_keyword": cluster["name"],
                }
                matrix["supporting_articles"].append(article)
            
            # 内部链接建议
            if len(cluster["keywords"]) > 1:
                matrix["internal_links"].append({
                    "from": cluster["keywords"][0],
                    "to": cluster["keywords"][1],
                    "type": "cluster_internal",
                })
        
        return matrix
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """清洗文本"""
        # 移除 HTML 标签
        text = re.sub(r"<[^>]+>", "", text)
        # 移除 URL
        text = re.sub(r"http[s]?://\S+", "", text)
        # 移除特殊字符
        text = re.sub(r"[^\w\s\u4e00-\u9fff]", " ", text)
        # 移除多余空白
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    
    @staticmethod
    def _get_word_pos(word: str) -> str:
        """获取词语词性（简化版）"""
        # 简单判断
        if re.match(r"^[a-zA-Z]+$", word):
            return "eng"
        if len(word) >= 4:
            return "nz"  # 其他专名
        return "n"  # 名词


# 便捷函数
def extract_keywords_from_text(
    text: str,
    top_k: int = 20,
    method: str = "tfidf",
) -> list[dict]:
    """便捷函数：从文本提取关键词"""
    engine = KeywordEngine()
    return engine.extract_keywords(text, top_k=top_k, method=method)


def cluster_keywords_list(
    keywords: list[str],
    n_clusters: int = 5,
) -> list[dict]:
    """便捷函数：聚类关键词"""
    engine = KeywordEngine()
    return engine.cluster_keywords(keywords, n_clusters=n_clusters)
