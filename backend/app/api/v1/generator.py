#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 文档生成API接口 V3（重构版）
使用统一文档生成器，支持行业过滤
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import json

from app.modules.generator.unified_generator import (
    UnifiedDocumentGenerator,
    generate_full_package,
    get_templates_by_industry
)
from app.modules.generator.base import GeneratedDocument, FileLevel, DocumentType
from app.core.constants import TEMPLATE_DIR
from app.core.database import get_db
from app.models.models import Document as DocumentModel
from app.api.v1.generator_state import tasks

# 子路由导入
from app.api.v1.generator_export import router as export_router
from app.api.v1.generator_filelist import router as filelist_router
from app.api.v1.generator_equipment import router as equipment_router
from app.api.v1.generator_emergency import router as emergency_router

router = APIRouter(prefix="/generator", tags=["文档生成"])

# 包含子路由
router.include_router(export_router)
router.include_router(filelist_router)
router.include_router(equipment_router)
router.include_router(emergency_router)


# ============ 请求/响应模型 ============

class GenerateRequest(BaseModel):
    """文档生成请求"""
    template_id: str = Field(..., description="模板ID")
    company_info: Dict[str, Any] = Field(..., description="企业信息，应包含industry_code字段")
    additional_vars: Optional[Dict[str, Any]] = Field(None, description="额外变量")


class GenerateBatchRequest(BaseModel):
    """批量生成请求"""
    template_ids: List[str] = Field(..., description="模板ID列表")
    company_info: Dict[str, Any] = Field(..., description="企业信息，应包含industry_code字段")
    additional_vars: Optional[Dict[str, Any]] = Field(None, description="额外变量")
    project_id: Optional[str] = Field(None, description="项目ID，提供后将写入数据库")


class GenerateLevelRequest(BaseModel):
    """按层级生成请求"""
    level: str = Field(..., description="层级（一级文件/二级文件/三级文件/四级文件）")
    company_info: Dict[str, Any] = Field(..., description="企业信息，应包含industry_code字段")
    additional_vars: Optional[Dict[str, Any]] = Field(None, description="额外变量")
    project_id: Optional[str] = Field(None, description="项目ID，提供后将写入数据库")


class GenerateAllRequest(BaseModel):
    """生成全套体系文件请求"""
    company_info: Dict[str, Any] = Field(
        ...,
        description="企业信息，必须包含industry_code字段用于行业过滤"
    )
    levels: Optional[List[str]] = Field(
        None,
        description="指定层级，None表示全部层级"
    )
    additional_vars: Optional[Dict[str, Any]] = Field(None, description="额外变量")
    project_id: Optional[str] = Field(None, description="项目ID，提供后将写入数据库")


class GenerateResponse(BaseModel):
    """生成响应"""
    task_id: str
    status: str
    message: str
    documents: Optional[List[Dict[str, Any]]] = None
    summary: Optional[Dict[str, Any]] = None


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str
    progress: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============ API路由 ============

@router.post("/generate", response_model=GenerateResponse, summary="生成单个文档")
async def generate_single(request: GenerateRequest):
    """
    生成单个文档

    会根据企业信息中的industry_code自动过滤不匹配的模板
    """
    task_id = str(uuid.uuid4())

    try:
        generator = UnifiedDocumentGenerator()
        result = generator.generate_single_document(
            request.company_info,
            request.template_id
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"模板不存在或行业不匹配: {request.template_id}"
            )

        tasks[task_id] = {
            "status": "completed",
            "progress": 100,
            "result": result.to_dict(),
        }

        return GenerateResponse(
            task_id=task_id,
            status="completed",
            message="文档生成成功",
            documents=[result.to_dict()],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/generate/batch", response_model=GenerateResponse, summary="批量生成文档")
async def generate_batch(
    request: GenerateBatchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    批量生成文档

    会根据企业信息中的industry_code自动过滤不匹配的模板。
    如果提供了 project_id，生成结果会写入数据库 documents 表。
    """
    task_id = str(uuid.uuid4())

    try:
        generator = UnifiedDocumentGenerator()
        documents = generator.batch_generate(
            request.company_info,
            request.template_ids
        )

        tasks[task_id] = {
            "status": "completed",
            "progress": 100,
            "results": [doc.to_dict() for doc in documents],
        }

        # 如果提供了 project_id，将文档写入数据库
        saved_document_ids = []
        if request.project_id:
            try:
                saved_document_ids = await _save_documents_to_db(db, documents, request.project_id)
                print(f"已将 {len(saved_document_ids)} 个文档写入数据库，项目ID: {request.project_id}")
            except Exception as db_err:
                await db.rollback()
                print(f"数据库写入失败（文档已生成但未持久化）: {str(db_err)}")

        return GenerateResponse(
            task_id=task_id,
            status="completed",
            message=f"成功生成 {len(documents)} 个文档",
            documents=[doc.to_dict() for doc in documents],
            summary={
                "total": len(documents),
                "saved_to_db": len(saved_document_ids) > 0,
                "document_ids": saved_document_ids,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量生成失败: {str(e)}")


@router.post("/generate/level", response_model=GenerateResponse, summary="按层级生成")
async def generate_level(
    request: GenerateLevelRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    按层级生成所有文档（支持行业过滤）

    会根据企业信息中的industry_code只生成该行业适用的模板。
    如果提供了 project_id，生成结果会写入数据库 documents 表。
    """
    task_id = str(uuid.uuid4())

    try:
        generator = UnifiedDocumentGenerator()
        documents = generator.generate_by_level(
            request.company_info,
            request.level
        )

        tasks[task_id] = {
            "status": "completed",
            "progress": 100,
            "results": [doc.to_dict() for doc in documents],
        }

        # 如果提供了 project_id，将文档写入数据库
        saved_document_ids = []
        if request.project_id:
            try:
                saved_document_ids = await _save_documents_to_db(db, documents, request.project_id)
                print(f"已将 {len(saved_document_ids)} 个文档写入数据库，项目ID: {request.project_id}")
            except Exception as db_err:
                await db.rollback()
                print(f"数据库写入失败（文档已生成但未持久化）: {str(db_err)}")

        return GenerateResponse(
            task_id=task_id,
            status="completed",
            message=f"成功生成 {len(documents)} 个文档",
            documents=[doc.to_dict() for doc in documents],
            summary={
                "total": len(documents),
                "saved_to_db": len(saved_document_ids) > 0,
                "document_ids": saved_document_ids,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"层级生成失败: {str(e)}")


@router.post("/generate/all", response_model=GenerateResponse, summary="生成全套体系文件")
async def generate_all_documents(
    request: GenerateAllRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    根据企业信息生成全套体系文件（支持行业过滤）

    会根据company_info中的industry_code字段，只生成该行业适用的模板：
    - 通用模板（无industry标记）：所有行业都生成
    - 行业特定模板：只生成匹配该行业的模板

    如果提供了 project_id，生成结果会写入数据库 documents 表。

    例如：
    - 选择"软件开发"行业 → 只生成软件开发相关的模板
    - 选择"物业服务"行业 → 只生成物业服务相关的模板
    """
    task_id = str(uuid.uuid4())

    try:
        # 获取企业行业代码
        industry_code = request.company_info.get("industry_code") or request.company_info.get("industry", "")

        if not industry_code:
            print("警告: 企业信息未包含industry_code，将只生成通用模板")
        else:
            print(f"企业行业: {industry_code}，将按行业过滤模板")

        # 使用统一生成器生成文档
        generator = UnifiedDocumentGenerator()
        documents = generator.generate_all_documents(
            request.company_info,
            request.levels
        )

        # 按层级分组
        results_by_level = {
            "一级文件": [],
            "二级文件": [],
            "三级文件": [],
            "四级文件": [],
        }

        for doc in documents:
            level_name = _get_level_name(doc.file_level)
            if level_name in results_by_level:
                results_by_level[level_name].append(doc.to_dict())

        tasks[task_id] = {
            "status": "completed",
            "progress": 100,
            "results": results_by_level,
        }

        # 如果提供了 project_id，将文档写入数据库
        saved_document_ids = []
        if request.project_id:
            try:
                saved_document_ids = await _save_documents_to_db(db, documents, request.project_id)
                print(f"已将 {len(saved_document_ids)} 个文档写入数据库，项目ID: {request.project_id}")
            except Exception as db_err:
                await db.rollback()
                print(f"数据库写入失败（文档已生成但未持久化）: {str(db_err)}")
                # 不中断流程，仍然返回生成结果

        response = GenerateResponse(
            task_id=task_id,
            status="completed",
            message=f"成功生成 {len(documents)} 个文档",
            documents=[doc.to_dict() for doc in documents],
            summary={
                "total": len(documents),
                "by_level": {k: len(v) for k, v in results_by_level.items()},
                "industry_code": industry_code,
                "saved_to_db": len(saved_document_ids) > 0,
                "document_ids": saved_document_ids,
            },
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"全套生成失败: {str(e)}")


@router.get("/task/{task_id}", response_model=TaskStatusResponse, summary="查询任务状态")
async def get_task_status(task_id: str):
    """查询任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        result=task.get("result") or task.get("results"),
        error=task.get("error"),
    )


@router.get("/levels", summary="获取支持的层级")
async def get_levels():
    """获取支持的文档层级及模板数量"""
    levels = []

    if TEMPLATE_DIR.exists():
        for level_dir in TEMPLATE_DIR.iterdir():
            if level_dir.is_dir():
                count = len(list(level_dir.glob("*.yaml")))
                levels.append({
                    "name": level_dir.name,
                    "template_count": count,
                })

    return {"levels": levels}


@router.get("/templates/available", summary="获取可用的模板列表")
async def get_available_templates(
    industry_code: Optional[str] = None,
    level: Optional[str] = None
):
    """
    获取可用的模板列表（支持行业过滤）

    Args:
        industry_code: 行业代码，用于过滤该行业适用的模板
        level: 层级过滤（一级文件/二级文件/三级文件/四级文件）

    Returns:
        模板信息列表
    """
    try:
        templates = get_templates_by_industry(industry_code, level)
        return {
            "industry_code": industry_code,
            "level": level,
            "total": len(templates),
            "templates": templates,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板列表失败: {str(e)}")


# ============ 辅助函数 ============

def _get_level_name(file_level) -> str:
    """获取层级名称"""
    from app.modules.generator.base import FileLevel

    name_map = {
        FileLevel.LEVEL_1: "一级文件",
        FileLevel.LEVEL_2: "二级文件",
        FileLevel.LEVEL_3: "三级文件",
        FileLevel.LEVEL_4: "四级文件",
    }
    return name_map.get(file_level, "四级文件")


async def _save_documents_to_db(
    db: AsyncSession,
    documents: List[GeneratedDocument],
    project_id: str
) -> List[str]:
    """
    将生成的文档列表写入数据库 documents 表

    Args:
        db: 数据库会话
        documents: GeneratedDocument 对象列表
        project_id: 项目ID

    Returns:
        写入的 document_id 列表
    """
    document_ids = []
    for doc in documents:
        doc_id = str(uuid.uuid4())
        content_json = json.dumps(doc.to_dict(), ensure_ascii=False)

        db_doc = DocumentModel(
            document_id=doc_id,
            project_id=project_id,
            doc_type=doc.document_type.value,
            title=doc.title,
            file_name=doc.file_name,
            ai_content=content_json,
            current_content=content_json,
            confirmed=False,
        )
        db.add(db_doc)
        document_ids.append(doc_id)

    await db.commit()
    return document_ids
