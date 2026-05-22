#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - V1.3 新增数据库模型
包含个人模板、团队协作相关模型
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class CustomTemplate(Base):
    """个人自定义模板表 (V1.3)"""
    __tablename__ = "custom_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # 关联用户
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    
    # 模板信息
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # 分类
    document_level = Column(Integer, nullable=False)  # 文档级别 1-4
    standard = Column(String(20), nullable=False)  # ISO9001/14001/45001
    
    # 文件路径
    file_path = Column(String(500), nullable=False)
    
    # 版本管理
    version = Column(String(10), default="1.0")
    change_log = Column(Text, nullable=True)  # 变更说明
    
    # 模板内容
    variables = Column(JSON, nullable=True)  # 变量列表
    
    # 使用统计
    use_count = Column(Integer, default=0)  # 使用次数
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    user = relationship("User", back_populates="custom_templates")
    
    def to_dict(self):
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "document_level": self.document_level,
            "standard": self.standard,
            "version": self.version,
            "variables": self.variables or [],
            "use_count": self.use_count,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Team(Base):
    """团队表 (V1.3)"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # 团队信息
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # 所有者
    owner_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "team_id": self.team_id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TeamMember(Base):
    """团队成员表 (V1.3)"""
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # 关联
    team_id = Column(String(36), ForeignKey("teams.team_id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    
    # 角色: owner/admin/member/viewer
    role = Column(String(20), default="member")
    
    # 状态: active/inactive/pending
    status = Column(String(20), default="active")
    
    # 邀请信息
    invited_by = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    
    # 时间戳
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    team = relationship("Team", back_populates="members")
    user = relationship("User", foreign_keys=[user_id], back_populates="team_members")
    
    def to_dict(self):
        return {
            "member_id": self.member_id,
            "team_id": self.team_id,
            "user_id": self.user_id,
            "role": self.role,
            "status": self.status,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
        }


class ProjectConfig(Base):
    """项目个性化配置表 (V1.3)"""
    __tablename__ = "project_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # 关联项目
    project_id = Column(String(36), ForeignKey("projects.project_id"), nullable=False, unique=True)
    
    # 封面配置
    cover_title = Column(String(200), nullable=True)  # 封面标题
    cover_subtitle = Column(String(200), nullable=True)  # 封面副标题
    cover_logo_url = Column(String(500), nullable=True)  # Logo URL
    
    # 编号配置
    doc_number_prefix = Column(String(20), default="QESMS")  # 编号前缀
    doc_number_format = Column(String(50), default="{prefix}-{level}-{seq:03d}")  # 编号格式
    
    # 样式配置
    primary_color = Column(String(7), default="#1890ff")  # 主题色
    font_family = Column(String(50), default="SimSun")  # 字体
    font_size = Column(Integer, default=12)  # 字号
    
    # 页眉页脚
    header_text = Column(String(200), nullable=True)  # 页眉文字
    footer_text = Column(String(200), nullable=True)  # 页脚文字
    show_page_number = Column(Boolean, default=True)  # 是否显示页码
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "config_id": self.config_id,
            "project_id": self.project_id,
            "cover_title": self.cover_title,
            "cover_subtitle": self.cover_subtitle,
            "cover_logo_url": self.cover_logo_url,
            "doc_number_prefix": self.doc_number_prefix,
            "doc_number_format": self.doc_number_format,
            "primary_color": self.primary_color,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "header_text": self.header_text,
            "footer_text": self.footer_text,
            "show_page_number": self.show_page_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
