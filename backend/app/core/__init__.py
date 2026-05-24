"""智质通·咨询版模块"""

from .fact_extractor import (
    FactType,
    FactSource,
    Fact,
    FactExtractor
)

from .fact_lock import (
    LockStatus,
    UpdatePermission,
    FactLock,
    FactUpdateRequest,
    FactLockManager
)

from .anti_fabrication import (
    FabricationType,
    Severity,
    FabricationIssue,
    FabricationReport,
    FabricationDetector
)

__all__ = [
    # 事实提取器
    "FactType",
    "FactSource",
    "Fact",
    "FactExtractor",
    # 事实锁定
    "LockStatus",
    "UpdatePermission",
    "FactLock",
    "FactUpdateRequest",
    "FactLockManager",
    # 防编造检测
    "FabricationType",
    "Severity",
    "FabricationIssue",
    "FabricationReport",
    "FabricationDetector"
]
