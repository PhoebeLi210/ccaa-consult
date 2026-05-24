#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 个人自定义模板API (V1.3)
支持用户上传、管理、使用个人模�?"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
import os
import yaml

from app.core.config import settings
from app.core.database import get_db
from app.models.models import CustomTemplate
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/custom-templates", tags=["个人模板"])


# ============ 请求/响应模型 ============

class TemplateCreateRequest(BaseModel):
    """创建模板请求"""
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    category: str = Field(..., description="模板分类")
    document_level: int = Field(..., ge=1, le=4, description="文档级别 1-4")
    standard: str = Field(..., description="适用标准 ISO9001/14001/45001")
    variables: List[str] = Field(default_factory=list, description="模板变量列表")


class TemplateUpdateRequest(BaseModel):
    """更新模板请求"""
    name: Optional[str] = Field(None, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    category: Optional[str] = Field(None, description="模板分类")
    is_active: Optional[bool] = Field(None, description="是否启用")


class TemplateResponse(BaseModel):
    """模板响应"""
    template_id: str
    name: str
    description: Optional[str]
    category: str
    document_level: int
    standard: str
    version: str
    variables: List[str]
    is_active: bool
    use_count: int
    created_at: str
    updated_at: str


class TemplateListResponse(BaseModel):
    """模板列表响应"""
    total: int
    templates: List[TemplateResponse]


class TemplateVersionInfo(BaseModel):
    """模板版本信息"""
    version: str
    created_at: str
    change_log: Optional[str]


# ============ API路由 ============

@router.post("/upload", response_model=TemplateResponse, summary="上传自定义模�?)
async def upload_custom_template(
    name: str = Form(..., description="模板名称"),
    description: Optional[str] = Form(None, description="模板描述"),
    category: str = Form(..., description="模板分类"),
    document_level: int = Form(..., ge=1, le=4, description="文档级别"),
    standard: str = Form(..., description="适用标准"),
    file: UploadFile = File(..., description="模板YAML文件"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    上传个人自定义模�?    
    支持上传YAML格式的模板文件，系统会自动：
    1. 验证YAML格式正确�?    2. 提取模板变量
    3. 创建模板版本记录
    """
    # 验证文件类型
    if not file.filename.endswith('.yaml'):
        raise HTTPException(status_code=400, detail="只支持YAML格式文件")
    
    # 读取并验证YAML内容
    content = await file.read()
    try:
        template_data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"YAML格式错误: {str(e)}")
    
    # 提取变量
    variables = _extract_variables(template_data)
    
    # 生成模板ID
    template_id = str(uuid.uuid4())
    
    # 保存文件
    upload_dir = os.path.join(
        settings.UPLOAD_DIR, 
        'custom_templates', 
        str(current_user["id"])
    )
    os.makedirs(upload_dir, exist_ok=True)
    
    file_name = f"{template_id}.yaml"
    file_path = os.path.join(upload_dir, file_name)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 创建数据库记�?    template = CustomTemplate(
        template_id=template_id,
        user_id=current_user["id"],
        name=name,
        description=description,
        category=category,
        document_level=document_level,
        standard=standard,
        file_path=file_path,
        version="1.0",
        variables=variables,
        is_active=True,
        use_count=0,
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return _template_to_response(template)


@router.get("/my", response_model=TemplateListResponse, summary="获取我的模板列表")
async def get_my_templates(
    category: Optional[str] = None,
    standard: Optional[str] = None,
    document_level: Optional[int] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的自定义模板列表"""
    query = db.query(CustomTemplate).filter(
        CustomTemplate.user_id == current_user["id"]
    )
    
    # 应用筛选条�?    if category:
        query = query.filter(CustomTemplate.category == category)
    if standard:
        query = query.filter(CustomTemplate.standard == standard)
    if document_level:
        query = query.filter(CustomTemplate.document_level == document_level)
    if is_active is not None:
        query = query.filter(CustomTemplate.is_active == is_active)
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    templates = query.order_by(desc(CustomTemplate.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return TemplateListResponse(
        total=total,
        templates=[_template_to_response(t) for t in templates],
    )


@router.get("/{template_id}", response_model=TemplateResponse, summary="获取模板详情")
async def get_template_detail(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取单个模板的详细信�?""
    template = db.query(CustomTemplate).filter(
        CustomTemplate.template_id == template_id,
        CustomTemplate.user_id == current_user["id"],
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存�?)
    
    return _template_to_response(template)


@router.get("/{template_id}/content", summary="获取模板内容")
async def get_template_content(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取模板的YAML内容"""
    template = db.query(CustomTemplate).filter(
        CustomTemplate.template_id == template_id,
        CustomTemplate.user_id == current_user["id"],
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存�?)
    
    # 读取文件内容
    try:
        with open(template.file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取模板失败: {str(e)}")


@router.patch("/{template_id}", response_model=TemplateResponse, summary="更新模板信息")
async def update_template(
    template_id: str,
    request: TemplateUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新模板的基本信息（不更新文件内容）"""
    template = db.query(CustomTemplate).filter(
        CustomTemplate.template_id == template_id,
        CustomTemplate.user_id == current_user["id"],
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存�?)
    
    # 更新字段
    if request.name is not None:
        template.name = request.name
    if request.description is not None:
        template.description = request.description
    if request.category is not None:
        template.category = request.category
    if request.is_active is not None:
        template.is_active = request.is_active
    
    template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(template)
    
    return _template_to_response(template)


@router.post("/{template_id}/update-content", response_model=TemplateResponse, summary="更新模板内容")
async def update_template_content(
    template_id: str,
    change_log: Optional[str] = Form(None, description="变更说明"),
    file: UploadFile = File(..., description="新的模板YAML文件"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新模板文件内容，自动创建新版本
    
    版本号自动递增�?.0 -> 1.1 -> 1.2 ...
    """
    template = db.query(CustomTemplate).filter(
        CustomTemplate.template_id == template_id,
        CustomTemplate.user_id == current_user["id"],
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存�?)
    
    # 验证文件类型
    if not file.filename.endswith('.yaml'):
        raise HTTPException(status_code=400, detail="只支持YAML格式文件")
    
    # 读取并验证YAML内容
    content = await file.read()
    try:
        template_data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"YAML格式错误: {str(e)}")
    
    # 提取变量
    variables = _extract_variables(template_data)
    
    # 版本号递增
    current_version = template.version
    try:
        major, minor = map(int, current_version.split('.'))
        new_version = f"{major}.{minor + 1}"
    except:
        new_version = "1.1"
    
    # 备份旧版�?    backup_dir = os.path.join(
        settings.UPLOAD_DIR,
        'custom_templates',
        str(current_user["id"]),
        'versions'
    )
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_name = f"{template_id}_v{current_version}.yaml"
    backup_path = os.path.join(backup_dir, backup_name)
    
    if os.path.exists(template.file_path):
        import shutil
        shutil.copy2(template.file_path, backup_path)
    
    # 保存新版�?    with open(template.file_path, "wb") as f:
        f.write(content)
    
    # 更新数据�?    template.version = new_version
    template.variables = variables
    template.change_log = change_log
    template.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(template)
    
    return _template_to_response(template)


@router.get("/{template_id}/versions", response_model=List[TemplateVersionInfo], summary="获取模板版本历史")
async def get_template_versions(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取模板的所有版本历�?""
    template = db.query(CustomTemplate).filter(
        CustomTemplate.template_id == template_id,
        CustomTemplate.user_id == current_user["id"],
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存�?)
    
    # 获取版本历史（从备份目录�?    versions = []
    backup_dir = os.path.join(
        settings.UPLOAD_DIR,
        'custom_templates',
        str(current_user["id"]),
        'versions'
    )
    
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.startswith(f"{template_id}_v"):
                version = filename.replace(f"{template_id}_v", "").replace(".yaml", "")
                filepath = os.path.join(backup_dir, filename)
                created_at = datetime.fromtimestamp(os.path.getctime(filepath))
                versions.append(TemplateVersionInfo(
                    version=version,
                    created_at=created_at.isoformat(),
                    change_log=None,
                ))
    
    # 添加当前版本
    versions.append(TemplateVersionInfo(
        version=template.version,
        created_at=template.updated_at.isoformat() if template.updated_at else template.created_at.isoformat(),
        change_log=template.change_log,
    ))
    
    # 按版本号排序
    versions.sort(key=lambda x: x.version, reverse=True)
    
    return versions


@router.post("/{template_id}/rollback", response_model=TemplateResponse, summary="回滚到指定版�?)
async def rollback_template(
    template_id: str,
    version: str = Form(..., description="目标版本�?),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """回滚模板到指定版�?""
    template = db.query(CustomTemplate).filter(
        CustomTemplate.template_id == template_id,
        CustomTemplate.user_id == current_user["id"],
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存�?)
    
    # 查找版本文件
    backup_dir = os.path.join(
        settings.UPLOAD_DIR,
        'custom_templates',
        str(current_user["id"]),
        'versions'
    )
    backup_file = os.path.join(backup_dir, f"{template_id}_v{version}.yaml")
    
    if not os.path.exists(backup_file):
        raise HTTPException(status_code=404, detail="指定版本不存�?)
    
    # 备份当前版本
    import shutil
    current_backup = os.path.join(backup_dir, f"{template_id}_v{template.version}.yaml")
    shutil.copy2(template.file_path, current_backup)
    
    # 恢复指定版本
    shutil.copy2(backup_file, template.file_path)
    
    # 更新版本号（使用新版本号�?    try:
        major, minor = map(int, template.version.split('.'))
        new_version = f"{major}.{minor + 1}"
    except:
        new_version = "1.1"
    
    template.version = new_version
    template.change_log = f"回滚到版�?{version}"
    template.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(template)
    
    return _template_to_response(template)


@router.delete("/{template_id}", summary="删除模板")
async def delete_template(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除自定义模�?""
    template = db.query(CustomTemplate).filter(
        CustomTemplate.template_id == template_id,
        CustomTemplate.user_id == current_user["id"],
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存�?)
    
    # 删除文件
    try:
        if os.path.exists(template.file_path):
            os.remove(template.file_path)
        
        # 删除版本备份
        backup_dir = os.path.join(
            settings.UPLOAD_DIR,
            'custom_templates',
            str(current_user["id"]),
            'versions'
        )
        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                if filename.startswith(f"{template_id}_v"):
                    os.remove(os.path.join(backup_dir, filename))
    except Exception as e:
        print(f"删除文件失败: {e}")
    
    # 删除数据库记�?    db.delete(template)
    db.commit()
    
    return {"message": "模板已删�?, "template_id": template_id}


@router.post("/{template_id}/use", summary="记录模板使用")
async def record_template_use(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """记录模板被使用一次（增加使用计数�?""
    template = db.query(CustomTemplate).filter(
        CustomTemplate.template_id == template_id,
        CustomTemplate.user_id == current_user["id"],
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存�?)
    
    template.use_count += 1
    db.commit()
    
    return {"message": "使用记录已更�?, "use_count": template.use_count}


@router.get("/categories/list", summary="获取模板分类列表")
async def get_template_categories(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户所有模板的分类列表"""
    categories = db.query(CustomTemplate.category).filter(
        CustomTemplate.user_id == current_user["id"],
        CustomTemplate.is_active == True,
    ).distinct().all()
    
    return [c[0] for c in categories if c[0]]


# ============ 辅助函数 ============

def _extract_variables(template_data: Dict[str, Any]) -> List[str]:
    """从模板数据中提取变量"""
    variables = []
    
    def find_variables(obj):
        if isinstance(obj, str):
            # 查找 {{variable}} 格式的变�?            import re
            matches = re.findall(r'\{\{(\w+)\}\}', obj)
            variables.extend(matches)
        elif isinstance(obj, dict):
            for value in obj.values():
                find_variables(value)
        elif isinstance(obj, list):
            for item in obj:
                find_variables(item)
    
    find_variables(template_data)
    return list(set(variables))  # 去重


def _template_to_response(template: CustomTemplate) -> TemplateResponse:
    """将数据库模型转换为响应模�?""
    return TemplateResponse(
        template_id=template.template_id,
        name=template.name,
        description=template.description,
        category=template.category,
        document_level=template.document_level,
        standard=template.standard,
        version=template.version,
        variables=template.variables or [],
        is_active=template.is_active,
        use_count=template.use_count,
        created_at=template.created_at.isoformat() if template.created_at else "",
        updated_at=template.updated_at.isoformat() if template.updated_at else "",
    )
