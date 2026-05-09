# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 统一文档生成器（重构版）

整合所有层级的文档生成器，提供统一的生成接口
支持按行业过滤模板
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

# 从现有模块导入
from app.modules.generator.base import (
    BaseGenerator, CompanyInfo, GeneratedDocument,
    FileLevel, DocumentType, TemplateEngine
)
from app.modules.generator.template_manager import TemplateManager

# 导入重构后的工具函数
from app.utils.template_utils import (
    replace_variables,
    load_yaml_template,
    find_template_file,
    get_template_metadata,
    filter_templates_by_industry,
    get_all_templates
)
from app.core.constants import TEMPLATE_DIR


class UnifiedDocumentGenerator:
    """统一文档生成器
    
    整合所有层级的文档生成功能，提供统一的生成接口
    支持按行业过滤模板，确保生成的文档符合行业特点
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        初始化生成器
        
        Args:
            template_dir: 模板目录路径，None则使用默认路径
        """
        self.template_dir = Path(template_dir) if template_dir else TEMPLATE_DIR
        self.template_manager = TemplateManager(str(self.template_dir))
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
        template_file = find_template_file(template_id, self.template_dir)
        if not template_file:
            print(f"模板未找到: {template_id}")
            return None
        
        # 加载模板数据
        template_data = load_yaml_template(template_file)
        if not template_data:
            return None
        
        try:
            # 获取模板元数据
            metadata = get_template_metadata(template_data)
            
            # 检查行业匹配（如果模板有行业标记）
            template_industry = metadata.get("industry")
            company_industry = company_info.get("industry_code") or company_info.get("industry", "")
            
            if template_industry and template_industry != company_industry:
                # 模板有行业标记但与企业行业不匹配，跳过生成
                print(f"跳过模板 {template_id}: 行业不匹配 (模板: {template_industry}, 企业: {company_industry})")
                return None
            
            # 获取内容
            content = template_data.get("content", template_data.get("sections", {}))
            if not content:
                content = template_data.get("form_structure", {})
            
            # 合并变量
            all_vars = {**company_info}
            if additional_vars:
                all_vars.update(additional_vars)
            
            # 渲染内容（使用重构后的工具函数）
            rendered_content = replace_variables(content, all_vars)
            
            # 确定文件层级
            level_str = self._get_level_str_from_metadata(metadata)
            file_level = self._parse_file_level(level_str)
            
            # 确定文档类型
            doc_type = self._parse_document_type(level_str)
            
            return GeneratedDocument(
                file_level=file_level,
                document_type=doc_type,
                file_code=metadata.get("code", template_id),
                file_name=f"{metadata.get('name', template_id)}.docx",
                title=metadata.get("name", ""),
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
        """生成全套体系文件（支持行业过滤）
        
        Args:
            company_info: 企业信息，必须包含 industry_code 或 industry 字段
            levels: 指定层级，None表示全部
            
        Returns:
            生成的文档列表
        """
        self.generated_documents = []
        
        # 获取企业行业代码
        company_industry = company_info.get("industry_code") or company_info.get("industry", "")
        
        if not self.template_dir.exists():
            print(f"模板目录不存在: {self.template_dir}")
            return []
        
        # 遍历所有层级目录
        for level_dir in self.template_dir.iterdir():
            if not level_dir.is_dir():
                continue
            
            level_name = level_dir.name
            
            # 过滤层级
            if levels and level_name not in levels:
                continue
            
            # 获取该层级下的所有模板文件
            template_files = list(level_dir.glob("*.yaml"))
            
            # 根据行业过滤模板
            if company_industry:
                filtered_files = filter_templates_by_industry(template_files, company_industry)
                skipped_count = len(template_files) - len(filtered_files)
                if skipped_count > 0:
                    print(f"层级 {level_name}: 跳过 {skipped_count} 个非本行业模板")
            else:
                # 未指定行业，只生成通用模板（无industry标记的）
                filtered_files = filter_templates_by_industry(template_files, None)
            
            # 生成过滤后的文档
            for template_file in filtered_files:
                doc = self.generate_from_template(
                    template_file.stem,
                    company_info
                )
                if doc:
                    self.generated_documents.append(doc)
        
        print(f"共生成 {len(self.generated_documents)} 个文档")
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
    
    def get_available_templates(
        self,
        industry_code: Optional[str] = None,
        level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取可用的模板列表
        
        Args:
            industry_code: 行业代码，None表示获取通用模板
            level: 层级过滤
            
        Returns:
            模板信息列表
        """
        templates = []
        
        target_dirs = []
        if level:
            target_dirs.append(self.template_dir / level)
        else:
            target_dirs = [d for d in self.template_dir.iterdir() if d.is_dir()]
        
        for level_dir in target_dirs:
            if not level_dir.exists():
                continue
            
            template_files = list(level_dir.glob("*.yaml"))
            filtered_files = filter_templates_by_industry(template_files, industry_code)
            
            for template_file in filtered_files:
                template_data = load_yaml_template(template_file)
                if template_data:
                    metadata = get_template_metadata(template_data)
                    templates.append({
                        "id": template_file.stem,
                        "level": level_dir.name,
                        **metadata
                    })
        
        return templates
    
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
                "industry_code": company_info.get("industry_code", ""),
                "employee_count": company_info.get("employee_count", 0),
                "target_standards": company_info.get("target_standards", []),
            },
            "documents": [doc.to_dict() for doc in self.generated_documents],
            "total_count": len(self.generated_documents),
            "document_tree": self.get_document_tree(),
            "generated_at": datetime.now().isoformat(),
        }
    
    # ============ 私有辅助方法 ============
    
    def _get_level_str_from_metadata(self, metadata: Dict[str, Any]) -> str:
        """从元数据获取层级字符串"""
        level_map = {
            1: "一级文件",
            2: "二级文件",
            3: "三级文件",
            4: "四级文件",
        }
        level_num = metadata.get("level", 4)
        return level_map.get(level_num, "四级文件")
    
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
    template_dir: Optional[str] = None
) -> List[GeneratedDocument]:
    """生成完整体系文件包
    
    Args:
        company_info: 企业信息，应包含 industry_code 字段用于行业过滤
        template_dir: 模板目录路径
        
    Returns:
        生成的文档列表
    """
    generator = UnifiedDocumentGenerator(template_dir)
    return generator.generate_all_documents(company_info)


def generate_by_level(
    company_info: Dict[str, Any],
    level: str,
    template_dir: Optional[str] = None
) -> List[GeneratedDocument]:
    """按层级生成文档"""
    generator = UnifiedDocumentGenerator(template_dir)
    return generator.generate_by_level(company_info, level)


def generate_single(
    company_info: Dict[str, Any],
    template_id: str,
    template_dir: Optional[str] = None
) -> Optional[GeneratedDocument]:
    """生成单个文档"""
    generator = UnifiedDocumentGenerator(template_dir)
    return generator.generate_single_document(company_info, template_id)


def batch_generate(
    company_info: Dict[str, Any],
    template_ids: List[str],
    template_dir: Optional[str] = None
) -> List[GeneratedDocument]:
    """批量生成文档"""
    generator = UnifiedDocumentGenerator(template_dir)
    return generator.batch_generate(company_info, template_ids)


def get_templates_by_industry(
    industry_code: Optional[str] = None,
    level: Optional[str] = None,
    template_dir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """获取指定行业的可用模板列表
    
    Args:
        industry_code: 行业代码
        level: 层级过滤
        template_dir: 模板目录
        
    Returns:
        模板信息列表
    """
    generator = UnifiedDocumentGenerator(template_dir)
    return generator.get_available_templates(industry_code, level)
