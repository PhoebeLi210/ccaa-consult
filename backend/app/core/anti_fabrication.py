"""
防编造验证模块
用于检测和验证文档内容是否存在编造、套用模板等问题
"""

import re
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


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


# 便捷函数接口
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
