"""
认证和授权管理
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.core.config import settings
from app.core.database import get_db
from supabase import Client
from loguru import logger


# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


class Token(BaseModel):
    """Token模型"""
    access_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]


class TokenData(BaseModel):
    """Token数据模型"""
    user_id: Optional[str] = None
    email: Optional[str] = None


class User(BaseModel):
    """用户模型"""
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    role: str = "user"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Client = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenData(user_id=user_id, email=email)
        
    except JWTError:
        raise credentials_exception
    
    # 从Supabase获取用户信息
    try:
        response = db.auth.admin.get_user_by_id(token_data.user_id)
        if not response.user:
            raise credentials_exception
            
        user = User(
            id=response.user.id,
            email=response.user.email,
            full_name=response.user.user_metadata.get("full_name"),
            is_active=not response.user.banned,
            is_superuser=response.user.user_metadata.get("is_superuser", False),
            created_at=response.user.created_at,
            role=response.user.user_metadata.get("role", "user")
        )
        
        return user
        
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """获取当前超级用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges"
        )
    return current_user


class RoleChecker:
    """角色检查器"""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="The user doesn't have enough privileges"
            )
        return user


# 预定义的角色检查器
require_admin = RoleChecker(["admin", "superuser"])
require_engineer = RoleChecker(["admin", "superuser", "engineer"])
require_viewer = RoleChecker(["admin", "superuser", "engineer", "viewer"])