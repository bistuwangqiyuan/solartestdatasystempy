"""
认证相关API端点
"""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from supabase import Client
from loguru import logger

from app.core.config import settings
from app.core.database import get_db
from app.core.auth import (
    create_access_token,
    get_current_active_user,
    Token,
    User
)

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Client = Depends(get_db)
) -> Any:
    """
    用户登录
    
    使用邮箱和密码登录，返回访问令牌
    """
    try:
        # 使用Supabase认证
        response = db.auth.sign_in_with_password({
            "email": form_data.username,  # OAuth2表单使用username字段
            "password": form_data.password
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={
                "sub": response.user.id,
                "email": response.user.email
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "full_name": response.user.user_metadata.get("full_name"),
                "role": response.user.user_metadata.get("role", "user")
            }
        }
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=Token)
async def register(
    email: str,
    password: str,
    full_name: str = None,
    db: Client = Depends(get_db)
) -> Any:
    """
    用户注册
    
    创建新用户账号并返回访问令牌
    """
    try:
        # 使用Supabase创建用户
        response = db.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "role": "user"
                }
            }
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={
                "sub": response.user.id,
                "email": response.user.email
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "full_name": full_name,
                "role": "user"
            }
        }
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        if "already registered" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user"
        )


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取当前用户信息
    """
    return current_user


@router.post("/logout")
async def logout(
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    用户登出
    """
    try:
        db.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return {"message": "Logout completed"}