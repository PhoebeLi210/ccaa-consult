#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 自然语言解析器

核心功能：
1. 从用户自然语言描述中提取企业信息
2. 支持多轮对话补充缺失信息
3. 与文件上传信息融合
"""

import re
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class IndustryType(Enum):
    """行业类型"""
    MANUFACTURING = "制造业"
    CONSTRUCTION = "建筑业"
    SERVICE = "服务业"
    TRADE = "贸易"
    IT = "IT"
    MEDICAL = "医疗"
    PROPERTY = "物业"
    OTHER = "其他"


class CertificationType(Enum):
    """认证类型"""
    INITIAL = "初次认证"
    SURVEILLANCE = "监督审核"
    RE_CERTIFICATION = "再认证"


class StandardType(Enum):
    """标准类型"""
    ISO9001 = "ISO9001"
    ISO14001 = "ISO14001"
    ISO45001 = "ISO45001"


@dataclass
class CompanyInfo:
    """企业信息结构"""
    company_name: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    employee_count: Optional[int] = None
    office_area_sqm: Optional[float] = None
    main_equipment: List[str] = field(default_factory=list)
    main_processes: List[str] = field(default_factory=list)
    departments: List[str] = field(default_factory=list)
    certification_type: Optional[str] = None
    existing_standards: List[str] = field(default_factory=list)
    target_standards: List[str] = field(default_factory=list)
    quality_goals: Optional[str] = None
    key_customers: Optional[str] = None
    special_processes: List[str] = field(default_factory=list)
    raw_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def get_missing_fields(self) -> List[str]:
        """获取缺失的关键字段"""
        missing = []
        if not self.company_name:
            missing.append("company_name")
        if not self.industry:
            missing.append("industry")
        if not self.employee_count:
            missing.append("employee_count")
        if not self.departments:
            missing.append("departments")
        if not self.quality_goals:
            missing.append("quality_goals")
        return missing


class NaturalLanguageParser:
    """自然语言解析器"""

    # 行业关键词映射
    INDUSTRY_KEYWORDS = {
        IndustryType.MANUFACTURING: ["制造", "生产", "加工", "工厂", "注塑", "焊接", "喷涂", "装配"],
        IndustryType.CONSTRUCTION: ["建筑", "施工", "工程", "装修", "市政"],
        IndustryType.SERVICE: ["服务", "咨询", "物业", "保洁", "餐饮"],
        IndustryType.TRADE: ["贸易", "销售", "批发", "零售", "经销"],
        IndustryType.IT: ["软件", "IT", "互联网", "科技", "信息"],
        IndustryType.MEDICAL: ["医疗", "医院", "诊所", "制药", "器械"],
        IndustryType.PROPERTY: ["物业", "房地产", "小区", "写字楼"],
    }

    # 设备关键词
    EQUIPMENT_PATTERNS = [
        r"(\w+机)\s*(\d+)\s*台",
        r"(\w+设备)\s*(\d+)\s*(台|套)",
        r"(\w+线)\s*(\d+)\s*条",
        r"电脑\s*(\d+)\s*台",
        r"(\w+)\s*(\d+)\s*台",
    ]

    # 面积模式
    AREA_PATTERN = r"(\d+(?:\.\d+)?)\s*(?:平米|平方米|㎡|平方)"

    # 人数模式
    EMPLOYEE_PATTERNS = [
        r"员工\s*(\d+)\s*人",
        r"(\d+)\s*名员工",
        r"(\d+)\s*人",
        r"职工\s*(\d+)\s*人",
    ]

    # 认证类型关键词
    CERT_TYPE_KEYWORDS = {
        CertificationType.INITIAL: ["初次认证", "首次认证", "新申请", "初次"],
        CertificationType.SURVEILLANCE: ["监督审核", "监督", "年审", "复审"],
        CertificationType.RE_CERTIFICATION: ["再认证", "复评", "换证"],
    }

    # 标准关键词
    STANDARD_KEYWORDS = {
        StandardType.ISO9001: ["ISO9001", "9001", "质量管理体系", "质量管理"],
        StandardType.ISO14001: ["ISO14001", "14001", "环境管理体系", "环境管理"],
        StandardType.ISO45001: ["ISO45001", "45001", "职业健康安全", "OHSAS18001"],
    }

    def __init__(self, llm_client=None):
        """
        初始化解析器

        Args:
            llm_client: 大模型客户端（可选，用于高级解析）
        """
        self.llm_client = llm_client

    def parse(self, free_text: str) -> CompanyInfo:
        """
        解析自然语言文本

        Args:
            free_text: 用户输入的自然语言描述

        Returns:
            CompanyInfo: 提取的企业信息
        """
        info = CompanyInfo(raw_text=free_text)

        # 1. 提取行业
        info.industry = self._extract_industry(free_text)

        # 2. 提取员工人数
        info.employee_count = self._extract_employee_count(free_text)

        # 3. 提取办公面积
        info.office_area_sqm = self._extract_area(free_text)

        # 4. 提取设备
        info.main_equipment = self._extract_equipment(free_text)

        # 5. 提取部门
        info.departments = self._extract_departments(free_text)

        # 6. 提取认证类型
        info.certification_type = self._extract_certification_type(free_text)

        # 7. 提取已有标准
        info.existing_standards = self._extract_standards(free_text, existing=True)

        # 8. 提取目标标准
        info.target_standards = self._extract_standards(free_text, existing=False)

        # 9. 提取主要过程
        info.main_processes = self._extract_processes(free_text)

        # 10. 提取公司名称（如果有）
        info.company_name = self._extract_company_name(free_text)

        return info

    def _extract_industry(self, text: str) -> Optional[str]:
        """提取行业"""
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return industry.value
        return None

    def _extract_employee_count(self, text: str) -> Optional[int]:
        """提取员工人数"""
        for pattern in self.EMPLOYEE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return None

    def _extract_area(self, text: str) -> Optional[float]:
        """提取面积"""
        match = re.search(self.AREA_PATTERN, text)
        if match:
            return float(match.group(1))
        return None

    def _extract_equipment(self, text: str) -> List[str]:
        """提取设备列表"""
        equipment = []
        for pattern in self.EQUIPMENT_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    equip_name = match[0]
                    equip_count = match[1] if len(match) > 1 else ""
                    equipment.append(f"{equip_name}{equip_count}台")
        return equipment

    def _extract_departments(self, text: str) -> List[str]:
        """提取部门列表"""
        departments = []
        # 常见部门关键词
        dept_keywords = ["部", "室", "科", "组", "中心"]
        dept_names = re.findall(r"(\w+(?:{}))".format("|".join(dept_keywords)), text)
        departments.extend(dept_names)
        return list(set(departments))

    def _extract_certification_type(self, text: str) -> Optional[str]:
        """提取认证类型"""
        for cert_type, keywords in self.CERT_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return cert_type.value
        # 默认为初次认证
        return CertificationType.INITIAL.value

    def _extract_standards(self, text: str, existing: bool = True) -> List[str]:
        """提取标准列表"""
        standards = []

        for standard, keywords in self.STANDARD_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    if existing and ("已通过" in text or "已有" in text):
                        standards.append(standard.value)
                    elif not existing and ("申请" in text or "要做" in text or "需要" in text):
                        standards.append(standard.value)
                    elif not existing and not standards:
                        # 如果没有明确说明，默认目标标准
                        standards.append(standard.value)
        return list(set(standards))

    def _extract_processes(self, text: str) -> List[str]:
        """提取主要过程"""
        processes = []
        # 查找"主要过程"、"生产过程"等关键词后的内容
        process_patterns = [
            r"主要过程[是为：:]+\s*([^。，]+)",
            r"生产过程[是为：:]+\s*([^。，]+)",
            r"工艺流程[是为：:]+\s*([^。，]+)",
        ]
        for pattern in process_patterns:
            match = re.search(pattern, text)
            if match:
                process_text = match.group(1)
                # 按顿号、逗号分割
                processes.extend(re.split(r"[、，,]", process_text))

        # 也提取常见的工艺动词
        process_verbs = re.findall(r"(\w{2,4})(?:、|，|,)", text)
        common_processes = ["注塑", "焊接", "喷涂", "组装", "质检", "包装", "切割", "冲压"]
        for verb in process_verbs:
            if verb in common_processes:
                processes.append(verb)

        return list(set(processes))

    def _extract_company_name(self, text: str) -> Optional[str]:
        """提取公司名称"""
        # 匹配"XX公司"、"XX有限公司"等
        patterns = [
            r"([\u4e00-\u9fa5]{2,20}(?:公司|有限公司|有限责任公司))",
            r"我(?:公司|单位)[是为：:]+\s*([\u4e00-\u9fa5]{2,20})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def generate_follow_up_questions(self, info: CompanyInfo) -> List[Dict[str, str]]:
        """
        生成追问问题

        Args:
            info: 已提取的企业信息

        Returns:
            追问问题列表
        """
        questions = []
        missing_fields = info.get_missing_fields()

        question_templates = {
            "company_name": {
                "question": "请问您的客户公司名称是什么？",
                "example": "例如：XX塑料制品有限公司",
                "field": "company_name"
            },
            "quality_goals": {
                "question": "请问企业的质量目标是什么？",
                "example": "例如：产品合格率≥98%，客户满意度≥95%",
                "field": "quality_goals"
            },
            "employee_count": {
                "question": "请问企业有多少员工？",
                "example": "例如：50人",
                "field": "employee_count"
            },
            "departments": {
                "question": "请问企业有哪些部门？",
                "example": "例如：品质部、生产部、销售部",
                "field": "departments"
            },
            "industry": {
                "question": "请问企业属于哪个行业？",
                "example": "例如：制造业、建筑业、服务业",
                "field": "industry"
            }
        }

        for field in missing_fields:
            if field in question_templates:
                questions.append(question_templates[field])

        # 特殊过程追问
        if not info.special_processes and info.industry == IndustryType.MANUFACTURING.value:
            questions.append({
                "question": "是否有特殊过程需要特别管控？",
                "example": "例如：焊接、热处理、喷涂等",
                "field": "special_processes"
            })

        return questions

    def update_with_answer(self, info: CompanyInfo, field: str, answer: str) -> CompanyInfo:
        """
        根据用户回答更新信息

        Args:
            info: 原有企业信息
            field: 字段名
            answer: 用户回答

        Returns:
            更新后的企业信息
        """
        if field == "company_name":
            info.company_name = answer
        elif field == "quality_goals":
            info.quality_goals = answer
        elif field == "employee_count":
            # 尝试提取数字
            match = re.search(r"(\d+)", answer)
            if match:
                info.employee_count = int(match.group(1))
        elif field == "departments":
            info.departments = re.split(r"[、，,]", answer)
        elif field == "industry":
            info.industry = answer
        elif field == "special_processes":
            info.special_processes = re.split(r"[、，,]", answer)

        return info

    def merge_with_file_data(self, info: CompanyInfo, file_data: Dict[str, Any]) -> CompanyInfo:
        """
        与文件上传数据融合

        Args:
            info: 自然语言提取的信息
            file_data: 文件解析的信息

        Returns:
            合并后的企业信息
        """
        info_dict = info.to_dict()

        for key, value in file_data.items():
            if value is not None and value != [] and value != "":
                # 文件数据优先
                info_dict[key] = value

        return CompanyInfo(**info_dict)


class LLMParser(NaturalLanguageParser):
    """基于大模型的解析器（增强版）"""

    SYSTEM_PROMPT = """你是一个ISO体系咨询助手。请从用户描述中提取企业信息，输出JSON格式。

需要提取的字段：
- company_name: 公司名称（如果有）
- industry: 行业（从制造业、建筑业、服务业、贸易、IT、医疗、物业等选择）
- sub_industry: 细分行业
- employee_count: 员工人数（数字）
- office_area_sqm: 办公面积（数字）
- main_equipment: 主要设备/资产（数组）
- main_processes: 主要生产过程（数组）
- departments: 组织部门（数组）
- certification_type: 认证类型（初次认证/监督审核/再认证）
- existing_standards: 已通过的标准（数组，如ISO9001、ISO14001、ISO45001）
- target_standards: 目标标准（数组）
- quality_goals: 质量目标
- special_processes: 特殊过程（数组）

如果某个字段无法提取，设为null。不要编造。只输出JSON，不要其他内容。"""

    def __init__(self, llm_client):
        super().__init__(llm_client)
        self.llm_client = llm_client

    async def parse_with_llm(self, free_text: str) -> CompanyInfo:
        """
        使用大模型解析

        Args:
            free_text: 用户输入的自然语言描述

        Returns:
            CompanyInfo: 提取的企业信息
        """
        # 先用规则解析
        info = self.parse(free_text)

        # 如果有大模型客户端，进行增强解析
        if self.llm_client:
            try:
                response = await self.llm_client.chat(
                    system_prompt=self.SYSTEM_PROMPT,
                    user_message=free_text
                )

                # 解析JSON响应
                llm_result = json.loads(response)

                # 合并结果
                for key, value in llm_result.items():
                    if value is not None and value != [] and value != "":
                        setattr(info, key, value)
            except Exception as e:
                print(f"LLM解析失败，使用规则解析结果: {e}")

        return info


# 便捷函数
def parse_company_info(free_text: str) -> CompanyInfo:
    """
    解析企业信息的便捷函数

    Args:
        free_text: 用户输入的自然语言描述

    Returns:
        CompanyInfo: 提取的企业信息
    """
    parser = NaturalLanguageParser()
    return parser.parse(free_text)


# 测试代码
if __name__ == "__main__":
    # 测试用例
    test_text = """
    我公司是一家生产塑料制品的制造企业，员工50人，办公室面积300平米，
    有注塑机5台，电脑20台，去年通过ISO9001认证，今年要做监督审核。
    主要产品为塑料包装盒，生产过程有注塑、修边、质检。
    公司有独立的品质部和生产部。
    """

    parser = NaturalLanguageParser()
    info = parser.parse(test_text)

    print("=" * 60)
    print("提取的企业信息：")
    print("=" * 60)
    for key, value in info.to_dict().items():
        if value and value != [] and value != "":
            print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("缺失字段：")
    print("=" * 60)
    for field in info.get_missing_fields():
        print(f"  - {field}")

    print("\n" + "=" * 60)
    print("追问问题：")
    print("=" * 60)
    questions = parser.generate_follow_up_questions(info)
    for q in questions:
        print(f"  Q: {q['question']}")
        print(f"     示例: {q['example']}")
        print()
