#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 文档生成API接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import yaml
import json
from datetime import datetime
import uuid

router = APIRouter(prefix="/generator", tags=["文档生成"])

TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "templates_wuxing"
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "outputs"


class GenerateRequest(BaseModel):
    """文档生成请求"""
    template_id: str
    company_info: Dict[str, Any]
    additional_vars: Optional[Dict[str, Any]] = None
    output_format: Optional[str] = "json"  # json / markdown / docx


class GenerateBatchRequest(BaseModel):
    """批量生成请求"""
    template_ids: List[str]
    company_info: Dict[str, Any]
    additional_vars: Optional[Dict[str, Any]] = None


class GenerateResponse(BaseModel):
    """生成响应"""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str  # pending / processing / completed / failed
    progress: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# 任务存储（实际应用中应使用数据库）
tasks = {}


def replace_vars(text, variables):
    """替换变量"""
    if isinstance(text, str):
        for key, value in variables.items():
            text = text.replace("{{" + key + "}}", str(value))
        return text
    elif isinstance(text, dict):
        return {k: replace_vars(v, variables) for k, v in text.items()}
    elif isinstance(text, list):
        return [replace_vars(item, variables) for item in text]
    return text


def generate_document(template_id: str, company_info: Dict, additional_vars: Dict = None):
    """生成文档"""
    # 查找模板
    template_file = None
    for level_dir in TEMPLATE_DIR.iterdir():
        if not level_dir.is_dir():
            continue
        candidate = level_dir / f"{template_id}.yaml"
        if candidate.exists():
            template_file = candidate
            break
    
    if not template_file:
        return None, f"模板不存在: {template_id}"
    
    try:
        with open(template_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        doc_info = data.get("document_info", {})
        content = data.get("content", data.get("form_structure", {}))
        
        # 合并变量
        all_vars = {**company_info}
        if additional_vars:
            all_vars.update(additional_vars)
        
        # 渲染内容
        rendered_content = replace_vars(content, all_vars)
        
        return {
            "template_id": template_id,
            "document_name": doc_info.get("document_name", ""),
            "document_code": doc_info.get("document_code", ""),
            "document_type": doc_info.get("document_type", ""),
            "version": doc_info.get("version", "A/0"),
            "content": rendered_content,
            "generated_at": datetime.now().isoformat(),
        }, None
    except Exception as e:
        return None, str(e)


@router.post("/generate", response_model=GenerateResponse, summary="生成单个文档")
async def generate_single(request: GenerateRequest):
    """生成单个文档"""
    task_id = str(uuid.uuid4())
    
    result, error = generate_document(
        request.template_id,
        request.company_info,
        request.additional_vars
    )
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    # 保存结果
    tasks[task_id] = {
        "status": "completed",
        "progress": 100,
        "result": result,
    }
    
    return GenerateResponse(
        task_id=task_id,
        status="completed",
        message="文档生成成功",
    )


@router.post("/generate/batch", response_model=GenerateResponse, summary="批量生成文档")
async def generate_batch(request: GenerateBatchRequest):
    """批量生成文档"""
    task_id = str(uuid.uuid4())
    
    tasks[task_id] = {
        "status": "processing",
        "progress": 0,
        "total": len(request.template_ids),
        "completed": 0,
        "results": [],
    }
    
    results = []
    for i, template_id in enumerate(request.template_ids):
        result, error = generate_document(
            template_id,
            request.company_info,
            request.additional_vars
        )
        
        if result:
            results.append(result)
        
        tasks[task_id]["progress"] = int((i + 1) / len(request.template_ids) * 100)
        tasks[task_id]["completed"] = i + 1
    
    tasks[task_id]["status"] = "completed"
    tasks[task_id]["results"] = results
    
    return GenerateResponse(
        task_id=task_id,
        status="completed",
        message=f"成功生成 {len(results)} 个文档",
    )


@router.get("/task/{task_id}", response_model=TaskStatusResponse, summary="查询任务状态")
async def get_task_status(task_id: str):
    """查询任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        result=task.get("result"),
        error=task.get("error"),
    )


@router.post("/generate/all", summary="生成全套体系文件")
async def generate_all_documents(request: GenerateBatchRequest):
    """根据企业信息生成全套体系文件"""
    task_id = str(uuid.uuid4())
    
    # 获取所有模板
    all_templates = []
    if TEMPLATE_DIR.exists():
        for level_dir in TEMPLATE_DIR.iterdir():
            if not level_dir.is_dir():
                continue
            for template_file in level_dir.glob("*.yaml"):
                all_templates.append(template_file.stem)
    
    # 如果指定了模板列表，使用指定的
    template_ids = request.template_ids if request.template_ids else all_templates
    
    results = {
        "一级文件": [],
        "二级文件": [],
        "三级文件": [],
        "四级文件": [],
    }
    
    for template_id in template_ids:
        result, error = generate_document(
            template_id,
            request.company_info,
            request.additional_vars
        )
        
        if result:
            level = result.get("document_type", "四级文件")
            if level in results:
                results[level].append(result)
    
    return {
        "task_id": task_id,
        "status": "completed",
        "summary": {
            "total": sum(len(v) for v in results.values()),
            "by_level": {k: len(v) for k, v in results.items()},
        },
        "results": results,
    }
