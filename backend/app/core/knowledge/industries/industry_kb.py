"""
行业知识库核心类

适配consult模块的业务场景，用于生成体系文件而非审核记录。
功能包括：
- 加载行业注册表数据
- 根据企业信息自动匹配行业（使用关键词匹配）
- 获取行业审核要点、典型NC、检查清单、法规要求
- 获取行业统计信息
"""

import json
import os
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class IndustryInfo:
    """行业信息数据类"""
    code: str
    name: str
    name_en: str
    sub_categories_count: int
    detail_categories_count: int
    keywords: List[str] = field(default_factory=list)
    related_clauses_priority: List[str] = field(default_factory=list)
    key_departments: List[str] = field(default_factory=list)
    key_processes: List[str] = field(default_factory=list)
    regulations: List[str] = field(default_factory=list)
    data_status: str = "template"  # template, partial, enriched


@dataclass
class IndustryMatchResult:
    """行业匹配结果"""
    industry: IndustryInfo
    match_score: float
    matched_keywords: List[str]


class IndustryKnowledgeBase:
    """
    行业知识库核心类
    
    用于consult模块，支持体系文件生成场景：
    - 根据企业信息自动识别行业
    - 获取行业特定的体系文件要求
    - 获取行业法规和标准要求
    - 获取行业关键部门和过程信息
    """
    
    def __init__(self, registry_path: Optional[str] = None):
        """
        初始化行业知识库
        
        Args:
            registry_path: 行业注册表JSON文件路径，默认为模块目录下的industry_registry.json
        """
        if registry_path is None:
            current_dir = Path(__file__).parent
            registry_path = current_dir / "industry_registry.json"
        
        self.registry_path = Path(registry_path)
        self._industries: Dict[str, IndustryInfo] = {}
        self._registry_data: Dict[str, Any] = {}
        self._loaded = False
        
        self._load_registry()
    
    def _load_registry(self) -> None:
        """加载行业注册表数据"""
        if not self.registry_path.exists():
            raise FileNotFoundError(f"行业注册表文件不存在: {self.registry_path}")
        
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self._registry_data = json.load(f)
            
            for industry_data in self._registry_data.get("industries", []):
                industry = IndustryInfo(
                    code=industry_data["code"],
                    name=industry_data["name"],
                    name_en=industry_data["name_en"],
                    sub_categories_count=industry_data["sub_categories_count"],
                    detail_categories_count=industry_data["detail_categories_count"],
                    keywords=industry_data.get("keywords", []),
                    related_clauses_priority=industry_data.get("related_clauses_priority", []),
                    key_departments=industry_data.get("key_departments", []),
                    key_processes=industry_data.get("key_processes", []),
                    regulations=industry_data.get("regulations", []),
                    data_status=industry_data.get("data_status", "template")
                )
                self._industries[industry.code] = industry
            
            self._loaded = True
        except json.JSONDecodeError as e:
            raise ValueError(f"行业注册表JSON格式错误: {e}")
        except KeyError as e:
            raise ValueError(f"行业注册表缺少必要字段: {e}")
    
    @property
    def is_loaded(self) -> bool:
        """检查知识库是否已加载"""
        return self._loaded
    
    @property
    def version(self) -> str:
        """获取知识库版本"""
        return self._registry_data.get("version", "unknown")
    
    @property
    def source(self) -> str:
        """获取知识库数据来源"""
        return self._registry_data.get("source", "")
    
    def get_all_industries(self) -> List[IndustryInfo]:
        """
        获取所有行业信息
        
        Returns:
            行业信息列表
        """
        return list(self._industries.values())
    
    def get_industry_by_code(self, code: str) -> Optional[IndustryInfo]:
        """
        根据行业代码获取行业信息
        
        Args:
            code: 行业代码（如 "01", "33"）
            
        Returns:
            行业信息，未找到返回None
        """
        return self._industries.get(code)
    
    def get_industry_by_name(self, name: str) -> Optional[IndustryInfo]:
        """
        根据行业名称获取行业信息（支持模糊匹配）
        
        Args:
            name: 行业名称
            
        Returns:
            行业信息，未找到返回None
        """
        # 精确匹配
        for industry in self._industries.values():
            if industry.name == name or industry.name_en == name:
                return industry
        
        # 模糊匹配
        name_lower = name.lower()
        for industry in self._industries.values():
            if name_lower in industry.name.lower() or name_lower in industry.name_en.lower():
                return industry
            # 检查关键词
            for keyword in industry.keywords:
                if name_lower in keyword.lower() or keyword.lower() in name_lower:
                    return industry
        
        return None
    
    def match_industry(
        self, 
        company_name: str = "",
        business_scope: str = "",
        products_services: str = "",
        top_n: int = 3
    ) -> List[IndustryMatchResult]:
        """
        根据企业信息自动匹配行业
        
        使用关键词匹配算法，根据企业名称、经营范围、产品服务等信息
        匹配最合适的行业。
        
        Args:
            company_name: 企业名称
            business_scope: 经营范围
            products_services: 产品/服务描述
            top_n: 返回最匹配的前N个行业
            
        Returns:
            行业匹配结果列表，按匹配分数降序排列
        """
        # 合并所有文本信息
        combined_text = f"{company_name} {business_scope} {products_services}".lower()
        
        results = []
        
        for industry in self._industries.values():
            score = 0.0
            matched_keywords = []
            
            # 关键词匹配
            for keyword in industry.keywords:
                keyword_lower = keyword.lower()
                # 完整匹配得分更高
                if keyword_lower in combined_text:
                    count = combined_text.count(keyword_lower)
                    score += count * 10
                    matched_keywords.append(keyword)
                # 部分匹配
                elif len(keyword) >= 3:
                    for part in combined_text.split():
                        if keyword_lower in part or part in keyword_lower:
                            score += 3
                            if keyword not in matched_keywords:
                                matched_keywords.append(keyword)
                            break
            
            # 行业名称匹配
            if industry.name.lower() in combined_text:
                score += 20
            for part in industry.name.split("。"):
                if part and part.lower() in combined_text:
                    score += 10
            
            # 去除重复关键词
            matched_keywords = list(set(matched_keywords))
            
            if score > 0:
                results.append(IndustryMatchResult(
                    industry=industry,
                    match_score=score,
                    matched_keywords=matched_keywords
                ))
        
        # 按匹配分数降序排列
        results.sort(key=lambda x: x.match_score, reverse=True)
        
        return results[:top_n]
    
    def get_industry_key_departments(self, industry_code: str) -> List[str]:
        """
        获取行业关键部门
        
        Args:
            industry_code: 行业代码
            
        Returns:
            关键部门列表
        """
        industry = self.get_industry_by_code(industry_code)
        if industry:
            return industry.key_departments
        return []
    
    def get_industry_key_processes(self, industry_code: str) -> List[str]:
        """
        获取行业关键过程
        
        Args:
            industry_code: 行业代码
            
        Returns:
            关键过程列表
        """
        industry = self.get_industry_by_code(industry_code)
        if industry:
            return industry.key_processes
        return []
    
    def get_industry_regulations(self, industry_code: str) -> List[str]:
        """
        获取行业法规要求
        
        Args:
            industry_code: 行业代码
            
        Returns:
            法规要求列表
        """
        industry = self.get_industry_by_code(industry_code)
        if industry:
            return industry.regulations
        return []
    
    def get_priority_clauses(self, industry_code: str) -> List[str]:
        """
        获取行业优先关注的标准条款
        
        Args:
            industry_code: 行业代码
            
        Returns:
            优先条款列表（如 ["8.5.1", "8.6"]）
        """
        industry = self.get_industry_by_code(industry_code)
        if industry:
            return industry.related_clauses_priority
        return []
    
    def get_document_generation_hints(self, industry_code: str) -> Dict[str, Any]:
        """
        获取行业文档生成提示
        
        为consult模块的文档生成提供行业特定的指导信息。
        
        Args:
            industry_code: 行业代码
            
        Returns:
            文档生成提示信息，包括：
            - 关键部门（用于组织架构）
            - 关键过程（用于程序文件）
            - 优先条款（用于手册重点）
            - 法规要求（用于合规性引用）
        """
        industry = self.get_industry_by_code(industry_code)
        if not industry:
            return {
                "industry_name": "通用",
                "key_departments": [],
                "key_processes": [],
                "priority_clauses": [],
                "regulations": [],
                "data_status": "template"
            }
        
        return {
            "industry_name": industry.name,
            "key_departments": industry.key_departments,
            "key_processes": industry.key_processes,
            "priority_clauses": industry.related_clauses_priority,
            "regulations": industry.regulations,
            "data_status": industry.data_status
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取行业知识库统计信息
        
        Returns:
            统计信息字典
        """
        stats = self._registry_data.get("statistics", {})
        
        # 计算额外统计
        data_status_counts = {"template": 0, "partial": 0, "enriched": 0}
        for industry in self._industries.values():
            status = industry.data_status
            if status in data_status_counts:
                data_status_counts[status] += 1
        
        return {
            "total_industries": len(self._industries),
            "version": self.version,
            "source": self.source,
            "created_at": self._registry_data.get("created_at", ""),
            "data_status_distribution": data_status_counts,
            **stats
        }
    
    def search_industries(self, keyword: str) -> List[IndustryInfo]:
        """
        搜索行业
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的行业列表
        """
        keyword_lower = keyword.lower()
        results = []
        
        for industry in self._industries.values():
            # 检查名称
            if (keyword_lower in industry.name.lower() or 
                keyword_lower in industry.name_en.lower()):
                results.append(industry)
                continue
            
            # 检查关键词
            for kw in industry.keywords:
                if keyword_lower in kw.lower():
                    results.append(industry)
                    break
        
        return results
    
    def get_industry_checklist(self, industry_code: str) -> List[Dict[str, Any]]:
        """
        获取行业检查清单（适配consult模块）
        
        生成适用于体系文件生成的检查清单，而非审核检查清单。
        
        Args:
            industry_code: 行业代码
            
        Returns:
            检查清单项列表
        """
        industry = self.get_industry_by_code(industry_code)
        if not industry:
            return []
        
        checklist = []
        
        # 基于关键过程生成检查项
        for process in industry.key_processes:
            checklist.append({
                "category": "关键过程",
                "item": f"是否建立了{process}的相关程序文件？",
                "priority": "high"
            })
            checklist.append({
                "category": "关键过程",
                "item": f"{process}的作业指导书是否完整？",
                "priority": "medium"
            })
        
        # 基于关键部门生成检查项
        for dept in industry.key_departments:
            checklist.append({
                "category": "组织架构",
                "item": f"{dept}的职责是否在手册中明确？",
                "priority": "high"
            })
        
        # 基于法规要求生成检查项
        for regulation in industry.regulations:
            checklist.append({
                "category": "法规合规",
                "item": f"是否识别并引用了{regulation}的相关要求？",
                "priority": "high"
            })
        
        return checklist
    
    def get_typical_nc(self, industry_code: str) -> List[Dict[str, Any]]:
        """
        获取行业典型不符合项（适配consult模块）
        
        提供该行业常见的不符合项示例，用于指导体系文件编写时避免。
        
        Args:
            industry_code: 行业代码
            
        Returns:
            典型不符合项列表
        """
        # 这里可以扩展为从数据库或配置文件加载
        # 目前返回基于行业的通用典型NC
        
        industry = self.get_industry_by_code(industry_code)
        if not industry:
            return []
        
        typical_ncs = {
            "03": [  # 食品、饮料和烟草
                {"clause": "8.5.1", "description": "生产过程中的关键控制点未有效监控"},
                {"clause": "8.6", "description": "产品检验记录不完整，无法追溯"},
                {"clause": "7.1.5", "description": "检验设备未按期校准"},
            ],
            "33": [  # 信息技术
                {"clause": "8.3", "description": "软件设计开发过程缺少设计评审记录"},
                {"clause": "8.2", "description": "客户需求确认记录不完整"},
            ],
            "01": [  # 农业、林业和渔业
                {"clause": "8.5.1", "description": "农药使用记录不完整"},
                {"clause": "8.6", "description": "农产品检验记录缺失"},
            ],
        }
        
        return typical_ncs.get(industry_code, [
            {"clause": "8.5.1", "description": "过程控制文件不完整"},
            {"clause": "8.6", "description": "检验记录不完整"},
        ])


# 全局知识库实例（单例模式）
_industry_kb_instance: Optional[IndustryKnowledgeBase] = None


def get_industry_kb() -> IndustryKnowledgeBase:
    """
    获取行业知识库单例实例
    
    Returns:
        IndustryKnowledgeBase实例
    """
    global _industry_kb_instance
    if _industry_kb_instance is None:
        _industry_kb_instance = IndustryKnowledgeBase()
    return _industry_kb_instance
