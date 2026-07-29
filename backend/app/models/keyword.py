from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class KeywordTier(str, enum.Enum):
    HIGH = "high"       # 高搜索量 + 低竞争
    MEDIUM = "medium"   # 中等
    LOW = "low"         # 低搜索量或高竞争


keyword_cluster_mapping = Table(
    "keyword_cluster_mapping",
    Base.metadata,
    Column("keyword_id", Integer, ForeignKey("keywords.id")),
    Column("cluster_id", Integer, ForeignKey("keyword_clusters.id")),
)


class Keyword(Base):
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("crawl_tasks.id"), nullable=False)
    keyword = Column(String(200), index=True, nullable=False)
    search_volume = Column(Integer, default=0)
    competition_score = Column(Float, default=0.0)
    tier = Column(Enum(KeywordTier), default=KeywordTier.MEDIUM)
    source_question = Column(String(500), nullable=True)
    source_answer_excerpt = Column(Text, nullable=True)
    vote_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="keywords")
    task = relationship("CrawlTask", back_populates="keywords")
    clusters = relationship("KeywordCluster", secondary=keyword_cluster_mapping, back_populates="keywords")


class KeywordCluster(Base):
    __tablename__ = "keyword_clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    pillar_keyword = Column(String(200), nullable=True)
    total_search_volume = Column(Integer, default=0)
    avg_competition = Column(Float, default=0.0)
    keyword_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    keywords = relationship("Keyword", secondary=keyword_cluster_mapping, back_populates="clusters")
