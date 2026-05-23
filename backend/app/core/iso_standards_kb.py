"""
ISO标准知识库模块
从audit模块复用并适配consult需求

提供ISO标准条款的查询、格式化等功能，用于咨询场景
支持的标准：ISO9001:2015、ISO14001:2015、ISO45001:2018
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path


class ISOStandardsKnowledgeBase:
    """ISO标准知识库类"""
    
    def __init__(self, knowledge_file: Optional[str] = None):
        """
        初始化知识库
        
        Args:
            knowledge_file: 知识库JSON文件路径，默认为模块所在目录下的data/iso_standards_knowledge.json
        """
        self.knowledge_data: Dict[str, Any] = {}
        self.standards: Dict[str, Dict[str, Any]] = {}
        self.metadata: Dict[str, Any] = {}
        
        if knowledge_file is None:
            # 默认路径：模块所在目录下的data文件夹
            module_dir = Path(__file__).parent
            knowledge_file = module_dir / "data" / "iso_standards_knowledge.json"
        
        self.knowledge_file = Path(knowledge_file)
        self.load()
    
    def load(self) -> None:
        """
        加载知识库JSON文件
        
        Raises:
            FileNotFoundError: 当知识库文件不存在时
            json.JSONDecodeError: 当JSON格式不正确时
        """
        if not self.knowledge_file.exists():
            raise FileNotFoundError(f"知识库文件不存在: {self.knowledge_file}")
        
        with open(self.knowledge_file, 'r', encoding='utf-8') as f:
            self.knowledge_data = json.load(f)
        
        self.metadata = self.knowledge_data.get("metadata", {})
        self.standards = self.knowledge_data.get("standards", {})
    
    def reload(self) -> None:
        """重新加载知识库"""
        self.load()
    
    def get_clause(self, standard: str, clause_num: str) -> Optional[Dict[str, Any]]:
        """
        获取指定条款
        
        Args:
            standard: 标准代码，如 "ISO9001:2015"
            clause_num: 条款号，如 "4.1"
        
        Returns:
            条款字典，包含clause、title、content、key_points、implementation_guidance等字段
            如果未找到则返回None
        """
        if standard not in self.standards:
            return None
        
        clauses = self.standards[standard].get("clauses", [])
        for clause in clauses:
            if clause.get("clause") == clause_num:
                return clause
        
        return None
    
    def get_clauses_by_standard(self, standard: str) -> List[Dict[str, Any]]:
        """
        获取标准所有条款
        
        Args:
            standard: 标准代码，如 "ISO9001:2015"
        
        Returns:
            条款列表，如果标准不存在则返回空列表
        """
        if standard not in self.standards:
            return []
        
        return self.standards[standard].get("clauses", [])
    
    def get_clauses_by_numbers(
        self, 
        clause_numbers: List[str], 
        standards: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量获取条款
        
        Args:
            clause_numbers: 条款号列表，如 ["4.1", "5.1"]
            standards: 标准代码列表，如 ["ISO9001:2015"]
                    如果为None，则在所有标准中搜索
        
        Returns:
            按标准分组的条款字典，格式：{standard: [clause1, clause2, ...]}
        """
        if standards is None:
            standards = list(self.standards.keys())
        
        result = {}
        for standard in standards:
            if standard not in self.standards:
                continue
            
            clauses = []
            for clause_num in clause_numbers:
                clause = self.get_clause(standard, clause_num)
                if clause:
                    clauses.append(clause)
            
            if clauses:
                result[standard] = clauses
        
        return result
    
    def format_clauses_for_prompt(
        self, 
        clause_numbers: List[str], 
        standards: Optional[List[str]] = None,
        include_guidance: bool = True
    ) -> str:
        """
        将条款格式化为Prompt文本
        
        Args:
            clause_numbers: 条款号列表
            standards: 标准代码列表，如果为None则在所有标准中搜索
            include_guidance: 是否包含实施指导
        
        Returns:
            格式化后的文本，适合用于LLM Prompt
        """
        clauses_by_standard = self.get_clauses_by_numbers(clause_numbers, standards)
        
        if not clauses_by_standard:
            return "未找到指定的ISO标准条款。"
        
        lines = []
        lines.append("=" * 60)
        lines.append("ISO标准条款参考")
        lines.append("=" * 60)
        
        for standard, clauses in clauses_by_standard.items():
            standard_info = self.standards.get(standard, {})
            lines.append(f"\n【{standard} - {standard_info.get('title', '')}】")
            lines.append(f"描述：{standard_info.get('description', '')}")
            lines.append("-" * 60)
            
            for clause in clauses:
                lines.append(f"\n### 条款 {clause.get('clause', '')} - {clause.get('title', '')}")
                lines.append(f"\n**内容：**")
                lines.append(clause.get('content', ''))
                
                # 关键点
                key_points = clause.get('key_points', [])
                if key_points:
                    lines.append(f"\n**关键点：**")
                    for i, point in enumerate(key_points, 1):
                        lines.append(f"{i}. {point}")
                
                # 实施指导
                if include_guidance:
                    guidance = clause.get('implementation_guidance', '')
                    if guidance:
                        lines.append(f"\n**实施指导：**")
                        lines.append(guidance)
                
                lines.append("")
        
        return "\n".join(lines)
    
    def get_implementation_guidance(
        self, 
        clause_numbers: List[str], 
        standards: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        获取实施指导（consult专用，替代audit的审核指导）
        
        Args:
            clause_numbers: 条款号列表
            standards: 标准代码列表，如果为None则在所有标准中搜索
        
        Returns:
            实施指导字典，格式：{standard: {clause_num: guidance}}
        """
        clauses_by_standard = self.get_clauses_by_numbers(clause_numbers, standards)
        
        result = {}
        for standard, clauses in clauses_by_standard.items():
            result[standard] = {}
            for clause in clauses:
                clause_num = clause.get("clause", "")
                guidance = clause.get("implementation_guidance", "")
                if guidance:
                    result[standard][clause_num] = guidance
        
        return result
    
    def format_all_clauses_for_prompt(self, standard: str) -> str:
        """
        格式化指定标准的全部条款
        
        Args:
            standard: 标准代码，如 "ISO9001:2015"
        
        Returns:
            格式化后的完整条款文本
        """
        if standard not in self.standards:
            return f"未找到标准：{standard}"
        
        standard_info = self.standards[standard]
        clauses = standard_info.get("clauses", [])
        
        lines = []
        lines.append("=" * 60)
        lines.append(f"{standard} 完整条款")
        lines.append(f"{standard_info.get('title', '')}")
        lines.append("=" * 60)
        lines.append(f"\n{standard_info.get('description', '')}\n")
        
        for clause in clauses:
            lines.append(f"\n{'=' * 60}")
            lines.append(f"条款 {clause.get('clause', '')} - {clause.get('title', '')}")
            lines.append(f"{'=' * 60}")
            
            lines.append(f"\n【内容】")
            lines.append(clause.get('content', ''))
            
            # 关键点
            key_points = clause.get('key_points', [])
            if key_points:
                lines.append(f"\n【关键点】")
                for i, point in enumerate(key_points, 1):
                    lines.append(f"{i}. {point}")
            
            # 实施指导
            guidance = clause.get('implementation_guidance', '')
            if guidance:
                lines.append(f"\n【实施指导】")
                lines.append(guidance)
        
        return "\n".join(lines)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典，包含：
            - total_standards: 标准总数
            - standards: 各标准的统计信息
            - version: 知识库版本
            - last_updated: 最后更新时间
        """
        stats = {
            "total_standards": len(self.standards),
            "standards": {},
            "version": self.metadata.get("version", "unknown"),
            "last_updated": self.metadata.get("last_updated", "unknown"),
            "description": self.metadata.get("description", "")
        }
        
        for standard, data in self.standards.items():
            clauses = data.get("clauses", [])
            stats["standards"][standard] = {
                "name": data.get("name", standard),
                "title": data.get("title", ""),
                "clause_count": len(clauses),
                "clauses": [c.get("clause", "") for c in clauses]
            }
        
        return stats
    
    def search_clauses(
        self, 
        keyword: str, 
        standards: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        搜索条款
        
        Args:
            keyword: 搜索关键词
            standards: 标准代码列表，如果为None则在所有标准中搜索
        
        Returns:
            按标准分组的匹配条款字典
        """
        if standards is None:
            standards = list(self.standards.keys())
        
        result = {}
        keyword_lower = keyword.lower()
        
        for standard in standards:
            if standard not in self.standards:
                continue
            
            matching_clauses = []
            for clause in self.standards[standard].get("clauses", []):
                # 在标题、内容、关键点中搜索
                searchable_text = " ".join([
                    clause.get("title", ""),
                    clause.get("content", ""),
                    " ".join(clause.get("key_points", []))
                ]).lower()
                
                if keyword_lower in searchable_text:
                    matching_clauses.append(clause)
            
            if matching_clauses:
                result[standard] = matching_clauses
        
        return result
    
    def get_standard_info(self, standard: str) -> Optional[Dict[str, Any]]:
        """
        获取标准信息
        
        Args:
            standard: 标准代码
        
        Returns:
            标准信息字典，包含name、title、description等
        """
        if standard not in self.standards:
            return None
        
        return {
            "name": self.standards[standard].get("name", standard),
            "title": self.standards[standard].get("title", ""),
            "description": self.standards[standard].get("description", ""),
            "clause_count": len(self.standards[standard].get("clauses", []))
        }
    
    def list_standards(self) -> List[str]:
        """
        列出所有可用的标准代码
        
        Returns:
            标准代码列表
        """
        return list(self.standards.keys())


# 全局知识库实例（单例模式）
_kb_instance: Optional[ISOStandardsKnowledgeBase] = None


def get_knowledge_base(knowledge_file: Optional[str] = None) -> ISOStandardsKnowledgeBase:
    """
    获取知识库单例实例
    
    Args:
        knowledge_file: 知识库文件路径，首次调用时有效
    
    Returns:
        ISOStandardsKnowledgeBase实例
    """
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = ISOStandardsKnowledgeBase(knowledge_file)
    return _kb_instance


def reset_knowledge_base() -> None:
    """重置知识库单例（用于重新加载）"""
    global _kb_instance
    _kb_instance = None


# 便捷函数
def get_clause(standard: str, clause_num: str) -> Optional[Dict[str, Any]]:
    """便捷函数：获取指定条款"""
    return get_knowledge_base().get_clause(standard, clause_num)


def format_clauses_for_prompt(
    clause_numbers: List[str], 
    standards: Optional[List[str]] = None
) -> str:
    """便捷函数：格式化条款为Prompt文本"""
    return get_knowledge_base().format_clauses_for_prompt(clause_numbers, standards)


def get_implementation_guidance(
    clause_numbers: List[str], 
    standards: Optional[List[str]] = None
) -> Dict[str, Dict[str, str]]:
    """便捷函数：获取实施指导"""
    return get_knowledge_base().get_implementation_guidance(clause_numbers, standards)
