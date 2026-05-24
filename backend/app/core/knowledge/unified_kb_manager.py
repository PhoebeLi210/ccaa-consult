"""
统一知识库管理器模块

整合四层知识库，提供统一的知识查询和管理接口。

功能:
- 统一查询接口: 跨层级知识检索
- 优先级管理: 按层级优先级返回结果
- 知识融合: 整合多层知识
- 缓存机制: 提高查询效率
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time
import threading
from functools import lru_cache

from .knowledge_base import (
    KnowledgeBase,
    KnowledgeItem,
    KnowledgeLevel,
    KnowledgeQuery,
    KnowledgeResult,
)
from .standard_kb import StandardKB
from .experience_kb import ExperienceKB
from .application_kb import ApplicationKB
from .user_kb import UserKB


class QueryPriority(Enum):
    """查询优先级策略"""
    STANDARD_FIRST = "标准优先"  # L1 > L2 > L3 > L4
    USER_FIRST = "用户优先"  # L4 > L3 > L2 > L1
    BALANCED = "均衡模式"  # 按相关性排序
    COMPREHENSIVE = "综合模式"  # 返回所有层级结果


@dataclass
class KnowledgeContext:
    """
    知识上下文数据类
    
    Attributes:
        user_id: 当前用户ID
        industry: 当前行业
        standards: 关注的标准列表
        query_history: 查询历史
        session_data: 会话数据
    """
    
    user_id: str = ""
    industry: str = ""
    standards: List[str] = field(default_factory=list)
    query_history: List[str] = field(default_factory=list)
    session_data: Dict[str, Any] = field(default_factory=dict)
    
    def add_query(self, query: str):
        """添加查询到历史"""
        self.query_history.append(query)
        # 保持最近20条记录
        if len(self.query_history) > 20:
            self.query_history = self.query_history[-20:]


@dataclass
class UnifiedQueryResult:
    """
    统一查询结果数据类
    
    Attributes:
        items: 合并后的知识项列表
        total_count: 总数量
        level_results: 各层级结果
        context: 查询上下文
        execution_time: 执行时间
        suggestions: 建议
        related_queries: 相关查询建议
    """
    
    items: List[KnowledgeItem] = field(default_factory=list)
    total_count: int = 0
    level_results: Dict[str, KnowledgeResult] = field(default_factory=dict)
    context: Optional[KnowledgeContext] = None
    execution_time: float = 0.0
    suggestions: List[str] = field(default_factory=list)
    related_queries: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "items": [item.to_dict() for item in self.items],
            "total_count": self.total_count,
            "level_results": {
                level: result.to_dict() 
                for level, result in self.level_results.items()
            },
            "execution_time": self.execution_time,
            "suggestions": self.suggestions,
            "related_queries": self.related_queries,
        }
    
    def get_items_by_level(self, level: KnowledgeLevel) -> List[KnowledgeItem]:
        """获取指定层级的知识项"""
        return [item for item in self.items if item.level == level]


class UnifiedKBManager:
    """
    统一知识库管理器
    
    整合四层知识库，提供统一的知识查询和管理接口。
    
    功能:
    - 初始化和管理四层知识库
    - 提供统一的查询接口
    - 支持多种查询优先级策略
    - 知识缓存和预加载
    - 用户上下文管理
    
    使用示例:
        manager = UnifiedKBManager()
        manager.initialize()
        
        result = manager.query("ISO9001 质量管理体系")
        for item in result.items:
            print(item.title)
    """
    
    def __init__(self, user_id: str = ""):
        """
        初始化统一知识库管理器
        
        Args:
            user_id: 当前用户ID
        """
        # 四层知识库实例
        self._standard_kb: Optional[StandardKB] = None
        self._experience_kb: Optional[ExperienceKB] = None
        self._application_kb: Optional[ApplicationKB] = None
        self._user_kb: Optional[UserKB] = None
        
        # 知识库映射
        self._kb_map: Dict[KnowledgeLevel, KnowledgeBase] = {}
        
        # 当前上下文
        self._context = KnowledgeContext(user_id=user_id)
        
        # 初始化状态
        self._initialized = False
        
        # 缓存
        self._cache: Dict[str, Tuple[UnifiedQueryResult, float]] = {}
        self._cache_lock = threading.Lock()
        self._cache_ttl = 300  # 缓存有效期（秒）
    
    @property
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized
    
    @property
    def context(self) -> KnowledgeContext:
        """获取当前上下文"""
        return self._context
    
    def set_user(self, user_id: str):
        """
        设置当前用户
        
        Args:
            user_id: 用户ID
        """
        self._context.user_id = user_id
        if self._user_kb:
            self._user_kb.set_current_user(user_id)
    
    def set_industry(self, industry: str):
        """
        设置当前行业
        
        Args:
            industry: 行业名称
        """
        self._context.industry = industry
    
    def set_standards(self, standards: List[str]):
        """
        设置关注的标准
        
        Args:
            standards: 标准列表
        """
        self._context.standards = standards
    
    def initialize(self, load_user_kb: bool = True) -> bool:
        """
        初始化所有知识库
        
        Args:
            load_user_kb: 是否加载用户知识库
            
        Returns:
            初始化是否成功
        """
        try:
            # 初始化 L1 标准知识库
            self._standard_kb = StandardKB()
            if not self._standard_kb.initialize():
                print("L1 标准知识库初始化失败")
                return False
            self._kb_map[KnowledgeLevel.L1_STANDARD] = self._standard_kb
            
            # 初始化 L2 经验知识库
            self._experience_kb = ExperienceKB()
            if not self._experience_kb.initialize():
                print("L2 经验知识库初始化失败")
                return False
            self._kb_map[KnowledgeLevel.L2_EXPERIENCE] = self._experience_kb
            
            # 初始化 L3 应用知识库
            self._application_kb = ApplicationKB()
            if not self._application_kb.initialize():
                print("L3 应用知识库初始化失败")
                return False
            self._kb_map[KnowledgeLevel.L3_APPLICATION] = self._application_kb
            
            # 初始化 L4 用户知识库
            if load_user_kb:
                self._user_kb = UserKB(user_id=self._context.user_id)
                if not self._user_kb.initialize():
                    print("L4 用户知识库初始化失败")
                self._kb_map[KnowledgeLevel.L4_USER] = self._user_kb
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"知识库初始化异常: {e}")
            return False
    
    def query(
        self,
        query_text: str,
        levels: Optional[List[KnowledgeLevel]] = None,
        priority: QueryPriority = QueryPriority.STANDARD_FIRST,
        limit: int = 20,
        use_cache: bool = True,
    ) -> UnifiedQueryResult:
        """
        统一知识查询
        
        Args:
            query_text: 查询文本
            levels: 限定的知识层级列表
            priority: 查询优先级策略
            limit: 返回结果数量限制
            use_cache: 是否使用缓存
            
        Returns:
            统一查询结果
        """
        start_time = time.time()
        
        # 检查缓存
        cache_key = f"{query_text}_{levels}_{priority}_{limit}"
        if use_cache:
            with self._cache_lock:
                if cache_key in self._cache:
                    cached_result, cached_time = self._cache[cache_key]
                    if time.time() - cached_time < self._cache_ttl:
                        return cached_result
        
        # 记录查询历史
        self._context.add_query(query_text)
        
        # 构建查询对象
        query = KnowledgeQuery(
            query_text=query_text,
            levels=levels,
            industry=self._context.industry,
            limit=limit * 2,  # 获取更多结果用于合并
        )
        
        # 执行各层级查询
        level_results: Dict[str, KnowledgeResult] = {}
        
        for level, kb in self._kb_map.items():
            if levels and level not in levels:
                continue
            if kb and kb.is_initialized:
                result = kb.query(query)
                level_results[level.value] = result
        
        # 合并结果
        merged_items = self._merge_results(level_results, priority, limit)
        
        # 生成建议
        suggestions = self._generate_suggestions(query_text, level_results)
        related_queries = self._generate_related_queries(query_text, level_results)
        
        execution_time = (time.time() - start_time) * 1000
        
        result = UnifiedQueryResult(
            items=merged_items,
            total_count=sum(r.total_count for r in level_results.values()),
            level_results=level_results,
            context=self._context,
            execution_time=execution_time,
            suggestions=suggestions,
            related_queries=related_queries,
        )
        
        # 缓存结果
        if use_cache:
            with self._cache_lock:
                self._cache[cache_key] = (result, time.time())
        
        return result
    
    def _merge_results(
        self,
        level_results: Dict[str, KnowledgeResult],
        priority: QueryPriority,
        limit: int,
    ) -> List[KnowledgeItem]:
        """
        合并各层级查询结果
        
        Args:
            level_results: 各层级结果
            priority: 优先级策略
            limit: 结果数量限制
            
        Returns:
            合并后的知识项列表
        """
        all_items = []
        
        for level_name, result in level_results.items():
            for item in result.items:
                all_items.append(item)
        
        # 根据优先级策略排序
        if priority == QueryPriority.STANDARD_FIRST:
            # 按层级优先级排序
            all_items.sort(key=lambda x: (x.level.priority, -x.confidence, -x.usage_count))
        
        elif priority == QueryPriority.USER_FIRST:
            # 用户知识优先
            all_items.sort(key=lambda x: (-x.level.priority, -x.confidence, -x.usage_count))
        
        elif priority == QueryPriority.BALANCED:
            # 按相关性和置信度排序
            all_items.sort(key=lambda x: (-x.confidence, -x.usage_count))
        
        elif priority == QueryPriority.COMPREHENSIVE:
            # 综合排序：考虑层级、置信度、使用次数
            all_items.sort(key=lambda x: (
                x.level.priority,
                -x.confidence,
                -x.usage_count
            ))
        
        return all_items[:limit]
    
    def _generate_suggestions(
        self,
        query_text: str,
        level_results: Dict[str, KnowledgeResult],
    ) -> List[str]:
        """
        生成查询建议
        
        Args:
            query_text: 原始查询
            level_results: 各层级结果
            
        Returns:
            建议列表
        """
        suggestions = []
        
        # 检查是否有结果
        total_items = sum(len(r.items) for r in level_results.values())
        
        if total_items == 0:
            suggestions.append("未找到相关结果，请尝试使用不同的关键词")
            suggestions.append("建议检查拼写或使用更通用的术语")
        
        # 根据层级分布给出建议
        level_counts = {
            level: len(result.items)
            for level, result in level_results.items()
        }
        
        if level_counts.get("L1标准", 0) == 0 and level_counts.get("L2经验", 0) > 0:
            suggestions.append("未找到标准条款，但找到了相关经验知识")
        
        if level_counts.get("L4用户", 0) > 0:
            suggestions.append("找到了您的个人知识，可以进一步定制")
        
        return suggestions[:5]
    
    def _generate_related_queries(
        self,
        query_text: str,
        level_results: Dict[str, KnowledgeResult],
    ) -> List[str]:
        """
        生成相关查询建议
        
        Args:
            query_text: 原始查询
            level_results: 各层级结果
            
        Returns:
            相关查询列表
        """
        related = []
        
        # 从结果中提取相关标签
        tags = set()
        for result in level_results.values():
            for item in result.items[:5]:
                tags.update(item.tags)
        
        # 生成相关查询
        for tag in list(tags)[:5]:
            if tag not in query_text and len(tag) > 1:
                related.append(f"{query_text} {tag}")
        
        return related[:5]
    
    def query_by_standard(
        self,
        standard: str,
        clause: Optional[str] = None,
        limit: int = 10,
    ) -> UnifiedQueryResult:
        """
        按标准查询知识
        
        Args:
            standard: 标准名称
            clause: 条款编号（可选）
            limit: 结果数量限制
            
        Returns:
            查询结果
        """
        query_text = f"{standard}"
        if clause:
            query_text += f" {clause}"
        
        return self.query(
            query_text=query_text,
            levels=[KnowledgeLevel.L1_STANDARD, KnowledgeLevel.L2_EXPERIENCE],
            priority=QueryPriority.STANDARD_FIRST,
            limit=limit,
        )
    
    def query_by_industry(
        self,
        industry: str,
        query_text: str = "",
        limit: int = 10,
    ) -> UnifiedQueryResult:
        """
        按行业查询知识
        
        Args:
            industry: 行业名称
            query_text: 额外查询文本
            limit: 结果数量限制
            
        Returns:
            查询结果
        """
        full_query = f"{industry} {query_text}".strip()
        
        return self.query(
            query_text=full_query,
            levels=[KnowledgeLevel.L2_EXPERIENCE, KnowledgeLevel.L3_APPLICATION],
            priority=QueryPriority.BALANCED,
            limit=limit,
        )
    
    def get_standard_clause(self, standard: str, clause: str) -> Optional[KnowledgeItem]:
        """
        获取特定标准条款
        
        Args:
            standard: 标准名称
            clause: 条款编号
            
        Returns:
            知识项或None
        """
        if not self._standard_kb:
            return None
        
        standard_clause = self._standard_kb.get_clause(standard, clause)
        if standard_clause:
            return standard_clause.to_knowledge_item(standard)
        return None
    
    def get_template(self, template_name: str) -> Optional[KnowledgeItem]:
        """
        获取模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            知识项或None
        """
        if not self._application_kb:
            return None
        
        result = self.query(
            query_text=template_name,
            levels=[KnowledgeLevel.L3_APPLICATION],
            limit=1,
        )
        
        if result.items:
            return result.items[0]
        return None
    
    def get_checklist(self, standard_clause: str) -> List[KnowledgeItem]:
        """
        获取检查表
        
        Args:
            standard_clause: 标准条款
            
        Returns:
            检查表列表
        """
        if not self._application_kb:
            return []
        
        checklists = self._application_kb.get_checklists_by_clause(standard_clause)
        return [c.to_knowledge_item() for c in checklists]
    
    def get_best_practices(self, standard: str = "", industry: str = "") -> List[KnowledgeItem]:
        """
        获取最佳实践
        
        Args:
            standard: 标准名称
            industry: 行业名称
            
        Returns:
            最佳实践列表
        """
        if not self._experience_kb:
            return []
        
        practices = []
        if standard:
            practices = self._experience_kb.get_best_practices_by_standard(standard)
        else:
            practices = list(self._experience_kb._best_practices.values())
        
        if industry:
            practices = [p for p in practices if p.industry == industry or p.industry == "通用"]
        
        return [p.to_knowledge_item() for p in practices]
    
    def get_common_issues(self, severity: str = "") -> List[KnowledgeItem]:
        """
        获取常见问题
        
        Args:
            severity: 严重程度过滤
            
        Returns:
            问题列表
        """
        if not self._experience_kb:
            return []
        
        if severity:
            issues = self._experience_kb.get_issues_by_severity(severity)
        else:
            issues = list(self._experience_kb._common_issues.values())
        
        return [i.to_knowledge_item() for i in issues]
    
    def get_user_templates(self, user_id: str = "") -> List[KnowledgeItem]:
        """
        获取用户模板
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户模板列表
        """
        if not self._user_kb:
            return []
        
        templates = self._user_kb.get_user_templates(user_id)
        return [t.to_knowledge_item() for t in templates]
    
    def add_user_knowledge(self, item: KnowledgeItem, user_id: str = "") -> bool:
        """
        添加用户知识
        
        Args:
            item: 知识项
            user_id: 用户ID
            
        Returns:
            添加是否成功
        """
        if not self._user_kb:
            return False
        
        item.level = KnowledgeLevel.L4_USER
        item.tags.append(user_id or self._context.user_id)
        
        return self._user_kb.add_item(item)
    
    def learn_user_preference(self, preference_type: str, value: Dict[str, Any], user_id: str = ""):
        """
        学习用户偏好
        
        Args:
            preference_type: 偏好类型
            value: 偏好值
            user_id: 用户ID
        """
        if not self._user_kb:
            return
        
        from .user_kb import UserPreference
        
        preference = UserPreference(
            user_id=user_id or self._context.user_id,
            preference_type=preference_type,
            preference_value=value,
        )
        self._user_kb.set_user_preference(preference)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "initialized": self._initialized,
            "knowledge_bases": {},
            "total_items": 0,
            "cache_size": len(self._cache),
        }
        
        for level, kb in self._kb_map.items():
            if kb:
                kb_stats = kb.get_statistics()
                stats["knowledge_bases"][level.value] = kb_stats
                stats["total_items"] += kb_stats.get("item_count", 0)
        
        stats["context"] = {
            "user_id": self._context.user_id,
            "industry": self._context.industry,
            "standards": self._context.standards,
        }
        
        return stats
    
    def clear_cache(self):
        """清空缓存"""
        with self._cache_lock:
            self._cache.clear()
    
    def refresh(self):
        """刷新知识库"""
        self.clear_cache()
        self.initialize()
    
    def get_kb(self, level: KnowledgeLevel) -> Optional[KnowledgeBase]:
        """
        获取指定层级的知识库实例
        
        Args:
            level: 知识层级
            
        Returns:
            知识库实例或None
        """
        return self._kb_map.get(level)
    
    def export_all(self) -> Dict[str, Any]:
        """
        导出所有知识库数据
        
        Returns:
            导出数据字典
        """
        export_data = {
            "export_time": datetime.now().isoformat(),
            "knowledge_bases": {},
        }
        
        for level, kb in self._kb_map.items():
            if kb:
                items = []
                for item in kb._items.values():
                    items.append(item.to_dict())
                export_data["knowledge_bases"][level.value] = {
                    "items": items,
                    "statistics": kb.get_statistics(),
                }
        
        return export_data
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"UnifiedKBManager(initialized={self._initialized}, user={self._context.user_id})"
