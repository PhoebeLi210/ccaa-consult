#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 职业健康安全评估解析器
支持 ISO45001 职业健康安全评估报告自动解析
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class Hazard:
    """危险源"""
    activity: str
    hazard_source: str
    risk_description: str
    likelihood: int  # 1-5
    severity: int    # 1-5
    risk_level: str  # 重大/较大/一般/低
    control_measures: List[str] = field(default_factory=list)


@dataclass
class Incident:
    """事故/事件记录"""
    date: Optional[datetime]
    type: str
    description: str
    injury: Optional[str]
    cause: Optional[str]
    corrective_action: Optional[str]


@dataclass
class SafetyAssessment:
    """职业健康安全评估报告"""
    company_name: str
    assessment_date: Optional[datetime] = None
    assessor: Optional[str] = None
    
    # 危险源识别
    hazards: List[Hazard] = field(default_factory=list)
    
    # 重大危险源
    significant_hazards: List[Hazard] = field(default_factory=list)
    
    # 事故记录
    incidents: List[Incident] = field(default_factory=list)
    
    # 法规合规
    legal_requirements: List[Dict[str, Any]] = field(default_factory=list)
    
    # 目标指标
    safety_targets: List[Dict[str, Any]] = field(default_factory=list)
    
    # 管理方案
    management_programs: List[Dict[str, Any]] = field(default_factory=list)
    
    # 应急准备
    emergency_procedures: List[str] = field(default_factory=list)


def parse_safety_assessment(text: str) -> SafetyAssessment:
    """
    解析职业健康安全评估报告
    
    Args:
        text: 安全评估报告全文
        
    Returns:
        SafetyAssessment 对象
    """
    assessment = SafetyAssessment(
        company_name=_extract_company_name(text)
    )
    
    # 解析危险源
    assessment.hazards = _extract_hazards(text)
    
    # 识别重大危险源
    assessment.significant_hazards = [
        h for h in assessment.hazards 
        if h.risk_level in ["重大", "较大"]
    ]
    
    # 解析事故记录
    assessment.incidents = _extract_incidents(text)
    
    # 解析法规要求
    assessment.legal_requirements = _extract_legal_requirements(text)
    
    # 解析目标指标
    assessment.safety_targets = _extract_safety_targets(text)
    
    # 解析应急程序
    assessment.emergency_procedures = _extract_emergency_procedures(text)
    
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


def _extract_hazards(text: str) -> List[Hazard]:
    """提取危险源"""
    hazards = []
    
    # 查找危险源识别表
    hazard_section = re.search(
        r'(?:危险源识别|危险源清单|风险识别)[\s\S]*?(?=\n\n|\Z)',
        text
    )
    
    if hazard_section:
        section_text = hazard_section.group(0)
        lines = section_text.split('\n')
        
        for line in lines:
            # 尝试匹配危险源条目
            # 格式：活动 | 危险源 | 风险描述 | 可能性 | 严重性 | 风险等级
            if '|' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 6:
                    try:
                        hazards.append(Hazard(
                            activity=parts[0],
                            hazard_source=parts[1],
                            risk_description=parts[2],
                            likelihood=int(parts[3]) if parts[3].isdigit() else 3,
                            severity=int(parts[4]) if parts[4].isdigit() else 3,
                            risk_level=parts[5],
                        ))
                    except (ValueError, IndexError):
                        continue
    
    # 如果没有匹配到表格，从文本中提取常见危险源
    if not hazards:
        common_hazards = [
            ("高空作业", "坠落", "人员坠落伤亡", 3, 5, "重大"),
            ("机械操作", "机械伤害", "肢体夹伤/切断", 3, 4, "较大"),
            ("电气作业", "触电", "电击伤亡", 2, 5, "重大"),
            ("化学品使用", "中毒", "化学品中毒", 2, 4, "较大"),
            ("火灾风险", "火灾", "人员伤亡/财产损失", 2, 5, "重大"),
            ("车辆运输", "交通事故", "人员伤亡", 3, 4, "较大"),
            ("噪声环境", "噪声", "听力损伤", 4, 2, "一般"),
            ("粉尘环境", "粉尘", "呼吸系统疾病", 4, 3, "一般"),
        ]
        
        for activity, hazard, risk, l, s, level in common_hazards:
            if activity in text or hazard in text:
                hazards.append(Hazard(
                    activity=activity,
                    hazard_source=hazard,
                    risk_description=risk,
                    likelihood=l,
                    severity=s,
                    risk_level=level,
                ))
    
    return hazards


def _extract_incidents(text: str) -> List[Incident]:
    """提取事故记录"""
    incidents = []
    
    # 查找事故记录部分
    incident_section = re.search(
        r'(?:事故记录|事件记录|事故统计)[\s\S]*?(?=\n\n|\Z)',
        text
    )
    
    if incident_section:
        section_text = incident_section.group(0)
        lines = section_text.split('\n')
        
        for line in lines:
            # 尝试匹配日期
            date_match = re.search(r'(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})', line)
            if date_match:
                try:
                    date = datetime(
                        int(date_match.group(1)),
                        int(date_match.group(2)),
                        int(date_match.group(3))
                    )
                except:
                    date = None
                
                # 提取事故类型和描述
                incident_type = _extract_incident_type(line)
                
                incidents.append(Incident(
                    date=date,
                    type=incident_type,
                    description=line.strip(),
                    injury=None,
                    cause=None,
                    corrective_action=None,
                ))
    
    return incidents


def _extract_incident_type(text: str) -> str:
    """提取事故类型"""
    incident_types = {
        "坠落": "高处坠落",
        "触电": "触电事故",
        "机械": "机械伤害",
        "车辆": "车辆伤害",
        "火灾": "火灾事故",
        "爆炸": "爆炸事故",
        "中毒": "中毒窒息",
        "物体": "物体打击",
    }
    
    for keyword, incident_type in incident_types.items():
        if keyword in text:
            return incident_type
    
    return "其他"


def _extract_legal_requirements(text: str) -> List[Dict[str, Any]]:
    """提取法规要求"""
    requirements = []
    
    # 常见职业健康安全法规
    common_regulations = [
        "中华人民共和国安全生产法",
        "中华人民共和国职业病防治法",
        "工伤保险条例",
        "生产安全事故报告和调查处理条例",
        "工作场所职业卫生管理规定",
    ]
    
    for regulation in common_regulations:
        if regulation in text:
            # 判断合规状态
            status = "合规"
            if "不符合" in text or "违规" in text:
                status = "不合规"
            
            requirements.append({
                "regulation": regulation,
                "status": status,
                "applicability": "适用",
            })
    
    return requirements


def _extract_safety_targets(text: str) -> List[Dict[str, Any]]:
    """提取安全目标指标"""
    targets = []
    
    # 查找目标部分
    target_section = re.search(
        r'(?:安全目标|目标指标|职业健康安全目标)[\s\S]*?(?=\n\n|\Z)',
        text
    )
    
    if target_section:
        section_text = target_section.group(0)
        
        # 常见安全目标模式
        target_patterns = [
            (r'重伤.*?事故.*?[：:]\s*(\d+|[零0])', "重伤事故", "起/年"),
            (r'死亡.*?事故.*?[：:]\s*(\d+|[零0])', "死亡事故", "起/年"),
            (r'轻伤.*?事故.*?[：:]\s*(\d+|[零0])', "轻伤事故", "起/年"),
            (r'职业病.*?[：:]\s*(\d+|[零0])', "职业病", "例/年"),
            (r'培训.*?覆盖率.*?[：:]\s*(\d+%?)', "安全培训覆盖率", "%"),
        ]
        
        for pattern, name, unit in target_patterns:
            match = re.search(pattern, section_text)
            if match:
                targets.append({
                    "name": name,
                    "target": match.group(1),
                    "unit": unit,
                })
    
    return targets


def _extract_emergency_procedures(text: str) -> List[str]:
    """提取应急程序"""
    procedures = []
    
    # 查找应急准备部分
    emergency_section = re.search(
        r'(?:应急准备|应急响应|应急预案)[\s\S]*?(?=\n\n|\Z)',
        text
    )
    
    if emergency_section:
        section_text = emergency_section.group(0)
        
        # 常见应急程序
        common_procedures = [
            "火灾应急响应",
            "化学品泄漏应急",
            "人员伤亡应急",
            "自然灾害应急",
            "设备故障应急",
        ]
        
        for procedure in common_procedures:
            if procedure.replace("应急", "") in section_text:
                procedures.append(procedure)
    
    return procedures


def generate_iso45001_documents(assessment: SafetyAssessment) -> Dict[str, Any]:
    """
    根据安全评估报告生成 ISO45001 体系文件所需内容
    
    Returns:
        包含各类文件内容的字典
    """
    documents = {
        "safety_policy": _generate_safety_policy(assessment),
        "hazard_register": _generate_hazard_register(assessment),
        "legal_register": _generate_legal_register(assessment),
        "objectives_targets": _generate_objectives_targets(assessment),
        "emergency_plan": _generate_emergency_plan(assessment),
        "incident_analysis": _generate_incident_analysis(assessment),
    }
    return documents


def _generate_safety_policy(assessment: SafetyAssessment) -> str:
    """生成职业健康安全方针"""
    hazards_summary = "、".join([h.hazard_source for h in assessment.significant_hazards[:3]])
    
    policy = f"""职业健康安全方针

{assessment.company_name}承诺：

1. 遵守职业健康安全法律法规及其他要求
2. 持续改进职业健康安全管理体系绩效
3. 针对重大危险源（{hazards_summary}等）实施有效控制
4. 预防工伤事故和职业病的发生
5. 提高全员安全意识，鼓励员工参与
6. 提供安全健康的工作环境

总经理：__________
日期：{datetime.now().strftime('%Y年%m月%d日')}
"""
    return policy


def _generate_hazard_register(assessment: SafetyAssessment) -> Dict[str, Any]:
    """生成危险源登记表"""
    return {
        "hazards_count": len(assessment.hazards),
        "significant_count": len(assessment.significant_hazards),
        "hazards": [
            {
                "activity": h.activity,
                "hazard_source": h.hazard_source,
                "risk_description": h.risk_description,
                "risk_score": h.likelihood * h.severity,
                "risk_level": h.risk_level,
            }
            for h in assessment.hazards
        ],
    }


def _generate_legal_register(assessment: SafetyAssessment) -> Dict[str, Any]:
    """生成法律法规登记表"""
    return {
        "regulations_count": len(assessment.legal_requirements),
        "compliance_rate": _calculate_compliance_rate(assessment.legal_requirements),
        "items": assessment.legal_requirements,
    }


def _calculate_compliance_rate(items: List[Dict[str, Any]]) -> float:
    """计算合规率"""
    if not items:
        return 100.0
    compliant = sum(1 for item in items if item.get("status") == "合规")
    return round(compliant / len(items) * 100, 1)


def _generate_objectives_targets(assessment: SafetyAssessment) -> List[Dict[str, Any]]:
    """生成目标指标"""
    return assessment.safety_targets


def _generate_emergency_plan(assessment: SafetyAssessment) -> Dict[str, Any]:
    """生成应急预案框架"""
    return {
        "emergency_procedures": assessment.emergency_procedures,
        "suggested_procedures": [
            "火灾应急响应程序",
            "人员伤亡应急响应程序",
            "化学品泄漏应急响应程序",
        ] if not assessment.emergency_procedures else [],
    }


def _generate_incident_analysis(assessment: SafetyAssessment) -> Dict[str, Any]:
    """生成事故分析报告"""
    incident_types = {}
    for incident in assessment.incidents:
        incident_type = incident.type
        if incident_type not in incident_types:
            incident_types[incident_type] = 0
        incident_types[incident_type] += 1
    
    return {
        "total_incidents": len(assessment.incidents),
        "incident_types": incident_types,
        "trend": "需分析趋势",
        "recommendations": [
            "加强安全培训",
            "完善防护措施",
            "定期安全检查",
        ],
    }
