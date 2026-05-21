#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - Excel上传解析模块
解析用户上传的Excel收集表，提取企业信息
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

import pandas as pd


# Excel收集表字段映射
# key: Excel中的列名（支持多种写法）
# value: 标准化后的字段名
FIELD_MAPPING = {
    # 公司基本信息
    "公司名称": "company_name",
    "企业名称": "company_name",
    "单位名称": "company_name",
    "名称": "company_name",
    
    # 行业
    "行业": "industry",
    "行业类型": "industry",
    "所属行业": "industry",
    
    # 员工人数
    "员工人数": "employee_count",
    "人数": "employee_count",
    "在册人数": "employee_count",
    
    # 办公面积
    "办公面积": "office_area",
    "面积": "office_area",
    "建筑面积": "office_area",
    
    # 地址
    "地址": "address",
    "公司地址": "address",
    "办公地址": "address",
    
    # 法人
    "法定代表人": "legal_representative",
    "法人": "legal_representative",
    
    # 联系人
    "联系人": "contact_person",
    
    # 联系电话
    "联系电话": "contact_phone",
    "电话": "contact_phone",
    "手机": "contact_phone",
    
    # 部门
    "部门": "departments",
    "部门设置": "departments",
    "组织架构": "departments",
    
    # 设备
    "设备": "main_equipment",
    "设备清单": "main_equipment",
    "主要设备": "main_equipment",
    
    # 主要过程
    "主要过程": "main_processes",
    "业务流程": "main_processes",
    "核心流程": "main_processes",
    
    # 认证类型
    "认证类型": "certification_type",
    "审核类型": "certification_type",
    
    # 目标标准
    "认证标准": "target_standards",
    "目标标准": "target_standards",
    "申请标准": "target_standards",
}


def parse_excel_file(file_path: str) -> Dict[str, Any]:
    """
    解析Excel收集表文件
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        解析出的企业信息字典
        
    Raises:
        ValueError: 文件格式不支持或解析失败
    """
    path = Path(file_path)
    
    if not path.exists():
        raise ValueError(f"文件不存在: {file_path}")
    
    suffix = path.suffix.lower()
    if suffix not in [".xlsx", ".xls", ".csv"]:
        raise ValueError(f"不支持的文件格式: {suffix}，仅支持 .xlsx/.xls/.csv")
    
    try:
        if suffix == ".csv":
            df = pd.read_csv(file_path, encoding="utf-8-sig")
        else:
            df = pd.read_excel(file_path, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"文件读取失败: {str(e)}")
    
    return _extract_from_dataframe(df)


def _extract_from_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    从DataFrame中提取企业信息
    
    支持两种Excel格式：
    1. 两列格式：第一列为字段名，第二列为值
    2. 表头格式：第一行为列名，后续行为数据
    """
    result: Dict[str, Any] = {}
    
    # 尝试格式1：两列格式（字段名 | 值）
    if len(df.columns) >= 2:
        col0_name = str(df.columns[0]).strip()
        col1_name = str(df.columns[1]).strip()
        
        # 检测是否为"项目 | 内容"格式
        if any(kw in col0_name for kw in ["项目", "名称", "字段", "内容项"]) or \
           any(kw in col1_name for kw in ["内容", "值", "填写", "信息"]):
            result = _parse_two_column_format(df)
            if result:
                return result
    
    # 尝试格式2：表头格式
    result = _parse_header_format(df)
    if result:
        return result
    
    # 尝试格式3：逐行扫描
    result = _parse_row_scan(df)
    return result


def _parse_two_column_format(df: pd.DataFrame) -> Dict[str, Any]:
    """解析两列格式（字段名 | 值）"""
    result = {}
    
    for _, row in df.iterrows():
        field_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        field_value = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        
        if not field_name or field_name == "nan":
            continue
        
        # 匹配字段
        standardized = _match_field(field_name)
        if standardized:
            result[standardized] = _convert_value(standardized, field_value)
    
    return result


def _parse_header_format(df: pd.DataFrame) -> Dict[str, Any]:
    """解析表头格式"""
    result = {}
    
    for col in df.columns:
        col_str = str(col).strip()
        standardized = _match_field(col_str)
        
        if standardized:
            # 取第一行非空值
            for val in df[col]:
                if pd.notna(val) and str(val).strip() and str(val).strip() != "nan":
                    result[standardized] = _convert_value(standardized, str(val).strip())
                    break
    
    return result


def _parse_row_scan(df: pd.DataFrame) -> Dict[str, Any]:
    """逐行扫描，查找包含已知字段的行"""
    result = {}
    
    for _, row in df.iterrows():
        for col in df.columns:
            cell_str = str(row[col]).strip() if pd.notna(row[col]) else ""
            if not cell_str or cell_str == "nan":
                continue
            
            standardized = _match_field(cell_str)
            if standardized and standardized not in result:
                # 取同行下一列的值
                col_idx = list(df.columns).index(col)
                if col_idx + 1 < len(df.columns):
                    next_val = row.iloc[col_idx + 1]
                    if pd.notna(next_val):
                        result[standardized] = _convert_value(
                            standardized, str(next_val).strip()
                        )
    
    return result


def _match_field(raw_name: str) -> Optional[str]:
    """匹配字段名到标准化字段"""
    raw = raw_name.strip()
    
    for excel_name, standard_name in FIELD_MAPPING.items():
        if excel_name in raw or raw in excel_name:
            return standard_name
    
    return None


def _convert_value(field_name: str, value: str) -> Any:
    """转换字段值到正确类型"""
    if not value or value in ["nan", "无", "无", "/", "-"]:
        return None
    
    value = value.strip()
    
    # 数字类型
    if field_name in ["employee_count"]:
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    if field_name in ["office_area"]:
        try:
            return float(value.replace("㎡", "").replace("平方米", "").replace("平", "").strip())
        except (ValueError, TypeError):
            return None
    
    # 列表类型
    if field_name in ["departments", "main_equipment", "main_processes", "target_standards"]:
        # 支持多种分隔符
        for sep in ["、", "，", ",", "\n", ";"]:
            if sep in value:
                return [item.strip() for item in value.split(sep) if item.strip()]
        return [value]
    
    # 认证标准特殊处理
    if field_name == "target_standards":
        standards = []
        if "9001" in value:
            standards.append("ISO9001")
        if "14001" in value:
            standards.append("ISO14001")
        if "45001" in value:
            standards.append("ISO45001")
        return standards if standards else [value]
    
    # 认证类型
    if field_name == "certification_type":
        if "监督" in value:
            return "监督审核"
        elif "再认证" in value or "复评" in value:
            return "再认证"
        elif "转" in value:
            return "转换认证"
        else:
            return "初次认证"
    
    return value


def get_excel_template_fields() -> List[Dict[str, str]]:
    """获取Excel收集表支持的字段列表"""
    fields = []
    seen = set()
    
    for excel_name, standard_name in FIELD_MAPPING.items():
        if standard_name not in seen:
            fields.append({
                "excel_column": excel_name,
                "field_name": standard_name,
                "required": standard_name in ["company_name"],
            })
            seen.add(standard_name)
    
    return fields
