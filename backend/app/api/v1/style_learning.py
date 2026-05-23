#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风格学习API

提供用户风格画像、风格学习事件记录、风格提示词等功能
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter(prefix="/style-learning", tags=["风格学习"])


# 请求/响应模型

class StyleProfile(BaseModel):
    """用户风格画像"""
    user_id: str
    writing_style: Dict[str, Any]
    preferred_terms: List[str]
    document_structure_preferences: Dict[str, Any]
    tone_preferences: Dict[str, Any]
    created_at: str
    updated_at: str


class StyleEventRequest(BaseModel):
    """风格学习事件请求"""
    user_id: str
    event_type: str = Field(..., description="事件类型: edit, generate, feedback")
    document_type: Optional[str] = None
    context: Dict[str, Any]
    timestamp: Optional[str] = None


class StyleEventResponse(BaseModel):
    """风格学习事件响应"""
    event_id: str
    user_id: str
    event_type: str
    processed: bool
    message: str


class StylePromptResponse(BaseModel):
    """风格提示词响应"""
    user_id: str
    prompt_text: str
    style_elements: Dict[str, Any]
    generated_at: str


class StyleStats(BaseModel):
    """学习统计"""
    user_id: str
    total_events: int
    events_by_type: Dict[str, int]
    top_terms: List[Dict[str, Any]]
    style_evolution: List[Dict[str, Any]]
    last_active: str


# 模拟数据存储
USER_PROFILES = {}
STYLE_EVENTS = []


# API端点

@router.get("/profile/{user_id}", response_model=StyleProfile)
async def get_user_style_profile(user_id: str):
    """获取用户风格画像"""
    if user_id not in USER_PROFILES:
        now = datetime.now().isoformat()
        USER_PROFILES[user_id] = {
            "user_id": user_id,
            "writing_style": {
                "formality": "formal",
                "verbosity": "concise",
                "technical_level": "professional"
            },
            "preferred_terms": [],
            "document_structure_preferences": {
                "prefer_numbered_sections": True,
                "prefer_detailed_appendix": False
            },
            "tone_preferences": {
                "professional": 0.8,
                "friendly": 0.2
            },
            "created_at": now,
            "updated_at": now
        }
    
    profile = USER_PROFILES[user_id]
    return StyleProfile(**profile)


@router.post("/events", response_model=StyleEventResponse)
async def record_style_event(request: StyleEventRequest):
    """记录风格学习事件"""
    import uuid
    
    event_id = str(uuid.uuid4())
    timestamp = request.timestamp or datetime.now().isoformat()
    
    event = {
        "event_id": event_id,
        "user_id": request.user_id,
        "event_type": request.event_type,
        "document_type": request.document_type,
        "context": request.context,
        "timestamp": timestamp
    }
    
    STYLE_EVENTS.append(event)
    
    if request.user_id in USER_PROFILES:
        USER_PROFILES[request.user_id]["updated_at"] = timestamp
        if request.event_type == "edit" and "preferred_terms" in request.context:
            terms = request.context["preferred_terms"]
            existing_terms = USER_PROFILES[request.user_id]["preferred_terms"]
            for term in terms:
                if term not in existing_terms:
                    existing_terms.append(term)
    
    return StyleEventResponse(
        event_id=event_id,
        user_id=request.user_id,
        event_type=request.event_type,
        processed=True,
        message="风格学习事件已记录"
    )


@router.get("/prompt/{user_id}", response_model=StylePromptResponse)
async def get_style_prompt(user_id: str):
    """获取风格提示词"""
    if user_id not in USER_PROFILES:
        await get_user_style_profile(user_id)
    
    profile = USER_PROFILES[user_id]
    
    style_elements = {
        "formality": profile["writing_style"].get("formality", "formal"),
        "verbosity": profile["writing_style"].get("verbosity", "concise"),
        "technical_level": profile["writing_style"].get("technical_level", "professional"),
        "preferred_terms": profile["preferred_terms"][:10] if profile["preferred_terms"] else [],
        "tone": profile["tone_preferences"]
    }
    
    prompt_parts = [
        "【写作风格要求】",
        "- 正式程度: " + style_elements["formality"],
        "- 详细程度: " + style_elements["verbosity"],
        "- 技术层次: " + style_elements["technical_level"],
    ]
    
    if style_elements["preferred_terms"]:
        terms_str = ", ".join(style_elements["preferred_terms"])
        prompt_parts.append("- 偏好术语: " + terms_str)
    
    tone_desc = []
    for tone, weight in style_elements["tone"].items():
        if weight > 0.3:
            pct = str(int(weight * 100)) + "%"
            tone_desc.append(tone + "(" + pct + ")")
    if tone_desc:
        tone_str = ", ".join(tone_desc)
        prompt_parts.append("- 语调偏好: " + tone_str)
    
    prompt_text = chr(10).join(prompt_parts)
    
    return StylePromptResponse(
        user_id=user_id,
        prompt_text=prompt_text,
        style_elements=style_elements,
        generated_at=datetime.now().isoformat()
    )


@router.get("/stats/{user_id}", response_model=StyleStats)
async def get_learning_stats(user_id: str):
    """获取学习统计"""
    user_events = [e for e in STYLE_EVENTS if e["user_id"] == user_id]
    
    events_by_type = {}
    for event in user_events:
        event_type = event["event_type"]
        events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
    
    top_terms = []
    if user_id in USER_PROFILES:
        for i, term in enumerate(USER_PROFILES[user_id]["preferred_terms"][:5]):
            top_terms.append({"term": term, "rank": i + 1})
    
    style_evolution = [
        {"date": "2024-01-01", "formality_score": 0.7, "technical_score": 0.6},
        {"date": "2024-02-01", "formality_score": 0.75, "technical_score": 0.65},
        {"date": "2024-03-01", "formality_score": 0.8, "technical_score": 0.7}
    ]
    
    last_active = user_events[-1]["timestamp"] if user_events else datetime.now().isoformat()
    
    return StyleStats(
        user_id=user_id,
        total_events=len(user_events),
        events_by_type=events_by_type,
        top_terms=top_terms,
        style_evolution=style_evolution,
        last_active=last_active
    )
