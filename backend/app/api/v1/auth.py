#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 用户认证API
使用JWT进行用户认证
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import secrets
import hashlib

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["用户认证"])

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# JWT配置
SECRET_KEY = secrets.token_urlsafe(32)  # 生产环境应从配置读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


# ============ 数据模型 ============

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    """用户注册模型"""
    password: str = Field(..., min_length=6, max_length=100)
    full_name: Optional[str] = None
    company: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class UserResponse(UserBase):
    """用户响应模型"""
    id: str
    full_name: Optional[str]
    company: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Token数据"""
    user_id: Optional[str] = None
    username: Optional[str] = None


# ============ 模拟用户存储（生产环境应使用数据库） ============

# 简单的用户存储（内存）
users_db = {}


# ============ 密码工具 ============

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


# ============ JWT工具 ============

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """解码令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        if user_id is None:
            return None
        return TokenData(user_id=user_id, username=username)
    except JWTError:
        return None


# ============ 用户依赖 ============

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> dict:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception
    
    user = users_db.get(token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """获取当前活跃用户"""
    if not current_user.get("is_active", False):
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


# ============ API路由 ============

@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(user: UserCreate):
    """
    注册新用户
    
    - username: 用户名（3-50字符）
    - password: 密码（6-100字符）
    - email: 邮箱（可选）
    - full_name: 全名（可选）
    - company: 公司（可选）
    """
    # 检查用户名是否已存在
    for u in users_db.values():
        if u["username"] == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被注册"
            )
    
    # 创建用户
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    
    user_data = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "company": user.company,
        "hashed_password": hashed_password,
        "is_active": True,
        "created_at": datetime.utcnow(),
    }
    
    users_db[user_id] = user_data
    
    return UserResponse(
        id=user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        is_active=True,
        created_at=user_data["created_at"],
    )


@router.post("/login", response_model=Token, summary="用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录
    
    使用OAuth2密码模式：
    - username: 用户名
    - password: 密码
    """
    # 查找用户
    user = None
    for u in users_db.values():
        if u["username"] == form_data.username:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建令牌
    access_token = create_access_token(
        data={"sub": user["id"], "username": user["username"]}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        user=UserResponse(
            id=user["id"],
            username=user["username"],
            email=user.get("email"),
            full_name=user.get("full_name"),
            company=user.get("company"),
            is_active=user["is_active"],
            created_at=user["created_at"],
        )
    )


@router.post("/login/json", response_model=Token, summary="JSON格式登录")
async def login_json(credentials: UserLogin):
    """
    JSON格式登录（用于前端API调用）
    
    - username: 用户名
    - password: 密码
    """
    # 查找用户
    user = None
    for u in users_db.values():
        if u["username"] == credentials.username:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建令牌
    access_token = create_access_token(
        data={"sub": user["id"], "username": user["username"]}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        user=UserResponse(
            id=user["id"],
            username=user["username"],
            email=user.get("email"),
            full_name=user.get("full_name"),
            company=user.get("company"),
            is_active=user["is_active"],
            created_at=user["created_at"],
        )
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_me(current_user: dict = Depends(get_current_active_user)):
    """获取当前登录用户的信息"""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user.get("email"),
        full_name=current_user.get("full_name"),
        company=current_user.get("company"),
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
    )


@router.put("/me", response_model=UserResponse, summary="更新用户信息")
async def update_me(
    full_name: Optional[str] = None,
    company: Optional[str] = None,
    email: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """更新当前用户信息"""
    user_id = current_user["id"]
    
    if full_name is not None:
        users_db[user_id]["full_name"] = full_name
    if company is not None:
        users_db[user_id]["company"] = company
    if email is not None:
        users_db[user_id]["email"] = email
    
    updated_user = users_db[user_id]
    
    return UserResponse(
        id=updated_user["id"],
        username=updated_user["username"],
        email=updated_user.get("email"),
        full_name=updated_user.get("full_name"),
        company=updated_user.get("company"),
        is_active=updated_user["is_active"],
        created_at=updated_user["created_at"],
    )


@router.post("/logout", summary="用户登出")
async def logout(current_user: dict = Depends(get_current_active_user)):
    """
    用户登出
    
    注意：JWT是无状态的，服务端不维护会话。
    客户端需要删除本地存储的token。
    """
    return {"message": "登出成功", "username": current_user["username"]}


@router.post("/change-password", summary="修改密码")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_active_user)
):
    """修改密码"""
    user_id = current_user["id"]
    
    # 验证旧密码
    if not verify_password(old_password, current_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    users_db[user_id]["hashed_password"] = get_password_hash(new_password)
    
    return {"message": "密码修改成功"}


# ============ 管理接口 ============

@router.get("/users", summary="获取用户列表（管理员）")
async def list_users(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_active_user)
):
    """获取用户列表（需要管理员权限）"""
    # 简单实现：所有用户都可以查看
    users = list(users_db.values())[skip:skip+limit]
    
    return {
        "total": len(users_db),
        "users": [
            UserResponse(
                id=u["id"],
                username=u["username"],
                email=u.get("email"),
                full_name=u.get("full_name"),
                company=u.get("company"),
                is_active=u["is_active"],
                created_at=u["created_at"],
            )
            for u in users
        ]
    }
