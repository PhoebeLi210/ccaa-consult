"""
防编造API接口模块
提供内容验证和差异化处理的REST API接口
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status
from enum import Enum

# 导入核心验证模块
from app.core.anti_fabrication import (
    AntiFabricationValidator,
    RiskLevel,
    ValidationResult
)
from app.core.content_diversifier import (
    ContentDiversifier,
    IndustryType,
    DiversificationResult
)


# 创建路由
router = APIRouter(prefix="/validators", tags=["validators"])


# ============ 请求/响应模型定义 ============

class RiskLevelEnum(str, Enum):
    """风险等级枚举（API用）"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IndustryEnum(str, Enum):
    """行业类型枚举（API用）"""
    MANUFACTURING = "manufacturing"
    SERVICE = "service"
    CONSTRUCTION = "construction"
    GENERAL = "general"


class AntiFabricationRequest(BaseModel):
    """防编造验证请求模型"""
    content: str = Field(..., description="待验证的内容文本", min_length=1)
    validation_type: str = Field(
        default="all",
        description="验证类型: all/quality_policy/quality_objectives/department/doc_number/person"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "我们坚持质量第一、客户至上的方针，持续改进产品质量",
                "validation_type": "all"
            }
        }


class QualityPolicyRequest(BaseModel):
    """质量方针验证请求模型"""
    policy_text: str = Field(..., description="质量方针文本", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "policy_text": "本公司坚持质量第一、客户满意、持续改进的质量方针"
            }
        }


class QualityObjectivesRequest(BaseModel):
    """质量目标验证请求模型"""
    objectives_text: str = Field(..., description="质量目标文本", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "objectives_text": "产品合格率达到98%，客户满意度达到95%以上"
            }
        }


class DiversifyRequest(BaseModel):
    """内容差异化请求模型"""
    text: str = Field(..., description="待处理的文本内容", min_length=1)
    industry: IndustryEnum = Field(
        default=IndustryEnum.GENERAL,
        description="行业类型"
    )
    replacement_ratio: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="术语替换比例"
    )
    company_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="企业信息（可选）"
    )
    generate_variants_count: int = Field(
        default=1,
        ge=1,
        le=5,
        description="生成变体数量"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "我们坚持质量第一、客户至上的方针，持续改进产品质量",
                "industry": "manufacturing",
                "replacement_ratio": 0.3,
                "company_info": {
                    "name": "某某制造有限公司",
                    "products": ["机械零部件", "精密配件"],
                    "equipment": ["CNC机床", "检测设备"]
                }
            }
        }


class ValidationDetail(BaseModel):
    """验证详情响应模型"""
    is_valid: bool
    risk_level: RiskLevelEnum
    message: str
    details: List[str]
    suggestions: List[str]


class AntiFabricationResponse(BaseModel):
    """防编造验证响应模型"""
    success: bool
    data: Dict[str, ValidationDetail]
    summary: Dict[str, Any]


class DiversifyResponse(BaseModel):
    """内容差异化响应模型"""
    success: bool
    data: Dict[str, Any]
    variants: List[Dict[str, Any]]


# ============ API端点定义 ============

@router.post(
    "/anti-fabrication",
    response_model=AntiFabricationResponse,
    summary="综合防编造验证",
    description="对输入内容进行全面的防编造验证，包括质量方针、目标、部门名称、文件编号、人员姓名等"
)
async def anti_fabrication_validate(request: AntiFabricationRequest):
    """
    综合防编造验证端点
    
    根据validation_type参数执行不同类型的验证：
    - all: 执行所有验证
    - quality_policy: 仅验证质量方针
    - quality_objectives: 仅验证质量目标
    - department: 仅验证部门名称
    - doc_number: 仅验证文件编号
    - person: 仅验证人员姓名
    """
    try:
        validator = AntiFabricationValidator()
        results = {}
        
        validation_type = request.validation_type.lower()
        content = request.content.strip()
        
        # 根据验证类型执行相应验证
        if validation_type in ["all", "quality_policy"]:
            result = validator.validate_quality_policy(content)
            results["quality_policy"] = _convert_validation_result(result)
        
        if validation_type in ["all", "quality_objectives"]:
            result = validator.validate_quality_objectives(content)
            results["quality_objectives"] = _convert_validation_result(result)
        
        if validation_type in ["all", "department"]:
            result = validator.validate_department_name(content)
            results["department"] = _convert_validation_result(result)
        
        if validation_type in ["all", "doc_number"]:
            result = validator.validate_document_number(content)
            results["doc_number"] = _convert_validation_result(result)
        
        if validation_type in ["all", "person"]:
            result = validator.validate_person_name(content)
            results["person"] = _convert_validation_result(result)
        
        # 生成汇总信息
        summary = _generate_summary(results)
        
        return AntiFabricationResponse(
            success=True,
            data=results,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证过程发生错误: {str(e)}"
        )


@router.post(
    "/quality-policy",
    response_model=ValidationDetail,
    summary="质量方针验证",
    description="专门验证质量方针是否为通用套话，检测是否包含企业特色"
)
async def validate_quality_policy(request: QualityPolicyRequest):
    """
    质量方针验证端点
    
    检测质量方针中是否包含过多的通用套话（如"持续改进"、"客户满意"等），
    并评估内容是否具有企业特色。
    """
    try:
        validator = AntiFabricationValidator()
        result = validator.validate_quality_policy(request.policy_text)
        return _convert_validation_result(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证过程发生错误: {str(e)}"
        )


@router.post(
    "/quality-objectives",
    response_model=ValidationDetail,
    summary="质量目标验证",
    description="专门验证质量目标是否包含具体数字指标和时间期限"
)
async def validate_quality_objectives(request: QualityObjectivesRequest):
    """
    质量目标验证端点
    
    检测质量目标是否包含：
    - 具体的量化指标（如百分比、数值）
    - 明确的时间期限
    - 避免模糊表述（如"力争"、"尽量"等）
    """
    try:
        validator = AntiFabricationValidator()
        result = validator.validate_quality_objectives(request.objectives_text)
        return _convert_validation_result(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证过程发生错误: {str(e)}"
        )


@router.post(
    "/diversify",
    response_model=DiversifyResponse,
    summary="内容差异化处理",
    description="对内容进行差异化处理，包括同义词替换、添加企业信息、调整句子结构等"
)
async def diversify_content(request: DiversifyRequest):
    """
    内容差异化处理端点
    
    提供以下功能：
    1. 根据行业类型替换专业术语
    2. 融入企业具体信息（名称、产品、设备等）
    3. 随机调整句子结构（主动/被动、长短句）
    4. 生成多个变体供选择
    """
    try:
        diversifier = ContentDiversifier()
        variants = []
        
        # 生成指定数量的变体
        diversification_results = diversifier.generate_variants(
            template=request.text,
            count=request.generate_variants_count,
            industry=request.industry.value,
            company_info=request.company_info
        )
        
        for i, result in enumerate(diversification_results):
            variant = {
                "variant_id": i + 1,
                "text": result.diversified_text,
                "changes": result.changes_made,
                "confidence_score": result.confidence_score,
                "industry": result.industry
            }
            variants.append(variant)
        
        # 主处理结果（第一个变体）
        main_result = diversification_results[0] if diversification_results else None
        
        data = {
            "original_text": request.text,
            "processed_text": main_result.diversified_text if main_result else request.text,
            "industry": request.industry.value,
            "total_changes": len(main_result.changes_made) if main_result else 0,
            "confidence_score": main_result.confidence_score if main_result else 0
        }
        
        return DiversifyResponse(
            success=True,
            data=data,
            variants=variants
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"差异化处理过程发生错误: {str(e)}"
        )


@router.post(
    "/validate-department",
    response_model=ValidationDetail,
    summary="部门名称验证",
    description="验证部门名称是否在标准列表中"
)
async def validate_department(department_name: str):
    """
    部门名称验证端点
    
    检查部门名称是否符合30个标准部门命名规范。
    """
    try:
        validator = AntiFabricationValidator()
        result = validator.validate_department_name(department_name)
        return _convert_validation_result(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证过程发生错误: {str(e)}"
        )


@router.post(
    "/validate-doc-number",
    response_model=ValidationDetail,
    summary="文件编号验证",
    description="验证文件编号格式是否符合标准（支持XXX-QESMS-A-001等格式）"
)
async def validate_document_number(doc_number: str):
    """
    文件编号验证端点
    
    支持以下格式：
    - XXX-QESMS-A-001（三体系文件）
    - XXX-ISO-001（ISO文件）
    - XXX-QM-001（质量手册）
    - XXX-EM-001（环境手册）
    - XXX-SM-001（安全手册）
    """
    try:
        validator = AntiFabricationValidator()
        result = validator.validate_document_number(doc_number)
        return _convert_validation_result(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证过程发生错误: {str(e)}"
        )


@router.post(
    "/validate-person",
    response_model=ValidationDetail,
    summary="人员姓名验证",
    description="验证人员姓名是否模糊（检测'负责人'、'相关人员'等模糊表述）"
)
async def validate_person_name(person_name: str):
    """
    人员姓名验证端点
    
    检测是否使用了模糊的人员称谓而非具体姓名。
    """
    try:
        validator = AntiFabricationValidator()
        result = validator.validate_person_name(person_name)
        return _convert_validation_result(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证过程发生错误: {str(e)}"
        )


# ============ 辅助函数 ============

def _convert_validation_result(result: ValidationResult) -> ValidationDetail:
    """
    将ValidationResult转换为API响应模型
    
    Args:
        result: 验证结果对象
        
    Returns:
        ValidationDetail: API响应模型
    """
    risk_level_map = {
        RiskLevel.LOW: RiskLevelEnum.LOW,
        RiskLevel.MEDIUM: RiskLevelEnum.MEDIUM,
        RiskLevel.HIGH: RiskLevelEnum.HIGH,
        RiskLevel.CRITICAL: RiskLevelEnum.CRITICAL
    }
    
    return ValidationDetail(
        is_valid=result.is_valid,
        risk_level=risk_level_map.get(result.risk_level, RiskLevelEnum.MEDIUM),
        message=result.message,
        details=result.details,
        suggestions=result.suggestions
    )


def _generate_summary(results: Dict[str, ValidationDetail]) -> Dict[str, Any]:
    """
    生成验证结果汇总
    
    Args:
        results: 各字段验证结果
        
    Returns:
        Dict: 汇总信息
    """
    total_checks = len(results)
    valid_checks = sum(1 for r in results.values() if r.is_valid)
    
    risk_counts = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0
    }
    
    for result in results.values():
        risk_counts[result.risk_level.value] += 1
    
    # 确定整体风险等级
    if risk_counts["critical"] > 0:
        overall_risk = "critical"
    elif risk_counts["high"] > 0:
        overall_risk = "high"
    elif risk_counts["medium"] > total_checks / 2:
        overall_risk = "medium"
    else:
        overall_risk = "low"
    
    return {
        "total_checks": total_checks,
        "valid_checks": valid_checks,
        "invalid_checks": total_checks - valid_checks,
        "valid_rate": round(valid_checks / total_checks * 100, 2) if total_checks > 0 else 0,
        "risk_distribution": risk_counts,
        "overall_risk_level": overall_risk,
        "recommendation": _get_recommendation(overall_risk)
    }


def _get_recommendation(risk_level: str) -> str:
    """
    根据风险等级获取建议
    
    Args:
        risk_level: 风险等级
        
    Returns:
        str: 建议文本
    """
    recommendations = {
        "low": "内容整体可信，可按需微调优化",
        "medium": "部分内容需要关注，建议根据提示进行优化",
        "high": "存在较多问题，建议重新审查并修改相关内容",
        "critical": "存在严重编造嫌疑，必须重新撰写"
    }
    return recommendations.get(risk_level, "请根据具体提示进行处理")


# ============ 批量验证接口（可选扩展） ============

class BatchValidationRequest(BaseModel):
    """批量验证请求模型"""
    items: List[Dict[str, str]] = Field(..., description="待验证的项目列表")
    validation_types: List[str] = Field(
        default=["quality_policy"],
        description="要执行的验证类型列表"
    )


class BatchValidationResponse(BaseModel):
    """批量验证响应模型"""
    success: bool
    total_count: int
    results: List[Dict[str, Any]]


@router.post(
    "/batch-validate",
    response_model=BatchValidationResponse,
    summary="批量验证",
    description="批量验证多个内容项"
)
async def batch_validate(request: BatchValidationRequest):
    """
    批量验证端点
    
    可同时验证多个内容项，提高处理效率。
    """
    try:
        validator = AntiFabricationValidator()
        results = []
        
        for item in request.items:
            item_results = {}
            for vtype in request.validation_types:
                if vtype in item:
                    if vtype == "quality_policy":
                        result = validator.validate_quality_policy(item[vtype])
                    elif vtype == "quality_objectives":
                        result = validator.validate_quality_objectives(item[vtype])
                    elif vtype == "department":
                        result = validator.validate_department_name(item[vtype])
                    elif vtype == "doc_number":
                        result = validator.validate_document_number(item[vtype])
                    elif vtype == "person":
                        result = validator.validate_person_name(item[vtype])
                    else:
                        continue
                    
                    item_results[vtype] = _convert_validation_result(result)
            
            results.append({
                "item_id": item.get("id", len(results) + 1),
                "validations": item_results
            })
        
        return BatchValidationResponse(
            success=True,
            total_count=len(request.items),
            results=results
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量验证过程发生错误: {str(e)}"
        )
