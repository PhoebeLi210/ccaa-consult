# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 统一文档生成器（重构版）

整合所有层级的文档生成器，提供统一的生成接口
支持按行业过滤模板
支持行业规则引擎联动
支持设备操作规程动态生成
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
from app.modules.generator.docx_exporter import DocxExporter, DocumentPackager
from app.core.config import settings

# 导入设备操作规程生成器
from app.modules.generator.level3.dynamic_equipment_generator import (
    generate_equipment_operations,
    get_equipment_categories,
)


class UnifiedDocumentGenerator:
    """统一文档生成器
    
    整合所有层级的文档生成功能，提供统一的生成接口
    支持按行业过滤模板，确保生成的文档符合行业特点
    支持AI扩写描述性内容
    """
    
    def __init__(self, template_dir: Optional[str] = None, output_dir: Optional[str] = None,
                 use_ai_expansion: bool = False):
        """
        初始化生成器
        
        Args:
            template_dir: 模板目录路径，None则使用默认路径
            output_dir: 输出目录路径，None则使用默认路径
            use_ai_expansion: 是否启用AI扩写描述性内容
        """
        self.template_dir = Path(template_dir) if template_dir else TEMPLATE_DIR
        self.template_manager = TemplateManager(str(self.template_dir))
        self.template_engine = TemplateEngine()
        self.generated_documents: List[GeneratedDocument] = []
        self.output_dir = output_dir or "./output"
        self.exporter = DocxExporter(self.output_dir)
        self.packager = DocumentPackager(self.exporter)
        self.use_ai_expansion = use_ai_expansion
    
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
            
            # 获取内容（兼容 metadata/content 和 document_info 两种格式）
            content = template_data.get("content", template_data.get("sections", {}))
            if not content:
                content = template_data.get("form_structure", {})
            if not content:
                # document_info 格式：整个 document_info 就是内容
                doc_info = template_data.get("document_info", {})
                if doc_info:
                    content = doc_info
            if not content:
                # 最后尝试：把整个 template_data 作为内容（去掉 metadata/document_info）
                content = {k: v for k, v in template_data.items() 
                          if k not in ("metadata", "document_info", "__comments__")}
            
            # 合并变量
            all_vars = {**company_info}
            if additional_vars:
                all_vars.update(additional_vars)
            
            # 渲染内容（使用重构后的工具函数）
            rendered_content = replace_variables(content, all_vars)
            
            # AI扩写描述性内容（可选）
            if self.use_ai_expansion and settings.LLM_API_KEY:
                rendered_content = self._ai_expand_content(
                    rendered_content, metadata, company_info
                )
            
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
        
        # ========== 行业规则引擎：动态生成设备操作规程 ==========
        # 根据行业配置决定是否生成设备操作规程
        equipment_list = company_info.get("equipment_list", [])
        industry_code = company_info.get("industry_code") or company_info.get("industry", "")
        
        # 检查行业配置中是否启用设备操作规程
        should_generate_equipment_ops = self._should_generate_equipment_operations(
            industry_code, equipment_list
        )
        
        if should_generate_equipment_ops and equipment_list:
            try:
                # 将字典转换为CompanyInfo对象
                company_info_obj = self._dict_to_company_info(company_info)
                equipment_docs = generate_equipment_operations(
                    company_info_obj,
                    equipment_list,
                    include_summary=True
                )
                self.generated_documents.extend(equipment_docs)
                print(f"动态生成 {len(equipment_docs)} 个设备操作规程")
            except Exception as e:
                print(f"设备操作规程生成失败: {e}")
        
        print(f"共生成 {len(self.generated_documents)} 个文档")
        return self.generated_documents
    
    def _should_generate_equipment_operations(
        self,
        industry_code: str,
        equipment_list: List[Dict]
    ) -> bool:
        """
        判断是否应生成设备操作规程
        
        规则：
        1. 如果提供了设备清单，且行业不是纯服务业（如咨询、软件开发），则生成
        2. 生产型行业（制造业、建筑业等）必须生成
        3. 办公型行业（物业服务、软件开发等）如果有特殊设备也生成
        
        Args:
            industry_code: 行业代码
            equipment_list: 设备清单
            
        Returns:
            是否生成设备操作规程
        """
        if not equipment_list:
            return False
        
        # 生产型行业列表
        production_industries = [
            "manufacturing", "construction", "mining", "transportation",
            "制造业", "建筑业", "采矿业", "运输业"
        ]
        
        # 检查是否为生产型行业
        is_production = any(pid in industry_code.lower() for pid in production_industries)
        
        # 生产型行业只要有设备就生成
        if is_production:
            return True
        
        # 非生产型行业：如果有特殊设备（非纯办公设备）也生成
        office_only = ["电脑", "打印机", "复印机", "投影仪", "碎纸机", "饮水机"]
        has_special_equipment = any(
            eq.get("name", "") not in office_only 
            for eq in equipment_list
        )
        
        return has_special_equipment
    
    def _dict_to_company_info(self, company_info: Dict[str, Any]) -> CompanyInfo:
        """将字典转换为CompanyInfo对象"""
        return CompanyInfo(
            company_name=company_info.get("company_name", ""),
            company_code=company_info.get("company_code", company_info.get("company_abbr", "")),
            industry=company_info.get("industry", ""),
            sub_industry=company_info.get("sub_industry", ""),
            employee_count=company_info.get("employee_count", 0),
            office_area_sqm=company_info.get("office_area_sqm", 0),
            certification_type=company_info.get("certification_type", "初次认证"),
            existing_standards=company_info.get("existing_standards", []),
            target_standards=company_info.get("target_standards", ["ISO9001", "ISO14001", "ISO45001"]),
            departments=company_info.get("departments", []),
            main_equipment=[eq.get("name", "") for eq in company_info.get("equipment_list", [])],
            main_processes=company_info.get("main_processes", []),
            special_processes=company_info.get("special_processes", []),
            quality_goals=company_info.get("quality_goals", ""),
            environment_goals=company_info.get("environment_goals", ""),
            safety_goals=company_info.get("safety_goals", ""),
            address=company_info.get("address", ""),
            legal_representative=company_info.get("legal_representative", ""),
            contact_person=company_info.get("contact_person", ""),
            contact_phone=company_info.get("contact_phone", ""),
            management_representative=company_info.get("management_representative", ""),
            file_version=company_info.get("file_version", "A/0"),
            effective_date=company_info.get("effective_date", ""),
            release_date=company_info.get("release_date", ""),
        )
    
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
    
    def export_to_docx(self, company_name: str = "") -> List[Path]:
        """导出所有生成的文档为.docx文件
        
        Args:
            company_name: 公司名称，用于创建子目录
            
        Returns:
            导出文件的路径列表
        """
        return self.exporter.export_batch(self.generated_documents, company_name)
    
    def export_single_to_docx(self, doc: GeneratedDocument, company_name: str = "") -> Path:
        """导出单个文档为.docx文件
        
        Args:
            doc: 要导出的文档
            company_name: 公司名称
            
        Returns:
            导出文件的路径
        """
        return self.exporter.export(doc, company_name)
    
    def export_to_zip(self, company_name: str) -> Path:
        """将所有文档打包为ZIP文件
        
        Args:
            company_name: 公司名称
            
        Returns:
            ZIP文件路径
        """
        return self.packager.create_package(self.generated_documents, company_name)
    
    def get_docx_bytes(self, doc: GeneratedDocument) -> bytes:
        """获取单个文档的字节流（用于API下载）
        
        Args:
            doc: 文档对象
            
        Returns:
            文档的字节内容
        """
        return self.exporter.export_to_bytes(doc)
    
    def get_zip_bytes(self) -> bytes:
        """获取所有文档打包后的字节流（用于API下载）
        
        Returns:
            ZIP文件的字节内容
        """
        return self.packager.create_package_bytes(self.generated_documents)
    
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
    
    def _ai_expand_content(
        self,
        content: Any,
        metadata: Dict[str, Any],
        company_info: Dict[str, Any]
    ) -> Any:
        """使用AI扩写描述性内容
        
        对模板中标记为需要AI扩写的章节，使用LLM生成更丰富的内容。
        四级文件（记录表单）不进行AI扩写。
        
        Args:
            content: 模板渲染后的内容
            metadata: 模板元数据
            company_info: 企业信息
            
        Returns:
            扩写后的内容
        """
        # 四级文件不扩写
        level = metadata.get("level", 4)
        if level >= 4:
            return content
        
        # 如果内容是字符串，检查是否需要扩写
        if isinstance(content, str):
            # 检查是否有AI扩写标记 {{ai_expand:...}}
            if "{{ai_expand:" not in content:
                return content
            
            try:
                import re
                import httpx
                
                # 查找所有AI扩写标记
                pattern = r'\{\{ai_expand:(.*?)\}\}'
                matches = re.findall(pattern, content)
                
                if not matches:
                    return content
                
                # 检查API配置
                api_key = settings.LLM_API_KEY
                api_url = settings.LLM_API_URL
                model = settings.LLM_MODEL
                
                if not api_key:
                    return content
                
                company_name = company_info.get("company_name", "企业")
                industry = company_info.get("industry", "")
                
                for prompt_hint in matches:
                    expand_prompt = f"""请为"{company_name}"（{industry}行业）生成以下内容，要求专业、具体、符合ISO体系文件规范：

{prompt_hint}

要求：
1. 内容专业、具体，不要过于笼统
2. 符合ISO9001/14001/45001标准要求
3. 适合{industry}行业特点
4. 字数200-500字"""
                    
                    try:
                        headers = {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        }
                        payload = {
                            "model": model,
                            "messages": [
                                {"role": "system", "content": "你是一个ISO体系文件编写专家，擅长编写质量、环境、职业健康安全管理体系文件。"},
                                {"role": "user", "content": expand_prompt}
                            ],
                            "temperature": 0.7,
                            "max_tokens": 2000
                        }
                        
                        with httpx.Client(timeout=30.0) as client:
                            response = client.post(
                                f"{api_url}/chat/completions",
                                headers=headers,
                                json=payload
                            )
                            response.raise_for_status()
                            data = response.json()
                            result = data["choices"][0]["message"]["content"]
                            
                            if result:
                                content = content.replace(
                                    f"{{{{ai_expand:{prompt_hint}}}}}",
                                    result.strip()
                                )
                    except Exception as e:
                        print(f"AI扩写失败: {e}")
                        # 扩写失败时保留原始标记
                        pass
                
                return content
                
            except Exception as e:
                print(f"AI扩写处理失败: {e}")
                return content
        
        # 如果内容是字典，递归处理
        if isinstance(content, dict):
            return {k: self._ai_expand_content(v, metadata, company_info) for k, v in content.items()}
        
        # 如果内容是列表，递归处理
        if isinstance(content, list):
            return [self._ai_expand_content(item, metadata, company_info) for item in content]
        
        return content
    


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
