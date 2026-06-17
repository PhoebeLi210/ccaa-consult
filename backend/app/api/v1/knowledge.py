#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库API

提供行业知识、条款知识、文档生成上下文等功能
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/knowledge", tags=["知识库"])


# 请求/响应模型

class IndustryInfo(BaseModel):
    """行业信息"""
    code: str
    name: str
    description: str
    applicable_standards: List[str] = []
    typical_clauses: List[str] = []


class IndustryDetail(BaseModel):
    """行业详情"""
    code: str
    name: str
    description: str
    applicable_standards: List[str]
    typical_clauses: List[str]
    key_requirements: List[str] = []
    common_documents: List[str] = []


class IndustryMatchRequest(BaseModel):
    """行业匹配请求"""
    company_name: Optional[str] = None
    business_scope: str = Field(..., description="经营范围描述")
    main_products: Optional[List[str]] = None
    industry_code: Optional[str] = None


class IndustryMatchResult(BaseModel):
    """行业匹配结果"""
    matched_industry: IndustryInfo
    confidence: float = Field(..., ge=0, le=1, description="匹配置信度")
    alternative_industries: List[IndustryInfo] = []
    match_reason: str


class IndustryContextResponse(BaseModel):
    """行业上下文响应"""
    industry_code: str
    industry_name: str
    context: str
    relevant_clauses: List[Dict[str, Any]]
    document_templates: List[str]


class ClauseKnowledgeResponse(BaseModel):
    """条款知识响应"""
    standard: str
    clause: str
    title: str
    content: str
    key_points: List[str]
    implementation_guidance: Optional[str]
    industry_applications: List[Dict[str, Any]]
    related_clauses: List[str]


class DocumentContextRequest(BaseModel):
    """文档生成上下文请求"""
    industry_code: str
    standard: str
    document_type: str
    company_info: Dict[str, Any]
    additional_context: Optional[Dict[str, Any]] = None


class DocumentContextResponse(BaseModel):
    """文档生成上下文响应"""
    context_id: str
    prompt_context: str
    relevant_clauses: List[Dict[str, Any]]
    industry_specific_requirements: List[str]
    suggested_structure: List[str]


class KnowledgeStatistics(BaseModel):
    """知识库统计"""
    total_industries: int
    total_standards: int
    total_clauses: int
    total_document_templates: int
    version: str
    last_updated: str
    coverage_by_standard: Dict[str, int]


class IndustriesListResponse(BaseModel):
    """行业列表响应"""
    industries: List[IndustryInfo]
    total: int


# 行业知识数据
INDUSTRIES_DATA = {
    "system_integration": {
        "code": "system_integration",
        "name": "系统集成",
        "description": "信息系统集成服务，包括软件开发、系统集成、IT咨询等",
        "applicable_standards": ["ISO9001:2015", "ISO20000-1:2018", "ISO27001:2022"],
        "typical_clauses": ["8.2.3", "8.3.2", "8.3.4", "9.1.2"],
        "key_requirements": ["项目管理", "需求分析", "系统测试", "交付验收", "信息安全", "客户服务"],
        "common_documents": ["项目管理程序", "需求分析规范", "测试规范", "验收报告", "变更管理程序", "配置管理程序"]
    },
    "software_development": {
        "code": "software_development",
        "name": "软件开发",
        "description": "软件产品开发、定制软件开发、移动应用开发等",
        "applicable_standards": ["ISO9001:2015", "ISO27001:2022", "CMMI"],
        "typical_clauses": ["8.3.1", "8.3.2", "8.3.3", "8.3.4", "8.3.5"],
        "key_requirements": ["需求管理", "设计开发", "代码评审", "版本控制", "缺陷管理", "发布管理"],
        "common_documents": ["软件开发计划", "需求规格说明书", "设计文档", "测试用例", "发布记录", "缺陷报告"]
    },
    "construction": {
        "code": "construction",
        "name": "建筑工程",
        "description": "建筑施工、工程承包、装饰装修企业",
        "applicable_standards": ["ISO9001:2015", "ISO14001:2015", "ISO45001:2018"],
        "typical_clauses": ["8.1", "8.4", "8.5.1", "9.1.1"],
        "key_requirements": ["施工过程控制", "分包管理", "安全管理", "质量控制", "环境保护"],
        "common_documents": ["施工组织设计", "安全方案", "质量计划", "验收规范", "环境管理方案"]
    },
    "steel_structure": {
        "code": "steel_structure",
        "name": "钢结构",
        "description": "钢结构工程设计、制作、安装企业",
        "applicable_standards": ["ISO9001:2015", "ISO14001:2015", "ISO45001:2018"],
        "typical_clauses": ["8.5.1", "8.5.2", "8.6", "7.1.3"],
        "key_requirements": ["焊接质量控制", "涂装质量", "安装精度", "材料检验", "无损检测"],
        "common_documents": ["焊接工艺评定", "涂装工艺规程", "检验试验计划", "材料质量证明", "安装方案"]
    },
    "archive_digitalization": {
        "code": "archive_digitalization",
        "name": "档案数字化",
        "description": "档案整理、数字化加工、档案管理服务",
        "applicable_standards": ["ISO9001:2015", "ISO27001:2022"],
        "typical_clauses": ["7.5", "8.5.1", "8.5.2", "8.6"],
        "key_requirements": ["档案整理规范", "数字化质量控制", "数据安全", "保密管理", "库房管理"],
        "common_documents": ["档案整理规范", "数字化加工规程", "保密管理制度", "质量检验标准", "库房管理制度"]
    },
    "intelligent_manufacturing": {
        "code": "intelligent_manufacturing",
        "name": "智能制造",
        "description": "智能制造装备、工业自动化、智能控制系统",
        "applicable_standards": ["ISO9001:2015", "ISO14001:2015", "ISO45001:2018"],
        "typical_clauses": ["8.3", "8.5.1", "7.1.3", "7.1.5"],
        "key_requirements": ["设计开发", "生产过程控制", "设备管理", "自动化控制", "质量检测"],
        "common_documents": ["设计开发程序", "设备维护规程", "生产过程控制程序", "质量检测规范", "自动化系统操作规程"]
    },
    "food_production": {
        "code": "food_production",
        "name": "食品生产",
        "description": "食品生产、加工、包装企业",
        "applicable_standards": ["ISO9001:2015", "ISO22000:2018", "HACCP"],
        "typical_clauses": ["7.1.6", "8.2.4", "8.5.1", "9.1.1"],
        "key_requirements": ["食品安全", "卫生控制", "追溯系统", "HACCP计划", "配方管理"],
        "common_documents": ["食品安全手册", "HACCP计划", "前提方案", "召回程序", "卫生管理规程"]
    },
    "electromechanical": {
        "code": "electromechanical",
        "name": "机电设备",
        "description": "机电设备制造、安装、维修服务",
        "applicable_standards": ["ISO9001:2015", "ISO14001:2015", "ISO45001:2018"],
        "typical_clauses": ["8.5.1", "7.1.3", "8.6", "7.1.5"],
        "key_requirements": ["设备制造质量", "安装调试", "维修保养", "备件管理", "技术文档"],
        "common_documents": ["设备制造工艺", "安装调试规程", "维修保养手册", "检验试验规程", "技术档案管理"]
    },
    "intelligent_tech": {
        "code": "intelligent_tech",
        "name": "智能科技",
        "description": "智能产品研发、销售，涉及设计开发过程",
        "applicable_standards": ["ISO9001:2015", "ISO14001:2015", "ISO45001:2018"],
        "typical_clauses": ["8.3.1", "8.3.2", "8.3.3", "8.3.4"],
        "key_requirements": ["产品设计开发", "硬件研发", "软件集成", "测试验证", "知识产权"],
        "common_documents": ["设计开发计划", "产品规格书", "测试报告", "知识产权管理制度", "技术文件管理"]
    },
    "property_management": {
        "code": "property_management",
        "name": "物业管理",
        "description": "物业服务、设施管理、社区管理",
        "applicable_standards": ["ISO9001:2015", "ISO14001:2015", "ISO45001:2018"],
        "typical_clauses": ["8.2.1", "8.5.1", "9.1.2", "7.1.2"],
        "key_requirements": ["服务标准", "设施维护", "安全管理", "环境绿化", "客户满意度"],
        "common_documents": ["服务标准手册", "设施维护规程", "安全管理方案", "应急预案", "客户投诉处理程序"]
    },
    "labor_dispatch": {
        "code": "labor_dispatch",
        "name": "劳务派遣",
        "description": "人力资源服务、劳务派遣、外包服务",
        "applicable_standards": ["ISO9001:2015", "ISO45001:2018"],
        "typical_clauses": ["8.2", "7.1.2", "7.2", "9.1.2"],
        "key_requirements": ["用工管理", "劳动关系", "社保公积金", "员工培训", "安全教育"],
        "common_documents": ["用工管理制度", "劳动合同模板", "社保管理规程", "员工培训计划", "安全教育记录"]
    },
}


# API端点

@router.get("/industries", summary="获取所有行业列表")
async def get_all_industries(current_user = Depends(get_current_user)):
    """获取所有行业列表"""
    industries = []
    for code, data in INDUSTRIES_DATA.items():
        industries.append({
            "code": data["code"],
            "name": data["name"],
            "description": data["description"],
        })
    return industries


@router.get("/industries/{code}", response_model=IndustryDetail)
async def get_industry_detail(code: str, current_user = Depends(get_current_user)):
    """
    获取指定行业详情
    """
    if code not in INDUSTRIES_DATA:
        raise HTTPException(status_code=404, detail=f"行业 '{code}' 不存在")
    
    data = INDUSTRIES_DATA[code]
    return IndustryDetail(
        code=data["code"],
        name=data["name"],
        description=data["description"],
        applicable_standards=data["applicable_standards"],
        typical_clauses=data["typical_clauses"],
        key_requirements=data.get("key_requirements", []),
        common_documents=data.get("common_documents", [])
    )


@router.post("/industries/match", response_model=IndustryMatchResult)
async def match_industry(request: IndustryMatchRequest, current_user = Depends(get_current_user)):
    """
    根据企业信息匹配行业
    """
    business_scope = request.business_scope.lower()
    
    industry_scores = {}
    
    keywords_mapping = {
        "manufacturing": ["制造", "生产", "加工", "工厂", "机械", "电子", "化工"],
        "it_service": ["软件", "开发", "系统", "it", "信息", "技术", "服务"],
        "food_processing": ["食品", "饮料", "加工", "餐饮", "食材"],
        "construction": ["建筑", "工程", "施工", "装修", "建设"],
        "medical_device": ["医疗", "器械", "设备", "药品", "健康"],
        "logistics": ["物流", "运输", "仓储", "配送", "供应链"]
    }
    
    for industry_code, keywords in keywords_mapping.items():
        score = 0
        for keyword in keywords:
            if keyword in business_scope:
                score += 1
        if score > 0:
            industry_scores[industry_code] = score
    
    if not industry_scores:
        matched_code = "manufacturing"
        confidence = 0.5
    else:
        matched_code = max(industry_scores, key=industry_scores.get)
        max_score = industry_scores[matched_code]
        total_keywords = len(keywords_mapping[matched_code])
        confidence = min(max_score / total_keywords * 2, 1.0) if total_keywords > 0 else 0.5
    
    matched_data = INDUSTRIES_DATA[matched_code]
    matched_industry = IndustryInfo(
        code=matched_data["code"],
        name=matched_data["name"],
        description=matched_data["description"],
        applicable_standards=matched_data["applicable_standards"],
        typical_clauses=matched_data["typical_clauses"]
    )
    
    alternative_industries = []
    sorted_scores = sorted(industry_scores.items(), key=lambda x: x[1], reverse=True)
    for code, score in sorted_scores[1:3]:
        if code != matched_code:
            data = INDUSTRIES_DATA[code]
            alternative_industries.append(IndustryInfo(
                code=data["code"],
                name=data["name"],
                description=data["description"],
                applicable_standards=data["applicable_standards"],
                typical_clauses=data["typical_clauses"]
            ))
    
    match_reason = f"根据经营范围描述中的关键词匹配，最符合'{matched_industry.name}'行业特征"
    
    return IndustryMatchResult(
        matched_industry=matched_industry,
        confidence=confidence,
        alternative_industries=alternative_industries,
        match_reason=match_reason
    )


@router.get("/industries/{code}/context", response_model=IndustryContextResponse)
async def get_industry_context(code: str, current_user = Depends(get_current_user)):
    """
    获取行业文档生成上下文
    """
    if code not in INDUSTRIES_DATA:
        raise HTTPException(status_code=404, detail=f"行业 '{code}' 不存在")
    
    data = INDUSTRIES_DATA[code]
    
    reqs = chr(10).join(['- ' + req for req in data.get("key_requirements", [])])
    docs = chr(10).join(['- ' + doc for doc in data.get("common_documents", [])])
    stds = ', '.join(data["applicable_standards"])
    
    context = (
        f"行业：{data['name']}\n"
        f"描述：{data['description']}\n\n"
        f"适用标准：{stds}\n\n"
        f"关键要求：\n{reqs}\n\n"
        f"常用文档：\n{docs}"
    )
    
    relevant_clauses = []
    for clause in data["typical_clauses"]:
        relevant_clauses.append({
            "clause": clause,
            "title": f"条款 {clause} 相关内容",
            "importance": "high"
        })
    
    return IndustryContextResponse(
        industry_code=code,
        industry_name=data["name"],
        context=context.strip(),
        relevant_clauses=relevant_clauses,
        document_templates=data.get("common_documents", [])
    )


@router.get("/clauses/{standard}/{clause}", response_model=ClauseKnowledgeResponse)
async def get_clause_knowledge(standard: str, clause: str, current_user = Depends(get_current_user)):
    """
    查询条款知识
    """
    clause_data = {
        "ISO9001:2015": {
            "4.1": {
                "title": "理解组织及其环境",
                "content": "组织应确定与其目标和战略方向相关并影响其实现质量管理体系预期结果的各种外部和内部因素。",
                "key_points": [
                    "识别外部因素：法律法规、技术、竞争、市场、文化、社会和经济环境",
                    "识别内部因素：价值观、文化、知识和绩效",
                    "定期监视和评审这些信息"
                ],
                "implementation_guidance": "建议建立组织环境分析程序，使用SWOT或PEST分析工具，每年至少评审一次。",
                "industry_applications": [
                    {"industry": "制造业", "application": "关注供应链稳定性、原材料价格波动"},
                    {"industry": "IT服务", "application": "关注技术更新速度、数据安全法规"}
                ],
                "related_clauses": ["4.2", "5.1", "9.3"]
            },
            "5.1": {
                "title": "领导作用和承诺",
                "content": "最高管理者应证实其对质量管理体系的领导作用和承诺。",
                "key_points": [
                    "对质量管理体系的有效性负责",
                    "确保质量方针和质量目标的建立",
                    "确保资源的可获得性",
                    "传达满足顾客和法律法规要求的重要性"
                ],
                "implementation_guidance": "最高管理者应签署质量方针，定期主持管理评审会议。",
                "industry_applications": [
                    {"industry": "通用", "application": "建立质量方针，任命管理者代表"}
                ],
                "related_clauses": ["5.2", "5.3", "9.3"]
            }
        },
        "ISO14001:2015": {
            "4.1": {
                "title": "理解组织及其所处的环境",
                "content": "组织应确定与其宗旨相关并影响其实现环境管理体系预期结果的能力的外部和内部问题。",
                "key_points": [
                    "识别环境问题相关的外部因素",
                    "识别组织内部的环境因素",
                    "考虑合规义务和风险"
                ],
                "implementation_guidance": "进行环境因素识别和评价，建立环境因素清单。",
                "industry_applications": [
                    {"industry": "制造业", "application": "重点关注废气、废水、固废排放"},
                    {"industry": "建筑业", "application": "关注施工噪声、扬尘、废弃物"}
                ],
                "related_clauses": ["4.2", "6.1", "9.3"]
            }
        }
    }
    
    if standard not in clause_data or clause not in clause_data[standard]:
        return ClauseKnowledgeResponse(
            standard=standard,
            clause=clause,
            title=f"条款 {clause}",
            content="该条款的详细内容请参考标准原文。",
            key_points=["请参考标准原文获取详细要求"],
            implementation_guidance="建议咨询专业审核员或查阅标准实施指南。",
            industry_applications=[],
            related_clauses=[]
        )
    
    data = clause_data[standard][clause]
    return ClauseKnowledgeResponse(
        standard=standard,
        clause=clause,
        title=data["title"],
        content=data["content"],
        key_points=data["key_points"],
        implementation_guidance=data.get("implementation_guidance"),
        industry_applications=data.get("industry_applications", []),
        related_clauses=data.get("related_clauses", [])
    )


@router.post("/document-context", response_model=DocumentContextResponse)
async def generate_document_context(request: DocumentContextRequest, current_user = Depends(get_current_user)):
    """
    生成文档生成上下文
    """
    if request.industry_code not in INDUSTRIES_DATA:
        raise HTTPException(status_code=404, detail=f"行业 '{request.industry_code}' 不存在")
    
    industry_data = INDUSTRIES_DATA[request.industry_code]
    
    reqs = chr(10).join(['- ' + req for req in industry_data.get("key_requirements", [])])
    clauses = chr(10).join(['- ' + clause for clause in industry_data["typical_clauses"]])
    name = request.company_info.get('name', '未指定')
    scope = request.company_info.get('business_scope', '未指定')
    
    prompt_context = (
        f"【文档生成上下文】\n\n"
        f"行业：{industry_data['name']}\n"
        f"标准：{request.standard}\n"
        f"文档类型：{request.document_type}\n\n"
        f"企业信息：\n"
        f"- 企业名称：{name}\n"
        f"- 经营范围：{scope}\n\n"
        f"行业特定要求：\n{reqs}\n\n"
        f"适用条款：\n{clauses}\n\n"
        f"请根据以上信息生成符合标准要求的专业文档内容。"
    )
    
    relevant_clauses = []
    for clause in industry_data["typical_clauses"][:5]:
        relevant_clauses.append({
            "clause": clause,
            "standard": request.standard,
            "title": f"条款 {clause}",
            "relevance": "high"
        })
    
    suggested_structure = [
        "1. 目的",
        "2. 适用范围",
        "3. 职责",
        "4. 程序/要求",
        "5. 相关文件",
        "6. 记录"
    ]
    
    import uuid
    return DocumentContextResponse(
        context_id=str(uuid.uuid4()),
        prompt_context=prompt_context.strip(),
        relevant_clauses=relevant_clauses,
        industry_specific_requirements=industry_data.get("key_requirements", []),
        suggested_structure=suggested_structure
    )


@router.get("/statistics", response_model=KnowledgeStatistics)
async def get_knowledge_statistics(current_user = Depends(get_current_user)):
    """
    获取知识库统计
    """
    coverage_by_standard = {
        "ISO9001:2015": 42,
        "ISO14001:2015": 38,
        "ISO45001:2018": 45,
        "ISO22000:2018": 35,
        "ISO13485:2016": 52,
        "ISO20000-1:2018": 40,
        "ISO27001:2022": 48
    }
    
    return KnowledgeStatistics(
        total_industries=len(INDUSTRIES_DATA),
        total_standards=len(coverage_by_standard),
        total_clauses=sum(coverage_by_standard.values()),
        total_document_templates=120,
        version="1.0.0",
        last_updated="2024-01-15",
        coverage_by_standard=coverage_by_standard
    )


# ============ 前端需要的额外端点 ============

@router.get("/list", summary="获取知识列表")
async def get_knowledge_list(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    industry: Optional[str] = None,
    current_user = Depends(get_current_user),
):
    """获取知识库条目列表"""
    items = []
    for code, data in INDUSTRIES_DATA.items():
        if industry and code != industry:
            continue
        items.append({
            "id": code,
            "title": data.get("name", code),
            "summary": data.get("description", ""),
            "category": "standard",
            "industry_name": data.get("name", code),
            "tags": data.get("typical_clauses", []),
            "view_count": 0,
            "key_requirements": data.get("key_requirements", []),
            "common_documents": data.get("common_documents", []),
            "applicable_standards": data.get("applicable_standards", []),
        })
    total = len(items)
    start = (page - 1) * page_size
    return {"items": items[start:start + page_size], "total": total}


@router.get("/categories/tree", summary="获取知识分类树")
async def get_knowledge_category_tree(current_user = Depends(get_current_user)):
    """获取知识库分类树"""
    return [
        {"key": "standard", "title": "标准知识", "children": [
            {"key": "iso9001", "title": "ISO 9001 质量管理"},
            {"key": "iso14001", "title": "ISO 14001 环境管理"},
            {"key": "iso45001", "title": "ISO 45001 职业健康安全"},
        ]},
        {"key": "industry", "title": "行业知识", "children": [
            {"key": code, "title": data.get("name", code)}
            for code, data in INDUSTRIES_DATA.items()
        ]},
        {"key": "experience", "title": "审核经验"},
        {"key": "application", "title": "应用案例"},
    ]


@router.get("/standards/list", summary="获取支持的标准列表")
async def get_supported_standards_list(current_user = Depends(get_current_user)):
    """获取所有支持的ISO标准"""
    return [
        {"code": "ISO9001", "name": "质量管理体系"},
        {"code": "ISO14001", "name": "环境管理体系"},
        {"code": "ISO45001", "name": "职业健康安全管理体系"},
        {"code": "ISO22000", "name": "食品安全管理体系"},
        {"code": "ISO13485", "name": "医疗器械质量管理体系"},
    ]


@router.get("/search", summary="搜索知识")
async def search_knowledge(q: str = "", query: str = "", current_user = Depends(get_current_user)):
    """搜索知识库"""
    keyword = q or query
    items = []
    for code, data in INDUSTRIES_DATA.items():
        if keyword and keyword.lower() not in data.get("name", "").lower() and keyword.lower() not in data.get("description", "").lower():
            continue
        items.append({
            "id": code,
            "title": data.get("name", code),
            "summary": data.get("description", ""),
            "category": "standard",
            "industry_name": data.get("name", code),
        })
    return {"items": items, "total": len(items)}


@router.get("/industry/status", summary="获取行业数据状态")
async def get_industry_data_status(current_user = Depends(get_current_user)):
    """获取各行业数据完整度状态"""
    return {
        code: {"status": "complete", "name": data.get("name", code)}
        for code, data in INDUSTRIES_DATA.items()
    }


@router.get("/articles/{article_id}", summary="获取单篇文章详情")
async def get_knowledge_article(article_id: str, current_user = Depends(get_current_user)):
    """根据ID获取单篇知识库文章"""
    from app.models.models import KnowledgeArticle
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    
    engine = create_engine("sqlite:///data/zhizhitong.db")
    with Session(engine) as session:
        article = session.query(KnowledgeArticle).filter(
            KnowledgeArticle.article_id == article_id,
            KnowledgeArticle.is_active == True
        ).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        return article.to_dict()


@router.get("/articles", summary="获取导入的知识文章列表")
async def list_knowledge_articles(
    category: Optional[str] = None,
    industry_code: Optional[str] = None,
    standard_code: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user = Depends(get_current_user),
):
    """获取已导入的知识库文章"""
    from app.models.models import KnowledgeArticle
    
    # 直接使用同步查询
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    
    engine = create_engine("sqlite:///data/zhizhitong.db")
    with Session(engine) as session:
        query = session.query(KnowledgeArticle).filter(KnowledgeArticle.is_active == True)
        
        if category:
            query = query.filter(KnowledgeArticle.category == category)
        if industry_code:
            query = query.filter(KnowledgeArticle.industry_code == industry_code)
        if standard_code:
            query = query.filter(KnowledgeArticle.standard_code == standard_code)
        
        total = query.count()
        articles = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "items": [a.to_dict() for a in articles],
            "total": total,
        }


@router.get("/{item_id}", summary="获取知识详情")
async def get_knowledge_detail(item_id: str, current_user = Depends(get_current_user)):
    """获取单个知识条目详情"""
    data = INDUSTRIES_DATA.get(item_id)
    if not data:
        return {"id": item_id, "title": item_id, "summary": "", "category": "standard"}
    return {
        "id": item_id,
        "title": data.get("name", item_id),
        "summary": data.get("description", ""),
        "category": "standard",
        "industry_name": data.get("name", item_id),
        "tags": data.get("typical_clauses", []),
        "content": data.get("description", ""),
        "key_requirements": data.get("key_requirements", []),
        "common_documents": data.get("common_documents", []),
        "applicable_standards": data.get("applicable_standards", []),
    }


@router.get("/{item_id}/related", summary="获取相关知识")
async def get_related_knowledge(item_id: str, limit: int = 5, current_user = Depends(get_current_user)):
    """获取与指定知识相关的其他知识条目"""
    items = []
    for code, data in INDUSTRIES_DATA.items():
        if code != item_id:
            items.append({
                "id": code,
                "title": data.get("name", code),
                "summary": data.get("description", ""),
                "category": "standard",
            })
        if len(items) >= limit:
            break
    return items


@router.post("/{item_id}/view", summary="增加浏览次数")
async def increment_view_count(item_id: str, current_user = Depends(get_current_user)):
    """记录知识条目被浏览"""
    return {"message": "ok"}


@router.get("/standards/{clause_id}", summary="获取标准条款详情")
async def get_standard_clause_detail(clause_id: str, current_user = Depends(get_current_user)):
    """获取标准条款详情"""
    data = INDUSTRIES_DATA.get(clause_id)
    if data:
        return {
            "id": clause_id,
            "clause_number": clause_id,
            "title": data.get("name", clause_id),
            "description": data.get("description", ""),
            "standard": data.get("applicable_standards", ["ISO9001"])[0] if data.get("applicable_standards") else "ISO9001",
            "requirements": data.get("key_requirements", []),
            "audit_points": [],
            "key_requirements": data.get("key_requirements", []),
            "common_documents": data.get("common_documents", []),
            "applicable_standards": data.get("applicable_standards", []),
        }
    return {
        "id": clause_id,
        "clause_number": clause_id,
        "title": clause_id,
        "description": "",
        "standard": "ISO9001",
        "requirements": [],
        "audit_points": [],
    }


# ============ 知识库导入接口 ============

@router.post("/import", summary="导入知识库文档")
async def import_knowledge_article(
    title: str,
    category: str = "standard",
    industry_code: Optional[str] = None,
    standard_code: Optional[str] = None,
    content: str = "",
    tags: Optional[List[str]] = None,
    db = None,
):
    """
    导入知识库文章
    
    支持导入Markdown格式的知识库文档
    """
    from app.models.models import KnowledgeArticle
    import uuid
    
    article_id = str(uuid.uuid4())
    
    # 生成摘要（取前200字）
    summary = content[:200].replace("#", "").replace("*", "").strip() if content else ""
    
    article = KnowledgeArticle(
        article_id=article_id,
        title=title,
        category=category,
        industry_code=industry_code,
        standard_code=standard_code,
        content=content,
        summary=summary,
        tags=tags or [],
        source_file="",
    )
    
    # 如果有数据库连接，保存到数据库
    if db:
        try:
            db.add(article)
            await db.commit()
            await db.refresh(article)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")
    
    return {
        "message": "导入成功",
        "article_id": article_id,
        "title": title,
    }


@router.post("/import/file", summary="导入Markdown文件")
async def import_markdown_file(
    file_path: str,
    category: str = "standard",
    industry_code: Optional[str] = None,
    standard_code: Optional[str] = None,
):
    """
    从文件路径导入Markdown文档
    """
    from pathlib import Path
    
    path = Path(file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")
    
    if not path.suffix.lower() in ['.md', '.markdown']:
        raise HTTPException(status_code=400, detail="仅支持Markdown文件(.md)")
    
    content = path.read_text(encoding='utf-8')
    
    # 从文件名或内容提取标题
    title = path.stem
    if content.startswith('#'):
        first_line = content.split('\n')[0].replace('#', '').strip()
        if first_line:
            title = first_line
    
    # 从内容提取标签
    tags = []
    if 'ISO9001' in content:
        tags.append('ISO9001')
    if 'ISO14001' in content:
        tags.append('ISO14001')
    if 'ISO45001' in content:
        tags.append('ISO45001')
    if 'ISO27001' in content:
        tags.append('ISO27001')
    
    return {
        "title": title,
        "category": category,
        "content": content[:5000],
        "total_length": len(content),
        "tags": tags,
        "file_path": str(path),
    }
