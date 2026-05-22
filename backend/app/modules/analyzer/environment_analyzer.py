#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 环境评估报告解析器
支持 ISO14001 环境评估报告自动解析
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class EnvironmentalAspect:
    """环境因素"""
    aspect_name: str
    activity: str
    environmental_impact: str
    significance: str  # 重要/一般
    control_measures: List[str] = field(default_factory=list)


@dataclass
class ComplianceItem:
    """合规性评价项"""
    regulation: str
    requirement: str
    compliance_status: str  # 合规/不合规/部分合规
    evidence: Optional[str] = None


@dataclass
class EnvironmentalAssessment:
    """环境评估报告"""
    company_name: str
    assessment_date: Optional[datetime] = None
    assessor: Optional[str] = None
    
    # 环境因素识别
    environmental_aspects: List[EnvironmentalAspect] = field(default_factory=list)
    
    # 重要环境因素
    significant_aspects: List[EnvironmentalAspect] = field(default_factory=list)
    
    # 合规性评价
    compliance_items: List[ComplianceItem] = field(default_factory=list)
    
    # 目标指标
    environmental_targets: List[Dict[str, Any]] = field(default_factory=list)
    
    # 管理方案
    management_programs: List[Dict[str, Any]] = field(default_factory=list)
    
    # 应急准备
    emergency_preparedness: List[str] = field(default_factory=list)


def parse_environmental_report(text: str) -> EnvironmentalAssessment:
    """
    解析环境评估报告文本
    
    Args:
        text: 环境评估报告全文
        
    Returns:
        EnvironmentalAssessment 对象
    """
    assessment = EnvironmentalAssessment(
        company_name=_extract_company_name(text)
    )
    
    # 解析环境因素
    assessment.environmental_aspects = _extract_environmental_aspects(text)
    
    # 识别重要因素
    assessment.significant_aspects = [
        a for a in assessment.environmental_aspects 
        if a.significance == "重要"
    ]
    
    # 解析合规性评价
    assessment.compliance_items = _extract_compliance_items(text)
    
    # 解析目标指标
    assessment.environmental_targets = _extract_environmental_targets(text)
    
    # 解析管理方案
    assessment.management_programs = _extract_management_programs(text)
    
    return assessment


def _extract_company_name(text: str) -> str:
    """提取公司名称"""
    patterns = [
        r'单位名称[：:]\s*(.+?)(?:\n|$)',
        r'企业名称[：:]\s*(.+?)(?:\n|$)',
        r'公司名称[：:]\s*(.+?)(?:\n|$)',
        r'受评单位[：:]\s*(.+?)(?:\n|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return ""


def _extract_environmental_aspects(text: str) -> List[EnvironmentalAspect]:
    """提取环境因素"""
    aspects = []
    
    # 查找环境因素表格或列表
    # 常见格式：活动/产品/服务 | 环境因素 | 环境影响 | 重要性
    
    # 尝试匹配表格格式
    table_pattern = r'(?:活动|产品/服务)[\s\|]*(?:环境因素)[\s\|]*(?:环境影响)[\s\|]*(?:重要性)'
    if re.search(table_pattern, text):
        # 提取表格行
        lines = text.split('\n')
        in_table = False
        for line in lines:
            if re.search(table_pattern, line):
                in_table = True
                continue
            if in_table and '|' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 4:
                    aspects.append(EnvironmentalAspect(
                        activity=parts[0],
                        aspect_name=parts[1],
                        environmental_impact=parts[2],
                        significance=parts[3],
                    ))
    
    # 如果没有匹配到表格，尝试从文本中提取
    if not aspects:
        # 查找环境因素列表
        aspect_patterns = [
            r'(?:废水|废气|噪声|固废|能耗|资源消耗)[：:]\s*(.+?)(?:\n|$)',
        ]
        for pattern in aspect_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                aspects.append(EnvironmentalAspect(
                    activity="日常运营",
                    aspect_name=match.strip(),
                    environmental_impact=_infer_impact(match),
                    significance="待评估",
                ))
    
    return aspects


def _infer_impact(aspect_name: str) -> str:
    """根据环境因素推断环境影响"""
    impact_map = {
        '废水': '水体污染',
        '废气': '大气污染',
        '噪声': '噪声污染',
        '固废': '土壤污染/资源消耗',
        '能耗': '能源消耗/温室气体',
        '资源': '资源消耗',
    }
    for key, value in impact_map.items():
        if key in aspect_name:
            return value
    return "待确定"


def _extract_compliance_items(text: str) -> List[ComplianceItem]:
    """提取合规性评价项"""
    items = []
    
    # 查找法规要求表格
    compliance_section = re.search(
        r'(?:合规性评价|法规要求|适用法规)[\s\S]*?(?=\n\n|\Z)',
        text
    )
    
    if compliance_section:
        section_text = compliance_section.group(0)
        # 尝试提取法规条目
        regulation_patterns = [
            r'(《[^》]+》)\s*[：:]\s*(.+?)(?:\n|$)',
            r'(中华人民共和国[^，。]+法)[\s\S]*?(?:符合|不符合)',
        ]
        for pattern in regulation_patterns:
            matches = re.findall(pattern, section_text)
            for match in matches:
                if isinstance(match, tuple):
                    reg, req = match
                else:
                    reg = match
                    req = "适用要求"
                
                # 判断合规状态
                status = "合规"
                if "不符合" in section_text or "违规" in section_text:
                    status = "不合规"
                elif "部分" in section_text:
                    status = "部分合规"
                
                items.append(ComplianceItem(
                    regulation=reg.strip(),
                    requirement=req.strip(),
                    compliance_status=status,
                ))
    
    return items


def _extract_environmental_targets(text: str) -> List[Dict[str, Any]]:
    """提取环境目标指标"""
    targets = []
    
    # 查找目标指标部分
    target_section = re.search(
        r'(?:环境目标|目标指标|环境指标)[\s\S]*?(?=\n\n|\Z)',
        text
    )
    
    if target_section:
        section_text = target_section.group(0)
        # 提取具体目标
        target_patterns = [
            r'(减少[^，。]+)(\d+%?)',
            r'(控制[^，。]+)(\d+%?)',
            r'(降低[^，。]+)(\d+%?)',
        ]
        for pattern in target_patterns:
            matches = re.findall(pattern, section_text)
            for match in matches:
                targets.append({
                    "target": match[0].strip(),
                    "indicator": match[1] if len(match) > 1 else "",
                    "deadline": None,
                })
    
    return targets


def _extract_management_programs(text: str) -> List[Dict[str, Any]]:
    """提取环境管理方案"""
    programs = []
    
    # 查找管理方案部分
    program_section = re.search(
        r'(?:管理方案|环境管理方案|实施方案)[\s\S]*?(?=\n\n|\Z)',
        text
    )
    
    if program_section:
        section_text = program_section.group(0)
        # 提取方案条目
        lines = section_text.split('\n')
        current_program = {}
        for line in lines:
            if '方案' in line or '措施' in line:
                if current_program:
                    programs.append(current_program)
                current_program = {"name": line.strip(), "measures": []}
            elif current_program and line.strip():
                current_program["measures"].append(line.strip())
        
        if current_program:
            programs.append(current_program)
    
    return programs


def generate_iso14001_documents(assessment: EnvironmentalAssessment) -> Dict[str, Any]:
    """
    根据环境评估报告生成 ISO14001 体系文件所需内容
    
    Returns:
        包含各类文件内容的字典
    """
    documents = {
        "environmental_policy": _generate_environmental_policy(assessment),
        "aspect_register": _generate_aspect_register(assessment),
        "legal_register": _generate_legal_register(assessment),
        "objectives_targets": _generate_objectives_targets(assessment),
        "management_programs": _generate_management_programs(assessment),
    }
    return documents


def _generate_environmental_policy(assessment: EnvironmentalAssessment) -> str:
    """生成环境方针"""
    aspects_summary = "、".join([a.aspect_name for a in assessment.significant_aspects[:3]])
    
    policy = f"""环境方针

{assessment.company_name}承诺：

1. 遵守环境保护法律法规及其他要求
2. 持续改进环境管理体系，预防污染
3. 针对重要环境因素（{aspects_summary}等）实施有效控制
4. 设定并实现环境目标和指标
5. 提高全员环境意识，鼓励员工参与

总经理：__________
日期：{datetime.now().strftime('%Y年%m月%d日')}
"""
    return policy


def _generate_aspect_register(assessment: EnvironmentalAssessment) -> Dict[str, Any]:
    """生成环境因素登记表"""
    return {
        "aspects_count": len(assessment.environmental_aspects),
        "significant_count": len(assessment.significant_aspects),
        "aspects": [
            {
                "activity": a.activity,
                "aspect": a.aspect_name,
                "impact": a.environmental_impact,
                "significance": a.significance,
            }
            for a in assessment.environmental_aspects
        ],
    }


def _generate_legal_register(assessment: EnvironmentalAssessment) -> Dict[str, Any]:
    """生成法律法规登记表"""
    return {
        "regulations_count": len(assessment.compliance_items),
        "compliance_rate": _calculate_compliance_rate(assessment.compliance_items),
        "items": [
            {
                "regulation": item.regulation,
                "requirement": item.requirement,
                "status": item.compliance_status,
            }
            for item in assessment.compliance_items
        ],
    }


def _calculate_compliance_rate(items: List[ComplianceItem]) -> float:
    """计算合规率"""
    if not items:
        return 100.0
    compliant = sum(1 for item in items if item.compliance_status == "合规")
    return round(compliant / len(items) * 100, 1)


def _generate_objectives_targets(assessment: EnvironmentalAssessment) -> List[Dict[str, Any]]:
    """生成目标指标"""
    return assessment.environmental_targets


def _generate_management_programs(assessment: EnvironmentalAssessment) -> List[Dict[str, Any]]:
    """生成管理方案"""
    return assessment.management_programs
