#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 数据库模型

数据表：
- projects: 项目表
- project_raw_inputs: 原始输入表
- documents: 文档表
- uploads: 上传文件表
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class ProjectStatus(enum.Enum):
    """项目状态"""
    DRAFT = "draft"  # 草稿
    PARSING = "parsing"  # 解析中
    CONFIRMED = "confirmed"  # 已确认
    GENERATING = "generating"  # 生成中
    COMPLETED = "completed"  # 已完成
    ARCHIVED = "archived"  # 已归档


class InputType(enum.Enum):
    """输入类型"""
    NATURAL_LANGUAGE = "natural_language"  # 自然语言
    FILE_UPLOAD = "file_upload"  # 文件上传


class DocumentType(enum.Enum):
    """文档类型"""
    MANUAL = "manual"  # 管理手册
    PROCEDURE = "procedure"  # 程序文件
    RECORD = "record"  # 记录表格
    INSTRUCTION = "instruction"  # 作业指导书
    FORM = "form"  # 表单


class Project(Base):
    """项目表"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(36), unique=True, nullable=False, index=True)  # UUID
    user_id = Column(String(36), nullable=False, index=True)  # 用户ID

    # 企业基本信息
    company_name = Column(String(200), nullable=True)
    industry = Column(String(50), nullable=True)
    sub_industry = Column(String(100), nullable=True)
    employee_count = Column(Integer, nullable=True)
    office_area_sqm = Column(Float, nullable=True)

    # 认证信息
    certification_type = Column(String(50), nullable=True)  # 初次认证/监督审核/再认证
    existing_standards = Column(JSON, nullable=True)  # 已有标准列表
    target_standards = Column(JSON, nullable=True)  # 目标标准列表

    # 组织信息
    departments = Column(JSON, nullable=True)  # 部门列表
    main_equipment = Column(JSON, nullable=True)  # 主要设备
    main_processes = Column(JSON, nullable=True)  # 主要过程
    special_processes = Column(JSON, nullable=True)  # 特殊过程

    # 质量信息
    quality_goals = Column(Text, nullable=True)  # 质量目标
    key_customers = Column(Text, nullable=True)  # 主要客户

    # 项目状态
    status = Column(String(20), default=ProjectStatus.DRAFT.value)

    # 配置信息
    config = Column(JSON, nullable=True)  # 个性化配置

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    raw_inputs = relationship("ProjectRawInput", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    uploads = relationship("Upload", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "industry": self.industry,
            "sub_industry": self.sub_industry,
            "employee_count": self.employee_count,
            "office_area_sqm": self.office_area_sqm,
            "certification_type": self.certification_type,
            "existing_standards": self.existing_standards or [],
            "target_standards": self.target_standards or [],
            "departments": self.departments or [],
            "main_equipment": self.main_equipment or [],
            "main_processes": self.main_processes or [],
            "special_processes": self.special_processes or [],
            "quality_goals": self.quality_goals,
            "key_customers": self.key_customers,
            "status": self.status,
            "config": self.config or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProjectRawInput(Base):
    """原始输入表"""
    __tablename__ = "project_raw_inputs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(36), ForeignKey("projects.project_id"), nullable=False, index=True)

    input_type = Column(String(20), nullable=False)  # natural_language / file_upload
    content = Column(Text, nullable=True)  # 原始内容（自然语言文本或文件路径）
    parsed_json = Column(JSON, nullable=True)  # 解析后的结构化数据

    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    project = relationship("Project", back_populates="raw_inputs")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "input_type": self.input_type,
            "content": self.content,
            "parsed_json": self.parsed_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Document(Base):
    """文档表"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(36), unique=True, nullable=False, index=True)  # UUID
    project_id = Column(String(36), ForeignKey("projects.project_id"), nullable=False, index=True)

    # 文档信息
    doc_type = Column(String(50), nullable=False)  # manual/procedure/record/instruction/form
    title = Column(String(200), nullable=False)
    file_name = Column(String(200), nullable=True)

    # 内容
    ai_content = Column(Text, nullable=True)  # AI生成的原始内容
    human_content = Column(Text, nullable=True)  # 人工修改后的内容
    current_content = Column(Text, nullable=True)  # 当前内容

    # 状态
    confirmed = Column(Boolean, default=False)  # 是否已确认
    confirmed_at = Column(DateTime, nullable=True)
    confirmed_by = Column(String(36), nullable=True)

    # 差异分析
    diff_metrics = Column(JSON, nullable=True)  # {edit_distance: 0, change_ratio: 0.0}

    # 版本
    version = Column(Integer, default=1)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    project = relationship("Project", back_populates="documents")

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "project_id": self.project_id,
            "doc_type": self.doc_type,
            "title": self.title,
            "file_name": self.file_name,
            "confirmed": self.confirmed,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
            "diff_metrics": self.diff_metrics or {},
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Upload(Base):
    """上传文件表"""
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    upload_id = Column(String(36), unique=True, nullable=False, index=True)  # UUID
    project_id = Column(String(36), ForeignKey("projects.project_id"), nullable=False, index=True)

    # 文件信息
    file_name = Column(String(200), nullable=False)
    file_url = Column(String(500), nullable=True)  # 存储路径
    file_type = Column(String(50), nullable=True)  # excel/word/pdf/image
    file_size = Column(Integer, nullable=True)  # 字节数

    # 解析状态
    parse_status = Column(String(20), default="pending")  # pending/parsing/parsed/failed
    parse_result = Column(JSON, nullable=True)  # 解析结果
    parse_error = Column(Text, nullable=True)  # 解析错误信息

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    parsed_at = Column(DateTime, nullable=True)

    # 关联
    project = relationship("Project", back_populates="uploads")

    def to_dict(self):
        return {
            "id": self.id,
            "upload_id": self.upload_id,
            "project_id": self.project_id,
            "file_name": self.file_name,
            "file_url": self.file_url,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "parse_status": self.parse_status,
            "parse_result": self.parse_result,
            "parse_error": self.parse_error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "parsed_at": self.parsed_at.isoformat() if self.parsed_at else None,
        }


class Template(Base):
    """模板表"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(String(36), unique=True, nullable=False, index=True)

    # 模板信息
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # iso9001/iso14001/iso45001/industry
    industry = Column(String(50), nullable=True)  # 行业

    # 模板内容
    content = Column(Text, nullable=True)  # 模板内容（可以是文件路径或内容）
    variables = Column(JSON, nullable=True)  # 变量列表

    # 元数据
    is_builtin = Column(Boolean, default=False)  # 是否内置模板
    is_public = Column(Boolean, default=False)  # 是否公开
    created_by = Column(String(36), nullable=True)  # 创建者

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
            "variables": self.variables or [],
            "is_builtin": self.is_builtin,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
