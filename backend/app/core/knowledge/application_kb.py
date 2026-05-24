"""
L3 应用知识库模块

实现第三层知识库 - 应用知识层，包含:
- 企业案例库
- 模板库
- 检查表库
- 实施指南

特点:
- 实用性: 可直接应用于实际工作
- 指导性: 提供具体实施指导
- 可定制: 可根据企业特点调整
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from .knowledge_base import (
    KnowledgeBase,
    KnowledgeItem,
    KnowledgeLevel,
    KnowledgeQuery,
    KnowledgeResult,
)


class TemplateType(Enum):
    """模板类型枚举"""
    PROCEDURE = "程序文件"
    RECORD = "记录表格"
    MANUAL = "手册"
    INSTRUCTION = "作业指导书"
    PLAN = "计划"
    REPORT = "报告"
    CHECKLIST = "检查表"
    FORM = "表单"


class CaseType(Enum):
    """案例类型枚举"""
    IMPLEMENTATION = "实施案例"
    IMPROVEMENT = "改进案例"
    PROBLEM_SOLVING = "问题解决"
    AUDIT = "审核案例"
    CERTIFICATION = "认证案例"


@dataclass
class EnterpriseCase:
    """
    企业案例数据类
    
    Attributes:
        title: 案例标题
        case_type: 案例类型
        enterprise_info: 企业信息
        background: 背景
        problem: 问题描述
        solution: 解决方案
        result: 实施结果
        lessons: 经验教训
        applicable_standards: 适用标准
        industry: 行业
        scale: 企业规模
    """
    
    title: str
    case_type: str
    enterprise_info: str = ""
    background: str = ""
    problem: str = ""
    solution: str = ""
    result: str = ""
    lessons: str = ""
    applicable_standards: List[str] = field(default_factory=list)
    industry: str = "通用"
    scale: str = "中型企业"
    
    def to_knowledge_item(self) -> KnowledgeItem:
        """转换为知识项"""
        content = f"""
## 企业案例: {self.title}

### 案例类型
{self.case_type}

### 企业信息
{self.enterprise_info}

### 行业/规模
{self.industry} / {self.scale}

### 背景
{self.background}

### 问题描述
{self.problem}

### 解决方案
{self.solution}

### 实施结果
{self.result}

### 经验教训
{self.lessons}

### 适用标准
{', '.join(self.applicable_standards) if self.applicable_standards else '通用'}
"""
        
        return KnowledgeItem(
            level=KnowledgeLevel.L3_APPLICATION,
            title=f"企业案例: {self.title}",
            content=content.strip(),
            category="企业案例",
            tags=["企业案例", self.case_type, self.industry, self.scale] + self.applicable_standards,
            source="企业实践案例",
            industry=self.industry,
            confidence=0.8,
            metadata={
                "case_type": self.case_type,
                "enterprise_info": self.enterprise_info,
                "scale": self.scale,
                "applicable_standards": self.applicable_standards,
            }
        )


@dataclass
class Template:
    """
    模板数据类
    
    Attributes:
        name: 模板名称
        template_type: 模板类型
        description: 模板描述
        content: 模板内容
        applicable_standards: 适用标准
        usage_guide: 使用指南
        version: 版本号
        customizable: 是否可定制
    """
    
    name: str
    template_type: str
    description: str = ""
    content: str = ""
    applicable_standards: List[str] = field(default_factory=list)
    usage_guide: str = ""
    version: str = "1.0"
    customizable: bool = True
    
    def to_knowledge_item(self) -> KnowledgeItem:
        """转换为知识项"""
        content = f"""
## 模板: {self.name}

### 模板类型
{self.template_type}

### 描述
{self.description}

### 模板内容
```
{self.content}
```

### 使用指南
{self.usage_guide}

### 适用标准
{', '.join(self.applicable_standards) if self.applicable_standards else '通用'}

### 版本
{self.version}

### 可定制
{'是' if self.customizable else '否'}
"""
        
        return KnowledgeItem(
            level=KnowledgeLevel.L3_APPLICATION,
            title=f"模板: {self.name}",
            content=content.strip(),
            category="模板",
            tags=["模板", self.template_type] + self.applicable_standards,
            source="模板库",
            confidence=0.9,
            metadata={
                "template_type": self.template_type,
                "version": self.version,
                "customizable": self.customizable,
                "applicable_standards": self.applicable_standards,
            }
        )


@dataclass
class Checklist:
    """
    检查表数据类
    
    Attributes:
        name: 检查表名称
        standard_clause: 相关标准条款
        description: 检查表描述
        items: 检查项列表
        scoring_method: 评分方法
        applicable_scope: 适用范围
    """
    
    name: str
    standard_clause: str
    description: str = ""
    items: List[Dict[str, Any]] = field(default_factory=list)
    scoring_method: str = "符合/不符合"
    applicable_scope: str = "全部适用"
    
    def to_knowledge_item(self) -> KnowledgeItem:
        """转换为知识项"""
        items_text = "\n".join([
            f"| {i+1} | {item.get('content', '')} | {item.get('evidence', '')} | {item.get('method', '')} |"
            for i, item in enumerate(self.items)
        ])
        
        content = f"""
## 检查表: {self.name}

### 相关标准条款
{self.standard_clause}

### 描述
{self.description}

### 适用范围
{self.applicable_scope}

### 评分方法
{self.scoring_method}

### 检查项

| 序号 | 检查内容 | 所需证据 | 检查方法 |
|------|----------|----------|----------|
{items_text}
"""
        
        return KnowledgeItem(
            level=KnowledgeLevel.L3_APPLICATION,
            title=f"检查表: {self.name}",
            content=content.strip(),
            category="检查表",
            tags=["检查表", self.standard_clause],
            source="检查表库",
            standard_ref=self.standard_clause,
            confidence=0.9,
            metadata={
                "items": self.items,
                "scoring_method": self.scoring_method,
                "applicable_scope": self.applicable_scope,
            }
        )


class ApplicationKB(KnowledgeBase):
    """
    L3 应用知识库
    
    管理应用层知识，包括:
    - 企业案例库
    - 模板库
    - 检查表库
    
    特点:
    - 提供可直接使用的资源
    - 支持定制化
    - 持续扩充更新
    """
    
    def __init__(self):
        """初始化应用知识库"""
        super().__init__(KnowledgeLevel.L3_APPLICATION)
        self._cases: Dict[str, EnterpriseCase] = {}
        self._templates: Dict[str, Template] = {}
        self._checklists: Dict[str, Checklist] = {}
    
    def initialize(self) -> bool:
        """
        初始化应用知识库
        
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
            print(f"应用知识库初始化失败: {e}")
            return False
    
    def load_knowledge(self) -> List[KnowledgeItem]:
        """
        加载应用知识数据
        
        Returns:
            应用知识项列表
        """
        items = []
        
        # 加载企业案例
        cases = self._load_enterprise_cases()
        for case_id, case in cases.items():
            self._cases[case_id] = case
            items.append(case.to_knowledge_item())
        
        # 加载模板
        templates = self._load_templates()
        for template_id, template in templates.items():
            self._templates[template_id] = template
            items.append(template.to_knowledge_item())
        
        # 加载检查表
        checklists = self._load_checklists()
        for checklist_id, checklist in checklists.items():
            self._checklists[checklist_id] = checklist
            items.append(checklist.to_knowledge_item())
        
        return items
    
    def _load_enterprise_cases(self) -> Dict[str, EnterpriseCase]:
        """加载企业案例"""
        cases = {
            "case_001": EnterpriseCase(
                title="某制造企业质量管理体系升级案例",
                case_type="实施案例",
                enterprise_info="某中型制造企业，员工500人，主要生产电子元器件",
                background="企业原有质量管理体系运行多年，但存在文件与实际脱节、过程控制不力等问题",
                problem="1. 文件体系庞大但执行率低\n2. 过程控制主要依赖检验\n3. 内审流于形式\n4. 持续改进机制不健全",
                solution="1. 重新梳理过程，精简文件体系\n2. 推行过程方法，加强过程控制\n3. 培养专业内审员队伍\n4. 建立基于风险的改进机制",
                result="1. 文件数量减少40%，执行率提升\n2. 过程能力显著提升\n3. 内审发现问题质量提高\n4. 客户投诉下降30%",
                lessons="1. 体系改进需要管理层支持\n2. 员工培训是关键\n3. 持续改进需要机制保障",
                applicable_standards=["ISO 9001"],
                industry="制造业",
                scale="中型企业",
            ),
            "case_002": EnterpriseCase(
                title="某服务企业环境管理体系建设案例",
                case_type="实施案例",
                enterprise_info="某大型物业服务企业，员工2000人，管理多个商业综合体",
                background="企业响应绿色建筑要求，需要建立环境管理体系",
                problem="1. 环境因素识别不系统\n2. 能源消耗大\n3. 废弃物管理不规范\n4. 员工环保意识薄弱",
                solution="1. 建立环境因素识别评价体系\n2. 实施节能改造\n3. 规范废弃物分类管理\n4. 开展环保培训",
                result="1. 获得ISO 14001认证\n2. 能耗降低15%\n3. 废弃物回收率提升\n4. 获得绿色建筑认证",
                lessons="1. 环境因素识别要全面\n2. 节能措施需要投入\n3. 员工参与是关键",
                applicable_standards=["ISO 14001"],
                industry="服务业",
                scale="大型企业",
            ),
            "case_003": EnterpriseCase(
                title="某建筑企业职业健康安全改进案例",
                case_type="改进案例",
                enterprise_info="某建筑施工企业，员工800人，主要从事房屋建筑",
                background="企业安全生产形势严峻，事故率较高",
                problem="1. 危险源辨识不充分\n2. 安全培训效果差\n3. 应急管理薄弱\n4. 安全投入不足",
                solution="1. 建立全员参与的危险源辨识机制\n2. 创新安全培训方式\n3. 完善应急预案并定期演练\n4. 加大安全投入",
                result="1. 获得ISO 45001认证\n2. 事故率下降50%\n3. 员工安全意识提升\n4. 获得安全文明工地称号",
                lessons="1. 安全管理需要全员参与\n2. 培训要注重实效\n3. 应急演练要常态化",
                applicable_standards=["ISO 45001"],
                industry="建筑业",
                scale="中型企业",
            ),
            "case_004": EnterpriseCase(
                title="内审发现的不符合整改案例",
                case_type="问题解决",
                enterprise_info="某电子制造企业",
                background="内审发现设计开发过程存在严重问题",
                problem="1. 设计输入不完整\n2. 设计评审流于形式\n3. 设计变更控制不规范\n4. 设计记录不完整",
                solution="1. 制定设计输入检查清单\n2. 规范设计评审程序\n3. 建立设计变更控制流程\n4. 完善设计档案管理",
                result="1. 设计问题减少70%\n2. 设计周期缩短\n3. 产品质量提升\n4. 客户满意度提高",
                lessons="1. 设计过程控制要系统化\n2. 记录管理要规范\n3. 变更控制要严格",
                applicable_standards=["ISO 9001"],
                industry="制造业",
                scale="中型企业",
            ),
        }
        return cases
    
    def _load_templates(self) -> Dict[str, Template]:
        """加载模板"""
        templates = {
            "tpl_001": Template(
                name="质量手册模板",
                template_type="手册",
                description="适用于中小型企业的质量手册模板，包含ISO 9001标准要求的所有章节",
                content="""
# 质量手册

## 1 范围
[描述质量管理体系的范围，包括覆盖的产品和服务、组织的主要过程等]

## 2 规范性引用文件
ISO 9001:2015 质量管理体系 要求

## 3 术语和定义
[列出组织使用的特定术语和定义]

## 4 组织环境
### 4.1 理解组织及其环境
### 4.2 理解相关方的需求和期望
### 4.3 确定质量管理体系的范围
### 4.4 质量管理体系及其过程

## 5 领导作用
### 5.1 领导作用和承诺
### 5.2 方针
### 5.3 组织的岗位、职责和权限

## 6 策划
### 6.1 应对风险和机遇的措施
### 6.2 质量目标及其实现的策划
### 6.3 变更的策划

## 7 支持
### 7.1 资源
### 7.2 能力
### 7.3 意识
### 7.4 沟通
### 7.5 成文信息

## 8 运行
### 8.1 运行策划和控制
### 8.2 产品和服务要求
### 8.3 产品和服务的设计和开发
### 8.4 外部提供的过程、产品和服务的控制
### 8.5 生产和服务提供
### 8.6 产品和服务的放行
### 8.7 不合格输出的控制

## 9 绩效评价
### 9.1 监视、测量、分析和评价
### 9.2 内部审核
### 9.3 管理评审

## 10 改进
### 10.1 总则
### 10.2 不合格和纠正措施
### 10.3 持续改进
""",
                applicable_standards=["ISO 9001"],
                usage_guide="1. 根据企业实际情况填写各章节内容\n2. 删除不适用的条款并说明理由\n3. 确保与程序文件协调一致\n4. 经批准后发布实施",
                version="1.0",
                customizable=True,
            ),
            "tpl_002": Template(
                name="内部审核检查表模板",
                template_type="检查表",
                description="通用内部审核检查表模板，可用于各类管理体系的内部审核",
                content="""
# 内部审核检查表

## 审核信息
- 审核日期：
- 审核员：
- 受审部门：
- 审核范围：

## 审核记录

| 序号 | 标准条款 | 审核内容 | 审核证据 | 符合性 | 备注 |
|------|----------|----------|----------|--------|------|
| 1 | | | | □符合 □不符合 | |
| 2 | | | | □符合 □不符合 | |
| 3 | | | | □符合 □不符合 | |

## 不符合项记录
| 序号 | 不符合描述 | 标准条款 | 严重程度 | 整改要求 |
|------|------------|----------|----------|----------|
| | | | □严重 □一般 | |

## 审核结论
[审核结论和改进建议]

审核员签名：          日期：
受审部门确认：        日期：
""",
                applicable_standards=["ISO 9001", "ISO 14001", "ISO 45001"],
                usage_guide="1. 审核前根据审核范围确定审核条款\n2. 审核过程中如实记录审核发现\n3. 发现不符合时详细记录\n4. 审核结束后编制审核报告",
                version="1.0",
                customizable=True,
            ),
            "tpl_003": Template(
                name="管理评审计划模板",
                template_type="计划",
                description="管理评审计划模板，用于策划年度管理评审",
                content="""
# 管理评审计划

## 1 评审目的
评价质量管理体系的适宜性、充分性和有效性，确定改进机会。

## 2 评审时间
日期：    年   月   日
时间：

## 3 评审地点

## 4 参加人员
- 总经理：
- 管理者代表：
- 各部门负责人：

## 5 评审输入
| 序号 | 输入内容 | 责任部门 | 提交形式 |
|------|----------|----------|----------|
| 1 | 审核结果 | | |
| 2 | 顾客反馈 | | |
| 3 | 过程绩效和产品符合性 | | |
| 4 | 不合格及纠正措施 | | |
| 5 | 监视和测量结果 | | |
| 6 | 上次评审的跟踪措施 | | |
| 7 | 变更 | | |
| 8 | 改进建议 | | |

## 6 评审议程
1. 
2. 
3. 

## 7 评审输出要求
- 体系改进决议
- 资源需求决议
- 其他决议

编制：          日期：
批准：          日期：
""",
                applicable_standards=["ISO 9001", "ISO 14001", "ISO 45001"],
                usage_guide="1. 提前一周编制计划\n2. 确定评审输入材料\n3. 通知相关人员\n4. 准备评审材料",
                version="1.0",
                customizable=True,
            ),
            "tpl_004": Template(
                name="纠正措施报告模板",
                template_type="报告",
                description="用于记录和分析不符合，制定和实施纠正措施",
                content="""
# 纠正措施报告

## 基本信息
- 报告编号：
- 开具日期：
- 责任部门：
- 来源：□内审 □外审 □客户投诉 □其他

## 不符合描述
[详细描述不符合的事实]

## 不符合标准条款

## 原因分析
采用5Why等方法分析根本原因：
1. 为什么？
2. 为什么？
3. 为什么？
4. 为什么？
5. 为什么？

根本原因：

## 纠正措施
| 序号 | 措施内容 | 责任人 | 完成期限 |
|------|----------|--------|----------|
| 1 | | | |
| 2 | | | |

## 验证结果
验证日期：
验证方法：
验证结论：□有效 □无效

验证人：          日期：

## 关闭
□已关闭
关闭日期：
""",
                applicable_standards=["ISO 9001", "ISO 14001", "ISO 45001"],
                usage_guide="1. 详细描述不符合事实\n2. 深入分析根本原因\n3. 制定针对性措施\n4. 验证措施有效性",
                version="1.0",
                customizable=True,
            ),
            "tpl_005": Template(
                name="环境因素识别评价表",
                template_type="记录表格",
                description="用于识别和评价环境因素的标准表格",
                content="""
# 环境因素识别评价表

## 基本信息
- 部门：
- 评价日期：
- 评价人：

## 环境因素识别

| 序号 | 活动/产品/服务 | 环境因素 | 环境影响 | 状态 | 时态 |
|------|----------------|----------|----------|------|------|
| 1 | | | | □正常 □异常 □紧急 | □过去 □现在 □将来 |
| 2 | | | | □正常 □异常 □紧急 | □过去 □现在 □将来 |

## 环境因素评价

| 序号 | 环境因素 | 发生频率 | 影响程度 | 法规符合性 | 影响范围 | 综合评分 | 是否重要 |
|------|----------|----------|----------|------------|----------|----------|----------|
| 1 | | | | | | | □是 □否 |
| 2 | | | | | | | □是 □否 |

## 评价准则
- 发生频率：1-5分
- 影响程度：1-5分
- 法规符合性：1-5分
- 影响范围：1-5分
- 综合评分 = 各项得分之和
- 重要环境因素判定标准：综合评分 ≥ X分

## 重要环境因素清单
| 序号 | 重要环境因素 | 控制措施 |
|------|--------------|----------|
| 1 | | |
| 2 | | |

编制：          日期：
审核：          日期：
""",
                applicable_standards=["ISO 14001"],
                usage_guide="1. 全面识别环境因素\n2. 采用生命周期观点\n3. 按评价准则评分\n4. 确定重要环境因素",
                version="1.0",
                customizable=True,
            ),
            "tpl_006": Template(
                name="危险源辨识评价表",
                template_type="记录表格",
                description="用于辨识和评价危险源的标准表格",
                content="""
# 危险源辨识评价表

## 基本信息
- 部门：
- 辨识日期：
- 辨识人：

## 危险源辨识

| 序号 | 作业活动 | 危险源 | 可能导致的事故 | 状态 | 时态 |
|------|----------|--------|----------------|------|------|
| 1 | | | | □正常 □异常 □紧急 | □过去 □现在 □将来 |
| 2 | | | | □正常 □异常 □紧急 | □过去 □现在 □将来 |

## 风险评价（LEC法）

| 序号 | 危险源 | L(可能性) | E(暴露频率) | C(后果严重性) | D=LEC | 风险等级 |
|------|--------|-----------|-------------|---------------|-------|----------|
| 1 | | | | | | □高 □中 □低 |
| 2 | | | | | | □高 □中 □低 |

## 评价标准
- L值：1-10分（事故发生的可能性）
- E值：1-10分（暴露于危险环境的频率）
- C值：1-100分（发生事故产生的后果）
- D值：风险值
  - D≥320：重大风险
  - 160≤D<320：较大风险
  - D<160：一般风险

## 重大危险源清单
| 序号 | 重大危险源 | 控制措施 | 责任人 |
|------|------------|----------|--------|
| 1 | | | |
| 2 | | | |

编制：          日期：
审核：          日期：
""",
                applicable_standards=["ISO 45001"],
                usage_guide="1. 全面辨识危险源\n2. 考虑所有工作状态\n3. 采用合适的评价方法\n4. 确定重大危险源",
                version="1.0",
                customizable=True,
            ),
        }
        return templates
    
    def _load_checklists(self) -> Dict[str, Checklist]:
        """加载检查表"""
        checklists = {
            "chk_001": Checklist(
                name="ISO 9001 管理评审检查表",
                standard_clause="ISO 9001 9.3",
                description="用于审核管理评审过程是否符合标准要求",
                items=[
                    {"content": "管理评审是否按规定间隔进行？", "evidence": "管理评审计划、记录", "method": "查阅记录"},
                    {"content": "评审输入是否完整？", "evidence": "评审输入材料清单", "method": "核对标准要求"},
                    {"content": "是否包含审核结果？", "evidence": "内审报告、外审报告", "method": "查阅报告"},
                    {"content": "是否包含顾客反馈？", "evidence": "顾客满意度调查、投诉记录", "method": "查阅记录"},
                    {"content": "是否包含过程绩效和产品符合性？", "evidence": "过程监控记录、产品检验记录", "method": "查阅记录"},
                    {"content": "是否包含不合格及纠正措施情况？", "evidence": "不合格记录、纠正措施报告", "method": "查阅记录"},
                    {"content": "是否评价了体系改进的机会？", "evidence": "管理评审报告", "method": "查阅报告"},
                    {"content": "是否评价了变更需求？", "evidence": "管理评审报告", "method": "查阅报告"},
                    {"content": "是否形成了评审输出？", "evidence": "管理评审报告", "method": "查阅报告"},
                    {"content": "输出是否包含改进决议？", "evidence": "管理评审报告", "method": "查阅报告"},
                    {"content": "输出是否包含资源需求？", "evidence": "管理评审报告", "method": "查阅报告"},
                    {"content": "评审决议是否得到落实？", "evidence": "跟踪验证记录", "method": "查阅记录"},
                ],
                scoring_method="符合/不符合",
                applicable_scope="全部适用",
            ),
            "chk_002": Checklist(
                name="ISO 9001 内部审核检查表",
                standard_clause="ISO 9001 9.2",
                description="用于审核内部审核过程是否符合标准要求",
                items=[
                    {"content": "是否制定了审核方案？", "evidence": "年度审核计划", "method": "查阅计划"},
                    {"content": "审核方案是否考虑了过程重要性和以往审核结果？", "evidence": "审核方案策划记录", "method": "查阅记录"},
                    {"content": "是否规定了审核准则和范围？", "evidence": "审核实施计划", "method": "查阅计划"},
                    {"content": "审核员是否具备能力？", "evidence": "审核员资质证书、培训记录", "method": "查阅证书"},
                    {"content": "审核员是否独立于受审活动？", "evidence": "审核员安排记录", "method": "核对安排"},
                    {"content": "是否编制了审核报告？", "evidence": "内审报告", "method": "查阅报告"},
                    {"content": "审核发现是否报告给相关管理层？", "evidence": "报告分发记录", "method": "查阅记录"},
                    {"content": "不符合是否得到整改？", "evidence": "纠正措施报告", "method": "查阅报告"},
                    {"content": "整改是否得到验证？", "evidence": "验证记录", "method": "查阅记录"},
                    {"content": "是否保留了成文信息？", "evidence": "审核记录", "method": "查阅记录"},
                ],
                scoring_method="符合/不符合",
                applicable_scope="全部适用",
            ),
            "chk_003": Checklist(
                name="ISO 14001 环境因素检查表",
                standard_clause="ISO 14001 6.1.2",
                description="用于审核环境因素识别评价过程",
                items=[
                    {"content": "是否建立了环境因素识别程序？", "evidence": "程序文件", "method": "查阅文件"},
                    {"content": "识别范围是否覆盖全部活动、产品和服务？", "evidence": "环境因素清单", "method": "核对清单"},
                    {"content": "是否考虑了生命周期观点？", "evidence": "识别记录", "method": "查阅记录"},
                    {"content": "是否考虑了异常和紧急情况？", "evidence": "环境因素清单", "method": "核对清单"},
                    {"content": "是否建立了评价准则？", "evidence": "评价程序", "method": "查阅程序"},
                    {"content": "评价方法是否合理？", "evidence": "评价记录", "method": "分析评价方法"},
                    {"content": "是否确定了重要环境因素？", "evidence": "重要环境因素清单", "method": "查阅清单"},
                    {"content": "是否在变更时更新环境因素？", "evidence": "更新记录", "method": "查阅记录"},
                    {"content": "环境因素信息是否保持？", "evidence": "环境因素清单", "method": "查阅清单"},
                    {"content": "重要环境因素是否得到控制？", "evidence": "控制措施", "method": "现场核实"},
                ],
                scoring_method="符合/不符合",
                applicable_scope="全部适用",
            ),
            "chk_004": Checklist(
                name="ISO 45001 危险源辨识检查表",
                standard_clause="ISO 45001 6.1.2",
                description="用于审核危险源辨识评价过程",
                items=[
                    {"content": "是否建立了危险源辨识程序？", "evidence": "程序文件", "method": "查阅文件"},
                    {"content": "辨识范围是否覆盖全部工作场所？", "evidence": "危险源清单", "method": "核对清单"},
                    {"content": "是否考虑了常规和非常规活动？", "evidence": "危险源清单", "method": "核对清单"},
                    {"content": "是否考虑了所有人员？", "evidence": "危险源清单", "method": "核对清单"},
                    {"content": "是否考虑了所有工作状态？", "evidence": "危险源清单", "method": "核对清单"},
                    {"content": "员工是否参与危险源辨识？", "evidence": "参与记录", "method": "查阅记录"},
                    {"content": "是否建立了风险评价方法？", "evidence": "评价程序", "method": "查阅程序"},
                    {"content": "是否确定了重大危险源？", "evidence": "重大危险源清单", "method": "查阅清单"},
                    {"content": "是否在变更时更新危险源？", "evidence": "更新记录", "method": "查阅记录"},
                    {"content": "危险源信息是否保持？", "evidence": "危险源清单", "method": "查阅清单"},
                ],
                scoring_method="符合/不符合",
                applicable_scope="全部适用",
            ),
        }
        return checklists
    
    def add_case(self, case: EnterpriseCase) -> bool:
        """添加企业案例"""
        import uuid
        case_id = str(uuid.uuid4())
        self._cases[case_id] = case
        return self.add_item(case.to_knowledge_item())
    
    def add_template(self, template: Template) -> bool:
        """添加模板"""
        import uuid
        template_id = str(uuid.uuid4())
        self._templates[template_id] = template
        return self.add_item(template.to_knowledge_item())
    
    def add_checklist(self, checklist: Checklist) -> bool:
        """添加检查表"""
        import uuid
        checklist_id = str(uuid.uuid4())
        self._checklists[checklist_id] = checklist
        return self.add_item(checklist.to_knowledge_item())
    
    def get_templates_by_type(self, template_type: str) -> List[Template]:
        """获取指定类型的模板"""
        return [
            t for t in self._templates.values()
            if t.template_type == template_type
        ]
    
    def get_templates_by_standard(self, standard: str) -> List[Template]:
        """获取指定标准的模板"""
        return [
            t for t in self._templates.values()
            if standard in t.applicable_standards
        ]
    
    def get_checklists_by_clause(self, clause: str) -> List[Checklist]:
        """获取指定条款的检查表"""
        return [
            c for c in self._checklists.values()
            if clause in c.standard_clause
        ]
    
    def get_cases_by_industry(self, industry: str) -> List[EnterpriseCase]:
        """获取指定行业的案例"""
        return [
            c for c in self._cases.values()
            if c.industry == industry
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        stats = super().get_statistics()
        stats["cases_count"] = len(self._cases)
        stats["templates_count"] = len(self._templates)
        stats["checklists_count"] = len(self._checklists)
        return stats
