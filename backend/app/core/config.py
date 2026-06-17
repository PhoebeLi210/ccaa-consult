"""
应用配置
"""
import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
TEMPLATE_DIR = ROOT_DIR / "templates"


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR / 'data' / 'zhizhitong.db'}")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "zhizhitong-dev-secret-key")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "zhizhitong-dev-secret-key"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_HOURS", "24"))
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", os.getenv("DEEPSEEK_API_KEY", ""))
    LLM_API_URL: str = os.getenv("LLM_API_URL", "https://api.deepseek.com/v1/chat/completions")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-chat")
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "deepseek")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(50 * 1024 * 1024)))
    UPLOAD_DIR: str = str(UPLOAD_DIR)


settings = Settings()
