#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 缺失项分析API
基于ISO标准条款检查文档覆盖情况
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.models import Project, Document
from app.modules.analyzer.missing_item_analyzer import MissingItemAnalyzer, analyze_coverage
from app.modules.analyzer.environment_analyzer import (
    parse_environmental_report, 
    generate_iso14001_documents,
    EnvironmentalAssessment
)
from app.modules.analyzer.safety_analyzer import (
    parse_safety_assessment,
    generate_iso45001_documents,
    SafetyAssessment
)

router = APIRouter(prefix="/analyzer", tags=["缺失项分析"])


# ============ 请求/响应模型 ============

class EnvironmentalReportRequest(BaseModel):
    """环境评估报告解析请求"""
    report_text: str = Field(..., description="环境评估报告全文")
    generate_documents: bool = Field(True, description="是否生成ISO14001文档内容")


class EnvironmentalReportResponse(BaseModel):
    """环境评估报告解析响应"""
    company_name: str
    aspects_count: int
    significant_aspects_count: int
    compliance_rate: float
    environmental_aspects: List[dict]
    generated_documents: Optional[dict] = None


class SafetyAssessmentRequest(BaseModel):
    """安全评估报告解析请求"""
    report_text: str = Field(..., description="职业健康安全评估报告全文")
    generate_documents: bool = Field(True, description="是否生成ISO45001文档内容")


class SafetyAssessmentResponse(BaseModel):
    """安全评估报告解析响应"""
    company_name: str
    hazards_count: int
    significant_hazards_count: int
    incidents_count: int
    compliance_rate: float
    hazards: List[dict]
    generated_documents: Optional[dict] = None


# ============ API路由 ============

@router.post("/coverage/{project_id}", summary="分析文档条款覆盖情况")
async def analyze_clause_coverage(
    project_id: str,
    standards: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    分析项目文档对ISO标准条款的覆盖情况
    
    Args:
        project_id: 项目ID
        standards: 要检查的标准列表，默认["ISO9001"]
        
    Returns:
        覆盖情况报告，包含每个条款的状态和补充建议
    """
    # 查找项目
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 获取项目文档
    result = await db.execute(select(Document).where(
        Document.project_id == project_id
    ))
    documents = result.scalars().all()
    
    if not documents:
        raise HTTPException(status_code=400, detail="项目暂无文档，请先生成文档")
    
    # 确定要检查的标准
    check_standards = standards or ["ISO9001"]
    
    # 构建文档列表用于分析
    doc_list = []
    for doc in documents:
        doc_list.append({
            "title": doc.title,
            "doc_type": doc.doc_type,
            "content": doc.current_content or doc.ai_content or "",
        })
    
    # 执行分析
    try:
        analyzer = MissingItemAnalyzer()
        report = analyzer.analyze(doc_list, check_standards)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")
    
    return {
        "project_id": project_id,
        "project_name": project.company_name,
        "standards": check_standards,
        "summary": report.get("summary", {}),
        "clauses": report.get("clauses", []),
        "suggestions": report.get("suggestions", []),
    }


@router.post("/coverage/quick", summary="快速覆盖检查")
async def quick_coverage_check(
    project_id: str,
    standard: str = "ISO9001",
    db: AsyncSession = Depends(get_db)
):
    """
    快速检查覆盖率（仅返回统计摘要）
    """
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    result = await db.execute(select(Document).where(
        Document.project_id == project_id
    ))
    documents = result.scalars().all()
    
    if not documents:
        raise HTTPException(status_code=400, detail="项目暂无文档")
    
    doc_list = [
        {
            "title": d.title,
            "doc_type": d.doc_type,
            "content": d.current_content or d.ai_content or "",
        }
        for d in documents
    ]
    
    try:
        report = analyze_coverage(doc_list, [standard])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")
    
    summary = report.get("summary", {})
    
    return {
        "project_id": project_id,
        "standard": standard,
        "total_clauses": summary.get("total_clauses", 0),
        "covered": summary.get("covered", 0),
        "partial": summary.get("partial", 0),
        "missing": summary.get("missing", 0),
        "coverage_rate": summary.get("coverage_rate", 0),
        "document_count": len(documents),
    }


@router.get("/standards", summary="获取支持的标准列表")
async def list_standards():
    """获取系统支持的ISO标准及其条款数量"""
    return {
        "standards": [
            {
                "code": "ISO9001",
                "name": "质量管理体系",
                "total_clauses": 42,
                "description": "ISO 9001:2015 质量管理体系要求",
            },
            {
                "code": "ISO14001",
                "name": "环境管理体系",
                "total_clauses": 25,
                "description": "ISO 14001:2015 环境管理体系要求",
            },
            {
                "code": "ISO45001",
                "name": "职业健康安全管理体系",
                "total_clauses": 26,
                "description": "ISO 45001:2018 职业健康安全管理体系要求",
            },
        ]
    }


# ============ V1.2 新增：环境评估报告解析 ============

@router.post("/environmental-report", response_model=EnvironmentalReportResponse, summary="解析环境评估报告")
async def analyze_environmental_report(request: EnvironmentalReportRequest):
    """
    解析 ISO14001 环境评估报告，提取环境因素、合规性评价等信息
    
    支持从环境评估报告文本中自动提取：
    - 环境因素识别
    - 重要环境因素
    - 合规性评价
    - 目标指标
    - 管理方案
    
    并可生成 ISO14001 体系文件所需内容
    """
    try:
        # 解析报告
        assessment = parse_environmental_report(request.report_text)
        
        # 生成文档内容（如果需要）
        generated_docs = None
        if request.generate_documents:
            generated_docs = generate_iso14001_documents(assessment)
        
        return EnvironmentalReportResponse(
            company_name=assessment.company_name,
            aspects_count=len(assessment.environmental_aspects),
            significant_aspects_count=len(assessment.significant_aspects),
            compliance_rate=_calculate_compliance_rate(assessment.compliance_items),
            environmental_aspects=[
                {
                    "activity": a.activity,
                    "aspect": a.aspect_name,
                    "impact": a.environmental_impact,
                    "significance": a.significance,
                }
                for a in assessment.environmental_aspects
            ],
            generated_documents=generated_docs,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


# ============ V1.2 新增：安全评估报告解析 ============

@router.post("/safety-assessment", response_model=SafetyAssessmentResponse, summary="解析职业健康安全评估报告")
async def analyze_safety_assessment(request: SafetyAssessmentRequest):
    """
    解析 ISO45001 职业健康安全评估报告，提取危险源、事故记录等信息
    
    支持从安全评估报告文本中自动提取：
    - 危险源识别
    - 重大危险源
    - 事故/事件记录
    - 法规合规性
    - 目标指标
    - 应急程序
    
    并可生成 ISO45001 体系文件所需内容
    """
    try:
        # 解析报告
        assessment = parse_safety_assessment(request.report_text)
        
        # 生成文档内容（如果需要）
        generated_docs = None
        if request.generate_documents:
            generated_docs = generate_iso45001_documents(assessment)
        
        return SafetyAssessmentResponse(
            company_name=assessment.company_name,
            hazards_count=len(assessment.hazards),
            significant_hazards_count=len(assessment.significant_hazards),
            incidents_count=len(assessment.incidents),
            compliance_rate=_calculate_compliance_rate(assessment.legal_requirements),
            hazards=[
                {
                    "activity": h.activity,
                    "hazard_source": h.hazard_source,
                    "risk_description": h.risk_description,
                    "risk_score": h.likelihood * h.severity,
                    "risk_level": h.risk_level,
                }
                for h in assessment.hazards
            ],
            generated_documents=generated_docs,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


# ============ 辅助函数 ============

def _calculate_compliance_rate(items: list) -> float:
    """计算合规率"""
    if not items:
        return 100.0
    compliant = sum(1 for item in items if getattr(item, 'compliance_status', None) == "合规" or item.get('status') == "合规")
    return round(compliant / len(items) * 100, 1)
