"""
L1 标准知识库模块

实现第一层知识库 - 标准知识层，包含:
- ISO 9001 质量管理体系标准条款
- ISO 14001 环境管理体系标准条款
- ISO 45001 职业健康安全管理体系标准条款
- 其他相关标准和法规要求

特点:
- 权威性: 来源于官方发布的标准文件
- 稳定性: 标准内容相对稳定，更新周期长
- 基础性: 是其他层级知识的根基
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .knowledge_base import (
    KnowledgeBase,
    KnowledgeItem,
    KnowledgeLevel,
    KnowledgeQuery,
    KnowledgeResult,
)


@dataclass
class StandardClause:
    """
    标准条款数据类
    
    表示ISO标准中的具体条款。
    
    Attributes:
        clause_number: 条款编号（如 "4.1", "8.5.1"）
        title: 条款标题
        requirement: 条款要求内容
        intent: 条款意图说明
        applicable_scope: 适用范围
        related_clauses: 相关条款列表
        required_records: 要求的记录
        audit_points: 审核要点
    """
    
    clause_number: str
    title: str
    requirement: str
    intent: str = ""
    applicable_scope: str = "全部适用"
    related_clauses: List[str] = field(default_factory=list)
    required_records: List[str] = field(default_factory=list)
    audit_points: List[str] = field(default_factory=list)
    
    def to_knowledge_item(self, standard: str) -> KnowledgeItem:
        """
        转换为知识项
        
        Args:
            standard: 所属标准名称
            
        Returns:
            KnowledgeItem 实例
        """
        content = f"""
## {standard} - {self.clause_number} {self.title}

### 要求
{self.requirement}

### 意图
{self.intent}

### 适用范围
{self.applicable_scope}

### 相关条款
{', '.join(self.related_clauses) if self.related_clauses else '无'}

### 要求的记录
{chr(10).join(f'- {r}' for r in self.required_records) if self.required_records else '无特定记录要求'}

### 审核要点
{chr(10).join(f'- {p}' for p in self.audit_points) if self.audit_points else '无'}
"""
        
        return KnowledgeItem(
            level=KnowledgeLevel.L1_STANDARD,
            title=f"{standard} {self.clause_number} {self.title}",
            content=content.strip(),
            category=f"{standard}标准条款",
            tags=[standard, self.clause_number, "标准条款", self.title],
            source=f"{standard}标准",
            standard_ref=f"{standard} {self.clause_number}",
            confidence=1.0,
            metadata={
                "clause_number": self.clause_number,
                "standard": standard,
                "requirement": self.requirement,
                "intent": self.intent,
                "applicable_scope": self.applicable_scope,
                "related_clauses": self.related_clauses,
                "required_records": self.required_records,
                "audit_points": self.audit_points,
            }
        )


class StandardKB(KnowledgeBase):
    """
    L1 标准知识库
    
    管理ISO管理体系标准条款知识，包括:
    - ISO 9001 质量管理体系
    - ISO 14001 环境管理体系
    - ISO 45001 职业健康安全管理体系
    
    特点:
    - 内容来源于官方标准文件
    - 条款结构化存储，便于检索
    - 支持条款间关联查询
    """
    
    # 支持的标准类型
    SUPPORTED_STANDARDS = [
        "ISO 9001",
        "ISO 14001", 
        "ISO 45001",
    ]
    
    def __init__(self):
        """初始化标准知识库"""
        super().__init__(KnowledgeLevel.L1_STANDARD)
        self._standard_clauses: Dict[str, Dict[str, StandardClause]] = {}
        # 标准版本信息
        self._standard_versions: Dict[str, str] = {
            "ISO 9001": "2015版",
            "ISO 14001": "2015版",
            "ISO 45001": "2018版",
        }
    
    def initialize(self) -> bool:
        """
        初始化标准知识库
        
        加载所有预定义的标准条款知识。
        
        Returns:
            初始化是否成功
        """
        try:
            # 加载知识数据
            items = self.load_knowledge()
            
            # 添加到知识库
            for item in items:
                self.add_item(item)
            
            self._initialized = True
            return True
        except Exception as e:
            print(f"标准知识库初始化失败: {e}")
            return False
    
    def load_knowledge(self) -> List[KnowledgeItem]:
        """
        加载标准知识数据
        
        Returns:
            标准知识项列表
        """
        items = []
        
        # 加载 ISO 9001 标准条款
        iso9001_clauses = self._load_iso9001_clauses()
        self._standard_clauses["ISO 9001"] = iso9001_clauses
        for clause in iso9001_clauses.values():
            items.append(clause.to_knowledge_item("ISO 9001"))
        
        # 加载 ISO 14001 标准条款
        iso14001_clauses = self._load_iso14001_clauses()
        self._standard_clauses["ISO 14001"] = iso14001_clauses
        for clause in iso14001_clauses.values():
            items.append(clause.to_knowledge_item("ISO 14001"))
        
        # 加载 ISO 45001 标准条款
        iso45001_clauses = self._load_iso45001_clauses()
        self._standard_clauses["ISO 45001"] = iso45001_clauses
        for clause in iso45001_clauses.values():
            items.append(clause.to_knowledge_item("ISO 45001"))
        
        return items
    
    def _load_iso9001_clauses(self) -> Dict[str, StandardClause]:
        """
        加载 ISO 9001 标准条款
        
        Returns:
            条款字典，键为条款编号
        """
        clauses = {
            "4.1": StandardClause(
                clause_number="4.1",
                title="理解组织及其环境",
                requirement="组织应确定与其宗旨相关并影响其实现质量管理体系预期结果的能力的各种外部和内部因素。",
                intent="确保组织了解可能影响其QMS的内外部环境，以便识别风险和机遇。",
                applicable_scope="全部适用",
                related_clauses=["4.2", "6.1"],
                required_records=["内外部因素分析记录"],
                audit_points=[
                    "组织是否识别了内外部因素？",
                    "因素识别是否全面、适当？",
                    "是否定期评审和更新？",
                ]
            ),
            "4.2": StandardClause(
                clause_number="4.2",
                title="理解相关方的需求和期望",
                requirement="组织应确定与质量管理体系有关的相关方及其要求。",
                intent="识别对QMS有影响的相关方及其需求，确保满足各方期望。",
                applicable_scope="全部适用",
                related_clauses=["4.1", "4.3"],
                required_records=["相关方及其要求清单"],
                audit_points=[
                    "是否识别了所有相关方？",
                    "是否确定了相关方的需求？",
                    "是否定期更新相关方信息？",
                ]
            ),
            "4.3": StandardClause(
                clause_number="4.3",
                title="确定质量管理体系的范围",
                requirement="组织应确定质量管理体系的边界和适用性，以确定其范围。",
                intent="明确QMS的边界，确保体系覆盖所有相关活动和过程。",
                applicable_scope="全部适用",
                related_clauses=["4.1", "4.2", "4.4"],
                required_records=["QMS范围说明文件"],
                audit_points=[
                    "范围是否明确界定？",
                    "是否有不适用条款的说明？",
                    "范围是否与组织实际情况一致？",
                ]
            ),
            "4.4": StandardClause(
                clause_number="4.4",
                title="质量管理体系及其过程",
                requirement="组织应按照本标准的要求建立、实施、保持和持续改进质量管理体系，包括所需过程及其相互作用。",
                intent="建立系统的QMS架构，确保过程有效运行和相互作用。",
                applicable_scope="全部适用",
                related_clauses=["4.3", "5.1", "6.1"],
                required_records=["过程清单", "过程相互作用图", "过程程序文件"],
                audit_points=[
                    "是否确定了所需过程？",
                    "是否确定了过程顺序和相互作用？",
                    "是否分配了过程职责和权限？",
                ]
            ),
            "5.1": StandardClause(
                clause_number="5.1",
                title="领导作用和承诺",
                requirement="最高管理者应证实其对质量管理体系的领导作用和承诺。",
                intent="确保最高管理者积极参与并支持QMS，提供必要的资源。",
                applicable_scope="全部适用",
                related_clauses=["5.2", "5.3", "7.1"],
                required_records=["管理评审记录", "资源提供证据"],
                audit_points=[
                    "最高管理者是否承担QMS责任？",
                    "是否确保了质量方针和目标的制定？",
                    "是否提供了必要的资源？",
                ]
            ),
            "5.2": StandardClause(
                clause_number="5.2",
                title="方针",
                requirement="最高管理者应制定、实施和保持质量方针。",
                intent="建立质量方针，为质量目标提供框架，指导组织质量方向。",
                applicable_scope="全部适用",
                related_clauses=["5.1", "6.2"],
                required_records=["质量方针文件", "方针沟通记录"],
                audit_points=[
                    "方针是否与组织宗旨相适应？",
                    "方针是否包含持续改进承诺？",
                    "方针是否在组织内得到沟通和理解？",
                ]
            ),
            "6.1": StandardClause(
                clause_number="6.1",
                title="应对风险和机遇的措施",
                requirement="组织应策划应对风险和机遇的措施，并将其整合到质量管理体系过程中。",
                intent="识别和管理影响QMS预期结果的风险和机遇。",
                applicable_scope="全部适用",
                related_clauses=["4.1", "4.2", "6.2"],
                required_records=["风险和机遇清单", "应对措施计划"],
                audit_points=[
                    "是否识别了风险和机遇？",
                    "是否制定了应对措施？",
                    "措施是否得到实施和评价？",
                ]
            ),
            "6.2": StandardClause(
                clause_number="6.2",
                title="质量目标及其实现的策划",
                requirement="组织应在相关职能、层次和过程上建立质量目标。",
                intent="将质量方针转化为可测量的目标，确保体系有效运行。",
                applicable_scope="全部适用",
                related_clauses=["5.2", "6.1", "9.1"],
                required_records=["质量目标文件", "目标实现计划"],
                audit_points=[
                    "目标是否与方针一致？",
                    "目标是否可测量？",
                    "是否策划了实现目标的措施？",
                ]
            ),
            "7.1": StandardClause(
                clause_number="7.1",
                title="资源",
                requirement="组织应确定并提供建立、实施、保持和持续改进质量管理体系所需的资源。",
                intent="确保QMS运行所需的各种资源得到保障。",
                applicable_scope="全部适用",
                related_clauses=["5.1", "7.2", "7.3"],
                required_records=["资源需求清单", "资源提供记录"],
                audit_points=[
                    "是否确定了所需资源？",
                    "资源是否得到提供？",
                    "资源是否满足要求？",
                ]
            ),
            "7.2": StandardClause(
                clause_number="7.2",
                title="能力",
                requirement="组织应确定在其控制下工作的人员所需的能力，确保这些人员是胜任的。",
                intent="确保人员具备执行任务所需的能力和资质。",
                applicable_scope="全部适用",
                related_clauses=["7.1", "7.3"],
                required_records=["岗位能力要求", "培训记录", "能力评价记录"],
                audit_points=[
                    "是否确定了岗位能力要求？",
                    "是否进行了能力评价？",
                    "是否采取了培训等措施？",
                ]
            ),
            "8.1": StandardClause(
                clause_number="8.1",
                title="运行策划和控制",
                requirement="组织应策划、实施和控制满足产品和服务要求所需的过程。",
                intent="确保产品和服务实现过程得到有效策划和控制。",
                applicable_scope="全部适用",
                related_clauses=["6.1", "8.2", "8.3"],
                required_records=["过程控制文件", "运行准则"],
                audit_points=[
                    "是否策划了运行过程？",
                    "是否建立了过程准则？",
                    "是否控制了外包过程？",
                ]
            ),
            "8.2": StandardClause(
                clause_number="8.2",
                title="产品和服务要求",
                requirement="组织应确保有能力满足向顾客提供的产品和服务的要求。",
                intent="确保产品和服务要求明确、可满足，并与顾客达成一致。",
                applicable_scope="全部适用",
                related_clauses=["8.1", "8.5", "8.6"],
                required_records=["产品要求评审记录", "合同/订单"],
                audit_points=[
                    "是否确定了产品和服务要求？",
                    "是否进行了要求评审？",
                    "评审结果是否形成文件？",
                ]
            ),
            "8.5.1": StandardClause(
                clause_number="8.5.1",
                title="生产和服务提供的控制",
                requirement="组织应在受控条件下进行生产和服务提供。",
                intent="确保生产和服务过程在受控状态下进行，保证输出质量。",
                applicable_scope="全部适用",
                related_clauses=["8.1", "8.5.2", "8.5.3"],
                required_records=["作业指导书", "过程参数记录", "设备维护记录"],
                audit_points=[
                    "是否规定了过程特性？",
                    "是否提供了作业指导书？",
                    "是否使用了适宜的设备？",
                ]
            ),
            "9.1": StandardClause(
                clause_number="9.1",
                title="监视、测量、分析和评价",
                requirement="组织应确定需要监视和测量的内容，以及监视、测量、分析和评价的方法。",
                intent="通过监视和测量获取体系运行信息，评价体系绩效。",
                applicable_scope="全部适用",
                related_clauses=["6.2", "9.2", "9.3"],
                required_records=["监视和测量记录", "分析评价报告"],
                audit_points=[
                    "是否确定了监视测量对象？",
                    "是否确定了监测方法？",
                    "是否进行了分析和评价？",
                ]
            ),
            "9.2": StandardClause(
                clause_number="9.2",
                title="内部审核",
                requirement="组织应按策划的时间间隔进行内部审核，以提供质量管理体系是否符合要求的信息。",
                intent="通过内部审核验证QMS的符合性和有效性。",
                applicable_scope="全部适用",
                related_clauses=["9.1", "9.3"],
                required_records=["内审计划", "内审检查表", "内审报告", "不符合报告"],
                audit_points=[
                    "是否制定了内审计划？",
                    "审核员是否具备能力？",
                    "是否编制了审核报告？",
                ]
            ),
            "9.3": StandardClause(
                clause_number="9.3",
                title="管理评审",
                requirement="最高管理者应按策划的时间间隔评审质量管理体系，以确保其持续的适宜性、充分性和有效性。",
                intent="通过管理评审评价QMS，做出改进决策。",
                applicable_scope="全部适用",
                related_clauses=["5.1", "9.1", "9.2"],
                required_records=["管理评审计划", "管理评审报告", "改进决议"],
                audit_points=[
                    "是否按规定间隔进行评审？",
                    "评审输入是否完整？",
                    "是否形成了评审输出？",
                ]
            ),
            "10.1": StandardClause(
                clause_number="10.1",
                title="总则",
                requirement="组织应确定并选择改进机会，采取必要措施，满足顾客要求和增强顾客满意。",
                intent="建立持续改进机制，不断提升QMS绩效。",
                applicable_scope="全部适用",
                related_clauses=["10.2", "10.3"],
                required_records=["改进机会清单", "改进措施记录"],
                audit_points=[
                    "是否识别了改进机会？",
                    "是否采取了改进措施？",
                    "改进效果是否得到验证？",
                ]
            ),
            "10.2": StandardClause(
                clause_number="10.2",
                title="不合格和纠正措施",
                requirement="当出现不合格时，组织应采取措施以控制和纠正不合格，并消除不合格的原因。",
                intent="有效处理不合格，防止再发生。",
                applicable_scope="全部适用",
                related_clauses=["10.1", "10.3"],
                required_records=["不合格记录", "纠正措施报告"],
                audit_points=[
                    "是否对不合格进行了控制？",
                    "是否分析了不合格原因？",
                    "是否采取了纠正措施？",
                ]
            ),
            "10.3": StandardClause(
                clause_number="10.3",
                title="持续改进",
                requirement="组织应持续改进质量管理体系的适宜性、充分性和有效性。",
                intent="推动QMS持续改进，提升整体绩效。",
                applicable_scope="全部适用",
                related_clauses=["10.1", "10.2"],
                required_records=["持续改进记录", "改进效果评价"],
                audit_points=[
                    "是否建立了改进机制？",
                    "是否利用了各种信息来源？",
                    "改进是否得到持续实施？",
                ]
            ),
        }
        
        return clauses
    
    def _load_iso14001_clauses(self) -> Dict[str, StandardClause]:
        """
        加载 ISO 14001 标准条款
        
        Returns:
            条款字典，键为条款编号
        """
        clauses = {
            "4.1": StandardClause(
                clause_number="4.1",
                title="理解组织及其环境",
                requirement="组织应确定与其宗旨相关并影响其实现环境管理体系预期结果的能力的各种外部和内部因素。",
                intent="确保组织了解可能影响其EMS的内外部环境，包括环境条件。",
                applicable_scope="全部适用",
                related_clauses=["4.2", "6.1"],
                required_records=["内外部因素分析记录", "环境条件分析"],
                audit_points=[
                    "是否识别了内外部因素？",
                    "是否考虑了环境条件？",
                    "是否定期评审更新？",
                ]
            ),
            "4.2": StandardClause(
                clause_number="4.2",
                title="理解相关方的需求和期望",
                requirement="组织应确定与环境管理体系有关的相关方及其相关需求和期望。",
                intent="识别与环境管理相关的相关方需求，确保合规。",
                applicable_scope="全部适用",
                related_clauses=["4.1", "4.3"],
                required_records=["相关方清单", "合规义务清单"],
                audit_points=[
                    "是否识别了相关方？",
                    "是否确定了合规义务？",
                    "是否定期更新？",
                ]
            ),
            "6.1": StandardClause(
                clause_number="6.1",
                title="应对风险和机遇的措施",
                requirement="组织应确定需要应对的风险和机遇，以确保环境管理体系能够实现预期结果。",
                intent="识别环境风险和机遇，制定应对措施。",
                applicable_scope="全部适用",
                related_clauses=["4.1", "4.2", "6.2"],
                required_records=["环境因素清单", "风险机遇评价", "应对措施计划"],
                audit_points=[
                    "是否识别了环境因素？",
                    "是否评价了重要环境因素？",
                    "是否制定了应对措施？",
                ]
            ),
            "6.1.2": StandardClause(
                clause_number="6.1.2",
                title="环境因素",
                requirement="组织应在所界定的环境管理体系范围内，确定其活动、产品和服务中能够控制和能够施加影响的环境因素及其环境影响。",
                intent="全面识别组织活动对环境的影响因素。",
                applicable_scope="全部适用",
                related_clauses=["6.1.1", "6.1.3"],
                required_records=["环境因素识别清单", "环境影响评价"],
                audit_points=[
                    "环境因素识别是否全面？",
                    "是否考虑了生命周期观点？",
                    "是否确定了重要环境因素？",
                ]
            ),
            "6.1.3": StandardClause(
                clause_number="6.1.3",
                title="合规义务",
                requirement="组织应确定并获取与环境因素有关的合规义务。",
                intent="确保组织了解并遵守适用的法律法规和其他要求。",
                applicable_scope="全部适用",
                related_clauses=["6.1.2", "7.5"],
                required_records=["法律法规清单", "合规性评价记录"],
                audit_points=[
                    "是否识别了合规义务？",
                    "是否获取了最新版本？",
                    "是否进行了合规性评价？",
                ]
            ),
            "6.2": StandardClause(
                clause_number="6.2",
                title="环境目标及其实现的策划",
                requirement="组织应在相关职能和层次建立环境目标。",
                intent="建立可测量的环境目标，推动环境绩效改进。",
                applicable_scope="全部适用",
                related_clauses=["5.2", "6.1"],
                required_records=["环境目标", "实施计划"],
                audit_points=[
                    "目标是否与环境方针一致？",
                    "目标是否可测量？",
                    "是否制定了实现计划？",
                ]
            ),
            "8.1": StandardClause(
                clause_number="8.1",
                title="运行策划和控制",
                requirement="组织应建立、实施、控制并保持满足环境管理体系要求所需的过程。",
                intent="确保运行过程得到有效控制，实现环境目标。",
                applicable_scope="全部适用",
                related_clauses=["6.1", "6.2"],
                required_records=["运行控制程序", "操作规程"],
                audit_points=[
                    "是否建立了运行准则？",
                    "是否控制了重要环境因素？",
                    "是否管理了外包过程？",
                ]
            ),
            "8.2": StandardClause(
                clause_number="8.2",
                title="应急准备和响应",
                requirement="组织应建立、实施并保持对潜在紧急情况进行应急准备和响应所需的过程。",
                intent="确保组织能够有效应对环境紧急情况。",
                applicable_scope="全部适用",
                related_clauses=["6.1", "8.1"],
                required_records=["应急预案", "应急演练记录"],
                audit_points=[
                    "是否识别了潜在紧急情况？",
                    "是否制定了应急预案？",
                    "是否进行了演练？",
                ]
            ),
            "9.1.2": StandardClause(
                clause_number="9.1.2",
                title="合规性评价",
                requirement="组织应建立、实施并保持评价其合规义务履行情况所需的过程。",
                intent="定期评价组织对合规义务的遵守情况。",
                applicable_scope="全部适用",
                related_clauses=["6.1.3", "9.1.1"],
                required_records=["合规性评价计划", "合规性评价报告"],
                audit_points=[
                    "是否制定了评价计划？",
                    "评价是否全面覆盖？",
                    "不符合是否得到处理？",
                ]
            ),
            "9.2": StandardClause(
                clause_number="9.2",
                title="内部审核",
                requirement="组织应按策划的时间间隔进行内部审核，以提供环境管理体系是否符合要求的信息。",
                intent="验证EMS的符合性和有效性。",
                applicable_scope="全部适用",
                related_clauses=["9.1", "9.3"],
                required_records=["内审计划", "内审报告"],
                audit_points=[
                    "是否制定了内审计划？",
                    "审核是否全面？",
                    "不符合是否得到整改？",
                ]
            ),
            "9.3": StandardClause(
                clause_number="9.3",
                title="管理评审",
                requirement="最高管理者应按策划的时间间隔评审环境管理体系，以确保其持续的适宜性、充分性和有效性。",
                intent="评价EMS绩效，做出改进决策。",
                applicable_scope="全部适用",
                related_clauses=["5.1", "9.1", "9.2"],
                required_records=["管理评审计划", "管理评审报告"],
                audit_points=[
                    "评审输入是否完整？",
                    "是否评价了环境绩效？",
                    "是否形成了改进决议？",
                ]
            ),
        }
        
        return clauses
    
    def _load_iso45001_clauses(self) -> Dict[str, StandardClause]:
        """
        加载 ISO 45001 标准条款
        
        Returns:
            条款字典，键为条款编号
        """
        clauses = {
            "4.1": StandardClause(
                clause_number="4.1",
                title="理解组织及其环境",
                requirement="组织应确定与其宗旨相关并影响其实现职业健康安全管理体系预期结果的能力的各种外部和内部因素。",
                intent="了解影响OH&S管理体系的外部和内部因素。",
                applicable_scope="全部适用",
                related_clauses=["4.2", "6.1"],
                required_records=["内外部因素分析"],
                audit_points=[
                    "是否识别了内外部因素？",
                    "是否考虑了员工能力？",
                    "是否定期更新？",
                ]
            ),
            "4.2": StandardClause(
                clause_number="4.2",
                title="理解工作人员和其他相关方的需求和期望",
                requirement="组织应确定职业健康安全管理体系有关的相关方及其需求和期望。",
                intent="识别员工和相关方的OH&S需求和期望。",
                applicable_scope="全部适用",
                related_clauses=["4.1", "5.4"],
                required_records=["相关方需求清单", "员工代表沟通记录"],
                audit_points=[
                    "是否识别了相关方？",
                    "是否确定了员工需求？",
                    "是否有员工参与机制？",
                ]
            ),
            "5.4": StandardClause(
                clause_number="5.4",
                title="工作人员的协商和参与",
                requirement="组织应建立、实施和保持工作人员协商和参与的过程。",
                intent="确保员工在OH&S管理中的参与和协商权利。",
                applicable_scope="全部适用",
                related_clauses=["4.2", "7.3"],
                required_records=["员工参与记录", "协商会议记录"],
                audit_points=[
                    "是否建立了参与机制？",
                    "员工是否参与危险源辨识？",
                    "是否有员工代表？",
                ]
            ),
            "6.1.2": StandardClause(
                clause_number="6.1.2",
                title="危险源辨识",
                requirement="组织应建立、实施和保持危险源辨识的过程。",
                intent="系统识别工作场所的危险源，评估风险。",
                applicable_scope="全部适用",
                related_clauses=["6.1.1", "6.1.3"],
                required_records=["危险源清单", "风险评价记录"],
                audit_points=[
                    "危险源辨识是否全面？",
                    "是否考虑了所有工作状态？",
                    "是否评估了风险等级？",
                ]
            ),
            "6.1.3": StandardClause(
                clause_number="6.1.3",
                title="合规义务评价",
                requirement="组织应确定并获取与危险源有关的合规义务。",
                intent="确保组织了解并遵守OH&S相关法规要求。",
                applicable_scope="全部适用",
                related_clauses=["6.1.2", "7.5"],
                required_records=["法律法规清单", "合规性评价"],
                audit_points=[
                    "是否识别了适用法规？",
                    "是否获取了最新版本？",
                    "是否进行了合规评价？",
                ]
            ),
            "6.2": StandardClause(
                clause_number="6.2",
                title="职业健康安全目标及其实现的策划",
                requirement="组织应在相关职能和层次建立职业健康安全目标。",
                intent="建立可测量的OH&S目标，推动绩效改进。",
                applicable_scope="全部适用",
                related_clauses=["5.2", "6.1"],
                required_records=["OH&S目标", "实施计划"],
                audit_points=[
                    "目标是否与方针一致？",
                    "目标是否可测量？",
                    "是否考虑了员工意见？",
                ]
            ),
            "8.1.1": StandardClause(
                clause_number="8.1.1",
                title="运行控制",
                requirement="组织应策划、实施、控制和保持满足OH&S管理体系要求所需的过程。",
                intent="确保运行过程得到有效控制，消除危险源和降低风险。",
                applicable_scope="全部适用",
                related_clauses=["6.1", "6.2"],
                required_records=["运行控制程序", "安全操作规程"],
                audit_points=[
                    "是否建立了控制措施？",
                    "控制措施是否有效？",
                    "是否管理了变更？",
                ]
            ),
            "8.1.2": StandardClause(
                clause_number="8.1.2",
                title="消除危险源和降低职业健康安全风险",
                requirement="组织应采用控制层级来消除危险源和降低职业健康安全风险。",
                intent="按照控制层级原则，优先采用最有效的风险控制措施。",
                applicable_scope="全部适用",
                related_clauses=["6.1.2", "8.1.1"],
                required_records=["风险控制措施", "控制层级应用记录"],
                audit_points=[
                    "是否应用了控制层级？",
                    "是否优先消除危险源？",
                    "PPE是否作为最后手段？",
                ]
            ),
            "8.2": StandardClause(
                clause_number="8.2",
                title="应急准备和响应",
                requirement="组织应建立、实施和保持对潜在紧急情况进行应急准备和响应所需的过程。",
                intent="确保组织能够有效应对OH&S紧急情况。",
                applicable_scope="全部适用",
                related_clauses=["6.1.2", "8.1"],
                required_records=["应急预案", "演练记录", "应急设备清单"],
                audit_points=[
                    "是否识别了紧急情况？",
                    "是否制定了应急预案？",
                    "是否定期演练？",
                ]
            ),
            "9.1": StandardClause(
                clause_number="9.1",
                title="监视、测量、分析和评价",
                requirement="组织应确定需要监视和测量的内容，以及监视、测量、分析和评价的方法。",
                intent="监测OH&S绩效，评价体系有效性。",
                applicable_scope="全部适用",
                related_clauses=["6.2", "9.2"],
                required_records=["监测记录", "健康监护记录", "事故统计"],
                audit_points=[
                    "是否确定了监测内容？",
                    "是否进行了健康监护？",
                    "是否分析了事故趋势？",
                ]
            ),
            "10.2": StandardClause(
                clause_number="10.2",
                title="事件调查",
                requirement="组织应建立、实施和保持事件报告、调查和处理的过程。",
                intent="及时调查事件，采取纠正措施防止再发生。",
                applicable_scope="全部适用",
                related_clauses=["10.1", "10.3"],
                required_records=["事件报告", "调查报告", "纠正措施"],
                audit_points=[
                    "是否建立了报告机制？",
                    "调查是否及时全面？",
                    "是否采取了纠正措施？",
                ]
            ),
        }
        
        return clauses
    
    def get_clause(self, standard: str, clause_number: str) -> Optional[StandardClause]:
        """
        获取指定标准的特定条款
        
        Args:
            standard: 标准名称
            clause_number: 条款编号
            
        Returns:
            StandardClause 或 None
        """
        if standard in self._standard_clauses:
            return self._standard_clauses[standard].get(clause_number)
        return None
    
    def get_all_clauses(self, standard: str) -> Dict[str, StandardClause]:
        """
        获取指定标准的所有条款
        
        Args:
            standard: 标准名称
            
        Returns:
            条款字典
        """
        return self._standard_clauses.get(standard, {})
    
    def get_standard_version(self, standard: str) -> Optional[str]:
        """
        获取标准版本信息
        
        Args:
            standard: 标准名称
            
        Returns:
            版本字符串或None
        """
        return self._standard_versions.get(standard)
    
    def get_supported_standards(self) -> List[str]:
        """
        获取支持的标准列表
        
        Returns:
            标准名称列表
        """
        return self.SUPPORTED_STANDARDS.copy()
    
    def query_by_standard(self, standard: str, query: KnowledgeQuery) -> KnowledgeResult:
        """
        按标准查询知识
        
        Args:
            standard: 标准名称
            query: 查询对象
            
        Returns:
            查询结果
        """
        # 设置分类过滤
        query.categories = [f"{standard}标准条款"]
        return self.query(query)
    
    def get_related_clauses(self, standard: str, clause_number: str) -> List[KnowledgeItem]:
        """
        获取相关条款
        
        Args:
            standard: 标准名称
            clause_number: 条款编号
            
        Returns:
            相关条款知识项列表
        """
        clause = self.get_clause(standard, clause_number)
        if not clause or not clause.related_clauses:
            return []
        
        related_items = []
        for related_num in clause.related_clauses:
            related_clause = self.get_clause(standard, related_num)
            if related_clause:
                related_items.append(related_clause.to_knowledge_item(standard))
        
        return related_items
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        stats = super().get_statistics()
        stats["supported_standards"] = self.SUPPORTED_STANDARDS
        stats["standard_versions"] = self._standard_versions
        stats["clause_counts"] = {
            standard: len(clauses) 
            for standard, clauses in self._standard_clauses.items()
        }
        return stats
