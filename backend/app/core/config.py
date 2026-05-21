#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 配置
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "智质通·咨询版"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库
    DATABASE_URL: str = "sqlite:///./data/zhizhitong.db"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # 文件存储
    UPLOAD_DIR: str = "./uploads"
    TEMPLATE_DIR: str = "./templates_industry"
    OUTPUT_DIR: str = "./output"

    # LLM配置 - 请在.env文件中配置API Key，不要硬编码
    LLM_PROVIDER: str = "deepseek"  # deepseek / openai / local
    LLM_API_KEY: str = ""  # 从.env文件读取，不要在此硬编码
    LLM_API_URL: str = "https://api.deepseek.com/v1"
    LLM_MODEL: str = "deepseek-chat"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4000

    # JWT认证
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # 文件上传
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB

    # 文档生成配置
    DEFAULT_COVER_STYLE: str = "standard"
    DEFAULT_CONTROLLED_STATUS: str = "草稿"
    DEFAULT_NUMBERING_RULE: str = "Q/{company}-{dept}-{year}-{seq}"

    # 日志
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
