#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 认证阶段确认API
提供认证阶段选项、文件范围查询和智能建议。
"""

from enum import Enum
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/cert-stage", tags=["认证阶段"])


# ==================== 数据模型 ====================

class CertStage(str, Enum):
    """认证阶段"""
    INITIAL = "initial"                    # 初次认证
    SUPERVISION_1 = "supervision_1"        # 监督审核1（第2年）
    SUPERVISION_2 = "supervision_2"        # 监督审核2（第3年）
    RECERTIFICATION = "recertification"    # 再认证（第4年）


class CertStageOption(BaseModel):
    """认证阶段选项"""
    stage: CertStage
    label: str
    description: str
    year: str


class DocumentScope(BaseModel):
    """文件范围"""
    level: str              # 层级名称
    level_code: str         # 层级编码
    action: str             # 操作类型："生成" / "更新"
    document_types: List[str]  # 文件类型列表
    optional: bool = Field(False, description="是否可选（询问用户）")
    default_selected: bool = Field(True, description="默认是否选中")


class DocumentScopeResponse(BaseModel):
    """文件范围响应"""
    stage: CertStage
    stage_label: str
    description: str
    scopes: List[DocumentScope]
    has_optional: bool = Field(False, description="是否包含可选文件层级")
    optional_scopes: List[DocumentScope] = Field([], description="可选文件层级列表")


class CertStageSuggestRequest(BaseModel):
    """认证阶段建议请求"""
    has_existing_cert: bool = Field(False, description="是否已有认证证书")
    cert_issue_year: Optional[int] = Field(None, description="初次发证年份（如2023）")
    cert_standards: Optional[List[str]] = Field(None, description="已认证标准列表")
    company_name: Optional[str] = Field(None, description="企业名称")


class CertStageSuggestResponse(BaseModel):
    """认证阶段建议响应"""
    suggested_stage: CertStage
    stage_label: str
    reason: str
    cert_year_info: Optional[str] = None


# ==================== 静态数据 ====================

CERT_STAGE_OPTIONS: List[Dict[str, Any]] = [
    {
        "stage": CertStage.INITIAL,
        "label": "初次认证",
        "description": "企业首次申请ISO认证，需要建立完整的体系文件（一级~四级）",
        "year": "第1年",
    },
    {
        "stage": CertStage.SUPERVISION_1,
        "label": "监督审核1",
        "description": "初次认证后的第一次监督审核，主要检查体系运行记录和三级/四级文件更新",
        "year": "第2年",
    },
    {
        "stage": CertStage.SUPERVISION_2,
        "label": "监督审核2",
        "description": "初次认证后的第二次监督审核，继续检查体系运行记录和三级/四级文件更新",
        "year": "第3年",
    },
    {
        "stage": CertStage.RECERTIFICATION,
        "label": "再认证",
        "description": "证书三年有效期届满前的全面再认证审核，需要更新全部体系文件（一级~四级）",
        "year": "第4年",
    },
]

# 各阶段文件范围定义
STAGE_DOCUMENT_SCOPES: Dict[CertStage, List[Dict[str, Any]]] = {
    CertStage.INITIAL: [
        {
            "level": "一级文件",
            "level_code": "level_1",
            "action": "生成",
            "document_types": [
                "质量管理手册",
                "环境管理手册",
                "职业健康安全管理手册",
                "综合管理手册",
            ],
        },
        {
            "level": "二级文件",
            "level_code": "level_2",
            "action": "生成",
            "document_types": [
                "文件控制程序",
                "记录控制程序",
                "内部审核程序",
                "管理评审程序",
                "纠正措施程序",
                "培训控制程序",
                "合同评审程序",
                "采购控制程序",
                "生产和服务提供控制程序",
                "产品检验控制程序",
                "顾客满意度测量程序",
                "环境因素识别与评价程序",
                "法律法规获取与更新程序",
                "应急准备和响应程序",
                "危险源辨识与风险评价程序",
                "事件调查与处理程序",
            ],
        },
        {
            "level": "三级文件",
            "level_code": "level_3",
            "action": "生成",
            "document_types": [
                "管理制度",
                "作业指导书",
                "操作规程",
                "岗位职责说明书",
                "检验标准",
                "服务规范",
            ],
        },
        {
            "level": "四级文件",
            "level_code": "level_4",
            "action": "生成",
            "document_types": [
                "培训记录表",
                "检验记录表",
                "内审检查表",
                "纠正措施单",
                "管理评审记录",
                "合同评审记录",
                "采购记录表",
                "顾客满意度调查表",
                "设备维护保养记录",
                "文件发放记录",
            ],
        },
    ],
    CertStage.SUPERVISION_1: [
        {
            "level": "一级文件",
            "level_code": "level_1",
            "action": "更新",
            "optional": True,
            "default_selected": False,
            "document_types": [
                "质量管理手册",
                "环境管理手册",
                "职业健康安全管理手册",
            ],
        },
        {
            "level": "二级文件",
            "level_code": "level_2",
            "action": "更新",
            "optional": True,
            "default_selected": False,
            "document_types": [
                "文件控制程序",
                "记录控制程序",
                "内部审核程序",
                "管理评审程序",
                "纠正措施程序",
                "培训控制程序",
                "合同评审程序",
                "采购控制程序",
                "生产和服务提供控制程序",
                "产品检验控制程序",
                "顾客满意度测量程序",
                "环境因素识别与评价程序",
                "法律法规获取与更新程序",
                "应急准备和响应程序",
                "危险源辨识与风险评价程序",
                "事件调查与处理程序",
            ],
        },
        {
            "level": "三级文件",
            "level_code": "level_3",
            "action": "更新",
            "optional": False,
            "default_selected": True,
            "document_types": [
                "管理制度（更新版）",
                "作业指导书（更新版）",
                "操作规程（更新版）",
            ],
        },
        {
            "level": "四级文件",
            "level_code": "level_4",
            "action": "更新",
            "optional": False,
            "default_selected": True,
            "document_types": [
                "培训记录表",
                "检验记录表",
                "内审检查表",
                "纠正措施单",
                "管理评审记录",
                "设备维护保养记录",
                "应急演练记录",
                "危险源辨识记录",
                "环境因素识别记录",
            ],
        },
    ],
    CertStage.SUPERVISION_2: [
        {
            "level": "一级文件",
            "level_code": "level_1",
            "action": "更新",
            "optional": True,
            "default_selected": False,
            "document_types": [
                "质量管理手册",
                "环境管理手册",
                "职业健康安全管理手册",
            ],
        },
        {
            "level": "二级文件",
            "level_code": "level_2",
            "action": "更新",
            "optional": True,
            "default_selected": False,
            "document_types": [
                "文件控制程序",
                "记录控制程序",
                "内部审核程序",
                "管理评审程序",
                "纠正措施程序",
                "培训控制程序",
                "合同评审程序",
                "采购控制程序",
                "生产和服务提供控制程序",
                "产品检验控制程序",
                "顾客满意度测量程序",
                "环境因素识别与评价程序",
                "法律法规获取与更新程序",
                "应急准备和响应程序",
                "危险源辨识与风险评价程序",
                "事件调查与处理程序",
            ],
        },
        {
            "level": "三级文件",
            "level_code": "level_3",
            "action": "更新",
            "optional": False,
            "default_selected": True,
            "document_types": [
                "管理制度（更新版）",
                "作业指导书（更新版）",
                "操作规程（更新版）",
            ],
        },
        {
            "level": "四级文件",
            "level_code": "level_4",
            "action": "更新",
            "optional": False,
            "default_selected": True,
            "document_types": [
                "培训记录表",
                "检验记录表",
                "内审检查表",
                "纠正措施单",
                "管理评审记录",
                "设备维护保养记录",
                "应急演练记录",
                "危险源辨识记录",
                "环境因素识别记录",
            ],
        },
    ],
    CertStage.RECERTIFICATION: [
        {
            "level": "一级文件",
            "level_code": "level_1",
            "action": "更新",
            "document_types": [
                "质量管理手册（更新版）",
                "环境管理手册（更新版）",
                "职业健康安全管理手册（更新版）",
                "综合管理手册（更新版）",
            ],
        },
        {
            "level": "二级文件",
            "level_code": "level_2",
            "action": "更新",
            "document_types": [
                "文件控制程序（更新版）",
                "记录控制程序（更新版）",
                "内部审核程序（更新版）",
                "管理评审程序（更新版）",
                "纠正措施程序（更新版）",
                "培训控制程序（更新版）",
                "合同评审程序（更新版）",
                "采购控制程序（更新版）",
                "生产和服务提供控制程序（更新版）",
                "产品检验控制程序（更新版）",
                "顾客满意度测量程序（更新版）",
                "环境因素识别与评价程序（更新版）",
                "法律法规获取与更新程序（更新版）",
                "应急准备和响应程序（更新版）",
                "危险源辨识与风险评价程序（更新版）",
                "事件调查与处理程序（更新版）",
            ],
        },
        {
            "level": "三级文件",
            "level_code": "level_3",
            "action": "更新",
            "document_types": [
                "管理制度（更新版）",
                "作业指导书（更新版）",
                "操作规程（更新版）",
                "岗位职责说明书（更新版）",
                "检验标准（更新版）",
                "服务规范（更新版）",
            ],
        },
        {
            "level": "四级文件",
            "level_code": "level_4",
            "action": "更新",
            "document_types": [
                "培训记录表",
                "检验记录表",
                "内审检查表",
                "纠正措施单",
                "管理评审记录",
                "合同评审记录",
                "采购记录表",
                "顾客满意度调查表",
                "设备维护保养记录",
                "文件发放记录",
            ],
        },
    ],
}


# ==================== API 接口 ====================

@router.get("/options", summary="获取认证阶段选项列表")
async def get_cert_stage_options() -> List[CertStageOption]:
    """
    获取所有可用的认证阶段选项。

    返回四个阶段：
    初次认证（第1年）
    监督审核1（第2年）
    监督审核2（第3年）
    再认证（第4年）
    """
    return [
        CertStageOption(
            stage=opt["stage"],
            label=opt["label"],
            description=opt["description"],
            year=opt["year"],
        )
        for opt in CERT_STAGE_OPTIONS
    ]


@router.get("/{stage}/document-scope", summary="获取指定阶段的文件范围")
async def get_document_scope(stage: CertStage) -> DocumentScopeResponse:
    """
    获取指定认证阶段需要生成或更新的文件范围。

    initial: 一级~四级全部生成
    supervision_1: 三级（管理制度）和四级（记录表格）必须更新，一级和二级可选
    supervision_2: 三级（管理制度）和四级（记录表格）必须更新，一级和二级可选
    recertification: 一级~四级全部更新
    """
    stage_info = None
    for opt in CERT_STAGE_OPTIONS:
        if opt["stage"] == stage:
            stage_info = opt
            break

    if not stage_info:
        raise HTTPException(status_code=400, detail=f"未知的认证阶段: {stage}")

    scopes_data = STAGE_DOCUMENT_SCOPES.get(stage, [])
    
    scopes = []
    for s in scopes_data:
        scope = DocumentScope(
            level=s["level"],
            level_code=s["level_code"],
            action=s["action"],
            document_types=s["document_types"],
            optional=s.get("optional", False),
            default_selected=s.get("default_selected", True),
        )
        scopes.append(scope)
    
    optional_scopes = [s for s in scopes if s.optional]
    has_optional = len(optional_scopes) > 0

    return DocumentScopeResponse(
        stage=stage,
        stage_label=stage_info["label"],
        description=stage_info["description"],
        scopes=scopes,
        has_optional=has_optional,
        optional_scopes=optional_scopes,
    )


@router.post("/suggest", summary="根据企业信息建议认证阶段")
async def suggest_cert_stage(request: CertStageSuggestRequest) -> CertStageSuggestResponse:
    """
    根据企业已有认证信息，智能建议当前应选择的认证阶段。
    """
    from datetime import datetime
    current_year = datetime.now().year

    if not request.has_existing_cert:
        return CertStageSuggestResponse(
            suggested_stage=CertStage.INITIAL,
            stage_label="初次认证",
            reason="企业尚未获得ISO认证证书，建议申请初次认证。需要建立完整的体系文件（一级~四级）。",
            cert_year_info=None,
        )

    if request.cert_issue_year is None:
        return CertStageSuggestResponse(
            suggested_stage=CertStage.INITIAL,
            stage_label="初次认证",
            reason="未提供发证年份信息，无法判断认证阶段。如已有证书请补充发证年份。",
            cert_year_info=None,
        )

    years_since_issue = current_year - request.cert_issue_year

    if years_since_issue <= 0:
        return CertStageSuggestResponse(
            suggested_stage=CertStage.INITIAL,
            stage_label="初次认证",
            reason=f"发证年份{request.cert_issue_year}不正确（晚于当前年份{current_year}），请核实。",
            cert_year_info=f"发证年份: {request.cert_issue_year}",
        )
    elif years_since_issue == 1:
        return CertStageSuggestResponse(
            suggested_stage=CertStage.SUPERVISION_1,
            stage_label="监督审核1",
            reason=f"证书于{request.cert_issue_year}年发证，距今{years_since_issue}年，处于第2年监督审核阶段。建议更新三级文件（管理制度）和四级文件（记录表格），一级和二级文件可选更新。",
            cert_year_info=f"发证年份: {request.cert_issue_year}，认证周期第{years_since_issue + 1}年",
        )
    elif years_since_issue == 2:
        return CertStageSuggestResponse(
            suggested_stage=CertStage.SUPERVISION_2,
            stage_label="监督审核2",
            reason=f"证书于{request.cert_issue_year}年发证，距今{years_since_issue}年，处于第3年监督审核阶段。建议更新三级文件（管理制度）和四级文件（记录表格），一级和二级文件可选更新。",
            cert_year_info=f"发证年份: {request.cert_issue_year}，认证周期第{years_since_issue + 1}年",
        )
    else:
        return CertStageSuggestResponse(
            suggested_stage=CertStage.RECERTIFICATION,
            stage_label="再认证",
            reason=f"证书于{request.cert_issue_year}年发证，距今{years_since_issue}年，证书三年有效期已届满，需要进行再认证审核。建议全面更新所有体系文件（一级~四级）。",
            cert_year_info=f"发证年份: {request.cert_issue_year}，认证周期第{years_since_issue + 1}年（需再认证）",
        )
