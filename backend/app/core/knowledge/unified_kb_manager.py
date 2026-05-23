"""
统一知识库管理器 (Unified Knowledge Manager)

整合四层知识库架构（L1标准层、L2经验层、L3应用层、L4用户层）
和行业知识库，为consult模块提供统一的知识查询接口。

适配consult模块的业务场景，用于生成体系文件而非审核记录。
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path

# 导入已有的知识库
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from iso_standards_kb import ISOStandardsKnowledgeBase, get_knowledge_base
from industries.industry_kb import IndustryKnowledgeBase, get_industry_kb


@dataclass
class ClauseKnowledge:
    """条款知识数据类"""
    standard: str
    clause: str
    title: str
    content: str
    key_points: List[str] = field(default_factory=list)
    implementation_guidance: str = ""
    document_hints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentContext:
    """文档生成上下文数据类"""
    standard: str
    clause: str
    department: str
    company_id: str
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    clause_knowledge: Optional[ClauseKnowledge] = None
    industry_context: Optional[Dict[str, Any]] = None
    template_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    generation_hints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IndustryContext:
    """行业上下文数据类"""
    industry_code: str
    industry_name: str
    key_departments: List[str] = field(default_factory=list)
    key_processes: List[str] = field(default_factory=list)
    regulations: List[str] = field(default_factory=list)
    priority_clauses: List[str] = field(default_factory=list)
    document_generation_hints: Dict[str, Any] = field(default_factory=dict)


class UnifiedKnowledgeManager:
    """
    统一知识库管理器
    
    整合四层知识库架构：
    - L1 标准层: ISO标准条款知识 (iso_standards_kb)
    - L2 经验层: 行业最佳实践和经验数据
    - L3 应用层: 文档模板和生成规则
    - L4 用户层: 企业特定的历史数据和偏好
    
    同时整合行业知识库 (industry_kb)，为consult模块提供：
    - 统一的知识查询接口
    - 文档生成上下文构建
    - 行业特定的生成建议
    """
    
    def __init__(self):
        """初始化统一知识库管理器"""
        # L1 标准层: ISO标准知识库
        self._iso_kb: Optional[ISOStandardsKnowledgeBase] = None
        
        # 行业知识库
        self._industry_kb: Optional[IndustryKnowledgeBase] = None
        
        # L2 经验层: 行业经验数据缓存
        self._industry_experience_cache: Dict[str, Any] = {}
        
        # L3 应用层: 文档模板配置
        self._template_config: Dict[str, Any] = {}
        
        # L4 用户层: 企业特定数据缓存
        self._company_cache: Dict[str, Any] = {}
        
        self._initialized = False
    
    def _ensure_initialized(self) -> None:
        """确保知识库已初始化"""
        if not self._initialized:
            self._initialize_kbs()
    
    def _initialize_kbs(self) -> None:
        """初始化各层知识库"""
        try:
            # 初始化L1标准层
            self._iso_kb = get_knowledge_base()
            
            # 初始化行业知识库
            self._industry_kb = get_industry_kb()
            
            self._initialized = True
        except Exception as e:
            raise RuntimeError(f"知识库初始化失败: {e}")
    
    # ==================== L1 标准层接口 ====================
    
    def query_clause(self, standard: str, clause: str) -> Optional[ClauseKnowledge]:
        """
        查询条款知识 (L1标准层)
        
        Args:
            standard: 标准代码，如 "ISO9001:2015"
            clause: 条款号，如 "4.1"
            
        Returns:
            条款知识对象，未找到返回None
        """
        self._ensure_initialized()
        
        if not self._iso_kb:
            return None
        
        clause_data = self._iso_kb.get_clause(standard, clause)
        if not clause_data:
            return None
        
        # 构建文档生成提示
        document_hints = self._build_document_hints(standard, clause)
        
        return ClauseKnowledge(
            standard=standard,
            clause=clause,
            title=clause_data.get("title", ""),
            content=clause_data.get("content", ""),
            key_points=clause_data.get("key_points", []),
            implementation_guidance=clause_data.get("implementation_guidance", ""),
            document_hints=document_hints
        )
    
    def query_clauses_batch(
        self, 
        clause_queries: List[Tuple[str, str]]
    ) -> List[ClauseKnowledge]:
        """
        批量查询条款知识
        
        Args:
            clause_queries: 查询列表，每项为 (standard, clause) 元组
            
        Returns:
            条款知识对象列表
        """
        self._ensure_initialized()
        
        results = []
        for standard, clause in clause_queries:
            knowledge = self.query_clause(standard, clause)
            if knowledge:
                results.append(knowledge)
        
        return results
    
    def search_clauses(
        self, 
        keyword: str, 
        standards: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        搜索条款
        
        Args:
            keyword: 搜索关键词
            standards: 标准代码列表，None则搜索所有标准
            
        Returns:
            按标准分组的匹配条款
        """
        self._ensure_initialized()
        
        if not self._iso_kb:
            return {}
        
        return self._iso_kb.search_clauses(keyword, standards)
    
    # ==================== 行业知识库接口 ====================
    
    def query_industry_context(
        self, 
        industry_code: str,
        company_info: Optional[Dict[str, Any]] = None
    ) -> Optional[IndustryContext]:
        """
        查询行业上下文 (适配consult)
        
        根据行业代码获取行业特定的上下文信息，
        用于指导体系文件生成。
        
        Args:
            industry_code: 行业代码，如 "33" (信息技术)
            company_info: 企业信息（可选），用于增强上下文
            
        Returns:
            行业上下文对象，未找到返回None
        """
        self._ensure_initialized()
        
        if not self._industry_kb:
            return None
        
        industry = self._industry_kb.get_industry_by_code(industry_code)
        if not industry:
            return None
        
        # 获取文档生成提示
        generation_hints = self._industry_kb.get_document_generation_hints(industry_code)
        
        return IndustryContext(
            industry_code=industry_code,
            industry_name=industry.name,
            key_departments=industry.key_departments,
            key_processes=industry.key_processes,
            regulations=industry.regulations,
            priority_clauses=industry.related_clauses_priority,
            document_generation_hints=generation_hints
        )
    
    def match_industry(
        self,
        company_name: str = "",
        business_scope: str = "",
        products_services: str = "",
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        根据企业信息匹配行业
        
        Args:
            company_name: 企业名称
            business_scope: 经营范围
            products_services: 产品/服务描述
            top_n: 返回最匹配的前N个行业
            
        Returns:
            行业匹配结果列表
        """
        self._ensure_initialized()
        
        if not self._industry_kb:
            return []
        
        matches = self._industry_kb.match_industry(
            company_name, business_scope, products_services, top_n
        )
        
        return [
            {
                "industry_code": match.industry.code,
                "industry_name": match.industry.name,
                "match_score": match.match_score,
                "matched_keywords": match.matched_keywords
            }
            for match in matches
        ]
    
    def get_industry_checklist(self, industry_code: str) -> List[Dict[str, Any]]:
        """
        获取行业检查清单（适配consult）
        
        Args:
            industry_code: 行业代码
            
        Returns:
            检查清单项列表
        """
        self._ensure_initialized()
        
        if not self._industry_kb:
            return []
        
        return self._industry_kb.get_industry_checklist(industry_code)
    
    # ==================== 统一上下文生成接口 ====================
    
    def generate_document_context(
        self,
        standard: str,
        clause: str,
        department: str,
        company_id: str,
        industry_code: Optional[str] = None
    ) -> Optional[DocumentContext]:
        """
        生成文档生成的完整上下文
        
        整合L1-L4层知识，构建文档生成所需的完整上下文。
        
        Args:
            standard: 标准代码，如 "ISO9001:2015"
            clause: 条款号，如 "4.1"
            department: 部门名称
            company_id: 企业ID
            industry_code: 行业代码（可选）
            
        Returns:
            文档生成上下文对象
        """
        self._ensure_initialized()
        
        # L1: 获取条款知识
        clause_knowledge = self.query_clause(standard, clause)
        if not clause_knowledge:
            return None
        
        # 行业上下文
        industry_context = None
        industry_name = None
        if industry_code:
            industry_ctx = self.query_industry_context(industry_code)
            if industry_ctx:
                industry_context = {
                    "code": industry_ctx.industry_code,
                    "name": industry_ctx.industry_name,
                    "key_departments": industry_ctx.key_departments,
                    "key_processes": industry_ctx.key_processes,
                    "regulations": industry_ctx.regulations
                }
                industry_name = industry_ctx.industry_name
        
        # L3: 获取模板建议
        template_suggestions = self._get_template_suggestions(
            standard, clause, department, industry_code
        )
        
        # L4: 获取企业特定生成提示
        generation_hints = self._get_company_generation_hints(
            company_id, standard, clause, department
        )
        
        return DocumentContext(
            standard=standard,
            clause=clause,
            department=department,
            company_id=company_id,
            industry_code=industry_code,
            industry_name=industry_name,
            clause_knowledge=clause_knowledge,
            industry_context=industry_context,
            template_suggestions=template_suggestions,
            generation_hints=generation_hints
        )
    
    def get_document_template_suggestions(
        self,
        industry_code: str,
        document_type: str
    ) -> List[Dict[str, Any]]:
        """
        获取文档模板建议（consult特有）
        
        根据行业和文档类型，推荐合适的模板和生成策略。
        
        Args:
            industry_code: 行业代码
            document_type: 文档类型，如 "manual", "procedure", "instruction", "record"
            
        Returns:
            模板建议列表
        """
        self._ensure_initialized()
        
        suggestions = []
        
        # 获取行业信息
        if self._industry_kb:
            industry = self._industry_kb.get_industry_by_code(industry_code)
            if industry:
                # 根据文档类型和行业特点生成建议
                if document_type == "manual":
                    # 质量手册建议
                    suggestions.append({
                        "template_type": "质量手册",
                        "priority_clauses": industry.related_clauses_priority[:5],
                        "key_sections": ["组织环境", "领导作用", "策划", "支持", "运行", "评价", "改进"],
                        "industry_specific": industry.key_departments[:3]
                    })
                
                elif document_type == "procedure":
                    # 程序文件建议
                    for process in industry.key_processes[:3]:
                        suggestions.append({
                            "template_type": "程序文件",
                            "process_name": process,
                            "applicable_departments": industry.key_departments[:2],
                            "priority": "high" if process in industry.key_processes[:2] else "medium"
                        })
                
                elif document_type == "instruction":
                    # 作业指导书建议
                    suggestions.append({
                        "template_type": "作业指导书",
                        "focus_areas": industry.key_processes[:3],
                        "regulatory_requirements": industry.regulations[:3]
                    })
                
                elif document_type == "record":
                    # 记录表单建议
                    suggestions.append({
                        "template_type": "记录表单",
                        "essential_records": ["培训记录", "检验记录", "内审记录", "管评记录"],
                        "industry_specific_records": [f"{dept}工作记录" for dept in industry.key_departments[:2]]
                    })
        
        # 添加通用建议
        suggestions.append({
            "template_type": "通用模板",
            "applicable_standards": ["ISO9001:2015", "ISO14001:2015", "ISO45001:2018"],
            "note": "根据企业实际情况调整"
        })
        
        return suggestions
    
    def _get_template_suggestions(
        self,
        standard: str,
        clause: str,
        department: str,
        industry_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """内部方法：获取模板建议"""
        suggestions = []
        
        # 基于条款确定文档类型
        doc_type = self._determine_document_type(clause)
        
        suggestions.append({
            "document_type": doc_type,
            "standard": standard,
            "clause": clause,
            "department": department,
            "suggested_structure": self._get_suggested_structure(doc_type, clause)
        })
        
        # 如果提供了行业代码，添加行业特定建议
        if industry_code and self._industry_kb:
            industry = self._industry_kb.get_industry_by_code(industry_code)
            if industry:
                suggestions.append({
                    "industry_specific": True,
                    "key_processes_relevant": [
                        p for p in industry.key_processes 
                        if department in str(p) or any(d in str(p) for d in industry.key_departments)
                    ],
                    "applicable_regulations": industry.regulations[:2]
                })
        
        return suggestions
    
    def _get_company_generation_hints(
        self,
        company_id: str,
        standard: str,
        clause: str,
        department: str
    ) -> Dict[str, Any]:
        """内部方法：获取企业特定的生成提示 (L4层)"""
        hints = {
            "company_id": company_id,
            "personalization_enabled": True,
            "suggestions": []
        }
        
        # 这里可以扩展为从数据库加载企业历史偏好
        # 目前返回通用提示
        hints["suggestions"] = [
            "根据企业实际情况调整内容",
            "确保符合部门实际运作流程",
            "参考以往类似文档的格式和风格"
        ]
        
        return hints
    
    def _build_document_hints(self, standard: str, clause: str) -> Dict[str, Any]:
        """内部方法：构建文档生成提示"""
        hints = {
            "standard": standard,
            "clause": clause,
            "document_focus": "",
            "key_elements": []
        }
        
        # 根据条款确定文档重点
        clause_prefix = clause.split(".")[0]
        
        if clause_prefix == "4":
            hints["document_focus"] = "组织环境分析"
            hints["key_elements"] = ["组织环境", "相关方", "体系范围", "过程方法"]
        elif clause_prefix == "5":
            hints["document_focus"] = "领导作用"
            hints["key_elements"] = ["领导承诺", "方针", "职责权限"]
        elif clause_prefix == "6":
            hints["document_focus"] = "策划"
            hints["key_elements"] = ["风险机遇", "目标", "变更策划"]
        elif clause_prefix == "7":
            hints["document_focus"] = "支持"
            hints["key_elements"] = ["资源", "能力", "意识", "沟通", "文件化信息"]
        elif clause_prefix == "8":
            hints["document_focus"] = "运行"
            hints["key_elements"] = ["运行策划", "产品和服务要求", "设计和开发", "外部提供", "生产服务提供"]
        elif clause_prefix == "9":
            hints["document_focus"] = "绩效评价"
            hints["key_elements"] = ["监视测量", "内审", "管评"]
        elif clause_prefix == "10":
            hints["document_focus"] = "改进"
            hints["key_elements"] = ["不合格", "纠正措施", "持续改进"]
        
        return hints
    
    def _determine_document_type(self, clause: str) -> str:
        """内部方法：根据条款确定文档类型"""
        clause_prefix = clause.split(".")[0]
        
        if clause_prefix in ["4", "5"]:
            return "一级文件（手册）"
        elif clause_prefix in ["6", "7", "8"]:
            return "二级文件（程序）"
        elif clause in ["8.5", "8.6", "8.7"]:
            return "三级文件（作业指导书）"
        elif clause_prefix in ["9", "10"]:
            return "四级文件（记录）"
        else:
            return "程序文件"
    
    def _get_suggested_structure(self, doc_type: str, clause: str) -> List[str]:
        """内部方法：获取建议的文档结构"""
        if "一级" in doc_type or "手册" in doc_type:
            return ["目的", "范围", "规范性引用文件", "术语和定义", "组织环境", "领导作用", "策划", "支持", "运行", "绩效评价", "改进"]
        elif "二级" in doc_type or "程序" in doc_type:
            return ["目的", "范围", "职责", "程序内容", "相关文件", "记录表单"]
        elif "三级" in doc_type or "作业指导书" in doc_type:
            return ["作业名称", "适用范围", "职责", "作业准备", "操作步骤", "注意事项", "相关记录"]
        elif "四级" in doc_type or "记录" in doc_type:
            return ["记录名称", "记录编号", "记录内容", "保存期限"]
        else:
            return ["目的", "范围", "职责", "内容", "相关文件"]
    
    # ==================== 统计和查询接口 ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            包含各层知识库统计信息的字典
        """
        self._ensure_initialized()
        
        stats = {
            "unified_kb_version": "1.0.0",
            "layers": {}
        }
        
        # L1 标准层统计
        if self._iso_kb:
            stats["layers"]["L1_standard"] = self._iso_kb.get_statistics()
        
        # 行业知识库统计
        if self._industry_kb:
            stats["layers"]["industry_kb"] = self._industry_kb.get_statistics()
        
        # L2-L4 层统计（当前为缓存状态）
        stats["layers"]["L2_experience"] = {
            "cache_entries": len(self._industry_experience_cache),
            "status": "active"
        }
        
        stats["layers"]["L3_application"] = {
            "template_configs": len(self._template_config),
            "status": "active"
        }
        
        stats["layers"]["L4_user"] = {
            "company_cache_entries": len(self._company_cache),
            "status": "active"
        }
        
        return stats
    
    def list_available_standards(self) -> List[str]:
        """
        列出所有可用的标准
        
        Returns:
            标准代码列表
        """
        self._ensure_initialized()
        
        if not self._iso_kb:
            return []
        
        return self._iso_kb.list_standards()
    
    def list_available_industries(self) -> List[Dict[str, str]]:
        """
        列出所有可用的行业
        
        Returns:
            行业代码和名称列表
        """
        self._ensure_initialized()
        
        if not self._industry_kb:
            return []
        
        industries = self._industry_kb.get_all_industries()
        return [
            {"code": ind.code, "name": ind.name}
            for ind in industries
        ]
    
    def format_context_for_prompt(self, context: DocumentContext) -> str:
        """
        将文档上下文格式化为Prompt文本
        
        Args:
            context: 文档生成上下文
            
        Returns:
            格式化后的Prompt文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append("文档生成上下文")
        lines.append("=" * 60)
        
        # 基本信息
        lines.append(f"\n【标准】{context.standard}")
        lines.append(f"【条款】{context.clause}")
        lines.append(f"【部门】{context.department}")
        if context.industry_name:
            lines.append(f"【行业】{context.industry_name}")
        
        # 条款知识
        if context.clause_knowledge:
            lines.append("\n" + "-" * 60)
            lines.append("【条款知识】")
            lines.append("-" * 60)
            lines.append(f"标题：{context.clause_knowledge.title}")
            lines.append(f"\n内容：\n{context.clause_knowledge.content}")
            
            if context.clause_knowledge.key_points:
                lines.append("\n关键点：")
                for i, point in enumerate(context.clause_knowledge.key_points, 1):
                    lines.append(f"  {i}. {point}")
            
            if context.clause_knowledge.implementation_guidance:
                lines.append(f"\n实施指导：\n{context.clause_knowledge.implementation_guidance}")
        
        # 行业上下文
        if context.industry_context:
            lines.append("\n" + "-" * 60)
            lines.append("【行业上下文】")
            lines.append("-" * 60)
            lines.append(f"行业：{context.industry_context['name']}")
            
            key_depts = context.industry_context.get('key_departments', [])
            if key_depts:
                dept_str = ', '.join(key_depts)
                lines.append(f"\n关键部门：{dept_str}")
            
            key_procs = context.industry_context.get('key_processes', [])
            if key_procs:
                proc_str = ', '.join(key_procs)
                lines.append(f"\n关键过程：{proc_str}")
            
            regs = context.industry_context.get('regulations', [])
            if regs:
                reg_str = ', '.join(regs)
                lines.append(f"\n适用法规：{reg_str}")
        
        # 模板建议
        if context.template_suggestions:
            lines.append("\n" + "-" * 60)
            lines.append("【模板建议】")
            lines.append("-" * 60)
            for suggestion in context.template_suggestions:
                for key, value in suggestion.items():
                    lines.append(f"{key}: {value}")
                lines.append("")
        
        # 生成提示
        if context.generation_hints:
            lines.append("-" * 60)
            lines.append("【生成提示】")
            lines.append("-" * 60)
            suggestions = context.generation_hints.get("suggestions", [])
            for suggestion in suggestions:
                lines.append(f"  - {suggestion}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)


# 全局单例实例
_unified_kb_manager_instance: Optional[UnifiedKnowledgeManager] = None


def get_unified_kb_manager() -> UnifiedKnowledgeManager:
    """
    获取统一知识库管理器单例实例
    
    Returns:
        UnifiedKnowledgeManager实例
    """
    global _unified_kb_manager_instance
    if _unified_kb_manager_instance is None:
        _unified_kb_manager_instance = UnifiedKnowledgeManager()
    return _unified_kb_manager_instance


def reset_unified_kb_manager() -> None:
    """重置统一知识库管理器单例"""
    global _unified_kb_manager_instance
    _unified_kb_manager_instance = None


# ==================== 便捷函数 ====================

def query_clause(standard: str, clause: str) -> Optional[ClauseKnowledge]:
    """便捷函数：查询条款知识"""
    return get_unified_kb_manager().query_clause(standard, clause)


def query_industry_context(
    industry_code: str,
    company_info: Optional[Dict[str, Any]] = None
) -> Optional[IndustryContext]:
    """便捷函数：查询行业上下文"""
    return get_unified_kb_manager().query_industry_context(industry_code, company_info)


def generate_document_context(
    standard: str,
    clause: str,
    department: str,
    company_id: str,
    industry_code: Optional[str] = None
) -> Optional[DocumentContext]:
    """便捷函数：生成文档生成上下文"""
    return get_unified_kb_manager().generate_document_context(
        standard, clause, department, company_id, industry_code
    )


def get_document_template_suggestions(
    industry_code: str,
    document_type: str
) -> List[Dict[str, Any]]:
    """便捷函数：获取文档模板建议"""
    return get_unified_kb_manager().get_document_template_suggestions(
        industry_code, document_type
    )


def get_statistics() -> Dict[str, Any]:
    """便捷函数：获取知识库统计"""
    return get_unified_kb_manager().get_statistics()