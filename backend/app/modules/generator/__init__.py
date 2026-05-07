#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档生成器架构 - 解耦设计

架构说明：
├── base.py              # 基类和通用工具
├── level1/              # 一级文件（管理手册）
│   └── manual_generator.py
├── level2/              # 二级文件（程序文件）
│   └── procedure_generator.py
├── level3/              # 三级文件（作业指导书/制度）
│   └── level3_generator.py
├── level4/              # 四级文件（记录表格）
│   └── level4_generator.py
├── required_docs/       # 企业必需文件清单
│   └── required_doc_generator.py
└── orchestrator.py      # 协调器

每个层级独立生成，互不耦合，便于维护和扩展。
"""

from .base import (
    BaseGenerator,
    VariableManager,
    TemplateEngine,
    CompanyInfo,
    StandardType,
    FileLevel,
    DocumentType,
    GeneratedDocument,
)
from .level1 import manual_generator
from .level2 import procedure_generator
from .level3 import level3_generator
from .level4 import level4_generator
from .required_docs import (
    required_doc_generator,
    RequiredDocChecker,
    RequiredDocTemplateGenerator,
    RequiredDocument,
    RequiredDocCheckResult,
    RequiredDocCategory,
    RequiredDocStatus,
)
from .orchestrator import (
    DocumentOrchestrator,
    generate_full_package,
    generate_document_tree,
)

__all__ = [
    # 基类
    "BaseGenerator",
    "VariableManager",
    "TemplateEngine",
    "CompanyInfo",
    "StandardType",
    "FileLevel",
    "DocumentType",
    "GeneratedDocument",
    
    # 一级文件
    "manual_generator",
    
    # 二级文件
    "procedure_generator",
    
    # 三级文件
    "level3_generator",
    
    # 四级文件
    "level4_generator",
    
    # 必需文件
    "required_doc_generator",
    "RequiredDocChecker",
    "RequiredDocTemplateGenerator",
    "RequiredDocument",
    "RequiredDocCheckResult",
    "RequiredDocCategory",
    "RequiredDocStatus",
    
    # 协调器
    "DocumentOrchestrator",
    "generate_full_package",
    "generate_document_tree",
]
