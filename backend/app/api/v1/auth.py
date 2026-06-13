#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 用户认证API
使用JWT进行用户认证，数据持久化到数据库
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User, UserStatus

router = APIRouter(prefix="/auth", tags=["用户认证"])

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# JWT配置（从settings读取，确保重启后不变）
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_HOURS = settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS


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


# ============ 数据库用户操作 ============

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """通过用户名获取用户"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """通过用户ID获取用户"""
    result = await db.execute(select(User).where(User.user_id == user_id))
    return result.scalar_one_or_none()


async def create_user_db(db: AsyncSession, user_data: dict) -> User:
    """在数据库中创建用户"""
    db_user = User(
        user_id=user_data["id"],
        username=user_data["username"],
        email=user_data.get("email"),
        hashed_password=user_data["hashed_password"],
        full_name=user_data.get("full_name"),
        company=user_data.get("company"),
        is_active=True,
        status=UserStatus.ACTIVE.value,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# ============ 用户依赖 ============

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户（从数据库）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception
    
    user = await get_user_by_id(db, token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


def user_to_response(user: User) -> UserResponse:
    """将User模型转换为UserResponse"""
    return UserResponse(
        id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        is_active=user.is_active,
        created_at=user.created_at,
    )


# ============ API路由 ============

@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    注册新用户
    
    - username: 用户名（3-50字符）
    - password: 密码（6-100字符）
    - email: 邮箱（可选）
    - full_name: 全名（可选）
    - company: 公司（可选）
    """
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
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
    }
    
    db_user = await create_user_db(db, user_data)
    
    return user_to_response(db_user)


@router.post("/login", response_model=Token, summary="用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    用户登录
    
    使用OAuth2密码模式：
    - username: 用户名
    - password: 密码
    """
    # 查找用户
    user = await get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # 创建令牌
    access_token = create_access_token(
        data={"sub": user.user_id, "username": user.username}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        user=user_to_response(user),
    )


@router.post("/login/json", response_model=Token, summary="JSON格式登录")
async def login_json(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    JSON格式登录（用于前端API调用）
    
    - username: 用户名
    - password: 密码
    """
    # 查找用户
    user = await get_user_by_username(db, credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # 创建令牌
    access_token = create_access_token(
        data={"sub": user.user_id, "username": user.username}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        user=user_to_response(user),
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_active_user)):
    """获取当前登录用户的信息"""
    return user_to_response(current_user)


@router.put("/me", response_model=UserResponse, summary="更新用户信息")
async def update_me(
    full_name: Optional[str] = None,
    company: Optional[str] = None,
    email: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息"""
    if full_name is not None:
        current_user.full_name = full_name
    if company is not None:
        current_user.company = company
    if email is not None:
        current_user.email = email
    
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    
    return user_to_response(current_user)


@router.post("/logout", summary="用户登出")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    用户登出
    
    注意：JWT是无状态的，服务端不维护会话。
    客户端需要删除本地存储的token。
    """
    return {"message": "登出成功", "username": current_user.username}


@router.post("/change-password", summary="修改密码")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    current_user.hashed_password = get_password_hash(new_password)
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "密码修改成功"}


# ============ 管理接口 ============

@router.get("/users", summary="获取用户列表（管理员）")
async def list_users(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    total = (await db.execute(select(func.count()).select_from(User))).scalar()
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    
    return {
        "total": total,
        "users": [user_to_response(u) for u in users]
    }
