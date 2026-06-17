#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 项目管理API接口
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import uuid
import io
import json

from sqlalchemy import select, func, cast, Integer, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from app.core.database import get_db
from app.models.models import Project, Document, Upload, ProjectRawInput, ProjectStatus
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["项目管理"])


# ============ 请求/响应模型 ============

class ProjectCreateRequest(BaseModel):
    user_id: str = Field(default="default_user", description="用户ID")
    company_name: Optional[str] = Field(None, description="公司名称")
    industry: Optional[str] = Field(None, description="行业")
    industry_code: Optional[str] = Field(None, description="行业代码")
    employee_count: Optional[int] = Field(None, description="员工人数")
    office_area_sqm: Optional[float] = Field(None, description="办公面积")
    certification_type: Optional[str] = Field("初次认证", description="认证类型")
    target_standards: Optional[List[str]] = Field(None, description="目标标准")
    departments: Optional[List[str]] = Field(None, description="部门列表")
    address: Optional[str] = Field(None, description="地址")
    legal_representative: Optional[str] = Field(None, description="法定代表人")
    contact_person: Optional[str] = Field(None, description="联系人")
    contact_phone: Optional[str] = Field(None, description="联系电话")


class ProjectUpdateRequest(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    industry_code: Optional[str] = None
    employee_count: Optional[int] = None
    office_area_sqm: Optional[float] = None
    certification_type: Optional[str] = None
    target_standards: Optional[List[str]] = None
    departments: Optional[List[str]] = None
    main_equipment: Optional[List[str]] = None
    main_processes: Optional[List[str]] = None
    quality_goals: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    project_id: str
    user_id: str
    company_name: Optional[str]
    industry: Optional[str]
    employee_count: Optional[int]
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]


class DocumentCreateRequest(BaseModel):
    doc_type: str = Field(..., description="文档类型")
    title: str = Field(..., description="文档标题")
    file_name: Optional[str] = Field(None, description="文件名")
    content: Optional[str] = Field(None, description="文档内容")


class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    confirmed: Optional[bool] = None


class BatchConfirmRequest(BaseModel):
    document_ids: List[str]


# ============ 项目API ============

@router.post("/", response_model=ProjectResponse, summary="创建项目")
async def create_project(request: ProjectCreateRequest, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    user_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.get("id")
    project_id = str(uuid.uuid4())
    project = Project(
        project_id=project_id,
        user_id=user_id,
        company_name=request.company_name,
        industry=request.industry_code or request.industry,
        employee_count=request.employee_count,
        office_area_sqm=request.office_area_sqm,
        certification_type=request.certification_type,
        target_standards=request.target_standards,
        departments=request.departments,
        status=ProjectStatus.DRAFT.value,
        config={
            "industry_code": request.industry_code,
            "address": request.address,
            "legal_representative": request.legal_representative,
            "contact_person": request.contact_person,
            "contact_phone": request.contact_phone,
        }
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectResponse(
        id=project.id,
        project_id=project.project_id,
        user_id=project.user_id,
        company_name=project.company_name,
        industry=project.industry,
        employee_count=project.employee_count,
        status=project.status,
        created_at=project.created_at.isoformat() if project.created_at else None,
        updated_at=project.updated_at.isoformat() if project.updated_at else None,
    )


@router.get("/", summary="获取项目列表")
async def list_projects(
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.get("id")
    is_admin = getattr(current_user, 'is_superuser', False)

    stmt = select(Project)
    if not is_admin:
        stmt = stmt.where(Project.user_id == user_id)
    if status:
        stmt = stmt.where(Project.status == status)
    if keyword:
        stmt = stmt.where(Project.company_name.contains(keyword))
    result = await db.execute(stmt.order_by(Project.updated_at.desc()).offset(skip).limit(limit))
    return [p.to_dict() for p in result.scalars().all()]


@router.get("/{project_id}", summary="获取项目详情")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    user_id = current_user.user_id if hasattr(current_user, 'user_id') else current_user.get("id")
    is_admin = getattr(current_user, 'is_superuser', False)

    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    if not is_admin and project.user_id != user_id:
        raise HTTPException(status_code=404, detail="项目不存在")
    result_dict = project.to_dict()
    doc_count = (await db.execute(select(func.count()).select_from(Document).where(Document.project_id == project_id))).scalar()
    upload_count = (await db.execute(select(func.count()).select_from(Upload).where(Upload.project_id == project_id))).scalar()
    result_dict["document_count"] = doc_count
    result_dict["upload_count"] = upload_count
    return result_dict


@router.put("/{project_id}", summary="更新项目")
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    update_data = request.dict(exclude_unset=True)
    if "industry_code" in update_data:
        if not project.config:
            project.config = {}
        project.config["industry_code"] = update_data.pop("industry_code")
        flag_modified(project, "config")
    for key, value in update_data.items():
        if hasattr(project, key):
            setattr(project, key, value)
    project.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(project)
    return project.to_dict()


@router.delete("/{project_id}", summary="删除项目")
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    await db.delete(project)
    await db.commit()
    return {"message": "项目已删除", "project_id": project_id}


# ============ 文档API ============

@router.post("/{project_id}/documents", summary="创建文档")
async def create_document(
    project_id: str,
    request: DocumentCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    document = Document(
        document_id=str(uuid.uuid4()),
        project_id=project_id,
        doc_type=request.doc_type,
        title=request.title,
        file_name=request.file_name,
        ai_content=request.content,
        current_content=request.content,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document.to_dict()


@router.get("/{project_id}/documents", summary="获取项目文档列表")
async def list_documents(
    project_id: str,
    doc_type: Optional[str] = Query(None),
    confirmed: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    stmt = select(Document).where(Document.project_id == project_id)
    if doc_type:
        stmt = stmt.where(Document.doc_type == doc_type)
    if confirmed is not None:
        stmt = stmt.where(Document.confirmed == confirmed)
    docs = await db.execute(stmt.order_by(Document.created_at))
    return [d.to_dict() for d in docs.scalars().all()]


@router.get("/{project_id}/documents/{document_id}", summary="获取文档详情")
async def get_document(
    project_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(
        Document.document_id == document_id,
        Document.project_id == project_id
    ))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document.to_dict()


@router.put("/{project_id}/documents/{document_id}", summary="更新文档")
async def update_document(
    project_id: str,
    document_id: str,
    request: DocumentUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(
        Document.document_id == document_id,
        Document.project_id == project_id
    ))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    if request.title is not None:
        document.title = request.title
    if request.content is not None:
        document.human_content = request.content
        document.current_content = request.content
    if request.confirmed is not None:
        document.confirmed = request.confirmed
        if request.confirmed:
            document.confirmed_at = datetime.utcnow()
    document.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(document)
    return document.to_dict()


@router.post("/{project_id}/documents/{document_id}/confirm", summary="确认文档")
async def confirm_document(
    project_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(
        Document.document_id == document_id,
        Document.project_id == project_id
    ))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    document.confirmed = True
    document.confirmed_at = datetime.utcnow()
    document.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(document)
    return document.to_dict()


@router.post("/{project_id}/documents/batch-confirm", summary="批量确认文档")
async def batch_confirm_documents(
    project_id: str,
    request: BatchConfirmRequest,
    db: AsyncSession = Depends(get_db)
):
    stmt = sql_update(Document).where(
        Document.document_id.in_(request.document_ids),
        Document.project_id == project_id
    ).values(confirmed=True, confirmed_at=datetime.utcnow())
    result = await db.execute(stmt)
    await db.commit()
    return {"message": f"已确认 {result.rowcount} 个文档", "count": result.rowcount}


# ============ 上传文件API ============

@router.post("/{project_id}/uploads", summary="上传文件记录")
async def create_upload(
    project_id: str,
    file_name: str,
    file_url: str,
    file_type: Optional[str] = None,
    file_size: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    upload = Upload(
        upload_id=str(uuid.uuid4()),
        project_id=project_id,
        file_name=file_name,
        file_url=file_url,
        file_type=file_type,
        file_size=file_size,
    )
    db.add(upload)
    await db.commit()
    await db.refresh(upload)
    return upload.to_dict()


@router.get("/{project_id}/uploads", summary="获取上传文件列表")
async def list_uploads(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    uploads = await db.execute(
        select(Upload).where(Upload.project_id == project_id).order_by(Upload.created_at.desc())
    )
    return {"total": len(uploads.scalars().all()), "uploads": [u.to_dict() for u in uploads.scalars().all()]}


@router.delete("/{project_id}/uploads/{upload_id}", summary="删除上传文件")
async def delete_upload(
    project_id: str,
    upload_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Upload).where(
        Upload.upload_id == upload_id,
        Upload.project_id == project_id
    ))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="文件记录不存在")
    await db.delete(upload)
    await db.commit()
    return {"message": "文件记录已删除", "upload_id": upload_id}


# ============ 项目状态管理 ============

@router.post("/{project_id}/status", summary="更新项目状态")
async def update_project_status(
    project_id: str,
    status: str,
    db: AsyncSession = Depends(get_db)
):
    valid_statuses = [s.value for s in ProjectStatus]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"无效的状态，有效值: {valid_statuses}")
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    project.status = status
    project.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "状态已更新", "project_id": project_id, "status": status}


@router.get("/{project_id}/confirmation-status", summary="获取项目文档确认状态")
async def get_confirmation_status(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    total = (await db.execute(
        select(func.count()).select_from(Document).where(Document.project_id == project_id)
    )).scalar()
    confirmed = (await db.execute(
        select(func.count()).select_from(Document).where(
            Document.project_id == project_id, Document.confirmed == True
        )
    )).scalar()
    return {
        "project_id": project_id,
        "total_documents": total,
        "confirmed_documents": confirmed,
        "unconfirmed_documents": total - confirmed,
        "all_confirmed": total > 0 and confirmed == total,
        "progress_percent": round(confirmed / total * 100, 1) if total > 0 else 0,
    }