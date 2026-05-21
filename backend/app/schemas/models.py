#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 集中Pydantic数据模型
将分散在各API文件中的请求/响应模型统一管理
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================
# 通用响应模型
# ============================================================

class APIResponse(BaseModel):
    """通用API响应"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None


class PagedResponse(BaseModel):
    """分页响应"""
    total: int
    items: List[Any]
    page: int = 1
    page_size: int = 20


# ============================================================
# 用户认证模型
# ============================================================

class UserCreate(BaseModel):
    """用户注册"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    email: Optional[str] = None
    full_name: Optional[str] = None
    company: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class UserOut(BaseModel):
    """用户信息输出"""
    id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    company: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


class Token(BaseModel):
    """JWT Token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


# ============================================================
# 项目管理模型
# ============================================================

class ProjectCreate(BaseModel):
    """创建项目"""
    user_id: str = "default_user"
    company_name: Optional[str] = None
    industry: Optional[str] = None
    industry_code: Optional[str] = None
    employee_count: Optional[int] = None
    office_area_sqm: Optional[float] = None
    certification_type: Optional[str] = "初次认证"
    target_standards: Optional[List[str]] = None
    departments: Optional[List[str]] = None
    address: Optional[str] = None
    legal_representative: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None


class ProjectUpdate(BaseModel):
    """更新项目"""
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
    legal_representative: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    status: Optional[str] = None


class ProjectOut(BaseModel):
    """项目输出"""
    id: int
    project_id: str
    user_id: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    status: str = "draft"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ============================================================
# 文档管理模型
# ============================================================

class DocumentCreate(BaseModel):
    """创建文档"""
    doc_type: str
    title: str
    file_name: Optional[str] = None
    content: Optional[str] = None


class DocumentUpdate(BaseModel):
    """更新文档"""
    title: Optional[str] = None
    content: Optional[str] = None
    confirmed: Optional[bool] = None


class DocumentOut(BaseModel):
    """文档输出"""
    document_id: str
    project_id: str
    doc_type: str
    title: str
    file_name: Optional[str] = None
    confirmed: bool = False
    created_at: Optional[str] = None


# ============================================================
# 自然语言解析模型
# ============================================================

class ParseRequest(BaseModel):
    """解析请求"""
    text: str = Field(..., description="用户输入的自然语言文本")
    use_llm: bool = Field(True, description="是否使用LLM解析")


class ParsedCompanyInfo(BaseModel):
    """解析出的企业信息"""
    company_name: Optional[str] = None
    industry: Optional[str] = None
    industry_code: Optional[str] = None
    employee_count: Optional[int] = None
    office_area: Optional[float] = None
    address: Optional[str] = None
    legal_representative: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    main_business: Optional[str] = None
    target_standards: Optional[List[str]] = None
    certification_type: Optional[str] = None


class ParseResponse(BaseModel):
    """解析响应"""
    success: bool
    parsed_info: ParsedCompanyInfo
    raw_text: str
    confidence: float = 0.0
    missing_fields: List[str] = []


# ============================================================
# 文档生成模型
# ============================================================

class GenerateRequest(BaseModel):
    """生成请求"""
    company_info: Dict[str, Any]
    template_id: Optional[str] = None
    levels: Optional[List[str]] = None
    standards: Optional[List[str]] = None


class ExportRequest(BaseModel):
    """导出请求"""
    company_name: str
    company_info: Dict[str, Any]
    levels: Optional[List[str]] = None


# ============================================================
# 缺失项分析模型
# ============================================================

class AnalyzeRequest(BaseModel):
    """缺失项分析请求"""
    project_id: str
    standards: Optional[List[str]] = Field(
        default=["ISO9001"],
        description="要检查的标准列表"
    )


class ClauseCoverage(BaseModel):
    """条款覆盖情况"""
    clause_number: str
    clause_title: str
    status: str  # covered / partial / missing
    matched_documents: List[str] = []


class AnalyzeResponse(BaseModel):
    """分析响应"""
    project_id: str
    standards: List[str]
    summary: Dict[str, Any]
    clauses: List[ClauseCoverage]
    suggestions: List[str]


# ============================================================
# 文件上传模型
# ============================================================

class UploadResponse(BaseModel):
    """上传响应"""
    upload_id: str
    project_id: str
    file_name: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    file_url: Optional[str] = None
    parse_status: Optional[str] = None
    created_at: Optional[str] = None
