#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 自然语言解析API
使用LLM从用户自然语言描述中提取企业信息
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import json
import re

from app.core.config import settings
from app.modules.generator.llm_client import LLMService, LLMConfig, create_llm_service

router = APIRouter(prefix="/parse", tags=["自然语言解析"])


# ============ 请求/响应模型 ============

class ParseRequest(BaseModel):
    """解析请求"""
    text: str = Field(..., description="用户输入的自然语言文本")
    use_llm: bool = Field(True, description="是否使用LLM解析")


class ParsedCompanyInfo(BaseModel):
    """解析出的企业信息"""
    company_name: Optional[str] = Field(None, description="公司名称")
    industry: Optional[str] = Field(None, description="行业")
    industry_code: Optional[str] = Field(None, description="行业代码")
    employee_count: Optional[int] = Field(None, description="员工人数")
    office_area: Optional[float] = Field(None, description="办公面积")
    address: Optional[str] = Field(None, description="地址")
    legal_representative: Optional[str] = Field(None, description="法定代表人")
    contact_person: Optional[str] = Field(None, description="联系人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    main_business: Optional[str] = Field(None, description="主营业务")
    target_standards: Optional[List[str]] = Field(None, description="目标认证标准")
    certification_type: Optional[str] = Field(None, description="认证类型")


class ParseResponse(BaseModel):
    """解析响应"""
    success: bool
    parsed_info: ParsedCompanyInfo
    raw_text: str
    confidence: float = Field(0.0, description="解析置信度")
    missing_fields: List[str] = Field(default_factory=list, description="缺失字段")


# ============ 行业代码映射 ============

INDUSTRY_CODE_MAP = {
    # 智能科技
    "智能科技": "intelligent_technology",
    "智能": "intelligent_technology",
    "人工智能": "intelligent_technology",
    "AI": "intelligent_technology",
    
    # 软件开发
    "软件开发": "software_development",
    "软件": "software_development",
    "IT": "software_development",
    "信息技术": "software_development",
    "互联网": "software_development",
    "程序": "software_development",
    "代码": "software_development",
    
    # 软件销售
    "软件销售": "software_sales",
    "销售": "software_sales",
    "教育科技": "software_sales",
    "教育": "software_sales",
    
    # 机电设备
    "机电设备": "electromechanical_equipment",
    "机电": "electromechanical_equipment",
    "设备": "electromechanical_equipment",
    "机械": "electromechanical_equipment",
    
    # 物业服务
    "物业": "property_service",
    "物业管理": "property_service",
    "物业服务": "property_service",
    
    # 环保科技
    "环保": "environmental_technology",
    "环境": "environmental_technology",
    "环保科技": "environmental_technology",
    "环保技术": "environmental_technology",
    
    # 档案服务
    "档案": "archive_service",
    "档案整理": "archive_service",
    "档案数字化": "archive_service",
    "档案服务": "archive_service",
}


# ============ LLM解析提示词 ============

SYSTEM_PROMPT = """你是一个企业信息提取专家，专门从用户的自然语言描述中提取企业信息。

请从用户输入中提取以下信息（如果存在）：
1. company_name: 公司名称
2. industry: 行业类型（如：软件开发、物业服务、环保科技、档案服务等）
3. employee_count: 员工人数（数字）
4. office_area: 办公面积（数字，单位平方米）
5. address: 公司地址
6. legal_representative: 法定代表人
7. contact_person: 联系人
8. contact_phone: 联系电话
9. main_business: 主营业务
10. target_standards: 目标认证标准（如ISO9001、ISO14001、ISO45001）
11. certification_type: 认证类型（初次认证/监督审核/再认证）

请以JSON格式输出，不要包含其他内容。如果某项信息未提及，则设为null。"""

USER_PROMPT_TEMPLATE = """请从以下文本中提取企业信息：

{text}

请以JSON格式输出提取结果。"""


# ============ API路由 ============

@router.post("", response_model=ParseResponse, summary="解析企业信息")
async def parse_company_info(request: ParseRequest):
    """兼容前端 /v1/parse 路径调用"""
    return await _parse_company(request)


@router.post("/company", response_model=ParseResponse, summary="解析企业信息")
async def parse_company_info_via_company(request: ParseRequest):
    return await _parse_company(request)


async def _parse_company(request: ParseRequest):
    """
    从自然语言文本中解析企业信息
    
    支持两种解析方式：
    1. LLM解析：使用DeepSeek等大模型进行智能解析
    2. 规则解析：使用正则表达式进行基础解析
    """
    text = request.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="输入文本不能为空")
    
    # 尝试LLM解析
    if request.use_llm and settings.LLM_API_KEY:
        try:
            parsed_info = await parse_with_llm(text)
            confidence = 0.9
        except Exception as e:
            print(f"LLM解析失败: {e}")
            # 回退到规则解析
            parsed_info = parse_with_rules(text)
            confidence = 0.6
    else:
        # 使用规则解析
        parsed_info = parse_with_rules(text)
        confidence = 0.6
    
    # 计算缺失字段
    missing_fields = []
    for field, value in parsed_info.items():
        if value is None:
            missing_fields.append(field)
    
    return ParseResponse(
        success=True,
        parsed_info=ParsedCompanyInfo(**parsed_info),
        raw_text=text,
        confidence=confidence,
        missing_fields=missing_fields,
    )


@router.post("/company/stream", summary="流式解析企业信息")
async def parse_company_info_stream(request: ParseRequest):
    """
    流式解析企业信息（实时返回解析过程）
    """
    from fastapi.responses import StreamingResponse
    import json
    
    text = request.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="输入文本不能为空")
    
    async def generate():
        # 先返回原始文本
        yield f"data: {json.dumps({'type': 'text', 'content': text})}\n\n"
        
        # 解析中
        yield f"data: {json.dumps({'type': 'status', 'content': '正在解析...'})}\n\n"
        
        try:
            if settings.LLM_API_KEY:
                # 使用LLM流式解析
                llm_service = get_llm_service()
                
                full_response = ""
                async for chunk in llm_service.generate_stream(
                    USER_PROMPT_TEMPLATE.format(text=text),
                    system_prompt=SYSTEM_PROMPT
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                
                # 解析JSON
                try:
                    if "```json" in full_response:
                        full_response = full_response.split("```json")[1].split("```")[0]
                    elif "```" in full_response:
                        full_response = full_response.split("```")[1].split("```")[0]
                    
                    parsed = json.loads(full_response.strip())
                    yield f"data: {json.dumps({'type': 'result', 'content': parsed})}\n\n"
                except json.JSONDecodeError:
                    yield f"data: {json.dumps({'type': 'error', 'content': 'JSON解析失败'})}\n\n"
                
                await llm_service.close()
            else:
                # 使用规则解析
                parsed = parse_with_rules(text)
                yield f"data: {json.dumps({'type': 'result', 'content': parsed})}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


# ============ 辅助函数 ============

def get_llm_service() -> LLMService:
    """获取LLM服务实例"""
    config = LLMConfig(
        provider=settings.LLM_PROVIDER,
        api_key=settings.LLM_API_KEY,
        api_url=settings.LLM_API_URL,
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
    )
    return LLMService(config)


async def parse_with_llm(text: str) -> Dict[str, Any]:
    """使用LLM解析企业信息"""
    llm_service = get_llm_service()
    
    try:
        result = await llm_service.generate_json(
            USER_PROMPT_TEMPLATE.format(text=text),
            system_prompt=SYSTEM_PROMPT
        )
        
        # 处理行业代码
        if result.get("industry"):
            result["industry_code"] = get_industry_code(result["industry"])
        
        return result
    
    finally:
        await llm_service.close()


def parse_with_rules(text: str) -> Dict[str, Any]:
    """使用规则解析企业信息"""
    result = {}
    
    # 提取公司名称
    company_patterns = [
        r"([^，。！？,]+?(?:有限公司|股份有限公司|集团|公司))",
        r"公司[名称：:]*([^，。！？,\n]+)",
    ]
    for pattern in company_patterns:
        match = re.search(pattern, text)
        if match:
            result["company_name"] = match.group(1).strip()
            break
    
    # 提取员工人数
    employee_patterns = [
        r"员工[人数]*[：:]*?(\d+)[人名]?",
        r"(\d+)[人名]?员工",
        r"现有员工(\d+)人",
    ]
    for pattern in employee_patterns:
        match = re.search(pattern, text)
        if match:
            result["employee_count"] = int(match.group(1))
            break
    
    # 提取办公面积
    area_patterns = [
        r"办公面积[：:]*?(\d+(?:\.\d+)?)\s*平方米",
        r"(\d+(?:\.\d+)?)\s*平[方]?米",
        r"面积[：:]*?(\d+(?:\.\d+)?)",
    ]
    for pattern in area_patterns:
        match = re.search(pattern, text)
        if match:
            result["office_area"] = float(match.group(1))
            break
    
    # 提取地址
    address_patterns = [
        r"地址[：:]*?([^，。！？,\n]+)",
        r"位于([^，。！？,\n]+)",
    ]
    for pattern in address_patterns:
        match = re.search(pattern, text)
        if match:
            result["address"] = match.group(1).strip()
            break
    
    # 提取联系电话
    phone_match = re.search(r"(?:电话|联系)[：:]*?(\d{3,4}[-\s]?\d{7,8}|\d{11})", text)
    if phone_match:
        result["contact_phone"] = phone_match.group(1)
    
    # 提取联系人
    contact_match = re.search(r"联系人[：:]*?([^，。！？,\n]+)", text)
    if contact_match:
        result["contact_person"] = contact_match.group(1).strip()
    
    # 提取法定代表人
    legal_match = re.search(r"(?:法定代表人|法人)[：:]*?([^，。！？,\n]+)", text)
    if legal_match:
        result["legal_representative"] = legal_match.group(1).strip()
    
    # 提取行业
    for keyword, code in INDUSTRY_CODE_MAP.items():
        if keyword in text:
            result["industry"] = keyword
            result["industry_code"] = code
            break
    
    # 提取认证标准
    standards = []
    if "ISO9001" in text or "质量" in text:
        standards.append("ISO9001")
    if "ISO14001" in text or "环境" in text:
        standards.append("ISO14001")
    if "ISO45001" in text or "安全" in text or "职业健康" in text:
        standards.append("ISO45001")
    if standards:
        result["target_standards"] = standards
    
    # 提取认证类型
    if "监督审核" in text:
        result["certification_type"] = "监督审核"
    elif "再认证" in text or "复评" in text:
        result["certification_type"] = "再认证"
    else:
        result["certification_type"] = "初次认证"
    
    return result


def get_industry_code(industry_name: str) -> str:
    """根据行业名称获取行业代码"""
    for keyword, code in INDUSTRY_CODE_MAP.items():
        if keyword in industry_name:
            return code
    return "other"


# ============ 测试 ============

if __name__ == "__main__":
    import asyncio
    
    async def test():
        test_text = """
        武汉鑫辰宇物业服务有限公司，位于武汉市江汉区，员工50人，办公面积200平方米。
        法定代表人张三，联系人李四，电话13800138000。
        主要从事物业管理服务，需要办理ISO9001、ISO14001、ISO45001三体系认证。
        """
        
        result = await parse_with_llm(test_text)
        print(f"LLM解析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        result2 = parse_with_rules(test_text)
        print(f"规则解析结果: {json.dumps(result2, ensure_ascii=False, indent=2)}")
    
    asyncio.run(test())
