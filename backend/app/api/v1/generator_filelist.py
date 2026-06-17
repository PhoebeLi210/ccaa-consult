#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 文件清单生成API接口
根据行业配置生成完整的文件清单
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import IndustryConfig, IndustrySpecialFile

router = APIRouter()


class FileListRequest(BaseModel):
    """文件清单生成请求"""
    industry_code: str = Field(..., description="行业代码")
    company_info: Dict[str, Any] = Field(..., description="企业信息")
    include_equipment: bool = Field(True, description="是否包含设备操作规程")
    include_emergency_plans: bool = Field(True, description="是否包含应急预案")
    equipment_list: Optional[List[Dict[str, Any]]] = Field(None, description="设备清单")
    levels: Optional[List[str]] = Field(None, description="文件层级过滤: A/B/C/D")


class FileItem(BaseModel):
    """单个文件项"""
    file_code: str
    file_name: str
    file_level: str  # A/B/C/D
    category: str  # manual/procedure/regulation/instruction/form/plan/equipment_op/emergency_plan
    iso_clause: Optional[str] = None
    is_industry_specific: bool = False  # 是否为行业特有文件
    is_dynamic: bool = False  # 是否为动态生成文件
    description: Optional[str] = None


class FileListResponse(BaseModel):
    """文件清单响应"""
    industry_code: str
    industry_name: str
    total_count: int
    level_counts: Dict[str, int]  # {"A": 1, "B": 27, "C": 25, "D": 55}
    files: List[FileItem]


# 一级文件（通用）
COMMON_LEVEL_A_FILES = [
    {"file_code": "A-001", "file_name": "管理手册", "category": "manual", "iso_clause": "全部"},
]

# 二级文件（通用27个程序文件）
COMMON_LEVEL_B_FILES = [
    {"file_code": "B-001", "file_name": "文件控制程序", "category": "procedure", "iso_clause": "7.5"},
    {"file_code": "B-002", "file_name": "记录控制程序", "category": "procedure", "iso_clause": "7.5"},
    {"file_code": "B-003", "file_name": "内部审核程序", "category": "procedure", "iso_clause": "9.2"},
    {"file_code": "B-004", "file_name": "管理评审程序", "category": "procedure", "iso_clause": "9.3"},
    {"file_code": "B-005", "file_name": "不合格品控制程序", "category": "procedure", "iso_clause": "8.7"},
    {"file_code": "B-006", "file_name": "纠正措施程序", "category": "procedure", "iso_clause": "10.2"},
    {"file_code": "B-007", "file_name": "预防措施程序", "category": "procedure", "iso_clause": "10.2"},
    {"file_code": "B-008", "file_name": "人力资源程序", "category": "procedure", "iso_clause": "7.1"},
    {"file_code": "B-009", "file_name": "基础设施程序", "category": "procedure", "iso_clause": "7.1"},
    {"file_code": "B-010", "file_name": "工作环境程序", "category": "procedure", "iso_clause": "7.1"},
    {"file_code": "B-011", "file_name": "与顾客有关的过程控制程序", "category": "procedure", "iso_clause": "8.2"},
    {"file_code": "B-012", "file_name": "设计和开发控制程序", "category": "procedure", "iso_clause": "8.3"},
    {"file_code": "B-013", "file_name": "采购控制程序", "category": "procedure", "iso_clause": "8.4"},
    {"file_code": "B-014", "file_name": "生产和服务提供控制程序", "category": "procedure", "iso_clause": "8.5"},
    {"file_code": "B-015", "file_name": "标识和可追溯性控制程序", "category": "procedure", "iso_clause": "8.5"},
    {"file_code": "B-016", "file_name": "顾客财产控制程序", "category": "procedure", "iso_clause": "8.5"},
    {"file_code": "B-017", "file_name": "产品防护程序", "category": "procedure", "iso_clause": "8.5"},
    {"file_code": "B-018", "file_name": "监视和测量设备控制程序", "category": "procedure", "iso_clause": "7.1"},
    {"file_code": "B-019", "file_name": "顾客满意度测量程序", "category": "procedure", "iso_clause": "9.1"},
    {"file_code": "B-020", "file_name": "内部审核程序", "category": "procedure", "iso_clause": "9.2"},
    {"file_code": "B-021", "file_name": "过程监视和测量程序", "category": "procedure", "iso_clause": "8.5"},
    {"file_code": "B-022", "file_name": "产品监视和测量程序", "category": "procedure", "iso_clause": "8.6"},
    {"file_code": "B-023", "file_name": "不合格品控制程序", "category": "procedure", "iso_clause": "8.7"},
    {"file_code": "B-024", "file_name": "数据分析程序", "category": "procedure", "iso_clause": "9.1"},
    {"file_code": "B-025", "file_name": "持续改进程序", "category": "procedure", "iso_clause": "10.1"},
    {"file_code": "B-026", "file_name": "环境因素识别与评价程序", "category": "procedure", "iso_clause": "6.1"},
    {"file_code": "B-027", "file_name": "危险源辨识与风险评价程序", "category": "procedure", "iso_clause": "6.1"},
]

# 三级文件（通用15个管理制度 + 10个操作规程）
COMMON_LEVEL_C_FILES = [
    {"file_code": "C-001", "file_name": "检验试验设备管理制度", "category": "regulation", "iso_clause": "7.1"},
    {"file_code": "C-002", "file_name": "消防安全管理制度", "category": "regulation", "iso_clause": "8.1"},
    {"file_code": "C-003", "file_name": "安全生产管理制度", "category": "regulation", "iso_clause": "8.1"},
    {"file_code": "C-004", "file_name": "设备管理制度", "category": "regulation", "iso_clause": "7.1"},
    {"file_code": "C-005", "file_name": "仓库管理制度", "category": "regulation", "iso_clause": "8.5"},
    {"file_code": "C-006", "file_name": "危险化学品管理制度", "category": "regulation", "iso_clause": "8.1"},
    {"file_code": "C-007", "file_name": "劳动防护用品管理制度", "category": "regulation", "iso_clause": "8.1"},
    {"file_code": "C-008", "file_name": "培训管理制度", "category": "regulation", "iso_clause": "7.2"},
    {"file_code": "C-009", "file_name": "文件档案管理制度", "category": "regulation", "iso_clause": "7.5"},
    {"file_code": "C-010", "file_name": "会议管理制度", "category": "regulation", "iso_clause": "5.1"},
    {"file_code": "C-011", "file_name": "卫生管理制度", "category": "regulation", "iso_clause": "7.1"},
    {"file_code": "C-012", "file_name": "节能降耗管理制度", "category": "regulation", "iso_clause": "7.1"},
    {"file_code": "C-013", "file_name": "环境保护管理制度", "category": "regulation", "iso_clause": "6.1"},
    {"file_code": "C-014", "file_name": "职业健康管理制度", "category": "regulation", "iso_clause": "6.1"},
    {"file_code": "C-015", "file_name": "应急预案管理制度", "category": "regulation", "iso_clause": "8.1"},
    # 操作规程（固定10个）
    {"file_code": "C-016", "file_name": "电脑操作规程", "category": "instruction", "iso_clause": "7.1"},
    {"file_code": "C-017", "file_name": "空调操作规程", "category": "instruction", "iso_clause": "7.1"},
    {"file_code": "C-018", "file_name": "打印机操作规程", "category": "instruction", "iso_clause": "7.1"},
    {"file_code": "C-019", "file_name": "复印机操作规程", "category": "instruction", "iso_clause": "7.1"},
    {"file_code": "C-020", "file_name": "投影仪操作规程", "category": "instruction", "iso_clause": "7.1"},
    {"file_code": "C-021", "file_name": "碎纸机操作规程", "category": "instruction", "iso_clause": "7.1"},
    {"file_code": "C-022", "file_name": "饮水机操作规程", "category": "instruction", "iso_clause": "7.1"},
    {"file_code": "C-023", "file_name": "消防器材操作规程", "category": "instruction", "iso_clause": "8.1"},
    {"file_code": "C-024", "file_name": "急救设备操作规程", "category": "instruction", "iso_clause": "8.1"},
    {"file_code": "C-025", "file_name": "监控设备操作规程", "category": "instruction", "iso_clause": "8.1"},
]


@router.post("/file-list", response_model=FileListResponse, summary="生成文件清单")
async def generate_file_list(request: FileListRequest, db: AsyncSession = Depends(get_db)):
    """
    根据行业配置生成完整的文件清单

    返回该行业需要生成的全部文件列表，包括：
    - 通用文件（所有行业都需要）
    - 行业特有文件（根据IndustrySpecialFile配置）
    - 设备操作规程（根据设备清单动态生成）
    - 应急预案（根据行业配置动态生成）
    """
    # 1. 查询行业配置
    result = await db.execute(
        select(IndustryConfig).where(
            IndustryConfig.industry_code == request.industry_code,
            IndustryConfig.is_active == True
        )
    )
    industry_config = result.scalar_one_or_none()

    if not industry_config:
        raise HTTPException(
            status_code=404,
            detail=f"行业配置不存在或未启用: {request.industry_code}"
        )

    industry_name = industry_config.industry_name
    all_files: List[FileItem] = []

    # 2. 添加通用文件
    for f in COMMON_LEVEL_A_FILES:
        all_files.append(FileItem(
            file_code=f["file_code"],
            file_name=f["file_name"],
            file_level="A",
            category=f["category"],
            iso_clause=f.get("iso_clause"),
            is_industry_specific=False,
            is_dynamic=False,
        ))

    for f in COMMON_LEVEL_B_FILES:
        all_files.append(FileItem(
            file_code=f["file_code"],
            file_name=f["file_name"],
            file_level="B",
            category=f["category"],
            iso_clause=f.get("iso_clause"),
            is_industry_specific=False,
            is_dynamic=False,
        ))

    for f in COMMON_LEVEL_C_FILES:
        all_files.append(FileItem(
            file_code=f["file_code"],
            file_name=f["file_name"],
            file_level="C",
            category=f["category"],
            iso_clause=f.get("iso_clause"),
            is_industry_specific=False,
            is_dynamic=False,
        ))

    # 3. 查询并添加行业特有文件
    result = await db.execute(
        select(IndustrySpecialFile).where(
            IndustrySpecialFile.industry_id == industry_config.id
        ).order_by(IndustrySpecialFile.sort_order)
    )
    special_files = result.scalars().all()

    for sf in special_files:
        all_files.append(FileItem(
            file_code=sf.file_code,
            file_name=sf.file_name,
            file_level=sf.file_level,
            category=sf.category or "procedure",
            iso_clause=sf.iso_clause,
            is_industry_specific=True,
            is_dynamic=False,
            description=sf.description,
        ))

    # 4. 添加设备操作规程（动态生成）
    if request.include_equipment and request.equipment_list:
        equipment_counter = 1
        for equipment in request.equipment_list:
            eq_name = equipment.get("name", "")
            if not eq_name:
                continue
            all_files.append(FileItem(
                file_code=f"C-EQ-{equipment_counter:03d}",
                file_name=f"{eq_name}操作规程",
                file_level="C",
                category="equipment_op",
                iso_clause="7.1",
                is_industry_specific=False,
                is_dynamic=True,
                description=f"设备操作规程：{eq_name}",
            ))
            equipment_counter += 1

    # 5. 添加应急预案（根据行业配置动态生成）
    if request.include_emergency_plans and industry_config.emergency_plans:
        emergency_counter = 1
        for plan in industry_config.emergency_plans:
            plan_name = plan if isinstance(plan, str) else plan.get("name", "")
            if not plan_name:
                continue
            all_files.append(FileItem(
                file_code=f"D-EP-{emergency_counter:03d}",
                file_name=f"{plan_name}应急预案",
                file_level="D",
                category="emergency_plan",
                iso_clause="8.1",
                is_industry_specific=True,
                is_dynamic=True,
                description=f"应急预案：{plan_name}",
            ))
            emergency_counter += 1

    # 6. 按层级过滤
    if request.levels:
        level_set = set(l.upper() for l in request.levels)
        all_files = [f for f in all_files if f.file_level in level_set]

    # 7. 统计各层级数量
    level_counts: Dict[str, int] = {}
    for f in all_files:
        level_counts[f.file_level] = level_counts.get(f.file_level, 0) + 1

    return FileListResponse(
        industry_code=request.industry_code,
        industry_name=industry_name,
        total_count=len(all_files),
        level_counts=level_counts,
        files=all_files,
    )
