#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 企业信息API接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

router = APIRouter(prefix="/company", tags=["企业管理"])

# 企业信息存储（实际应用中应使用数据库）
companies = {}


class CompanyInfo(BaseModel):
    """企业信息模型"""
    company_id: Optional[str] = None
    company_name: str
    company_name_en: Optional[str] = None
    unified_credit_code: Optional[str] = None
    legal_representative: Optional[str] = None
    registered_capital: Optional[str] = None
    establishment_date: Optional[str] = None
    business_scope: Optional[str] = None
    address: Optional[str] = None
    office_address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    
    # 规模信息
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    employee_count: Optional[int] = None
    office_area_sqm: Optional[float] = None
    
    # 认证信息
    target_standards: Optional[List[str]] = None
    existing_standards: Optional[List[str]] = None
    
    # 体系信息
    quality_policy: Optional[str] = None
    quality_goals: Optional[List[str]] = None
    environment_policy: Optional[str] = None
    safety_policy: Optional[str] = None
    
    # 组织信息
    departments: Optional[List[Dict[str, Any]]] = None
    positions: Optional[List[Dict[str, Any]]] = None


class CompanyCreateRequest(BaseModel):
    """创建企业请求"""
    company_name: str
    industry: Optional[str] = None
    **kwargs: Any


class CompanyUpdateRequest(BaseModel):
    """更新企业请求"""
    **kwargs: Any


@router.post("/", summary="创建企业")
async def create_company(request: CompanyCreateRequest):
    """创建企业信息"""
    company_id = str(uuid.uuid4())
    
    company_data = request.dict()
    company_data["company_id"] = company_id
    company_data["created_at"] = datetime.now().isoformat()
    
    companies[company_id] = company_data
    
    return {
        "company_id": company_id,
        "message": "企业创建成功",
        "data": company_data,
    }


@router.get("/{company_id}", summary="获取企业信息")
async def get_company(company_id: str):
    """获取企业信息"""
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="企业不存在")
    
    return companies[company_id]


@router.put("/{company_id}", summary="更新企业信息")
async def update_company(company_id: str, request: CompanyUpdateRequest):
    """更新企业信息"""
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="企业不存在")
    
    companies[company_id].update(request.dict(exclude_unset=True))
    companies[company_id]["updated_at"] = datetime.now().isoformat()
    
    return {
        "company_id": company_id,
        "message": "企业信息更新成功",
        "data": companies[company_id],
    }


@router.delete("/{company_id}", summary="删除企业")
async def delete_company(company_id: str):
    """删除企业"""
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="企业不存在")
    
    del companies[company_id]
    
    return {"message": "企业删除成功"}


@router.get("/", summary="获取企业列表")
async def list_companies():
    """获取企业列表"""
    return {
        "total": len(companies),
        "companies": list(companies.values()),
    }


@router.post("/{company_id}/analyze", summary="分析企业信息")
async def analyze_company(company_id: str):
    """分析企业信息，确定所需文档"""
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="企业不存在")
    
    company = companies[company_id]
    
    # 根据企业信息分析所需文档
    required_docs = {
        "一级文件": ["管理手册"],
        "二级文件": [],
        "三级文件": [],
        "四级文件": [],
    }
    
    # 根据目标标准确定所需程序文件
    standards = company.get("target_standards", [])
    
    if "ISO9001" in standards or "INTEGRATED" in standards:
        required_docs["二级文件"].extend([
            "文件控制程序",
            "记录控制程序",
            "内部审核程序",
            "管理评审程序",
            "不合格控制程序",
            "纠正措施程序",
        ])
    
    if "ISO14001" in standards or "INTEGRATED" in standards:
        required_docs["二级文件"].extend([
            "环境因素识别程序",
            "法律法规获取程序",
            "应急准备和响应程序",
        ])
    
    if "ISO45001" in standards or "INTEGRATED" in standards:
        required_docs["二级文件"].extend([
            "危险源辨识程序",
            "事故调查程序",
        ])
    
    return {
        "company_id": company_id,
        "analysis": {
            "industry": company.get("industry"),
            "standards": standards,
            "employee_count": company.get("employee_count"),
        },
        "required_documents": required_docs,
    }
