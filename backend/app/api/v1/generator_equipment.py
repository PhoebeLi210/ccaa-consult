#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 设备操作规程生成API接口
根据设备清单动态生成设备操作规程
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import io

from app.modules.generator.docx_exporter import DocxExporter
from app.modules.generator.level3.dynamic_equipment_generator import (
    generate_equipment_operations,
    get_equipment_categories,
    EQUIPMENT_NAME_MAP,
)
from app.modules.generator.base import CompanyInfo, GeneratedDocument
from app.core.database import get_db
from app.api.v1.generator_state import tasks

router = APIRouter()


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


class GenerateResponse(BaseModel):
    """生成响应"""
    task_id: str
    status: str
    message: str
    documents: Optional[List[Dict[str, Any]]] = None
    summary: Optional[Dict[str, Any]] = None


@router.post("/equipment-operations", response_model=GenerateResponse, summary="生成设备操作规程")
async def generate_equipment_operations_api(
    request: EquipmentOperationRequest,
    db: AsyncSession = Depends(get_db)
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
