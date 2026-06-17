#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 主入口

FastAPI应用入口
"""

import time
import uuid
import traceback

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.core.logging_config import setup_logging, get_logger
from app.core.backup import create_backup, list_backups, get_backup_info, setup_auto_backup
from app.api.v1 import templates, generator, company, materials, projects, parse, auth, analyzer, uploads, conversation, custom_templates, team, flowcharts, industry, certification_scope, knowledge, speech


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时初始化日志和数据库
    setup_logging()
    logger = get_logger("main")
    logger.info("智质通·咨询版 启动中...")
    logger.info("初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")
    
    # 启动时创建一次备份
    logger.info("创建启动备份...")
    create_backup()
    
    # 启动自动备份任务
    setup_auto_backup()
    
    yield
    # 关闭时
    logger.info("智质通·咨询版 关闭中...")


app = FastAPI(
    title="智质通·咨询版 API",
    description="面向ISO咨询顾问的AI智能文书工作站",
    version="1.5.0",
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

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录HTTP请求（仅记录错误）"""
    trace_id = str(uuid.uuid4())[:8]
    
    # 处理请求
    response = await call_next(request)
    
    # 仅记录错误响应
    if response.status_code >= 400:
        access_logger = get_logger("access")
        access_logger.warning(
            f"{request.method} {request.url.path} {response.status_code}",
            extra={
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            }
        )
    
    # 添加trace_id到响应头
    response.headers["X-Trace-ID"] = trace_id
    
    return response

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
app.include_router(custom_templates.router, prefix="/api/v1")
app.include_router(team.router, prefix="/api/v1")
app.include_router(flowcharts.router, prefix="/api/v1")
app.include_router(industry.router, prefix="/api/v1")
app.include_router(certification_scope.router, prefix="/api/v1", tags=["认证范围"])
app.include_router(knowledge.router, prefix="/api/v1")
app.include_router(speech.router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "智质通·咨询版",
        "version": "1.0.0",
        "description": "面向ISO咨询顾问的AI智能文书工作站",
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
        },
        "features": [
            "JWT用户认证",
            "数据库持久化（SQLite）",
            "LLM自然语言解析（DeepSeek）",
            "AI扩写描述性内容",
            "行业模板自动匹配（7个行业）",
            "文档导出为.docx/ZIP",
            "Excel收集表上传解析",
            "ISO条款覆盖检查",
            "四层知识库架构（V1.5）",
            "事实锁定与防编造（V1.5）",
            "27个程序文件生成器（V1.5）",
            "55个记录表单生成器（V1.5）",
        ]
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


# ============ 全局异常处理 ============

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger = get_logger("main")
    logger.error(f"未捕获的异常: {exc}\n{traceback.format_exc()}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.DEBUG else "请联系管理员",
            "trace_id": request.headers.get("X-Trace-ID", "unknown"),
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "trace_id": request.headers.get("X-Trace-ID", "unknown"),
        }
    )


# ============ 备份管理API ============

@app.post("/api/v1/admin/backup", summary="手动触发数据库备份")
async def trigger_backup():
    """手动触发数据库备份"""
    backup_path = create_backup()
    if backup_path:
        return {
            "success": True,
            "message": "备份成功",
            "backup": get_backup_info(backup_path),
        }
    return {"success": False, "message": "备份失败"}


@app.get("/api/v1/admin/backups", summary="获取备份列表")
async def get_backups():
    """获取所有备份文件列表"""
    backups = list_backups()
    return {
        "total": len(backups),
        "backups": [get_backup_info(b) for b in backups],
    }


@app.get("/api/v1/admin/backup/status", summary="获取备份状态")
async def backup_status():
    """获取备份状态统计"""
    backups = list_backups()
    db_path = Path("./data/zhizhitong.db")
    
    return {
        "total_backups": len(backups),
        "max_backups": 30,
        "latest_backup": get_backup_info(backups[0]) if backups else None,
        "database_size_mb": round(db_path.stat().st_size / 1024 / 1024, 2) if db_path.exists() else 0,
        "auto_backup_enabled": True,
        "backup_interval_hours": 24,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)
