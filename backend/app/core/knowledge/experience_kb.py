"""
L2 经验知识库模块

实现第二层知识库 - 经验知识层，包含:
- 行业最佳实践
- 常见问题解决方案
- 审核要点和技巧
- 行业特定经验

特点:
- 实践性: 来源于实际工作经验
- 行业性: 针对不同行业特点
- 指导性: 为实际工作提供参考
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .knowledge_base import (
    KnowledgeBase,
    KnowledgeItem,
    KnowledgeLevel,
    KnowledgeQuery,
    KnowledgeResult,
)


class IndustryType(Enum):
    """行业类型枚举"""
    MANUFACTURING = "制造业"
    SERVICE = "服务业"
    CONSTRUCTION = "建筑业"
    IT_SOFTWARE = "IT软件"
    HEALTHCARE = "医疗健康"
    EDUCATION = "教育"
    FINANCE = "金融"
    LOGISTICS = "物流运输"
    FOOD = "食品饮料"
    CHEMICAL = "化工"
    GENERAL = "通用"


class ExperienceType(Enum):
    """经验类型枚举"""
    BEST_PRACTICE = "最佳实践"
    COMMON_ISSUE = "常见问题"
    AUDIT_POINT = "审核要点"
    SOLUTION = "解决方案"
    CASE_STUDY = "案例分析"
    LESSON_LEARNED = "经验教训"


@dataclass
class BestPractice:
    """
    最佳实践数据类
    
    Attributes:
        title: 实践标题
        description: 实践描述
        applicable_standards: 适用标准
        industry: 适用行业
        implementation_steps: 实施步骤
        benefits: 预期收益
        risks: 潜在风险
        references: 参考资料
    """
    
    title: str
    description: str
    applicable_standards: List[str] = field(default_factory=list)
    industry: str = "通用"
    implementation_steps: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    
    def to_knowledge_item(self) -> KnowledgeItem:
        """转换为知识项"""
        content = f"""
## 最佳实践: {self.title}

### 描述
{self.description}

### 适用标准
{', '.join(self.applicable_standards) if self.applicable_standards else '通用'}

### 适用行业
{self.industry}

### 实施步骤
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(self.implementation_steps))}

### 预期收益
{chr(10).join(f'- {b}' for b in self.benefits)}

### 潜在风险
{chr(10).join(f'- {r}' for r in self.risks) if self.risks else '无明显风险'}

### 参考资料
{chr(10).join(f'- {ref}' for ref in self.references) if self.references else '无'}
"""
        
        return KnowledgeItem(
            level=KnowledgeLevel.L2_EXPERIENCE,
            title=f"最佳实践: {self.title}",
            content=content.strip(),
            category="最佳实践",
            tags=["最佳实践", self.industry] + self.applicable_standards,
            source="行业经验积累",
            industry=self.industry,
            confidence=0.9,
            metadata={
                "experience_type": "best_practice",
                "applicable_standards": self.applicable_standards,
                "implementation_steps": self.implementation_steps,
                "benefits": self.benefits,
                "risks": self.risks,
            }
        )


@dataclass
class CommonIssue:
    """
    常见问题数据类
    
    Attributes:
        title: 问题标题
        description: 问题描述
        standard_clause: 相关标准条款
        root_cause: 根本原因
        solution: 解决方案
        prevention: 预防措施
        severity: 严重程度 (高/中/低)
        frequency: 发生频率
    """
    
    title: str
    description: str
    standard_clause: str = ""
    root_cause: str = ""
    solution: str = ""
    prevention: str = ""
    severity: str = "中"
    frequency: str = "常见"
    
    def to_knowledge_item(self) -> KnowledgeItem:
        """转换为知识项"""
        content = f"""
## 常见问题: {self.title}

### 问题描述
{self.description}

### 相关标准条款
{self.standard_clause if self.standard_clause else '通用问题'}

### 根本原因
{self.root_cause if self.root_cause else '待分析'}

### 解决方案
{self.solution if self.solution else '待确定'}

### 预防措施
{self.prevention if self.prevention else '待制定'}

### 问题等级
- 严重程度: {self.severity}
- 发生频率: {self.frequency}
"""
        
        return KnowledgeItem(
            level=KnowledgeLevel.L2_EXPERIENCE,
            title=f"常见问题: {self.title}",
            content=content.strip(),
            category="常见问题",
            tags=["常见问题", self.severity, self.frequency],
            source="审核经验总结",
            standard_ref=self.standard_clause,
            confidence=0.85,
            metadata={
                "experience_type": "common_issue",
                "root_cause": self.root_cause,
                "solution": self.solution,
                "prevention": self.prevention,
                "severity": self.severity,
                "frequency": self.frequency,
            }
        )


@dataclass
class AuditPoint:
    """
    审核要点数据类
    
    Attributes:
        title: 审核要点标题
        standard_clause: 相关标准条款
        audit_questions: 审核问题列表
        evidence_required: 所需证据
        common_nonconformities: 常见不符合
        audit_tips: 审核技巧
        industry_specific: 行业特定要求
    """
    
    title: str
    standard_clause: str
    audit_questions: List[str] = field(default_factory=list)
    evidence_required: List[str] = field(default_factory=list)
    common_nonconformities: List[str] = field(default_factory=list)
    audit_tips: List[str] = field(default_factory=list)
    industry_specific: str = ""
    
    def to_knowledge_item(self) -> KnowledgeItem:
        """转换为知识项"""
        content = f"""
## 审核要点: {self.title}

### 相关标准条款
{self.standard_clause}

### 审核问题
{chr(10).join(f'- {q}' for q in self.audit_questions)}

### 所需证据
{chr(10).join(f'- {e}' for e in self.evidence_required)}

### 常见不符合
{chr(10).join(f'- {n}' for n in self.common_nonconformities) if self.common_nonconformities else '无特定不符合'}

### 审核技巧
{chr(10).join(f'- {t}' for t in self.audit_tips) if self.audit_tips else '无特定技巧'}

### 行业特定要求
{self.industry_specific if self.industry_specific else '无特定要求'}
"""
        
        return KnowledgeItem(
            level=KnowledgeLevel.L2_EXPERIENCE,
            title=f"审核要点: {self.title}",
            content=content.strip(),
            category="审核要点",
            tags=["审核要点", self.standard_clause],
            source="审核经验积累",
            standard_ref=self.standard_clause,
            confidence=0.95,
            metadata={
                "experience_type": "audit_point",
                "audit_questions": self.audit_questions,
                "evidence_required": self.evidence_required,
                "common_nonconformities": self.common_nonconformities,
                "audit_tips": self.audit_tips,
            }
        )


class ExperienceKB(KnowledgeBase):
    """
    L2 经验知识库
    
    管理行业经验知识，包括:
    - 最佳实践库
    - 常见问题库
    - 审核要点库
    - 行业特定经验
    
    特点:
    - 基于实践经验积累
    - 按行业分类管理
    - 持续更新完善
    """
    
    def __init__(self):
        """初始化经验知识库"""
        super().__init__(KnowledgeLevel.L2_EXPERIENCE)
        self._best_practices: Dict[str, BestPractice] = {}
        self._common_issues: Dict[str, CommonIssue] = {}
        self._audit_points: Dict[str, AuditPoint] = {}
    
    def initialize(self) -> bool:
        """
        初始化经验知识库
        
        Returns:
            初始化是否成功
        """
        try:
            items = self.load_knowledge()
            for item in items:
                self.add_item(item)
            
            self._initialized = True
            return True
        except Exception as e:
            print(f"经验知识库初始化失败: {e}")
            return False
    
    def load_knowledge(self) -> List[KnowledgeItem]:
        """
        加载经验知识数据
        
        Returns:
            经验知识项列表
        """
        items = []
        
        # 加载最佳实践
        practices = self._load_best_practices()
        for bp_id, practice in practices.items():
            self._best_practices[bp_id] = practice
            items.append(practice.to_knowledge_item())
        
        # 加载常见问题
        issues = self._load_common_issues()
        for issue_id, issue in issues.items():
            self._common_issues[issue_id] = issue
            items.append(issue.to_knowledge_item())
        
        # 加载审核要点
        audit_points = self._load_audit_points()
        for ap_id, audit_point in audit_points.items():
            self._audit_points[ap_id] = audit_point
            items.append(audit_point.to_knowledge_item())
        
        return items
    
    def _load_best_practices(self) -> Dict[str, BestPractice]:
        """加载最佳实践"""
        practices = {
            "bp_001": BestPractice(
                title="过程方法实施",
                description="采用过程方法建立和实施管理体系，确保过程间的相互作用得到识别和管理。",
                applicable_standards=["ISO 9001", "ISO 14001", "ISO 45001"],
                industry="通用",
                implementation_steps=[
                    "识别组织所需的所有过程",
                    "确定过程的顺序和相互作用",
                    "确定过程运行和控制所需的准则和方法",
                    "确保获得必要的资源和信息",
                    "监视、测量和分析过程",
                    "实施必要的措施实现策划的结果",
                ],
                benefits=[
                    "提高过程效率",
                    "减少接口问题",
                    "增强体系协调性",
                    "便于持续改进",
                ],
                risks=[
                    "过程识别不完整",
                    "接口管理不到位",
                ],
                references=["ISO 9001 条款 4.4", "ISO 9001 条款 8.1"],
            ),
            "bp_002": BestPractice(
                title="风险思维融入日常管理",
                description="将风险思维融入组织的各项活动和过程，主动识别和管理风险。",
                applicable_standards=["ISO 9001", "ISO 14001", "ISO 45001"],
                industry="通用",
                implementation_steps=[
                    "建立风险识别机制",
                    "制定风险评价方法",
                    "确定风险应对措施",
                    "将风险管理融入过程控制",
                    "定期评审风险状态",
                ],
                benefits=[
                    "预防问题发生",
                    "提高决策质量",
                    "增强组织韧性",
                ],
                risks=[
                    "风险识别不全面",
                    "应对措施不落实",
                ],
                references=["ISO 9001 条款 6.1", "ISO 45001 条款 6.1"],
            ),
            "bp_003": BestPractice(
                title="内部审核有效性提升",
                description="通过系统化的方法提升内部审核的有效性和价值。",
                applicable_standards=["ISO 9001", "ISO 14001", "ISO 45001"],
                industry="通用",
                implementation_steps=[
                    "制定年度审核计划",
                    "培训合格的内审员",
                    "编制详细的检查表",
                    "采用过程方法审核",
                    "跟踪验证纠正措施",
                    "分析审核趋势",
                ],
                benefits=[
                    "发现体系问题",
                    "促进持续改进",
                    "提升审核价值",
                ],
                risks=[
                    "审核流于形式",
                    "审核员能力不足",
                ],
                references=["ISO 9001 条款 9.2"],
            ),
            "bp_004": BestPractice(
                title="制造业过程控制",
                description="针对制造业特点的过程控制最佳实践。",
                applicable_standards=["ISO 9001"],
                industry="制造业",
                implementation_steps=[
                    "识别关键过程和特殊过程",
                    "制定过程参数控制要求",
                    "实施过程监视和测量",
                    "建立设备维护制度",
                    "控制过程变更",
                ],
                benefits=[
                    "保证产品质量稳定性",
                    "减少过程变异",
                    "提高生产效率",
                ],
                risks=[
                    "过程参数失控",
                    "设备故障",
                ],
                references=["ISO 9001 条款 8.5.1"],
            ),
            "bp_005": BestPractice(
                title="环境因素系统化管理",
                description="建立系统化的环境因素识别、评价和控制机制。",
                applicable_standards=["ISO 14001"],
                industry="通用",
                implementation_steps=[
                    "建立环境因素识别程序",
                    "采用生命周期观点",
                    "建立评价准则",
                    "确定重要环境因素",
                    "制定控制措施",
                    "定期更新评审",
                ],
                benefits=[
                    "全面识别环境影响",
                    "有效控制环境风险",
                    "提升环境绩效",
                ],
                risks=[
                    "因素识别遗漏",
                    "评价方法不当",
                ],
                references=["ISO 14001 条款 6.1.2"],
            ),
            "bp_006": BestPractice(
                title="危险源辨识与风险控制",
                description="建立全面的危险源辨识和风险控制体系。",
                applicable_standards=["ISO 45001"],
                industry="通用",
                implementation_steps=[
                    "建立危险源辨识程序",
                    "考虑所有工作状态",
                    "评估风险等级",
                    "按控制层级制定措施",
                    "实施并监控措施效果",
                    "定期更新评审",
                ],
                benefits=[
                    "预防职业伤害",
                    "降低安全风险",
                    "提升安全文化",
                ],
                risks=[
                    "危险源遗漏",
                    "控制措施无效",
                ],
                references=["ISO 45001 条款 6.1.2", "ISO 45001 条款 8.1.2"],
            ),
        }
        return practices
    
    def _load_common_issues(self) -> Dict[str, CommonIssue]:
        """加载常见问题"""
        issues = {
            "issue_001": CommonIssue(
                title="文件控制不规范",
                description="体系文件版本管理混乱，现场使用过期文件，文件审批流程不完整。",
                standard_clause="ISO 9001 7.5",
                root_cause="文件管理制度不健全，执行不到位，缺乏有效监督。",
                solution="1. 建立文件控制程序\n2. 明确文件编号规则\n3. 建立文件发放回收记录\n4. 定期检查现场文件",
                prevention="建立文件定期审查机制，加强培训，落实责任。",
                severity="中",
                frequency="常见",
            ),
            "issue_002": CommonIssue(
                title="培训记录不完整",
                description="员工培训记录缺失，培训效果评价不足，岗位能力要求不明确。",
                standard_clause="ISO 9001 7.2",
                root_cause="培训管理重视不够，培训体系不完善。",
                solution="1. 制定年度培训计划\n2. 建立培训档案\n3. 实施培训效果评价\n4. 定期评估岗位能力",
                prevention="将培训纳入绩效考核，建立培训提醒机制。",
                severity="中",
                frequency="常见",
            ),
            "issue_003": CommonIssue(
                title="内审流于形式",
                description="内部审核走过场，问题发现不深入，审核报告质量差。",
                standard_clause="ISO 9001 9.2",
                root_cause="内审员能力不足，审核策划不充分，管理层重视不够。",
                solution="1. 加强内审员培训\n2. 优化审核策划\n3. 编制详细检查表\n4. 建立审核质量评价机制",
                prevention="定期评估内审效果，持续改进审核方法。",
                severity="高",
                frequency="常见",
            ),
            "issue_004": CommonIssue(
                title="纠正措施无效",
                description="纠正措施不能消除问题根本原因，同类问题重复发生。",
                standard_clause="ISO 9001 10.2",
                root_cause="原因分析不深入，措施制定不针对，验证不充分。",
                solution="1. 采用5Why等方法深入分析\n2. 制定针对性措施\n3. 明确责任人和时限\n4. 验证措施有效性",
                prevention="建立纠正措施跟踪机制，定期统计分析。",
                severity="高",
                frequency="常见",
            ),
            "issue_005": CommonIssue(
                title="环境因素识别不全面",
                description="环境因素识别遗漏，未考虑生命周期观点，评价方法不合理。",
                standard_clause="ISO 14001 6.1.2",
                root_cause="识别方法不当，人员能力不足，更新不及时。",
                solution="1. 建立系统识别方法\n2. 培训相关人员\n3. 采用多种识别方式\n4. 定期更新评审",
                prevention="建立环境因素清单动态管理机制。",
                severity="中",
                frequency="常见",
            ),
            "issue_006": CommonIssue(
                title="危险源辨识不充分",
                description="危险源辨识范围不完整，未考虑非常规活动，员工参与不足。",
                standard_clause="ISO 45001 6.1.2",
                root_cause="辨识方法单一，员工参与机制不健全，更新不及时。",
                solution="1. 采用多种辨识方法\n2. 建立员工参与机制\n3. 考虑所有工作状态\n4. 定期更新评审",
                prevention="建立危险源辨识责任制，加强培训。",
                severity="高",
                frequency="常见",
            ),
            "issue_007": CommonIssue(
                title="应急演练流于形式",
                description="应急预案不完善，演练频次不足，演练效果评价缺失。",
                standard_clause="ISO 14001 8.2 / ISO 45001 8.2",
                root_cause="对应急管理重视不够，资源投入不足。",
                solution="1. 完善应急预案\n2. 制定演练计划\n3. 实施情景模拟演练\n4. 评价演练效果并改进",
                prevention="将应急管理纳入日常管理，定期检查。",
                severity="高",
                frequency="常见",
            ),
        }
        return issues
    
    def _load_audit_points(self) -> Dict[str, AuditPoint]:
        """加载审核要点"""
        audit_points = {
            "ap_001": AuditPoint(
                title="管理评审审核要点",
                standard_clause="ISO 9001 9.3",
                audit_questions=[
                    "管理评审是否按规定间隔进行？",
                    "评审输入信息是否完整？",
                    "是否评价了体系绩效？",
                    "是否形成了改进决议？",
                    "决议是否得到落实？",
                ],
                evidence_required=[
                    "管理评审计划",
                    "评审输入材料",
                    "管理评审会议记录",
                    "管理评审报告",
                    "改进决议及跟踪记录",
                ],
                common_nonconformities=[
                    "评审输入不完整",
                    "未评价体系绩效",
                    "决议未落实",
                    "记录不完整",
                ],
                audit_tips=[
                    "关注评审输入的完整性",
                    "检查决议落实情况",
                    "追溯上次评审决议",
                ],
            ),
            "ap_002": AuditPoint(
                title="内部审核审核要点",
                standard_clause="ISO 9001 9.2",
                audit_questions=[
                    "是否制定了审核方案？",
                    "审核员是否具备能力？",
                    "审核范围是否覆盖全部？",
                    "不符合是否得到整改？",
                    "审核结果是否报告管理层？",
                ],
                evidence_required=[
                    "年度审核计划",
                    "审核实施计划",
                    "内审检查表",
                    "不符合报告",
                    "内审报告",
                    "整改验证记录",
                ],
                common_nonconformities=[
                    "审核计划不完整",
                    "审核员能力不足",
                    "审核深度不够",
                    "整改验证不到位",
                ],
                audit_tips=[
                    "检查审核员资质",
                    "抽查检查表质量",
                    "追溯不符合整改",
                ],
            ),
            "ap_003": AuditPoint(
                title="设计开发审核要点",
                standard_clause="ISO 9001 8.3",
                audit_questions=[
                    "是否建立了设计开发程序？",
                    "设计输入是否完整明确？",
                    "设计评审、验证、确认是否进行？",
                    "设计输出是否满足输入要求？",
                    "设计变更是否受控？",
                ],
                evidence_required=[
                    "设计开发程序",
                    "设计计划",
                    "设计输入文件",
                    "设计评审记录",
                    "设计验证记录",
                    "设计确认记录",
                    "设计输出文件",
                    "设计变更记录",
                ],
                common_nonconformities=[
                    "设计输入不完整",
                    "评审验证确认缺失",
                    "设计输出不满足要求",
                    "变更控制不规范",
                ],
                audit_tips=[
                    "关注设计过程完整性",
                    "检查设计输入输出对应",
                    "追溯设计变更控制",
                ],
            ),
            "ap_004": AuditPoint(
                title="采购控制审核要点",
                standard_clause="ISO 9001 8.4",
                audit_questions=[
                    "是否对供方进行了评价选择？",
                    "是否建立了合格供方名录？",
                    "采购信息是否明确？",
                    "是否对采购产品进行了验证？",
                    "供方绩效是否进行监控？",
                ],
                evidence_required=[
                    "供方评价准则",
                    "供方评价记录",
                    "合格供方名录",
                    "采购合同/订单",
                    "进货检验记录",
                    "供方绩效评价记录",
                ],
                common_nonconformities=[
                    "供方评价不充分",
                    "采购信息不明确",
                    "进货验证不到位",
                    "供方绩效未监控",
                ],
                audit_tips=[
                    "抽查供方评价记录",
                    "核对采购信息完整性",
                    "追溯进货验证",
                ],
            ),
            "ap_005": AuditPoint(
                title="环境因素审核要点",
                standard_clause="ISO 14001 6.1.2",
                audit_questions=[
                    "环境因素识别是否全面？",
                    "是否考虑了生命周期观点？",
                    "评价方法是否合理？",
                    "重要环境因素是否确定？",
                    "是否定期更新？",
                ],
                evidence_required=[
                    "环境因素识别程序",
                    "环境因素清单",
                    "环境因素评价记录",
                    "重要环境因素清单",
                    "更新评审记录",
                ],
                common_nonconformities=[
                    "因素识别遗漏",
                    "未考虑生命周期",
                    "评价方法不当",
                    "更新不及时",
                ],
                audit_tips=[
                    "现场核对因素识别",
                    "检查评价准则",
                    "关注更新机制",
                ],
            ),
            "ap_006": AuditPoint(
                title="危险源辨识审核要点",
                standard_clause="ISO 45001 6.1.2",
                audit_questions=[
                    "危险源辨识是否全面？",
                    "是否考虑了所有工作状态？",
                    "员工是否参与辨识？",
                    "风险评价方法是否合理？",
                    "是否定期更新？",
                ],
                evidence_required=[
                    "危险源辨识程序",
                    "危险源清单",
                    "风险评价记录",
                    "员工参与记录",
                    "更新评审记录",
                ],
                common_nonconformities=[
                    "危险源遗漏",
                    "未考虑非常规活动",
                    "员工参与不足",
                    "更新不及时",
                ],
                audit_tips=[
                    "现场核对危险源",
                    "检查员工参与证据",
                    "关注更新机制",
                ],
            ),
        }
        return audit_points
    
    def add_best_practice(self, practice: BestPractice) -> bool:
        """
        添加最佳实践
        
        Args:
            practice: 最佳实践对象
            
        Returns:
            添加是否成功
        """
        import uuid
        practice_id = str(uuid.uuid4())
        self._best_practices[practice_id] = practice
        return self.add_item(practice.to_knowledge_item())
    
    def add_common_issue(self, issue: CommonIssue) -> bool:
        """
        添加常见问题
        
        Args:
            issue: 常见问题对象
            
        Returns:
            添加是否成功
        """
        import uuid
        issue_id = str(uuid.uuid4())
        self._common_issues[issue_id] = issue
        return self.add_item(issue.to_knowledge_item())
    
    def add_audit_point(self, audit_point: AuditPoint) -> bool:
        """
        添加审核要点
        
        Args:
            audit_point: 审核要点对象
            
        Returns:
            添加是否成功
        """
        import uuid
        ap_id = str(uuid.uuid4())
        self._audit_points[ap_id] = audit_point
        return self.add_item(audit_point.to_knowledge_item())
    
    def query_by_industry(self, industry: str, query: KnowledgeQuery) -> KnowledgeResult:
        """
        按行业查询经验知识
        
        Args:
            industry: 行业名称
            query: 查询对象
            
        Returns:
            查询结果
        """
        query.industry = industry
        return self.query(query)
    
    def query_by_standard_clause(self, clause: str, query: KnowledgeQuery) -> KnowledgeResult:
        """
        按标准条款查询经验知识
        
        Args:
            clause: 标准条款
            query: 查询对象
            
        Returns:
            查询结果
        """
        query.standard_ref = clause
        return self.query(query)
    
    def get_best_practices_by_standard(self, standard: str) -> List[BestPractice]:
        """
        获取指定标准的最佳实践
        
        Args:
            standard: 标准名称
            
        Returns:
            最佳实践列表
        """
        return [
            bp for bp in self._best_practices.values()
            if standard in bp.applicable_standards
        ]
    
    def get_issues_by_severity(self, severity: str) -> List[CommonIssue]:
        """
        获取指定严重程度的问题
        
        Args:
            severity: 严重程度
            
        Returns:
            问题列表
        """
        return [
            issue for issue in self._common_issues.values()
            if issue.severity == severity
        ]
    
    def get_audit_points_by_clause(self, clause: str) -> List[AuditPoint]:
        """
        获取指定条款的审核要点
        
        Args:
            clause: 标准条款
            
        Returns:
            审核要点列表
        """
        return [
            ap for ap in self._audit_points.values()
            if clause in ap.standard_clause
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        stats = super().get_statistics()
        stats["best_practices_count"] = len(self._best_practices)
        stats["common_issues_count"] = len(self._common_issues)
        stats["audit_points_count"] = len(self._audit_points)
        return stats
