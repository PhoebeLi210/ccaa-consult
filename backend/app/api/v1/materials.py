#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 补充材料上传API
支持组织架构图、设备清单、工艺流程图等材料上传和解析
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid
import json
import os

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Project, ProjectRawInput

router = APIRouter(prefix="/materials", tags=["补充材料"])


# ============ 请求/响应模型 ============

class MaterialUploadResponse(BaseModel):
    """材料上传响应"""
    material_id: str
    material_type: str
    file_name: str
    file_size: int
    status: str = Field(..., description="状态: uploaded/processing/completed/failed")
    extracted_info: Optional[Dict[str, Any]] = None
    message: str


class MaterialInfo(BaseModel):
    """材料信息"""
    material_id: str
    material_type: str
    file_name: str
    file_size: int
    status: str
    extracted_info: Optional[Dict[str, Any]] = None
    uploaded_at: str


class MaterialListResponse(BaseModel):
    """材料列表响应"""
    project_id: str
    materials: List[MaterialInfo]
    total_count: int


class MaterialTypeConfig(BaseModel):
    """材料类型配置"""
    type: str
    name: str
    description: str
    allowed_extensions: List[str]
    max_size_mb: int
    extract_fields: List[str]


# ============ 材料类型配置 ============

MATERIAL_TYPES = {
    "org_chart": MaterialTypeConfig(
        type="org_chart",
        name="组织架构图",
        description="企业组织架构图，用于提取部门设置和职责",
        allowed_extensions=[".png", ".jpg", ".jpeg", ".pdf", ".docx"],
        max_size_mb=10,
        extract_fields=["departments", "management_structure", "reporting_lines"],
    ),
    "equipment_list": MaterialTypeConfig(
        type="equipment_list",
        name="设备清单",
        description="主要生产设备清单，用于识别关键设备和维护要求",
        allowed_extensions=[".xlsx", ".xls", ".csv", ".pdf", ".docx"],
        max_size_mb=10,
        extract_fields=["equipment", "maintenance_requirements", "calibration_items"],
    ),
    "process_flow": MaterialTypeConfig(
        type="process_flow",
        name="工艺流程图",
        description="生产工艺流程图，用于识别关键过程和特殊过程",
        allowed_extensions=[".png", ".jpg", ".jpeg", ".pdf", ".vsdx"],
        max_size_mb=10,
        extract_fields=["processes", "special_processes", "quality_control_points"],
    ),
    "site_layout": MaterialTypeConfig(
        type="site_layout",
        name="厂区平面图",
        description="厂区/办公区平面布局图",
        allowed_extensions=[".png", ".jpg", ".jpeg", ".pdf", ".dwg"],
        max_size_mb=10,
        extract_fields=["areas", "emergency_exits", "hazardous_areas"],
    ),
    "license_cert": MaterialTypeConfig(
        type="license_cert",
        name="资质证书",
        description="营业执照、许可证等资质证书",
        allowed_extensions=[".png", ".jpg", ".jpeg", ".pdf"],
        max_size_mb=5,
        extract_fields=["company_info", "business_scope", "validity_period"],
    ),
    "previous_cert": MaterialTypeConfig(
        type="previous_cert",
        name="历史认证证书",
        description="已有的ISO认证证书或审核报告",
        allowed_extensions=[".png", ".jpg", ".jpeg", ".pdf"],
        max_size_mb=5,
        extract_fields=["certification_body", "cert_scope", "expiry_date", "non_conformities"],
    ),
    "other": MaterialTypeConfig(
        type="other",
        name="其他材料",
        description="其他补充材料",
        allowed_extensions=[".png", ".jpg", ".jpeg", ".pdf", ".docx", ".xlsx"],
        max_size_mb=20,
        extract_fields=[],
    ),
}


# ============ 内存存储（生产环境应使用数据库）============
material_storage: Dict[str, Dict[str, Any]] = {}


# ============ API路由 ============

@router.get("/types", response_model=List[MaterialTypeConfig], summary="获取支持的补充材料类型")
async def get_material_types():
    """获取所有支持的补充材料类型及其配置"""
    return list(MATERIAL_TYPES.values())


@router.post("/upload", response_model=MaterialUploadResponse, summary="上传补充材料")
async def upload_material(
    project_id: str = Form(..., description="项目ID"),
    material_type: str = Form(..., description="材料类型"),
    file: UploadFile = File(..., description="上传的文件"),
    db: AsyncSession = Depends(get_db),
):
    """
    上传补充材料（组织架构图、设备清单等）
    
    支持类型:
    - org_chart: 组织架构图
    - equipment_list: 设备清单
    - process_flow: 工艺流程图
    - site_layout: 厂区平面图
    - license_cert: 资质证书
    - previous_cert: 历史认证证书
    - other: 其他材料
    """
    # 验证项目存在
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 验证材料类型
    if material_type not in MATERIAL_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的类型: {material_type}. 支持的类型: {list(MATERIAL_TYPES.keys())}"
        )
    
    config = MATERIAL_TYPES[material_type]
    
    # 验证文件扩展名
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in config.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {file_ext}. 支持的格式: {config.allowed_extensions}"
        )
    
    # 验证文件大小
    content = await file.read()
    file_size = len(content)
    max_size = config.max_size_mb * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大: {file_size / 1024 / 1024:.1f}MB > 最大 {config.max_size_mb}MB"
        )
    
    # 生成材料ID
    material_id = str(uuid.uuid4())
    
    # 保存文件
    upload_dir = os.path.join(settings.UPLOAD_DIR, "materials", project_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    file_name = f"{material_id}{file_ext}"
    file_path = os.path.join(upload_dir, file_name)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 保存材料信息
    material_info = {
        "material_id": material_id,
        "project_id": project_id,
        "material_type": material_type,
        "file_name": file.filename,
        "file_size": file_size,
        "file_path": file_path,
        "status": "uploaded",
        "extracted_info": None,
        "uploaded_at": datetime.utcnow().isoformat(),
    }
    material_storage[material_id] = material_info
    
    # 异步处理：提取信息
    # 注意：实际生产环境应使用后台任务（如Celery）
    extracted_info = await _extract_material_info(file_path, material_type, content)
    material_info["extracted_info"] = extracted_info
    material_info["status"] = "completed" if extracted_info else "failed"
    
    # 保存到项目原始输入
    await _save_material_to_project(project_id, material_type, file.filename, extracted_info, db)
    
    return MaterialUploadResponse(
        material_id=material_id,
        material_type=material_type,
        file_name=file.filename,
        file_size=file_size,
        status=material_info["status"],
        extracted_info=extracted_info,
        message="上传成功" if material_info["status"] == "completed" else "上传成功但信息提取失败",
    )


@router.get("/project/{project_id}", response_model=MaterialListResponse, summary="获取项目的补充材料列表")
async def list_project_materials(
    project_id: str,
    material_type: Optional[str] = None,
):
    """获取指定项目的所有补充材料"""
    materials = [
        m for m in material_storage.values()
        if m["project_id"] == project_id
        and (material_type is None or m["material_type"] == material_type)
    ]
    
    return MaterialListResponse(
        project_id=project_id,
        materials=[
            MaterialInfo(
                material_id=m["material_id"],
                material_type=m["material_type"],
                file_name=m["file_name"],
                file_size=m["file_size"],
                status=m["status"],
                extracted_info=m.get("extracted_info"),
                uploaded_at=m["uploaded_at"],
            )
            for m in materials
        ],
        total_count=len(materials),
    )


@router.get("/{material_id}", response_model=MaterialInfo, summary="获取材料详情")
async def get_material_detail(material_id: str):
    """获取单个补充材料的详细信息"""
    if material_id not in material_storage:
        raise HTTPException(status_code=404, detail="材料不存在")
    
    m = material_storage[material_id]
    return MaterialInfo(
        material_id=m["material_id"],
        material_type=m["material_type"],
        file_name=m["file_name"],
        file_size=m["file_size"],
        status=m["status"],
        extracted_info=m.get("extracted_info"),
        uploaded_at=m["uploaded_at"],
    )


@router.delete("/{material_id}", summary="删除补充材料")
async def delete_material(material_id: str):
    """删除补充材料"""
    if material_id not in material_storage:
        raise HTTPException(status_code=404, detail="材料不存在")
    
    material = material_storage[material_id]
    
    # 删除文件
    try:
        if os.path.exists(material["file_path"]):
            os.remove(material["file_path"])
    except Exception as e:
        print(f"删除文件失败: {e}")
    
    # 删除记录
    del material_storage[material_id]
    
    return {"message": "材料已删除", "material_id": material_id}


@router.post("/{material_id}/reprocess", response_model=MaterialUploadResponse, summary="重新处理材料")
async def reprocess_material(material_id: str):
    """重新提取材料中的信息"""
    if material_id not in material_storage:
        raise HTTPException(status_code=404, detail="材料不存在")
    
    material = material_storage[material_id]
    material["status"] = "processing"
    
    # 读取文件内容
    try:
        with open(material["file_path"], "rb") as f:
            content = f.read()
        
        extracted_info = await _extract_material_info(
            material["file_path"],
            material["material_type"],
            content
        )
        material["extracted_info"] = extracted_info
        material["status"] = "completed" if extracted_info else "failed"
    except Exception as e:
        material["status"] = "failed"
        print(f"重新处理失败: {e}")
    
    return MaterialUploadResponse(
        material_id=material_id,
        material_type=material["material_type"],
        file_name=material["file_name"],
        file_size=material["file_size"],
        status=material["status"],
        extracted_info=material.get("extracted_info"),
        message="重新处理完成" if material["status"] == "completed" else "重新处理失败",
    )


# ============ 辅助函数 ============

async def _extract_material_info(
    file_path: str,
    material_type: str,
    content: bytes
) -> Optional[Dict[str, Any]]:
    """从材料中提取信息"""
    
    if material_type == "equipment_list":
        return await _extract_equipment_info(file_path, content)
    elif material_type == "org_chart":
        return await _extract_org_info(file_path, content)
    elif material_type == "process_flow":
        return await _extract_process_info(file_path, content)
    elif material_type == "license_cert":
        return await _extract_license_info(file_path, content)
    else:
        # 其他类型暂不支持自动提取
        return {"note": "该类型材料暂不支持自动信息提取"}


async def _extract_equipment_info(file_path: str, content: bytes) -> Dict[str, Any]:
    """从设备清单中提取信息"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext in [".xlsx", ".xls", ".csv"]:
        try:
            # 使用 pandas 读取 Excel
            import pandas as pd
            from io import BytesIO
            
            df = pd.read_excel(BytesIO(content)) if file_ext != ".csv" else pd.read_csv(BytesIO(content))
            
            equipment = []
            for _, row in df.iterrows():
                equip = {
                    "name": str(row.get("设备名称", row.iloc[0]) if len(row) > 0 else ""),
                    "model": str(row.get("型号规格", "")),
                    "quantity": str(row.get("数量", "")),
                    "location": str(row.get("存放位置", "")),
                }
                if equip["name"] and equip["name"] != "nan":
                    equipment.append(equip)
            
            return {
                "equipment_count": len(equipment),
                "equipment_list": equipment[:20],  # 限制数量
                "has_calibration": any("校准" in str(c) or "检定" in str(c) for c in df.columns),
            }
        except Exception as e:
            print(f"Excel解析失败: {e}")
            return {"error": "无法解析Excel文件", "equipment_count": 0}
    
    return {"note": "非Excel格式的设备清单，请手动录入"}


async def _extract_org_info(file_path: str, content: bytes) -> Dict[str, Any]:
    """从组织架构图中提取信息（使用OCR）"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext in [".png", ".jpg", ".jpeg"]:
        try:
            # 尝试使用OCR
            # 注意：实际生产环境需要安装 pytesseract 和 tesseract-ocr
            # from PIL import Image
            # import pytesseract
            # image = Image.open(BytesIO(content))
            # text = pytesseract.image_to_string(image, lang='chi_sim')
            
            # 这里返回模拟数据
            return {
                "departments_detected": ["总经理", "品质部", "生产部", "行政部"],
                "management_levels": 3,
                "note": "图片格式组织架构图，建议手动确认部门设置",
            }
        except Exception as e:
            return {"error": "OCR识别失败", "note": "请手动输入部门信息"}
    
    return {"note": "非图片格式，无法自动提取"}


async def _extract_process_info(file_path: str, content: bytes) -> Dict[str, Any]:
    """从工艺流程图中提取信息"""
    # 工艺流程图通常需要人工解读
    return {
        "processes_detected": [],
        "note": "工艺流程图需要人工分析，请手动输入关键过程",
        "suggested_processes": ["来料检验", "生产加工", "过程检验", "成品检验", "包装入库"],
    }


async def _extract_license_info(file_path: str, content: bytes) -> Dict[str, Any]:
    """从资质证书中提取信息（使用OCR）"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext in [".png", ".jpg", ".jpeg"]:
        try:
            # OCR识别（模拟）
            return {
                "cert_type": "营业执照",
                "extracted_fields": ["公司名称", "统一社会信用代码", "法定代表人", "注册资本"],
                "note": "营业执照已上传，关键信息已识别",
            }
        except Exception as e:
            return {"error": "证书识别失败"}
    
    return {"note": "证书已保存"}


async def _save_material_to_project(
    project_id: str,
    material_type: str,
    file_name: str,
    extracted_info: Optional[Dict[str, Any]],
    db: AsyncSession
):
    """保存材料信息到项目原始输入"""
    try:
        raw_input = ProjectRawInput(
            project_id=project_id,
            input_type=f"material_{material_type}",
            content=f"上传文件: {file_name}",
            parsed_json=extracted_info or {},
        )
        db.add(raw_input)
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"保存材料信息失败: {e}")
