#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 流程图数据模型

支持流程图配置和作业指导书生成
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
import enum

from app.models.models import Base


class FlowchartStatus(enum.Enum):
    """流程图状态"""
    DRAFT = "draft"        # 草稿
    PUBLISHED = "published"  # 已发布
    ARCHIVED = "archived"    # 已归档


class Flowchart(Base):
    """流程图表"""
    __tablename__ = "flowcharts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    flowchart_id = Column(String(36), unique=True, nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.project_id"), nullable=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)

    # 流程图信息
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # 生产/质量/安全/行政等

    # 流程图数据
    nodes = Column(JSON, nullable=True)  # 节点列表 [{id, type, position, data}]
    edges = Column(JSON, nullable=True)  # 连线列表 [{id, source, target, label}]

    # 生成的作业指导书
    generated_instruction_id = Column(String(36), nullable=True)

    # 状态
    status = Column(String(20), default=FlowchartStatus.DRAFT.value)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "flowchart_id": self.flowchart_id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "nodes": self.nodes or [],
            "edges": self.edges or [],
            "generated_instruction_id": self.generated_instruction_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FlowchartTemplate(Base):
    """流程图模板表"""
    __tablename__ = "flowchart_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(String(36), unique=True, nullable=False, index=True)

    # 模板信息
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    industry = Column(String(50), nullable=True)

    # 模板数据
    nodes = Column(JSON, nullable=True)
    edges = Column(JSON, nullable=True)

    # 元数据
    is_builtin = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    created_by = Column(String(36), nullable=True)

    # 使用统计
    use_count = Column(Integer, default=0)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "industry": self.industry,
            "nodes": self.nodes or [],
            "edges": self.edges or [],
            "is_builtin": self.is_builtin,
            "is_public": self.is_public,
            "use_count": self.use_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class FlowchartNodeConfig(Base):
    """流程图节点配置表"""
    __tablename__ = "flowchart_node_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(String(36), unique=True, nullable=False, index=True)

    # 节点类型
    node_type = Column(String(50), nullable=False)  # start/end/process/decision/document

    # 配置信息
    name = Column(String(100), nullable=False)
    icon = Column(String(100), nullable=True)
    color = Column(String(20), nullable=True)
    default_size = Column(JSON, nullable=True)  # {width, height}

    # 样式配置
    style_config = Column(JSON, nullable=True)

    # 是否内置
    is_builtin = Column(Boolean, default=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "config_id": self.config_id,
            "node_type": self.node_type,
            "name": self.name,
            "icon": self.icon,
            "color": self.color,
            "default_size": self.default_size or {},
            "style_config": self.style_config or {},
            "is_builtin": self.is_builtin,
        }


# 预定义的节点类型配置
DEFAULT_NODE_TYPES = [
    {
        "node_type": "start",
        "name": "开始",
        "icon": "play-circle",
        "color": "#52c41a",
        "default_size": {"width": 120, "height": 40}
    },
    {
        "node_type": "end",
        "name": "结束",
        "icon": "stop-circle",
        "color": "#ff4d4f",
        "default_size": {"width": 120, "height": 40}
    },
    {
        "node_type": "process",
        "name": "处理过程",
        "icon": "block",
        "color": "#1890ff",
        "default_size": {"width": 160, "height": 60}
    },
    {
        "node_type": "decision",
        "name": "判断",
        "icon": "fork",
        "color": "#faad14",
        "default_size": {"width": 100, "height": 100}
    },
    {
        "node_type": "document",
        "name": "文档",
        "icon": "file-text",
        "color": "#722ed1",
        "default_size": {"width": 140, "height": 50}
    },
    {
        "node_type": "subprocess",
        "name": "子流程",
        "icon": "apartment",
        "color": "#13c2c2",
        "default_size": {"width": 160, "height": 60}
    },
    {
        "node_type": "data",
        "name": "数据",
        "icon": "database",
        "color": "#eb2f96",
        "default_size": {"width": 140, "height": 50}
    },
]


# 预定义的流程图模板
DEFAULT_FLOWCHART_TEMPLATES = [
    {
        "name": "采购流程",
        "category": "采购管理",
        "description": "标准采购流程模板",
        "nodes": [
            {"id": "n1", "type": "start", "position": {"x": 100, "y": 100}, "data": {"label": "开始"}},
            {"id": "n2", "type": "process", "position": {"x": 300, "y": 100}, "data": {"label": "提出采购申请"}},
            {"id": "n3", "type": "decision", "position": {"x": 500, "y": 100}, "data": {"label": "审批"}},
            {"id": "n4", "type": "process", "position": {"x": 700, "y": 50}, "data": {"label": "选择供应商"}},
            {"id": "n5", "type": "process", "position": {"x": 700, "y": 150}, "data": {"label": "修改申请"}},
            {"id": "n6", "type": "process", "position": {"x": 900, "y": 50}, "data": {"label": "签订合同"}},
            {"id": "n7", "type": "end", "position": {"x": 1100, "y": 50}, "data": {"label": "结束"}},
        ],
        "edges": [
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
            {"id": "e3", "source": "n3", "target": "n4", "label": "通过"},
            {"id": "e4", "source": "n3", "target": "n5", "label": "不通过"},
            {"id": "e5", "source": "n5", "target": "n2"},
            {"id": "e6", "source": "n4", "target": "n6"},
            {"id": "e7", "source": "n6", "target": "n7"},
        ]
    },
    {
        "name": "生产流程",
        "category": "生产管理",
        "description": "标准生产流程模板",
        "nodes": [
            {"id": "n1", "type": "start", "position": {"x": 100, "y": 100}, "data": {"label": "开始"}},
            {"id": "n2", "type": "document", "position": {"x": 300, "y": 100}, "data": {"label": "接收生产计划"}},
            {"id": "n3", "type": "process", "position": {"x": 500, "y": 100}, "data": {"label": "准备物料"}},
            {"id": "n4", "type": "process", "position": {"x": 700, "y": 100}, "data": {"label": "生产作业"}},
            {"id": "n5", "type": "process", "position": {"x": 900, "y": 100}, "data": {"label": "质量检验"}},
            {"id": "n6", "type": "decision", "position": {"x": 1100, "y": 100}, "data": {"label": "合格?"}},
            {"id": "n7", "type": "process", "position": {"x": 1300, "y": 50}, "data": {"label": "入库"}},
            {"id": "n8", "type": "process", "position": {"x": 1300, "y": 150}, "data": {"label": "返工/报废"}},
            {"id": "n9", "type": "end", "position": {"x": 1500, "y": 50}, "data": {"label": "结束"}},
        ],
        "edges": [
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
            {"id": "e3", "source": "n3", "target": "n4"},
            {"id": "e4", "source": "n4", "target": "n5"},
            {"id": "e5", "source": "n5", "target": "n6"},
            {"id": "e6", "source": "n6", "target": "n7", "label": "是"},
            {"id": "e7", "source": "n6", "target": "n8", "label": "否"},
            {"id": "e8", "source": "n7", "target": "n9"},
        ]
    },
    {
        "name": "文件控制流程",
        "category": "文件管理",
        "description": "ISO标准文件控制流程",
        "nodes": [
            {"id": "n1", "type": "start", "position": {"x": 100, "y": 100}, "data": {"label": "开始"}},
            {"id": "n2", "type": "process", "position": {"x": 300, "y": 100}, "data": {"label": "文件起草"}},
            {"id": "n3", "type": "process", "position": {"x": 500, "y": 100}, "data": {"label": "部门审核"}},
            {"id": "n4", "type": "decision", "position": {"x": 700, "y": 100}, "data": {"label": "审核通过?"}},
            {"id": "n5", "type": "process", "position": {"x": 900, "y": 50}, "data": {"label": "批准发布"}},
            {"id": "n6", "type": "document", "position": {"x": 900, "y": 150}, "data": {"label": "修改完善"}},
            {"id": "n7", "type": "process", "position": {"x": 1100, "y": 50}, "data": {"label": "分发实施"}},
            {"id": "n8", "type": "end", "position": {"x": 1300, "y": 50}, "data": {"label": "结束"}},
        ],
        "edges": [
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
            {"id": "e3", "source": "n3", "target": "n4"},
            {"id": "e4", "source": "n4", "target": "n5", "label": "是"},
            {"id": "e5", "source": "n4", "target": "n6", "label": "否"},
            {"id": "e6", "source": "n6", "target": "n2"},
            {"id": "e7", "source": "n5", "target": "n7"},
            {"id": "e8", "source": "n7", "target": "n8"},
        ]
    },
]
