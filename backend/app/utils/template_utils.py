#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 模板工具函数
提供模板加载、变量替换等通用功能
"""

import yaml
import re
from pathlib import Path
from typing import Any, Dict, Optional, List


def replace_variables(content: Any, variables: Dict[str, Any]) -> Any:
    """
    递归替换内容中的变量占位符
    
    支持英文和中文变量名，英文变量名会自动映射到中文变量名进行查找。
    
    Args:
        content: 需要替换的内容（字符串、字典、列表）
        variables: 变量字典
        
    Returns:
        替换后的内容
    """
    # 英文变量名到中文变量名的映射
    EN_TO_CN_VAR_MAP = {
        "company_code": "公司代号",
        "company_name": "公司名称",
        "legal_representative": "法定代表人",
        "established_date": "成立日期",
        "registered_address": "注册地址",
        "business_scope": "经营范围",
        "office_address": "办公地址",
        "issue_date": "发布日期",
        "implementation_date": "生效日期",
        "company_introduction": "公司简介",
        "general_manager": "总经理",
        "sign_date": "签署日期",
        "management_representative": "管理者代表",
        "employee_representative": "员工代表",
        "industry": "行业",
        "employee_count": "员工人数",
        "office_area_sqm": "办公面积",
        "certification_type": "认证类型",
        "address": "地址",
        "contact_person": "联系人",
        "contact_phone": "联系电话",
        "file_version": "文件版本",
        "year": "年份",
        "date": "日期",
        "target_standards": "目标标准",
        "departments": "部门列表",
        "main_equipment": "主要设备",
        "main_processes": "主要过程",
        "quality_goals": "质量目标",
        "environment_goals": "环境目标",
        "safety_goals": "安全目标",
    }

    if isinstance(content, str):
        # 使用正则表达式替换 {{variable}} 格式的变量
        def replace_match(match):
            var_name = match.group(1).strip()

            # 直接查找
            if var_name in variables:
                return str(variables[var_name])

            # 英文→中文映射查找
            cn_name = EN_TO_CN_VAR_MAP.get(var_name)
            if cn_name and cn_name in variables:
                return str(variables[cn_name])

            # 带{{}}包裹的中文键名查找
            if f"{{{{{var_name}}}}}" in variables:
                return str(variables[f"{{{{{var_name}}}}}"])
            if cn_name and f"{{{{{cn_name}}}}}" in variables:
                return str(variables[f"{{{{{cn_name}}}}}"])

            # 未找到，保留原始占位符
            return match.group(0)

        return re.sub(r'\{\{\s*([^}]+)\s*\}\}', replace_match, content)

    elif isinstance(content, dict):
        return {k: replace_variables(v, variables) for k, v in content.items()}

    elif isinstance(content, list):
        return [replace_variables(item, variables) for item in content]

    return content


def load_yaml_template(template_path: Path) -> Optional[Dict[str, Any]]:
    """
    加载YAML模板文件
    
    Args:
        template_path: 模板文件路径
        
    Returns:
        模板数据字典，加载失败返回None
    """
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载模板失败 {template_path}: {e}")
        return None


def find_template_file(template_id: str, template_dir: Path) -> Optional[Path]:
    """
    在模板目录中查找模板文件
    
    Args:
        template_id: 模板ID（文件名，不含扩展名）
        template_dir: 模板根目录
        
    Returns:
        模板文件路径，未找到返回None
    """
    if not template_dir.exists():
        return None
    
    # 在所有层级目录中查找
    for level_dir in template_dir.iterdir():
        if not level_dir.is_dir():
            continue
        
        candidate = level_dir / f"{template_id}.yaml"
        if candidate.exists():
            return candidate
    
    return None


def get_template_metadata(template_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取模板元数据
    
    兼容两种模板格式：
    1. metadata格式：顶层有 metadata: 键
    2. document_info格式：顶层有 document_info: 键
    
    Args:
        template_data: 模板数据
        
    Returns:
        元数据字典
    """
    # 优先从 metadata 读取
    metadata = template_data.get("metadata", {})
    
    # 如果 metadata 为空，尝试从 document_info 读取
    if not metadata:
        doc_info = template_data.get("document_info", {})
        if doc_info:
            metadata = {
                "name": doc_info.get("title", doc_info.get("name", "")),
                "code": doc_info.get("file_code", doc_info.get("code", "")),
                "level": doc_info.get("level", 0),
                "industry": doc_info.get("industry"),
                "version": doc_info.get("version", "A/0"),
                "standard": doc_info.get("standard", ""),
                "department": doc_info.get("department", ""),
            }
    
    return {
        "name": metadata.get("name", ""),
        "code": metadata.get("code", ""),
        "level": metadata.get("level", 0),
        "industry": metadata.get("industry"),
        "version": metadata.get("version", "A/0"),
        "standard": metadata.get("standard", ""),
        "department": metadata.get("department", ""),
    }


def filter_templates_by_industry(
    template_files: List[Path], 
    industry_code: Optional[str] = None
) -> List[Path]:
    """
    根据行业代码过滤模板文件
    
    Args:
        template_files: 模板文件路径列表
        industry_code: 行业代码，None表示返回所有通用模板
        
    Returns:
        过滤后的模板文件路径列表
    """
    filtered = []
    
    for template_file in template_files:
        template_data = load_yaml_template(template_file)
        if not template_data:
            continue
        
        metadata = get_template_metadata(template_data)
        template_industry = metadata.get("industry")
        
        # 如果模板没有行业标记，说明是通用模板，所有行业都适用
        if template_industry is None:
            filtered.append(template_file)
            continue
        
        # 如果指定了行业代码，只返回匹配该行业的模板
        if industry_code and template_industry == industry_code:
            filtered.append(template_file)
    
    return filtered


def get_all_templates(template_dir: Path) -> List[Path]:
    """
    获取所有模板文件
    
    Args:
        template_dir: 模板根目录
        
    Returns:
        所有模板文件路径列表
    """
    templates = []
    
    if not template_dir.exists():
        return templates
    
    for level_dir in template_dir.iterdir():
        if not level_dir.is_dir():
            continue
        
        for template_file in level_dir.glob("*.yaml"):
            templates.append(template_file)
    
    return templates
