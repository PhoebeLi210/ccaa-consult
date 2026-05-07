#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 主入口

FastAPI应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1 import projects, documents, uploads


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时
    print("智质通·咨询版 启动中...")
    yield
    # 关闭时
    print("智质通·咨询版 关闭中...")


app = FastAPI(
    title="智质通·咨询版 API",
    description="面向ISO咨询顾问的AI智能文书工作站",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(projects.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "智质通·咨询版",
        "version": "1.0.0",
        "description": "面向ISO咨询顾问的AI智能文书工作站",
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
