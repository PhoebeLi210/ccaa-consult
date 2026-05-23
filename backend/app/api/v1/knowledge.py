#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库API

提供行业知识、条款知识、文档生成上下文等功能
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query

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


# 模拟数据 - 行业信息
INDUSTRIES_DATA = {
    "manufacturing": {
        "code": "manufacturing",
        "name": "制造业",
        "description": "包括机械制造、电子制造、化工制造等各类制造型企业",
        "applicable_standards": ["ISO9001:2015", "ISO14001:2015", "ISO45001:2018"],
        "typical_clauses": ["7.1.3", "7.1.4", "8.5.1", "8.5.4"],
        "key_requirements": ["生产过程控制", "设备管理", "质量检验", "环境管理"],
        "common_documents": ["质量手册", "程序文件", "作业指导书", "检验规范"]
    },
    "it_service": {
        "code": "it_service",
        "name": "IT服务业",
        "description": "软件开发、系统集成、IT咨询等服务型企业",
        "applicable_standards": ["ISO9001:2015", "ISO20000-1:2018", "ISO27001:2022"],
        "typical_clauses": ["8.2.3", "8.3.2", "8.3.4", "9.1.2"],
        "key_requirements": ["服务级别管理", "变更管理", "信息安全", "客户满意度"],
        "common_documents": ["服务目录", "SLA协议", "变更流程", "事件管理程序"]
    },
    "food_processing": {
        "code": "food_processing",
        "name": "食品加工",
        "description": "食品生产、加工、包装企业",
        "applicable_standards": ["ISO9001:2015", "ISO22000:2018", "HACCP"],
        "typical_clauses": ["7.1.6", "8.2.4", "8.5.1", "9.1.1"],
        "key_requirements": ["食品安全", "卫生控制", "追溯系统", "HACCP计划"],
        "common_documents": ["食品安全手册", "HACCP计划", "前提方案", "召回程序"]
    },
    "construction": {
        "code": "construction",
        "name": "建筑工程",
        "description": "建筑施工、工程承包、装饰装修企业",
        "applicable_standards": ["ISO9001:2015", "ISO14001:2015", "ISO45001:2018"],
        "typical_clauses": ["8.1", "8.4", "8.5.1", "9.1.1"],
        "key_requirements": ["施工过程控制", "分包管理", "安全管理", "质量控制"],
        "common_documents": ["施工组织设计", "安全方案", "质量计划", "验收规范"]
    },
    "medical_device": {
        "code": "medical_device",
        "name": "医疗器械",
        "description": "医疗器械生产、经营企业",
        "applicable_standards": ["ISO9001:2015", "ISO13485:2016", "ISO14971:2019"],
        "typical_clauses": ["7.1", "7.3", "7.5", "8.2.4"],
        "key_requirements": ["风险管理", "设计控制", "灭菌验证", "可追溯性"],
        "common_documents": ["风险管理文件", "设计历史文件", "主文档", "警戒系统程序"]
    },
    "logistics": {
        "code": "logistics",
        "name": "物流服务",
        "description": "仓储、运输、配送等物流服务提供商",
        "applicable_standards": ["ISO9001:2015", "ISO14001:2015", "ISO28000:2007"],
        "typical_clauses": ["8.2.3", "8.4", "8.5.4", "9.1.2"],
        "key_requirements": ["运输安全", "仓储管理", "供应链安全", "应急准备"],
        "common_documents": ["运输操作规程", "仓储管理程序", "应急预案", "供应商评估表"]
    }
}


# API端点

@router.get("/industries", response_model=IndustriesListResponse)
async def get_all_industries():
    """
    获取所有行业列表
    
    返回系统中支持的所有行业及其基本信息
    """
    industries = []
    for code, data in INDUSTRIES_DATA.items():
        industries.append(IndustryInfo(
            code=data["code"],
            name=data["name"],
            description=data["description"],
            applicable_standards=data["applicable_standards"],
            typical_clauses=data["typical_clauses"]
        ))
    
    return IndustriesListResponse(
        industries=industries,
        total=len(industries)
    )


@router.get("/industries/{code}", response_model=IndustryDetail)
async def get_industry_detail(code: str):
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
async def match_industry(request: IndustryMatchRequest):
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
async def get_industry_context(code: str):
    """
    获取行业文档生成上下文
    """
    if code not in INDUSTRIES_DATA:
        raise HTTPException(status_code=404, detail=f"行业 '{code}' 不存在")
    
    data = INDUSTRIES_DATA[code]
    
    reqs = chr(10).join(['- ' + req for req in data.get("key_requirements", [])])
    docs = chr(10).join(['- ' + doc for doc in data.get("common_documents", [])])
    stds = ', '.join(data["applicable_standards"])
    
    context = f"行业：{data['name']}
描述：{data['description']}

适用标准：{stds}

关键要求：
{reqs}

常用文档：
{docs}"
    
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
async def get_clause_knowledge(standard: str, clause: str):
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
async def generate_document_context(request: DocumentContextRequest):
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
    
    prompt_context = f"【文档生成上下文】

行业：{industry_data['name']}
标准：{request.standard}
文档类型：{request.document_type}

企业信息：
- 企业名称：{name}
- 经营范围：{scope}

行业特定要求：
{reqs}

适用条款：
{clauses}

请根据以上信息生成符合标准要求的专业文档内容。"
    
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
async def get_knowledge_statistics():
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
