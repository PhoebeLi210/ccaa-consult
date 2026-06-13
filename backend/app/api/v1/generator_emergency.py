#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 应急预案生成API接口
根据预案类型列表动态生成应急预案
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.modules.generator.base import CompanyInfo
from app.core.database import get_db
from app.api.v1.generator_state import tasks

router = APIRouter()


class EmergencyPlanRequest(BaseModel):
    """应急预案生成请求"""
    company_info: Dict[str, Any] = Field(..., description="企业信息")
    plan_types: List[str] = Field(..., description="预案类型列表，如['火灾', '触电', '高处坠落']")
    include_summary: bool = Field(True, description="是否生成目录总册")


class EmergencyPlanCategoryResponse(BaseModel):
    """预案分类响应"""
    code: str
    name: str
    plans: List[str]


class GenerateResponse(BaseModel):
    """生成响应"""
    task_id: str
    status: str
    message: str
    documents: Optional[List[Dict[str, Any]]] = None
    summary: Optional[Dict[str, Any]] = None


@router.post("/emergency-plans", response_model=GenerateResponse, summary="生成应急预案")
async def generate_emergency_plans_api(
    request: EmergencyPlanRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    根据预案类型列表动态生成应急预案

    支持预案类型：
    - 消防类：火灾
    - 用电安全类：触电
    - 高空作业类：高处坠落、高空坠落
    - 建筑安全类：坍塌
    - 机械安全类：机械伤害、设备伤害
    - 物体打击类：物体打击
    - 食品安全类：食品安全事故
    - 信息安全类：信息安全事件
    - 交通安全类：交通意外
    - 健康安全类：中暑
    - 人身安全类：身体伤害

    每个预案生成一个独立的应急预案文档（三级文件）。
    """
    task_id = str(uuid.uuid4())

    try:
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
            main_equipment=request.company_info.get("main_equipment", []),
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

        from app.modules.generator.level3.dynamic_emergency_plan_generator import (
            generate_emergency_plans,
        )

        documents = generate_emergency_plans(
            company_info_obj,
            request.plan_types,
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
            message=f"成功生成 {len(documents)} 个应急预案",
            documents=[doc.to_dict() for doc in documents],
            summary={
                "total": len(documents),
                "plan_count": len(request.plan_types),
                "include_summary": request.include_summary,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"应急预案生成失败: {str(e)}")


@router.get("/emergency-plan-categories", response_model=List[EmergencyPlanCategoryResponse], summary="获取预案分类列表")
async def get_emergency_plan_categories_api():
    """
    获取支持的应急预案分类列表

    返回所有预定义的预案分类，供前端选择使用。
    """
    from app.modules.generator.level3.dynamic_emergency_plan_generator import (
        get_emergency_plan_categories,
    )
    categories = get_emergency_plan_categories()
    return categories
