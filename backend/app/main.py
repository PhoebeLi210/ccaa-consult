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
from app.core.database import init_db
from app.api.v1 import templates, generator, company, materials, projects, parse, auth, analyzer, uploads, conversation, flowcharts, cert_stage, old_files


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时初始化数据库
    print("智质通·咨询版 启动中...")
    print("初始化数据库...")
    init_db()
    print("数据库初始化完成")
    yield
    # 关闭时
    print("智质通·咨询版 关闭中...")


app = FastAPI(
    title="智质通·咨询版 API",
    description="面向ISO认证咨询的AI智能文书工作端",
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
app.include_router(templates.router, prefix="/api/v1")
app.include_router(generator.router, prefix="/api/v1")
app.include_router(company.router, prefix="/api/v1")
app.include_router(materials.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(parse.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(analyzer.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1")
app.include_router(conversation.router, prefix="/api/v1")
app.include_router(flowcharts.router, prefix="/api/v1")
app.include_router(cert_stage.router, prefix="/api/v1")
app.include_router(old_files.router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "智质通·咨询版",
        "version": "1.0.0",
        "description": "面向ISO认证咨询的AI智能文书工作端",
        "endpoints": {
            "auth": "/api/v1/auth - 用户认证（注册/登录）",
            "projects": "/api/v1/projects - 项目管理",
            "generator": "/api/v1/generator - 文档生成与导出",
            "templates": "/api/v1/templates - 模板管理",
            "materials": "/api/v1/materials - 材料管理",
            "parse": "/api/v1/parse - 自然语言解析",
            "analyzer": "/api/v1/analyzer - 缺失项分析",
            "uploads": "/api/v1/uploads - 文件上传与Excel解析",
            "company": "/api/v1/company - 企业管理",
            "cert_stage": "/api/v1/cert-stage - 认证阶段确认",
            "old_files": "/api/v1/old-files - 旧版文件上传和提取",
        },
        "features": [
            "JWT用户认证",
            "数据库持久化（SQLite）",
            "LLM自然语言解析（DeepSeek）",
            "AI扩充描述性内容",
            "行业模板自动匹配（5行业）",
            "文档导出为docx/ZIP",
            "Excel收集表上传解析",
            "ISO条款覆盖检查",
        ]
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
