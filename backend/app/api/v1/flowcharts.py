"""
流程图管理API模块
提供流程图的CRUD操作、模板管理和作业指导书生成功能
"""

from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, Field

from app.models.flowchart_models import Flowchart, FlowchartTemplate, FlowchartNodeConfig
from app.core.database import get_db


# ==================== Pydantic请求/响应模型 ====================

class FlowchartNodeConfigSchema(BaseModel):
    """流程图节点配置模式"""
    node_id: str = Field(..., description="节点唯一标识")
    node_type: str = Field(..., description="节点类型")
    label: str = Field(..., description="节点标签")
    position_x: float = Field(..., description="X坐标位置")
    position_y: float = Field(..., description="Y坐标位置")
    width: Optional[float] = Field(default=None, description="节点宽度")
    height: Optional[float] = Field(default=None, description="节点高度")
    style: Optional[dict] = Field(default=None, description="节点样式配置")
    data: Optional[dict] = Field(default=None, description="节点数据")

    class Config:
        from_attributes = True


class FlowchartEdgeConfigSchema(BaseModel):
    """流程图边线配置模式"""
    edge_id: str = Field(..., description="边线唯一标识")
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    label: Optional[str] = Field(default=None, description="边线标签")
    edge_type: Optional[str] = Field(default="default", description="边线类型")
    style: Optional[dict] = Field(default=None, description="边线样式")

    class Config:
        from_attributes = True


class FlowchartCreateRequest(BaseModel):
    """创建流程图请求模式"""
    project_id: UUID = Field(..., description="所属项目ID")
    name: str = Field(..., min_length=1, max_length=200, description="流程图名称")
    description: Optional[str] = Field(default=None, max_length=1000, description="流程图描述")
    nodes: List[FlowchartNodeConfigSchema] = Field(default=[], description="节点列表")
    edges: List[FlowchartEdgeConfigSchema] = Field(default=[], description="边线列表")


class FlowchartUpdateRequest(BaseModel):
    """更新流程图请求模式"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="流程图名称")
    description: Optional[str] = Field(default=None, max_length=1000, description="流程图描述")
    nodes: Optional[List[FlowchartNodeConfigSchema]] = Field(default=None, description="节点列表")
    edges: Optional[List[FlowchartEdgeConfigSchema]] = Field(default=None, description="边线列表")
    status: Optional[str] = Field(default=None, description="流程图状态")


class FlowchartResponse(BaseModel):
    """流程图响应模式"""
    id: UUID
    project_id: UUID
    name: str
    description: Optional[str]
    nodes: List[FlowchartNodeConfigSchema]
    edges: List[FlowchartEdgeConfigSchema]
    status: str
    version: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    class Config:
        from_attributes = True


class FlowchartListItem(BaseModel):
    """流程图列表项模式"""
    id: UUID
    project_id: UUID
    name: str
    description: Optional[str]
    status: str
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FlowchartTemplateResponse(BaseModel):
    """流程图模板响应模式"""
    id: UUID
    name: str
    description: Optional[str]
    category: Optional[str]
    nodes: List[FlowchartNodeConfigSchema]
    edges: List[FlowchartEdgeConfigSchema]
    thumbnail_url: Optional[str]
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ApplyTemplateRequest(BaseModel):
    """应用模板请求模式"""
    project_id: UUID = Field(..., description="目标项目ID")
    name: Optional[str] = Field(default=None, description="流程图名称，默认使用模板名称")
    description: Optional[str] = Field(default=None, description="流程图描述")


class InstructionGenerateResponse(BaseModel):
    """作业指导书生成响应模式"""
    flowchart_id: UUID
    instruction_content: str
    generated_at: datetime
    steps_count: int


class ErrorResponse(BaseModel):
    """错误响应模式"""
    detail: str
    error_code: Optional[str] = None


# ==================== API Router ====================

router = APIRouter(prefix="/flowcharts", tags=["流程图管理"])


# ==================== 流程图CRUD端点 ====================

@router.post(
    "",
    response_model=FlowchartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建流程图",
    description="创建一个新的流程图，可以指定节点和边线配置"
)
def create_flowchart(
    request: FlowchartCreateRequest,
    db: Session = Depends(get_db)
):
    """
    创建新流程图

    - **project_id**: 所属项目ID（必需）
    - **name**: 流程图名称（必需）
    - **description**: 流程图描述（可选）
    - **nodes**: 节点配置列表（可选）
    - **edges**: 边线配置列表（可选）
    """
    # 检查项目名称是否已存在（同一项目内）
    existing = db.query(Flowchart).filter(
        Flowchart.project_id == request.project_id,
        Flowchart.name == request.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"项目下已存在名为 '{request.name}' 的流程图"
        )

    # 创建流程图实例
    flowchart = Flowchart(
        id=uuid4(),
        project_id=request.project_id,
        name=request.name,
        description=request.description,
        nodes=[node.model_dump() for node in request.nodes],
        edges=[edge.model_dump() for edge in request.edges],
        status="draft",
        version=1
    )

    db.add(flowchart)
    db.commit()
    db.refresh(flowchart)

    return flowchart


@router.get(
    "/{flowchart_id}",
    response_model=FlowchartResponse,
    summary="获取流程图详情",
    description="根据ID获取流程图的完整信息"
)
def get_flowchart(
    flowchart_id: UUID,
    db: Session = Depends(get_db)
):
    """
    获取流程图详情

    - **flowchart_id**: 流程图ID（路径参数）
    """
    flowchart = db.query(Flowchart).filter(Flowchart.id == flowchart_id).first()

    if not flowchart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程图 '{flowchart_id}' 不存在"
        )

    return flowchart


@router.put(
    "/{flowchart_id}",
    response_model=FlowchartResponse,
    summary="更新流程图",
    description="更新流程图的基本信息、节点或边线配置"
)
def update_flowchart(
    flowchart_id: UUID,
    request: FlowchartUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    更新流程图

    - **flowchart_id**: 流程图ID（路径参数）
    - **name**: 新名称（可选）
    - **description**: 新描述（可选）
    - **nodes**: 新节点配置（可选）
    - **edges**: 新边线配置（可选）
    - **status**: 新状态（可选）
    """
    flowchart = db.query(Flowchart).filter(Flowchart.id == flowchart_id).first()

    if not flowchart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程图 '{flowchart_id}' 不存在"
        )

    # 检查名称冲突
    if request.name and request.name != flowchart.name:
        existing = db.query(Flowchart).filter(
            Flowchart.project_id == flowchart.project_id,
            Flowchart.name == request.name,
            Flowchart.id != flowchart_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"项目下已存在名为 '{request.name}' 的流程图"
            )

        flowchart.name = request.name

    # 更新其他字段
    if request.description is not None:
        flowchart.description = request.description

    if request.nodes is not None:
        flowchart.nodes = [node.model_dump() for node in request.nodes]

    if request.edges is not None:
        flowchart.edges = [edge.model_dump() for edge in request.edges]

    if request.status is not None:
        valid_statuses = ["draft", "published", "archived"]
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值，必须是以下之一: {', '.join(valid_statuses)}"
            )
        flowchart.status = request.status

    # 版本号递增
    flowchart.version += 1
    flowchart.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(flowchart)

    return flowchart


@router.delete(
    "/{flowchart_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除流程图",
    description="删除指定的流程图"
)
def delete_flowchart(
    flowchart_id: UUID,
    db: Session = Depends(get_db)
):
    """
    删除流程图

    - **flowchart_id**: 流程图ID（路径参数）
    """
    flowchart = db.query(Flowchart).filter(Flowchart.id == flowchart_id).first()

    if not flowchart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程图 '{flowchart_id}' 不存在"
        )

    db.delete(flowchart)
    db.commit()

    return None


@router.get(
    "/project/{project_id}",
    response_model=List[FlowchartListItem],
    summary="获取项目的流程图列表",
    description="获取指定项目下的所有流程图列表"
)
def get_project_flowcharts(
    project_id: UUID,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取项目的流程图列表

    - **project_id**: 项目ID（路径参数）
    - **status**: 按状态筛选（可选，查询参数）
    """
    query = db.query(Flowchart).filter(Flowchart.project_id == project_id)

    if status:
        query = query.filter(Flowchart.status == status)

    flowcharts = query.order_by(Flowchart.updated_at.desc()).all()

    return flowcharts


# ==================== 作业指导书生成功能 ====================

@router.post(
    "/{flowchart_id}/generate-instruction",
    response_model=InstructionGenerateResponse,
    summary="生成作业指导书",
    description="根据流程图内容自动生成作业指导书"
)
def generate_instruction(
    flowchart_id: UUID,
    db: Session = Depends(get_db)
):
    """
    根据流程图生成作业指导书

    - **flowchart_id**: 流程图ID（路径参数）

    系统会分析流程图的节点和连接关系，生成结构化的作业指导书内容
    """
    flowchart = db.query(Flowchart).filter(Flowchart.id == flowchart_id).first()

    if not flowchart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"流程图 '{flowchart_id}' 不存在"
        )

    # 获取节点和边线数据
    nodes = flowchart.nodes or []
    edges = flowchart.edges or []

    if not nodes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="流程图为空，无法生成作业指导书"
        )

    # 构建节点映射
    node_map = {node.get("node_id"): node for node in nodes if node.get("node_id")}

    # 构建连接关系图
    connections = {}
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source:
            if source not in connections:
                connections[source] = []
            connections[source].append(target)

    # 生成作业指导书内容
    instruction_lines = [
        f"# {flowchart.name} - 作业指导书",
        "",
        f"**流程图描述**: {flowchart.description or '无'}",
        f"**版本**: v{flowchart.version}",
        f"**生成时间**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 作业步骤",
        ""
    ]

    # 查找起始节点（没有入边的节点）
    all_targets = set()
    for edge in edges:
        target = edge.get("target")
        if target:
            all_targets.add(target)

    start_nodes = [n for n in nodes if n.get("node_id") not in all_targets]
    if not start_nodes and nodes:
        start_nodes = [nodes[0]]

    # 遍历生成步骤
    visited = set()
    step_number = 1

    def traverse_node(node_id, depth=0):
        nonlocal step_number
        if node_id in visited or node_id not in node_map:
            return

        visited.add(node_id)
        node = node_map[node_id]

        indent = "  " * depth
        node_label = node.get("label", "未命名步骤")
        node_type = node.get("node_type", "default")
        node_data = node.get("data", {}) or {}

        instruction_lines.append(f"{step_number}. {node_label}")

        # 添加详细说明
        if node_data.get("description"):
            instruction_lines.append(f"   - 操作说明: {node_data.get('description')}")

        if node_data.get("responsible"):
            instruction_lines.append(f"   - 负责人: {node_data.get('responsible')}")

        if node_data.get("duration"):
            instruction_lines.append(f"   - 预计时长: {node_data.get('duration')}")

        if node_type == "decision":
            instruction_lines.append(f"   - 类型: 决策节点")

        instruction_lines.append("")
        step_number += 1

        # 递归处理后续节点
        for next_node_id in connections.get(node_id, []):
            traverse_node(next_node_id, depth + 1)

    # 从起始节点开始遍历
    for start_node in start_nodes:
        traverse_node(start_node.get("node_id"))

    # 添加注意事项
    instruction_lines.extend([
        "## 注意事项",
        "",
        "1. 请严格按照步骤顺序执行",
        "2. 每个步骤完成后需确认无误再进行下一步",
        "3. 如遇异常情况，请及时上报处理",
        "",
        "---",
        "*本指导书由系统自动生成，如有疑问请联系流程管理员*"
    ])

    instruction_content = "\n".join(instruction_lines)

    return InstructionGenerateResponse(
        flowchart_id=flowchart_id,
        instruction_content=instruction_content,
        generated_at=datetime.utcnow(),
        steps_count=step_number - 1
    )


# ==================== 模板管理端点 ====================

@router.get(
    "/templates/list",
    response_model=List[FlowchartTemplateResponse],
    summary="获取流程图模板列表",
    description="获取所有可用的流程图模板"
)
def get_flowchart_templates(
    category: Optional[str] = None,
    include_system: bool = True,
    db: Session = Depends(get_db)
):
    """
    获取流程图模板列表

    - **category**: 按分类筛选（可选，查询参数）
    - **include_system**: 是否包含系统模板（可选，默认true）
    """
    query = db.query(FlowchartTemplate)

    if category:
        query = query.filter(FlowchartTemplate.category == category)

    if not include_system:
        query = query.filter(FlowchartTemplate.is_system == False)

    templates = query.order_by(FlowchartTemplate.created_at.desc()).all()

    return templates


@router.post(
    "/templates/{template_id}/apply",
    response_model=FlowchartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="应用模板创建流程图",
    description="使用指定模板创建新的流程图"
)
def apply_template(
    template_id: UUID,
    request: ApplyTemplateRequest,
    db: Session = Depends(get_db)
):
    """
    应用模板创建流程图

    - **template_id**: 模板ID（路径参数）
    - **project_id**: 目标项目ID（请求体）
    - **name**: 流程图名称（可选，默认使用模板名称）
    - **description**: 流程图描述（可选）
    """
    # 获取模板
    template = db.query(FlowchartTemplate).filter(
        FlowchartTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模板 '{template_id}' 不存在"
        )

    # 确定流程图名称
    flowchart_name = request.name or template.name

    # 检查名称冲突
    existing = db.query(Flowchart).filter(
        Flowchart.project_id == request.project_id,
        Flowchart.name == flowchart_name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"项目下已存在名为 '{flowchart_name}' 的流程图"
        )

    # 创建新流程图
    flowchart = Flowchart(
        id=uuid4(),
        project_id=request.project_id,
        name=flowchart_name,
        description=request.description or template.description,
        nodes=template.nodes or [],
        edges=template.edges or [],
        status="draft",
        version=1,
        template_id=template_id
    )

    db.add(flowchart)
    db.commit()
    db.refresh(flowchart)

    return flowchart
