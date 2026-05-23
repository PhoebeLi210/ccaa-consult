#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 信息来源优先级管理模块

借鉴audit模块的三层优先级机制：
- P1: 用户直接输入（最高优先级）
- P2: 从上传文件提取
- P3: AI生成（需验证）
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable


class InformationSource(str, Enum):
    """信息来源优先级 - 借鉴audit模块"""
    USER_INPUT = "P1"      # 用户直接输入（最高优先级）
    FILE_EXTRACTED = "P2"  # 从上传文件提取
    AI_GENERATED = "P3"    # AI生成（需验证）


@dataclass
class FieldInfo:
    """字段信息"""
    field_name: str
    value: str
    source: InformationSource
    source_file: Optional[str] = None  # 来源文件名（P2时填写）
    verified: bool = False  # 是否已验证
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "field_name": self.field_name,
            "value": self.value,
            "source": self.source.value,
            "source_file": self.source_file,
            "verified": self.verified,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "verified_by": self.verified_by,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FieldInfo":
        """从字典创建"""
        verified_at = data.get("verified_at")
        if verified_at and isinstance(verified_at, str):
            verified_at = datetime.fromisoformat(verified_at)

        return cls(
            field_name=data["field_name"],
            value=data["value"],
            source=InformationSource(data["source"]),
            source_file=data.get("source_file"),
            verified=data.get("verified", False),
            verified_at=verified_at,
            verified_by=data.get("verified_by"),
        )


@dataclass
class FieldValidationResult:
    """字段验证结果"""
    field_name: str
    is_valid: bool
    risk_level: str  # low/medium/high/critical
    message: str
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "field_name": self.field_name,
            "is_valid": self.is_valid,
            "risk_level": self.risk_level,
            "message": self.message,
            "suggestions": self.suggestions,
        }


# 关键字段配置（借鉴audit的必填字段）
CRITICAL_FIELDS = {
    "company_name": {"display_name": "公司名称", "required": True},
    "credit_code": {"display_name": "统一社会信用代码", "required": True},
    "reg_address": {"display_name": "注册地址", "required": True},
    "quality_policy": {"display_name": "质量方针", "required": True},
    "quality_objectives": {"display_name": "质量目标", "required": True},
    "cert_scope": {"display_name": "认证范围", "required": True},
    "professional_code": {"display_name": "专业代码", "required": True},
}


class InformationPriorityManager:
    """信息优先级管理器"""

    def __init__(self, fields: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        初始化字段列表

        Args:
            fields: 字段配置字典，默认为CRITICAL_FIELDS
        """
        self._fields: Dict[str, FieldInfo] = {}
        self._field_config = fields or CRITICAL_FIELDS

    def set_field(
        self,
        field_name: str,
        value: str,
        source: InformationSource,
        source_file: Optional[str] = None
    ) -> None:
        """
        设置字段值

        优先级规则：
        - P1（用户输入）> P2（文件提取）> P3（AI生成）
        - 只有当新值优先级高于或等于现有值时才更新

        Args:
            field_name: 字段名
            value: 字段值
            source: 信息来源
            source_file: 来源文件名（P2时填写）
        """
        # 如果字段不存在，直接设置
        if field_name not in self._fields:
            self._fields[field_name] = FieldInfo(
                field_name=field_name,
                value=value,
                source=source,
                source_file=source_file,
            )
            return

        # 获取现有字段
        existing = self._fields[field_name]

        # 优先级比较：P1 > P2 > P3
        priority_order = {
            InformationSource.USER_INPUT: 3,
            InformationSource.FILE_EXTRACTED: 2,
            InformationSource.AI_GENERATED: 1,
        }

        new_priority = priority_order.get(source, 0)
        existing_priority = priority_order.get(existing.source, 0)

        # 新值优先级更高或相等时更新
        if new_priority >= existing_priority:
            self._fields[field_name] = FieldInfo(
                field_name=field_name,
                value=value,
                source=source,
                source_file=source_file if source == InformationSource.FILE_EXTRACTED else existing.source_file,
                verified=False,  # 更新后重置验证状态
                verified_at=None,
                verified_by=None,
            )

    def get_field(self, field_name: str) -> Optional[FieldInfo]:
        """
        获取字段信息

        Args:
            field_name: 字段名

        Returns:
            字段信息，不存在则返回None
        """
        return self._fields.get(field_name)

    def get_field_value(self, field_name: str) -> Optional[str]:
        """
        获取字段值（快捷方法）

        Args:
            field_name: 字段名

        Returns:
            字段值，不存在则返回None
        """
        field = self._fields.get(field_name)
        return field.value if field else None

    def mark_verified(self, field_name: str, verified_by: str) -> bool:
        """
        标记字段已验证

        Args:
            field_name: 字段名
            verified_by: 验证人

        Returns:
            是否成功标记
        """
        if field_name not in self._fields:
            return False

        self._fields[field_name].verified = True
        self._fields[field_name].verified_at = datetime.utcnow()
        self._fields[field_name].verified_by = verified_by
        return True

    def get_fields_by_source(self, source: InformationSource) -> List[FieldInfo]:
        """
        按来源获取字段列表

        Args:
            source: 信息来源

        Returns:
            字段列表
        """
        return [f for f in self._fields.values() if f.source == source]

    def get_unverified_fields(self) -> List[FieldInfo]:
        """
        获取未验证的字段列表

        Returns:
            未验证的字段列表
        """
        return [f for f in self._fields.values() if not f.verified]

    def get_completion_rate(self) -> Dict[str, Any]:
        """
        获取字段完成率

        Returns:
            完成率统计信息
        """
        total = len(self._field_config)
        filled = sum(
            1 for name in self._field_config.keys()
            if name in self._fields and self._fields[name].value
        )

        # 按来源统计
        by_source = {
            "P1": len(self.get_fields_by_source(InformationSource.USER_INPUT)),
            "P2": len(self.get_fields_by_source(InformationSource.FILE_EXTRACTED)),
            "P3": len(self.get_fields_by_source(InformationSource.AI_GENERATED)),
        }

        # 验证状态统计
        verified_count = sum(1 for f in self._fields.values() if f.verified)

        return {
            "total_fields": total,
            "filled_fields": filled,
            "completion_rate": filled / total if total > 0 else 0,
            "by_source": by_source,
            "verified_count": verified_count,
            "unverified_count": len(self._fields) - verified_count,
        }

    def validate_all_fields(
        self,
        validator: Callable[[str, str], FieldValidationResult]
    ) -> List[FieldValidationResult]:
        """
        验证所有字段

        Args:
            validator: 验证函数，接收(字段名, 字段值)，返回FieldValidationResult

        Returns:
            验证结果列表
        """
        results = []
        for field_name, field_info in self._fields.items():
            result = validator(field_name, field_info.value)
            results.append(result)
        return results

    def to_dict(self) -> Dict[str, Any]:
        """
        导出为字典

        Returns:
            包含所有字段信息的字典
        """
        return {
            "fields": {name: info.to_dict() for name, info in self._fields.items()},
            "field_config": self._field_config,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InformationPriorityManager":
        """
        从字典导入

        Args:
            data: 包含字段信息的字典

        Returns:
            InformationPriorityManager实例
        """
        manager = cls(fields=data.get("field_config", CRITICAL_FIELDS))

        fields_data = data.get("fields", {})
        for field_name, field_data in fields_data.items():
            manager._fields[field_name] = FieldInfo.from_dict(field_data)

        return manager

    def get_missing_required_fields(self) -> List[str]:
        """
        获取缺失的必填字段列表

        Returns:
            缺失的必填字段名列表
        """
        missing = []
        for field_name, config in self._field_config.items():
            if config.get("required", False):
                if field_name not in self._fields or not self._fields[field_name].value:
                    missing.append(field_name)
        return missing

    def get_field_summary(self) -> Dict[str, Any]:
        """
        获取字段摘要信息

        Returns:
            字段摘要
        """
        return {
            "total_managed": len(self._fields),
            "configured_fields": list(self._field_config.keys()),
            "missing_required": self.get_missing_required_fields(),
            "completion": self.get_completion_rate(),
        }


# 便捷函数
def get_source_priority(source: InformationSource) -> int:
    """获取来源优先级数值（越高越优先）"""
    priority_map = {
        InformationSource.USER_INPUT: 3,
        InformationSource.FILE_EXTRACTED: 2,
        InformationSource.AI_GENERATED: 1,
    }
    return priority_map.get(source, 0)


def should_update_field(
    current_source: Optional[InformationSource],
    new_source: InformationSource
) -> bool:
    """
    判断是否应该更新字段

    Args:
        current_source: 当前来源
        new_source: 新来源

    Returns:
        是否应该更新
    """
    if current_source is None:
        return True
    return get_source_priority(new_source) >= get_source_priority(current_source)


def create_default_manager() -> InformationPriorityManager:
    """创建默认的管理器实例"""
    return InformationPriorityManager(fields=CRITICAL_FIELDS)
