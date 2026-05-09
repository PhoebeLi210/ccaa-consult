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
    
    Args:
        content: 需要替换的内容（字符串、字典、列表）
        variables: 变量字典
        
    Returns:
        替换后的内容
    """
    if isinstance(content, str):
        # 使用正则表达式替换 {{variable}} 格式的变量
        def replace_match(match):
            var_name = match.group(1).strip()
            return str(variables.get(var_name, match.group(0)))
        
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
    
    Args:
        template_data: 模板数据
        
    Returns:
        元数据字典
    """
    metadata = template_data.get("metadata", {})
    return {
        "name": metadata.get("name", ""),
        "code": metadata.get("code", ""),
        "level": metadata.get("level", 0),
        "industry": metadata.get("industry"),  # 行业标记
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
