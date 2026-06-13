#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 文件上传API
支持Excel收集表上传解析
"""

import os
import json
import uuid
import shutil
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from sqlalchemy import select, func

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Project, Upload
from app.modules.parser.excel_parser import parse_excel_file, get_excel_template_fields

router = APIRouter(prefix="/uploads", tags=["文件上传"])


# 确保上传目录存在
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/{project_id}", summary="上传文件")
async def upload_file(
    project_id: str,
    file: UploadFile = File(...),
    parse_excel: bool = Query(True, description="是否自动解析Excel文件"),
    db: AsyncSession = Depends(get_db)
):
    """
    上传文件到项目
    
    支持的文件类型: .xlsx, .xls, .csv, .docx, .pdf, .jpg, .png
    
    如果是Excel文件且parse_excel=True，会自动解析提取企业信息
    """
    # 验证项目存在
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 验证文件类型
    allowed_extensions = {".xlsx", ".xls", ".csv", ".docx", ".doc", ".pdf", ".jpg", ".jpeg", ".png"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_ext}，支持: {', '.join(allowed_extensions)}"
        )
    
    # 验证文件大小
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制: {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB"
        )
    
    # 保存文件
    upload_id = str(uuid.uuid4())
    project_dir = UPLOAD_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = project_dir / f"{upload_id}{file_ext}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 确定文件类型
    file_type_map = {
        ".xlsx": "excel", ".xls": "excel", ".csv": "excel",
        ".docx": "word", ".doc": "word",
        ".pdf": "pdf",
        ".jpg": "image", ".jpeg": "image", ".png": "image",
    }
    file_type = file_type_map.get(file_ext, "other")
    
    # 创建上传记录
    upload = Upload(
        upload_id=upload_id,
        project_id=project_id,
        file_name=file.filename,
        file_url=str(file_path),
        file_type=file_type,
        file_size=len(content),
        parse_status="pending",
    )
    
    # 尝试解析Excel
    parse_result = None
    if parse_excel and file_type == "excel":
        try:
            parse_result = parse_excel_file(str(file_path))
            upload.parse_status = "success"
            upload.parse_result = json.dumps(parse_result, ensure_ascii=False) if parse_result else None
            
            # 如果解析成功，更新项目信息
            if parse_result:
                _update_project_from_parse(project, parse_result, db)
        except Exception as e:
            upload.parse_status = "failed"
            upload.parse_error = str(e)
    
    db.add(upload)
    await db.commit()
    await db.refresh(upload)
    
    response = upload.to_dict()
    response["parsed_info"] = parse_result
    
    return response


@router.get("/{project_id}", summary="获取上传文件列表")
async def list_uploads(
    project_id: str,
    file_type: Optional[str] = Query(None, description="按类型过滤"),
    db: AsyncSession = Depends(get_db)
):
    """获取项目的上传文件列表"""
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    query = select(Upload).where(Upload.project_id == project_id)
    if file_type:
        query = query.where(Upload.file_type == file_type)
    
    result = await db.execute(query.order_by(Upload.created_at.desc()))
    uploads = result.scalars().all()
    
    return [u.to_dict() for u in uploads]


@router.get("/{project_id}/{upload_id}", summary="获取上传文件详情")
async def get_upload(project_id: str, upload_id: str, db: AsyncSession = Depends(get_db)):
    """获取上传文件详情（含解析结果）"""
    result = await db.execute(select(Upload).where(
        Upload.upload_id == upload_id,
        Upload.project_id == project_id
    ))
    upload = result.scalar_one_or_none()
    
    if not upload:
        raise HTTPException(status_code=404, detail="文件记录不存在")
    
    result = upload.to_dict()
    
    # 如果有解析结果，转为字典
    if upload.parse_result:
        try:
            result["parsed_info"] = json.loads(upload.parse_result)
        except (json.JSONDecodeError, TypeError):
            result["parsed_info"] = upload.parse_result
    
    return result


@router.get("/{project_id}/{upload_id}/download", summary="下载上传的文件")
async def download_file(project_id: str, upload_id: str, db: AsyncSession = Depends(get_db)):
    """下载已上传的文件"""
    result = await db.execute(select(Upload).where(
        Upload.upload_id == upload_id,
        Upload.project_id == project_id
    ))
    upload = result.scalar_one_or_none()
    
    if not upload:
        raise HTTPException(status_code=404, detail="文件记录不存在")
    
    file_path = Path(upload.file_url)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=str(file_path),
        filename=upload.file_name,
        media_type="application/octet-stream"
    )


@router.delete("/{project_id}/{upload_id}", summary="删除上传文件")
async def delete_upload(project_id: str, upload_id: str, db: AsyncSession = Depends(get_db)):
    """删除上传文件及其记录"""
    result = await db.execute(select(Upload).where(
        Upload.upload_id == upload_id,
        Upload.project_id == project_id
    ))
    upload = result.scalar_one_or_none()
    
    if not upload:
        raise HTTPException(status_code=404, detail="文件记录不存在")
    
    # 删除物理文件
    file_path = Path(upload.file_url)
    if file_path.exists():
        file_path.unlink()
    
    await db.delete(upload)
    await db.commit()
    
    return {"message": "文件已删除", "upload_id": upload_id}


@router.get("/template/fields", summary="获取Excel收集表支持的字段")
async def get_template_fields():
    """获取Excel收集表支持的字段列表"""
    return {
        "fields": get_excel_template_fields(),
        "description": "Excel收集表第一列应包含以上字段名，第二列填写对应值"
    }


def _update_project_from_parse(project: Project, parsed: dict, db: AsyncSession):
    """用Excel解析结果更新项目信息"""
    update_map = {
        "company_name": "company_name",
        "industry": "industry",
        "employee_count": "employee_count",
        "address": "address",
        "legal_representative": "legal_representative",
        "contact_person": "contact_person",
        "contact_phone": "contact_phone",
    }
    
    for excel_field, project_field in update_map.items():
        if excel_field in parsed and parsed[excel_field]:
            setattr(project, project_field, parsed[excel_field])
    
    # 处理行业代码
    if parsed.get("industry"):
        from app.api.v1.parse import get_industry_code
        project.industry = get_industry_code(parsed["industry"])
    
    # 处理目标标准
    if parsed.get("target_standards"):
        project.target_standards = parsed["target_standards"]
    
    # 处理部门
    if parsed.get("departments"):
        project.departments = parsed["departments"]
    
    # 处理设备
    if parsed.get("main_equipment"):
        if not project.config:
            project.config = {}
        project.config["main_equipment"] = parsed["main_equipment"]
    
    # 处理主要过程
    if parsed.get("main_processes"):
        if not project.config:
            project.config = {}
        project.config["main_processes"] = parsed["main_processes"]
    
    project.updated_at = __import__("datetime").datetime.utcnow()
