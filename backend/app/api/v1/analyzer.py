#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 缺失项分析API
基于ISO标准条款检查文档覆盖情况
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Project, Document
from app.modules.analyzer.missing_item_analyzer import MissingItemAnalyzer, analyze_coverage

router = APIRouter(prefix="/analyzer", tags=["缺失项分析"])


@router.post("/coverage/{project_id}", summary="分析文档条款覆盖情况")
async def analyze_clause_coverage(
    project_id: str,
    standards: Optional[List[str]] = None,
    db: Session = Depends(get_db)
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
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 获取项目文档
    documents = db.query(Document).filter(
        Document.project_id == project_id
    ).all()
    
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
    db: Session = Depends(get_db)
):
    """
    快速检查覆盖率（仅返回统计摘要）
    """
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    documents = db.query(Document).filter(
        Document.project_id == project_id
    ).all()
    
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
