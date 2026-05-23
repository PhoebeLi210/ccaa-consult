"""
防编造验证模块
用于检测和验证文档内容是否存在编造、套用模板等问题
"""

import re
import logging
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "low"           # 低风险 - 内容可信
    MEDIUM = "medium"     # 中风险 - 需要关注
    HIGH = "high"         # 高风险 - 疑似编造
    CRITICAL = "critical" # 严重风险 - 明显编造


@dataclass
class ValidationResult:
    """验证结果数据类"""
    is_valid: bool
    risk_level: RiskLevel
    message: str
    details: List[str]
    suggestions: List[str]
    # 新增字段
    field_name: str = ""  # 字段名称
    field_value: str = ""  # 字段值
    source: str = ""  # 信息来源 (P1/P2/P3)
    needs_verification: bool = False  # 是否需要人工验证
    verification_reason: str = ""  # 需要验证的原因


class AntiFabricationValidator:
    """防编造验证器类"""

    # 通用套话关键词列表（25个）
    GENERIC_PHRASES = [
        "持续改进",
        "客户满意",
        "质量第一",
        "顾客至上",
        "精益求精",
        "追求卓越",
        "以人为本",
        "科学管理",
        "诚信经营",
        "创新发展",
        "质量为本",
        "信誉至上",
        "用户至上",
        "服务至上",
        "品质卓越",
        "管理规范",
        "技术先进",
        "设备精良",
        "检测完善",
        "体系健全",
        "全员参与",
        "过程控制",
        "预防为主",
        "数据说话",
        "持续创新"
    ]

    # 模糊人员名称关键词（15个）
    VAGUE_PERSON_KEYWORDS = [
        "负责人",
        "相关人员",
        "有关人员",
        "相关人员员",
        "主管人员",
        "管理人员",
        "技术人员",
        "操作人员",
        "检验人员",
        "质量人员",
        "部门人员",
        "岗位人员",
        "专职人员",
        "兼职人员",
        "指定人员"
    ]

    # 标准部门列表（30个）
    STANDARD_DEPARTMENTS = [
        "总经理办公室",
        "综合管理部",
        "质量管理部",
        "质量控制部",
        "质量保证部",
        "生产管理部",
        "生产制造部",
        "生产技术部",
        "技术研发部",
        "技术部",
        "研发部",
        "采购部",
        "供应链管理部",
        "物流部",
        "仓储部",
        "销售部",
        "市场部",
        "客户服务部",
        "售后服务部",
        "人力资源部",
        "行政部",
        "财务部",
        "审计部",
        "设备管理部",
        "设备部",
        "安全环保部",
        "安环部",
        "信息部",
        "IT部",
        "项目管理部"
    ]

    # 文件编号格式正则表达式
    DOCUMENT_NUMBER_PATTERNS = [
        # XXX-QESMS-A-001 格式
        r'^[A-Z]{2,5}-QESMS-[A-Z]-\d{3,4}$',
        # XXX-ISO-001 格式
        r'^[A-Z]{2,5}-ISO-\d{3,4}$',
        # XXX-QM-001 格式（质量管理）
        r'^[A-Z]{2,5}-QM-\d{3,4}$',
        # XXX-EM-001 格式（环境管理）
        r'^[A-Z]{2,5}-EM-\d{3,4}$',
        # XXX-SM-001 格式（安全管理）
        r'^[A-Z]{2,5}-SM-\d{3,4}$',
        # 通用格式：部门代码-类别-序号
        r'^[A-Z]{2,4}-[A-Z]{1,3}-\d{3,4}$'
    ]

    def __init__(self):
        """初始化验证器"""
        self.validation_history: List[ValidationResult] = []

    def validate_quality_policy(self, policy_text: str) -> ValidationResult:
        """
        验证质量方针是否为通用套话

        Args:
            policy_text: 质量方针文本

        Returns:
            ValidationResult: 验证结果
        """
        if not policy_text or not isinstance(policy_text, str):
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.CRITICAL,
                message="质量方针内容为空或格式错误",
                details=["输入内容为空或不是字符串类型"],
                suggestions=["请提供有效的质量方针文本"]
            )

        policy_text = policy_text.strip()
        if len(policy_text) < 10:
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.CRITICAL,
                message="质量方针内容过短，疑似编造",
                details=[f"内容长度仅{len(policy_text)}个字符，不符合正常质量方针要求"],
                suggestions=["质量方针应包含企业特色，长度建议不少于20个字"]
            )

        # 检测通用套话
        matched_phrases = []
        for phrase in self.GENERIC_PHRASES:
            if phrase in policy_text:
                matched_phrases.append(phrase)

        # 计算套话密度
        generic_ratio = len(matched_phrases) / len(policy_text) * 100 if policy_text else 0

        details = []
        suggestions = []

        if len(matched_phrases) >= 5:
            risk_level = RiskLevel.HIGH
            message = "质量方针包含大量通用套话，疑似直接套用模板"
            details.append(f"检测到{len(matched_phrases)}个通用套话词汇: {', '.join(matched_phrases[:10])}")
            suggestions.extend([
                "结合企业实际业务特点重新撰写",
                "体现企业独特的发展理念和价值观",
                "避免使用过于空泛的表述"
            ])
        elif len(matched_phrases) >= 3:
            risk_level = RiskLevel.MEDIUM
            message = "质量方针包含较多通用表述，建议优化"
            details.append(f"检测到{len(matched_phrases)}个通用套话词汇: {', '.join(matched_phrases)}")
            suggestions.extend([
                "增加企业特色的具体描述",
                "减少通用性表述的使用"
            ])
        elif len(matched_phrases) >= 1:
            risk_level = RiskLevel.LOW
            message = "质量方针基本可信，包含少量通用表述"
            details.append(f"检测到{len(matched_phrases)}个通用词汇: {', '.join(matched_phrases)}")
            suggestions.append("可适当增加企业个性化元素")
        else:
            risk_level = RiskLevel.LOW
            message = "质量方针内容个性化程度较高"
            details.append("未检测到明显的通用套话")
            suggestions.append("保持当前质量方针的特色")

        # 检查是否包含企业具体信息
        company_specific_patterns = [
            r'[\u4e00-\u9fa5]{2,10}(公司|集团|厂|企业)',
            r'(产品|服务|客户|市场)',
            r'(行业|领域|产业)'
        ]

        has_specific_info = any(
            re.search(pattern, policy_text)
            for pattern in company_specific_patterns
        )

        if not has_specific_info:
            details.append("未检测到企业具体信息（如公司名称、产品类型等）")
            if risk_level == RiskLevel.LOW:
                risk_level = RiskLevel.MEDIUM
                message = "质量方针缺少企业具体信息，可能为通用模板"
                suggestions.insert(0, "建议加入企业名称、产品特点等具体信息")

        result = ValidationResult(
            is_valid=risk_level.value in ['low', 'medium'],
            risk_level=risk_level,
            message=message,
            details=details,
            suggestions=suggestions
        )

        self.validation_history.append(result)
        return result

    def validate_quality_objectives(self, objectives_text: str) -> ValidationResult:
        """
        验证质量目标是否有具体数字

        Args:
            objectives_text: 质量目标文本

        Returns:
            ValidationResult: 验证结果
        """
        if not objectives_text or not isinstance(objectives_text, str):
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.CRITICAL,
                message="质量目标内容为空或格式错误",
                details=["输入内容为空或不是字符串类型"],
                suggestions=["请提供有效的质量目标文本"]
            )

        objectives_text = objectives_text.strip()
        details = []
        suggestions = []

        # 匹配百分比数字（如 95%、99.5%）
        percentage_pattern = r'\d+\.?\d*\s*%'
        percentages = re.findall(percentage_pattern, objectives_text)

        # 匹配普通数字（如 100、1000）
        number_pattern = r'\b\d+\b'
        numbers = re.findall(number_pattern, objectives_text)

        # 匹配时间期限（如 2024年、Q1、第一季度）
        time_pattern = r'(20\d{2}年|20\d{2}|Q[1-4]|第[一二三四]季度|年度|月度)'
        time_refs = re.findall(time_pattern, objectives_text)

        has_percentage = len(percentages) > 0
        has_number = len(numbers) > 0
        has_time = len(time_refs) > 0

        if has_percentage:
            details.append(f"检测到{len(percentages)}个百分比指标: {', '.join(percentages[:5])}")

        if has_number:
            details.append(f"检测到{len(numbers)}个数字指标")

        if has_time:
            details.append(f"检测到时间期限: {', '.join(time_refs[:3])}")

        # 评估风险等级
        if has_percentage and has_time:
            risk_level = RiskLevel.LOW
            message = "质量目标包含具体的量化指标和时间期限"
            suggestions.append("保持目标的可测量性和时效性")
        elif has_percentage and not has_time:
            risk_level = RiskLevel.MEDIUM
            message = "质量目标有量化指标但缺少明确时间期限"
            suggestions.append("建议为每个目标设定完成时间节点")
        elif has_number and not has_percentage:
            risk_level = RiskLevel.MEDIUM
            message = "质量目标包含数字但缺少百分比指标"
            suggestions.extend([
                "建议增加百分比形式的指标（如合格率、满意度等）",
                "明确目标的时间期限"
            ])
        else:
            risk_level = RiskLevel.HIGH
            message = "质量目标缺少具体数字指标，疑似编造"
            details.append("未检测到任何百分比或具体数值")
            suggestions.extend([
                "质量目标应包含可测量的量化指标",
                "使用百分比表示合格率、满意度等",
                "设定具体的数值目标（如投诉次数<=3次）",
                "明确目标的时间期限"
            ])

        # 检查模糊表述
        vague_patterns = ['力争', '争取', '努力', '尽量', '可能', '大概', '基本']
        vague_matches = [p for p in vague_patterns if p in objectives_text]

        if vague_matches:
            details.append(f"检测到模糊表述: {', '.join(vague_matches)}")
            if risk_level == RiskLevel.LOW:
                risk_level = RiskLevel.MEDIUM
                message = "质量目标包含模糊表述，影响可测量性"
            suggestions.append("避免使用'力争'、'尽量'等模糊词汇")

        result = ValidationResult(
            is_valid=risk_level.value in ['low', 'medium'],
            risk_level=risk_level,
            message=message,
            details=details,
            suggestions=suggestions
        )

        self.validation_history.append(result)
        return result

    def validate_department_name(self, department_name: str) -> ValidationResult:
        """
        检测部门名称是否在标准列表

        Args:
            department_name: 部门名称

        Returns:
            ValidationResult: 验证结果
        """
        if not department_name or not isinstance(department_name, str):
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.CRITICAL,
                message="部门名称为空或格式错误",
                details=["输入内容为空或不是字符串类型"],
                suggestions=["请提供有效的部门名称"]
            )

        department_name = department_name.strip()
        details = []
        suggestions = []

        # 检查是否在标准列表中
        is_standard = department_name in self.STANDARD_DEPARTMENTS

        # 模糊匹配（允许部分匹配）
        partial_matches = [
            dept for dept in self.STANDARD_DEPARTMENTS
            if department_name in dept or dept in department_name
        ]

        if is_standard:
            risk_level = RiskLevel.LOW
            message = f"部门名称'{department_name}'为标准部门名称"
            details.append("该部门名称在标准部门列表中")
            suggestions.append("部门名称规范，无需修改")
        elif partial_matches:
            risk_level = RiskLevel.LOW
            message = f"部门名称'{department_name}'与标准名称相似"
            details.append(f"相似的标准部门: {', '.join(partial_matches[:3])}")
            suggestions.append(f"建议使用标准名称: {partial_matches[0]}")
        else:
            # 检查是否为常见非标准命名
            non_standard_patterns = [
                r'.*部$', r'.*中心$', r'.*室$', r'.*科$', r'.*组$',
                r'.*处$', r'.*课$'
            ]

            is_valid_format = any(
                re.match(pattern, department_name)
                for pattern in non_standard_patterns
            )

            if is_valid_format:
                risk_level = RiskLevel.MEDIUM
                message = f"部门名称'{department_name}'不在标准列表中，但格式正确"
                details.append("部门名称格式符合常见命名规则")
                suggestions.extend([
                    "确认是否为自定义部门名称",
                    "可参考标准部门列表进行规范",
                    "如为新设部门，请确保命名符合企业实际"
                ])
            else:
                risk_level = RiskLevel.HIGH
                message = f"部门名称'{department_name}'格式异常，需核实"
                details.append("部门名称不符合常见命名格式")
                suggestions.extend([
                    "参考标准部门名称进行命名",
                    "部门名称应以'部'、'中心'、'室'等结尾",
                    "避免使用过于笼统或模糊的命名"
                ])

        result = ValidationResult(
            is_valid=risk_level.value in ['low', 'medium'],
            risk_level=risk_level,
            message=message,
            details=details,
            suggestions=suggestions
        )

        self.validation_history.append(result)
        return result

    def validate_document_number(self, doc_number: str) -> ValidationResult:
        """
        检测文件编号格式
        支持格式：XXX-QESMS-A-001、XXX-ISO-001等

        Args:
            doc_number: 文件编号

        Returns:
            ValidationResult: 验证结果
        """
        if not doc_number or not isinstance(doc_number, str):
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.CRITICAL,
                message="文件编号为空或格式错误",
                details=["输入内容为空或不是字符串类型"],
                suggestions=["请提供有效的文件编号"]
            )

        doc_number = doc_number.strip().upper()
        details = []
        suggestions = []

        # 检查是否匹配任一标准格式
        matched_pattern = None
        for pattern in self.DOCUMENT_NUMBER_PATTERNS:
            if re.match(pattern, doc_number):
                matched_pattern = pattern
                break

        if matched_pattern:
            risk_level = RiskLevel.LOW
            message = f"文件编号'{doc_number}'格式正确"
            details.append("符合标准文件编号格式")
            suggestions.append("文件编号规范，无需修改")

            # 提取编号组成部分
            parts = doc_number.split('-')
            details.append(f"编号组成: {' - '.join(parts)}")
        else:
            # 分析可能的问题
            risk_level = RiskLevel.HIGH
            message = f"文件编号'{doc_number}'格式不符合标准"

            # 检查分隔符
            if '-' not in doc_number:
                details.append("缺少分隔符'-'，标准格式应使用'-'分隔各部分")
                suggestions.append("使用'-'分隔部门代码、类别和序号")

            # 检查长度
            if len(doc_number) < 5:
                details.append("编号长度过短")
                suggestions.append("文件编号应包含足够的信息标识")

            # 检查是否包含数字
            if not re.search(r'\d', doc_number):
                details.append("缺少数字序号")
                suggestions.append("文件编号应包含数字序号（如001、002）")

            suggestions.extend([
                "推荐格式: XXX-QESMS-A-001（三体系文件）",
                "推荐格式: XXX-QM-001（质量手册）",
                "推荐格式: XXX-ISO-001（ISO文件）",
                "其中XXX为2-5位字母的部门代码"
            ])

        result = ValidationResult(
            is_valid=risk_level.value in ['low', 'medium'],
            risk_level=risk_level,
            message=message,
            details=details,
            suggestions=suggestions
        )

        self.validation_history.append(result)
        return result

    def validate_person_name(self, person_name: str) -> ValidationResult:
        """
        检测人员姓名是否模糊

        Args:
            person_name: 人员姓名或称谓

        Returns:
            ValidationResult: 验证结果
        """
        if not person_name or not isinstance(person_name, str):
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.CRITICAL,
                message="人员名称为空或格式错误",
                details=["输入内容为空或不是字符串类型"],
                suggestions=["请提供有效的人员姓名"]
            )

        person_name = person_name.strip()
        details = []
        suggestions = []

        # 检查是否为模糊关键词
        is_vague = any(keyword in person_name for keyword in self.VAGUE_PERSON_KEYWORDS)

        # 检查是否为纯模糊词
        exact_vague_match = person_name in self.VAGUE_PERSON_KEYWORDS

        # 检查是否为正常中文姓名（2-4个汉字）
        chinese_name_pattern = r'^[\u4e00-\u9fa5]{2,4}$'
        is_chinese_name = re.match(chinese_name_pattern, person_name) is not None

        # 检查是否包含职务
        title_patterns = [
            r'.*经理$', r'.*主管$', r'.*主任$', r'.*部长$',
            r'.*组长$', r'.*班长$', r'.*工程师$', r'.*专员$'
        ]
        has_title = any(re.match(pattern, person_name) for pattern in title_patterns)

        if exact_vague_match:
            risk_level = RiskLevel.CRITICAL
            message = f"'{person_name}'为模糊称谓，必须指定具体人员"
            details.append("使用了模糊的通用称谓而非具体姓名")
            suggestions.extend([
                "指定具体的人员姓名",
                "如确实不确定，应标注'待确定'并后续补充",
                "避免使用'负责人'、'相关人员'等模糊表述"
            ])
        elif is_vague:
            risk_level = RiskLevel.HIGH
            message = f"'{person_name}'包含模糊表述，建议明确具体人员"
            matched_keywords = [k for k in self.VAGUE_PERSON_KEYWORDS if k in person_name]
            details.append(f"检测到模糊关键词: {', '.join(matched_keywords)}")
            suggestions.extend([
                "使用具体人员姓名",
                "明确责任人的姓名和职务",
                "确保可追溯性"
            ])
        elif is_chinese_name and not has_title:
            risk_level = RiskLevel.LOW
            message = f"'{person_name}'为正常姓名格式"
            details.append("符合中文姓名格式（2-4个汉字）")
            suggestions.append("如需要可补充职务信息")
        elif is_chinese_name and has_title:
            risk_level = RiskLevel.LOW
            message = f"'{person_name}'为姓名+职务格式"
            details.append("包含姓名和职务信息")
            suggestions.append("格式规范，信息完整")
        elif has_title:
            risk_level = RiskLevel.MEDIUM
            message = f"'{person_name}'仅包含职务，建议补充姓名"
            details.append("只有职务信息，缺少具体姓名")
            suggestions.extend([
                "补充具体人员姓名",
                "格式建议: 姓名+职务（如：张三-质量经理）"
            ])
        else:
            risk_level = RiskLevel.MEDIUM
            message = f"'{person_name}'格式不常见，请核实"
            details.append("不符合常见的中文姓名或职务格式")
            suggestions.extend([
                "使用规范的中文姓名",
                "或采用'姓名-职务'格式",
                "避免使用编号、代号等代替姓名"
            ])

        result = ValidationResult(
            is_valid=risk_level.value in ['low', 'medium'],
            risk_level=risk_level,
            message=message,
            details=details,
            suggestions=suggestions
        )

        self.validation_history.append(result)
        return result

    def validate_with_source(
        self,
        field_name: str,
        field_value: str,
        source: str,
        source_file: Optional[str] = None
    ) -> ValidationResult:
        """
        带来源信息的验证

        根据信息来源调整验证严格程度：
        - P1(用户输入): 宽松验证，信任用户
        - P2(文件提取): 中等验证，检查提取准确性
        - P3(AI生成): 严格验证，必须人工确认
        """
        # 根据来源设置基础风险等级
        if source == "P1":
            base_risk = RiskLevel.LOW
        elif source == "P2":
            base_risk = RiskLevel.MEDIUM
        else:  # P3或未知
            base_risk = RiskLevel.HIGH

        # 执行具体字段验证
        if field_name == "quality_policy":
            result = self.validate_quality_policy(field_value)
        elif field_name == "quality_objectives":
            result = self.validate_quality_objectives(field_value)
        elif field_name == "department":
            result = self.validate_department_name(field_value)
        elif field_name == "doc_number":
            result = self.validate_document_number(field_value)
        elif field_name == "person":
            result = self.validate_person_name(field_value)
        else:
            # 未知字段类型，返回通用结果
            return ValidationResult(
                is_valid=True,
                risk_level=base_risk,
                message=f"未知字段类型: {field_name}",
                details=["该字段没有专门的验证规则"],
                suggestions=["使用通用验证规则"],
                field_name=field_name,
                field_value=field_value,
                source=source,
                needs_verification=source == "P3",
                verification_reason="未知字段类型，建议人工确认" if source == "P3" else ""
            )

        # 合并来源风险和验证结果风险
        final_risk = self._merge_risk_levels(base_risk, result.risk_level)

        # P3来源必须标记为需要验证
        needs_verification = (source == "P3") or (final_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL])

        return ValidationResult(
            is_valid=result.is_valid and not needs_verification,
            risk_level=final_risk,
            message=result.message,
            details=result.details,
            suggestions=result.suggestions,
            field_name=field_name,
            field_value=field_value,
            source=source,
            needs_verification=needs_verification,
            verification_reason="AI生成内容必须人工确认" if source == "P3" else result.message
        )

    def _merge_risk_levels(self, risk1: RiskLevel, risk2: RiskLevel) -> RiskLevel:
        """合并两个风险等级，取较高者"""
        risk_order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        idx1 = risk_order.index(risk1)
        idx2 = risk_order.index(risk2)
        return risk_order[max(idx1, idx2)]

    def validate_fields_batch(
        self,
        fields: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """
        批量验证多个字段

        fields格式: [
            {"field_name": "quality_policy", "value": "...", "source": "P3"},
            {"field_name": "quality_objectives", "value": "...", "source": "P2", "source_file": "手册.docx"},
        ]
        """
        results = []
        for field in fields:
            result = self.validate_with_source(
                field["field_name"],
                field["value"],
                field.get("source", "P3"),
                field.get("source_file")
            )
            results.append(result)
        return results

    def generate_validation_report(
        self,
        results: List[ValidationResult]
    ) -> Dict[str, Any]:
        """生成验证报告"""
        total = len(results)
        valid_count = sum(1 for r in results if r.is_valid)
        needs_verification_count = sum(1 for r in results if r.needs_verification)

        risk_distribution = {
            "low": sum(1 for r in results if r.risk_level == RiskLevel.LOW),
            "medium": sum(1 for r in results if r.risk_level == RiskLevel.MEDIUM),
            "high": sum(1 for r in results if r.risk_level == RiskLevel.HIGH),
            "critical": sum(1 for r in results if r.risk_level == RiskLevel.CRITICAL),
        }

        source_distribution = {
            "P1": sum(1 for r in results if r.source == "P1"),
            "P2": sum(1 for r in results if r.source == "P2"),
            "P3": sum(1 for r in results if r.source == "P3"),
        }

        return {
            "total_fields": total,
            "valid_fields": valid_count,
            "needs_verification": needs_verification_count,
            "valid_rate": valid_count / total if total > 0 else 0,
            "risk_distribution": risk_distribution,
            "source_distribution": source_distribution,
            "critical_issues": [
                {"field": r.field_name, "reason": r.verification_reason}
                for r in results if r.risk_level == RiskLevel.CRITICAL
            ],
            "verification_required": [
                {"field": r.field_name, "value": r.field_value, "reason": r.verification_reason}
                for r in results if r.needs_verification
            ],
        }

    def validate_document(self, document: Dict[str, Any]) -> Dict[str, ValidationResult]:
        """
        综合验证整个文档

        Args:
            document: 包含各字段的字典
                - quality_policy: 质量方针
                - quality_objectives: 质量目标
                - department: 部门名称
                - doc_number: 文件编号
                - person: 人员姓名

        Returns:
            Dict[str, ValidationResult]: 各字段的验证结果
        """
        results = {}

        if 'quality_policy' in document:
            results['quality_policy'] = self.validate_quality_policy(document['quality_policy'])

        if 'quality_objectives' in document:
            results['quality_objectives'] = self.validate_quality_objectives(document['quality_objectives'])

        if 'department' in document:
            results['department'] = self.validate_department_name(document['department'])

        if 'doc_number' in document:
            results['doc_number'] = self.validate_document_number(document['doc_number'])

        if 'person' in document:
            results['person'] = self.validate_person_name(document['person'])

        return results

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        获取验证历史汇总

        Returns:
            Dict: 验证统计信息
        """
        if not self.validation_history:
            return {
                "total_validations": 0,
                "risk_distribution": {},
                "valid_rate": 0.0
            }

        total = len(self.validation_history)
        valid_count = sum(1 for r in self.validation_history if r.is_valid)

        risk_distribution = {
            "low": sum(1 for r in self.validation_history if r.risk_level == RiskLevel.LOW),
            "medium": sum(1 for r in self.validation_history if r.risk_level == RiskLevel.MEDIUM),
            "high": sum(1 for r in self.validation_history if r.risk_level == RiskLevel.HIGH),
            "critical": sum(1 for r in self.validation_history if r.risk_level == RiskLevel.CRITICAL)
        }

        return {
            "total_validations": total,
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "valid_rate": round(valid_count / total * 100, 2),
            "risk_distribution": risk_distribution
        }


# ============================================================
# FabricationDetector - 增强版编造检测器
# ============================================================

@dataclass
class FabricatedItem:
    """单个编造项数据类"""
    item_type: str          # 编造类型: keyword / vague_expression / number / date / cert_number / name
    original_text: str      # 生成文本中的原始内容
    description: str        # 编造描述
    risk_level: RiskLevel   # 风险等级
    position: int = -1      # 在文本中的位置（字符偏移）
    context: str = ""       # 上下文片段（前后各30字符）
    source_match: str = ""  # 源文件中匹配到的内容（如有）
    suggestion: str = ""    # 修正建议


@dataclass
class FabricationResult:
    """编造检测结果数据类"""
    is_fabricated: bool                         # 是否存在编造
    overall_risk: RiskLevel                     # 整体风险等级
    fabricated_items: List[FabricatedItem]      # 编造项列表
    total_checks: int = 0                       # 总检查项数
    passed_checks: int = 0                      # 通过检查项数
    failed_checks: int = 0                      # 未通过检查项数
    summary: str = ""                           # 检测摘要
    details: Dict[str, Any] = field(default_factory=dict)  # 各步骤详细结果


class FabricationDetector:
    """
    增强版编造检测器

    提供完整的6步编造检测流程，支持与源文件交叉验证。
    用于检测AI生成内容中可能存在的编造、虚构信息。

    使用方式:
        detector = FabricationDetector()
        result = detector.detect_fabrication(generated_text, source_texts)
    """

    # ---- 正则模式 ----

    # 数字模式：匹配各种数字格式（整数、小数、百分比、金额等）
    _NUMBER_PATTERN = re.compile(
        r'(?:'
        r'\d+\.?\d*\s*%'                        # 百分比: 95%, 99.5%
        r'|人民币\s*\d+\.?\d*\s*元'             # 人民币金额
        r'|\d+\.?\d*\s*万元'                    # 万元金额
        r'|\d+\.?\d*\s*亿'                      # 亿
        r'|\d{1,3}(?:,\d{3})+'                  # 千分位数字: 1,000
        r'|\b\d+\.?\d*\b'                       # 普通数字
        r')'
    )

    # 日期模式：匹配各种日期格式
    _DATE_PATTERN = re.compile(
        r'(?:'
        r'\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日'   # 2024年1月15日
        r'|\d{4}\s*年\s*\d{1,2}\s*月'                  # 2024年1月
        r'|\d{4}[-/]\d{1,2}[-/]\d{1,2}'               # 2024-01-15, 2024/01/15
        r'|\d{4}[-/]\d{1,2}'                           # 2024-01
        r'|(?:19|20)\d{2}年'                           # 2024年
        r'|Q[1-4]\s*[-/]?\s*(?:19|20)\d{2}'           # Q1/2024
        r'|第[一二三四1-4]季度'                         # 第一季度
        r')'
    )

    # 证书/编号模式：匹配各种证书编号和文件编号
    _CERT_NUMBER_PATTERN = re.compile(
        r'(?:'
        r'[A-Z]{2,5}-[A-Z]{1,6}-[A-Z]-\d{3,4}'       # XXX-QESMS-A-001
        r'|[A-Z]{2,5}-[A-Z]{1,3}-\d{3,4}'             # XXX-ISO-001
        r'|(?:ISO|GB|GB/T|HJ|QB|DB|Q|JG|SL|JT|YS|CJ|NY|AQ|SN|WS)\s*[\d/.-]+'  # 标准编号
        r'|CNAS-[A-Z]{2,4}-\d{4,6}'                   # CNAS编号
        r'|证书编号\s*[:：]?\s*\S+'                    # 证书编号: XXX
        r'|注册号\s*[:：]?\s*\S+'                      # 注册号: XXX
        r'|编号\s*[:：]?\s*[A-Z0-9-]+'                # 编号: XXX
        r')'
    )

    # 人名模式：匹配中文姓名（2-4个汉字，常见姓氏开头）
    _NAME_PATTERN = re.compile(
        r'(?:'
        r'[\u4e00-\u9fa5]{2,4}(?=担任|负责|主管|经理|主任|部长|组长|审核|批准|编制|实施|执行|参与)'
        r'|(?:总经理|副总经理|总工程师|管理者代表|质量负责人|技术负责人|安全负责人)\s*[:：]?\s*[\u4e00-\u9fa5]{2,4}'
        r')'
    )

    # ---- 编造关键词（18个） ----
    _FABRICATION_KEYWORDS: List[str] = [
        "根据公司实际情况",
        "结合本公司实际",
        "经公司研究决定",
        "按照公司要求",
        "公司高度重视",
        "公司始终坚持以",
        "公司秉承",
        "公司致力于",
        "公司积极推行",
        "公司严格执行",
        "公司全面实施",
        "公司不断完善",
        "公司注重",
        "公司坚持",
        "公司确保",
        "经讨论决定",
        "经领导批准",
        "按照相关规定"
    ]

    # ---- 模糊表达（22个） ----
    _VAGUE_EXPRESSIONS: List[str] = [
        "适当",
        "合理",
        "必要时",
        "按规定",
        "按有关规定",
        "按相关要求",
        "视情况而定",
        "酌情处理",
        "及时",
        "定期",
        "不定期",
        "适时",
        "相应的",
        "相关的",
        "有关的",
        "必要的",
        "充分的",
        "有效的",
        "适宜的",
        "足够的",
        "妥善",
        "妥善处理"
    ]

    # ---- 500个常见中文姓氏 ----
    _COMMON_SURNAMES: Set[str] = {
        # 大姓（前100）
        "赵", "钱", "孙", "李", "周", "吴", "郑", "王", "冯", "陈",
        "褚", "卫", "蒋", "沈", "韩", "杨", "朱", "秦", "尤", "许",
        "何", "吕", "施", "张", "孔", "曹", "严", "华", "金", "魏",
        "陶", "姜", "戚", "谢", "邹", "喻", "柏", "水", "窦", "章",
        "云", "苏", "潘", "葛", "奚", "范", "彭", "郎", "鲁", "韦",
        "昌", "马", "苗", "凤", "花", "方", "俞", "任", "袁", "柳",
        "酆", "鲍", "史", "唐", "费", "廉", "岑", "薛", "雷", "贺",
        "倪", "汤", "滕", "殷", "罗", "毕", "郝", "邬", "安", "常",
        "乐", "于", "时", "傅", "皮", "卞", "齐", "康", "伍", "余",
        "元", "卜", "顾", "孟", "平", "黄", "和", "穆", "萧", "尹",
        # 中等常见姓（101-200）
        "姚", "邵", "湛", "汪", "祁", "毛", "禹", "狄", "米", "贝",
        "明", "臧", "计", "伏", "成", "戴", "谈", "宋", "茅", "庞",
        "熊", "纪", "舒", "屈", "项", "祝", "董", "梁", "杜", "阮",
        "蓝", "闵", "席", "季", "麻", "强", "贾", "路", "娄", "危",
        "江", "童", "颜", "郭", "梅", "盛", "林", "刁", "钟", "徐",
        "邱", "骆", "高", "夏", "蔡", "田", "樊", "胡", "凌", "霍",
        "虞", "万", "支", "柯", "昝", "管", "卢", "莫", "经", "房",
        "裘", "缪", "干", "解", "应", "宗", "丁", "宣", "贲", "邓",
        "郁", "单", "杭", "洪", "包", "诸", "左", "石", "崔", "吉",
        "钮", "龚", "程", "嵇", "邢", "滑", "裴", "陆", "荣", "翁",
        # 较常见姓（201-300）
        "荀", "羊", "於", "惠", "甄", "曲", "家", "封", "芮", "羿",
        "储", "靳", "汲", "邴", "糜", "松", "井", "段", "富", "巫",
        "乌", "焦", "巴", "弓", "牧", "隗", "山", "谷", "车", "侯",
        "宓", "蓬", "全", "郗", "班", "仰", "秋", "仲", "伊", "宫",
        "宁", "仇", "栾", "暴", "甘", "钭", "厉", "戎", "祖", "武",
        "符", "刘", "景", "詹", "束", "龙", "叶", "幸", "司", "韶",
        "郜", "黎", "蓟", "溥", "印", "宿", "白", "怀", "蒲", "邰",
        "从", "鄂", "索", "咸", "籍", "赖", "卓", "蔺", "屠", "蒙",
        "池", "乔", "阴", "郁", "胥", "能", "苍", "双", "闻", "莘",
        "党", "翟", "谭", "贡", "劳", "逄", "姬", "申", "扶", "堵",
        # 少见但存在的姓（301-400）
        "冉", "宰", "郦", "雍", "却", "璩", "桑", "桂", "濮", "牛",
        "寿", "通", "边", "扈", "燕", "冀", "郏", "浦", "尚", "农",
        "温", "别", "庄", "晏", "柴", "瞿", "阎", "充", "慕", "连",
        "茹", "习", "宦", "艾", "鱼", "容", "向", "古", "易", "慎",
        "戈", "廖", "庾", "终", "暨", "居", "衡", "步", "都", "耿",
        "满", "弘", "匡", "国", "文", "寇", "广", "禄", "阙", "东",
        "欧", "殳", "沃", "利", "蔚", "越", "夔", "隆", "师", "巩",
        "厍", "聂", "晁", "勾", "敖", "融", "冷", "訾", "辛", "阚",
        "那", "简", "饶", "空", "曾", "毋", "沙", "乜", "养", "鞠",
        "须", "丰", "巢", "关", "蒯", "相", "查", "后", "荆", "红",
        # 罕见姓（401-500）
        "游", "竺", "权", "逯", "盖", "益", "桓", "公", "万俟", "司马",
        "上官", "欧阳", "夏侯", "诸葛", "闻人", "东方", "赫连", "皇甫", "尉迟", "公羊",
        "澹台", "公冶", "宗政", "濮阳", "淳于", "单于", "太叔", "申屠", "公孙", "仲孙",
        "轩辕", "令狐", "钟离", "宇文", "长孙", "慕容", "鲜于", "闾丘", "司徒", "司空",
        "亓官", "司寇", "仉", "督", "子车", "颛孙", "端木", "巫马", "公西", "漆雕",
        "乐正", "壤驷", "公良", "拓跋", "夹谷", "宰父", "谷梁", "晋", "楚", "闫",
        "法", "汝", "鄢", "涂", "钦", "段干", "百里", "东郭", "南门", "呼延",
        "归", "海", "羊舌", "微生", "岳", "帅", "缑", "亢", "况", "后",
        "有", "琴", "梁丘", "左丘", "东门", "西门", "商", "牟", "佘", "佴",
        "伯", "赏", "南宫", "墨", "哈", "谯", "笪", "年", "爱", "阳",
    }

    def __init__(self):
        """初始化编造检测器"""
        self._logger = logging.getLogger(f"{__name__}.FabricationDetector")

    def detect_fabrication(
        self,
        generated_text: str,
        source_texts: Optional[List[str]] = None
    ) -> FabricationResult:
        """
        完整编造检测（6步）

        检测流程:
        1. 关键词检测 - 检测18个编造关键词
        2. 模糊表达检测 - 检测22个模糊表达
        3. 数字验证 - 与源文件比对数字
        4. 日期验证 - 与源文件比对日期
        5. 证书/编号验证 - 与源文件比对编号
        6. 人名验证 - 使用常见姓氏列表验证

        Args:
            generated_text: 待检测的生成文本
            source_texts: 源文件文本列表（用于交叉验证）

        Returns:
            FabricationResult: 编造检测结果
        """
        if not generated_text or not isinstance(generated_text, str):
            return FabricationResult(
                is_fabricated=True,
                overall_risk=RiskLevel.CRITICAL,
                fabricated_items=[FabricatedItem(
                    item_type="input_error",
                    original_text="",
                    description="输入文本为空或格式错误",
                    risk_level=RiskLevel.CRITICAL,
                    suggestion="请提供有效的待检测文本"
                )],
                summary="输入文本无效，无法执行编造检测"
            )

        source_texts = source_texts or []
        combined_source = "\n".join(source_texts)
        all_items: List[FabricatedItem] = []
        step_details: Dict[str, Any] = {}

        # 步骤1: 关键词检测
        keyword_items = self._detect_keywords(generated_text)
        all_items.extend(keyword_items)
        step_details["keywords"] = {
            "checked": True,
            "found_count": len(keyword_items),
            "items": [it.original_text for it in keyword_items]
        }

        # 步骤2: 模糊表达检测
        vague_items = self._detect_vague_expressions(generated_text)
        all_items.extend(vague_items)
        step_details["vague_expressions"] = {
            "checked": True,
            "found_count": len(vague_items),
            "items": [it.original_text for it in vague_items]
        }

        # 步骤3: 数字验证
        number_items = self._verify_numbers(generated_text, combined_source)
        all_items.extend(number_items)
        step_details["numbers"] = {
            "checked": True,
            "found_count": len(number_items),
            "items": [it.original_text for it in number_items]
        }

        # 步骤4: 日期验证
        date_items = self._verify_dates(generated_text, combined_source)
        all_items.extend(date_items)
        step_details["dates"] = {
            "checked": True,
            "found_count": len(date_items),
            "items": [it.original_text for it in date_items]
        }

        # 步骤5: 证书/编号验证
        cert_items = self._verify_cert_numbers(generated_text, combined_source)
        all_items.extend(cert_items)
        step_details["cert_numbers"] = {
            "checked": True,
            "found_count": len(cert_items),
            "items": [it.original_text for it in cert_items]
        }

        # 步骤6: 人名验证
        name_items = self._verify_person_names(generated_text, combined_source)
        all_items.extend(name_items)
        step_details["names"] = {
            "checked": True,
            "found_count": len(name_items),
            "items": [it.original_text for it in name_items]
        }

        # 汇总结果
        total_checks = 6
        failed_steps = sum(
            1 for v in step_details.values() if v["found_count"] > 0
        )
        passed_checks = total_checks - failed_steps

        # 确定整体风险等级
        overall_risk = self._calculate_overall_risk(all_items)

        # 生成摘要
        high_risk_items = [it for it in all_items if it.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)]
        if not high_risk_items:
            summary = f"编造检测完成，共检查{total_checks}个维度，未发现高风险编造项。"
            if len(all_items) > 0:
                summary += f"发现{len(all_items)}个低风险提示项，建议关注。"
        else:
            summary = (
                f"编造检测完成，共检查{total_checks}个维度，"
                f"发现{len(high_risk_items)}个高风险编造项，"
                f"共{len(all_items)}个问题项需要关注。"
            )

        self._logger.info(
            f"编造检测完成: overall_risk={overall_risk.value}, "
            f"total_items={len(all_items)}, high_risk={len(high_risk_items)}"
        )

        return FabricationResult(
            is_fabricated=overall_risk in (RiskLevel.HIGH, RiskLevel.CRITICAL),
            overall_risk=overall_risk,
            fabricated_items=all_items,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_steps,
            summary=summary,
            details=step_details
        )

    def verify_data_point(
        self,
        data_point: str,
        source_texts: Optional[List[str]] = None
    ) -> FabricatedItem:
        """
        单数据点验证

        对单个数据点进行编造检测，自动判断数据类型并选择合适的验证策略。

        Args:
            data_point: 待验证的单个数据点
            source_texts: 源文件文本列表

        Returns:
            FabricatedItem: 验证结果项
        """
        if not data_point or not isinstance(data_point, str):
            return FabricatedItem(
                item_type="input_error",
                original_text=data_point or "",
                description="数据点为空或格式错误",
                risk_level=RiskLevel.CRITICAL,
                suggestion="请提供有效的数据点"
            )

        source_texts = source_texts or []
        combined_source = "\n".join(source_texts)
        data_point = data_point.strip()

        # 自动判断数据类型
        if self._CERT_NUMBER_PATTERN.search(data_point):
            return self._verify_single_cert(data_point, combined_source)
        elif self._DATE_PATTERN.search(data_point):
            return self._verify_single_date(data_point, combined_source)
        elif self._NUMBER_PATTERN.search(data_point):
            return self._verify_single_number(data_point, combined_source)
        elif self._is_person_name(data_point):
            return self._verify_single_name(data_point, combined_source)
        else:
            # 通用文本验证：检查是否为模糊表达或编造关键词
            if data_point in self._FABRICATION_KEYWORDS:
                return FabricatedItem(
                    item_type="keyword",
                    original_text=data_point,
                    description=f"数据点为编造关键词: {data_point}",
                    risk_level=RiskLevel.HIGH,
                    suggestion="该表述为常见编造套话，建议替换为具体内容"
                )
            elif data_point in self._VAGUE_EXPRESSIONS:
                return FabricatedItem(
                    item_type="vague_expression",
                    original_text=data_point,
                    description=f"数据点为模糊表达: {data_point}",
                    risk_level=RiskLevel.MEDIUM,
                    suggestion="该表述过于模糊，建议使用更具体的描述"
                )
            else:
                return FabricatedItem(
                    item_type="unknown",
                    original_text=data_point,
                    description="无法自动判断数据类型，需人工验证",
                    risk_level=RiskLevel.MEDIUM,
                    suggestion="建议人工核实该数据点的准确性"
                )

    # ---- 步骤1: 关键词检测 ----

    def _detect_keywords(self, text: str) -> List[FabricatedItem]:
        """检测18个编造关键词"""
        items = []
        for keyword in self._FABRICATION_KEYWORDS:
            for match in re.finditer(re.escape(keyword), text):
                start = match.start()
                context = self._extract_context(text, start, len(keyword))
                items.append(FabricatedItem(
                    item_type="keyword",
                    original_text=keyword,
                    description=f"检测到编造关键词: '{keyword}'，该表述常用于模板化内容",
                    risk_level=RiskLevel.MEDIUM,
                    position=start,
                    context=context,
                    suggestion=f"建议将'{keyword}'替换为具体的企业实际情况描述"
                ))
        return items

    # ---- 步骤2: 模糊表达检测 ----

    def _detect_vague_expressions(self, text: str) -> List[FabricatedItem]:
        """检测22个模糊表达"""
        items = []
        for expr in self._VAGUE_EXPRESSIONS:
            for match in re.finditer(re.escape(expr), text):
                start = match.start()
                context = self._extract_context(text, start, len(expr))
                items.append(FabricatedItem(
                    item_type="vague_expression",
                    original_text=expr,
                    description=f"检测到模糊表达: '{expr}'，缺乏具体可衡量的标准",
                    risk_level=RiskLevel.LOW,
                    position=start,
                    context=context,
                    suggestion=f"建议将'{expr}'替换为具体的量化标准或明确的时间/条件"
                ))
        return items

    # ---- 步骤3: 数字验证 ----

    def _verify_numbers(self, text: str, source_text: str) -> List[FabricatedItem]:
        """数字验证 - 与源文件比对"""
        items = []
        gen_numbers = self._NUMBER_PATTERN.findall(text)

        if not gen_numbers:
            return items

        if not source_text:
            # 无源文件时，标记所有数字为需验证
            for match in self._NUMBER_PATTERN.finditer(text):
                num = match.group()
                start = match.start()
                context = self._extract_context(text, start, len(num))
                items.append(FabricatedItem(
                    item_type="number",
                    original_text=num,
                    description=f"数字'{num}'无法与源文件交叉验证（无源文件）",
                    risk_level=RiskLevel.MEDIUM,
                    position=start,
                    context=context,
                    suggestion="建议人工核实该数字的准确性"
                ))
            return items

        # 提取源文件中的数字
        source_numbers = set(self._NUMBER_PATTERN.findall(source_text))

        for match in self._NUMBER_PATTERN.finditer(text):
            num = match.group()
            start = match.start()
            context = self._extract_context(text, start, len(num))

            if num in source_numbers:
                # 数字在源文件中找到，可信
                continue
            else:
                # 数字未在源文件中找到
                items.append(FabricatedItem(
                    item_type="number",
                    original_text=num,
                    description=f"数字'{num}'在源文件中未找到，可能为编造",
                    risk_level=RiskLevel.HIGH,
                    position=start,
                    context=context,
                    suggestion="请核实该数字是否来自源文件，如为AI生成请修改为源文件中的实际数据"
                ))

        return items

    # ---- 步骤4: 日期验证 ----

    def _verify_dates(self, text: str, source_text: str) -> List[FabricatedItem]:
        """日期验证 - 与源文件比对"""
        items = []
        gen_dates = self._DATE_PATTERN.findall(text)

        if not gen_dates:
            return items

        if not source_text:
            for match in self._DATE_PATTERN.finditer(text):
                date_str = match.group()
                start = match.start()
                context = self._extract_context(text, start, len(date_str))
                items.append(FabricatedItem(
                    item_type="date",
                    original_text=date_str,
                    description=f"日期'{date_str}'无法与源文件交叉验证（无源文件）",
                    risk_level=RiskLevel.MEDIUM,
                    position=start,
                    context=context,
                    suggestion="建议人工核实该日期的准确性"
                ))
            return items

        # 提取源文件中的日期
        source_dates = set(self._DATE_PATTERN.findall(source_text))

        for match in self._DATE_PATTERN.finditer(text):
            date_str = match.group()
            start = match.start()
            context = self._extract_context(text, start, len(date_str))

            if date_str in source_dates:
                continue
            else:
                items.append(FabricatedItem(
                    item_type="date",
                    original_text=date_str,
                    description=f"日期'{date_str}'在源文件中未找到，可能为编造",
                    risk_level=RiskLevel.HIGH,
                    position=start,
                    context=context,
                    suggestion="请核实该日期是否来自源文件，如为AI生成请修改为源文件中的实际日期"
                ))

        return items

    # ---- 步骤5: 证书/编号验证 ----

    def _verify_cert_numbers(self, text: str, source_text: str) -> List[FabricatedItem]:
        """证书/编号验证 - 与源文件比对"""
        items = []
        gen_certs = self._CERT_NUMBER_PATTERN.findall(text)

        if not gen_certs:
            return items

        if not source_text:
            for match in self._CERT_NUMBER_PATTERN.finditer(text):
                cert = match.group()
                start = match.start()
                context = self._extract_context(text, start, len(cert))
                items.append(FabricatedItem(
                    item_type="cert_number",
                    original_text=cert,
                    description=f"证书/编号'{cert}'无法与源文件交叉验证（无源文件）",
                    risk_level=RiskLevel.MEDIUM,
                    position=start,
                    context=context,
                    suggestion="建议人工核实该编号的真实性"
                ))
            return items

        # 提取源文件中的证书/编号
        source_certs = set(self._CERT_NUMBER_PATTERN.findall(source_text))

        for match in self._CERT_NUMBER_PATTERN.finditer(text):
            cert = match.group()
            start = match.start()
            context = self._extract_context(text, start, len(cert))

            if cert in source_certs:
                continue
            else:
                items.append(FabricatedItem(
                    item_type="cert_number",
                    original_text=cert,
                    description=f"证书/编号'{cert}'在源文件中未找到，可能为编造",
                    risk_level=RiskLevel.HIGH,
                    position=start,
                    context=context,
                    suggestion="请核实该编号是否来自源文件，如为AI生成请修改为源文件中的实际编号"
                ))

        return items

    # ---- 步骤6: 人名验证 ----

    def _verify_person_names(self, text: str, source_text: str) -> List[FabricatedItem]:
        """人名验证 - 使用常见姓氏列表"""
        items = []

        # 提取文本中可能的人名
        name_matches = self._NAME_PATTERN.findall(text)
        if not name_matches:
            # 尝试更宽泛的人名提取
            name_matches = self._extract_potential_names(text)

        if not name_matches:
            return items

        seen_names: Set[str] = set()
        for name in name_matches:
            name = name.strip()
            if not name or name in seen_names or len(name) < 2 or len(name) > 4:
                continue
            seen_names.add(name)

            # 检查姓氏是否在常见姓氏列表中
            first_char = name[0]
            # 复姓检查
            first_two = name[:2] if len(name) >= 2 else ""
            is_common_surname = (
                first_char in self._COMMON_SURNAMES
                or first_two in self._COMMON_SURNAMES
            )

            if not is_common_surname:
                # 姓氏不在常见列表中，可能是编造
                position = text.find(name)
                context = self._extract_context(text, position, len(name)) if position >= 0 else ""
                items.append(FabricatedItem(
                    item_type="name",
                    original_text=name,
                    description=f"姓名'{name}'的姓氏'{first_char}'不在500个常见中文姓氏列表中，可能为编造",
                    risk_level=RiskLevel.HIGH,
                    position=position,
                    context=context,
                    suggestion="请核实该姓名是否正确，如为AI生成请替换为源文件中的实际人员姓名"
                ))
            else:
                # 姓氏常见，检查是否在源文件中
                if source_text and name not in source_text:
                    position = text.find(name)
                    context = self._extract_context(text, position, len(name)) if position >= 0 else ""
                    items.append(FabricatedItem(
                        item_type="name",
                        original_text=name,
                        description=f"姓名'{name}'的姓氏常见，但在源文件中未找到该姓名，需人工确认",
                        risk_level=RiskLevel.MEDIUM,
                        position=position,
                        context=context,
                        source_match="",
                        suggestion="请核实该姓名是否为源文件中的实际人员"
                    ))

        return items

    # ---- 单数据点验证辅助方法 ----

    def _verify_single_number(self, data_point: str, source_text: str) -> FabricatedItem:
        """验证单个数字"""
        match = self._NUMBER_PATTERN.search(data_point)
        num = match.group() if match else data_point

        if source_text and num in source_text:
            return FabricatedItem(
                item_type="number",
                original_text=num,
                description=f"数字'{num}'在源文件中找到，验证通过",
                risk_level=RiskLevel.LOW,
                source_match=num
            )
        else:
            return FabricatedItem(
                item_type="number",
                original_text=num,
                description=f"数字'{num}'在源文件中未找到，可能为编造",
                risk_level=RiskLevel.HIGH,
                suggestion="请核实该数字的准确性"
            )

    def _verify_single_date(self, data_point: str, source_text: str) -> FabricatedItem:
        """验证单个日期"""
        match = self._DATE_PATTERN.search(data_point)
        date_str = match.group() if match else data_point

        if source_text and date_str in source_text:
            return FabricatedItem(
                item_type="date",
                original_text=date_str,
                description=f"日期'{date_str}'在源文件中找到，验证通过",
                risk_level=RiskLevel.LOW,
                source_match=date_str
            )
        else:
            return FabricatedItem(
                item_type="date",
                original_text=date_str,
                description=f"日期'{date_str}'在源文件中未找到，可能为编造",
                risk_level=RiskLevel.HIGH,
                suggestion="请核实该日期的准确性"
            )

    def _verify_single_cert(self, data_point: str, source_text: str) -> FabricatedItem:
        """验证单个证书/编号"""
        match = self._CERT_NUMBER_PATTERN.search(data_point)
        cert = match.group() if match else data_point

        if source_text and cert in source_text:
            return FabricatedItem(
                item_type="cert_number",
                original_text=cert,
                description=f"证书/编号'{cert}'在源文件中找到，验证通过",
                risk_level=RiskLevel.LOW,
                source_match=cert
            )
        else:
            return FabricatedItem(
                item_type="cert_number",
                original_text=cert,
                description=f"证书/编号'{cert}'在源文件中未找到，可能为编造",
                risk_level=RiskLevel.HIGH,
                suggestion="请核实该编号的真实性"
            )

    def _verify_single_name(self, data_point: str, source_text: str) -> FabricatedItem:
        """验证单个人名"""
        name = data_point.strip()
        first_char = name[0]
        first_two = name[:2] if len(name) >= 2 else ""
        is_common_surname = (
            first_char in self._COMMON_SURNAMES
            or first_two in self._COMMON_SURNAMES
        )

        if not is_common_surname:
            return FabricatedItem(
                item_type="name",
                original_text=name,
                description=f"姓名'{name}'的姓氏'{first_char}'不在常见姓氏列表中，可能为编造",
                risk_level=RiskLevel.HIGH,
                suggestion="请核实该姓名是否正确"
            )

        if source_text and name in source_text:
            return FabricatedItem(
                item_type="name",
                original_text=name,
                description=f"姓名'{name}'验证通过（姓氏常见且在源文件中找到）",
                risk_level=RiskLevel.LOW,
                source_match=name
            )
        else:
            return FabricatedItem(
                item_type="name",
                original_text=name,
                description=f"姓名'{name}'的姓氏常见，但在源文件中未找到，需人工确认",
                risk_level=RiskLevel.MEDIUM,
                suggestion="请核实该姓名是否为源文件中的实际人员"
            )

    # ---- 通用辅助方法 ----

    def _extract_context(self, text: str, position: int, length: int, context_size: int = 30) -> str:
        """提取文本上下文片段"""
        if position < 0:
            return ""
        start = max(0, position - context_size)
        end = min(len(text), position + length + context_size)
        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        return context

    def _extract_potential_names(self, text: str) -> List[str]:
        """
        从文本中提取潜在的人名
        使用常见姓氏列表 + 姓名长度模式匹配
        """
        names = []
        # 模式: 常见姓氏 + 1~3个汉字
        name_pattern = re.compile(
            r'([\u4e00-\u9fa5])([\u4e00-\u9fa5]{1,3})'
        )
        for match in name_pattern.finditer(text):
            full_name = match.group(0)
            first_char = match.group(1)
            # 复姓检查
            first_two = full_name[:2]

            if (first_char in self._COMMON_SURNAMES
                    or first_two in self._COMMON_SURNAMES):
                # 排除常见非人名词汇
                non_name_words = {
                    "公司", "企业", "部门", "管理", "质量", "技术", "生产",
                    "服务", "客户", "市场", "产品", "设备", "安全", "环境",
                    "文件", "记录", "过程", "控制", "审核", "评审", "监督",
                    "检查", "检验", "测量", "改进", "培训", "采购", "销售",
                    "设计", "开发", "实施", "维护", "运行", "操作", "处置",
                    "我们", "他们", "你们", "自己", "什么", "怎么", "这个",
                    "那个", "因为", "所以", "但是", "而且", "或者", "如果",
                    "可以", "应该", "需要", "能够", "已经", "正在", "将要",
                    "根据", "按照", "通过", "进行", "开展", "组织", "建立",
                    "保持", "确保", "达到", "满足", "符合", "遵守", "执行",
                }
                if full_name not in non_name_words:
                    names.append(full_name)

        return names

    def _is_person_name(self, data_point: str) -> bool:
        """判断数据点是否为人名"""
        data_point = data_point.strip()
        if not data_point:
            return False
        # 纯中文2-4个字
        if not re.match(r'^[\u4e00-\u9fa5]{2,4}$', data_point):
            return False
        first_char = data_point[0]
        first_two = data_point[:2]
        return (
            first_char in self._COMMON_SURNAMES
            or first_two in self._COMMON_SURNAMES
        )

    def _calculate_overall_risk(self, items: List[FabricatedItem]) -> RiskLevel:
        """根据所有编造项计算整体风险等级"""
        if not items:
            return RiskLevel.LOW

        risk_order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        max_risk = RiskLevel.LOW

        for item in items:
            if risk_order.index(item.risk_level) > risk_order.index(max_risk):
                max_risk = item.risk_level

        # 如果HIGH/CRITICAL项超过3个，整体风险提升
        high_count = sum(
            1 for it in items
            if it.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
        )
        if high_count >= 5 and max_risk == RiskLevel.HIGH:
            max_risk = RiskLevel.CRITICAL

        return max_risk


# ============================================================
# 便捷函数接口
# ============================================================

def validate_quality_policy(policy_text: str) -> ValidationResult:
    """验证质量方针的便捷函数"""
    validator = AntiFabricationValidator()
    return validator.validate_quality_policy(policy_text)


def validate_quality_objectives(objectives_text: str) -> ValidationResult:
    """验证质量目标的便捷函数"""
    validator = AntiFabricationValidator()
    return validator.validate_quality_objectives(objectives_text)


def validate_department_name(department_name: str) -> ValidationResult:
    """验证部门名称的便捷函数"""
    validator = AntiFabricationValidator()
    return validator.validate_department_name(department_name)


def validate_document_number(doc_number: str) -> ValidationResult:
    """验证文件编号的便捷函数"""
    validator = AntiFabricationValidator()
    return validator.validate_document_number(doc_number)


def validate_person_name(person_name: str) -> ValidationResult:
    """验证人员姓名的便捷函数"""
    validator = AntiFabricationValidator()
    return validator.validate_person_name(person_name)


def detect_fabrication(
    generated_text: str,
    source_texts: Optional[List[str]] = None
) -> FabricationResult:
    """编造检测的便捷函数"""
    detector = FabricationDetector()
    return detector.detect_fabrication(generated_text, source_texts)
