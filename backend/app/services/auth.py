"""
用户认证模块
- 用户注册/登录
- JWT Token 认证
- 密码加密
- 付费等级管理
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, PlanTier

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
security = HTTPBearer()


# ============== Pydantic 模型 ==============

class UserRegister(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserProfile(BaseModel):
    id: int
    email: str
    username: str
    plan_tier: PlanTier
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


class UserUpgrade(BaseModel):
    plan_tier: PlanTier


# ============== 认证服务 ==============

class AuthService:
    """用户认证服务"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """加密密码"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """创建 JWT Token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """解码 JWT Token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )
            return payload
        except JWTError:
            return None
    
    @classmethod
    def register_user(
        cls,
        db: Session,
        user_data: UserRegister,
    ) -> User:
        """注册新用户"""
        # 检查邮箱是否已存在
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        # 检查用户名是否已存在
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        
        # 创建用户
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=cls.hash_password(user_data.password),
            plan_tier=PlanTier.FREE,
            is_active=True,
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @classmethod
    def authenticate_user(
        cls,
        db: Session,
        username: str,
        password: str,
    ) -> Optional[User]:
        """验证用户登录"""
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return None
        
        if not cls.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    @classmethod
    def get_user_profile(cls, db: Session, user_id: int) -> Optional[User]:
        """获取用户资料"""
        return db.query(User).filter(User.id == user_id).first()
    
    @classmethod
    def upgrade_plan(
        cls,
        db: Session,
        user_id: int,
        new_plan: PlanTier,
    ) -> User:
        """升级用户套餐"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        user.plan_tier = new_plan
        db.commit()
        db.refresh(user)
        
        return user
    
    @classmethod
    def check_plan_limit(
        cls,
        user: PlanTier,
        feature: str,
    ) -> dict:
        """检查用户套餐权限"""
        limits = {
            PlanTier.FREE: {
                "max_bookmarks_per_month": 1,
                "max_keywords_per_task": 50,
                "max_clusters": 3,
                "max_content_plans": 1,
                "has_competitor_monitor": False,
                "has_api_access": False,
                "has_priority_support": False,
            },
            PlanTier.PRO: {
                "max_bookmarks_per_month": 999,
                "max_keywords_per_task": 9999,
                "max_clusters": 20,
                "max_content_plans": 50,
                "has_competitor_monitor": True,
                "has_api_access": False,
                "has_priority_support": False,
            },
            PlanTier.ENTERPRISE: {
                "max_bookmarks_per_month": 9999,
                "max_keywords_per_task": 99999,
                "max_clusters": 999,
                "max_content_plans": 999,
                "has_competitor_monitor": True,
                "has_api_access": True,
                "has_priority_support": True,
            },
        }
        
        user_limits = limits.get(user, limits[PlanTier.FREE])
        
        return {
            "plan_tier": user,
            "limits": user_limits,
            "can_use_feature": user_limits.get(feature, True)
            if isinstance(user_limits.get(feature), bool)
            else True,
        }


# ============== 依赖函数 ==============

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """获取当前认证用户"""
    token = credentials.credentials
    
    payload = AuthService.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = AuthService.get_user_profile(db, int(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


def require_plan(required_plan: PlanTier):
    """套餐权限检查装饰器"""
    async def checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        plan_hierarchy = {
            PlanTier.FREE: 0,
            PlanTier.PRO: 1,
            PlanTier.ENTERPRISE: 2,
        }
        
        user_level = plan_hierarchy.get(current_user.plan_tier, 0)
        required_level = plan_hierarchy.get(required_plan, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {required_plan.value} plan or higher",
            )
        
        return current_user
    
    return checker
