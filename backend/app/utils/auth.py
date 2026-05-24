#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 认证工具模块

提供用户认证相关的工具函数，供其他模块导入使用
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import secrets

from sqlalchemy.orm import Session

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# JWT配置（与auth.py保持一致）
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# 用户存储（与auth.py共享）
# 注意：生产环境应使用数据库
_users_db: Dict[str, Dict[str, Any]] = {}


def set_users_db(users_db: Dict[str, Dict[str, Any]]):
    """设置用户存储（由auth.py调用）"""
    global _users_db
    _users_db = users_db


def get_users_db() -> Dict[str, Dict[str, Any]]:
    """获取用户存储"""
    return _users_db


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    """
    获取当前登录用户
    
    从JWT token中解析用户信息，返回用户字典
    
    Args:
        token: JWT访问令牌
        
    Returns:
        用户信息字典
        
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    from jose import JWTError, jwt
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = _users_db.get(user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取当前活跃用户
    
    确保用户账户处于活跃状态
    
    Args:
        current_user: 当前用户
        
    Returns:
        活跃用户信息
        
    Raises:
        HTTPException: 用户被禁用时抛出400错误
    """
    if not current_user.get("is_active", False):
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


def get_user_id(current_user: Dict[str, Any]) -> str:
    """
    从用户字典中获取用户ID
    
    Args:
        current_user: 用户信息字典
        
    Returns:
        用户ID字符串
    """
    return current_user.get("id", "")


def get_username(current_user: Dict[str, Any]) -> str:
    """
    从用户字典中获取用户名
    
    Args:
        current_user: 用户信息字典
        
    Returns:
        用户名字符串
    """
    return current_user.get("username", "")
