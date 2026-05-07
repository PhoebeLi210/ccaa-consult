#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 配置
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "智质通·咨询版"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "sqlite:///./zhizhitong.db"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # 文件存储
    UPLOAD_DIR: str = "./uploads"
    TEMPLATE_DIR: str = "./templates"
    OUTPUT_DIR: str = "./outputs"

    # LLM配置
    LLM_PROVIDER: str = "deepseek"  # deepseek / openai / local
    LLM_API_KEY: str = ""
    LLM_API_URL: str = "https://api.deepseek.com/v1"
    LLM_MODEL: str = "deepseek-chat"

    # 文档生成配置
    DEFAULT_COVER_STYLE: str = "standard"
    DEFAULT_CONTROLLED_STATUS: str = "草稿"
    DEFAULT_NUMBERING_RULE: str = "Q/{company}-{dept}-{year}-{seq}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
