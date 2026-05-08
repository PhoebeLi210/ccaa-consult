#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 模板管理器
管理ISO体系文件模板，支持变量替换和内容渲染
"""
import os
import re
import json
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import yaml


class DocumentLevel(Enum):
    """文档层级"""
    LEVEL_1 = "一级文件"  # 管理手册
    LEVEL_2 = "二级文件"  # 程序文件
    LEVEL_3 = "三级文件"  # 作业指导书
    LEVEL_4 = "四级文件"  # 记录表格


class StandardType(Enum):
    """标准类型"""
    ISO9001 = "ISO9001"
    ISO14001 = "ISO14001"
    ISO45001 = "ISO45001"
    INTEGRATED = "INTEGRATED"  # 三标一体


@dataclass
class TemplateVariable:
    """模板变量定义"""
    name: str                           # 变量名，如 {{company_name}}
    description: str                    # 描述
    required: bool = True               # 是否必需
    default_value: Any = None           # 默认值
    data_type: str = "string"           # 数据类型: string, number, date, list, dict
    source: str = "company_info"        # 数据来源: company_info, user_input, generated
    example: Optional[str] = None       # 示例值


@dataclass
class TemplateSection:
    """模板章节"""
    id: str                             # 章节ID
    title: str                          # 章节标题
    content: str                        # 章节内容模板
    variables: List[str] = field(default_factory=list)  # 使用的变量
    ai_enhance: bool = False            # 是否需要AI增强
    ai_prompt: Optional[str] = None     # AI增强提示词
    required: bool = True               # 是否必需章节


@dataclass
class Template:
    """文档模板"""
    template_id: str                    # 模板ID
    name: str                           # 模板名称
    document_level: DocumentLevel       # 文档层级
    standard: Optional[StandardType]    # 适用标准
    industry: Optional[str] = None      # 适用行业（None表示通用）
    
    # 模板内容
    sections: List[TemplateSection] = field(default_factory=list)
    variables: Dict[str, TemplateVariable] = field(default_factory=dict)
    
    # 元数据
    description: Optional[str] = None
    version: str = "1.0"
    author: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # 文件信息
    file_path: Optional[str] = None     # 模板文件路径（.docx或.md）
    file_type: str = "markdown"         # markdown / docx


class TemplateLoader:
    """模板加载器"""
    
    def __init__(self, template_dir: str = "./templates"):
        self.template_dir = Path(template_dir)
        self._cache: Dict[str, Template] = {}
    
    def load(self, template_id: str) -> Optional[Template]:
        """加载模板"""
        if template_id in self._cache:
            return self._cache[template_id]
        
        # 查找模板文件
        template_path = self._find_template_file(template_id)
        if not template_path:
            return None
        
        # 根据文件类型加载
        if template_path.suffix == ".yaml" or template_path.suffix == ".yml":
            template = self._load_yaml_template(template_path)
        elif template_path.suffix == ".json":
            template = self._load_json_template(template_path)
        else:
            return None
        
        if template:
            self._cache[template_id] = template
        
        return template
    
    def load_by_type(
        self,
        document_level: DocumentLevel,
        standard: Optional[StandardType] = None,
        industry: Optional[str] = None
    ) -> List[Template]:
        """按类型加载模板列表"""
        templates = []
        
        # 遍历模板目录
        for level_dir in self.template_dir.iterdir():
            if not level_dir.is_dir():
                continue
            
            # 检查文档层级
            try:
                level = DocumentLevel(level_dir.name)
            except ValueError:
                continue
            
            if level != document_level:
                continue
            
            # 加载该层级下的所有模板
            for template_file in level_dir.rglob("*.yaml"):
                template = self._load_yaml_template(template_file)
                if template:
                    # 检查标准和行业匹配
                    if standard and template.standard and template.standard != standard:
                        continue
                    if industry and template.industry and template.industry != industry:
                        continue
                    templates.append(template)
        
        return templates
    
    def _find_template_file(self, template_id: str) -> Optional[Path]:
        """查找模板文件"""
        for ext in [".yaml", ".yml", ".json"]:
            for path in self.template_dir.rglob(f"{template_id}{ext}"):
                return path
        return None
    
    def _load_yaml_template(self, path: Path) -> Optional[Template]:
        """加载YAML格式模板"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return self._parse_template_data(data, str(path))
        except Exception as e:
            print(f"加载模板失败: {path}, 错误: {e}")
            return None
    
    def _load_json_template(self, path: Path) -> Optional[Template]:
        """加载JSON格式模板"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self._parse_template_data(data, str(path))
        except Exception as e:
            print(f"加载模板失败: {path}, 错误: {e}")
            return None
    
    def _parse_template_data(self, data: Dict, file_path: str) -> Template:
        """解析模板数据"""
        # 解析变量
        variables = {}
        for var_name, var_data in data.get("variables", {}).items():
            variables[var_name] = TemplateVariable(
                name=var_name,
                description=var_data.get("description", ""),
                required=var_data.get("required", True),
                default_value=var_data.get("default_value"),
                data_type=var_data.get("data_type", "string"),
                source=var_data.get("source", "company_info"),
                example=var_data.get("example"),
            )
        
        # 解析章节
        sections = []
        for section_data in data.get("sections", []):
            sections.append(TemplateSection(
                id=section_data.get("id", ""),
                title=section_data.get("title", ""),
                content=section_data.get("content", ""),
                variables=section_data.get("variables", []),
                ai_enhance=section_data.get("ai_enhance", False),
                ai_prompt=section_data.get("ai_prompt"),
                required=section_data.get("required", True),
            ))
        
        # 解析文档层级
        level_str = data.get("document_level", "一级文件")
        try:
            document_level = DocumentLevel(level_str)
        except ValueError:
            document_level = DocumentLevel.LEVEL_1
        
        # 解析标准类型
        standard = None
        if data.get("standard"):
            try:
                standard = StandardType(data["standard"])
            except ValueError:
                pass
        
        return Template(
            template_id=data.get("template_id", ""),
            name=data.get("name", ""),
            document_level=document_level,
            standard=standard,
            industry=data.get("industry"),
            sections=sections,
            variables=variables,
            description=data.get("description"),
            version=data.get("version", "1.0"),
            author=data.get("author"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            file_path=file_path,
            file_type=data.get("file_type", "markdown"),
        )


class VariableResolver:
    """变量解析器"""
    
    # 标准变量映射
    STANDARD_VARIABLES = {
        # 企业基础信息
        "{{company_name}}": "company_name",
        "{{company_name_en}}": "company_name_en",
        "{{unified_credit_code}}": "unified_credit_code",
        "{{legal_representative}}": "legal_representative",
        "{{registered_capital}}": "registered_capital",
        "{{establishment_date}}": "establishment_date",
        "{{business_scope}}": "business_scope",
        "{{address}}": "address",
        "{{office_address}}": "office_address",
        "{{contact_person}}": "contact_person",
        "{{contact_phone}}": "contact_phone",
        "{{email}}": "email",
        
        # 规模信息
        "{{industry}}": "industry",
        "{{sub_industry}}": "sub_industry",
        "{{employee_count}}": "employee_count",
        "{{office_area_sqm}}": "office_area_sqm",
        "{{production_area_sqm}}": "production_area_sqm",
        
        # 认证信息
        "{{certification_type}}": "certification_type",
        "{{existing_standards}}": "existing_standards",
        "{{target_standards}}": "target_standards",
        
        # 体系信息
        "{{quality_policy}}": "quality_policy",
        "{{quality_goals}}": "quality_goals",
        "{{environment_policy}}": "environment_policy",
        "{{safety_policy}}": "safety_policy",
        
        # 文档信息
        "{{doc_number}}": "doc_number",
        "{{version}}": "version",
        "{{issue_date}}": "issue_date",
        "{{effective_date}}": "effective_date",
        "{{controlled_status}}": "controlled_status",
        "{{review_date}}": "review_date",
        
        # 组织信息
        "{{departments}}": "departments",
        "{{positions}}": "positions",
        "{{responsibilities}}": "responsibilities",
        
        # 业务信息
        "{{main_products}}": "main_products",
        "{{main_processes}}": "main_processes",
        "{{main_equipment}}": "main_equipment",
        "{{key_customers}}": "key_customers",
        "{{key_suppliers}}": "key_suppliers",
        
        # 行业特定
        "{{special_processes}}": "special_processes",
        "{{hazard_factors}}": "hazard_factors",
        "{{environmental_factors}}": "environmental_factors",
    }
    
    def resolve(
        self,
        company_info: Dict[str, Any],
        template: Template,
        additional_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """解析模板变量"""
        resolved = {}
        
        # 合并数据源
        data = {**company_info}
        if additional_vars:
            data.update(additional_vars)
        
        # 解析每个变量
        for var_name, var_def in template.variables.items():
            # 获取变量值
            value = self._get_variable_value(var_name, var_def, data)
            resolved[var_name] = value
        
        return resolved
    
    def _get_variable_value(
        self,
        var_name: str,
        var_def: TemplateVariable,
        data: Dict[str, Any]
    ) -> Any:
        """获取变量值"""
        # 1. 尝试从数据中获取
        if var_name in self.STANDARD_VARIABLES:
            field_name = self.STANDARD_VARIABLES[var_name]
            if field_name in data and data[field_name] is not None:
                return self._format_value(data[field_name], var_def.data_type)
        
        # 2. 尝试直接匹配
        if var_name in data:
            return self._format_value(data[var_name], var_def.data_type)
        
        # 3. 使用默认值
        if var_def.default_value is not None:
            return var_def.default_value
        
        # 4. 返回占位符
        return f"[待填写: {var_def.description}]"
    
    def _format_value(self, value: Any, data_type: str) -> Any:
        """格式化值"""
        if value is None:
            return ""
        
        if data_type == "string":
            return str(value)
        elif data_type == "number":
            return float(value) if value else 0
        elif data_type == "date":
            if hasattr(value, 'strftime'):
                return value.strftime("%Y年%m月%d日")
            return str(value)
        elif data_type == "list":
            if isinstance(value, list):
                return "、".join(str(v) for v in value)
            return str(value)
        elif data_type == "dict":
            if isinstance(value, dict):
                return json.dumps(value, ensure_ascii=False, indent=2)
            return str(value)
        
        return str(value)


class TemplateRenderer:
    """模板渲染器"""
    
    def __init__(self, variable_resolver: VariableResolver):
        self.variable_resolver = variable_resolver
    
    def render(
        self,
        template: Template,
        company_info: Dict[str, Any],
        additional_vars: Optional[Dict[str, Any]] = None,
        ai_generated_content: Optional[Dict[str, str]] = None
    ) -> str:
        """渲染模板"""
        # 解析变量
        resolved_vars = self.variable_resolver.resolve(
            company_info, template, additional_vars
        )
        
        # 渲染每个章节
        rendered_sections = []
        for section in template.sections:
            content = section.content
            
            # 如果有AI生成的内容，使用AI内容
            if ai_generated_content and section.id in ai_generated_content:
                content = ai_generated_content[section.id]
            
            # 变量替换
            content = self._replace_variables(content, resolved_vars)
            
            rendered_sections.append({
                "id": section.id,
                "title": section.title,
                "content": content,
            })
        
        # 组装最终文档
        return self._assemble_document(template, rendered_sections)
    
    def render_section(
        self,
        section: TemplateSection,
        variables: Dict[str, Any]
    ) -> str:
        """渲染单个章节"""
        content = section.content
        return self._replace_variables(content, variables)
    
    def _replace_variables(self, content: str, variables: Dict[str, Any]) -> str:
        """替换变量"""
        for var_name, value in variables.items():
            # 支持多种格式: {{var}}, {var}, {{ var }}
            patterns = [
                var_name,
                var_name.replace("{{", "{").replace("}}", "}"),
                var_name.replace("{{", "{{ ").replace("}}", " }}"),
            ]
            for pattern in patterns:
                content = content.replace(pattern, str(value))
        
        return content
    
    def _assemble_document(
        self,
        template: Template,
        sections: List[Dict[str, Any]]
    ) -> str:
        """组装文档"""
        parts = []
        
        # 文档头部
        parts.append(f"# {template.name}\n\n")
        parts.append(f"**文件编号**: {template.template_id}\n")
        parts.append(f"**版本**: {template.version}\n")
        parts.append(f"**文档层级**: {template.document_level.value}\n")
        if template.standard:
            parts.append(f"**适用标准**: {template.standard.value}\n")
        parts.append("\n---\n\n")
        
        # 目录
        parts.append("## 目录\n\n")
        for i, section in enumerate(sections, 1):
            parts.append(f"{i}. {section['title']}\n")
        parts.append("\n---\n\n")
        
        # 正文
        for section in sections:
            parts.append(f"## {section['title']}\n\n")
            parts.append(section['content'])
            parts.append("\n\n")
        
        return "".join(parts)


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, template_dir: str = "./templates"):
        self.loader = TemplateLoader(template_dir)
        self.resolver = VariableResolver()
        self.renderer = TemplateRenderer(self.resolver)
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """获取模板"""
        return self.loader.load(template_id)
    
    def get_templates_by_level(
        self,
        document_level: DocumentLevel,
        standard: Optional[StandardType] = None,
        industry: Optional[str] = None
    ) -> List[Template]:
        """按层级获取模板列表"""
        return self.loader.load_by_type(document_level, standard, industry)
    
    def render_template(
        self,
        template_id: str,
        company_info: Dict[str, Any],
        additional_vars: Optional[Dict[str, Any]] = None,
        ai_generated_content: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """渲染模板"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        return self.renderer.render(
            template, company_info, additional_vars, ai_generated_content
        )
    
    def get_required_variables(self, template_id: str) -> List[TemplateVariable]:
        """获取模板所需变量"""
        template = self.get_template(template_id)
        if not template:
            return []
        
        return list(template.variables.values())
    
    def get_missing_variables(
        self,
        template_id: str,
        company_info: Dict[str, Any]
    ) -> List[TemplateVariable]:
        """获取缺失的变量"""
        template = self.get_template(template_id)
        if not template:
            return []
        
        missing = []
        for var_name, var_def in template.variables.items():
            if var_def.required:
                field_name = self.resolver.STANDARD_VARIABLES.get(var_name)
                if field_name and not company_info.get(field_name):
                    missing.append(var_def)
        
        return missing


# 预定义模板ID常量
class TemplateIDs:
    """模板ID常量"""
    
    # 一级文件 - 管理手册
    QUALITY_MANUAL = "iso9001_quality_manual"
    ENVIRONMENT_MANUAL = "iso14001_environment_manual"
    SAFETY_MANUAL = "iso45001_safety_manual"
    INTEGRATED_MANUAL = "integrated_management_manual"
    
    # 二级文件 - 程序文件
    DOC_CONTROL_PROCEDURE = "doc_control_procedure"
    RECORD_CONTROL_PROCEDURE = "record_control_procedure"
    INTERNAL_AUDIT_PROCEDURE = "internal_audit_procedure"
    MANAGEMENT_REVIEW_PROCEDURE = "management_review_procedure"
    CORRECTIVE_ACTION_PROCEDURE = "corrective_action_procedure"
    TRAINING_PROCEDURE = "training_procedure"
    
    # ISO9001特定程序
    CONTRACT_REVIEW_PROCEDURE = "contract_review_procedure"
    PURCHASING_PROCEDURE = "purchasing_procedure"
    PRODUCTION_CONTROL_PROCEDURE = "production_control_procedure"
    INSPECTION_PROCEDURE = "inspection_procedure"
    CUSTOMER_SATISFACTION_PROCEDURE = "customer_satisfaction_procedure"
    
    # ISO14001特定程序
    ENVIRONMENTAL_FACTORS_PROCEDURE = "environmental_factors_procedure"
    LEGAL_REQUIREMENTS_PROCEDURE = "legal_requirements_procedure"
    EMERGENCY_RESPONSE_PROCEDURE = "emergency_response_procedure"
    
    # ISO45001特定程序
    HAZARD_IDENTIFICATION_PROCEDURE = "hazard_identification_procedure"
    INCIDENT_INVESTIGATION_PROCEDURE = "incident_investigation_procedure"
    
    # 三级文件 - 作业指导书
    JOB_DESCRIPTION = "job_description"
    WORK_INSTRUCTION = "work_instruction"
    EQUIPMENT_OPERATION = "equipment_operation"
    INSPECTION_STANDARD = "inspection_standard"
    SAFETY_PROCEDURE = "safety_procedure"
    
    # 四级文件 - 记录表格
    TRAINING_RECORD = "training_record"
    INSPECTION_RECORD = "inspection_record"
    AUDIT_CHECKLIST = "audit_checklist"
    CORRECTIVE_ACTION_FORM = "corrective_action_form"
    MANAGEMENT_REVIEW_RECORD = "management_review_record"


# 测试代码
if __name__ == "__main__":
    # 测试模板管理器
    manager = TemplateManager("./templates")
    
    # 测试变量解析
    company_info = {
        "company_name": "武汉鑫辰宇物业服务有限公司",
        "industry": "物业",
        "employee_count": 50,
        "address": "武汉市XX区XX路XX号",
        "legal_representative": "张三",
    }
    
    print("模板管理器初始化完成")
    print(f"标准变量映射数量: {len(VariableResolver.STANDARD_VARIABLES)}")
