#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档生成器 - 基类和通用工具

包含：
1. 枚举定义（文件级别、标准类型等）
2. 企业信息模型
3. 生成的文档模型
4. 变量管理器
5. 模板引擎
6. 生成器基类
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import re


# ============================================================
# 枚举定义
# ============================================================

class FileLevel(Enum):
    """文件层级"""
    LEVEL_1 = "level_1"  # 一级文件（管理手册）
    LEVEL_2 = "level_2"  # 二级文件（程序文件）
    LEVEL_3 = "level_3"  # 三级文件（作业指导书/制度）
    LEVEL_4 = "level_4"  # 四级文件（记录表格）


class StandardType(Enum):
    """标准类型"""
    ISO9001 = "iso9001"  # 质量管理体系
    ISO14001 = "iso14001"  # 环境管理体系
    ISO45001 = "iso45001"  # 职业健康安全
    QES = "qes"  # 三体系一体化


class DocumentType(Enum):
    """文档类型"""
    # 一级
    MANUAL = "manual"  # 管理手册
    
    # 二级
    PROCEDURE = "procedure"  # 程序文件
    
    # 三级
    REGULATION = "regulation"  # 管理制度
    INSTRUCTION = "instruction"  # 操作规程
    
    # 四级
    FORM = "form"  # 记录表格
    PLAN = "plan"  # 年度计划
    REPORT = "report"  # 审核/评审报告
    RECORD = "record"  # 台账/清单


# ============================================================
# 数据模型
# ============================================================

@dataclass
class CompanyInfo:
    """企业信息"""
    # 基本信息
    company_name: str = ""  # 公司名称
    company_code: str = ""  # 公司代号（如BDC）
    industry: str = ""  # 行业
    sub_industry: str = ""  # 细分行业
    employee_count: int = 0  # 员工人数
    office_area_sqm: float = 0  # 办公面积
    
    # 认证信息
    certification_type: str = "初次认证"  # 初次认证/监督审核/再认证
    existing_standards: List[str] = field(default_factory=list)  # 已有标准
    target_standards: List[str] = field(default_factory=list)  # 目标标准
    
    # 组织信息
    departments: List[str] = field(default_factory=list)  # 部门列表
    main_equipment: List[str] = field(default_factory=list)  # 主要设备
    main_processes: List[str] = field(default_factory=list)  # 主要过程
    special_processes: List[str] = field(default_factory=list)  # 特殊过程
    
    # 目标和指标
    quality_goals: str = ""  # 质量目标
    environment_goals: str = ""  # 环境目标
    safety_goals: str = ""  # 安全目标
    
    # 地址和联系方式
    address: str = ""  # 地址
    legal_representative: str = ""  # 法定代表人
    contact_person: str = ""  # 联系人
    contact_phone: str = ""  # 联系电话
    
    # 管理者代表
    management_representative: str = ""
    
    # 文件信息
    file_version: str = "A/0"  # 文件版本
    effective_date: str = ""  # 生效日期
    release_date: str = ""  # 发布日期
    
    def get_full_year(self) -> str:
        """获取当前年份字符串"""
        return datetime.now().strftime("%Y")
    
    def get_full_date(self) -> str:
        """获取当前日期字符串"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_chinese_date(self) -> str:
        """获取中文日期格式"""
        return datetime.now().strftime("%Y年%m月%d日")
    
    def to_variables(self) -> Dict[str, str]:
        """转换为变量字典"""
        return {
            "{{公司名称}}": self.company_name,
            "{{公司代号}}": self.company_code,
            "{{行业}}": self.industry,
            "{{员工人数}}": str(self.employee_count),
            "{{办公面积}}": str(self.office_area_sqm),
            "{{认证类型}}": self.certification_type,
            "{{目标标准}}": "、".join(self.target_standards) if self.target_standards else "",
            "{{部门列表}}": "、".join(self.departments) if self.departments else "",
            "{{主要设备}}": "、".join(self.main_equipment) if self.main_equipment else "",
            "{{主要过程}}": "、".join(self.main_processes) if self.main_processes else "",
            "{{质量目标}}": self.quality_goals,
            "{{环境目标}}": self.environment_goals,
            "{{安全目标}}": self.safety_goals,
            "{{地址}}": self.address,
            "{{法定代表人}}": self.legal_representative,
            "{{联系人}}": self.contact_person,
            "{{联系电话}}": self.contact_phone,
            "{{管理者代表}}": self.management_representative,
            "{{文件版本}}": self.file_version,
            "{{生效日期}}": self.effective_date or self.get_chinese_date(),
            "{{发布日期}}": self.release_date or self.get_chinese_date(),
            "{{年份}}": self.get_full_year(),
            "{{日期}}": self.get_full_date(),
        }


@dataclass
class GeneratedDocument:
    """生成的文档"""
    file_level: FileLevel
    document_type: DocumentType
    file_code: str  # 文件编号
    file_name: str  # 文件名称
    title: str  # 文档标题
    content: str  # 内容
    standards: List[str] = field(default_factory=list)  # 涉及的标准
    related_clauses: List[str] = field(default_factory=list)  # 相关条款
    required_records: List[str] = field(default_factory=list)  # 产生的记录
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_level": self.file_level.value,
            "document_type": self.document_type.value,
            "file_code": self.file_code,
            "file_name": self.file_name,
            "title": self.title,
            "content": self.content,
            "standards": self.standards,
            "related_clauses": self.related_clauses,
            "required_records": self.required_records,
            "created_at": self.created_at.isoformat(),
        }


# ============================================================
# 变量管理器
# ============================================================

class VariableManager:
    """变量管理器 - 处理模板变量替换"""
    
    def __init__(self):
        self.variables: Dict[str, str] = {}
        self.custom_variables: Dict[str, str] = {}
    
    def add_variables(self, variables: Dict[str, str]):
        """添加变量"""
        self.variables.update(variables)
    
    def add_custom(self, key: str, value: str):
        """添加自定义变量"""
        self.custom_variables[key] = value
    
    def replace(self, content: str) -> str:
        """替换内容中的变量"""
        # 合并所有变量
        all_vars = {**self.variables, **self.custom_variables}
        
        result = content
        for key, value in all_vars.items():
            result = result.replace(key, value)
        
        return result
    
    def replace_company_info(self, company_info: CompanyInfo):
        """从企业信息填充变量"""
        self.add_variables(company_info.to_variables())


# ============================================================
# 模板引擎
# ============================================================

class TemplateEngine:
    """模板引擎 - 渲染文档内容"""
    
    def __init__(self):
        self.variable_manager = VariableManager()
    
    def render(self, template: str, company_info: CompanyInfo, **kwargs) -> str:
        """
        渲染模板
        
        Args:
            template: 模板字符串
            company_info: 企业信息
            **kwargs: 其他变量
            
        Returns:
            渲染后的内容
        """
        # 填充企业信息变量
        self.variable_manager.replace_company_info(company_info)
        
        # 添加自定义变量
        for key, value in kwargs.items():
            self.variable_manager.add_custom(f"{{{{{key}}}}}", str(value))
        
        # 执行替换
        return self.variable_manager.replace(template)
    
    def render_table_cell(self, cells: List[str]) -> str:
        """渲染表格单元格"""
        return " | ".join(cells)
    
    def render_list(self, items: List[str], numbered: bool = False) -> str:
        """渲染列表"""
        if numbered:
            return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
        return "\n".join(f"- {item}" for item in items)


# ============================================================
# 基类
# ============================================================

class BaseGenerator:
    """
    文档生成器基类
    
    所有层级的生成器都应继承此类
    """
    
    def __init__(self, company_info: CompanyInfo):
        self.company_info = company_info
        self.template_engine = TemplateEngine()
    
    def generate(self) -> GeneratedDocument:
        """
        生成文档 - 子类必须实现
        
        Returns:
            生成的文档
        """
        raise NotImplementedError("子类必须实现generate方法")
    
    def render(self, template: str, **kwargs) -> str:
        """渲染模板的便捷方法"""
        return self.template_engine.render(template, self.company_info, **kwargs)
    
    def get_file_code(self, prefix: str, seq: int, suffix: str = "") -> str:
        """
        生成文件编号
        
        Args:
            prefix: 前缀（如BDC-QESMS）
            seq: 序号
            suffix: 后缀（如A表示
            
        Returns:
            文件编号字符串
        """
        if suffix:
            return f"{prefix}-{seq:03d}{suffix}"
        return f"{prefix}-{seq:03d}"
    
    def get_procedure_file_code(self, seq: int, suffix: str = "") -> str:
        """生成程序文件编号"""
        return self.get_file_code(
            f"{self.company_info.company_code}-QESMS-B",
            seq,
            suffix
        )
    
    def get_level3_file_code(self, seq: int, suffix: str = "") -> str:
        """生成三级文件编号"""
        return self.get_file_code(
            f"{self.company_info.company_code}-QESMS-C",
            seq,
            suffix
        )
    
    def get_level4_file_code(self, seq: int, suffix: str = "") -> str:
        """生成四级文件编号"""
        return self.get_file_code(
            f"{self.company_info.company_code}-QESMS-D",
            seq,
            suffix
        )
