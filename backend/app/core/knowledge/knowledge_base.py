"""
知识库核心基类模块

定义了知识库的基础数据结构和抽象接口，
包括知识层级枚举、知识项数据类、知识库基类等核心组件。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Generic, TypeVar
import uuid


class KnowledgeLevel(Enum):
    """
    知识层级枚举
    
    定义四层知识库架构的层级结构:
    - L1_STANDARD: 标准知识层 - ISO标准条款、法规要求等权威知识
    - L2_EXPERIENCE: 经验知识层 - 行业最佳实践、审核经验等
    - L3_APPLICATION: 应用知识层 - 企业案例、模板、检查表等
    - L4_USER: 用户知识层 - 用户自定义模板、个人风格、历史数据
    """
    
    L1_STANDARD = "L1标准"
    L2_EXPERIENCE = "L2经验"
    L3_APPLICATION = "L3应用"
    L4_USER = "L4用户"
    
    @property
    def priority(self) -> int:
        """获取知识层级优先级，数值越小优先级越高"""
        priorities = {
            KnowledgeLevel.L1_STANDARD: 1,
            KnowledgeLevel.L2_EXPERIENCE: 2,
            KnowledgeLevel.L3_APPLICATION: 3,
            KnowledgeLevel.L4_USER: 4,
        }
        return priorities[self]
    
    @property
    def description(self) -> str:
        """获取知识层级描述"""
        descriptions = {
            KnowledgeLevel.L1_STANDARD: "标准知识层 - ISO标准条款、法规要求等权威知识",
            KnowledgeLevel.L2_EXPERIENCE: "经验知识层 - 行业最佳实践、审核经验等",
            KnowledgeLevel.L3_APPLICATION: "应用知识层 - 企业案例、模板、检查表等",
            KnowledgeLevel.L4_USER: "用户知识层 - 用户自定义模板、个人风格、历史数据",
        }
        return descriptions[self]


@dataclass
class KnowledgeItem:
    """
    知识项数据类
    
    表示知识库中的单个知识条目，包含知识的元数据和内容。
    
    Attributes:
        id: 知识项唯一标识符
        level: 知识所属层级
        title: 知识标题
        content: 知识内容
        category: 知识分类
        tags: 知识标签列表
        source: 知识来源
        standard_ref: 关联的标准条款编号（如ISO9001 4.1）
        industry: 适用行业
        created_at: 创建时间
        updated_at: 更新时间
        metadata: 扩展元数据
        confidence: 知识置信度（0-1）
        usage_count: 使用次数统计
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    level: KnowledgeLevel = KnowledgeLevel.L1_STANDARD
    title: str = ""
    content: str = ""
    category: str = ""
    tags: List[str] = field(default_factory=list)
    source: str = ""
    standard_ref: str = ""
    industry: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    usage_count: int = 0
    
    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.level, str):
            self.level = KnowledgeLevel(self.level)
    
    def update_usage(self):
        """更新使用次数"""
        self.usage_count += 1
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "level": self.level.value,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "tags": self.tags,
            "source": self.source,
            "standard_ref": self.standard_ref,
            "industry": self.industry,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "confidence": self.confidence,
            "usage_count": self.usage_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeItem":
        """从字典创建知识项"""
        data["level"] = KnowledgeLevel(data.get("level", "L1标准"))
        data["created_at"] = datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else data.get("created_at", datetime.now())
        data["updated_at"] = datetime.fromisoformat(data["updated_at"]) if isinstance(data.get("updated_at"), str) else data.get("updated_at", datetime.now())
        return cls(**data)


@dataclass
class KnowledgeQuery:
    """
    知识查询数据类
    
    封装知识查询请求的参数。
    
    Attributes:
        query_text: 查询文本
        levels: 限定的知识层级列表（可选）
        categories: 限定的知识分类列表（可选）
        tags: 限定的标签列表（可选）
        industry: 限定的行业（可选）
        standard_ref: 关联的标准条款（可选）
        limit: 返回结果数量限制
        min_confidence: 最小置信度阈值
        include_metadata: 是否包含元数据
    """
    
    query_text: str = ""
    levels: Optional[List[KnowledgeLevel]] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    industry: Optional[str] = None
    standard_ref: Optional[str] = None
    limit: int = 10
    min_confidence: float = 0.0
    include_metadata: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "query_text": self.query_text,
            "levels": [l.value for l in self.levels] if self.levels else None,
            "categories": self.categories,
            "tags": self.tags,
            "industry": self.industry,
            "standard_ref": self.standard_ref,
            "limit": self.limit,
            "min_confidence": self.min_confidence,
            "include_metadata": self.include_metadata,
        }


@dataclass
class KnowledgeResult:
    """
    知识查询结果数据类
    
    封装知识查询的返回结果。
    
    Attributes:
        items: 匹配的知识项列表
        total_count: 总匹配数量
        query: 原始查询对象
        execution_time: 查询执行时间（毫秒）
        suggestions: 相关建议列表
        level_distribution: 各层级结果分布
    """
    
    items: List[KnowledgeItem] = field(default_factory=list)
    total_count: int = 0
    query: Optional[KnowledgeQuery] = None
    execution_time: float = 0.0
    suggestions: List[str] = field(default_factory=list)
    level_distribution: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "items": [item.to_dict() for item in self.items],
            "total_count": self.total_count,
            "query": self.query.to_dict() if self.query else None,
            "execution_time": self.execution_time,
            "suggestions": self.suggestions,
            "level_distribution": self.level_distribution,
        }
    
    def get_items_by_level(self, level: KnowledgeLevel) -> List[KnowledgeItem]:
        """获取指定层级的知识项"""
        return [item for item in self.items if item.level == level]


T = TypeVar('T')


class KnowledgeBase(ABC, Generic[T]):
    """
    知识库抽象基类
    
    定义知识库的基本接口和通用功能，
    所有具体知识库实现都应继承此类。
    
    Type Parameters:
        T: 知识项的具体类型
    """
    
    def __init__(self, level: KnowledgeLevel):
        """
        初始化知识库
        
        Args:
            level: 知识库所属层级
        """
        self._level = level
        self._items: Dict[str, KnowledgeItem] = {}
        self._indices: Dict[str, Dict[str, List[str]]] = {
            "category": {},
            "tag": {},
            "standard_ref": {},
            "industry": {},
        }
        self._initialized = False
    
    @property
    def level(self) -> KnowledgeLevel:
        """获取知识库层级"""
        return self._level
    
    @property
    def item_count(self) -> int:
        """获取知识项数量"""
        return len(self._items)
    
    @property
    def is_initialized(self) -> bool:
        """检查知识库是否已初始化"""
        return self._initialized
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化知识库
        
        加载知识数据、构建索引等初始化操作。
        
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def load_knowledge(self) -> List[KnowledgeItem]:
        """
        加载知识数据
        
        从数据源加载知识项列表。
        
        Returns:
            加载的知识项列表
        """
        pass
    
    def add_item(self, item: KnowledgeItem) -> bool:
        """
        添加知识项
        
        Args:
            item: 要添加的知识项
            
        Returns:
            添加是否成功
        """
        if not item.id:
            item.id = str(uuid.uuid4())
        
        item.level = self._level
        self._items[item.id] = item
        self._update_indices(item)
        return True
    
    def remove_item(self, item_id: str) -> bool:
        """
        移除知识项
        
        Args:
            item_id: 要移除的知识项ID
            
        Returns:
            移除是否成功
        """
        if item_id not in self._items:
            return False
        
        item = self._items[item_id]
        self._remove_from_indices(item)
        del self._items[item_id]
        return True
    
    def get_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """
        获取知识项
        
        Args:
            item_id: 知识项ID
            
        Returns:
            知识项或None
        """
        item = self._items.get(item_id)
        if item:
            item.update_usage()
        return item
    
    def query(self, query: KnowledgeQuery) -> KnowledgeResult:
        """
        查询知识
        
        Args:
            query: 查询对象
            
        Returns:
            查询结果
        """
        import time
        start_time = time.time()
        
        # 收集匹配的知识项
        matched_items = []
        
        for item in self._items.values():
            if self._match_item(item, query):
                matched_items.append(item)
        
        # 排序：按置信度和使用次数排序
        matched_items.sort(key=lambda x: (x.confidence, x.usage_count), reverse=True)
        
        # 限制结果数量
        limited_items = matched_items[:query.limit]
        
        # 计算层级分布
        level_distribution = {}
        for item in matched_items:
            level_name = item.level.value
            level_distribution[level_name] = level_distribution.get(level_name, 0) + 1
        
        execution_time = (time.time() - start_time) * 1000
        
        return KnowledgeResult(
            items=limited_items,
            total_count=len(matched_items),
            query=query,
            execution_time=execution_time,
            level_distribution=level_distribution,
        )
    
    def _match_item(self, item: KnowledgeItem, query: KnowledgeQuery) -> bool:
        """
        检查知识项是否匹配查询条件
        
        Args:
            item: 知识项
            query: 查询对象
            
        Returns:
            是否匹配
        """
        # 检查置信度
        if item.confidence < query.min_confidence:
            return False
        
        # 检查层级
        if query.levels and item.level not in query.levels:
            return False
        
        # 检查分类
        if query.categories and item.category not in query.categories:
            return False
        
        # 检查标签
        if query.tags and not any(tag in item.tags for tag in query.tags):
            return False
        
        # 检查行业
        if query.industry and item.industry != query.industry:
            return False
        
        # 检查标准条款
        if query.standard_ref and item.standard_ref != query.standard_ref:
            return False
        
        # 检查查询文本
        if query.query_text:
            query_lower = query.query_text.lower()
            if (query_lower not in item.title.lower() and
                query_lower not in item.content.lower() and
                query_lower not in item.category.lower() and
                not any(query_lower in tag.lower() for tag in item.tags)):
                return False
        
        return True
    
    def _update_indices(self, item: KnowledgeItem):
        """
        更新索引
        
        Args:
            item: 新增或更新的知识项
        """
        # 更新分类索引
        if item.category:
            if item.category not in self._indices["category"]:
                self._indices["category"][item.category] = []
            self._indices["category"][item.category].append(item.id)
        
        # 更新标签索引
        for tag in item.tags:
            if tag not in self._indices["tag"]:
                self._indices["tag"][tag] = []
            self._indices["tag"][tag].append(item.id)
        
        # 更新标准条款索引
        if item.standard_ref:
            if item.standard_ref not in self._indices["standard_ref"]:
                self._indices["standard_ref"][item.standard_ref] = []
            self._indices["standard_ref"][item.standard_ref].append(item.id)
        
        # 更新行业索引
        if item.industry:
            if item.industry not in self._indices["industry"]:
                self._indices["industry"][item.industry] = []
            self._indices["industry"][item.industry].append(item.id)
    
    def _remove_from_indices(self, item: KnowledgeItem):
        """
        从索引中移除
        
        Args:
            item: 要移除的知识项
        """
        # 从分类索引移除
        if item.category and item.category in self._indices["category"]:
            if item.id in self._indices["category"][item.category]:
                self._indices["category"][item.category].remove(item.id)
        
        # 从标签索引移除
        for tag in item.tags:
            if tag in self._indices["tag"] and item.id in self._indices["tag"][tag]:
                self._indices["tag"][tag].remove(item.id)
        
        # 从标准条款索引移除
        if item.standard_ref and item.standard_ref in self._indices["standard_ref"]:
            if item.id in self._indices["standard_ref"][item.standard_ref]:
                self._indices["standard_ref"][item.standard_ref].remove(item.id)
        
        # 从行业索引移除
        if item.industry and item.industry in self._indices["industry"]:
            if item.id in self._indices["industry"][item.industry]:
                self._indices["industry"][item.industry].remove(item.id)
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        return list(self._indices["category"].keys())
    
    def get_tags(self) -> List[str]:
        """获取所有标签"""
        return list(self._indices["tag"].keys())
    
    def get_industries(self) -> List[str]:
        """获取所有行业"""
        return list(self._indices["industry"].keys())
    
    def get_standard_refs(self) -> List[str]:
        """获取所有标准条款引用"""
        return list(self._indices["standard_ref"].keys())
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "level": self._level.value,
            "item_count": self.item_count,
            "categories": len(self._indices["category"]),
            "tags": len(self._indices["tag"]),
            "industries": len(self._indices["industry"]),
            "standard_refs": len(self._indices["standard_ref"]),
            "initialized": self._initialized,
        }
    
    def clear(self):
        """清空知识库"""
        self._items.clear()
        for index in self._indices.values():
            index.clear()
        self._initialized = False
