#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - SQLite数据备份机制

功能：
- 自动备份SQLite数据库（按天轮转）
- 保留最近30个备份
- 支持手动触发备份API
- 备份文件压缩（节省空间）
"""

import shutil
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# 备份目录
BACKUP_DIR = Path("./backups")
BACKUP_DIR.mkdir(exist_ok=True)

# 保留备份数量
MAX_BACKUPS = 30


def get_db_path() -> Path:
    """从DATABASE_URL解析数据库文件路径"""
    # sqlite:///./data/zhizhitong.db -> ./data/zhizhitong.db
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        return Path(db_url.replace("sqlite:///", ""))
    return Path("./data/zhizhitong.db")


def create_backup() -> Optional[Path]:
    """
    创建数据库备份
    
    Returns:
        备份文件路径，失败返回None
    """
    try:
        db_path = get_db_path()
        if not db_path.exists():
            logger.warning(f"数据库文件不存在: {db_path}")
            return None
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"zhizhitong_backup_{timestamp}.db.gz"
        backup_path = BACKUP_DIR / backup_name
        
        # 压缩备份
        with open(db_path, "rb") as f_in:
            with gzip.open(backup_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # 获取原始文件大小和压缩后大小
        original_size = db_path.stat().st_size
        compressed_size = backup_path.stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        logger.info(
            f"数据库备份完成: {backup_name} "
            f"(原始: {original_size/1024/1024:.1f}MB, "
            f"压缩后: {compressed_size/1024/1024:.1f}MB, "
            f"压缩率: {compression_ratio:.1f}%)"
        )
        
        # 清理旧备份
        cleanup_old_backups()
        
        return backup_path
        
    except Exception as e:
        logger.error(f"数据库备份失败: {e}")
        return None


def cleanup_old_backups() -> None:
    """清理超过保留数量的旧备份"""
    try:
        backups = list_backups()
        if len(backups) > MAX_BACKUPS:
            # 按时间排序，删除最旧的
            backups_to_delete = backups[MAX_BACKUPS:]
            for backup in backups_to_delete:
                backup.unlink()
                logger.info(f"删除旧备份: {backup.name}")
    except Exception as e:
        logger.error(f"清理旧备份失败: {e}")


def list_backups() -> List[Path]:
    """
    列出所有备份文件（按时间从最新到最旧排序）
    
    Returns:
        备份文件路径列表
    """
    if not BACKUP_DIR.exists():
        return []
    
    backups = [f for f in BACKUP_DIR.glob("zhizhitong_backup_*.db.gz")]
    # 按修改时间排序（最新的在前）
    backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return backups


def restore_backup(backup_path: Path) -> bool:
    """
    从备份恢复数据库
    
    Args:
        backup_path: 备份文件路径
        
    Returns:
        是否恢复成功
    """
    try:
        db_path = get_db_path()
        
        # 先备份当前数据库（防止恢复失败）
        if db_path.exists():
            safe_backup = db_path.with_suffix(".db.safe")
            shutil.copy2(db_path, safe_backup)
            logger.info(f"已创建安全备份: {safe_backup}")
        
        # 解压恢复
        with gzip.open(backup_path, "rb") as f_in:
            with open(db_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        logger.info(f"数据库已从备份恢复: {backup_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"数据库恢复失败: {e}")
        return False


def get_backup_info(backup_path: Path) -> dict:
    """
    获取备份文件信息
    
    Args:
        backup_path: 备份文件路径
        
    Returns:
        备份信息字典
    """
    stat = backup_path.stat()
    return {
        "name": backup_path.name,
        "size_mb": round(stat.st_size / 1024 / 1024, 2),
        "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "path": str(backup_path),
    }


# 定时备份任务（可以在应用启动时调用）
def setup_auto_backup() -> None:
    """配置自动备份（每天一次）"""
    import threading
    
    def backup_task():
        create_backup()
        # 24小时后再次执行
        threading.Timer(86400, backup_task).start()
    
    # 启动定时任务
    threading.Timer(86400, backup_task).start()
    logger.info("自动备份任务已启动（每24小时执行一次）")
