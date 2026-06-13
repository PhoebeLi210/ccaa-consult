"""
文档生成器模块

集成逐级引用功能，在生成文档时自动查找上级文档并插入引用文本。
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import re

from app.core.document_hierarchy import (
    DocumentLevel,
    DocumentLevelConfig,
    DocumentInfo,
    DocumentReferenceManager,
    ReferenceInfo,
    get_level_name,
)


@dataclass
class DocumentTemplate:
    """文档模板"""
    template_id: str
    name: str
    level: DocumentLevel
    content_template: str
    required_fields: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationContext:
    """生成上下文"""
    project_id: str
    standard: Optional[str] = None  # 标准名称（如 ISO9001:2015）
    clause: Optional[str] = None  # 当前条款号
    company_name: Optional[str] = None
    custom_references: Dict[str, str] = field(default_factory=dict)


class DocumentGenerator:
    """文档生成器

    集成逐级引用功能，在生成文档时自动：
    1. 查找上级文档
    2. 生成引用文本
    3. 插入到文档内容中

    示例：
        generator = DocumentGenerator("project_001")
        context = GenerationContext(
            project_id="project_001",
            standard="ISO9001:2015",
            clause="7.1",
            company_name="XXX公司"
        )
        result = generator.generate_document(
            doc_id="doc_003",
            level=DocumentLevel.LEVEL_3,
            name="设备管理制度",
            code="XXX-QESMS-C-005",
            template=template,
            context=context
        )
    """

    def __init__(self, project_id: str):
        """初始化文档生成器

        Args:
            project_id: 项目ID
        """
        self.project_id = project_id
        self.reference_manager = DocumentReferenceManager(project_id)
        self._templates: Dict[str, DocumentTemplate] = {}
        self._generated_documents: Dict[str, Dict[str, Any]] = {}

    def register_template(self, template: DocumentTemplate) -> None:
        """注册文档模板

        Args:
            template: 文档模板
        """
        self._templates[template.template_id] = template

    def generate_document(
        self,
        doc_id: str,
        level: DocumentLevel,
        name: str,
        code: str,
        template: Optional[DocumentTemplate] = None,
        context: Optional[GenerationContext] = None,
        content_data: Optional[Dict[str, Any]] = None,
        clause_mapping: Optional[Dict[str, str]] = None,
        parent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """生成文档

        自动生成文档并插入引用关系。

        Args:
            doc_id: 文档唯一标识
            level: 文档层级
            name: 文档名称
            code: 文档编号
            template: 文档模板（可选）
            context: 生成上下文（可选）
            content_data: 内容数据（可选）
            clause_mapping: 条款映射关系（可选）
            parent_id: 上级文档ID（可选，自动推断）

        Returns:
            Dict[str, Any]: 生成结果，包含文档内容和引用信息
        """
        # 注册文档到引用管理器
        doc_info = self.reference_manager.register_document(
            doc_id=doc_id,
            level=level,
            name=name,
            code=code,
            clause_mapping=clause_mapping or {},
            parent_id=parent_id,
        )

        # 生成引用文本
        references = self._generate_references(doc_id, level, context)

        # 生成文档内容
        content = self._generate_content(
            doc_info=doc_info,
            template=template,
            context=context,
            content_data=content_data,
            references=references,
        )

        # 保存生成结果
        result = {
            "doc_id": doc_id,
            "level": level.value,
            "level_name": get_level_name(level),
            "name": name,
            "code": code,
            "content": content,
            "references": references,
            "parent_id": doc_info.parent_id,
            "generated_at": datetime.now().isoformat(),
        }

        self._generated_documents[doc_id] = result
        return result

    def _generate_references(
        self,
        doc_id: str,
        level: DocumentLevel,
        context: Optional[GenerationContext] = None,
    ) -> Dict[str, str]:
        """生成引用文本

        Args:
            doc_id: 文档ID
            level: 文档层级
            context: 生成上下文

        Returns:
            Dict[str, str]: 各级引用文本
        """
        references = {}

        if context is None:
            return references

        # 获取文档链
        doc_chain = self.reference_manager.get_document_chain(doc_id)

        # 生成标准引用（针对一级文件）
        if level == DocumentLevel.LEVEL_1 and context.standard and context.clause:
            ref_text = self.reference_manager.generate_reference(
                level=DocumentLevel.LEVEL_1,
                standard=context.standard,
                clause=context.clause,
            )
            references["standard"] = ref_text

        # 生成上级文档引用
        for doc in doc_chain:
            if doc.level == DocumentLevel.LEVEL_1:
                # 一级文件引用标准
                if context.standard and context.clause:
                    ref_text = self.reference_manager.generate_reference(
                        level=DocumentLevel.LEVEL_1,
                        standard=context.standard,
                        clause=context.clause,
                    )
                    references["standard"] = ref_text
            else:
                # 其他层级引用上级
                # 获取映射后的条款号
                mapped_clause = context.clause
                if context.clause and doc_id in self.reference_manager._documents:
                    doc_info = self.reference_manager._documents[doc_id]
                    mapped_clause = doc_info.clause_mapping.get(context.clause, context.clause)

                ref_text = self.reference_manager.generate_reference(
                    level=doc.level,
                    clause=mapped_clause,
                    doc_id=doc.doc_id,
                )
                references[f"level_{doc.level.value}"] = ref_text

        # 添加自定义引用
        if context and context.custom_references:
            references.update(context.custom_references)

        return references

    def _generate_content(
        self,
        doc_info: DocumentInfo,
        template: Optional[DocumentTemplate],
        context: Optional[GenerationContext],
        content_data: Optional[Dict[str, Any]],
        references: Dict[str, str],
    ) -> str:
        """生成文档内容

        Args:
            doc_info: 文档信息
            template: 文档模板
            context: 生成上下文
            content_data: 内容数据
            references: 引用文本

        Returns:
            str: 生成的内容
        """
        if template:
            # 使用模板生成
            content = self._apply_template(
                template=template,
                doc_info=doc_info,
                context=context,
                content_data=content_data,
                references=references,
            )
        else:
            # 生成默认内容
            content = self._generate_default_content(
                doc_info=doc_info,
                context=context,
                content_data=content_data,
                references=references,
            )

        return content

    def _apply_template(
        self,
        template: DocumentTemplate,
        doc_info: DocumentInfo,
        context: Optional[GenerationContext],
        content_data: Optional[Dict[str, Any]],
        references: Dict[str, str],
    ) -> str:
        """应用模板生成内容

        Args:
            template: 文档模板
            doc_info: 文档信息
            context: 生成上下文
            content_data: 内容数据
            references: 引用文本

        Returns:
            str: 生成的内容
        """
        content = template.content_template

        # 替换基本变量
        variables = {
            "{{doc_name}}": doc_info.name,
            "{{doc_code}}": doc_info.code,
            "{{doc_level}}": get_level_name(doc_info.level),
            "{{company_name}}": context.company_name if context else "",
            "{{generation_date}}": datetime.now().strftime("%Y-%m-%d"),
        }

        # 添加引用变量
        for key, value in references.items():
            variables[f"{{{{{key}}}}}"] = value

        # 添加内容数据
        if content_data:
            for key, value in content_data.items():
                variables[f"{{{{{key}}}}}"] = str(value)

        # 替换变量
        for var, val in variables.items():
            content = content.replace(var, val)

        return content

    def _generate_default_content(
        self,
        doc_info: DocumentInfo,
        context: Optional[GenerationContext],
        content_data: Optional[Dict[str, Any]],
        references: Dict[str, str],
    ) -> str:
        """生成默认内容

        Args:
            doc_info: 文档信息
            context: 生成上下文
            content_data: 内容数据
            references: 引用文本

        Returns:
            str: 生成的内容
        """
        lines = [
            f"# {doc_info.name}",
            f"",
            f"**文件编号**: {doc_info.code}",
            f"**文件层级**: {get_level_name(doc_info.level)}",
            f"**编制日期**: {datetime.now().strftime('%Y-%m-%d')}",
            f"",
            f"## 1. 目的",
            f"",
            f"## 2. 适用范围",
            f"",
            f"## 3. 引用文件",
            f"",
        ]

        # 添加引用
        if references:
            for key, value in references.items():
                if value:
                    lines.append(f"- {value}")
            lines.append("")

        lines.extend([
            f"## 4. 职责",
            f"",
            f"## 5. 程序/要求",
            f"",
            f"## 6. 相关记录",
            f"",
        ])

        return "\n".join(lines)

    def insert_reference(
        self,
        doc_id: str,
        reference_type: str,
        reference_text: str,
        position: Optional[str] = None,
    ) -> bool:
        """在文档中插入引用

        Args:
            doc_id: 文档ID
            reference_type: 引用类型（如 "standard", "level_2" 等）
            reference_text: 引用文本
            position: 插入位置（可选，默认为引用章节）

        Returns:
            bool: 是否成功插入
        """
        if doc_id not in self._generated_documents:
            return False

        doc = self._generated_documents[doc_id]

        if position:
            # 在指定位置插入
            content = doc["content"]
            # 简单替换占位符
            placeholder = f"{{{{{position}}}}}"
            if placeholder in content:
                doc["content"] = content.replace(placeholder, reference_text)
                return True
        else:
            # 添加到引用字典
            doc["references"][reference_type] = reference_text
            return True

        return False

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """获取生成的文档

        Args:
            doc_id: 文档ID

        Returns:
            Optional[Dict[str, Any]]: 文档信息
        """
        return self._generated_documents.get(doc_id)

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """获取所有生成的文档

        Returns:
            List[Dict[str, Any]]: 文档列表
        """
        return list(self._generated_documents.values())

    def validate_document_references(self, doc_id: str) -> Dict[str, Any]:
        """验证文档引用

        Args:
            doc_id: 文档ID

        Returns:
            Dict[str, Any]: 验证结果
        """
        doc = self._generated_documents.get(doc_id)
        if not doc:
            return {"valid": False, "error": "Document not found"}

        level = DocumentLevel(doc["level"])
        references = doc.get("references", {})

        validation_results = {
            "valid": True,
            "doc_id": doc_id,
            "level": level.value,
            "checks": {},
        }

        # 验证各级引用
        for ref_type, ref_text in references.items():
            if ref_type == "standard":
                is_valid = self.reference_manager.validate_reference(
                    DocumentLevel.LEVEL_1, ref_text
                )
            elif ref_type.startswith("level_"):
                level_num = int(ref_type.split("_")[1])
                is_valid = self.reference_manager.validate_reference(
                    DocumentLevel(level_num), ref_text
                )
            else:
                is_valid = bool(ref_text)

            validation_results["checks"][ref_type] = {
                "valid": is_valid,
                "text": ref_text,
            }

            if not is_valid:
                validation_results["valid"] = False

        return validation_results

    def export_document_with_references(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """导出带引用的完整文档

        Args:
            doc_id: 文档ID

        Returns:
            Optional[Dict[str, Any]]: 完整文档数据
        """
        doc = self._generated_documents.get(doc_id)
        if not doc:
            return None

        # 获取文档链
        doc_chain = self.reference_manager.get_document_chain(doc_id)

        export_data = {
            "document": doc,
            "document_chain": [
                {
                    "doc_id": d.doc_id,
                    "name": d.name,
                    "code": d.code,
                    "level": d.level.value,
                }
                for d in doc_chain
            ],
            "hierarchy": self.reference_manager.build_hierarchy(),
            "exported_at": datetime.now().isoformat(),
        }

        return export_data

    def set_custom_reference_format(
        self, level: DocumentLevel, format_str: str
    ) -> None:
        """设置自定义引用格式

        Args:
            level: 文档层级
            format_str: 格式字符串
        """
        # 更新配置中的格式
        config = DocumentLevelConfig.get_config(level)
        if config:
            config["reference_format"] = format_str

    def auto_generate_references(
        self,
        doc_id: str,
        standard: str,
        clause: str,
    ) -> Dict[str, str]:
        """自动生成完整的引用链

        Args:
            doc_id: 文档ID
            standard: 标准名称
            clause: 条款号

        Returns:
            Dict[str, str]: 完整引用链
        """
        return self.reference_manager.generate_full_references(
            doc_id=doc_id,
            standard=standard,
            clause=clause,
        )


# 便捷函数
def create_generator(project_id: str) -> DocumentGenerator:
    """创建文档生成器

    Args:
        project_id: 项目ID

    Returns:
        DocumentGenerator: 文档生成器实例
    """
    return DocumentGenerator(project_id)


def generate_with_auto_references(
    project_id: str,
    doc_id: str,
    level: DocumentLevel,
    name: str,
    code: str,
    standard: str,
    clause: str,
    company_name: str = "",
    content_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """自动生成带引用的文档

    便捷函数，一步完成文档生成和引用插入。

    Args:
        project_id: 项目ID
        doc_id: 文档ID
        level: 文档层级
        name: 文档名称
        code: 文档编号
        standard: 标准名称
        clause: 条款号
        company_name: 公司名称
        content_data: 内容数据

    Returns:
        Dict[str, Any]: 生成结果
    """
    generator = DocumentGenerator(project_id)

    context = GenerationContext(
        project_id=project_id,
        standard=standard,
        clause=clause,
        company_name=company_name,
    )

    return generator.generate_document(
        doc_id=doc_id,
        level=level,
        name=name,
        code=code,
        context=context,
        content_data=content_data,
    )
