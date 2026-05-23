#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISO标准知识库API

提供ISO标准条款的查询、搜索、格式化等功能
支持的标准：ISO9001:2015、ISO14001:2015、ISO45001:2018
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query

from app.core.iso_standards_kb import get_knowledge_base, ISOStandardsKnowledgeBase

router = APIRouter(prefix="/iso-standards", tags=["ISO标准知识库"])


# 响应模型
class StandardInfo(BaseModel):
    """标准信息"""
    name: str
    title: str
    description: str
    clause_count: int


class ClauseInfo(BaseModel):
    """条款信息"""
    clause: str
    title: str
    content: str
    key_points: List[str] = []
    implementation_guidance: Optional[str] = None


class StandardDetail(BaseModel):
    """标准详情"""
    name: str
    title: str
    description: str
    clauses: List[ClauseInfo]


class StandardsListResponse(BaseModel):
    """标准列表响应"""
    standards: List[StandardInfo]
    total: int
    version: str
    last_updated: str


class ClausesBatchRequest(BaseModel):
    """批量获取条款请求"""
    clause_numbers: List[str] = Field(..., description="条款号列表，如 [\"4.1\", \"5.1\"]")
    standards: Optional[List[str]] = Field(None, description="标准代码列表，如 [\"ISO9001:2015\"]")


class ClausesBatchResponse(BaseModel):
    """批量获取条款响应"""
    results: Dict[str, List[ClauseInfo]]
    total_found: int


class SearchResponse(BaseModel):
    """搜索响应"""
    keyword: str
    results: Dict[str, List[ClauseInfo]]
    total_found: int


class FormatForPromptRequest(BaseModel):
    """格式化为Prompt请求"""
    clause_numbers: List[str] = Field(..., description="条款号列表")
    standards: Optional[List[str]] = Field(None, description="标准代码列表")
    include_guidance: bool = Field(True, description="是否包含实施指导")


class FormatForPromptResponse(BaseModel):
    """格式化为Prompt响应"""
    prompt_text: str
    clause_count: int


class ImplementationGuidanceResponse(BaseModel):
    """实施指导响应"""
    standard: str
    guidance: Dict[str, str]


# 获取知识库实例
def get_kb() -> ISOStandardsKnowledgeBase:
    """获取ISO标准知识库实例"""
    return get_knowledge_base()


@router.get("", response_model=StandardsListResponse)
async def get_all_standards():
    """
    获取所有可用标准列表
    
    返回系统中支持的所有ISO标准及其基本信息
    """
    kb = get_kb()
    stats = kb.get_statistics()
    
    standards = []
    for std_code, std_info in stats.get("standards", {}).items():
        standards.append(StandardInfo(
            name=std_code,
            title=std_info.get("title", ""),
            description=kb.get_standard_info(std_code).get("description", "") if kb.get_standard_info(std_code) else "",
            clause_count=std_info.get("clause_count", 0)
        ))
    
    return StandardsListResponse(
        standards=standards,
        total=len(standards),
        version=stats.get("version", "unknown"),
        last_updated=stats.get("last_updated", "unknown")
    )


@router.get("/{standard}", response_model=StandardDetail)
async def get_standard_clauses(standard: str):
    """
    获取指定标准的所有条款
    
    Args:
        standard: 标准代码，如 ISO9001:2015
    
    Returns:
        标准的所有条款详情
    """
    kb = get_kb()
    
    if standard not in kb.standards:
        raise HTTPException(status_code=404, detail=f"标准 '{standard}' 不存在")
    
    standard_info = kb.get_standard_info(standard)
    clauses = kb.get_clauses_by_standard(standard)
    
    clause_infos = []
    for clause in clauses:
        clause_infos.append(ClauseInfo(
            clause=clause.get("clause", ""),
            title=clause.get("title", ""),
            content=clause.get("content", ""),
            key_points=clause.get("key_points", []),
            implementation_guidance=clause.get("implementation_guidance")
        ))
    
    return StandardDetail(
        name=standard,
        title=standard_info.get("title", ""),
        description=standard_info.get("description", ""),
        clauses=clause_infos
    )


@router.get("/{standard}/clauses/{clause_num}", response_model=ClauseInfo)
async def get_clause_detail(standard: str, clause_num: str):
    """
    获取指定条款详情
    
    Args:
        standard: 标准代码，如 ISO9001:2015
        clause_num: 条款号，如 4.1
    
    Returns:
        条款详细信息
    """
    kb = get_kb()
    
    if standard not in kb.standards:
        raise HTTPException(status_code=404, detail=f"标准 '{standard}' 不存在")
    
    clause = kb.get_clause(standard, clause_num)
    
    if not clause:
        raise HTTPException(status_code=404, detail=f"条款 '{clause_num}' 不存在于标准 '{standard}'")
    
    return ClauseInfo(
        clause=clause.get("clause", ""),
        title=clause.get("title", ""),
        content=clause.get("content", ""),
        key_points=clause.get("key_points", []),
        implementation_guidance=clause.get("implementation_guidance")
    )


@router.post("/clauses/batch", response_model=ClausesBatchResponse)
async def get_clauses_batch(request: ClausesBatchRequest):
    """
    批量获取条款
    
    根据条款号列表批量获取多个条款的详细信息
    """
    kb = get_kb()
    
    results = kb.get_clauses_by_numbers(
        clause_numbers=request.clause_numbers,
        standards=request.standards
    )
    
    # 转换为响应模型
    response_results = {}
    total_found = 0
    
    for std, clauses in results.items():
        clause_infos = []
        for clause in clauses:
            clause_infos.append(ClauseInfo(
                clause=clause.get("clause", ""),
                title=clause.get("title", ""),
                content=clause.get("content", ""),
                key_points=clause.get("key_points", []),
                implementation_guidance=clause.get("implementation_guidance")
            ))
        response_results[std] = clause_infos
        total_found += len(clause_infos)
    
    return ClausesBatchResponse(
        results=response_results,
        total_found=total_found
    )


@router.get("/search", response_model=SearchResponse)
async def search_clauses(
    q: str = Query(..., description="搜索关键词"),
    standards: Optional[List[str]] = Query(None, description="指定搜索的标准代码列表")
):
    """
    搜索条款
    
    根据关键词在条款标题、内容和关键点中搜索
    
    Args:
        q: 搜索关键词
        standards: 可选，指定要搜索的标准代码列表
    
    Returns:
        匹配的条款列表
    """
    kb = get_kb()
    
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="搜索关键词不能为空")
    
    results = kb.search_clauses(keyword=q, standards=standards)
    
    # 转换为响应模型
    response_results = {}
    total_found = 0
    
    for std, clauses in results.items():
        clause_infos = []
        for clause in clauses:
            clause_infos.append(ClauseInfo(
                clause=clause.get("clause", ""),
                title=clause.get("title", ""),
                content=clause.get("content", ""),
                key_points=clause.get("key_points", []),
                implementation_guidance=clause.get("implementation_guidance")
            ))
        response_results[std] = clause_infos
        total_found += len(clause_infos)
    
    return SearchResponse(
        keyword=q,
        results=response_results,
        total_found=total_found
    )


@router.post("/format-for-prompt", response_model=FormatForPromptResponse)
async def format_clauses_for_prompt(request: FormatForPromptRequest):
    """
    格式化为Prompt文本
    
    将指定的条款格式化为适合LLM Prompt的文本格式
    """
    kb = get_kb()
    
    prompt_text = kb.format_clauses_for_prompt(
        clause_numbers=request.clause_numbers,
        standards=request.standards,
        include_guidance=request.include_guidance
    )
    
    return FormatForPromptResponse(
        prompt_text=prompt_text,
        clause_count=len(request.clause_numbers)
    )


@router.get("/{standard}/implementation-guidance", response_model=ImplementationGuidanceResponse)
async def get_implementation_guidance(
    standard: str,
    clauses: Optional[List[str]] = Query(None, description="指定条款号列表，不传则返回所有条款")
):
    """
    获取实施指导
    
    获取指定标准的实施指导信息
    
    Args:
        standard: 标准代码，如 ISO9001:2015
        clauses: 可选，指定条款号列表
    
    Returns:
        各条款的实施指导
    """
    kb = get_kb()
    
    if standard not in kb.standards:
        raise HTTPException(status_code=404, detail=f"标准 '{standard}' 不存在")
    
    # 如果未指定条款，获取所有条款
    if not clauses:
        all_clauses = kb.get_clauses_by_standard(standard)
        clauses = [c.get("clause", "") for c in all_clauses]
    
    guidance_dict = kb.get_implementation_guidance(
        clause_numbers=clauses,
        standards=[standard]
    )
    
    guidance = guidance_dict.get(standard, {})
    
    return ImplementationGuidanceResponse(
        standard=standard,
        guidance=guidance
    )
