#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 旧版文件上传和提取API
支持上传旧版体系文件，提取方针、目标、部门、文件编号等信息，并进行文件分类。
"""

import os
import json
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from pydantic import BaseModel, Field

from app.core.file_extractor import FileExtractor
from app.core.file_classifier import FileClassifier


router = APIRouter(prefix="/old-files", tags=["旧版文件管理"])

# 上传存储根目录
OLD_FILES_DIR = Path(__file__).parent.parent.parent.parent / "uploads" / "old_files"
OLD_FILES_DIR.mkdir(parents=True, exist_ok=True)

# 提取结果内存存储（生产环境应使用数据库）
_extraction_store: Dict[str, Dict[str, Any]] = {}


# ==================== 数据模型 ====================

class UploadResponse(BaseModel):
    """上传响应"""
    project_id: str
    files: List[Dict[str, Any]]
    total_count: int


class ExtractRequest(BaseModel):
    """提取请求"""
    project_id: str = Field(..., description="项目ID")
    file_paths: Optional[List[str]] = Field(None, description="指定要提取的文件路径（不传则提取全部）")


class ClassifyRequest(BaseModel):
    """分类请求"""
    project_id: str = Field(..., description="项目ID")


class ClassifyResponse(BaseModel):
    """分类响应"""
    project_id: str
    classifications: List[Dict[str, Any]]
    summary: Dict[str, int]


class ExtractionResultResponse(BaseModel):
    """提取结果响应"""
    project_id: str
    status: str
    result: Optional[Dict[str, Any]] = None


# ==================== API 接口 ====================

@router.post("/upload", summary="上传旧版体系文件")
async def upload_old_files(
    project_id: str = Query(..., description="项目ID"),
    files: List[UploadFile] = File(..., description="旧版体系文件列表"),
) -> UploadResponse:
    """
    上传旧版体系文件到指定项目。

    支持的文件类型：.docx, .pdf, .xlsx, .xls, .txt
    文件将保存到 uploads/old_files/{project_id}/ 目录下。
    """
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id 不能为空")

    allowed_extensions = {".docx", ".pdf", ".xlsx", ".xls", ".txt"}
    project_dir = OLD_FILES_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files: List[Dict[str, Any]] = []

    for file in files:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_ext}（{file.filename}），支持: {', '.join(allowed_extensions)}"
            )

        # 生成唯一文件名，避免重名冲突
        unique_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
        file_path = project_dir / unique_name

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        uploaded_files.append({
            "original_name": file.filename,
            "saved_name": unique_name,
            "file_path": str(file_path),
            "file_size": len(content),
            "file_type": file_ext.lstrip("."),
        })

    return UploadResponse(
        project_id=project_id,
        files=uploaded_files,
        total_count=len(uploaded_files),
    )


@router.post("/extract", summary="提取旧版文件中的信息")
async def extract_old_files(request: ExtractRequest) -> Dict[str, Any]:
    """
    从旧版体系文件中提取关键信息。

    提取内容包括：
    - 方针信息（质量方针、环境方针、安全方针）
    - 目标信息（质量目标）
    - 部门信息
    - 文件编号
    - 版本号
    - 发布日期
    - 批准人/编制人
    - 营业执照信息（如有）
    - 租赁合同信息（如有）
    """
    project_dir = OLD_FILES_DIR / request.project_id
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail=f"项目目录不存在: {request.project_id}")

    # 收集要处理的文件
    all_files = _list_project_files(project_dir)
    if not all_files:
        raise HTTPException(status_code=404, detail="该项目下没有上传的文件")

    # 如果指定了文件路径，则只处理指定的文件
    target_files = all_files
    if request.file_paths:
        target_files = [f for f in all_files if str(f) in request.file_paths]

    extractor = FileExtractor()
    classifier = FileClassifier()

    # 提取结果
    result: Dict[str, Any] = {
        "project_id": request.project_id,
        "total_files": len(target_files),
        "processed_files": 0,
        "policies": {},          # 方针
        "goals": {},             # 目标
        "departments": [],       # 部门
        "document_numbers": [],  # 文件编号
        "versions": [],          # 版本号
        "release_dates": [],     # 发布日期
        "approvers": [],         # 批准人
        "authors": [],           # 编制人
        "business_license": None,  # 营业执照信息
        "lease_contract": None,    # 租赁合同信息
        "file_list": [],         # 文件清单及分类
        "errors": [],            # 错误信息
    }

    # 提取所有方针
    file_paths = [str(f) for f in target_files]
    result["policies"] = extractor.extract_all_policies(file_paths)

    # 逐文件提取
    for file_path in target_files:
        try:
            file_name = file_path.name
            doc = extractor.parse_document(str(file_path))

            # 文件分类
            classification = classifier.classify_file(file_name, doc.content)
            result["file_list"].append({
                "file_name": file_name,
                "file_type": classification.file_type,
                "file_level": classification.file_level.value,
                "confidence": classification.confidence,
            })

            # 提取质量目标
            if classification.file_level.value == "一级文件" or "手册" in file_name:
                manual_info = extractor.parse_quality_manual(str(file_path))
                if manual_info.get("quality_goals"):
                    result["goals"][file_name] = manual_info["quality_goals"]
                if manual_info.get("manual_number"):
                    result["document_numbers"].append({
                        "source": file_name,
                        "number": manual_info["manual_number"],
                    })
                if manual_info.get("version"):
                    result["versions"].append({
                        "source": file_name,
                        "version": manual_info["version"],
                    })
                if manual_info.get("release_date"):
                    result["release_dates"].append({
                        "source": file_name,
                        "date": manual_info["release_date"],
                    })
                if manual_info.get("approver"):
                    result["approvers"].append({
                        "source": file_name,
                        "approver": manual_info["approver"],
                    })
                if manual_info.get("author"):
                    result["authors"].append({
                        "source": file_name,
                        "author": manual_info["author"],
                    })

            # 提取文件编号（从所有文件中）
            import re
            number_patterns = [
                r"文件编号[：:]\s*([A-Z0-9\-/]+)",
                r"编号[：:]\s*([A-Z0-9\-/]+)",
                r"([A-Z]{2,4}[-/]\d{4}[-/]\d{2})",  # 如 QP-2024-01
            ]
            for pattern in number_patterns:
                match = re.search(pattern, doc.content)
                if match:
                    result["document_numbers"].append({
                        "source": file_name,
                        "number": match.group(1),
                    })
                    break

            # 提取版本号
            version_patterns = [
                r"版本[：:]\s*([Vv]?\d+\.?\d*)",
                r"版次[：:]\s*([A-Z]?\d+)",
            ]
            for pattern in version_patterns:
                match = re.search(pattern, doc.content)
                if match:
                    result["versions"].append({
                        "source": file_name,
                        "version": match.group(1),
                    })
                    break

            # 提取部门信息
            dept_patterns = [
                r"(?:部门|科室|中心|车间)[：:]\s*(.+?)(?:\n|$)",
                r"(\w+(?:部|处|科|室|中心|车间|组|办))",
            ]
            for pattern in dept_patterns:
                matches = re.findall(pattern, doc.content)
                for m in matches:
                    dept = m.strip()
                    if dept and len(dept) <= 20 and dept not in result["departments"]:
                        result["departments"].append(dept)

            # 营业执照识别
            if any(kw in file_name for kw in ["营业执照", "执照"]):
                license_info = extractor.parse_business_license(str(file_path))
                result["business_license"] = license_info

            # 租赁合同识别
            if any(kw in file_name for kw in ["租赁", "租房", "合同"]):
                lease_info = extractor.parse_lease_contract(str(file_path))
                result["lease_contract"] = lease_info

            result["processed_files"] += 1

        except Exception as e:
            result["errors"].append({
                "file_name": file_path.name,
                "error": str(e),
            })

    # 存储提取结果
    _extraction_store[request.project_id] = result

    return result


@router.get(
    "/extraction-result/{project_id}",
    summary="获取提取结果",
)
async def get_extraction_result(project_id: str) -> ExtractionResultResponse:
    """
    获取指定项目的旧版文件提取结果。

    需要先调用 POST /old-files/extract 进行提取。
    """
    result = _extraction_store.get(project_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"未找到项目 {project_id} 的提取结果，请先调用 /old-files/extract",
        )

    return ExtractionResultResponse(
        project_id=project_id,
        status="completed",
        result=result,
    )


@router.post("/classify", summary="分类上传的文件")
async def classify_files(request: ClassifyRequest) -> ClassifyResponse:
    """
    对项目下所有旧版文件进行分类。

    分类规则：
    - 一级文件：管理手册、质量手册、环境手册、安全手册
    - 二级文件：程序文件
    - 三级文件：管理制度、作业指导书、操作规程
    - 四级文件：记录表格、表单
    - 其他：营业执照、申请书、审核计划、合同等
    """
    project_dir = OLD_FILES_DIR / request.project_id
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail=f"项目目录不存在: {request.project_id}")

    all_files = _list_project_files(project_dir)
    if not all_files:
        raise HTTPException(status_code=404, detail="该项目下没有上传的文件")

    classifier = FileClassifier()
    extractor = FileExtractor()

    classifications: List[Dict[str, Any]] = []
    summary: Dict[str, int] = {}

    for file_path in all_files:
        file_name = file_path.name
        content = ""

        # 尝试读取文件内容以辅助分类
        try:
            doc = extractor.parse_document(str(file_path))
            content = doc.content[:2000]  # 只取前2000字符用于分类，节省性能
        except Exception:
            pass

        classification = classifier.classify_file(file_name, content)

        classifications.append({
            "file_name": file_name,
            "file_level": classification.file_level.value,
            "file_type": classification.file_type,
            "sub_type": classification.sub_type,
            "confidence": classification.confidence,
            "matched_keywords": classification.matched_keywords,
        })

        # 统计
        level = classification.file_level.value
        summary[level] = summary.get(level, 0) + 1

    return ClassifyResponse(
        project_id=request.project_id,
        classifications=classifications,
        summary=summary,
    )


# ==================== 内部工具函数 ====================

def _list_project_files(project_dir: Path) -> List[Path]:
    """列出项目目录下所有支持的文件"""
    allowed_extensions = {".docx", ".pdf", ".xlsx", ".xls", ".txt"}
    files: List[Path] = []

    if not project_dir.exists():
        return files

    for f in project_dir.iterdir():
        if f.is_file() and f.suffix.lower() in allowed_extensions:
            files.append(f)

    return sorted(files)
