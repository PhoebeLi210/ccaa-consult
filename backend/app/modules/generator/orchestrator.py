#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档生成器协调器

协调各个层级的生成器，生成完整的体系文件包。
"""

from typing import List, Dict, Optional
from .base import (
    BaseGenerator,
    CompanyInfo,
    GeneratedDocument,
    FileLevel,
    DocumentType,
)
from .level1 import manual_generator
from .level2 import procedure_generator
from .level3 import level3_generator
from .level4 import level4_generator
from .required_docs import (
    required_doc_generator,
    RequiredDocChecker,
    RequiredDocTemplateGenerator,
    RequiredDocCategory,
)


class DocumentOrchestrator:
    """
    文档生成器协调器

    负责协调各个层级的生成器，一次性生成完整的体系文件包。
    """

    def __init__(self, company_info: CompanyInfo):
        self.company_info = company_info
        self.generated_documents: List[GeneratedDocument] = []

    def generate_all(
        self,
        include_level1: bool = True,
        include_level2: bool = True,
        include_level3: bool = True,
        include_level4: bool = True,
        include_required_docs: bool = True,
    ) -> List[GeneratedDocument]:
        """
        生成所有体系文件

        Args:
            include_level1: 是否生成一级文件（管理手册）
            include_level2: 是否生成二级文件（程序文件）
            include_level3: 是否生成三级文件（作业指导书/制度）
            include_level4: 是否生成四级文件（记录表格）
            include_required_docs: 是否生成必需文件模板

        Returns:
            所有生成的文档列表
        """
        self.generated_documents = []

        # 生成一级文件
        if include_level1:
            doc = manual_generator.generate_manual(self.company_info)
            self.generated_documents.append(doc)

        # 生成二级文件
        if include_level2:
            docs = procedure_generator.generate_all_procedures(self.company_info)
            self.generated_documents.extend(docs)

        # 生成三级文件
        if include_level3:
            docs = self._generate_level3_documents()
            self.generated_documents.extend(docs)

        # 生成四级文件
        if include_level4:
            docs = level4_generator.generate_all_level4_forms(self.company_info)
            self.generated_documents.extend(docs)

        # 生成必需文件模板
        if include_required_docs:
            template_gen = RequiredDocTemplateGenerator()
            docs = template_gen.generate_all_templates(self.company_info)
            self.generated_documents.extend(docs)

        return self.generated_documents

    def _generate_level3_documents(self) -> List[GeneratedDocument]:
        """生成三级文件"""
        docs = []

        # 生成管理制度示例
        try:
            doc = level3_generator.generate_regulation(self.company_info, 1)
            docs.append(doc)
        except ValueError:
            pass

        try:
            doc = level3_generator.generate_regulation(self.company_info, 22)
            docs.append(doc)
        except ValueError:
            pass

        # 生成设备操作规程示例
        try:
            doc = level3_generator.generate_operation(self.company_info, 3)
            docs.append(doc)
        except ValueError:
            pass

        try:
            doc = level3_generator.generate_operation(self.company_info, 19)
            docs.append(doc)
        except ValueError:
            pass

        return docs

    def generate_by_level(
        self,
        file_level: FileLevel,
        file_codes: List[int] = None
    ) -> List[GeneratedDocument]:
        """
        按层级生成指定文档

        Args:
            file_level: 文件层级
            file_codes: 指定文件序号列表，如果为空则生成该层级所有文档

        Returns:
            生成的文档列表
        """
        if file_level == FileLevel.LEVEL_1:
            return [manual_generator.generate_manual(self.company_info)]

        elif file_level == FileLevel.LEVEL_2:
            if file_codes:
                return [
                    procedure_generator.generate_procedure(self.company_info, code)
                    for code in file_codes
                ]
            return procedure_generator.generate_all_procedures(self.company_info)

        elif file_level == FileLevel.LEVEL_3:
            if file_codes:
                docs = []
                for code in file_codes:
                    try:
                        doc = level3_generator.generate_regulation(self.company_info, code)
                        docs.append(doc)
                    except ValueError:
                        try:
                            doc = level3_generator.generate_operation(self.company_info, code)
                            docs.append(doc)
                        except ValueError:
                            pass
                return docs
            return self._generate_level3_documents()

        elif file_level == FileLevel.LEVEL_4:
            if file_codes:
                return [
                    level4_generator.generate_level4_form(self.company_info, code)
                    for code in file_codes
                ]
            return level4_generator.generate_all_level4_forms(self.company_info)

        return []

    def generate_required_doc_templates(
        self,
        doc_codes: List[str] = None
    ) -> List[GeneratedDocument]:
        """
        生成必需文件模板

        Args:
            doc_codes: 指定文件编号列表，如果为空则生成所有可用模板

        Returns:
            生成的模板列表
        """
        template_gen = RequiredDocTemplateGenerator()

        if doc_codes:
            docs = []
            for code in doc_codes:
                doc = template_gen.generate_template(code, self.company_info)
                if doc:
                    docs.append(doc)
            return docs

        return template_gen.generate_all_templates(self.company_info)

    def check_required_documents(
        self,
        provided_files: Dict[str, str]
    ) -> Dict:
        """
        检查企业必需文件提供情况

        Args:
            provided_files: 企业已提供的文件，格式 {文件编号: 文件路径}

        Returns:
            检查结果汇总
        """
        checker = RequiredDocChecker()
        results = checker.check_documents(provided_files)
        return checker.get_missing_summary(results)

    def get_document_tree(self) -> Dict:
        """
        获取文档树结构

        Returns:
            文档树结构
        """
        tree = {
            "level_1": {
                "name": "一级文件",
                "description": "管理手册",
                "count": 0,
                "documents": [],
            },
            "level_2": {
                "name": "二级文件",
                "description": "程序文件",
                "count": 0,
                "documents": [],
            },
            "level_3": {
                "name": "三级文件",
                "description": "作业指导书/制度",
                "count": 0,
                "documents": [],
            },
            "level_4": {
                "name": "四级文件",
                "description": "记录表格",
                "count": 0,
                "documents": [],
            },
            "required_docs": {
                "name": "必需文件",
                "description": "企业认证必需文件",
                "count": 0,
                "documents": [],
            },
        }

        for doc in self.generated_documents:
            if doc.file_level == FileLevel.LEVEL_1:
                key = "level_1"
            elif doc.file_level == FileLevel.LEVEL_2:
                key = "level_2"
            elif doc.file_level == FileLevel.LEVEL_3:
                key = "level_3"
            elif doc.file_level == FileLevel.LEVEL_4:
                key = "level_4"
            else:
                key = "required_docs"

            tree[key]["documents"].append({
                "file_code": doc.file_code,
                "file_name": doc.file_name,
                "title": doc.title,
            })
            tree[key]["count"] += 1

        return tree

    def export_to_dict(self) -> Dict:
        """
        导出为字典格式

        Returns:
            包含所有文档的字典
        """
        return {
            "company_info": {
                "company_name": self.company_info.company_name,
                "industry": self.company_info.industry,
                "employee_count": self.company_info.employee_count,
                "target_standards": self.company_info.target_standards,
            },
            "documents": [doc.to_dict() for doc in self.generated_documents],
            "total_count": len(self.generated_documents),
            "document_tree": self.get_document_tree(),
        }


# ============================================================
# 便捷函数
# ============================================================

def generate_full_package(
    company_info: CompanyInfo,
    **kwargs
) -> List[GeneratedDocument]:
    """
    生成完整体系文件包

    Args:
        company_info: 企业信息
        **kwargs: 其他参数

    Returns:
        所有生成的文档列表
    """
    orchestrator = DocumentOrchestrator(company_info)
    return orchestrator.generate_all(**kwargs)


def generate_document_tree(
    company_info: CompanyInfo,
) -> Dict:
    """
    获取文档树结构

    Args:
        company_info: 企业信息

    Returns:
        文档树结构
    """
    orchestrator = DocumentOrchestrator(company_info)
    orchestrator.generate_all()
    return orchestrator.get_document_tree()
