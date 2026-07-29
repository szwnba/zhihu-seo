from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "Zhihu SEO Gold Miner"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/zhihu_seo.db"
    
    REDIS_URL: str = "redis://localhost:6379/0"
    
    SECRET_KEY: str = "zhihu-seo-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    ZHIHU_BASE_URL: str = "https://www.zhihu.com"
    ZHIHU_API_URL: str = "https://www.zhihu.com/api/v4"
    
    CRAWL_DELAY_SECONDS: float = 2.0
    MAX_ANSWERS_PER_QUESTION: int = 50
    MIN_VOTE_THRESHOLD: int = 100
    
    class Config:
        env_file = ".env"


settings = Settings()
