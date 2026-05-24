"""
四层知识库架构模块

本模块实现了CCAA咨询系统的四层知识库架构:
- L1 标准知识库 (StandardKB): ISO标准条款知识
- L2 经验知识库 (ExperienceKB): 行业最佳实践和审核经验
- L3 应用知识库 (ApplicationKB): 企业案例和模板库
- L4 用户知识库 (UserKB): 用户自定义知识和历史数据

使用示例:
    from app.core.knowledge import UnifiedKBManager, KnowledgeLevel
    
    manager = UnifiedKBManager()
    results = manager.query("ISO9001 质量管理体系")
"""

from .knowledge_base import (
    KnowledgeLevel,
    KnowledgeItem,
    KnowledgeBase,
    KnowledgeQuery,
    KnowledgeResult,
)

from .standard_kb import StandardKB
from .experience_kb import ExperienceKB
from .application_kb import ApplicationKB
from .user_kb import UserKB
from .unified_kb_manager import UnifiedKBManager

__all__ = [
    # 核心类和枚举
    "KnowledgeLevel",
    "KnowledgeItem", 
    "KnowledgeBase",
    "KnowledgeQuery",
    "KnowledgeResult",
    # 四层知识库实现
    "StandardKB",
    "ExperienceKB", 
    "ApplicationKB",
    "UserKB",
    # 统一管理器
    "UnifiedKBManager",
]

__version__ = "1.0.0"
__author__ = "CCAA Consult Team"
