from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import PlanTier
from app.services.auth import (
    AuthService,
    UserRegister,
    UserLogin,
    TokenResponse,
    UserProfile,
    UserUpgrade,
    get_current_user,
)
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    user = AuthService.register_user(db, user_data)
    
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return TokenResponse(
        access_token=access_token,
        user=UserProfile.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = AuthService.authenticate_user(
        db, user_data.username, user_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return TokenResponse(
        access_token=access_token,
        user=UserProfile.model_validate(user),
    )


@router.get("/me", response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserProfile.model_validate(current_user)


@router.get("/plan")
async def get_plan(current_user: User = Depends(get_current_user)):
    """获取当前套餐信息"""
    plan_info = AuthService.check_plan_limit(
        current_user.plan_tier, ""
    )
    return plan_info


@router.post("/upgrade")
async def upgrade_plan(
    upgrade: UserUpgrade,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """升级套餐（模拟支付）"""
    # TODO: 集成真实支付
    user = AuthService.upgrade_plan(db, current_user.id, upgrade.plan_tier)
    return {
        "message": f"Upgraded to {upgrade.plan_tier.value}",
        "user": UserProfile.model_validate(user),
    }
