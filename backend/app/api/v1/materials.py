#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 企业资料清单API
管理企业需提供的资料，识别缺失材料，提供模板下载
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import yaml

router = APIRouter(prefix="/materials", tags=["企业资料管理"])

# 加载行业配置
CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "industry_config.yaml"


def load_industry_config():
    """加载行业配置"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


# ============ 请求/响应模型 ============

class MaterialCheckRequest(BaseModel):
    """材料检查请求"""
    industry_code: str  # 行业代码
    company_info: Dict[str, Any]
    uploaded_materials: List[str]  # 已上传的材料名称列表


class MaterialItem(BaseModel):
    """材料项"""
    name: str
    required: bool
    description: str
    alert_level: str  # critical / warning / info
    template_available: bool
    template_name: Optional[str] = None


class MaterialCheckResponse(BaseModel):
    """材料检查响应"""
    industry_name: str
    total_required: int
    uploaded_count: int
    missing_critical: List[MaterialItem]
    missing_warning: List[MaterialItem]
    missing_info: List[MaterialItem]
    provided_materials: List[MaterialItem]


class TemplateDownloadRequest(BaseModel):
    """模板下载请求"""
    material_name: str
    industry_code: Optional[str] = None


# ============ API路由 ============

@router.get("/industries", summary="获取行业列表")
async def get_industries():
    """获取支持的行业列表"""
    config = load_industry_config()
    industries = []
    
    for code, info in config.get("industries", {}).items():
        industries.append({
            "code": code,
            "name": info.get("name", ""),
            "description": info.get("description", ""),
            "representative_company": info.get("representative_company", ""),
        })
    
    return {"industries": industries}


@router.get("/industry/{industry_code}", summary="获取行业详情")
async def get_industry_detail(industry_code: str):
    """获取行业详细信息"""
    config = load_industry_config()
    industry = config.get("industries", {}).get(industry_code)
    
    if not industry:
        raise HTTPException(status_code=404, detail="行业不存在")
    
    return {
        "code": industry_code,
        "name": industry.get("name"),
        "description": industry.get("description"),
        "business_characteristics": industry.get("business_characteristics", []),
        "special_requirements": industry.get("special_requirements", {}),
        "required_materials": industry.get("required_company_materials", {}),
    }


@router.post("/check", response_model=MaterialCheckResponse, summary="检查企业材料完整性")
async def check_materials(request: MaterialCheckRequest):
    """检查企业材料是否完整，识别缺失材料"""
    config = load_industry_config()
    industry = config.get("industries", {}).get(request.industry_code)
    common = config.get("common", {})
    
    if not industry:
        raise HTTPException(status_code=404, detail="行业不存在")
    
    # 收集所有必需材料
    all_materials = []
    
    # 行业特定材料
    for category, materials in industry.get("required_company_materials", {}).items():
        for material in materials:
            all_materials.append({
                "name": material["name"],
                "required": material["required"],
                "description": material["description"],
                "category": category,
                "source": "industry",
            })
    
    # 通用材料
    for category, materials in common.get("required_materials", {}).items():
        for material in materials:
            all_materials.append({
                "name": material["name"],
                "required": material["required"],
                "description": material["description"],
                "category": category,
                "source": "common",
                "template_available": material.get("template_available", False),
            })
    
    # 分类材料
    missing_critical = []
    missing_warning = []
    missing_info = []
    provided_materials = []
    
    for material in all_materials:
        material_item = MaterialItem(
            name=material["name"],
            required=material["required"],
            description=material["description"],
            alert_level="critical" if material["required"] else "warning",
            template_available=material.get("template_available", True),
            template_name=f"{material['name']}模板" if material.get("template_available") else None,
        )
        
        if material["name"] in request.uploaded_materials:
            provided_materials.append(material_item)
        elif material["required"]:
            missing_critical.append(material_item)
        else:
            missing_warning.append(material_item)
    
    return MaterialCheckResponse(
        industry_name=industry.get("name", ""),
        total_required=len([m for m in all_materials if m["required"]]),
        uploaded_count=len(provided_materials),
        missing_critical=missing_critical,
        missing_warning=missing_warning,
        missing_info=missing_info,
        provided_materials=provided_materials,
    )


@router.get("/list/{industry_code}", summary="获取行业材料清单")
async def get_materials_list(industry_code: str):
    """获取指定行业的完整材料清单"""
    config = load_industry_config()
    industry = config.get("industries", {}).get(industry_code)
    common = config.get("common", {})
    
    if not industry:
        raise HTTPException(status_code=404, detail="行业不存在")
    
    materials = {
        "industry_specific": industry.get("required_company_materials", {}),
        "common": common.get("required_materials", {}),
    }
    
    return {
        "industry_code": industry_code,
        "industry_name": industry.get("name"),
        "materials": materials,
    }


@router.post("/template/download", summary="下载材料模板")
async def download_template(request: TemplateDownloadRequest):
    """下载指定材料的填写模板"""
    # 模板映射
    template_mapping = {
        "管理者代表任命书": "templates/appointments/management_representative.docx",
        "内审员名单": "templates/forms/internal_auditor_list.docx",
        "组织架构图": "templates/forms/organization_chart.pptx",
        "岗位说明书": "templates/forms/job_description.docx",
        "目标指标": "templates/forms/objectives_targets.docx",
        "环境因素识别表": "templates/forms/environmental_factors.docx",
        "危险源识别表": "templates/forms/hazard_identification.docx",
        "法律法规清单": "templates/forms/legal_requirements.docx",
        "管理体系运行情况说明": "templates/forms/system_operation_description.docx",
    }
    
    template_path = template_mapping.get(request.material_name)
    
    if not template_path:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return {
        "material_name": request.material_name,
        "template_path": template_path,
        "download_url": f"/api/v1/materials/template/file/{request.material_name}",
        "description": f"{request.material_name}填写模板",
    }


@router.get("/templates/available", summary="获取可用模板列表")
async def get_available_templates():
    """获取软件可提供的所有模板列表"""
    config = load_industry_config()
    templates = config.get("software_templates", {})
    
    result = []
    for category, info in templates.items():
        result.append({
            "category": category,
            "description": info.get("description", ""),
            "items": info.get("items", []),
        })
    
    return {"templates": result}


@router.get("/workflow", summary="获取材料准备流程")
async def get_materials_workflow():
    """获取材料准备的完整流程"""
    config = load_industry_config()
    workflow = config.get("missing_materials_config", {}).get("workflow", [])
    
    return {
        "workflow": workflow,
        "description": "企业材料准备的标准流程",
    }


@router.post("/generate-checklist", summary="生成材料检查清单")
async def generate_checklist(request: MaterialCheckRequest):
    """生成企业材料检查清单（可用于打印）"""
    config = load_industry_config()
    industry = config.get("industries", {}).get(request.industry_code)
    
    if not industry:
        raise HTTPException(status_code=404, detail="行业不存在")
    
    checklist = {
        "title": f"{industry.get('name')} - 体系认证材料检查清单",
        "company": request.company_info.get("company_name", ""),
        "generated_at": "2026-01-01",
        "items": [],
    }
    
    # 添加检查项
    for category, materials in industry.get("required_company_materials", {}).items():
        for material in materials:
            checklist["items"].append({
                "category": category,
                "material_name": material["name"],
                "required": material["required"],
                "description": material["description"],
                "status": "已提供" if material["name"] in request.uploaded_materials else "待补充",
                "has_template": True,
            })
    
    return checklist
