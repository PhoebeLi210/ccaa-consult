"""
行业知识库模块

提供行业识别、行业数据管理和行业相关知识获取功能。
适配consult模块的业务场景（生成体系文件而非审核记录）。
"""

from .industry_kb import IndustryKnowledgeBase, get_industry_kb

__all__ = ["IndustryKnowledgeBase", "get_industry_kb"]
