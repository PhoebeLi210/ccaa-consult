#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 全局常量定义
集中管理所有路径和配置常量
"""

from pathlib import Path
from enum import Enum

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 模板目录
TEMPLATE_DIR = PROJECT_ROOT / "templates_wuxing"
BASE_TEMPLATE_DIR = PROJECT_ROOT / "templates"
DOWNLOAD_TEMPLATE_DIR = PROJECT_ROOT / "download_templates"

# 配置文件路径
INDUSTRY_CONFIG_PATH = PROJECT_ROOT / "config" / "industry_config.yaml"


class DocumentLevel(str, Enum):
    """文档层级"""
    LEVEL1 = "一级文件"
    LEVEL2 = "二级文件"
    LEVEL3 = "三级文件"
    LEVEL4 = "四级文件"


class StandardType(str, Enum):
    """标准类型"""
    ISO9001 = "ISO9001"
    ISO14001 = "ISO14001"
    ISO45001 = "ISO45001"
    INTEGRATED = "INTEGRATED"  # 三标一体


class FileType(str, Enum):
    """文件类型"""
    MANUAL = "管理手册"
    PROCEDURE = "程序文件"
    INSTRUCTION = "作业指导书"
    RECORD = "记录表单"
