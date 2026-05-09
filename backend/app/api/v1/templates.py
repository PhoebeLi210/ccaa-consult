#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 模板API接口
提供模板列表、详情、变量解析等功能
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import yaml

from app.core.constants import TEMPLATE_DIR

router = APIRouter(prefix="/templates", tags=["模板管理"])


class TemplateListResponse(BaseModel):
    """模板列表响应"""
    total: int
    templates: List[Dict[str, Any]]


class TemplateDetailResponse(BaseModel):
    """模板详情响应"""
    template_id: str
    name: str
    document_level: str
    document_code: Optional[str] = None
    version: str
    variables: List[Dict[str, Any]]
    content: Optional[Dict[str, Any]] = None


class VariableResolveRequest(BaseModel):
    """变量解析请求"""
    template_id: str
    company_info: Dict[str, Any]
    additional_vars: Optional[Dict[str, Any]] = None


class VariableResolveResponse(BaseModel):
    """变量解析响应"""
    resolved_variables: Dict[str, Any]
    missing_variables: List[Dict[str, Any]]


class RenderPreviewRequest(BaseModel):
    """渲染预览请求"""
    template_id: str
    company_info: Dict[str, Any]
    additional_vars: Optional[Dict[str, Any]] = None


class RenderPreviewResponse(BaseModel):
    """渲染预览响应"""
    content: str
    template_id: str
    document_name: str


@router.get("/levels", summary="获取文档层级列表")
async def get_document_levels():
    """获取所有文档层级"""
    levels = [
        {"code": "一级文件", "name": "管理手册", "description": "一级文件，体系纲领性文件"},
        {"code": "二级文件", "name": "程序文件", "description": "二级文件，描述过程控制方法"},
        {"code": "三级文件", "name": "作业指导书", "description": "三级文件，具体操作规程"},
        {"code": "四级文件", "name": "记录表格", "description": "四级文件，记录表单"},
    ]
    return {"levels": levels}


@router.get("/standards", summary="获取标准类型列表")
async def get_standards():
    """获取所有标准类型"""
    standards = [
        {"code": "ISO9001", "name": "质量管理体系", "full_name": "GB/T 19001-2016 idt ISO 9001:2015"},
        {"code": "ISO14001", "name": "环境管理体系", "full_name": "GB/T 24001-2016 idt ISO 14001:2015"},
        {"code": "ISO45001", "name": "职业健康安全管理体系", "full_name": "GB/T 45001-2020 idt ISO 45001:2018"},
        {"code": "INTEGRATED", "name": "三标一体", "full_name": "质量/环境/职业健康安全三标一体"},
    ]
    return {"standards": standards}


@router.get("/list", response_model=TemplateListResponse, summary="获取模板列表")
async def list_templates(
    level: Optional[str] = Query(None, description="文档层级"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
):
    """获取模板列表"""
    templates = []
    
    if TEMPLATE_DIR.exists():
        for level_dir in TEMPLATE_DIR.iterdir():
            if not level_dir.is_dir():
                continue
            
            level_name = level_dir.name
            if level and level_name != level:
                continue
            
            for template_file in level_dir.glob("*.yaml"):
                try:
                    with open(template_file, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                    
                    if not data:
                        continue
                    
                    doc_info = data.get("document_info", {})
                    name = doc_info.get("document_name", template_file.stem)
                    
                    if keyword and keyword.lower() not in name.lower():
                        continue
                    
                    templates.append({
                        "template_id": template_file.stem,
                        "name": name,
                        "document_level": level_name,
                        "document_code": doc_info.get("document_code", ""),
                        "version": doc_info.get("version", "A/0"),
                    })
                except Exception as e:
                    continue
    
    return TemplateListResponse(total=len(templates), templates=templates)


@router.get("/{template_id}", response_model=TemplateDetailResponse, summary="获取模板详情")
async def get_template_detail(template_id: str):
    """获取模板详情"""
    template_file = None
    for level_dir in TEMPLATE_DIR.iterdir():
        if not level_dir.is_dir():
            continue
        candidate = level_dir / f"{template_id}.yaml"
        if candidate.exists():
            template_file = candidate
            break
    
    if not template_file:
        raise HTTPException(status_code=404, detail=f"模板不存在: {template_id}")
    
    try:
        with open(template_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        doc_info = data.get("document_info", {})
        variables = []
        for var_name, var_data in data.get("variables", {}).items():
            variables.append({
                "name": var_name,
                "description": var_data.get("description", ""),
                "example": var_data.get("example", ""),
            })
        
        return TemplateDetailResponse(
            template_id=template_id,
            name=doc_info.get("document_name", ""),
            document_level=doc_info.get("document_type", ""),
            document_code=doc_info.get("document_code", ""),
            version=doc_info.get("version", "A/0"),
            variables=variables,
            content=data.get("content", data.get("form_structure", {})),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取模板失败: {str(e)}")


@router.post("/resolve-variables", response_model=VariableResolveResponse, summary="解析模板变量")
async def resolve_variables(request: VariableResolveRequest):
    """解析模板变量"""
    template_file = None
    for level_dir in TEMPLATE_DIR.iterdir():
        if not level_dir.is_dir():
            continue
        candidate = level_dir / f"{request.template_id}.yaml"
        if candidate.exists():
            template_file = candidate
            break
    
    if not template_file:
        raise HTTPException(status_code=404, detail=f"模板不存在: {request.template_id}")
    
    try:
        with open(template_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        resolved = {}
        missing = []
        
        for var_name, var_data in data.get("variables", {}).items():
            value = request.company_info.get(var_name)
            if not value:
                value = request.additional_vars.get(var_name) if request.additional_vars else None
            
            if value:
                resolved[var_name] = value
            else:
                missing.append({
                    "name": var_name,
                    "description": var_data.get("description", ""),
                    "example": var_data.get("example", ""),
                })
        
        return VariableResolveResponse(
            resolved_variables=resolved,
            missing_variables=missing,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析变量失败: {str(e)}")


@router.post("/preview", summary="预览渲染结果")
async def preview_render(request: RenderPreviewRequest):
    """预览模板渲染结果"""
    template_file = None
    for level_dir in TEMPLATE_DIR.iterdir():
        if not level_dir.is_dir():
            continue
        candidate = level_dir / f"{request.template_id}.yaml"
        if candidate.exists():
            template_file = candidate
            break
    
    if not template_file:
        raise HTTPException(status_code=404, detail=f"模板不存在: {request.template_id}")
    
    try:
        with open(template_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        doc_info = data.get("document_info", {})
        content = data.get("content", data.get("form_structure", {}))
        
        def replace_vars(text, variables):
            if isinstance(text, str):
                for key, value in variables.items():
                    text = text.replace("{{" + key + "}}", str(value))
                return text
            elif isinstance(text, dict):
                return {k: replace_vars(v, variables) for k, v in text.items()}
            elif isinstance(text, list):
                return [replace_vars(item, variables) for item in text]
            return text
        
        all_vars = {**request.company_info}
        if request.additional_vars:
            all_vars.update(request.additional_vars)
        
        rendered_content = replace_vars(content, all_vars)
        
        import json
        content_str = json.dumps(rendered_content, ensure_ascii=False, indent=2)
        
        return {
            "content": content_str,
            "template_id": request.template_id,
            "document_name": doc_info.get("document_name", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"渲染预览失败: {str(e)}")


@router.get("/stats/summary", summary="获取模板统计")
async def get_template_stats():
    """获取模板统计信息"""
    stats = {
        "total": 0,
        "by_level": {},
    }
    
    if TEMPLATE_DIR.exists():
        for level_dir in TEMPLATE_DIR.iterdir():
            if not level_dir.is_dir():
                continue
            level_name = level_dir.name
            count = len(list(level_dir.glob("*.yaml")))
            stats["by_level"][level_name] = count
            stats["total"] += count
    
    return stats
