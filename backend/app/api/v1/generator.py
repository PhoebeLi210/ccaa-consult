#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 文档生成API接口 V3（重构版）
使用统一文档生成器，支持行业过滤
支持导出为.docx文件和ZIP包下载
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
import uuid
import io
import json

# 导入重构后的统一生成器
from app.modules.generator.unified_generator import (
    UnifiedDocumentGenerator,
    generate_full_package,
    get_templates_by_industry
)
from app.modules.generator.base import GeneratedDocument, FileLevel, DocumentType
from app.modules.generator.docx_exporter import DocxExporter, DocumentPackager
from app.core.constants import TEMPLATE_DIR
from app.core.database import get_db
from app.models.models import Document as DocumentModel

router = APIRouter(prefix="/generator", tags=["文档生成"])


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


class TemplateInfoResponse(BaseModel):
    """模板信息响应"""
    id: str
    name: str
    code: str
    level: int
    industry: Optional[str] = None
    version: str
    standard: Optional[str] = None


# ============ 任务存储 ============

tasks = {}


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
    db: Session = Depends(get_db)
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
                saved_document_ids = _save_documents_to_db(db, documents, request.project_id)
                print(f"已将 {len(saved_document_ids)} 个文档写入数据库，项目ID: {request.project_id}")
            except Exception as db_err:
                db.rollback()
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
    db: Session = Depends(get_db)
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
                saved_document_ids = _save_documents_to_db(db, documents, request.project_id)
                print(f"已将 {len(saved_document_ids)} 个文档写入数据库，项目ID: {request.project_id}")
            except Exception as db_err:
                db.rollback()
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
    db: Session = Depends(get_db)
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
                saved_document_ids = _save_documents_to_db(db, documents, request.project_id)
                print(f"已将 {len(saved_document_ids)} 个文档写入数据库，项目ID: {request.project_id}")
            except Exception as db_err:
                db.rollback()
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


def _save_documents_to_db(
    db: Session, 
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
    
    db.commit()
    return document_ids


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


# ============ 文件下载API ============

class ExportRequest(BaseModel):
    """导出请求"""
    company_name: str = Field(..., description="公司名称")
    company_info: Dict[str, Any] = Field(None, description="企业信息（仅当project_id未提供时用于重新生成）")
    levels: Optional[List[str]] = Field(None, description="指定层级")
    project_id: Optional[str] = Field(None, description="项目ID，提供后从数据库读取已确认文档导出")
    force_export: bool = Field(False, description="强制导出（跳过确认检查）")


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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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


from fastapi import Body

# 导入设备操作规程生成器
from app.modules.generator.level3.dynamic_equipment_generator import (
    generate_equipment_operations,
    get_equipment_categories,
    EQUIPMENT_NAME_MAP,
)
from app.modules.generator.base import CompanyInfo


# ============ 设备操作规程生成API ============

class EquipmentOperationRequest(BaseModel):
    """设备操作规程生成请求"""
    company_info: Dict[str, Any] = Field(..., description="企业信息")
    equipment_list: List[Dict[str, Any]] = Field(..., description="设备列表，每个设备包含name, model, quantity等字段")
    include_summary: bool = Field(True, description="是否生成目录总册")


class EquipmentCategoryResponse(BaseModel):
    """设备分类响应"""
    code: str
    name: str
    equipments: List[str]


@router.post("/equipment-operations", response_model=GenerateResponse, summary="生成设备操作规程")
async def generate_equipment_operations_api(
    request: EquipmentOperationRequest,
    db: Session = Depends(get_db)
):
    """
    根据设备清单动态生成设备操作规程
    
    支持设备：
    - 办公设备：电脑、空调、打印机、复印机、投影仪、碎纸机、饮水机
    - 安全设备：消防器材、急救设备、监控设备
    - 生产设备：电焊机、切割机、行车/起重机、叉车
    - 其他设备：使用通用模板生成
    
    每个设备生成一个独立的操作规程文档（三级文件）。
    """
    task_id = str(uuid.uuid4())
    
    try:
        # 将字典转换为CompanyInfo对象
        company_info_obj = CompanyInfo(
            company_name=request.company_info.get("company_name", ""),
            company_code=request.company_info.get("company_code", request.company_info.get("company_abbr", "")),
            industry=request.company_info.get("industry", ""),
            sub_industry=request.company_info.get("sub_industry", ""),
            employee_count=request.company_info.get("employee_count", 0),
            office_area_sqm=request.company_info.get("office_area_sqm", 0),
            certification_type=request.company_info.get("certification_type", "初次认证"),
            existing_standards=request.company_info.get("existing_standards", []),
            target_standards=request.company_info.get("target_standards", ["ISO9001", "ISO14001", "ISO45001"]),
            departments=request.company_info.get("departments", []),
            main_equipment=[eq.get("name", "") for eq in request.equipment_list],
            main_processes=request.company_info.get("main_processes", []),
            special_processes=request.company_info.get("special_processes", []),
            quality_goals=request.company_info.get("quality_goals", ""),
            environment_goals=request.company_info.get("environment_goals", ""),
            safety_goals=request.company_info.get("safety_goals", ""),
            address=request.company_info.get("address", ""),
            legal_representative=request.company_info.get("legal_representative", ""),
            contact_person=request.company_info.get("contact_person", ""),
            contact_phone=request.company_info.get("contact_phone", ""),
            management_representative=request.company_info.get("management_representative", ""),
            file_version=request.company_info.get("file_version", "A/0"),
            effective_date=request.company_info.get("effective_date", ""),
            release_date=request.company_info.get("release_date", ""),
        )
        
        # 生成设备操作规程
        documents = generate_equipment_operations(
            company_info_obj,
            request.equipment_list,
            include_summary=request.include_summary
        )
        
        tasks[task_id] = {
            "status": "completed",
            "progress": 100,
            "results": [doc.to_dict() for doc in documents],
        }
        
        return GenerateResponse(
            task_id=task_id,
            status="completed",
            message=f"成功生成 {len(documents)} 个设备操作规程",
            documents=[doc.to_dict() for doc in documents],
            summary={
                "total": len(documents),
                "equipment_count": len(request.equipment_list),
                "include_summary": request.include_summary,
            },
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设备操作规程生成失败: {str(e)}")


@router.get("/equipment-categories", response_model=List[EquipmentCategoryResponse], summary="获取设备分类列表")
async def get_equipment_categories_api():
    """
    获取支持的设备分类列表
    
    返回所有预定义的设备分类，供前端选择使用。
    """
    categories = get_equipment_categories()
    return categories


@router.post("/equipment-operations/preview", summary="预览单个设备操作规程")
async def preview_equipment_operation(
    company_info: Dict[str, Any] = Body(...),
    equipment: Dict[str, Any] = Body(...),
):
    """
    预览单个设备的操作规程
    
    Args:
        company_info: 企业信息
        equipment: 设备信息 {"name": "设备名称", "model": "型号", "quantity": 1}
    """
    try:
        # 转换为CompanyInfo对象
        company_info_obj = CompanyInfo(
            company_name=company_info.get("company_name", ""),
            company_code=company_info.get("company_code", company_info.get("company_abbr", "")),
        )
        
        # 生成单个设备操作规程
        from app.modules.generator.level3.dynamic_equipment_generator import (
            DynamicEquipmentOperationGenerator
        )
        generator = DynamicEquipmentOperationGenerator(company_info_obj, [equipment])
        documents = generator.generate()
        
        if not documents:
            raise HTTPException(status_code=404, detail="无法生成该设备的操作规程")
        
        doc = documents[0]
        
        # 导出为字节流
        exporter = DocxExporter("./output")
        doc_bytes = exporter.export_to_bytes(doc)
        
        filename = doc.file_name
        
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
