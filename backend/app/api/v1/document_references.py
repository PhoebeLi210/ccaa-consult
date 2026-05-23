#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档引用关系API

管理四级文件体系的文档引用关系
支持：文档注册、层级查询、引用链生成、引用验证
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.core.document_hierarchy import (
    DocumentReferenceManager, DocumentLevel, DocumentLevelConfig,
    DocumentInfo, ReferenceInfo, create_document_manager
)

router = APIRouter(prefix="/document-references", tags=["文档引用关系"])


# 缓存管理器实例
_manager_cache: Dict[str, DocumentReferenceManager] = {}


def get_manager(project_id: str) -> DocumentReferenceManager:
    """获取或创建文档引用管理器"""
    if project_id not in _manager_cache:
        _manager_cache[project_id] = create_document_manager(project_id)
    return _manager_cache[project_id]


# 请求和响应模型
class RegisterDocumentRequest(BaseModel):
    """注册文档请求"""
    project_id: str
    doc_id: str
    level: int = Field(..., ge=1, le=4, description="文档层级: 1-4")
    name: str
    code: str
    clause_mapping: Optional[Dict[str, str]] = Field(None, description="条款映射关系")
    parent_id: Optional[str] = Field(None, description="上级文档ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class RegisterDocumentResponse(BaseModel):
    """注册文档响应"""
    success: bool
    doc_id: str
    level: int
    level_name: str
    name: str
    code: str
    parent_id: Optional[str] = None
    message: str


class DocumentHierarchyResponse(BaseModel):
    """文档层级结构响应"""
    project_id: str
    levels: Dict[str, Any]
    total_documents: int


class DocumentChainResponse(BaseModel):
    """文档引用链响应"""
    project_id: str
    doc_id: str
    chain: List[Dict[str, Any]]
    chain_length: int


class GenerateReferenceRequest(BaseModel):
    """生成引用文本请求"""
    project_id: str
    doc_id: str
    clause: Optional[str] = None
    standard: Optional[str] = None


class GenerateReferenceResponse(BaseModel):
    """生成引用文本响应"""
    project_id: str
    doc_id: str
    reference_text: str
    level: int


class DocumentsByLevelResponse(BaseModel):
    """按层级获取文档响应"""
    project_id: str
    level: int
    level_name: str
    documents: List[Dict[str, Any]]
    count: int


class ValidateReferenceRequest(BaseModel):
    """验证引用请求"""
    project_id: str
    doc_id: str
    reference_text: str


class ValidateReferenceResponse(BaseModel):
    """验证引用响应"""
    project_id: str
    doc_id: str
    is_valid: bool
    level: int
    message: str


class FullReferencesResponse(BaseModel):
    """完整引用链响应"""
    project_id: str
    doc_id: str
    references: Dict[str, str]


@router.post("/register", response_model=RegisterDocumentResponse)
async def register_document(request: RegisterDocumentRequest):
    """
    注册文档
    
    将文档注册到文档引用管理系统中，建立文档层级关系
    """
    manager = get_manager(request.project_id)
    
    # 转换层级
    level = DocumentLevel(request.level)
    
    # 注册文档
    doc_info = manager.register_document(
        doc_id=request.doc_id,
        level=level,
        name=request.name,
        code=request.code,
        clause_mapping=request.clause_mapping,
        parent_id=request.parent_id,
        metadata=request.metadata
    )
    
    return RegisterDocumentResponse(
        success=True,
        doc_id=doc_info.doc_id,
        level=doc_info.level.value,
        level_name=DocumentLevelConfig.get_name(level),
        name=doc_info.name,
        code=doc_info.code,
        parent_id=doc_info.parent_id,
        message=f"文档 '{request.name}' 注册成功"
    )


@router.get("/{project_id}/hierarchy", response_model=DocumentHierarchyResponse)
async def get_document_hierarchy(project_id: str):
    """
    获取文档层级结构
    
    获取项目的完整文档层级结构，按四级文件体系组织
    """
    manager = get_manager(project_id)
    hierarchy = manager.build_hierarchy()
    
    return DocumentHierarchyResponse(
        project_id=project_id,
        levels=hierarchy.get("levels", {}),
        total_documents=hierarchy.get("total_documents", 0)
    )


@router.get("/{project_id}/chain/{level}", response_model=DocumentChainResponse)
async def get_document_chain(project_id: str, level: int):
    """
    获取引用链
    
    获取指定层级文档的完整引用链（从一级到当前级别）
    
    Args:
        project_id: 项目ID
        level: 文档层级 (1-4)
    """
    if level < 1 or level > 4:
        raise HTTPException(status_code=400, detail="层级必须在1-4之间")
    
    manager = get_manager(project_id)
    
    # 获取该层级的所有文档
    docs = manager.get_documents_by_level(DocumentLevel(level))
    
    if not docs:
        return DocumentChainResponse(
            project_id=project_id,
            doc_id="",
            chain=[],
            chain_length=0
        )
    
    # 获取第一个文档的引用链作为示例
    doc = docs[0]
    chain = manager.get_document_chain(doc.doc_id)
    
    chain_data = []
    for item in chain:
        chain_data.append({
            "doc_id": item.doc_id,
            "level": item.level.value,
            "level_name": DocumentLevelConfig.get_name(item.level),
            "name": item.name,
            "code": item.code
        })
    
    return DocumentChainResponse(
        project_id=project_id,
        doc_id=doc.doc_id,
        chain=chain_data,
        chain_length=len(chain_data)
    )


@router.post("/generate", response_model=GenerateReferenceResponse)
async def generate_reference(request: GenerateReferenceRequest):
    """
    生成引用文本
    
    根据文档层级和条款信息生成标准引用文本
    """
    manager = get_manager(request.project_id)
    
    doc = manager.get_document(request.doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"文档 '{request.doc_id}' 不存在")
    
    reference_text = manager.generate_reference(
        level=doc.level,
        clause=request.clause,
        standard=request.standard,
        doc_id=request.doc_id
    )
    
    return GenerateReferenceResponse(
        project_id=request.project_id,
        doc_id=request.doc_id,
        reference_text=reference_text,
        level=doc.level.value
    )


@router.get("/{project_id}/by-level/{level}", response_model=DocumentsByLevelResponse)
async def get_documents_by_level(project_id: str, level: int):
    """
    按层级获取文档
    
    获取指定层级的所有文档列表
    """
    if level < 1 or level > 4:
        raise HTTPException(status_code=400, detail="层级必须在1-4之间")
    
    manager = get_manager(project_id)
    docs = manager.get_documents_by_level(DocumentLevel(level))
    
    documents = []
    for doc in docs:
        documents.append({
            "doc_id": doc.doc_id,
            "name": doc.name,
            "code": doc.code,
            "parent_id": doc.parent_id,
            "clause_mapping": doc.clause_mapping,
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        })
    
    return DocumentsByLevelResponse(
        project_id=project_id,
        level=level,
        level_name=DocumentLevelConfig.get_name(DocumentLevel(level)),
        documents=documents,
        count=len(documents)
    )


@router.post("/validate", response_model=ValidateReferenceResponse)
async def validate_reference(request: ValidateReferenceRequest):
    """
    验证引用
    
    验证引用文本格式是否正确
    """
    manager = get_manager(request.project_id)
    
    doc = manager.get_document(request.doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"文档 '{request.doc_id}' 不存在")
    
    is_valid = manager.validate_reference(doc.level, request.reference_text)
    
    message = "引用格式正确" if is_valid else "引用格式不正确"
    
    return ValidateReferenceResponse(
        project_id=request.project_id,
        doc_id=request.doc_id,
        is_valid=is_valid,
        level=doc.level.value,
        message=message
    )


@router.get("/{project_id}/full-references/{doc_id}", response_model=FullReferencesResponse)
async def get_full_references(
    project_id: str,
    doc_id: str,
    standard: Optional[str] = None,
    clause: Optional[str] = None
):
    """
    获取完整引用链文本
    
    生成从当前文档到一级文件及标准的完整引用链
    """
    manager = get_manager(project_id)
    
    doc = manager.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"文档 '{doc_id}' 不存在")
    
    references = manager.generate_full_references(
        doc_id=doc_id,
        standard=standard,
        clause=clause
    )
    
    return FullReferencesResponse(
        project_id=project_id,
        doc_id=doc_id,
        references=references
    )
