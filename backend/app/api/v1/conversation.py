#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 多轮对话API
支持追问缺失信息、对话历史管理
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid
import json

from app.core.database import get_db
from app.models.models import Project, ProjectRawInput
from app.api.v1.parse import parse_with_llm, ParsedCompanyInfo, INDUSTRY_CODE_MAP

router = APIRouter(prefix="/conversation", tags=["多轮对话"])


# ============ 内存会话存储（生产环境应使用Redis）============
conversation_sessions: Dict[str, Dict[str, Any]] = {}


# ============ 请求/响应模型 ============

class ConversationStartRequest(BaseModel):
    """开始对话请求"""
    project_id: Optional[str] = Field(None, description="项目ID（如有）")
    initial_text: str = Field(..., description="用户初始输入")


class ConversationContinueRequest(BaseModel):
    """继续对话请求"""
    session_id: str = Field(..., description="会话ID")
    answer: str = Field(..., description="用户对追问的回答")


class FollowUpQuestion(BaseModel):
    """追问问题"""
    field: str = Field(..., description="字段名")
    question: str = Field(..., description="问题文本")
    example: Optional[str] = Field(None, description="示例回答")
    reason: Optional[str] = Field(None, description="为什么需要这个信息")


class ConversationResponse(BaseModel):
    """对话响应"""
    session_id: str
    status: str = Field(..., description="状态: collecting/complete")
    parsed_info: Dict[str, Any]
    missing_fields: List[str]
    follow_up_questions: List[FollowUpQuestion] = []
    progress_percent: int = Field(0, description="信息完整度百分比")
    message: str


class ConversationStatusResponse(BaseModel):
    """会话状态响应"""
    session_id: str
    status: str
    created_at: str
    last_updated: str
    message_count: int
    current_info: Dict[str, Any]


# ============ API路由 ============

@router.post("/start", response_model=ConversationResponse, summary="开始多轮对话")
async def start_conversation(
    request: ConversationStartRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    开始一个新的多轮对话会话
    
    解析用户初始输入，识别缺失字段，生成追问问题
    """
    session_id = str(uuid.uuid4())
    
    # 解析初始输入
    try:
        parsed_info = await parse_with_llm(request.initial_text)
    except Exception as e:
        # LLM解析失败，使用规则解析
        from app.api.v1.parse import parse_with_rules
        parsed_info = parse_with_rules(request.initial_text)
    
    # 识别缺失字段
    missing_fields = _identify_missing_fields(parsed_info)
    
    # 生成追问问题
    follow_up_questions = _generate_follow_up_questions(missing_fields, parsed_info)
    
    # 计算进度
    total_fields = 8  # 核心字段数
    filled_fields = total_fields - len(missing_fields)
    progress = int((filled_fields / total_fields) * 100)
    
    # 确定状态
    status = "complete" if not missing_fields else "collecting"
    
    # 保存会话
    conversation_sessions[session_id] = {
        "project_id": request.project_id,
        "parsed_info": parsed_info,
        "missing_fields": missing_fields,
        "history": [
            {"role": "user", "content": request.initial_text, "timestamp": datetime.utcnow().isoformat()}
        ],
        "created_at": datetime.utcnow().isoformat(),
        "last_updated": datetime.utcnow().isoformat(),
        "status": status,
    }
    
    # 如果有项目ID，保存到项目原始输入
    if request.project_id:
        await _save_to_project_raw_input(request.project_id, request.initial_text, parsed_info, db)
    
    return ConversationResponse(
        session_id=session_id,
        status=status,
        parsed_info=parsed_info,
        missing_fields=missing_fields,
        follow_up_questions=follow_up_questions,
        progress_percent=progress,
        message="信息收集完成" if status == "complete" else f"还需要补充{len(missing_fields)}项信息",
    )


@router.post("/continue", response_model=ConversationResponse, summary="继续对话")
async def continue_conversation(
    request: ConversationContinueRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    继续多轮对话，回答追问问题
    
    根据用户回答更新信息，继续追问或完成收集
    """
    session_id = request.session_id
    
    # 检查会话是否存在
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")
    
    session = conversation_sessions[session_id]
    
    # 添加用户回答到历史
    session["history"].append({
        "role": "user",
        "content": request.answer,
        "timestamp": datetime.utcnow().isoformat(),
    })
    
    # 解析用户回答，提取信息
    new_info = _extract_info_from_answer(request.answer, session["missing_fields"])
    
    # 更新已解析信息
    for field, value in new_info.items():
        if value is not None:
            session["parsed_info"][field] = value
            if field in session["missing_fields"]:
                session["missing_fields"].remove(field)
    
    # 重新识别缺失字段（可能有新发现的依赖字段）
    remaining_missing = _identify_missing_fields(session["parsed_info"])
    # 合并剩余缺失字段
    for field in remaining_missing:
        if field not in session["missing_fields"]:
            session["missing_fields"].append(field)
    
    # 生成新的追问问题
    follow_up_questions = _generate_follow_up_questions(
        session["missing_fields"], 
        session["parsed_info"]
    )
    
    # 计算进度
    total_fields = 8
    filled_fields = total_fields - len(session["missing_fields"])
    progress = int((filled_fields / total_fields) * 100)
    
    # 更新状态
    status = "complete" if not session["missing_fields"] else "collecting"
    session["status"] = status
    session["last_updated"] = datetime.utcnow().isoformat()
    
    # 如果完成且有关联项目，更新项目信息
    if status == "complete" and session.get("project_id"):
                await _update_project_with_complete_info(session["project_id"], session["parsed_info"], db)
    
    return ConversationResponse(
        session_id=session_id,
        status=status,
        parsed_info=session["parsed_info"],
        missing_fields=session["missing_fields"],
        follow_up_questions=follow_up_questions,
        progress_percent=progress,
        message="信息收集完成！" if status == "complete" else f"已记录，还需要补充{len(session['missing_fields'])}项信息",
    )


@router.get("/{session_id}/status", response_model=ConversationStatusResponse, summary="获取会话状态")
async def get_conversation_status(session_id: str):
    """获取对话会话的当前状态"""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")
    
    session = conversation_sessions[session_id]
    
    return ConversationStatusResponse(
        session_id=session_id,
        status=session["status"],
        created_at=session["created_at"],
        last_updated=session["last_updated"],
        message_count=len(session["history"]),
        current_info=session["parsed_info"],
    )


@router.post("/{session_id}/complete", summary="完成对话并保存到项目")
async def complete_conversation(
    session_id: str,
    project_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    手动完成对话，将收集的信息保存到项目
    
    即使还有缺失字段，也可以手动完成
    """
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")
    
    session = conversation_sessions[session_id]
    target_project_id = project_id or session.get("project_id")
    
    if not target_project_id:
        raise HTTPException(status_code=400, detail="未指定项目ID")
    
    # 更新项目信息
    await _update_project_with_complete_info(target_project_id, session["parsed_info"], db)
    
    # 标记会话完成
    session["status"] = "completed"
    session["last_updated"] = datetime.utcnow().isoformat()
    
    return {
        "message": "对话已完成，信息已保存到项目",
        "session_id": session_id,
        "project_id": target_project_id,
        "final_info": session["parsed_info"],
        "remaining_missing": session["missing_fields"],
    }


# ============ 辅助函数 ============

def _identify_missing_fields(parsed_info: Dict[str, Any]) -> List[str]:
    """识别缺失的关键字段"""
    required_fields = [
        ("company_name", "公司名称"),
        ("industry", "行业"),
        ("employee_count", "员工人数"),
        ("address", "地址"),
        ("contact_person", "联系人"),
        ("contact_phone", "联系电话"),
        ("target_standards", "目标认证标准"),
    ]
    
    missing = []
    for field, _ in required_fields:
        value = parsed_info.get(field)
        if not value or (isinstance(value, list) and len(value) == 0):
            missing.append(field)
    
    return missing


def _generate_follow_up_questions(
    missing_fields: List[str],
    parsed_info: Dict[str, Any]
) -> List[FollowUpQuestion]:
    """生成追问问题列表"""
    
    question_templates = {
        "company_name": {
            "question": "请问您的公司名称是什么？",
            "example": "例如：武汉智质科技有限公司",
            "reason": "用于生成体系文件中的公司信息",
        },
        "industry": {
            "question": "请问企业属于哪个行业？",
            "example": "例如：软件开发、物业服务、制造业等",
            "reason": "用于匹配行业特定的模板",
        },
        "employee_count": {
            "question": "请问企业有多少员工？",
            "example": "例如：50人",
            "reason": "用于确定体系文件的适用范围",
        },
        "address": {
            "question": "请问公司的注册地址或办公地址是？",
            "example": "例如：武汉市江汉区XX路XX号",
            "reason": "用于体系文件中的地址信息",
        },
        "contact_person": {
            "question": "请问联系人姓名是？",
            "example": "例如：张三",
            "reason": "用于体系文件中的联系信息",
        },
        "contact_phone": {
            "question": "请问联系电话是？",
            "example": "例如：13800138000",
            "reason": "用于体系文件中的联系信息",
        },
        "target_standards": {
            "question": "请问需要办理哪些认证？",
            "example": "例如：ISO9001质量管理体系、ISO14001环境管理体系、ISO45001职业健康安全管理体系",
            "reason": "用于确定需要生成的体系文件类型",
        },
        "legal_representative": {
            "question": "请问法定代表人是？",
            "example": "例如：李四",
            "reason": "用于体系文件中的签字页",
        },
        "main_business": {
            "question": "请问企业的主营业务是什么？",
            "example": "例如：软件开发与销售、物业管理服务",
            "reason": "用于确定体系文件的适用产品和服务范围",
        },
    }
    
    questions = []
    for field in missing_fields:
        if field in question_templates:
            template = question_templates[field]
            questions.append(FollowUpQuestion(
                field=field,
                question=template["question"],
                example=template.get("example"),
                reason=template.get("reason"),
            ))
    
    return questions


def _extract_info_from_answer(answer: str, expected_fields: List[str]) -> Dict[str, Any]:
    """从用户回答中提取信息"""
    extracted = {}
    
    # 员工人数
    if "employee_count" in expected_fields:
        import re
        match = re.search(r'(\d+)\s*人', answer)
        if match:
            extracted["employee_count"] = int(match.group(1))
    
    # 电话号码
    if "contact_phone" in expected_fields:
        import re
        match = re.search(r'(\d{11}|\d{3,4}-\d{7,8})', answer)
        if match:
            extracted["contact_phone"] = match.group(1)
    
    # 行业（简单匹配）
    if "industry" in expected_fields:
        for keyword, code in INDUSTRY_CODE_MAP.items():
            if keyword in answer:
                extracted["industry"] = keyword
                extracted["industry_code"] = code
                break
    
    # 目标标准
    if "target_standards" in expected_fields:
        standards = []
        if "9001" in answer or "质量" in answer:
            standards.append("ISO9001")
        if "14001" in answer or "环境" in answer:
            standards.append("ISO14001")
        if "45001" in answer or "安全" in answer or "职业健康" in answer:
            standards.append("ISO45001")
        if standards:
            extracted["target_standards"] = standards
    
    # 其他字段直接使用回答内容
    for field in ["company_name", "address", "contact_person", "legal_representative", "main_business"]:
        if field in expected_fields and field not in extracted:
            # 如果回答不太长，直接使用
            if len(answer) < 100:
                extracted[field] = answer.strip()
    
    return extracted


async def _save_to_project_raw_input(
    project_id: str,
    content: str,
    parsed_info: Dict[str, Any],
    db: AsyncSession
):
    """保存到项目原始输入表"""
    try:
        raw_input = ProjectRawInput(
            project_id=project_id,
            input_type="natural_language",
            content=content,
            parsed_json=parsed_info,
        )
        db.add(raw_input)
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"保存原始输入失败: {e}")


async def _update_project_with_complete_info(
    project_id: str,
    parsed_info: Dict[str, Any],
    db: AsyncSession
):
    """将完整信息更新到项目"""
    try:
        result = await db.execute(select(Project).where(Project.project_id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return
        
        # 更新基本信息
        if parsed_info.get("company_name"):
            project.company_name = parsed_info["company_name"]
        if parsed_info.get("industry"):
            project.industry = parsed_info.get("industry_code") or parsed_info["industry"]
        if parsed_info.get("employee_count"):
            project.employee_count = parsed_info["employee_count"]
        if parsed_info.get("address"):
            project.config = project.config or {}
            project.config["address"] = parsed_info["address"]
        if parsed_info.get("target_standards"):
            project.target_standards = parsed_info["target_standards"]
        
        # 更新联系人信息到config
        if parsed_info.get("contact_person") or parsed_info.get("contact_phone"):
            project.config = project.config or {}
            if parsed_info.get("contact_person"):
                project.config["contact_person"] = parsed_info["contact_person"]
            if parsed_info.get("contact_phone"):
                project.config["contact_phone"] = parsed_info["contact_phone"]
            if parsed_info.get("legal_representative"):
                project.config["legal_representative"] = parsed_info["legal_representative"]
        
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"更新项目信息失败: {e}")
