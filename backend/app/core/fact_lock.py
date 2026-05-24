#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 事实锁定机制
确保事实数据的一致性和完整性
"""

import json
import hashlib
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from datetime import datetime
from enum import Enum
from pathlib import Path
import threading

from .fact_extractor import Fact, FactType, FactSource

logger = logging.getLogger(__name__)


class LockStatus(str, Enum):
    """锁定状态枚举"""
    UNLOCKED = "未锁定"
    LOCKED = "已锁定"
    FROZEN = "已冻结"  # 不可修改，不可删除
    ARCHIVED = "已归档"


class UpdatePermission(str, Enum):
    """更新权限枚举"""
    ALLOWED = "允许"
    NEEDS_UNLOCK = "需要解锁"
    NEEDS_APPROVAL = "需要审批"
    DENIED = "拒绝"


@dataclass
class FactLock:
    """事实锁定数据类"""
    lock_id: str
    fact_id: str
    status: LockStatus = LockStatus.LOCKED
    locked_at: datetime = field(default_factory=datetime.now)
    locked_by: str = ""  # 锁定者标识
    lock_reason: str = ""
    version: int = 1
    checksum: str = ""  # 内容校验和
    update_history: List[Dict[str, Any]] = field(default_factory=list)
    approval_required: bool = False
    approved_by: str = ""
    approved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None  # 锁定过期时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "lock_id": self.lock_id,
            "fact_id": self.fact_id,
            "status": self.status.value,
            "locked_at": self.locked_at.isoformat(),
            "locked_by": self.locked_by,
            "lock_reason": self.lock_reason,
            "version": self.version,
            "checksum": self.checksum,
            "update_history": self.update_history,
            "approval_required": self.approval_required,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FactLock":
        """从字典创建"""
        return cls(
            lock_id=data["lock_id"],
            fact_id=data["fact_id"],
            status=LockStatus(data["status"]),
            locked_at=datetime.fromisoformat(data["locked_at"]) if isinstance(data.get("locked_at"), str) else datetime.now(),
            locked_by=data.get("locked_by", ""),
            lock_reason=data.get("lock_reason", ""),
            version=data.get("version", 1),
            checksum=data.get("checksum", ""),
            update_history=data.get("update_history", []),
            approval_required=data.get("approval_required", False),
            approved_by=data.get("approved_by", ""),
            approved_at=datetime.fromisoformat(data["approved_at"]) if data.get("approved_at") else None,
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
        )


@dataclass
class FactUpdateRequest:
    """事实更新请求"""
    request_id: str
    fact_id: str
    old_content: str
    new_content: str
    requested_by: str
    requested_at: datetime = field(default_factory=datetime.now)
    reason: str = ""
    status: str = "pending"  # pending, approved, rejected
    reviewed_by: str = ""
    reviewed_at: Optional[datetime] = None
    review_comment: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "request_id": self.request_id,
            "fact_id": self.fact_id,
            "old_content": self.old_content,
            "new_content": self.new_content,
            "requested_by": self.requested_by,
            "requested_at": self.requested_at.isoformat(),
            "reason": self.reason,
            "status": self.status,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "review_comment": self.review_comment
        }


class FactLockManager:
    """事实锁定管理器"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化事实锁定管理器
        
        Args:
            storage_path: 存储路径（可选）
        """
        self._locks: Dict[str, FactLock] = {}  # fact_id -> FactLock
        self._facts: Dict[str, Fact] = {}  # fact_id -> Fact
        self._update_requests: Dict[str, FactUpdateRequest] = {}
        self._lock = threading.RLock()  # 线程锁
        self._storage_path = Path(storage_path) if storage_path else None
        
        # 加载已有数据
        if self._storage_path:
            self._load_from_storage()
    
    def _generate_checksum(self, content: str) -> str:
        """
        生成内容校验和
        
        Args:
            content: 内容字符串
            
        Returns:
            校验和
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def _generate_lock_id(self, fact_id: str) -> str:
        """
        生成锁定ID
        
        Args:
            fact_id: 事实ID
            
        Returns:
            锁定ID
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"lock_{fact_id}_{timestamp}"
    
    def lock_facts(
        self, 
        facts: List[Fact], 
        locked_by: str = "",
        reason: str = "",
        freeze: bool = False
    ) -> List[FactLock]:
        """
        锁定事实
        
        Args:
            facts: 要锁定的事实列表
            locked_by: 锁定者标识
            reason: 锁定原因
            freeze: 是否冻结（不可修改）
            
        Returns:
            锁定信息列表
        """
        locks = []
        
        with self._lock:
            for fact in facts:
                # 检查是否已锁定
                if fact.fact_id in self._locks:
                    existing_lock = self._locks[fact.fact_id]
                    if existing_lock.status == LockStatus.FROZEN:
                        logger.warning(f"事实 {fact.fact_id} 已冻结，无法重新锁定")
                        continue
                    if existing_lock.status == LockStatus.LOCKED:
                        logger.info(f"事实 {fact.fact_id} 已锁定，跳过")
                        locks.append(existing_lock)
                        continue
                
                # 创建锁定
                lock = FactLock(
                    lock_id=self._generate_lock_id(fact.fact_id),
                    fact_id=fact.fact_id,
                    status=LockStatus.FROZEN if freeze else LockStatus.LOCKED,
                    locked_by=locked_by,
                    lock_reason=reason,
                    checksum=self._generate_checksum(fact.content)
                )
                
                self._locks[fact.fact_id] = lock
                self._facts[fact.fact_id] = fact
                locks.append(lock)
                
                logger.info(f"已锁定事实: {fact.fact_id}, 状态: {lock.status.value}")
            
            # 保存到存储
            if self._storage_path:
                self._save_to_storage()
        
        return locks
    
    def unlock_fact(self, fact_id: str, unlocked_by: str = "", reason: str = "") -> bool:
        """
        解锁事实
        
        Args:
            fact_id: 事实ID
            unlocked_by: 解锁者标识
            reason: 解锁原因
            
        Returns:
            是否成功解锁
        """
        with self._lock:
            if fact_id not in self._locks:
                logger.warning(f"事实 {fact_id} 未被锁定")
                return False
            
            lock = self._locks[fact_id]
            
            # 检查是否冻结
            if lock.status == LockStatus.FROZEN:
                logger.error(f"事实 {fact_id} 已冻结，无法解锁")
                return False
            
            # 记录解锁历史
            lock.update_history.append({
                "action": "unlock",
                "by": unlocked_by,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
            
            # 更新状态
            lock.status = LockStatus.UNLOCKED
            
            # 从锁定列表移除
            del self._locks[fact_id]
            
            if self._storage_path:
                self._save_to_storage()
            
            logger.info(f"已解锁事实: {fact_id}")
            return True
    
    def verify_fact(self, fact: Fact, strict: bool = False) -> Dict[str, Any]:
        """
        验证事实
        
        Args:
            fact: 要验证的事实
            strict: 是否严格模式（检查校验和）
            
        Returns:
            验证结果字典
        """
        result = {
            "fact_id": fact.fact_id,
            "is_valid": True,
            "is_locked": False,
            "checksum_match": True,
            "issues": [],
            "warnings": []
        }
        
        with self._lock:
            # 检查是否锁定
            if fact.fact_id in self._locks:
                lock = self._locks[fact.fact_id]
                result["is_locked"] = True
                result["lock_status"] = lock.status.value
                result["locked_at"] = lock.locked_at.isoformat()
                
                # 检查校验和
                if strict:
                    current_checksum = self._generate_checksum(fact.content)
                    if current_checksum != lock.checksum:
                        result["is_valid"] = False
                        result["checksum_match"] = False
                        result["issues"].append("内容校验和不匹配，可能已被篡改")
            
            # 检查事实内容有效性
            if not fact.content or not fact.content.strip():
                result["is_valid"] = False
                result["issues"].append("事实内容为空")
            
            # 检查置信度
            if fact.confidence < 0.5:
                result["warnings"].append(f"置信度较低: {fact.confidence}")
            
            # 检查来源
            if fact.source == FactSource.SYSTEM_INFERENCE and not fact.is_verified:
                result["warnings"].append("系统推断的事实尚未验证")
        
        return result
    
    def get_locked_facts(
        self, 
        fact_type: Optional[FactType] = None,
        status: Optional[LockStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        获取已锁定事实
        
        Args:
            fact_type: 筛选事实类型（可选）
            status: 筛选锁定状态（可选）
            
        Returns:
            锁定事实列表
        """
        result = []
        
        with self._lock:
            for fact_id, lock in self._locks.items():
                # 筛选状态
                if status and lock.status != status:
                    continue
                
                # 获取事实
                if fact_id in self._facts:
                    fact = self._facts[fact_id]
                    
                    # 筛选类型
                    if fact_type and fact.fact_type != fact_type:
                        continue
                    
                    result.append({
                        "fact": fact.to_dict(),
                        "lock": lock.to_dict()
                    })
        
        return result
    
    def update_fact(
        self, 
        fact_id: str, 
        new_content: str,
        updated_by: str = "",
        reason: str = "",
        force: bool = False
    ) -> Dict[str, Any]:
        """
        更新事实（需要解锁）
        
        Args:
            fact_id: 事实ID
            new_content: 新内容
            updated_by: 更新者标识
            reason: 更新原因
            force: 是否强制更新（跳过锁定检查）
            
        Returns:
            更新结果
        """
        result = {
            "success": False,
            "message": "",
            "old_content": "",
            "new_content": new_content,
            "permission": UpdatePermission.ALLOWED.value
        }
        
        with self._lock:
            # 检查事实是否存在
            if fact_id not in self._facts:
                result["message"] = f"事实 {fact_id} 不存在"
                return result
            
            fact = self._facts[fact_id]
            result["old_content"] = fact.content
            
            # 检查是否锁定
            if fact_id in self._locks:
                lock = self._locks[fact_id]
                
                if lock.status == LockStatus.FROZEN:
                    result["permission"] = UpdatePermission.DENIED.value
                    result["message"] = "事实已冻结，无法更新"
                    return result
                
                if lock.status == LockStatus.LOCKED:
                    if force:
                        result["permission"] = UpdatePermission.ALLOWED.value
                        result["message"] = "强制更新已锁定事实"
                    else:
                        result["permission"] = UpdatePermission.NEEDS_UNLOCK.value
                        result["message"] = "事实已锁定，需要先解锁或使用强制模式"
                        return result
            
            # 执行更新
            old_content = fact.content
            fact.content = new_content
            fact.updated_at = datetime.now()
            
            # 更新锁定信息
            if fact_id in self._locks:
                lock = self._locks[fact_id]
                lock.version += 1
                lock.checksum = self._generate_checksum(new_content)
                lock.update_history.append({
                    "action": "update",
                    "by": updated_by,
                    "reason": reason,
                    "old_content": old_content,
                    "new_content": new_content,
                    "timestamp": datetime.now().isoformat()
                })
            
            result["success"] = True
            result["message"] = "事实更新成功"
            
            if self._storage_path:
                self._save_to_storage()
            
            logger.info(f"已更新事实: {fact_id}")
        
        return result
    
    def request_update(
        self, 
        fact_id: str, 
        new_content: str,
        requested_by: str,
        reason: str
    ) -> FactUpdateRequest:
        """
        请求更新事实（用于需要审批的情况）
        
        Args:
            fact_id: 事实ID
            new_content: 新内容
            requested_by: 请求者标识
            reason: 更新原因
            
        Returns:
            更新请求
        """
        with self._lock:
            # 检查事实是否存在
            if fact_id not in self._facts:
                raise ValueError(f"事实 {fact_id} 不存在")
            
            fact = self._facts[fact_id]
            
            # 创建更新请求
            request = FactUpdateRequest(
                request_id=f"req_{fact_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                fact_id=fact_id,
                old_content=fact.content,
                new_content=new_content,
                requested_by=requested_by,
                reason=reason
            )
            
            self._update_requests[request.request_id] = request
            
            if self._storage_path:
                self._save_to_storage()
            
            logger.info(f"已创建更新请求: {request.request_id}")
            return request
    
    def approve_update(
        self, 
        request_id: str, 
        approved_by: str,
        comment: str = ""
    ) -> bool:
        """
        批准更新请求
        
        Args:
            request_id: 请求ID
            approved_by: 审批者标识
            comment: 审批意见
            
        Returns:
            是否成功
        """
        with self._lock:
            if request_id not in self._update_requests:
                logger.error(f"更新请求 {request_id} 不存在")
                return False
            
            request = self._update_requests[request_id]
            
            if request.status != "pending":
                logger.error(f"更新请求 {request_id} 已处理")
                return False
            
            # 更新请求状态
            request.status = "approved"
            request.reviewed_by = approved_by
            request.reviewed_at = datetime.now()
            request.review_comment = comment
            
            # 执行更新
            result = self.update_fact(
                fact_id=request.fact_id,
                new_content=request.new_content,
                updated_by=approved_by,
                reason=f"审批通过: {comment}",
                force=True
            )
            
            if self._storage_path:
                self._save_to_storage()
            
            logger.info(f"已批准更新请求: {request_id}")
            return result["success"]
    
    def reject_update(
        self, 
        request_id: str, 
        rejected_by: str,
        comment: str = ""
    ) -> bool:
        """
        拒绝更新请求
        
        Args:
            request_id: 请求ID
            rejected_by: 拒绝者标识
            comment: 拒绝原因
            
        Returns:
            是否成功
        """
        with self._lock:
            if request_id not in self._update_requests:
                logger.error(f"更新请求 {request_id} 不存在")
                return False
            
            request = self._update_requests[request_id]
            
            if request.status != "pending":
                logger.error(f"更新请求 {request_id} 已处理")
                return False
            
            # 更新请求状态
            request.status = "rejected"
            request.reviewed_by = rejected_by
            request.reviewed_at = datetime.now()
            request.review_comment = comment
            
            if self._storage_path:
                self._save_to_storage()
            
            logger.info(f"已拒绝更新请求: {request_id}")
            return True
    
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """
        获取待处理的更新请求
        
        Returns:
            待处理请求列表
        """
        result = []
        with self._lock:
            for request in self._update_requests.values():
                if request.status == "pending":
                    result.append(request.to_dict())
        return result
    
    def archive_fact(self, fact_id: str, archived_by: str = "", reason: str = "") -> bool:
        """
        归档事实
        
        Args:
            fact_id: 事实ID
            archived_by: 归档者标识
            reason: 归档原因
            
        Returns:
            是否成功
        """
        with self._lock:
            if fact_id not in self._locks:
                logger.warning(f"事实 {fact_id} 未被锁定")
                return False
            
            lock = self._locks[fact_id]
            
            if lock.status == LockStatus.FROZEN:
                logger.error(f"事实 {fact_id} 已冻结，无法归档")
                return False
            
            lock.status = LockStatus.ARCHIVED
            lock.update_history.append({
                "action": "archive",
                "by": archived_by,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
            
            if self._storage_path:
                self._save_to_storage()
            
            logger.info(f"已归档事实: {fact_id}")
            return True
    
    def get_fact_history(self, fact_id: str) -> List[Dict[str, Any]]:
        """
        获取事实变更历史
        
        Args:
            fact_id: 事实ID
            
        Returns:
            变更历史列表
        """
        with self._lock:
            if fact_id not in self._locks:
                return []
            
            return self._locks[fact_id].update_history
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取锁定统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "total_locked": len(self._locks),
            "by_status": {},
            "by_type": {},
            "pending_requests": 0,
            "total_updates": 0
        }
        
        with self._lock:
            # 按状态统计
            for lock in self._locks.values():
                status = lock.status.value
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                stats["total_updates"] += len(lock.update_history)
            
            # 按类型统计
            for fact_id, lock in self._locks.items():
                if fact_id in self._facts:
                    fact = self._facts[fact_id]
                    type_name = fact.fact_type.value
                    stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1
            
            # 待处理请求
            for request in self._update_requests.values():
                if request.status == "pending":
                    stats["pending_requests"] += 1
        
        return stats
    
    def _save_to_storage(self):
        """保存到存储"""
        if not self._storage_path:
            return
        
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "locks": {fid: lock.to_dict() for fid, lock in self._locks.items()},
                "facts": {fid: fact.to_dict() for fid, fact in self._facts.items()},
                "update_requests": {rid: req.to_dict() for rid, req in self._update_requests.items()},
                "saved_at": datetime.now().isoformat()
            }
            
            with open(self._storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
    
    def _load_from_storage(self):
        """从存储加载"""
        if not self._storage_path or not self._storage_path.exists():
            return
        
        try:
            with open(self._storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._locks = {
                fid: FactLock.from_dict(lock_data) 
                for fid, lock_data in data.get("locks", {}).items()
            }
            
            self._facts = {
                fid: Fact.from_dict(fact_data) 
                for fid, fact_data in data.get("facts", {}).items()
            }
            
            self._update_requests = {
                rid: FactUpdateRequest(**req_data) 
                for rid, req_data in data.get("update_requests", {}).items()
            }
            
            logger.info(f"已加载 {len(self._locks)} 个锁定记录")
            
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
    
    def export_locked_facts(self, output_path: str) -> bool:
        """
        导出锁定事实到文件
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            是否成功
        """
        try:
            data = self.get_locked_facts()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已导出锁定事实到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出失败: {e}")
            return False
    
    def import_locked_facts(self, input_path: str, merge: bool = True) -> int:
        """
        从文件导入锁定事实
        
        Args:
            input_path: 输入文件路径
            merge: 是否合并（True）或覆盖（False）
            
        Returns:
            导入数量
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            count = 0
            for item in data:
                fact = Fact.from_dict(item["fact"])
                lock = FactLock.from_dict(item["lock"])
                
                if not merge or fact.fact_id not in self._facts:
                    self._facts[fact.fact_id] = fact
                    self._locks[fact.fact_id] = lock
                    count += 1
            
            if self._storage_path:
                self._save_to_storage()
            
            logger.info(f"已导入 {count} 个锁定事实")
            return count
            
        except Exception as e:
            logger.error(f"导入失败: {e}")
            return 0
