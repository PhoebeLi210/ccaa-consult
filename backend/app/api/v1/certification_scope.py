#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 认证范围和专业代码API接口

提供认证标准列表、专业代码分类树、搜索和验证功能
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

router = APIRouter(prefix="/certification-scope", tags=["认证范围管理"])


# ============ 认证标准定义 ============

class CertificationStandard(BaseModel):
    """认证标准模型"""
    code: str = Field(..., description="标准代码")
    name: str = Field(..., description="标准名称")
    name_en: str = Field(..., description="英文名称")
    description: str = Field(..., description="标准描述")
    version: str = Field(..., description="版本号")


# 支持的认证标准列表
SUPPORTED_STANDARDS = [
    CertificationStandard(
        code="ISO9001",
        name="质量管理体系",
        name_en="ISO 9001:2015",
        description="国际标准化组织制定的质量管理体系标准，适用于各类组织",
        version="2015"
    ),
    CertificationStandard(
        code="ISO14001",
        name="环境管理体系",
        name_en="ISO 14001:2015",
        description="国际标准化组织制定的环境管理体系标准，帮助组织减少环境影响",
        version="2015"
    ),
    CertificationStandard(
        code="ISO45001",
        name="职业健康安全管理体系",
        name_en="ISO 45001:2018",
        description="国际标准化组织制定的职业健康安全管理体系标准，保护员工健康安全",
        version="2018"
    ),
]


# ============ 专业代码数据结构 ============

class ProfessionalCode(BaseModel):
    """专业代码模型"""
    code: str = Field(..., description="专业代码")
    name: str = Field(..., description="专业名称")
    name_en: Optional[str] = Field(None, description="英文名称")
    description: Optional[str] = Field(None, description="描述")
    parent_code: Optional[str] = Field(None, description="父级代码")
    level: int = Field(..., description="层级(1-4)")
    children: Optional[List["ProfessionalCode"]] = Field(None, description="子级代码列表")
    applicable_standards: List[str] = Field(default_factory=list, description="适用的认证标准")


# 专业代码分类树数据（模拟从ccaa-common读取的数据）
# 实际项目中这些数据应该从数据库或外部服务加载
PROFESSIONAL_CODES_TREE: List[ProfessionalCode] = [
    ProfessionalCode(
        code="01",
        name="农业、林业和渔业",
        name_en="Agriculture, forestry and fishing",
        description="农业生产、林业经营、渔业捕捞等相关活动",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
        children=[
            ProfessionalCode(
                code="01.01",
                name="农作物种植",
                description="谷物、蔬菜、水果等农作物种植",
                parent_code="01",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
                children=[
                    ProfessionalCode(
                        code="01.01.01",
                        name="谷物种植",
                        description="小麦、水稻、玉米等谷物种植",
                        parent_code="01.01",
                        level=3,
                        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
                    ),
                    ProfessionalCode(
                        code="01.01.02",
                        name="蔬菜种植",
                        description="各类蔬菜种植",
                        parent_code="01.01",
                        level=3,
                        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
                    ),
                    ProfessionalCode(
                        code="01.01.03",
                        name="水果种植",
                        description="各类水果种植",
                        parent_code="01.01",
                        level=3,
                        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
                    ),
                ]
            ),
            ProfessionalCode(
                code="01.02",
                name="畜牧业",
                description="牲畜、家禽饲养",
                parent_code="01",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="01.03",
                name="渔业",
                description="水产捕捞和养殖",
                parent_code="01",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
        ]
    ),
    ProfessionalCode(
        code="02",
        name="采矿业和采石业",
        name_en="Mining and quarrying",
        description="矿产资源开采和采石活动",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
        children=[
            ProfessionalCode(
                code="02.01",
                name="煤炭开采",
                description="煤炭的开采和洗选",
                parent_code="02",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="02.02",
                name="石油和天然气开采",
                description="原油和天然气开采",
                parent_code="02",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="02.03",
                name="金属矿开采",
                description="铁矿、有色金属矿开采",
                parent_code="02",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
        ]
    ),
    ProfessionalCode(
        code="03",
        name="食品、饮料和烟草",
        name_en="Food, beverages and tobacco",
        description="食品加工、饮料生产和烟草制品",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
        children=[
            ProfessionalCode(
                code="03.01",
                name="食品制造",
                description="各类食品生产加工",
                parent_code="03",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
                children=[
                    ProfessionalCode(
                        code="03.01.01",
                        name="肉类加工",
                        description="畜禽屠宰和肉类加工",
                        parent_code="03.01",
                        level=3,
                        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
                    ),
                    ProfessionalCode(
                        code="03.01.02",
                        name="乳制品制造",
                        description="液态奶、奶粉、奶酪等乳制品生产",
                        parent_code="03.01",
                        level=3,
                        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
                    ),
                    ProfessionalCode(
                        code="03.01.03",
                        name="烘焙食品制造",
                        description="面包、糕点、饼干等烘焙食品生产",
                        parent_code="03.01",
                        level=3,
                        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
                    ),
                    ProfessionalCode(
                        code="03.01.04",
                        name="饮料制造",
                        description="碳酸饮料、果汁、瓶装水等饮料生产",
                        parent_code="03.01",
                        level=3,
                        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
                    ),
                ]
            ),
            ProfessionalCode(
                code="03.02",
                name="烟草制品",
                description="卷烟、雪茄等烟草制品生产",
                parent_code="03",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
        ]
    ),
    ProfessionalCode(
        code="04",
        name="纺织品及纺织制品",
        name_en="Textiles and textile products",
        description="纺织原料、纺织品和服装制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
        children=[
            ProfessionalCode(
                code="04.01",
                name="纺织业",
                description="棉纺、毛纺、化纤织造等",
                parent_code="04",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="04.02",
                name="服装制造",
                description="各类服装生产加工",
                parent_code="04",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
        ]
    ),
    ProfessionalCode(
        code="05",
        name="皮革及皮革制品",
        name_en="Leather and leather products",
        description="皮革鞣制、皮革制品和鞋类制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="06",
        name="木材及木制品",
        name_en="Wood and wood products",
        description="木材加工、木制品和家具制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="07",
        name="纸浆、纸及纸制品",
        name_en="Pulp, paper and paper products",
        description="纸浆制造、造纸和纸制品加工",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="08",
        name="出版业",
        name_en="Publishing",
        description="图书、报刊、音像制品出版",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="09",
        name="印刷业",
        name_en="Printing",
        description="印刷和记录媒介复制",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="10",
        name="焦炭及精炼石油制品",
        name_en="Coke and refined petroleum products",
        description="焦炭、石油炼制和核燃料加工",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="11",
        name="化学品、化学制品及纤维",
        name_en="Chemicals, chemical products and fibres",
        description="基础化学原料、化肥、农药、合成材料等制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="12",
        name="药品",
        name_en="Pharmaceuticals",
        description="医药原料药和制剂制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="13",
        name="橡胶和塑料制品",
        name_en="Rubber and plastic products",
        description="橡胶制品和塑料制品制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="14",
        name="非金属矿物制品",
        name_en="Non-metallic mineral products",
        description="水泥、玻璃、陶瓷等非金属矿物制品",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="15",
        name="混凝土、水泥、石灰、石膏及其他",
        name_en="Concrete, cement, lime, plaster etc.",
        description="混凝土、水泥、石灰等建筑材料制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="16",
        name="基础金属及金属制品",
        name_en="Base metals and fabricated metal products",
        description="钢铁、有色金属冶炼和金属制品制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="17",
        name="机械及设备",
        name_en="Machinery and equipment",
        description="通用设备、专用设备、交通运输设备制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
        children=[
            ProfessionalCode(
                code="17.01",
                name="通用设备制造",
                description="锅炉、内燃机、泵、阀门等通用设备",
                parent_code="17",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="17.02",
                name="专用设备制造",
                description="矿山、冶金、化工、食品等专用设备",
                parent_code="17",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="17.03",
                name="汽车制造",
                description="汽车整车及零部件制造",
                parent_code="17",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="17.04",
                name="铁路、船舶、航空航天设备",
                description="铁路运输设备、船舶、航空航天器制造",
                parent_code="17",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
        ]
    ),
    ProfessionalCode(
        code="18",
        name="电及光学设备",
        name_en="Electrical and optical equipment",
        description="电气机械、电子设备、仪器仪表制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
        children=[
            ProfessionalCode(
                code="18.01",
                name="电机及输配电设备",
                description="发电机、电动机、变压器等电气设备",
                parent_code="18",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="18.02",
                name="电子及通信设备",
                description="计算机、通信设备、电子元器件制造",
                parent_code="18",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="18.03",
                name="仪器仪表制造",
                description="测量仪器、光学仪器、钟表等制造",
                parent_code="18",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
        ]
    ),
    ProfessionalCode(
        code="19",
        name="造船业",
        name_en="Shipbuilding",
        description="船舶及浮动装置制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="20",
        name="航空航天",
        name_en="Aerospace",
        description="航空器、航天器及相关设备制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="21",
        name="其他运输设备",
        name_en="Other transport equipment",
        description="摩托车、自行车、其他运输设备制造",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="22",
        name="其他未分类的制造业",
        name_en="Other not classified manufacturing",
        description="家具、珠宝、乐器等其他制造业",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="23",
        name="回收业",
        name_en="Recycling",
        description="废旧物资回收和加工",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="24",
        name="供电业",
        name_en="Electricity supply",
        description="电力生产和供应",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="25",
        name="供气业",
        name_en="Gas supply",
        description="燃气生产和供应",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="26",
        name="供水业",
        name_en="Water supply",
        description="自来水生产和供应",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="27",
        name="建设业",
        name_en="Construction",
        description="房屋建筑、土木工程、安装等建筑活动",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
        children=[
            ProfessionalCode(
                code="27.01",
                name="房屋建筑业",
                description="住宅、厂房、公共建筑等房屋建造",
                parent_code="27",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="27.02",
                name="土木工程建筑业",
                description="道路、桥梁、隧道、水利等工程建设",
                parent_code="27",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="27.03",
                name="建筑安装业",
                description="建筑物内设备安装、管道安装等",
                parent_code="27",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="27.04",
                name="建筑装饰业",
                description="建筑物装修装饰",
                parent_code="27",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
        ]
    ),
    ProfessionalCode(
        code="28",
        name="批发和零售业；汽车、摩托车、个人及家庭用品修理业",
        name_en="Wholesale and retail trade; repair of motor vehicles, motorcycles, personal and household goods",
        description="商品批发、零售和维修服务",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="29",
        name="宾馆及餐馆",
        name_en="Hotels and restaurants",
        description="住宿和餐饮服务",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="30",
        name="运输、仓储和通信",
        name_en="Transport, storage and communication",
        description="货物运输、仓储和电信服务",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="31",
        name="金融中介、房地产和租赁",
        name_en="Financial intermediation, real estate and renting",
        description="银行、保险、房地产和租赁服务",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="32",
        name="信息技术",
        name_en="Information technology",
        description="软件开发、信息技术服务、数据处理",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
        children=[
            ProfessionalCode(
                code="32.01",
                name="软件开发",
                description="系统软件、应用软件、嵌入式软件开发",
                parent_code="32",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="32.02",
                name="信息技术服务",
                description="信息系统集成、运维服务、数据处理",
                parent_code="32",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
            ProfessionalCode(
                code="32.03",
                name="互联网服务",
                description="互联网平台、互联网数据服务",
                parent_code="32",
                level=2,
                applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
            ),
        ]
    ),
    ProfessionalCode(
        code="33",
        name="工程服务",
        name_en="Engineering services",
        description="工程勘察、设计、监理等技术服务",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="34",
        name="其他服务",
        name_en="Other services",
        description="科学研究、教育、卫生、文化等其他服务",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
    ProfessionalCode(
        code="35",
        name="公共行政管理",
        name_en="Public administration",
        description="政府机构、公共管理和社会组织",
        level=1,
        applicable_standards=["ISO9001", "ISO14001", "ISO45001"],
    ),
]

# 构建代码索引字典，用于快速查找
PROFESSIONAL_CODES_INDEX: Dict[str, ProfessionalCode] = {}


def build_code_index(codes: List[ProfessionalCode], index: Dict[str, ProfessionalCode]):
    """构建专业代码索引"""
    for code in codes:
        index[code.code] = code
        if code.children:
            build_code_index(code.children, index)


# 初始化索引
build_code_index(PROFESSIONAL_CODES_TREE, PROFESSIONAL_CODES_INDEX)


# ============ 请求/响应模型 ============

class ValidateRequest(BaseModel):
    """验证请求模型"""
    standards: List[str] = Field(..., description="认证标准代码列表", example=["ISO9001", "ISO14001"])
    professional_codes: List[str] = Field(..., description="专业代码列表", example=["03.01.02", "17.03"])


class ValidateResult(BaseModel):
    """验证结果模型"""
    valid: bool = Field(..., description="是否有效")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")
    warnings: List[str] = Field(default_factory=list, description="警告信息列表")
    details: Dict[str, Any] = Field(default_factory=dict, description="详细信息")


class ProfessionalCodeSearchResult(BaseModel):
    """专业代码搜索结果"""
    total: int = Field(..., description="结果总数")
    codes: List[ProfessionalCode] = Field(..., description="匹配的专业代码列表")


# ============ API端点 ============

@router.get("/standards", response_model=List[CertificationStandard], summary="获取支持的认证标准列表")
async def get_standards():
    """
    获取系统支持的所有认证标准列表
    
    返回:
        - ISO9001: 质量管理体系
        - ISO14001: 环境管理体系  
        - ISO45001: 职业健康安全管理体系
    """
    return SUPPORTED_STANDARDS


@router.get("/standards/{code}", response_model=CertificationStandard, summary="获取指定认证标准详情")
async def get_standard_detail(code: str):
    """
    获取指定认证标准的详细信息
    
    参数:
        code: 标准代码 (ISO9001/ISO14001/ISO45001)
    """
    for standard in SUPPORTED_STANDARDS:
        if standard.code.upper() == code.upper():
            return standard
    raise HTTPException(status_code=404, detail=f"未找到认证标准: {code}")


@router.get("/professional-codes", response_model=List[ProfessionalCode], summary="获取专业代码分类树")
async def get_professional_codes(
    level: Optional[int] = Query(None, ge=1, le=4, description="层级过滤(1-4)")
):
    """
    获取专业代码分类树
    
    参数:
        level: 可选，按层级过滤(1=大类, 2=中类, 3=小类, 4=细类)
    
    返回完整的分类树结构，包含层级关系
    """
    if level is None:
        return PROFESSIONAL_CODES_TREE
    
    # 按层级过滤
    def filter_by_level(codes: List[ProfessionalCode], target_level: int) -> List[ProfessionalCode]:
        result = []
        for code in codes:
            if code.level <= target_level:
                new_code = code.copy()
                if code.children and code.level < target_level:
                    new_code.children = filter_by_level(code.children, target_level)
                else:
                    new_code.children = None
                result.append(new_code)
        return result
    
    return filter_by_level(PROFESSIONAL_CODES_TREE, level)


@router.get("/professional-codes/search", response_model=ProfessionalCodeSearchResult, summary="搜索专业代码")
async def search_professional_codes(
    q: str = Query(..., min_length=1, max_length=50, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回结果数量限制")
):
    """
    根据关键词搜索专业代码
    
    参数:
        q: 搜索关键词（支持代码或名称模糊匹配）
        limit: 返回结果数量限制
    
    返回匹配的专业代码列表
    """
    keyword = q.lower()
    results = []
    
    for code in PROFESSIONAL_CODES_INDEX.values():
        # 匹配代码或名称
        if (keyword in code.code.lower() or 
            keyword in code.name.lower() or
            (code.description and keyword in code.description.lower())):
            results.append(code)
    
    # 去重并限制数量
    seen_codes = set()
    unique_results = []
    for code in results:
        if code.code not in seen_codes:
            seen_codes.add(code.code)
            unique_results.append(code)
    
    # 按代码排序
    unique_results.sort(key=lambda x: x.code)
    
    return ProfessionalCodeSearchResult(
        total=len(unique_results),
        codes=unique_results[:limit]
    )


@router.get("/professional-codes/{code}", response_model=ProfessionalCode, summary="获取指定专业代码详情")
async def get_professional_code_detail(code: str):
    """
    获取指定专业代码的详细信息
    
    参数:
        code: 专业代码 (如: 03.01.02)
    """
    if code in PROFESSIONAL_CODES_INDEX:
        return PROFESSIONAL_CODES_INDEX[code]
    raise HTTPException(status_code=404, detail=f"未找到专业代码: {code}")


@router.post("/validate", response_model=ValidateResult, summary="验证认证范围组合是否有效")
async def validate_certification_scope(request: ValidateRequest):
    """
    验证认证范围组合是否有效
    
    验证规则:
        1. 检查认证标准是否有效
        2. 检查专业代码是否有效
        3. 检查专业代码是否适用于指定的认证标准
        4. 检查组合是否合理（如某些高风险行业需要特定标准）
    
    请求体:
        standards: 认证标准代码列表
        professional_codes: 专业代码列表
    
    返回验证结果，包含有效性、错误和警告信息
    """
    errors = []
    warnings = []
    details = {
        "valid_standards": [],
        "valid_codes": [],
        "invalid_standards": [],
        "invalid_codes": [],
        "incompatible_codes": []
    }
    
    # 验证认证标准
    valid_standard_codes = [s.code.upper() for s in SUPPORTED_STANDARDS]
    for std in request.standards:
        if std.upper() not in valid_standard_codes:
            errors.append(f"无效的认证标准: {std}")
            details["invalid_standards"].append(std)
        else:
            details["valid_standards"].append(std)
    
    # 验证专业代码
    for code in request.professional_codes:
        if code not in PROFESSIONAL_CODES_INDEX:
            errors.append(f"无效的专业代码: {code}")
            details["invalid_codes"].append(code)
        else:
            code_info = PROFESSIONAL_CODES_INDEX[code]
            details["valid_codes"].append({
                "code": code,
                "name": code_info.name,
                "applicable_standards": code_info.applicable_standards
            })
            
            # 检查专业代码是否适用于所有指定的认证标准
            for std in request.standards:
                if std.upper() not in [s.upper() for s in code_info.applicable_standards]:
                    warnings.append(f"专业代码 {code} ({code_info.name}) 可能不适用于认证标准 {std}")
                    details["incompatible_codes"].append({
                        "code": code,
                        "standard": std
                    })
    
    # 特定组合验证规则
    # ISO45001 通常适用于所有行业，但某些高风险行业强烈建议
    high_risk_codes = ["02", "10", "11", "16", "17", "27"]
    if "ISO45001" not in [s.upper() for s in request.standards]:
        for code in request.professional_codes:
            code_prefix = code.split(".")[0]
            if code_prefix in high_risk_codes:
                warnings.append(f"专业代码 {code} 属于高风险行业，建议同时申请 ISO45001 职业健康安全管理体系认证")
                break
    
    # ISO14001 对于环境敏感行业
    env_sensitive_codes = ["02", "10", "11", "12", "15"]
    if "ISO14001" not in [s.upper() for s in request.standards]:
        for code in request.professional_codes:
            code_prefix = code.split(".")[0]
            if code_prefix in env_sensitive_codes:
                warnings.append(f"专业代码 {code} 属于环境敏感行业，建议同时申请 ISO14001 环境管理体系认证")
                break
    
    valid = len(errors) == 0
    
    return ValidateResult(
        valid=valid,
        errors=errors,
        warnings=warnings,
        details=details
    )


@router.get("/professional-codes/by-standard/{standard}", response_model=List[ProfessionalCode], summary="获取适用于指定标准的专业代码")
async def get_codes_by_standard(standard: str):
    """
    获取适用于指定认证标准的所有专业代码
    
    参数:
        standard: 认证标准代码 (ISO9001/ISO14001/ISO45001)
    """
    standard_upper = standard.upper()
    valid_standard_codes = [s.code.upper() for s in SUPPORTED_STANDARDS]
    
    if standard_upper not in valid_standard_codes:
        raise HTTPException(status_code=404, detail=f"未找到认证标准: {standard}")
    
    results = []
    for code in PROFESSIONAL_CODES_INDEX.values():
        if standard_upper in [s.upper() for s in code.applicable_standards]:
            results.append(code)
    
    # 按代码排序
    results.sort(key=lambda x: x.code)
    return results
