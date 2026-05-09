#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 企业资料清单API
管理企业需提供的资料，识别缺失材料，提供模板下载
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import yaml
import os

router = APIRouter(prefix="/materials", tags=["企业资料管理"])

# 加载行业配置
CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "industry_config.yaml"

# 模板文件根目录
TEMPLATE_ROOT = Path(__file__).parent.parent.parent.parent / "download_templates"


def load_industry_config():
    """加载行业配置"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


# ============ 模板文件映射 ============

# 模板名称 -> 文件路径映射（相对于 TEMPLATE_ROOT）
TEMPLATE_FILE_MAPPING = {
    # === 人事类 ===
    "员工花名册": "人事类/员工花名册模板.xlsx",
    "劳动合同": "人事类/劳动合同模板.docx",
    "社保缴纳证明": None,  # 社保局出具，无模板
    "员工体检报告": None,  # 医院出具，无模板
    "设计开发人员能力要求": "人事类/设计开发人员能力要求模板.docx",
    "销售人员任职要求": "人事类/销售人员任职要求模板.docx",
    "管理者代表任命书": "人事类/管理者代表任命书模板.docx",
    "内审员名单": "人事类/内审员名单模板.xlsx",
    "关键岗位人员清单": "人事类/关键岗位人员清单模板.xlsx",
    "保安员证": None,  # 政府颁发
    "消防员证": None,  # 政府颁发
    "电梯安全管理员证": None,  # 政府颁发
    "电工证": None,  # 政府颁发

    # === 场地类 ===
    "场地租赁合同或产权证明": "场地类/场地租赁合同模板.docx",
    "场地租赁合同": "场地类/场地租赁合同模板.docx",
    "办公场地证明": "场地类/办公场地证明模板.docx",
    "研发场地照片": None,  # 需实地拍摄
    "办公场所照片": None,  # 需实地拍摄
    "仓库照片": None,  # 需实地拍摄
    "在管项目照片": None,  # 需实地拍摄

    # === 业务类 ===
    "产品/服务清单": "业务类/产品服务清单模板.xlsx",
    "软件产品清单": "业务类/软件产品清单模板.xlsx",
    "销售产品清单": "业务类/销售产品清单模板.xlsx",
    "设备清单": "业务类/设备清单模板.xlsx",
    "服务项目清单": "业务类/服务项目清单模板.xlsx",
    "设计开发项目案例": "业务类/设计开发项目案例模板.docx",
    "软件著作权或专利证书": None,  # 政府颁发
    "软件销售合同": "业务类/销售合同模板.docx",
    "软件采购合同": "业务类/采购合同模板.docx",
    "设备销售合同": "业务类/销售合同模板.docx",
    "设备采购合同": "业务类/采购合同模板.docx",
    "物业服务合同": "业务类/物业服务合同模板.docx",
    "外包服务合同": "业务类/外包服务合同模板.docx",
    "停车场经营许可证": None,  # 政府颁发
    "电梯维保合同": "业务类/电梯维保合同模板.docx",
    "消防维保合同": "业务类/消防维保合同模板.docx",

    # === 基础证照类 ===
    "营业执照": None,  # 工商局颁发
    "组织架构图": "基础类/组织架构图模板.pptx",

    # === 体系运行类 ===
    "管理体系运行情况说明": "体系类/管理体系运行情况说明模板.docx",
    "质量目标指标": "体系类/质量目标指标模板.docx",
    "环境目标指标": "体系类/环境目标指标模板.docx",
    "职业健康安全目标指标": "体系类/职业健康安全目标指标模板.docx",
}


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
    template_file: Optional[str] = None


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
        template_file = TEMPLATE_FILE_MAPPING.get(material["name"])
        has_template = template_file is not None

        material_item = MaterialItem(
            name=material["name"],
            required=material["required"],
            description=material["description"],
            alert_level="critical" if material["required"] else "warning",
            template_available=has_template,
            template_name=f"{material['name']}模板" if has_template else None,
            template_file=template_file,
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
    """获取指定行业的完整材料清单（含模板下载信息）"""
    config = load_industry_config()
    industry = config.get("industries", {}).get(industry_code)
    common = config.get("common", {})

    if not industry:
        raise HTTPException(status_code=404, detail="行业不存在")

    # 构建材料清单，附加模板信息
    industry_materials = {}
    for category, materials in industry.get("required_company_materials", {}).items():
        category_items = []
        for material in materials:
            template_file = TEMPLATE_FILE_MAPPING.get(material["name"])
            category_items.append({
                "name": material["name"],
                "required": material["required"],
                "description": material["description"],
                "template_available": template_file is not None,
                "template_file": template_file,
            })
        industry_materials[category] = category_items

    common_materials = {}
    for category, materials in common.get("required_materials", {}).items():
        category_items = []
        for material in materials:
            template_file = TEMPLATE_FILE_MAPPING.get(material["name"])
            category_items.append({
                "name": material["name"],
                "required": material["required"],
                "description": material.get("description", ""),
                "template_available": template_file is not None,
                "template_file": template_file,
            })
        common_materials[category] = category_items

    return {
        "industry_code": industry_code,
        "industry_name": industry.get("name"),
        "materials": {
            "industry_specific": industry_materials,
            "common": common_materials,
        },
    }


@router.get("/templates/downloadable", summary="获取可下载的模板列表")
async def get_downloadable_templates(industry_code: Optional[str] = None):
    """获取所有可下载的模板文件列表"""
    config = load_industry_config()

    # 收集该行业所有需要的材料名称
    material_names = set()

    if industry_code:
        industry = config.get("industries", {}).get(industry_code)
        if not industry:
            raise HTTPException(status_code=404, detail="行业不存在")
        for category, materials in industry.get("required_company_materials", {}).items():
            for material in materials:
                material_names.add(material["name"])

    # 通用材料
    common = config.get("common", {})
    for category, materials in common.get("required_materials", {}).items():
        for material in materials:
            material_names.add(material["name"])

    # 筛选出有模板的材料
    downloadable = []
    for name in material_names:
        template_file = TEMPLATE_FILE_MAPPING.get(name)
        if template_file:
            downloadable.append({
                "material_name": name,
                "template_file": template_file,
                "download_url": f"/api/v1/materials/template/download/{name}",
            })

    return {
        "industry_code": industry_code,
        "total": len(downloadable),
        "templates": downloadable,
    }


@router.get("/template/download/{material_name}", summary="下载材料模板文件")
async def download_template_file(material_name: str):
    """下载指定材料的空白模板文件（真实文件下载）"""
    template_file = TEMPLATE_FILE_MAPPING.get(material_name)

    if not template_file:
        raise HTTPException(
            status_code=404,
            detail=f"该材料（{material_name}）无需模板，请直接提供原件或扫描件"
        )

    file_path = TEMPLATE_ROOT / template_file

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"模板文件暂未上传，请联系管理员"
        )

    # 确定文件类型
    suffix = file_path.suffix.lower()
    media_types = {
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".pdf": "application/pdf",
    }

    media_type = media_types.get(suffix, "application/octet-stream")

    return FileResponse(
        path=str(file_path),
        filename=f"{material_name}模板{suffix}",
        media_type=media_type,
    )


@router.post("/template/download", summary="下载材料模板（POST方式）")
async def download_template_post(request: TemplateDownloadRequest):
    """下载指定材料的填写模板（POST方式，返回下载信息）"""
    template_file = TEMPLATE_FILE_MAPPING.get(request.material_name)

    if not template_file:
        raise HTTPException(
            status_code=404,
            detail=f"该材料（{request.material_name}）无需模板，请直接提供原件或扫描件"
        )

    file_path = TEMPLATE_ROOT / template_file

    if not file_path.exists():
        return {
            "material_name": request.material_name,
            "template_available": True,
            "template_file": template_file,
            "file_exists": False,
            "message": "模板文件暂未上传，请联系管理员",
            "download_url": None,
        }

    return {
        "material_name": request.material_name,
        "template_available": True,
        "template_file": template_file,
        "file_exists": True,
        "message": f"{request.material_name}模板已就绪",
        "download_url": f"/api/v1/materials/template/download/{request.material_name}",
    }


@router.get("/workflow", summary="获取材料准备流程")
async def get_materials_workflow():
    """获取材料准备的完整流程"""
    return {
        "workflow": [
            {
                "step": 1,
                "title": "选择行业",
                "description": "根据企业经营范围选择对应的行业类型",
            },
            {
                "step": 2,
                "title": "查看材料清单",
                "description": "系统自动列出该行业所需的全部材料",
            },
            {
                "step": 3,
                "title": "下载空白模板",
                "description": "对于有模板的材料，可直接下载空白模板填写",
            },
            {
                "step": 4,
                "title": "准备并上传材料",
                "description": "将填写完成的模板或其他材料上传到系统",
            },
            {
                "step": 5,
                "title": "材料完整性检查",
                "description": "系统自动检查材料是否齐全",
            },
            {
                "step": 6,
                "title": "生成体系文件",
                "description": "材料齐全后，系统自动生成全套体系文件",
            },
        ],
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
            template_file = TEMPLATE_FILE_MAPPING.get(material["name"])
            checklist["items"].append({
                "category": category,
                "material_name": material["name"],
                "required": material["required"],
                "description": material["description"],
                "status": "已提供" if material["name"] in request.uploaded_materials else "待补充",
                "has_template": template_file is not None,
                "template_file": template_file,
            })

    return checklist
