#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行业配置API - V2.1

提供行业配置的查询和管理接口。
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import IndustryConfig, IndustrySpecialFile


router = APIRouter(prefix="/industry", tags=["行业配置"])


# ==================== Pydantic模型 ====================

class IndustrySpecialFileResponse(BaseModel):
    id: int
    file_level: str
    file_code: str
    file_name: str
    description: Optional[str]
    category: Optional[str]
    iso_clause: Optional[str]
    sort_order: int

    class Config:
        from_attributes = True


class IndustryConfigResponse(BaseModel):
    id: int
    industry_code: str
    industry_name: str
    description: Optional[str]
    has_design_development: bool
    has_equipment_operations: bool
    has_multi_projects: bool
    has_outsourcing: bool
    internal_audit_by_dept: bool
    emergency_plans: List[str]
    required_licenses: List[str]
    certification_scope_classes: List[str]
    is_active: bool
    special_files: List[IndustrySpecialFileResponse] = []

    class Config:
        from_attributes = True


class IndustryListResponse(BaseModel):
    id: int
    industry_code: str
    industry_name: str
    description: Optional[str]
    has_design_development: bool
    has_equipment_operations: bool
    special_file_count: int

    class Config:
        from_attributes = True


class IndustryFileListRequest(BaseModel):
    industry_codes: List[str]
    file_levels: Optional[List[str]] = None  # ["B", "C", "D"]


class IndustryFileListResponse(BaseModel):
    industry_code: str
    industry_name: str
    files: List[IndustrySpecialFileResponse]


# ==================== API接口 ====================

@router.get("/list", response_model=List[IndustryListResponse])
async def list_industries(
    db: AsyncSession = Depends(get_db),
    active_only: bool = Query(True, description="仅显示启用的行业")
):
    """获取行业列表
    
    Returns:
        行业列表，包含每个行业的特有文件数量
    """
    query = select(IndustryConfig)
    if active_only:
        query = query.where(IndustryConfig.is_active == True)
    
    result = await db.execute(query.order_by(IndustryConfig.industry_code))
    industries = result.scalars().all()
    
    result_list = []
    for industry in industries:
        count_result = await db.execute(
            select(func.count()).select_from(IndustrySpecialFile).where(
                IndustrySpecialFile.industry_id == industry.id
            )
        )
        file_count = count_result.scalar()
        
        result_list.append({
            "id": industry.id,
            "industry_code": industry.industry_code,
            "industry_name": industry.industry_name,
            "description": industry.description,
            "has_design_development": industry.has_design_development,
            "has_equipment_operations": industry.has_equipment_operations,
            "special_file_count": file_count,
        })
    
    return result_list


@router.get("/{industry_code}", response_model=IndustryConfigResponse)
async def get_industry(
    industry_code: str,
    db: AsyncSession = Depends(get_db)
):
    """获取行业详情
    
    Args:
        industry_code: 行业代码，如 "property_management"
    
    Returns:
        行业详情，包含所有特有文件
    """
    result = await db.execute(select(IndustryConfig).where(
        IndustryConfig.industry_code == industry_code
    ))
    industry = result.scalar_one_or_none()
    
    if not industry:
        raise HTTPException(status_code=404, detail=f"行业不存在: {industry_code}")
    
    # 获取特有文件
    result = await db.execute(
        select(IndustrySpecialFile).where(
            IndustrySpecialFile.industry_id == industry.id
        ).order_by(IndustrySpecialFile.sort_order)
    )
    special_files = result.scalars().all()
    
    result = industry.to_dict()
    result["special_files"] = [f.to_dict() for f in special_files]
    
    return result


@router.post("/files", response_model=List[IndustryFileListResponse])
async def get_industry_files(
    request: IndustryFileListRequest,
    db: AsyncSession = Depends(get_db)
):
    """获取多个行业的文件清单
    
    用于双主营业务场景，合并两个行业的特有文件。
    
    Args:
        request: 包含行业代码列表和可选的文件层级过滤
    
    Returns:
        每个行业的文件列表
    """
    result = []
    
    for code in request.industry_codes:
        result = await db.execute(select(IndustryConfig).where(
            IndustryConfig.industry_code == code
        ))
        industry = result.scalar_one_or_none()
        
        if not industry:
            continue
        
        query = select(IndustrySpecialFile).where(
            IndustrySpecialFile.industry_id == industry.id
        )
        
        # 按层级过滤
        if request.file_levels:
            query = query.where(
                IndustrySpecialFile.file_level.in_(request.file_levels)
            )
        
        result = await db.execute(query.order_by(IndustrySpecialFile.sort_order))
        files = result.scalars().all()
        
        result.append({
            "industry_code": industry.industry_code,
            "industry_name": industry.industry_name,
            "files": [f.to_dict() for f in files],
        })
    
    return result


@router.get("/{industry_code}/check-features")
async def check_industry_features(
    industry_code: str,
    db: AsyncSession = Depends(get_db)
):
    """检查行业特征
    
    返回行业特征标志，用于前端动态显示表单字段。
    
    Args:
        industry_code: 行业代码
    
    Returns:
        行业特征对象
    """
    result = await db.execute(select(IndustryConfig).where(
        IndustryConfig.industry_code == industry_code
    ))
    industry = result.scalar_one_or_none()
    
    if not industry:
        raise HTTPException(status_code=404, detail=f"行业不存在: {industry_code}")
    
    return {
        "industry_code": industry.industry_code,
        "industry_name": industry.industry_name,
        "features": {
            "has_design_development": industry.has_design_development,
            "has_equipment_operations": industry.has_equipment_operations,
            "has_multi_projects": industry.has_multi_projects,
            "has_outsourcing": industry.has_outsourcing,
            "internal_audit_by_dept": industry.internal_audit_by_dept,
        },
        "emergency_plans": industry.emergency_plans or [],
        "required_licenses": industry.required_licenses or [],
    }


@router.post("/init")
async def init_industry_data(db: AsyncSession = Depends(get_db)):
    """初始化行业数据
    
    从 init_industries.py 加载11个行业配置到数据库。
    仅管理员使用，已有数据不会重复创建。
    
    Returns:
        创建的行业数量
    """
    from app.core.init_industries import init_industries
    
    try:
        count = await init_industries(db)
        return {
            "success": True,
            "created_count": count,
            "message": f"成功创建 {count} 个行业配置",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"初始化失败: {str(e)}")


@router.get("/{industry_code}/emergency-plans")
async def get_emergency_plans(
    industry_code: str,
    db: AsyncSession = Depends(get_db)
):
    """获取行业应急预案列表
    
    Args:
        industry_code: 行业代码
    
    Returns:
        应急预案类型列表
    """
    result = await db.execute(select(IndustryConfig).where(
        IndustryConfig.industry_code == industry_code
    ))
    industry = result.scalar_one_or_none()
    
    if not industry:
        raise HTTPException(status_code=404, detail=f"行业不存在: {industry_code}")
    
    return {
        "industry_code": industry.industry_code,
        "industry_name": industry.industry_name,
        "emergency_plans": industry.emergency_plans or [],
    }


@router.get("/{industry_code}/required-licenses")
async def get_required_licenses(
    industry_code: str,
    db: AsyncSession = Depends(get_db)
):
    """获取行业所需资质许可
    
    Args:
        industry_code: 行业代码
    
    Returns:
        所需资质许可列表
    """
    result = await db.execute(select(IndustryConfig).where(
        IndustryConfig.industry_code == industry_code
    ))
    industry = result.scalar_one_or_none()
    
    if not industry:
        raise HTTPException(status_code=404, detail=f"行业不存在: {industry_code}")
    
    return {
        "industry_code": industry.industry_code,
        "industry_name": industry.industry_name,
        "required_licenses": industry.required_licenses or [],
    }
