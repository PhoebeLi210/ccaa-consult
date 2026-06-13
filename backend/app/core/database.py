#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 异步数据库配置
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


async def init_db():
    """初始化数据库"""
    from app.models.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)