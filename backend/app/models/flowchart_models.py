#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V1.4 流程图模型
用于存储和管理作业指导书中的流程图
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
import enum

from app.models.models import Base


class NodeType(enum.Enum):
    """流程节点类型"""
    START = "start"           # 开始节点
    END = "end"               # 结束节点
    PROCESS = "process"       # 处理节点
    DECISION = "decision"     # 判断节点
    DOCUMENT = "document"     # 文档节点
    DATA = "data"             # 数据节点


class Flowchart(Base):
    """流程图表 - 存储完整的流程图定义"""
    __tablename__ = "flowcharts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    flowchart_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # 关联信息
    project_id = Column(String(36), nullable=False, index=True)  # 所属项目
    template_id = Column(String(36), nullable=True)  # 关联的模板ID
    instruction_id = Column(String(36), nullable=True)  # 关联的作业指导书ID
    
    # 流程图基本信息
    name = Column(String(200), nullable=False)  # 流程图名称
    description = Column(Text, nullable=True)  # 描述
    category = Column(String(50), nullable=True)  # 类别：生产/服务/管理/质量
    
    # 流程图数据（JSON格式，兼容LogicFlow等前端库）
    graph_data = Column(JSON, nullable=False)  # {nodes: [], edges: []}
    
    # 节点详细配置
    node_configs = Column(JSON, nullable=True)  # 每个节点的详细配置
    
    # 样式配置
    style_config = Column(JSON, nullable=True)  # 颜色、字体、布局等
    
    # 状态
    status = Column(String(20), default="draft")  # draft/published/archived
    
    # 版本管理
    version = Column(String(10), default="1.0")
    version_history = Column(JSON, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(36), nullable=False)
    
    def to_dict(self):
        return {
            "flowchartId": self.flowchart_id,
            "projectId": self.project_id,
            "templateId": self.template_id,
            "instructionId": self.instruction_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "graphData": self.graph_data,
            "nodeConfigs": self.node_configs or {},
            "styleConfig": self.style_config or {},
            "status": self.status,
            "version": self.version,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class FlowchartTemplate(Base):
    """流程图模板 - 预定义的流程图模板"""
    __tablename__ = "flowchart_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # 模板信息
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # 行业类别
    
    # 适用场景
    applicable_scenarios = Column(JSON, nullable=True)  # ["保洁服务", "设备维修", ...]
    
    # 模板数据
    graph_data = Column(JSON, nullable=False)  # 流程图结构
    node_templates = Column(JSON, nullable=True)  # 节点模板配置
    
    # 关联的作业指导书模板
    instruction_template_id = Column(String(36), nullable=True)
    
    # 元数据
    is_builtin = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    created_by = Column(String(36), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "templateId": self.template_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "applicableScenarios": self.applicable_scenarios or [],
            "graphData": self.graph_data,
            "nodeTemplates": self.node_templates or {},
            "instructionTemplateId": self.instruction_template_id,
            "isBuiltin": self.is_builtin,
            "isPublic": self.is_public,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class FlowchartNodeConfig(Base):
    """流程节点配置 - 节点的详细配置信息"""
    __tablename__ = "flowchart_node_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(String(36), unique=True, nullable=False, index=True)
    flowchart_id = Column(String(36), ForeignKey("flowcharts.flowchart_id"), nullable=False)
    node_id = Column(String(50), nullable=False)  # 流程图中的节点ID
    
    # 节点类型
    node_type = Column(String(20), nullable=False)  # start/process/decision/document/data/end
    
    # 节点内容
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 操作细节
    operation_steps = Column(JSON, nullable=True)  # ["步骤1", "步骤2", ...]
    
    # 关联文档
    related_documents = Column(JSON, nullable=True)  # [{name, template, required}]
    
    # 质量控制点
    quality_checkpoints = Column(JSON, nullable=True)  # [{item, standard, method}]
    
    # 责任人/部门
    responsible_role = Column(String(100), nullable=True)
    responsible_dept = Column(String(100), nullable=True)
    
    # 时间要求
    time_limit = Column(String(50), nullable=True)  # 如："30分钟", "2小时"
    
    # 异常处理
    exception_handling = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "configId": self.config_id,
            "flowchartId": self.flowchart_id,
            "nodeId": self.node_id,
            "nodeType": self.node_type,
            "title": self.title,
            "description": self.description,
            "operationSteps": self.operation_steps or [],
            "relatedDocuments": self.related_documents or [],
            "qualityCheckpoints": self.quality_checkpoints or [],
            "responsibleRole": self.responsible_role,
            "responsibleDept": self.responsible_dept,
            "timeLimit": self.time_limit,
            "exceptionHandling": self.exception_handling,
        }
