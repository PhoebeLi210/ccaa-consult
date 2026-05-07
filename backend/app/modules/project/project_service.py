#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 项目管理服务

核心功能：
1. 项目创建、查询、更新、删除
2. 项目状态管理
3. 企业信息管理
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from app.models.models import Project, ProjectRawInput, ProjectStatus
from app.modules.parser.natural_language_parser import (
    NaturalLanguageParser,
    CompanyInfo,
    LLMParser
)


@dataclass
class CreateProjectRequest:
    """创建项目请求"""
    user_id: str
    free_text: Optional[str] = None
    file_data: Optional[Dict[str, Any]] = None


@dataclass
class UpdateProjectRequest:
    """更新项目请求"""
    project_id: str
    company_info: Dict[str, Any]


class ProjectService:
    """项目管理服务"""

    def __init__(self, db_session=None, llm_client=None):
        """
        初始化服务

        Args:
            db_session: 数据库会话
            llm_client: 大模型客户端
        """
        self.db_session = db_session
        self.parser = LLMParser(llm_client) if llm_client else NaturalLanguageParser()

    async def create_project(self, request: CreateProjectRequest) -> Dict[str, Any]:
        """
        创建项目

        Args:
            request: 创建请求

        Returns:
            创建的项目信息
        """
        # 生成项目ID
        project_id = str(uuid.uuid4())

        # 解析输入
        company_info = None
        parsed_json = None

        if request.free_text:
            # 自然语言解析
            company_info = self.parser.parse(request.free_text)
            parsed_json = company_info.to_dict()

        if request.file_data:
            # 文件数据解析
            if company_info:
                company_info = self.parser.merge_with_file_data(
                    company_info, request.file_data
                )
            else:
                company_info = CompanyInfo(**request.file_data)
            parsed_json = company_info.to_dict()

        # 创建项目记录
        project = Project(
            project_id=project_id,
            user_id=request.user_id,
            company_name=company_info.company_name if company_info else None,
            industry=company_info.industry if company_info else None,
            sub_industry=company_info.sub_industry if company_info else None,
            employee_count=company_info.employee_count if company_info else None,
            office_area_sqm=company_info.office_area_sqm if company_info else None,
            departments=company_info.departments if company_info else None,
            main_equipment=company_info.main_equipment if company_info else None,
            main_processes=company_info.main_processes if company_info else None,
            special_processes=company_info.special_processes if company_info else None,
            certification_type=company_info.certification_type if company_info else None,
            existing_standards=company_info.existing_standards if company_info else None,
            target_standards=company_info.target_standards if company_info else None,
            quality_goals=company_info.quality_goals if company_info else None,
            key_customers=company_info.key_customers if company_info else None,
            status=ProjectStatus.PARSING.value,
        )

        if self.db_session:
            self.db_session.add(project)

            # 保存原始输入
            if request.free_text:
                raw_input = ProjectRawInput(
                    project_id=project_id,
                    input_type="natural_language",
                    content=request.free_text,
                    parsed_json=parsed_json,
                )
                self.db_session.add(raw_input)

            self.db_session.commit()

        return project.to_dict()

    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        获取项目

        Args:
            project_id: 项目ID

        Returns:
            项目信息
        """
        if self.db_session:
            project = self.db_session.query(Project).filter(
                Project.project_id == project_id
            ).first()
            return project.to_dict() if project else None
        return None

    async def list_projects(
        self,
        user_id: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        列出项目

        Args:
            user_id: 用户ID
            status: 状态过滤
            page: 页码
            page_size: 每页数量

        Returns:
            项目列表
        """
        if self.db_session:
            query = self.db_session.query(Project).filter(
                Project.user_id == user_id
            )

            if status:
                query = query.filter(Project.status == status)

            total = query.count()
            projects = query.offset((page - 1) * page_size).limit(page_size).all()

            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [p.to_dict() for p in projects],
            }

        return {"total": 0, "page": page, "page_size": page_size, "items": []}

    async def update_project(
        self,
        project_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新项目

        Args:
            project_id: 项目ID
            updates: 更新内容

        Returns:
            更新后的项目信息
        """
        if self.db_session:
            project = self.db_session.query(Project).filter(
                Project.project_id == project_id
            ).first()

            if project:
                for key, value in updates.items():
                    if hasattr(project, key):
                        setattr(project, key, value)

                project.updated_at = datetime.utcnow()
                self.db_session.commit()

                return project.to_dict()

        return None

    async def confirm_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        确认项目信息

        Args:
            project_id: 项目ID

        Returns:
            更新后的项目信息
        """
        return await self.update_project(
            project_id,
            {"status": ProjectStatus.CONFIRMED.value}
        )

    async def delete_project(self, project_id: str) -> bool:
        """
        删除项目

        Args:
            project_id: 项目ID

        Returns:
            是否成功
        """
        if self.db_session:
            project = self.db_session.query(Project).filter(
                Project.project_id == project_id
            ).first()

            if project:
                self.db_session.delete(project)
                self.db_session.commit()
                return True

        return False

    async def get_missing_fields(self, project_id: str) -> List[Dict[str, str]]:
        """
        获取项目缺失字段

        Args:
            project_id: 项目ID

        Returns:
            缺失字段列表及追问问题
        """
        project = await self.get_project(project_id)
        if not project:
            return []

        # 构建CompanyInfo
        company_info = CompanyInfo(
            company_name=project.get("company_name"),
            industry=project.get("industry"),
            employee_count=project.get("employee_count"),
            departments=project.get("departments", []),
            quality_goals=project.get("quality_goals"),
        )

        # 生成追问问题
        questions = self.parser.generate_follow_up_questions(company_info)
        return questions

    async def answer_question(
        self,
        project_id: str,
        field: str,
        answer: str
    ) -> Optional[Dict[str, Any]]:
        """
        回答追问问题

        Args:
            project_id: 项目ID
            field: 字段名
            answer: 回答内容

        Returns:
            更新后的项目信息
        """
        project = await self.get_project(project_id)
        if not project:
            return None

        # 构建CompanyInfo
        company_info = CompanyInfo(
            company_name=project.get("company_name"),
            industry=project.get("industry"),
            employee_count=project.get("employee_count"),
            departments=project.get("departments", []),
            quality_goals=project.get("quality_goals"),
            special_processes=project.get("special_processes", []),
        )

        # 更新信息
        updated_info = self.parser.update_with_answer(company_info, field, answer)

        # 保存更新
        updates = {field: getattr(updated_info, field)}
        return await self.update_project(project_id, updates)


# API路由示例
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


class CreateProjectInput(BaseModel):
    free_text: Optional[str] = None
    file_data: Optional[Dict[str, Any]] = None


class AnswerQuestionInput(BaseModel):
    field: str
    answer: str


@router.post("/")
async def create_project(
    input_data: CreateProjectInput,
    user_id: str = "default_user"
):
    """创建项目"""
    service = ProjectService()
    request = CreateProjectRequest(
        user_id=user_id,
        free_text=input_data.free_text,
        file_data=input_data.file_data,
    )
    return await service.create_project(request)


@router.get("/{project_id}")
async def get_project(project_id: str):
    """获取项目"""
    service = ProjectService()
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/")
async def list_projects(
    user_id: str = "default_user",
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """列出项目"""
    service = ProjectService()
    return await service.list_projects(user_id, status, page, page_size)


@router.patch("/{project_id}")
async def update_project(project_id: str, updates: Dict[str, Any]):
    """更新项目"""
    service = ProjectService()
    project = await service.update_project(project_id, updates)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/confirm")
async def confirm_project(project_id: str):
    """确认项目"""
    service = ProjectService()
    project = await service.confirm_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    service = ProjectService()
    success = await service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True}


@router.get("/{project_id}/missing-fields")
async def get_missing_fields(project_id: str):
    """获取缺失字段"""
    service = ProjectService()
    return await service.get_missing_fields(project_id)


@router.post("/{project_id}/answer")
async def answer_question(project_id: str, input_data: AnswerQuestionInput):
    """回答问题"""
    service = ProjectService()
    project = await service.answer_question(
        project_id, input_data.field, input_data.answer
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
