#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 结构化日志配置

支持：
- 控制台彩色输出（开发环境）
- 文件日志轮转（生产环境）
- JSON格式日志（便于日志收集系统解析）
- 请求链路追踪（trace_id）
"""

import logging
import logging.handlers
import sys
import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

from app.core.config import settings


# 日志目录
LOG_DIR = Path("./logs")
LOG_DIR.mkdir(exist_ok=True)


class JSONFormatter(logging.Formatter):
    """JSON格式日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加额外字段
        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        # 异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """带颜色的控制台日志格式化器"""
    
    # ANSI颜色码
    COLORS = {
        "DEBUG": "\033[36m",      # 青色
        "INFO": "\033[32m",       # 绿色
        "WARNING": "\033[33m",    # 黄色
        "ERROR": "\033[31m",      # 红色
        "CRITICAL": "\033[35m",   # 紫色
        "RESET": "\033[0m",       # 重置
    }
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        
        # 简化格式用于控制台
        formatted = f"{color}[{record.levelname}]{reset} {record.name} - {record.getMessage()}"
        
        # 添加trace_id（如果有）
        if hasattr(record, "trace_id"):
            formatted = f"[{record.trace_id}] {formatted}"
        
        return formatted


def setup_logging() -> None:
    """配置日志系统"""
    
    # 获取日志级别
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)  # 控制台只显示 WARNING 及以上
    
    # 清除现有处理器
    root_logger.handlers = []
    
    # ===== 控制台处理器（仅 WARNING 及以上） =====
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    
    if settings.DEBUG:
        console_formatter = logging.Formatter('[%(levelname)s] %(name)s - %(message)s')
    else:
        console_formatter = JSONFormatter()
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # ===== 文件处理器（按天轮转） =====
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_DIR / "app.log",
        when="midnight",           # 每天午夜轮转
        interval=1,
        backupCount=30,            # 保留30天
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # ===== 错误日志处理器（单独记录ERROR及以上） =====
    error_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_DIR / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(error_handler)
    
    # ===== 访问日志处理器 =====
    access_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_DIR / "access.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(JSONFormatter())
    
    # 创建访问日志专用logger
    access_logger = logging.getLogger("access")
    access_logger.handlers = []
    access_logger.addHandler(access_handler)
    access_logger.propagate = False  # 不向根logger传播
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logging.getLogger(__name__).info("日志系统初始化完成")


# 便捷函数
def get_logger(name: str) -> logging.Logger:
    """获取logger实例"""
    return logging.getLogger(name)
