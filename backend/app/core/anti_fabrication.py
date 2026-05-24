#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 防编造检测
检测和防止AI生成内容中的编造信息
"""

import re
import json
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Set
from datetime import datetime

from .fact_extractor import Fact, FactType, FactExtractor

logger = logging.getLogger(__name__)


class FabricationType(str, Enum):
    """编造类型枚举"""
    GENERIC_PHRASE = "通用短语"
    HALLUCINATED_NAME = "幻觉人名"
    HALLUCINATED_DEPT = "幻觉部门"
    HALLUCINATED_DATE = "幻觉日期"
    HALLUCINATED_NUMBER = "幻觉数字"
    INCONSISTENT_DATA = "数据不一致"
    UNVERIFIABLE_CLAIM = "无法验证的声明"
    VAGUE_REFERENCE = "模糊引用"
    TEMPLATE_FILLER = "模板填充内容"
    SPECULATION = "推测性内容"
    MISSING_SOURCE = "缺少来源"
    CONTEXT_MISMATCH = "上下文不匹配"


class Severity(str, Enum):
    """严重程度枚举"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    CRITICAL = "严重"


@dataclass
class FabricationIssue:
    """编造问题"""
    issue_id: str
    fabrication_type: FabricationType
    severity: Severity
    content: str
    position: Tuple[int, int]
    description: str
    suggestion: str
    confidence: float = 0.8
    related_facts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "issue_id": self.issue_id,
            "fabrication_type": self.fabrication_type.value,
            "severity": self.severity.value,
            "content": self.content,
            "position": self.position,
            "description": self.description,
            "suggestion": self.suggestion,
            "confidence": self.confidence,
            "related_facts": self.related_facts,
            "metadata": self.metadata
        }


@dataclass
class FabricationReport:
    """编造检测报告"""
    report_id: str
    text: str
    issues: List[FabricationIssue]
    total_issues: int
    issues_by_type: Dict[str, int]
    issues_by_severity: Dict[str, int]
    overall_score: float  # 0-100, 100表示无编造
    checked_at: datetime = field(default_factory=datetime.now)
    checked_facts: List[Fact] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "report_id": self.report_id,
            "text_length": len(self.text),
            "total_issues": self.total_issues,
            "issues_by_type": self.issues_by_type,
            "issues_by_severity": self.issues_by_severity,
            "overall_score": self.overall_score,
            "checked_at": self.checked_at.isoformat(),
            "issues": [issue.to_dict() for issue in self.issues],
            "checked_facts_count": len(self.checked_facts)
        }


class FabricationDetector:
    """防编造检测器"""
    
    # 常见姓氏列表（500个）- 与fact_extractor保持一致
    COMMON_SURNAMES = [
        # 前100大姓
        "王", "李", "张", "刘", "陈", "杨", "黄", "赵", "吴", "周",
        "徐", "孙", "马", "朱", "胡", "郭", "何", "林", "罗", "高",
        "郑", "梁", "谢", "宋", "唐", "许", "邓", "冯", "韩", "曹",
        "曾", "彭", "萧", "蔡", "潘", "田", "董", "袁", "于", "余",
        "叶", "蒋", "杜", "苏", "魏", "程", "吕", "丁", "沈", "任",
        "姚", "卢", "傅", "钟", "姜", "崔", "谭", "廖", "范", "汪",
        "陆", "金", "石", "戴", "贾", "韦", "夏", "邱", "方", "侯",
        "邹", "熊", "孟", "秦", "白", "江", "阎", "薛", "尹", "段",
        "雷", "黎", "史", "龙", "贺", "顾", "毛", "郝", "龚", "邵",
        "万", "钱", "严", "覃", "武", "戚", "柳", "乔", "齐", "欧阳",
        # 101-200
        "洪", "康", "施", "龚", "颜", "倪", "龙", "万", "段", "雷",
        "钱", "汤", "尹", "黎", "易", "常", "武", "乔", "贺", "赖",
        "龚", "文", "庞", "樊", "兰", "殷", "施", "陶", "洪", "翟",
        "安", "颜", "倪", "严", "温", "芦", "季", "俞", "章", "鲁",
        "葛", "伍", "韦", "申", "尚", "董", "傅", "卜", "戚", "乌",
        "焦", "巴", "弓", "牧", "隗", "山", "谷", "车", "侯", "宓",
        "蓬", "全", "郗", "班", "仰", "秋", "仲", "伊", "宫", "宁",
        "仇", "栾", "暴", "甘", "钭", "厉", "戎", "祖", "武", "符",
        "刘", "景", "詹", "束", "龙", "叶", "幸", "司", "韶", "郜",
        "黎", "蓟", "薄", "印", "宿", "白", "怀", "蒲", "台", "丛",
        # 201-300
        "鄂", "索", "咸", "籍", "赖", "卓", "蔺", "屠", "蒙", "池",
        "乔", "阴", "郁", "胥", "能", "苍", "双", "闻", "莘", "党",
        "翟", "谭", "贡", "劳", "逄", "姬", "申", "扶", "堵", "冉",
        "宰", "郦", "雍", "却", "璩", "桑", "桂", "濮", "牛", "寿",
        "通", "边", "扈", "燕", "冀", "郏", "浦", "尚", "农", "温",
        "别", "庄", "晏", "柴", "瞿", "阎", "充", "慕", "连", "茹",
        "习", "宦", "艾", "鱼", "容", "向", "古", "易", "慎", "戈",
        "廖", "庚", "终", "暨", "居", "衡", "步", "都", "耿", "满",
        "弘", "匡", "国", "文", "寇", "广", "禄", "阙", "东", "殴",
        "殳", "沃", "利", "蔚", "越", "夔", "隆", "师", "巩", "厍",
        # 301-400
        "聂", "晁", "勾", "敖", "融", "冷", "訾", "辛", "阚", "那",
        "简", "饶", "空", "曾", "毋", "沙", "乜", "养", "鞠", "须",
        "丰", "巢", "关", "蒯", "相", "查", "後", "荆", "红", "游",
        "竺", "权", "逯", "盖", "益", "桓", "公", "万俟", "司马", "上官",
        "欧阳", "夏侯", "诸葛", "闻人", "东方", "赫连", "皇甫", "尉迟", "公羊", "澹台",
        "公冶", "宗政", "濮阳", "淳于", "单于", "太叔", "申屠", "公孙", "仲孙", "轩辕",
        "令狐", "钟离", "宇文", "长孙", "慕容", "鲜于", "闾丘", "司徒", "司空", "亓官",
        "司寇", "仉", "督", "子车", "颛孙", "端木", "巫马", "公西", "漆雕", "乐正",
        "壤驷", "公良", "拓跋", "夹谷", "宰父", "谷梁", "晋", "楚", "闫", "法",
        "汝", "鄢", "涂", "钦", "段干", "百里", "东郭", "南门", "呼延", "归海",
        # 401-500
        "羊舌", "微生", "岳", "帅", "缑", "亢", "况", "郈", "有", "琴",
        "梁丘", "左丘", "东门", "西门", "商", "牟", "佘", "佴", "伯", "赏",
        "南宫", "墨", "哈", "谯", "笪", "年", "爱", "阳", "佟", "言",
        "福", "南", "火", "铁", "迟", "漆", "卞", "康", "韦", "昌",
        "苗", "凤", "花", "方", "俞", "任", "袁", "柳", "酆", "鲍",
        "史", "唐", "费", "廉", "岑", "薛", "雷", "贺", "倪", "汤",
        "滕", "殷", "罗", "毕", "郝", "邬", "安", "常", "乐", "于",
        "时", "傅", "皮", "卞", "齐", "康", "伍", "余", "元", "卜",
        "顾", "孟", "平", "黄", "和", "穆", "萧", "尹", "姚", "邵",
        "湛", "汪", "祁", "毛", "禹", "狄", "米", "贝", "明", "臧",
    ]
    
    # 标准部门名称列表（30个）
    STANDARD_DEPARTMENTS = [
        "总经理办公室",
        "行政部",
        "人力资源部",
        "财务部",
        "采购部",
        "销售部",
        "市场部",
        "生产部",
        "质量管理部",
        "技术研发部",
        "工程部",
        "设备部",
        "安全环保部",
        "仓储物流部",
        "客户服务部",
        "审计部",
        "法务部",
        "信息技术部",
        "战略规划部",
        "品牌推广部",
        "供应链管理部",
        "品质保证部",
        "检验检测中心",
        "研发中心",
        "实验室",
        "培训中心",
        "售后服务部",
        "进出口部",
        "项目管理部",
        "综合管理部"
    ]
    
    # 通用编造短语列表（25个）
    GENERIC_FABRICATION_PHRASES = [
        "某某某",
        "XXX",
        "待填写",
        "待补充",
        "待完善",
        "待确定",
        "待确认",
        "请填写",
        "请补充",
        "请完善",
        "根据实际情况",
        "按照相关规定",
        "参照相关标准",
        "符合相关要求",
        "满足相关条件",
        "具体内容待定",
        "具体数据待确认",
        "以实际情况为准",
        "根据企业实际情况填写",
        "按企业具体情况进行调整",
        "此处需要补充具体内容",
        "此处需要填写相关信息",
        "具体信息请参考相关文件",
        "详细内容请参见相关资料",
        "相关信息请咨询相关部门"
    ]
    
    # 模板填充词
    TEMPLATE_FILLERS = [
        "【", "】", "{", "}", "___", "____", "...", "……",
        "（请填写）", "（待填写）", "（需补充）", "（示例）"
    ]
    
    # 可疑数字模式
    SUSPICIOUS_NUMBER_PATTERNS = [
        r'\d{10,}',  # 过长的数字
        r'\d{4}年\d{2}月\d{2}日',  # 日期格式
        r'电话[：:]\s*\d{3,4}-\d{7,8}',  # 电话格式
    ]
    
    def __init__(self, fact_extractor: Optional[FactExtractor] = None):
        """
        初始化防编造检测器
        
        Args:
            fact_extractor: 事实提取器实例（可选）
        """
        self.fact_extractor = fact_extractor or FactExtractor()
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        # 编译通用短语模式
        self.generic_phrase_pattern = re.compile(
            '|'.join(re.escape(phrase) for phrase in self.GENERIC_FABRICATION_PHRASES)
        )
        
        # 编译模板填充词模式
        self.template_filler_pattern = re.compile(
            '|'.join(re.escape(filler) for filler in self.TEMPLATE_FILLERS)
        )
        
        # 编译人名模式
        self.person_name_pattern = re.compile(
            r'(?:负责人|经理|主管|主任|工程师|技术员|操作员|员工|联系人)[：:]\s*([^\s，。！？、]{2,4})'
        )
        
        # 编译部门模式
        self.department_pattern = re.compile(
            r'([^\s，。！？、]*(?:部|处|科|室|中心|组|班|车间))'
        )
        
        # 编译模糊引用模式
        self.vague_reference_pattern = re.compile(
            r'(?:根据|按照|参照|依据)[^，。！？]{0,10}(?:相关|相应|有关|一定)'
        )
    
    def detect_fabrication(
        self, 
        text: str, 
        known_facts: Optional[List[Fact]] = None,
        strict_mode: bool = False
    ) -> FabricationReport:
        """
        检测编造内容
        
        Args:
            text: 待检测文本
            known_facts: 已知事实列表（用于对比验证）
            strict_mode: 是否启用严格模式
            
        Returns:
            编造检测报告
        """
        issues = []
        issue_id_counter = 0
        
        # 1. 检查通用短语
        generic_issues = self.check_generic_phrases(text)
        for issue in generic_issues:
            issue.issue_id = f"issue_{issue_id_counter}"
            issue_id_counter += 1
            issues.append(issue)
        
        # 2. 检查模板填充内容
        template_issues = self._check_template_fillers(text)
        for issue in template_issues:
            issue.issue_id = f"issue_{issue_id_counter}"
            issue_id_counter += 1
            issues.append(issue)
        
        # 3. 提取并验证人名
        person_issues = self._check_person_names(text, known_facts)
        for issue in person_issues:
            issue.issue_id = f"issue_{issue_id_counter}"
            issue_id_counter += 1
            issues.append(issue)
        
        # 4. 提取并验证部门名称
        dept_issues = self._check_department_names(text, known_facts)
        for issue in dept_issues:
            issue.issue_id = f"issue_{issue_id_counter}"
            issue_id_counter += 1
            issues.append(issue)
        
        # 5. 检查数据点
        data_issues = self._check_data_points(text, known_facts)
        for issue in data_issues:
            issue.issue_id = f"issue_{issue_id_counter}"
            issue_id_counter += 1
            issues.append(issue)
        
        # 6. 检查模糊引用
        vague_issues = self._check_vague_references(text)
        for issue in vague_issues:
            issue.issue_id = f"issue_{issue_id_counter}"
            issue_id_counter += 1
            issues.append(issue)
        
        # 7. 检查一致性
        if known_facts:
            consistency_issues = self.check_consistency(text, known_facts)
            for issue in consistency_issues:
                issue.issue_id = f"issue_{issue_id_counter}"
                issue_id_counter += 1
                issues.append(issue)
        
        # 8. 严格模式额外检查
        if strict_mode:
            strict_issues = self._strict_mode_checks(text)
            for issue in strict_issues:
                issue.issue_id = f"issue_{issue_id_counter}"
                issue_id_counter += 1
                issues.append(issue)
        
        # 生成报告
        report = self._generate_report(text, issues, known_facts)
        
        logger.info(f"检测完成，发现 {len(issues)} 个潜在问题")
        return report
    
    def check_generic_phrases(self, text: str) -> List[FabricationIssue]:
        """
        检查通用短语
        
        Args:
            text: 待检测文本
            
        Returns:
            问题列表
        """
        issues = []
        
        matches = self.generic_phrase_pattern.finditer(text)
        for match in matches:
            phrase = match.group()
            issue = FabricationIssue(
                issue_id="",
                fabrication_type=FabricationType.GENERIC_PHRASE,
                severity=Severity.MEDIUM,
                content=phrase,
                position=(match.start(), match.end()),
                description=f"发现通用编造短语: '{phrase}'",
                suggestion="请替换为具体、明确的内容",
                confidence=0.9
            )
            issues.append(issue)
        
        return issues
    
    def _check_template_fillers(self, text: str) -> List[FabricationIssue]:
        """检查模板填充内容"""
        issues = []
        
        matches = self.template_filler_pattern.finditer(text)
        for match in matches:
            filler = match.group()
            issue = FabricationIssue(
                issue_id="",
                fabrication_type=FabricationType.TEMPLATE_FILLER,
                severity=Severity.HIGH,
                content=filler,
                position=(match.start(), match.end()),
                description=f"发现模板填充内容: '{filler}'",
                suggestion="请填写实际内容或删除此占位符",
                confidence=0.95
            )
            issues.append(issue)
        
        return issues
    
    def _check_person_names(
        self, 
        text: str, 
        known_facts: Optional[List[Fact]] = None
    ) -> List[FabricationIssue]:
        """检查人名"""
        issues = []
        known_persons = set()
        
        # 收集已知人名
        if known_facts:
            for fact in known_facts:
                if fact.fact_type == FactType.PERSON_NAME:
                    known_persons.add(fact.content)
        
        # 提取文本中的人名
        matches = self.person_name_pattern.finditer(text)
        for match in matches:
            name = match.group(1)
            
            # 检查是否为有效人名
            if not self._is_valid_person_name(name):
                issue = FabricationIssue(
                    issue_id="",
                    fabrication_type=FabricationType.HALLUCINATED_NAME,
                    severity=Severity.HIGH,
                    content=name,
                    position=(match.start(), match.end()),
                    description=f"可能为编造的人名: '{name}'",
                    suggestion="请核实此人名是否正确，或使用实际姓名",
                    confidence=0.7
                )
                issues.append(issue)
            elif known_persons and name not in known_persons:
                # 如果有已知人名列表，检查是否在其中
                issue = FabricationIssue(
                    issue_id="",
                    fabrication_type=FabricationType.UNVERIFIABLE_CLAIM,
                    severity=Severity.MEDIUM,
                    content=name,
                    position=(match.start(), match.end()),
                    description=f"人名 '{name}' 不在已知人员列表中",
                    suggestion="请核实此人名是否为实际员工姓名",
                    confidence=0.6,
                    metadata={"known_persons": list(known_persons)}
                )
                issues.append(issue)
        
        return issues
    
    def _is_valid_person_name(self, name: str) -> bool:
        """验证是否为有效人名"""
        if not name or len(name) < 2 or len(name) > 4:
            return False
        
        # 检查是否以常见姓氏开头
        has_valid_surname = any(name.startswith(surname) for surname in self.COMMON_SURNAMES)
        if not has_valid_surname:
            return False
        
        # 检查是否包含非姓名字符
        invalid_chars = ['公司', '部门', '企业', '有限', '责任', '集团', '股份', '某某']
        if any(char in name for char in invalid_chars):
            return False
        
        return True
    
    def _check_department_names(
        self, 
        text: str, 
        known_facts: Optional[List[Fact]] = None
    ) -> List[FabricationIssue]:
        """检查部门名称"""
        issues = []
        known_depts = set()
        
        # 收集已知部门
        if known_facts:
            for fact in known_facts:
                if fact.fact_type == FactType.DEPARTMENT:
                    known_depts.add(fact.content)
        
        # 提取文本中的部门名称
        matches = self.department_pattern.finditer(text)
        for match in matches:
            dept_name = match.group(1)
            
            # 检查是否为标准部门名称
            is_standard = dept_name in self.STANDARD_DEPARTMENTS
            
            # 检查是否为有效部门名称
            if not self._is_valid_department(dept_name):
                continue  # 跳过无效匹配
            
            if not is_standard and known_depts and dept_name not in known_depts:
                issue = FabricationIssue(
                    issue_id="",
                    fabrication_type=FabricationType.HALLUCINATED_DEPT,
                    severity=Severity.MEDIUM,
                    content=dept_name,
                    position=(match.start(), match.end()),
                    description=f"部门名称 '{dept_name}' 不是标准部门名称，也不在已知部门列表中",
                    suggestion="请核实部门名称是否正确，或使用标准部门名称",
                    confidence=0.6,
                    metadata={
                        "standard_departments": self.STANDARD_DEPARTMENTS[:10],
                        "known_departments": list(known_depts)
                    }
                )
                issues.append(issue)
        
        return issues
    
    def _is_valid_department(self, dept_name: str) -> bool:
        """验证是否为有效部门名称"""
        if not dept_name or len(dept_name) < 3:
            return False
        
        invalid_patterns = ['全部', '部分', '大部', '支部', '支部书记', '大部分', '小部分']
        if any(pattern in dept_name for pattern in invalid_patterns):
            return False
        
        return True
    
    def verify_data_point(
        self, 
        data_point: str, 
        expected_type: str,
        known_facts: Optional[List[Fact]] = None
    ) -> Dict[str, Any]:
        """
        验证数据点
        
        Args:
            data_point: 数据点内容
            expected_type: 期望类型 (number, date, phone, email等)
            known_facts: 已知事实列表
            
        Returns:
            验证结果
        """
        result = {
            "data_point": data_point,
            "expected_type": expected_type,
            "is_valid": True,
            "issues": [],
            "confidence": 1.0
        }
        
        # 类型验证
        type_validators = {
            "number": self._validate_number,
            "date": self._validate_date,
            "phone": self._validate_phone,
            "email": self._validate_email,
            "percentage": self._validate_percentage
        }
        
        validator = type_validators.get(expected_type)
        if validator:
            validation_result = validator(data_point)
            result["is_valid"] = validation_result["is_valid"]
            result["issues"].extend(validation_result["issues"])
            result["confidence"] = validation_result["confidence"]
        
        # 与已知事实对比
        if known_facts and result["is_valid"]:
            for fact in known_facts:
                if fact.content == data_point:
                    result["matched_fact"] = fact.fact_id
                    result["confidence"] = 1.0
                    break
        
        return result
    
    def _validate_number(self, value: str) -> Dict[str, Any]:
        """验证数字"""
        result = {"is_valid": True, "issues": [], "confidence": 1.0}
        
        try:
            num = float(value.replace(',', '').replace('，', ''))
            
            # 检查是否为异常数字
            if num < 0:
                result["issues"].append("数字为负数，请确认是否正确")
                result["confidence"] = 0.8
            
            if num > 1000000:
                result["issues"].append("数字过大，请确认是否正确")
                result["confidence"] = 0.7
            
        except ValueError:
            result["is_valid"] = False
            result["issues"].append("不是有效的数字格式")
            result["confidence"] = 0.3
        
        return result
    
    def _validate_date(self, value: str) -> Dict[str, Any]:
        """验证日期"""
        result = {"is_valid": True, "issues": [], "confidence": 1.0}
        
        date_patterns = [
            r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?',
            r'\d{1,2}[-/月]\d{1,2}[-/日]?'
        ]
        
        matched = False
        for pattern in date_patterns:
            if re.match(pattern, value):
                matched = True
                break
        
        if not matched:
            result["is_valid"] = False
            result["issues"].append("不是有效的日期格式")
            result["confidence"] = 0.3
        
        return result
    
    def _validate_phone(self, value: str) -> Dict[str, Any]:
        """验证电话号码"""
        result = {"is_valid": True, "issues": [], "confidence": 1.0}
        
        # 清理格式
        cleaned = re.sub(r'[\s\-()]', '', value)
        
        # 手机号验证
        if re.match(r'1[3-9]\d{9}', cleaned):
            return result
        
        # 固定电话验证
        if re.match(r'\d{3,4}\d{7,8}', cleaned):
            return result
        
        result["is_valid"] = False
        result["issues"].append("不是有效的电话号码格式")
        result["confidence"] = 0.3
        
        return result
    
    def _validate_email(self, value: str) -> Dict[str, Any]:
        """验证邮箱"""
        result = {"is_valid": True, "issues": [], "confidence": 1.0}
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, value):
            result["is_valid"] = False
            result["issues"].append("不是有效的邮箱格式")
            result["confidence"] = 0.3
        
        return result
    
    def _validate_percentage(self, value: str) -> Dict[str, Any]:
        """验证百分比"""
        result = {"is_valid": True, "issues": [], "confidence": 1.0}
        
        try:
            # 移除百分号
            num_str = value.replace('%', '').replace('％', '')
            num = float(num_str)
            
            if num < 0 or num > 100:
                result["issues"].append("百分比超出合理范围(0-100)")
                result["confidence"] = 0.6
            
        except ValueError:
            result["is_valid"] = False
            result["issues"].append("不是有效的百分比格式")
            result["confidence"] = 0.3
        
        return result
    
    def _check_data_points(
        self, 
        text: str, 
        known_facts: Optional[List[Fact]] = None
    ) -> List[FabricationIssue]:
        """检查数据点"""
        issues = []
        
        # 检查人数数据
        employee_pattern = re.compile(r'(?:员工|职工|人员)[：:]*\s*(\d+)[人名]?')
        matches = employee_pattern.finditer(text)
        for match in matches:
            count = int(match.group(1))
            
            # 检查是否为合理范围
            if count <= 0:
                issue = FabricationIssue(
                    issue_id="",
                    fabrication_type=FabricationType.HALLUCINATED_NUMBER,
                    severity=Severity.HIGH,
                    content=match.group(0),
                    position=(match.start(), match.end()),
                    description=f"员工人数 {count} 不合理（应为正数）",
                    suggestion="请核实员工人数",
                    confidence=0.9
                )
                issues.append(issue)
            elif count > 100000:
                issue = FabricationIssue(
                    issue_id="",
                    fabrication_type=FabricationType.HALLUCINATED_NUMBER,
                    severity=Severity.MEDIUM,
                    content=match.group(0),
                    position=(match.start(), match.end()),
                    description=f"员工人数 {count} 异常大，请确认",
                    suggestion="请核实员工人数是否正确",
                    confidence=0.7
                )
                issues.append(issue)
        
        # 检查电话号码
        phone_pattern = re.compile(r'(?:电话|手机|联系方式)[：:]\s*(\d[\d\-]{7,18})')
        matches = phone_pattern.finditer(text)
        for match in matches:
            phone = match.group(1)
            validation = self._validate_phone(phone)
            
            if not validation["is_valid"]:
                issue = FabricationIssue(
                    issue_id="",
                    fabrication_type=FabricationType.HALLUCINATED_NUMBER,
                    severity=Severity.MEDIUM,
                    content=phone,
                    position=(match.start(), match.end()),
                    description=f"电话号码格式可能不正确: {phone}",
                    suggestion="请核实电话号码格式",
                    confidence=validation["confidence"]
                )
                issues.append(issue)
        
        return issues
    
    def _check_vague_references(self, text: str) -> List[FabricationIssue]:
        """检查模糊引用"""
        issues = []
        
        matches = self.vague_reference_pattern.finditer(text)
        for match in matches:
            phrase = match.group()
            issue = FabricationIssue(
                issue_id="",
                fabrication_type=FabricationType.VAGUE_REFERENCE,
                severity=Severity.LOW,
                content=phrase,
                position=(match.start(), match.end()),
                description=f"发现模糊引用: '{phrase}'",
                suggestion="建议明确指出具体的标准、规定或文件名称",
                confidence=0.7
            )
            issues.append(issue)
        
        return issues
    
    def check_consistency(
        self, 
        text: str, 
        known_facts: List[Fact]
    ) -> List[FabricationIssue]:
        """
        检查一致性
        
        Args:
            text: 待检测文本
            known_facts: 已知事实列表
            
        Returns:
            问题列表
        """
        issues = []
        
        # 提取文本中的事实
        extracted_facts = self.fact_extractor.extract_from_text(text)
        
        # 按类型分组
        facts_by_type: Dict[FactType, List[Fact]] = {}
        for fact in extracted_facts:
            if fact.fact_type not in facts_by_type:
                facts_by_type[fact.fact_type] = []
            facts_by_type[fact.fact_type].append(fact)
        
        # 检查每种类型的一致性
        for fact_type, facts in facts_by_type.items():
            if len(facts) > 1:
                # 检查同一类型的事实是否有冲突
                contents = [f.content for f in facts]
                unique_contents = set(contents)
                
                if len(unique_contents) > 1:
                    # 存在不一致
                    issue = FabricationIssue(
                        issue_id="",
                        fabrication_type=FabricationType.INCONSISTENT_DATA,
                        severity=Severity.HIGH,
                        content=", ".join(unique_contents),
                        position=(0, len(text)),
                        description=f"发现{fact_type.value}数据不一致: {', '.join(unique_contents)}",
                        suggestion="请核实并统一相关数据",
                        confidence=0.85,
                        related_facts=[f.fact_id for f in facts]
                    )
                    issues.append(issue)
        
        # 与已知事实对比
        for extracted in extracted_facts:
            for known in known_facts:
                if extracted.fact_type == known.fact_type:
                    if extracted.content != known.content:
                        # 检查是否为相似但不完全相同的内容
                        similarity = self._calculate_similarity(extracted.content, known.content)
                        if similarity < 0.8:  # 相似度低于80%
                            issue = FabricationIssue(
                                issue_id="",
                                fabrication_type=FabricationType.INCONSISTENT_DATA,
                                severity=Severity.MEDIUM,
                                content=extracted.content,
                                position=extracted.position,
                                description=f"{extracted.fact_type.value}与已知事实不一致。已知: '{known.content}', 文本中: '{extracted.content}'",
                                suggestion="请核实数据是否正确",
                                confidence=0.75,
                                related_facts=[known.fact_id]
                            )
                            issues.append(issue)
        
        return issues
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """计算字符串相似度"""
        if not str1 or not str2:
            return 0.0
        
        # 简单的字符级相似度
        set1 = set(str1)
        set2 = set(str2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _strict_mode_checks(self, text: str) -> List[FabricationIssue]:
        """严格模式额外检查"""
        issues = []
        
        # 检查推测性内容
        speculation_patterns = [
            r'(?:可能|也许|大概|或许|估计|猜测)',
            r'(?:应该|可能)是[^\s，。！？、]+',
            r'(?:我认为|我觉得|我估计)'
        ]
        
        for pattern in speculation_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                issue = FabricationIssue(
                    issue_id="",
                    fabrication_type=FabricationType.SPECULATION,
                    severity=Severity.LOW,
                    content=match.group(),
                    position=(match.start(), match.end()),
                    description="发现推测性内容",
                    suggestion="建议使用确定性的表述，或明确标注为推测",
                    confidence=0.6
                )
                issues.append(issue)
        
        # 检查缺少来源的声明
        claim_patterns = [
            r'(?:根据|按照|依据)[^，。！？]{5,30}(?:规定|要求|标准)',
            r'(?:符合|满足)[^，。！？]{5,20}(?:要求|条件|标准)'
        ]
        
        for pattern in claim_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                # 检查是否有具体的引用来源
                context_start = max(0, match.start() - 50)
                context = text[context_start:match.end() + 50]
                
                if not re.search(r'(?:GB|ISO|标准|文件|规定|办法)', context):
                    issue = FabricationIssue(
                        issue_id="",
                        fabrication_type=FabricationType.MISSING_SOURCE,
                        severity=Severity.MEDIUM,
                        content=match.group(),
                        position=(match.start(), match.end()),
                        description="声明缺少具体来源引用",
                        suggestion="建议添加具体的标准编号或文件名称",
                        confidence=0.65
                    )
                    issues.append(issue)
        
        return issues
    
    def _generate_report(
        self, 
        text: str, 
        issues: List[FabricationIssue],
        known_facts: Optional[List[Fact]] = None
    ) -> FabricationReport:
        """生成检测报告"""
        # 统计问题类型
        issues_by_type: Dict[str, int] = {}
        for issue in issues:
            type_name = issue.fabrication_type.value
            issues_by_type[type_name] = issues_by_type.get(type_name, 0) + 1
        
        # 统计严重程度
        issues_by_severity: Dict[str, int] = {}
        for issue in issues:
            severity_name = issue.severity.value
            issues_by_severity[severity_name] = issues_by_severity.get(severity_name, 0) + 1
        
        # 计算总体分数
        # 基础分100，每个问题扣分
        base_score = 100
        severity_weights = {
            Severity.LOW: 2,
            Severity.MEDIUM: 5,
            Severity.HIGH: 10,
            Severity.CRITICAL: 20
        }
        
        total_deduction = sum(severity_weights.get(issue.severity, 5) for issue in issues)
        overall_score = max(0, base_score - total_deduction)
        
        # 生成报告ID
        report_id = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return FabricationReport(
            report_id=report_id,
            text=text,
            issues=issues,
            total_issues=len(issues),
            issues_by_type=issues_by_type,
            issues_by_severity=issues_by_severity,
            overall_score=overall_score,
            checked_facts=known_facts or []
        )
    
    def get_fabrication_summary(self, report: FabricationReport) -> str:
        """
        获取编造检测摘要
        
        Args:
            report: 检测报告
            
        Returns:
            摘要文本
        """
        lines = [
            f"=== 防编造检测报告 ===",
            f"报告ID: {report.report_id}",
            f"检测时间: {report.checked_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"总体评分: {report.overall_score}/100",
            f"发现问题: {report.total_issues} 个",
            f"",
            f"问题类型分布:"
        ]
        
        for type_name, count in report.issues_by_type.items():
            lines.append(f"  - {type_name}: {count} 个")
        
        lines.append(f"")
        lines.append(f"严重程度分布:")
        
        for severity, count in report.issues_by_severity.items():
            lines.append(f"  - {severity}: {count} 个")
        
        if report.overall_score >= 80:
            lines.append(f"")
            lines.append(f"评估结果: 内容质量良好，无明显编造风险")
        elif report.overall_score >= 60:
            lines.append(f"")
            lines.append(f"评估结果: 内容存在一定问题，建议核查")
        else:
            lines.append(f"")
            lines.append(f"评估结果: 内容存在较多问题，需要重点审核")
        
        return "\n".join(lines)
    
    def export_report(self, report: FabricationReport, output_path: str) -> bool:
        """
        导出检测报告
        
        Args:
            report: 检测报告
            output_path: 输出路径
            
        Returns:
            是否成功
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"报告已导出至: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出报告失败: {e}")
            return False
