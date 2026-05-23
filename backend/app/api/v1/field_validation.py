#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字段验证API

集成防编造和信息来源优先级，提供字段验证功能
支持：质量方针、质量目标、部门名称、文件编号、人员姓名等字段验证
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.core.anti_fabrication import AntiFabricationValidator, RiskLevel, ValidationResult
from app.core.information_priority import InformationSource, CRITICAL_FIELDS

router = APIRouter(prefix="/field-validation", tags=["字段验证"])


# 请求和响应模型
class FieldValidationRequest(BaseModel):
    """字段验证请求"""
    field_name: str = Field(..., description="字段名称")
    field_value: str = Field(..., description="字段值")
    source: str = Field(..., description="信息来源: P1(用户输入)/P2(文件提取)/P3(AI生成)")
    source_file: Optional[str] = Field(None, description="来源文件名(P2时填写)")


class FieldValidationResponse(BaseModel):
    """字段验证响应"""
    field_name: str
    field_value: str
    is_valid: bool
    risk_level: str  # low/medium/high/critical
    message: str
    details: List[str]
    suggestions: List[str]
    source: str
    needs_verification: bool
    verification_reason: Optional[str] = None


class BatchValidationRequest(BaseModel):
    """批量验证请求"""
    fields: List[FieldValidationRequest]


class BatchValidationResponse(BaseModel):
    """批量验证响应"""
    results: List[FieldValidationResponse]
    summary: Dict[str, Any]


class ValidationReportRequest(BaseModel):
    """验证报告请求"""
    project_id: str
    fields: List[FieldValidationRequest]


class ValidationReportResponse(BaseModel):
    """验证报告响应"""
    project_id: str
    total_fields: int
    valid_fields: int
    needs_verification: int
    valid_rate: float
    risk_distribution: Dict[str, int]
    source_distribution: Dict[str, int]
    critical_issues: List[Dict[str, str]]
    verification_required: List[Dict[str, Any]]


class CriticalFieldInfo(BaseModel):
    """关键字段信息"""
    field_name: str
    display_name: str
    required: bool


class CriticalFieldsResponse(BaseModel):
    """关键字段列表响应"""
    fields: List[CriticalFieldInfo]
    total: int


class MarkVerifiedRequest(BaseModel):
    """标记已验证请求"""
    field_name: str
    verified_by: str


class MarkVerifiedResponse(BaseModel):
    """标记已验证响应"""
    success: bool
    field_name: str
    message: str


# 验证器实例
_validator = AntiFabricationValidator()


def _convert_risk_level(risk_level: RiskLevel) -> str:
    """转换风险等级为字符串"""
    return risk_level.value


def _validation_result_to_response(result: ValidationResult, source: str) -> FieldValidationResponse:
    """将验证结果转换为响应模型"""
    return FieldValidationResponse(
        field_name=result.field_name or "",
        field_value=result.field_value or "",
        is_valid=result.is_valid,
        risk_level=_convert_risk_level(result.risk_level),
        message=result.message,
        details=result.details,
        suggestions=result.suggestions,
        source=source,
        needs_verification=result.needs_verification,
        verification_reason=result.verification_reason if result.needs_verification else None
    )


@router.post("/validate", response_model=FieldValidationResponse)
async def validate_field(request: FieldValidationRequest):
    """
    验证单个字段（带来源信息）
    
    根据字段名称自动选择验证规则，结合信息来源进行验证
    
    信息来源优先级：
    - P1: 用户直接输入（最高优先级，宽松验证）
    - P2: 从上传文件提取（中等优先级，检查提取准确性）
    - P3: AI生成（需验证，严格验证）
    """
    # 验证来源值
    if request.source not in ["P1", "P2", "P3"]:
        raise HTTPException(status_code=400, detail="source必须是P1、P2或P3")
    
    # 执行验证
    result = _validator.validate_with_source(
        field_name=request.field_name,
        field_value=request.field_value,
        source=request.source,
        source_file=request.source_file
    )
    
    return _validation_result_to_response(result, request.source)


@router.post("/batch", response_model=BatchValidationResponse)
async def validate_batch(request: BatchValidationRequest):
    """
    批量验证字段
    
    同时验证多个字段，返回每个字段的验证结果和汇总统计
    """
    results = []
    
    for field in request.fields:
        # 验证来源值
        if field.source not in ["P1", "P2", "P3"]:
            raise HTTPException(status_code=400, detail=f"字段 {field.field_name} 的source必须是P1、P2或P3")
        
        result = _validator.validate_with_source(
            field_name=field.field_name,
            field_value=field.field_value,
            source=field.source,
            source_file=field.source_file
        )
        results.append(_validation_result_to_response(result, field.source))
    
    # 生成汇总
    total = len(results)
    valid_count = sum(1 for r in results if r.is_valid)
    needs_verification_count = sum(1 for r in results if r.needs_verification)
    
    risk_distribution = {
        "low": sum(1 for r in results if r.risk_level == "low"),
        "medium": sum(1 for r in results if r.risk_level == "medium"),
        "high": sum(1 for r in results if r.risk_level == "high"),
        "critical": sum(1 for r in results if r.risk_level == "critical"),
    }
    
    source_distribution = {
        "P1": sum(1 for r in results if r.source == "P1"),
        "P2": sum(1 for r in results if r.source == "P2"),
        "P3": sum(1 for r in results if r.source == "P3"),
    }
    
    summary = {
        "total": total,
        "valid": valid_count,
        "needs_verification": needs_verification_count,
        "valid_rate": valid_count / total if total > 0 else 0,
        "risk_distribution": risk_distribution,
        "source_distribution": source_distribution,
    }
    
    return BatchValidationResponse(
        results=results,
        summary=summary
    )


@router.post("/report", response_model=ValidationReportResponse)
async def generate_validation_report(request: ValidationReportRequest):
    """
    生成验证报告
    
    为项目生成完整的字段验证报告，包含统计信息和需验证项
    """
    # 准备验证数据
    fields_data = []
    for field in request.fields:
        fields_data.append({
            "field_name": field.field_name,
            "value": field.field_value,
            "source": field.source,
            "source_file": field.source_file
        })
    
    # 批量验证
    validation_results = _validator.validate_fields_batch(fields_data)
    
    # 生成报告
    report = _validator.generate_validation_report(validation_results)
    
    return ValidationReportResponse(
        project_id=request.project_id,
        total_fields=report["total_fields"],
        valid_fields=report["valid_fields"],
        needs_verification=report["needs_verification"],
        valid_rate=report["valid_rate"],
        risk_distribution=report["risk_distribution"],
        source_distribution=report["source_distribution"],
        critical_issues=report["critical_issues"],
        verification_required=report["verification_required"]
    )


@router.get("/critical-fields", response_model=CriticalFieldsResponse)
async def get_critical_fields():
    """
    获取关键字段列表
    
    返回系统中定义的关键字段及其配置信息
    """
    fields = []
    for field_name, config in CRITICAL_FIELDS.items():
        fields.append(CriticalFieldInfo(
            field_name=field_name,
            display_name=config.get("display_name", field_name),
            required=config.get("required", False)
        ))
    
    return CriticalFieldsResponse(
        fields=fields,
        total=len(fields)
    )


@router.post("/mark-verified", response_model=MarkVerifiedResponse)
async def mark_field_verified(request: MarkVerifiedRequest):
    """
    标记字段已验证
    
    人工确认字段内容正确后，标记为已验证状态
    """
    # 这里可以实现数据库更新逻辑
    # 简化处理，直接返回成功
    return MarkVerifiedResponse(
        success=True,
        field_name=request.field_name,
        message=f"字段 '{request.field_name}' 已由 {request.verified_by} 标记为已验证"
    )
