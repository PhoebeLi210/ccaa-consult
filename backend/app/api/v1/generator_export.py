#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 文档导出API接口
支持导出为.docx文件和ZIP包下载
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import io
import json

from app.modules.generator.unified_generator import UnifiedDocumentGenerator
from app.modules.generator.base import GeneratedDocument, FileLevel, DocumentType
from app.modules.generator.docx_exporter import DocxExporter, DocumentPackager
from app.core.database import get_db
from app.models.models import Document as DocumentModel
from app.api.v1.generator_state import tasks

router = APIRouter()


class ExportRequest(BaseModel):
    """导出请求"""
    company_name: str = Field(..., description="公司名称")
    company_info: Dict[str, Any] = Field(None, description="企业信息（仅当project_id未提供时用于重新生成）")
    levels: Optional[List[str]] = Field(None, description="指定层级")
    project_id: Optional[str] = Field(None, description="项目ID，提供后从数据库读取已确认文档导出")
    force_export: bool = Field(False, description="强制导出（跳过确认检查）")


def _dict_to_generated_document(data: Dict[str, Any]) -> GeneratedDocument:
    """
    将字典反序列化为 GeneratedDocument 对象

    Args:
        data: 文档字典（来自 to_dict() 或数据库 current_content）

    Returns:
        GeneratedDocument 对象
    """
    return GeneratedDocument(
        file_level=FileLevel(data["file_level"]),
        document_type=DocumentType(data["document_type"]),
        file_code=data["file_code"],
        file_name=data["file_name"],
        title=data["title"],
        content=data["content"],
        standards=data.get("standards", []),
        related_clauses=data.get("related_clauses", []),
        required_records=data.get("required_records", []),
        created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
    )


@router.post("/export/docx/{task_id}", summary="下载单个文档")
async def download_single_docx(task_id: str, document_index: int = 0):
    """
    下载单个生成的文档为.docx格式

    Args:
        task_id: 任务ID
        document_index: 文档索引（默认第一个）
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")

    results = task.get("results", [])
    if not results or document_index >= len(results):
        raise HTTPException(status_code=404, detail="文档不存在")

    # 这里需要重新生成文档以获取字节流
    # 实际应用中应该缓存生成的文档
    raise HTTPException(status_code=501, detail="请使用 /export/zip 接口下载完整文档包")


@router.post("/export/zip", summary="生成并下载全套文档ZIP包")
async def export_and_download_zip(
    request: ExportRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    导出全套体系文件并打包为ZIP下载

    优先从数据库读取已确认/编辑后的文档：
    - 如果提供了 project_id，从数据库 documents 表读取该项目的文档
    - 优先使用已确认（confirmed=True）的文档
    - 未确认的文档使用 current_content（可能包含用户编辑）
    - 如果存在未确认文档，会在响应头中附加警告信息

    向后兼容：
    - 如果未提供 project_id，则使用旧的重新生成方式

    Args:
        request: 导出请求，包含企业信息和层级选择

    Returns:
        ZIP文件流
    """
    try:
        documents: List[GeneratedDocument] = []
        warnings = []

        if request.project_id:
            # ===== 从数据库读取文档 =====
            db_docs = db.query(DocumentModel).filter(
                DocumentModel.project_id == request.project_id
            ).all()

            if not db_docs:
                raise HTTPException(
                    status_code=404,
                    detail=f"项目 {request.project_id} 下没有找到任何文档，请先调用 /generate/all 生成文档"
                )

            # 检查确认状态
            total_count = len(db_docs)
            confirmed_count = sum(1 for d in db_docs if d.confirmed)
            unconfirmed_count = total_count - confirmed_count

            if unconfirmed_count > 0 and not request.force_export:
                # 获取未确认文档的列表
                unconfirmed_docs = [
                    {"document_id": d.document_id, "title": d.title, "doc_type": d.doc_type}
                    for d in db_docs if not d.confirmed
                ]
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": f"有 {unconfirmed_count} 个文档尚未确认，无法导出正式版本",
                        "total_documents": total_count,
                        "confirmed_documents": confirmed_count,
                        "unconfirmed_documents": unconfirmed_count,
                        "unconfirmed_list": unconfirmed_docs,
                        "hint": "请先确认所有文档，或设置 force_export=true 强制导出草稿版本"
                    }
                )

            if unconfirmed_count > 0 and request.force_export:
                warnings.append(f"强制导出模式：有 {unconfirmed_count}/{total_count} 个文档尚未确认，导出内容可能不完整")

            # 反序列化文档
            for db_doc in db_docs:
                try:
                    content_data = json.loads(db_doc.current_content) if db_doc.current_content else {}
                    gen_doc = _dict_to_generated_document(content_data)
                    documents.append(gen_doc)
                except (json.JSONDecodeError, KeyError, ValueError) as parse_err:
                    warnings.append(f"文档 {db_doc.document_id} ({db_doc.title}) 反序列化失败: {str(parse_err)}，已跳过")
                    print(f"文档反序列化失败: document_id={db_doc.document_id}, error={parse_err}")

            if not documents:
                raise HTTPException(
                    status_code=500,
                    detail="所有文档反序列化失败，无法导出"
                )

            print(f"从数据库读取了 {len(documents)} 个文档（项目ID: {request.project_id}）")

        else:
            # ===== 向后兼容：重新生成文档 =====
            if not request.company_info:
                raise HTTPException(
                    status_code=400,
                    detail="未提供 project_id 时，必须提供 company_info 以重新生成文档"
                )

            industry_code = request.company_info.get("industry_code") or request.company_info.get("industry", "")
            generator = UnifiedDocumentGenerator()
            documents = generator.generate_all_documents(
                request.company_info,
                request.levels
            )

            if not documents:
                raise HTTPException(status_code=404, detail="没有生成任何文档")

        # 使用 DocumentPackager 打包为 ZIP
        packager = DocumentPackager("./output")
        zip_bytes = packager.create_package_bytes(documents)

        # 生成文件名
        company_name = request.company_name or "企业"
        filename = f"{company_name}_体系文件_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

        # 构建响应头
        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
        }
        if warnings:
            headers["X-Export-Warnings"] = "; ".join(warnings)

        # 返回文件流
        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers=headers
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/export/single/{document_id}", summary="导出单个文档为.docx")
async def export_single_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    从数据库读取单个文档并导出为 .docx 文件下载

    Args:
        document_id: 文档ID（UUID）

    Returns:
        .docx 文件流
    """
    try:
        # 从数据库查询文档
        db_doc = db.query(DocumentModel).filter(
            DocumentModel.document_id == document_id
        ).first()

        if not db_doc:
            raise HTTPException(status_code=404, detail=f"文档不存在: {document_id}")

        # 反序列化为 GeneratedDocument
        try:
            content_data = json.loads(db_doc.current_content) if db_doc.current_content else {}
            gen_doc = _dict_to_generated_document(content_data)
        except (json.JSONDecodeError, KeyError, ValueError) as parse_err:
            raise HTTPException(
                status_code=500,
                detail=f"文档数据反序列化失败: {str(parse_err)}"
            )

        # 使用 DocxExporter 导出为字节流
        exporter = DocxExporter("./output")
        doc_bytes = exporter.export_to_bytes(gen_doc)

        # 确定文件名
        filename = db_doc.file_name or f"{db_doc.title}.docx"
        if not filename.endswith(".docx"):
            filename = f"{filename}.docx"

        return StreamingResponse(
            io.BytesIO(doc_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"单文档导出失败: {str(e)}")


@router.post("/export/preview/{template_id}", summary="预览单个文档")
async def preview_document(
    template_id: str,
    company_info: Dict[str, Any] = Body(...)
):
    """
    预览单个文档（返回.docx字节流）

    Args:
        template_id: 模板ID
        company_info: 企业信息
    """
    try:
        generator = UnifiedDocumentGenerator()
        doc = generator.generate_single_document(company_info, template_id)

        if not doc:
            raise HTTPException(status_code=404, detail=f"模板不存在: {template_id}")

        # 获取文档字节流
        doc_bytes = generator.get_docx_bytes(doc)

        filename = f"{doc.file_name}"

        return StreamingResponse(
            io.BytesIO(doc_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}")
