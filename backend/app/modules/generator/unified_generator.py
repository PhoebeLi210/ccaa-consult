# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 统一文档生成器

整合所有层级的文档生成器，提供统一的生成接口
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import yaml

# 从现有模块导入
from app.modules.generator.base import (
    BaseGenerator, CompanyInfo, GeneratedDocument,
    FileLevel, DocumentType, TemplateEngine, VariableManager
)
from app.modules.generator.template_manager import TemplateManager


class UnifiedDocumentGenerator:
    """统一文档生成器
    
    整合所有层级的文档生成功能，提供统一的生成接口
    """
    
    def __init__(self, template_dir: str = "./templates_wuxing"):
        self.template_manager = TemplateManager(template_dir)
        self.template_engine = TemplateEngine()
        self.generated_documents: List[GeneratedDocument] = []
    
    def generate_from_template(
        self,
        template_id: str,
        company_info: Dict[str, Any],
        additional_vars: Optional[Dict[str, Any]] = None
    ) -> Optional[GeneratedDocument]:
        """从YAML模板生成文档
        
        Args:
            template_id: 模板ID（文件名）
            company_info: 企业信息字典
            additional_vars: 额外变量
            
        Returns:
            生成的文档
        """
        # 查找模板文件
        template_file = self._find_template_file(template_id)
        if not template_file:
            return None
        
        try:
            # 加载模板
            with open(template_file, "r", encoding="utf-8") as f:
                template_data = yaml.safe_load(f)
            
            doc_info = template_data.get("document_info", {})
            content = template_data.get("content", template_data.get("form_structure", {}))
            
            # 合并变量
            all_vars = {**company_info}
            if additional_vars:
                all_vars.update(additional_vars)
            
            # 渲染内容
            rendered_content = self._replace_variables(content, all_vars)
            
            # 确定文件层级
            level_str = doc_info.get("document_type", "四级文件")
            file_level = self._parse_file_level(level_str)
            
            # 确定文档类型
            doc_type = self._parse_document_type(level_str)
            
            return GeneratedDocument(
                file_level=file_level,
                document_type=doc_type,
                file_code=doc_info.get("document_code", template_id),
                file_name=f"{doc_info.get('document_name', template_id)}.docx",
                title=doc_info.get("document_name", ""),
                content=str(rendered_content),
                standards=company_info.get("target_standards", []),
                created_at=datetime.now(),
            )
        except Exception as e:
            print(f"生成文档失败: {template_id}, 错误: {e}")
            return None
    
    def generate_all_documents(
        self,
        company_info: Dict[str, Any],
        levels: Optional[List[str]] = None
    ) -> List[GeneratedDocument]:
        """生成全套体系文件
        
        Args:
            company_info: 企业信息
            levels: 指定层级，None表示全部
            
        Returns:
            生成的文档列表
        """
        self.generated_documents = []
        
        template_dir = Path(self.template_manager.loader.template_dir)
        if not template_dir.exists():
            return []
        
        for level_dir in template_dir.iterdir():
            if not level_dir.is_dir():
                continue
            
            level_name = level_dir.name
            
            # 过滤层级
            if levels and level_name not in levels:
                continue
            
            # 生成该层级下的所有文档
            for template_file in level_dir.glob("*.yaml"):
                doc = self.generate_from_template(
                    template_file.stem,
                    company_info
                )
                if doc:
                    self.generated_documents.append(doc)
        
        return self.generated_documents
    
    def generate_by_level(
        self,
        company_info: Dict[str, Any],
        level: str
    ) -> List[GeneratedDocument]:
        """按层级生成文档
        
        Args:
            company_info: 企业信息
            level: 层级（一级文件/二级文件/三级文件/四级文件）
            
        Returns:
            生成的文档列表
        """
        return self.generate_all_documents(company_info, [level])
    
    def generate_single_document(
        self,
        company_info: Dict[str, Any],
        template_id: str
    ) -> Optional[GeneratedDocument]:
        """生成单个文档
        
        Args:
            company_info: 企业信息
            template_id: 模板ID
            
        Returns:
            生成的文档
        """
        return self.generate_from_template(template_id, company_info)
    
    def batch_generate(
        self,
        company_info: Dict[str, Any],
        template_ids: List[str]
    ) -> List[GeneratedDocument]:
        """批量生成文档
        
        Args:
            company_info: 企业信息
            template_ids: 模板ID列表
            
        Returns:
            生成的文档列表
        """
        documents = []
        for template_id in template_ids:
            doc = self.generate_from_template(template_id, company_info)
            if doc:
                documents.append(doc)
        return documents
    
    def get_document_tree(self) -> Dict[str, Any]:
        """获取文档树结构"""
        tree = {
            "一级文件": {"count": 0, "documents": []},
            "二级文件": {"count": 0, "documents": []},
            "三级文件": {"count": 0, "documents": []},
            "四级文件": {"count": 0, "documents": []},
        }
        
        for doc in self.generated_documents:
            level_name = self._get_level_name(doc.file_level)
            if level_name in tree:
                tree[level_name]["documents"].append({
                    "file_code": doc.file_code,
                    "file_name": doc.file_name,
                    "title": doc.title,
                })
                tree[level_name]["count"] += 1
        
        return tree
    
    def export_to_dict(self, company_info: Dict[str, Any]) -> Dict[str, Any]:
        """导出为字典格式"""
        return {
            "company_info": {
                "company_name": company_info.get("company_name", ""),
                "industry": company_info.get("industry", ""),
                "employee_count": company_info.get("employee_count", 0),
                "target_standards": company_info.get("target_standards", []),
            },
            "documents": [doc.to_dict() for doc in self.generated_documents],
            "total_count": len(self.generated_documents),
            "document_tree": self.get_document_tree(),
            "generated_at": datetime.now().isoformat(),
        }
    
    def _find_template_file(self, template_id: str) -> Optional[Path]:
        """查找模板文件"""
        template_dir = Path(self.template_manager.loader.template_dir)
        if not template_dir.exists():
            return None
        
        for level_dir in template_dir.iterdir():
            if not level_dir.is_dir():
                continue
            
            candidate = level_dir / f"{template_id}.yaml"
            if candidate.exists():
                return candidate
        
        return None
    
    def _replace_variables(self, content: Any, variables: Dict[str, Any]) -> Any:
        """替换变量"""
        if isinstance(content, str):
            for key, value in variables.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))
            return content
        elif isinstance(content, dict):
            return {k: self._replace_variables(v, variables) for k, v in content.items()}
        elif isinstance(content, list):
            return [self._replace_variables(item, variables) for item in content]
        return content
    
    def _parse_file_level(self, level_str: str) -> FileLevel:
        """解析文件层级"""
        level_map = {
            "一级文件": FileLevel.LEVEL_1,
            "二级文件": FileLevel.LEVEL_2,
            "三级文件": FileLevel.LEVEL_3,
            "四级文件": FileLevel.LEVEL_4,
        }
        return level_map.get(level_str, FileLevel.LEVEL_4)
    
    def _parse_document_type(self, level_str: str) -> DocumentType:
        """解析文档类型"""
        type_map = {
            "一级文件": DocumentType.MANUAL,
            "二级文件": DocumentType.PROCEDURE,
            "三级文件": DocumentType.INSTRUCTION,
            "四级文件": DocumentType.FORM,
        }
        return type_map.get(level_str, DocumentType.FORM)
    
    def _get_level_name(self, file_level: FileLevel) -> str:
        """获取层级名称"""
        name_map = {
            FileLevel.LEVEL_1: "一级文件",
            FileLevel.LEVEL_2: "二级文件",
            FileLevel.LEVEL_3: "三级文件",
            FileLevel.LEVEL_4: "四级文件",
        }
        return name_map.get(file_level, "四级文件")


# ============================================================
# 便捷函数
# ============================================================

def generate_full_package(
    company_info: Dict[str, Any],
    template_dir: str = "./templates_wuxing"
) -> List[GeneratedDocument]:
    """生成完整体系文件包"""
    generator = UnifiedDocumentGenerator(template_dir)
    return generator.generate_all_documents(company_info)


def generate_by_level(
    company_info: Dict[str, Any],
    level: str,
    template_dir: str = "./templates_wuxing"
) -> List[GeneratedDocument]:
    """按层级生成文档"""
    generator = UnifiedDocumentGenerator(template_dir)
    return generator.generate_by_level(company_info, level)


def generate_single(
    company_info: Dict[str, Any],
    template_id: str,
    template_dir: str = "./templates_wuxing"
) -> Optional[GeneratedDocument]:
    """生成单个文档"""
    generator = UnifiedDocumentGenerator(template_dir)
    return generator.generate_single_document(company_info, template_id)


def batch_generate(
    company_info: Dict[str, Any],
    template_ids: List[str],
    template_dir: str = "./templates_wuxing"
) -> List[GeneratedDocument]:
    """批量生成文档"""
    generator = UnifiedDocumentGenerator(template_dir)
    return generator.batch_generate(company_info, template_ids)
