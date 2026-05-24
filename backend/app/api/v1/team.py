#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 团队协作API (V1.3)
支持团队管理、成员协作、权限控�?"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid

from app.core.database import get_db
from app.models.models import Team, TeamMember, Project
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/teams", tags=["团队协作"])


# ============ 请求/响应模型 ============

class TeamCreateRequest(BaseModel):
    """创建团队请求"""
    name: str = Field(..., min_length=1, max_length=100, description="团队名称")
    description: Optional[str] = Field(None, max_length=500, description="团队描述")


class TeamUpdateRequest(BaseModel):
    """更新团队请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class TeamMemberInviteRequest(BaseModel):
    """邀请成员请�?""
    email: str = Field(..., description="被邀请人邮箱")
    role: str = Field(default="member", description="角色: admin/member/viewer")


class TeamMemberUpdateRequest(BaseModel):
    """更新成员请求"""
    role: Optional[str] = Field(None, description="角色: admin/member/viewer")
    status: Optional[str] = Field(None, description="状�? active/inactive")


class TeamResponse(BaseModel):
    """团队响应"""
    team_id: str
    name: str
    description: Optional[str]
    owner_id: str
    owner_name: str
    member_count: int
    project_count: int
    created_at: str
    updated_at: str


class TeamMemberResponse(BaseModel):
    """团队成员响应"""
    member_id: str
    user_id: str
    user_name: str
    user_email: str
    role: str
    status: str
    joined_at: str


class TeamDetailResponse(TeamResponse):
    """团队详情响应"""
    members: List[TeamMemberResponse]
    projects: List[Dict[str, Any]]


class TeamListResponse(BaseModel):
    """团队列表响应"""
    total: int
    teams: List[TeamResponse]


# ============ 角色权限定义 ============

ROLE_PERMISSIONS = {
    "owner": {
        "can_manage_team": True,
        "can_invite_member": True,
        "can_remove_member": True,
        "can_manage_project": True,
        "can_view_all_projects": True,
        "can_edit_all_documents": True,
    },
    "admin": {
        "can_manage_team": False,
        "can_invite_member": True,
        "can_remove_member": True,
        "can_manage_project": True,
        "can_view_all_projects": True,
        "can_edit_all_documents": True,
    },
    "member": {
        "can_manage_team": False,
        "can_invite_member": False,
        "can_remove_member": False,
        "can_manage_project": True,
        "can_view_all_projects": True,
        "can_edit_all_documents": True,
    },
    "viewer": {
        "can_manage_team": False,
        "can_invite_member": False,
        "can_remove_member": False,
        "can_manage_project": False,
        "can_view_all_projects": True,
        "can_edit_all_documents": False,
    },
}


# ============ API路由 ============

@router.post("/create", response_model=TeamResponse, summary="创建团队")
async def create_team(
    request: TeamCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新团队，当前用户自动成为团队所有�?""
    # 检查用户是否已有团�?    existing_team = db.query(Team).filter(
        Team.owner_id == current_user["id"]
    ).first()
    
    if existing_team:
        raise HTTPException(status_code=400, detail="您已拥有一个团�?)
    
    # 创建团队
    team_id = str(uuid.uuid4())
    team = Team(
        team_id=team_id,
        name=request.name,
        description=request.description,
        owner_id=current_user["id"],
    )
    
    db.add(team)
    db.commit()
    db.refresh(team)
    
    # 创建者自动成为团队成员（owner角色�?    member = TeamMember(
        member_id=str(uuid.uuid4()),
        team_id=team_id,
        user_id=current_user["id"],
        role="owner",
        status="active",
        invited_by=current_user["id"],
    )
    
    db.add(member)
    db.commit()
    
    return _team_to_response(team, db)


@router.get("/my", response_model=TeamListResponse, summary="获取我的团队列表")
async def get_my_teams(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户所属的所有团�?""
    # 查询用户作为成员的团�?    member_teams = db.query(Team).join(
        TeamMember, Team.team_id == TeamMember.team_id
    ).filter(
        TeamMember.user_id == current_user["id"],
        TeamMember.status == "active",
    ).all()
    
    return TeamListResponse(
        total=len(member_teams),
        teams=[_team_to_response(team, db) for team in member_teams],
    )


@router.get("/{team_id}", response_model=TeamDetailResponse, summary="获取团队详情")
async def get_team_detail(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取团队的详细信息，包括成员和项�?""
    # 检查权�?    if not _is_team_member(team_id, current_user["id"], db):
        raise HTTPException(status_code=403, detail="您不是该团队成员")
    
    team = db.query(Team).filter(Team.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="团队不存�?)
    
    # 获取成员列表
    members = db.query(TeamMember, User).join(
        User, TeamMember.user_id == User.user_id
    ).filter(
        TeamMember.team_id == team_id,
    ).all()
    
    member_responses = []
    for member, user in members:
        member_responses.append(TeamMemberResponse(
            member_id=member.member_id,
            user_id=user.user_id,
            user_name=user.username or user.email,
            user_email=user.email,
            role=member.role,
            status=member.status,
            joined_at=member.joined_at.isoformat() if member.joined_at else "",
        ))
    
    # 获取团队项目
    projects = db.query(Project).filter(
        Project.team_id == team_id,
    ).all()
    
    project_list = [
        {
            "project_id": p.project_id,
            "company_name": p.company_name,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else "",
        }
        for p in projects
    ]
    
    return TeamDetailResponse(
        **_team_to_response(team, db).dict(),
        members=member_responses,
        projects=project_list,
    )


@router.patch("/{team_id}", response_model=TeamResponse, summary="更新团队信息")
async def update_team(
    team_id: str,
    request: TeamUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新团队基本信息（仅owner和admin�?""
    # 检查权�?    if not _has_team_permission(team_id, current_user["id"], "can_manage_team", db):
        raise HTTPException(status_code=403, detail="无权更新团队信息")
    
    team = db.query(Team).filter(Team.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="团队不存�?)
    
    if request.name is not None:
        team.name = request.name
    if request.description is not None:
        team.description = request.description
    
    team.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(team)
    
    return _team_to_response(team, db)


@router.post("/{team_id}/invite", response_model=TeamMemberResponse, summary="邀请成�?)
async def invite_member(
    team_id: str,
    request: TeamMemberInviteRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """邀请新成员加入团队"""
    # 检查权�?    if not _has_team_permission(team_id, current_user["id"], "can_invite_member", db):
        raise HTTPException(status_code=403, detail="无权邀请成�?)
    
    team = db.query(Team).filter(Team.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="团队不存�?)
    
    # 查找被邀请用�?    invited_user = db.query(User).filter(User.email == request.email).first()
    
    if not invited_user:
        raise HTTPException(status_code=404, detail="该邮箱未注册")
    
    # 检查是否已是成�?    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == invited_user.user_id,
    ).first()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="该用户已是团队成�?)
    
    # 创建成员记录
    member = TeamMember(
        member_id=str(uuid.uuid4()),
        team_id=team_id,
        user_id=invited_user.user_id,
        role=request.role,
        status="active",
        invited_by=current_user["id"],
    )
    
    db.add(member)
    db.commit()
    db.refresh(member)
    
    return TeamMemberResponse(
        member_id=member.member_id,
        user_id=invited_user.user_id,
        user_name=invited_user.username or invited_user.email,
        user_email=invited_user.email,
        role=member.role,
        status=member.status,
        joined_at=member.joined_at.isoformat() if member.joined_at else "",
    )


@router.patch("/{team_id}/members/{member_id}", response_model=TeamMemberResponse, summary="更新成员信息")
async def update_member(
    team_id: str,
    member_id: str,
    request: TeamMemberUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新团队成员的角色或状�?""
    # 检查权�?    if not _has_team_permission(team_id, current_user["id"], "can_manage_team", db):
        raise HTTPException(status_code=403, detail="无权更新成员信息")
    
    member = db.query(TeamMember).filter(
        TeamMember.member_id == member_id,
        TeamMember.team_id == team_id,
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="成员不存�?)
    
    # 不能修改owner
    if member.role == "owner":
        raise HTTPException(status_code=403, detail="不能修改团队所有�?)
    
    if request.role is not None:
        member.role = request.role
    if request.status is not None:
        member.status = request.status
    
    db.commit()
    db.refresh(member)
    
    user = db.query(User).filter(User.user_id == member.user_id).first()
    
    return TeamMemberResponse(
        member_id=member.member_id,
        user_id=user.user_id,
        user_name=user.username or user.email,
        user_email=user.email,
        role=member.role,
        status=member.status,
        joined_at=member.joined_at.isoformat() if member.joined_at else "",
    )


@router.delete("/{team_id}/members/{member_id}", summary="移除成员")
async def remove_member(
    team_id: str,
    member_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """从团队中移除成员"""
    # 检查权�?    if not _has_team_permission(team_id, current_user["id"], "can_remove_member", db):
        raise HTTPException(status_code=403, detail="无权移除成员")
    
    member = db.query(TeamMember).filter(
        TeamMember.member_id == member_id,
        TeamMember.team_id == team_id,
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="成员不存�?)
    
    # 不能移除owner
    if member.role == "owner":
        raise HTTPException(status_code=403, detail="不能移除团队所有�?)
    
    # 不能移除自己
    if member.user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="不能移除自己，请使用退出团队功�?)
    
    db.delete(member)
    db.commit()
    
    return {"message": "成员已移�?, "member_id": member_id}


@router.post("/{team_id}/leave", summary="退出团�?)
async def leave_team(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """当前用户退出团队（owner不能退出）"""
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user["id"],
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="您不是该团队成员")
    
    if member.role == "owner":
        raise HTTPException(
            status_code=400, 
            detail="团队所有者不能退出，请先转让所有权或解散团�?
        )
    
    db.delete(member)
    db.commit()
    
    return {"message": "已退出团�?}


@router.post("/{team_id}/transfer-ownership", summary="转让团队所有权")
async def transfer_ownership(
    team_id: str,
    new_owner_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """转让团队所有权给指定成�?""
    team = db.query(Team).filter(Team.team_id == team_id).first()
    
    if not team:
        raise HTTPException(status_code=404, detail="团队不存�?)
    
    # 只有owner可以转让
    if team.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="只有团队所有者可以转让所有权")
    
    # 检查新所有者是否是团队成员
    new_owner_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == new_owner_id,
        TeamMember.status == "active",
    ).first()
    
    if not new_owner_member:
        raise HTTPException(status_code=400, detail="指定用户不是团队成员")
    
    # 更新团队所有�?    team.owner_id = new_owner_id
    
    # 更新原owner角色为admin
    old_owner_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user["id"],
    ).first()
    
    if old_owner_member:
        old_owner_member.role = "admin"
    
    # 更新新owner角色
    new_owner_member.role = "owner"
    
    db.commit()
    
    return {"message": "团队所有权已转�?, "new_owner_id": new_owner_id}


@router.delete("/{team_id}", summary="解散团队")
async def delete_team(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """解散团队（仅owner�?""
    team = db.query(Team).filter(Team.team_id == team_id).first()
    
    if not team:
        raise HTTPException(status_code=404, detail="团队不存�?)
    
    if team.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="只有团队所有者可以解散团�?)
    
    # 删除所有成员记�?    db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
    
    # 删除团队
    db.delete(team)
    db.commit()
    
    return {"message": "团队已解�?}


@router.get("/{team_id}/permissions", summary="获取当前用户权限")
async def get_my_permissions(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户在团队中的权限列�?""
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user["id"],
        TeamMember.status == "active",
    ).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="您不是该团队成员")
    
    permissions = ROLE_PERMISSIONS.get(member.role, {})
    
    return {
        "role": member.role,
        "permissions": permissions,
    }


@router.post("/{team_id}/projects/{project_id}/assign", summary="分配项目到团�?)
async def assign_project_to_team(
    team_id: str,
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """将项目分配给团队"""
    # 检查权�?    if not _has_team_permission(team_id, current_user["id"], "can_manage_project", db):
        raise HTTPException(status_code=403, detail="无权管理团队项目")
    
    # 检查项目所有权
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user["id"],
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权�?)
    
    # 分配项目到团�?    project.team_id = team_id
    db.commit()
    
    return {"message": "项目已分配到团队", "project_id": project_id}


# ============ 辅助函数 ============

def _is_team_member(team_id: str, user_id: str, db: Session) -> bool:
    """检查用户是否是团队成员"""
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id,
        TeamMember.status == "active",
    ).first()
    return member is not None


def _has_team_permission(team_id: str, user_id: str, permission: str, db: Session) -> bool:
    """检查用户是否有指定权限"""
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id,
        TeamMember.status == "active",
    ).first()
    
    if not member:
        return False
    
    role_permissions = ROLE_PERMISSIONS.get(member.role, {})
    return role_permissions.get(permission, False)


def _team_to_response(team: Team, db: Session) -> TeamResponse:
    """将团队模型转换为响应"""
    owner = db.query(User).filter(User.user_id == team.owner_id).first()
    
    member_count = db.query(TeamMember).filter(
        TeamMember.team_id == team.team_id,
        TeamMember.status == "active",
    ).count()
    
    project_count = db.query(Project).filter(
        Project.team_id == team.team_id,
    ).count()
    
    return TeamResponse(
        team_id=team.team_id,
        name=team.name,
        description=team.description,
        owner_id=team.owner_id,
        owner_name=owner.username if owner else "Unknown",
        member_count=member_count,
        project_count=project_count,
        created_at=team.created_at.isoformat() if team.created_at else "",
        updated_at=team.updated_at.isoformat() if team.updated_at else "",
    )
