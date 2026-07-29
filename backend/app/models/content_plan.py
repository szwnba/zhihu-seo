from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class PlanStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ContentPlan(Base):
    __tablename__ = "content_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    pillar_page_title = Column(String(300), nullable=True)
    target_domain = Column(String(200), nullable=True)
    estimated_traffic = Column(Integer, default=0)
    status = Column(Enum(PlanStatus), default=PlanStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="content_plans")
    articles = relationship("ContentArticle", back_populates="plan")


class ContentArticle(Base):
    __tablename__ = "content_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("content_plans.id"), nullable=False)
    title = Column(String(300), nullable=False)
    target_keyword = Column(String(200), nullable=False)
    search_volume = Column(Integer, default=0)
    competition_score = Column(Float, default=0.0)
    priority_score = Column(Float, default=0.0)
    internal_links_to = Column(Text, nullable=True)  # JSON list of article IDs
    suggested_outline = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    plan = relationship("ContentPlan", back_populates="articles")
