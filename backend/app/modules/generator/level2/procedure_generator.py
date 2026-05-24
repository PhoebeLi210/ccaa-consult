#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二级文件生成器 - 程序文件

每个程序文件独立一个生成器类，便于维护和扩展。

程序文件列表（共27个）：
- B-001 组织环境分析控制程序
- B-002 相关方需求和期望控制程序
- B-003 风险与机遇识别评价控制程序
- B-004 环境因素识别、危险源辨识和风险评价控制程序
- B-005 目标指标和管理方案控制程序
- B-006 基础设施和工作环境控制程序
- B-007 监视和测量设备控制程序
- B-008 组织知识控制程序
- B-009 人力资源控制程序
- B-010 信息交流和沟通控制程序
- B-011 记录控制程序
- B-012 文件控制程序
- B-013 环境、职业健康安全管理体系运行控制程序
- B-014 应急准备和响应控制程序
- B-015 与客户有关的过程控制程序
- B-016 产品和服务的设计开发程序
- B-017 外部提供过程、产品和服务的控制程序
- B-018 服务提供控制程序
- B-019 服务监视和测量控制程序
- B-020 管理体系监视和测量控制程序
- B-021 合规义务管理及合规性评价控制程序
- B-022 客户满意度监测控制程序
- B-023 内部审核控制程序
- B-024 管理评审控制程序
- B-025 不合格（不符合）控制程序
- B-026 事故报告调查处理控制程序
- B-027 改进措施控制程序
"""

from abc import abstractmethod
from typing import List, Optional
from ..base import (
    BaseGenerator,
    CompanyInfo,
    GeneratedDocument,
    FileLevel,
    DocumentType,
)


class BaseProcedureGenerator(BaseGenerator):
    """
    程序文件生成器基类
    
    所有程序文件生成器继承此类
    """
    
    @property
    @abstractmethod
    def procedure_name(self) -> str:
        """程序文件名称"""
        pass
    
    @property
    @abstractmethod
    def procedure_code(self) -> int:
        """程序文件序号"""
        pass
    
    @property
    @abstractmethod
    def purpose(self) -> str:
        """目的"""
        pass
    
    @property
    @abstractmethod
    def scope(self) -> str:
        """适用范围"""
        pass
    
    @property
    @abstractmethod
    def responsibilities(self) -> str:
        """职责"""
        pass
    
    @property
    @abstractmethod
    def procedures(self) -> str:
        """工作程序"""
        pass
    
    @property
    def related_files(self) -> str:
        """相关文件"""
        return ""
    
    @property
    def records(self) -> str:
        """产生的记录"""
        return ""
    
    def _render_procedure(self) -> str:
        """渲染程序文件通用结构"""
        template = f"""
# {{公司名称}} {self.procedure_name}

**文件编号**：{{company_code}}-QESMS-B-{self.procedure_code:03d}

**版本**：A/0

**生效日期**：{{effective_date}}

---

## 1. 目的

{self.purpose}

## 2. 适用范围

{self.scope}

## 3. 职责和权限

{self.responsibilities}

## 4. 工作程序

{self.procedures}

## 5. 相关文件

{self.related_files or "无"}

## 6. 记录

{self.records or "无"}

---

**编制/日期**：
**审核/日期**：
**批准/日期**：
"""
        return self.render(template)
    
    def generate(self) -> GeneratedDocument:
        """生成程序文件"""
        content = self._render_procedure()
        
        return GeneratedDocument(
            file_level=FileLevel.LEVEL_2,
            document_type=DocumentType.PROCEDURE,
            file_code=f"{{company_code}}-QESMS-B-{self.procedure_code:03d}",
            file_name=f"{self.procedure_name}.docx",
            title=self.procedure_name,
            content=content,
            standards=["ISO9001", "ISO14001", "ISO45001"],
            related_clauses=self._get_related_clauses(),
        )
    
    def _get_related_clauses(self) -> List[str]:
        """获取相关条款"""
        return []


# ============================================================
# 具体程序文件生成器
# ============================================================

class EnvironmentAnalysisGenerator(BaseProcedureGenerator):
    """B-001 组织环境分析控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "组织环境分析控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 1
    
    @property
    def purpose(self) -> str:
        return """本程序规定了组织内外部环境分析的方法和要求，确保公司正确识别和分析影响管理体系预期结果的各种因素，为管理决策提供依据。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司各部门对组织内外部环境的分析和监视活动。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 总经理**
- 审批环境分析报告
- 确保提供必要资源

**3.2 管理者代表**
- 组织环境分析活动
- 审核分析结果

**3.3 综合管理部**
- 负责收集内外部环境信息
- 组织环境分析
- 更新分析记录

**3.4 各部门**
- 配合提供相关信息
- 参与环境分析"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 环境信息的收集**

综合管理部负责收集与公司相关的内外部环境信息，包括但不限于：

a） 内部环境信息：
   - 组织结构和职责
   - 资源状况（人力、财务、设施）
   - 企业文化
   - 技术能力
   - 管理现状

b） 外部环境信息：
   - 法律法规要求
   - 行业发展趋势
   - 市场竞争状况
   - 技术发展方向
   - 社会责任要求

**4.2 环境分析**

4.2.1 综合管理部根据收集的信息，组织进行环境分析。

4.2.2 分析应确定对公司实现预期结果能力产生影响的因素。

4.2.3 分析方法可采用SWOT分析、PEST分析等。

**4.3 环境评审**

4.3.1 管理者代表组织对环境分析结果进行评审。

4.3.2 评审结果作为管理评审的输入。

**4.4 信息的更新**

当公司内外部环境发生重大变化时，应及时更新环境分析。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-002 相关方需求和期望控制程序
- BDC-QESMS-B-003 风险与机遇识别评价控制程序
- BDC-QESMS-B-024 管理评审控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-001 组织内外部环境分析表
- BDC-QESMS-D-002 组织内外部环境相关信息的监视和评审"""


class StakeholderNeedsGenerator(BaseProcedureGenerator):
    """B-002 相关方需求和期望控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "相关方需求和期望控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 2
    
    @property
    def purpose(self) -> str:
        return """本程序规定了识别相关方及其需求和期望的方法和要求，确保公司正确理解和满足相关方的合理要求。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司各部门对相关方及其需求和期望的识别和管理活动。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 综合管理部**
- 负责识别和更新相关方清单
- 组织相关方需求分析

**3.2 各部门**
- 提供相关方信息
- 配合相关方需求分析

**3.3 管理者代表**
- 审核相关方分析结果"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 相关方的识别**

综合管理部负责识别与公司相关的内外部相关方，主要包括：

a） 内部相关方：
   - 员工
   - 管理层
   - 股东

b） 外部相关方：
   - 顾客
   - 供应商
   - 政府监管部门
   - 社区
   - 行业协会

**4.2 需求和期望的分析**

4.2.1 对已识别的相关方，分析其对公司提出的需求和期望。

4.2.2 分析应考虑相关方的合法要求以及公司承诺。

**4.3 相关方评审**

管理者代表组织对相关方分析结果进行评审，确定需要采取的对策。

**4.4 信息的更新**

当相关方或其需求发生变化时，应及时更新相关方信息。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-001 组织环境分析控制程序
- BDC-QESMS-B-010 信息交流和沟通控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-003 相关方需求和期望识别表"""


class RiskOpportunityGenerator(BaseProcedureGenerator):
    """B-003 风险与机遇识别评价控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "风险与机遇识别评价控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 3
    
    @property
    def purpose(self) -> str:
        return """本程序规定了识别和评价质量、环境、职业健康安全风险与机遇的方法和要求，确保公司采取有效措施应对风险、把握机遇。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司各部门在质量、环境、职业健康安全领域的风险与机遇管理活动。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 管理者代表**
- 组织风险与机遇识别评价
- 审批风险评价结果

**3.2 综合管理部**
- 收集风险信息
- 组织风险评价
- 编制风险清单

**3.3 各部门**
- 识别本部门的风险
- 配合风险评价工作"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 风险与机遇的识别**

4.1.1 综合管理部组织各部门识别与质量、环境、职业健康安全相关的风险与机遇。

4.1.2 风险识别应考虑：
   - 组织环境分析结果
   - 相关方需求和期望
   - 法律法规要求
   - 历史事件和经验教训

**4.2 风险评价**

4.2.1 对已识别的风险进行评价，确定其重要程度。

4.2.2 风险评价方法可采用风险矩阵法。

**4.3 风险应对**

4.3.1 根据风险评价结果，制定风险应对措施。

4.3.2 风险应对措施包括：规避、降低、转移、接受。

**4.4 机遇的把握**

识别的机遇应进行评估，确定把握机遇的行动计划。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-001 组织环境分析控制程序
- BDC-QESMS-B-002 相关方需求和期望控制程序
- BDC-QESMS-B-005 目标指标和管理方案控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-004 风险与机遇评价与应对措施表"""


class EnvFactorHazardGenerator(BaseProcedureGenerator):
    """B-004 环境因素识别、危险源辨识和风险评价控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "环境因素识别、危险源辨识和风险评价控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 4
    
    @property
    def purpose(self) -> str:
        return """本程序规定了识别和评价环境因素、危险源的方法和要求，为制定环境和职业健康安全管理措施提供依据。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司各部门在日常运营活动中环境因素和危险源的识别与评价。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 综合管理部**
- 组织环境因素和危险源识别
- 编制环境因素清单和危险源清单
- 汇总评价结果

**3.2 各部门**
- 识别本部门的的环境因素和危险源
- 配合评价工作"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 环境因素识别**

4.1.1 各部门识别本部门活动中的环境因素。

4.1.2 环境因素包括：大气污染、水污染、固体废弃物、噪声污染、能源消耗等。

4.1.3 评价重要环境因素，确定需重点控制的因素。

**4.2 危险源辨识**

4.2.1 各部门识别本部门活动中的危险源。

4.2.2 危险源包括：机械伤害、电气伤害、火灾爆炸、中毒窒息、高处坠落等。

4.2.3 评价不可接受风险，制定控制措施。

**4.3 重要环境因素清单**

综合管理部编制《重要环境因素清单》。

**4.4 不可接受风险清单**

综合管理部编制《不可接受风险清单》。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-003 风险与机遇识别评价控制程序
- BDC-QESMS-B-005 目标指标和管理方案控制程序
- BDC-QESMS-B-013 环境、职业健康安全管理体系运行控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-005 环境因素识别与评价表（办公区域）
- BDC-QESMS-D-006 环境因素识别与评价表
- BDC-QESMS-D-007 重要环境因素清单
- BDC-QESMS-D-008 办公区域危险源识别与评价表
- BDC-QESMS-D-009 危险源识别与评价表
- BDC-QESMS-D-010 不可接受风险清单"""


class ObjectiveProgramGenerator(BaseProcedureGenerator):
    """B-005 目标指标和管理方案控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "目标指标和管理方案控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 5
    
    @property
    def purpose(self) -> str:
        return """本程序规定了制定和实施质量、环境、职业健康安全目标、指标和管理方案的方法和要求，确保目标的实现。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司各部门质量、环境、职业健康安全目标、指标和管理方案的制定和实施。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 总经理**
- 审批公司级目标

**3.2 管理者代表**
- 组织目标分解
- 监督目标实施

**3.3 综合管理部**
- 编制公司级目标
- 组织目标分解
- 编制管理方案
- 监督目标完成情况

**3.4 各部门**
- 分解部门目标
- 制定实现措施"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 目标的制定**

4.1.1 综合管理部根据管理方针、公司战略和风险评价结果，制定公司级目标。

4.1.2 目标应与管理方针一致、可测量和可实现、考虑适用要求、得到监视。

**4.2 目标的分解**

各部门根据公司级目标，分解制定部门目标。目标分解应SMART。

**4.3 指标**

为实现目标，制定相应的指标。指标应可测量。

**4.4 管理方案**

为实现目标和指标，制定管理方案。管理方案包括：措施内容、责任部门、完成时间、资源需求。

**4.5 监视和测量**

综合管理部定期监视目标完成情况，编制《目标统计表》。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-003 风险与机遇识别评价控制程序
- BDC-QESMS-B-004 环境因素识别、危险源辨识和风险评价控制程序
- BDC-QESMS-B-024 管理评审控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-012 目标分解表
- BDC-QESMS-D-013 目标统计表
- BDC-QESMS-D-014 环境体系目标管理方案表
- BDC-QESMS-D-016 安全目标管理方案"""


# ============================================================
# B-006 到 B-027 程序文件生成器
# ============================================================

class InfrastructureGenerator(BaseProcedureGenerator):
    """B-006 基础设施和工作环境控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "基础设施和工作环境控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 6
    
    @property
    def purpose(self) -> str:
        return """本程序规定了公司基础设施和工作环境的确定、提供和维护的要求，确保其满足产品和服务符合性的要求。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司建筑物、工作场所、设备设施、运输通讯、信息系统的管理。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 总经理**
- 审批基础设施采购计划
- 审批重大维修改造项目

**3.2 综合管理部**
- 编制基础设施采购计划
- 组织基础设施验收
- 监督维护保养

**3.3 各部门**
- 提出基础设施需求
- 负责日常维护
- 建立设备台账"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 基础设施的确定**

4.1.1 各部门根据工作需要，确定所需的基础设施。

4.1.2 基础设施包括：
   - 建筑物和工作场所
   - 设备（生产设备、办公设备）
   - 运输和通讯设施
   - 信息管理系统

**4.2 基础设施的提供**

4.2.1 综合管理部编制采购计划，报总经理审批。

4.2.2 采购后组织验收，验收合格后方可投入使用。

**4.3 基础设施的维护**

4.3.1 各部门负责本部门基础设施的日常维护。

4.3.2 建立设备维护保养计划，定期保养。

**4.4 工作环境管理**

4.4.1 确保工作环境符合产品要求和人员健康安全要求。

4.4.2 工作环境包括：温度、湿度、照明、清洁度等。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-007 监视和测量设备控制程序
- BDC-QESMS-B-013 环境、职业健康安全管理体系运行控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-017 设备台账
- BDC-QESMS-D-018 设备维护保养计划
- BDC-QESMS-D-019 设备维护保养记录"""


class MonitoringDeviceGenerator(BaseProcedureGenerator):
    """B-007 监视和测量设备控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "监视和测量设备控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 7
    
    @property
    def purpose(self) -> str:
        return """本程序规定了监视和测量设备的配备、校准和维护的要求，确保测量结果的有效性。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司所有用于验证产品符合性的监视和测量设备的管理。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 综合管理部**
- 建立监视和测量设备台账
- 编制校准计划
- 组织校准实施

**3.2 各部门**
- 提出设备需求
- 负责日常维护
- 妥善保管设备"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 设备的配备**

4.1.1 各部门根据测量要求，提出设备需求。

4.1.2 设备应满足测量精度和范围要求。

**4.2 设备的校准**

4.2.1 建立校准计划，定期校准。

4.2.2 校准可委托有资质的机构进行，也可自校准。

4.2.3 校准结果应记录并保存。

**4.3 设备的标识**

4.3.1 设备应有唯一性标识。

4.3.2 校准状态应有标识（合格证、校准标签）。

**4.4 设备的维护**

4.4.1 使用人员应按操作规程使用设备。

4.4.2 发现设备异常应立即停止使用并报告。

**4.5 设备的报废**

设备损坏无法修复或精度不满足要求时，办理报废手续。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-006 基础设施和工作环境控制程序
- BDC-QESMS-B-019 服务监视和测量控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-020 监视和测量设备台账
- BDC-QESMS-D-021 监视和测量设备校准计划
- BDC-QESMS-D-022 监视和测量设备校准记录"""


class KnowledgeGenerator(BaseProcedureGenerator):
    """B-008 组织知识控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "组织知识控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 8
    
    @property
    def purpose(self) -> str:
        return """本程序规定了组织知识的确定、获取、保持和更新的要求，确保组织过程运行和实现产品符合性所需的知识得到管理。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司内部知识（经验、教训、最佳实践）和外部知识（标准、法规、技术资料）的管理。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 综合管理部**
- 组织知识管理活动
- 建立知识库
- 组织知识分享

**3.2 各部门**
- 积累本部门知识
- 参与知识分享
- 应用组织知识"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 知识的确定**

4.1.1 确定运行过程和实现产品符合性所需的知识。

4.1.2 知识来源包括：
   - 内部来源：经验、教训、改进成果
   - 外部来源：标准、法规、学术资料

**4.2 知识的获取**

4.2.1 内部知识通过总结、提炼获取。

4.2.2 外部知识通过收集、学习获取。

**4.3 知识的保持**

4.3.1 建立知识库，分类存储知识。

4.3.2 知识载体包括：文件、记录、数据库、人员经验。

**4.4 知识的更新**

4.4.1 定期评审知识的有效性。

4.4.2 及时更新过时的知识。

**4.5 知识的分享**

通过培训、会议、文档共享等方式分享知识。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-009 人力资源控制程序
- BDC-QESMS-B-012 文件控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-023 组织知识清单
- BDC-QESMS-D-024 知识分享记录"""


class HumanResourceGenerator(BaseProcedureGenerator):
    """B-009 人力资源控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "人力资源控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 9
    
    @property
    def purpose(self) -> str:
        return """本程序规定了人员能力确定、培训、考核的要求，确保从事影响质量、环境、职业健康安全工作的人员具备相应的能力。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司所有员工的能力管理和培训管理。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 总经理**
- 审批培训计划
- 审批人员任职

**3.2 综合管理部**
- 确定岗位能力要求
- 编制培训计划
- 组织培训实施
- 建立培训档案

**3.3 各部门**
- 提出培训需求
- 参与培训实施
- 评价培训效果"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 能力的确定**

4.1.1 综合管理部确定各岗位的能力要求。

4.1.2 能力要求包括：教育、培训、经历、技能。

**4.2 能力的评价**

4.2.1 定期评价人员是否具备岗位能力要求。

4.2.2 评价方式：考核、面试、工作表现。

**4.3 培训**

4.3.1 编制年度培训计划。

4.3.2 培训类型：入职培训、岗位培训、专项培训。

4.3.3 培训实施：内部培训、外部培训。

**4.4 培训效果评价**

4.4.1 培训后进行效果评价。

4.4.2 评价方式：考试、实操、工作表现。

**4.5 培训记录**

建立员工培训档案，保存培训记录。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-008 组织知识控制程序
- BDC-QESMS-B-010 信息交流和沟通控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-025 岗位能力要求表
- BDC-QESMS-D-026 年度培训计划表
- BDC-QESMS-D-027 培训记录表
- BDC-QESMS-D-028 培训效果评价表"""


class CommunicationGenerator(BaseProcedureGenerator):
    """B-010 信息交流和沟通控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "信息交流和沟通控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 10
    
    @property
    def purpose(self) -> str:
        return """本程序规定了内部和外部信息交流的要求，确保管理体系相关信息得到有效传递和沟通。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司内部各部门之间以及公司与外部相关方之间的信息交流。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 管理者代表**
- 审批信息交流计划
- 协调重大信息交流

**3.2 综合管理部**
- 组织内部信息交流
- 负责外部信息交流
- 保存交流记录

**3.3 各部门**
- 参与信息交流
- 反馈交流信息"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 内部信息交流**

4.1.1 内部信息交流内容包括：
   - 管理方针和目标
   - 管理体系运行情况
   - 法律法规要求
   - 事故、事件信息
   - 改进建议

4.1.2 内部交流方式：会议、公告、邮件、内部网站。

**4.2 外部信息交流**

4.2.1 外部信息交流内容包括：
   - 向相关方传达管理方针
   - 接收外部相关方信息
   - 向监管部门报告

4.2.2 外部交流方式：信函、电话、网站、媒体。

**4.3 信息交流记录**

重要信息交流应保存记录。

**4.4 信息保密**

涉及商业秘密的信息应按保密规定处理。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-002 相关方需求和期望控制程序
- BDC-QESMS-B-009 人力资源控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-029 信息交流记录
- BDC-QESMS-D-030 会议记录"""


class RecordControlGenerator(BaseProcedureGenerator):
    """B-011 记录控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "记录控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 11
    
    @property
    def purpose(self) -> str:
        return """本程序规定了记录的标识、贮存、保护、检索、保存期限和处置的要求，为管理体系运行提供证据。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司管理体系运行产生的所有记录的管理。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 综合管理部**
- 制定记录管理规范
- 监督记录管理执行

**3.2 各部门**
- 负责本部门记录的填写
- 负责本部门记录的保管"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 记录的标识**

4.1.1 记录应有唯一性编号。

4.1.2 记录应注明填写日期和填写人。

**4.2 记录的填写**

4.2.1 记录应真实、准确、完整。

4.2.2 填写错误应划改并签名，不得涂改。

**4.3 记录的贮存**

4.3.1 记录应分类存放，便于检索。

4.3.2 贮存环境应防潮、防火、防虫。

**4.4 记录的保护**

4.4.1 电子记录应备份。

4.4.2 纸质记录应妥善保管。

**4.5 记录的保存期限**

根据法规要求和实际需要确定保存期限。

**4.6 记录的处置**

超过保存期限的记录可按规定销毁。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-012 文件控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-031 记录清单
- BDC-QESMS-D-032 记录销毁记录"""


class DocumentControlGenerator(BaseProcedureGenerator):
    """B-012 文件控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "文件控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 12
    
    @property
    def purpose(self) -> str:
        return """本程序规定了管理体系文件的编制、审批、发放、使用、修订和作废的要求，确保文件的有效性和适用性。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司管理体系文件（手册、程序文件、作业指导书、记录表格）的控制。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 总经理**
- 审批管理手册

**3.2 管理者代表**
- 审核程序文件
- 批准作业指导书

**3.3 综合管理部**
- 组织文件编制
- 负责文件发放
- 管理文件档案

**3.4 各部门**
- 参与文件编制
- 正确使用文件"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 文件的编制**

4.1.1 文件编制应依据标准和法规要求。

4.1.2 文件内容应清晰、完整、可操作。

**4.2 文件的审批**

4.2.1 管理手册由总经理审批。

4.2.2 程序文件由管理者代表审核。

4.2.3 作业指导书由部门负责人审批。

**4.3 文件的发放**

4.3.1 文件发放应登记，确保使用处获得有效版本。

4.3.2 作废文件应及时收回。

**4.4 文件的使用**

4.4.1 使用人员应按文件规定执行。

4.4.2 发现文件问题应及时反馈。

**4.5 文件的修订**

4.5.1 文件需要修订时，填写修订申请。

4.5.2 修订后应重新审批。

**4.6 文件的作废**

作废文件应标识并隔离存放。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-011 记录控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-033 文件清单
- BDC-QESMS-D-034 文件发放记录
- BDC-QESMS-D-035 文件修订记录"""


class OperationControlGenerator(BaseProcedureGenerator):
    """B-013 环境、职业健康安全管理体系运行控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "环境、职业健康安全管理体系运行控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 13
    
    @property
    def purpose(self) -> str:
        return """本程序规定了环境和职业健康安全管理体系运行控制的要求，确保对重要环境因素和不可接受风险实施有效控制。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司环境和职业健康安全管理体系运行活动的控制。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 管理者代表**
- 审批运行控制方案
- 监督运行控制实施

**3.2 综合管理部**
- 组织制定运行控制方案
- 监督检查运行控制

**3.3 各部门**
- 实施运行控制措施
- 记录运行控制情况"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 运行控制的策划**

4.1.1 针对重要环境因素和不可接受风险，制定运行控制措施。

4.1.2 运行控制措施包括：
   - 制定作业指导书
   - 设置警示标识
   - 配备防护用品
   - 实施监督检查

**4.2 运行控制的实施**

4.2.1 各部门按规定的控制措施实施。

4.2.2 特殊作业应办理作业许可。

**4.3 相关方的控制**

4.3.1 对供应商、承包方提出环境和安全要求。

4.3.2 监督相关方遵守公司规定。

**4.4 变更管理**

4.4.1 设备、工艺、人员变更时应进行风险评价。

4.4.2 重大变更应审批。

**4.5 运行记录**

运行控制活动应记录。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-004 环境因素识别、危险源辨识和风险评价控制程序
- BDC-QESMS-B-014 应急准备和响应控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-036 运行控制检查记录
- BDC-QESMS-D-037 作业许可记录"""


class EmergencyGenerator(BaseProcedureGenerator):
    """B-014 应急准备和响应控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "应急准备和响应控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 14
    
    @property
    def purpose(self) -> str:
        return """本程序规定了潜在事故和紧急情况的识别、应急准备和响应的要求，最大限度地减少事故造成的损失。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司可能发生的火灾、爆炸、泄漏、伤害等紧急情况的预防和响应。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 总经理**
- 审批应急预案
- 指挥重大事故应急

**3.2 管理者代表**
- 组织应急预案编制
- 组织应急演练

**3.3 综合管理部**
- 编制应急预案
- 组织应急培训
- 管理应急物资

**3.4 各部门**
- 参与应急演练
- 执行应急响应"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 潜在紧急情况的识别**

识别可能发生的紧急情况：火灾、爆炸、泄漏、中毒、伤害、自然灾害等。

**4.2 应急预案的编制**

4.2.1 编制应急预案，内容包括：
   - 应急组织及职责
   - 应急响应程序
   - 应急物资清单
   - 联系方式

4.2.2 应急预案应定期评审和修订。

**4.3 应急准备**

4.3.1 配备必要的应急物资和设备。

4.3.2 设置应急通道和集合点。

4.3.3 组织应急培训。

**4.4 应急演练**

4.4.1 每年至少组织一次应急演练。

4.4.2 演练后进行评估和改进。

**4.5 应急响应**

4.5.1 事故发生时，按应急预案响应。

4.5.2 及时报告和处置。

**4.6 事后处理**

事故后进行调查、分析和改进。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-013 环境、职业健康安全管理体系运行控制程序
- BDC-QESMS-B-026 事故报告调查处理控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-038 应急预案
- BDC-QESMS-D-039 应急演练记录
- BDC-QESMS-D-040 应急物资清单"""


class CustomerProcessGenerator(BaseProcedureGenerator):
    """B-015 与客户有关的过程控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "与客户有关的过程控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 15
    
    @property
    def purpose(self) -> str:
        return """本程序规定了与产品和服务有关要求的确定、评审和沟通的要求，确保公司有能力满足客户要求。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司与客户有关的产品和服务要求的确定、评审和变更管理。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 销售部**
- 负责客户要求的确定
- 组织合同评审
- 负责客户沟通

**3.2 生产部**
- 参与合同评审
- 确认生产能力

**3.3 质量部**
- 参与合同评审
- 确认质量要求"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 要求的确定**

4.1.1 销售部确定客户要求，包括：
   - 客户明示的要求
   - 隐含的要求
   - 法律法规要求
   - 公司的附加要求

**4.2 要求的评审**

4.2.1 在承诺向客户提供产品之前进行评审。

4.2.2 评审内容：
   - 要求是否明确
   - 是否有能力满足
   - 与之前表述不一致的要求是否解决

**4.3 评审结果**

4.3.1 评审通过后签订合同或订单。

4.3.2 评审记录应保存。

**4.4 要求的变更**

4.4.1 客户要求变更时，应重新评审。

4.4.2 变更信息应及时传递到相关部门。

**4.5 客户沟通**

与客户保持沟通，及时处理客户反馈。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-017 外部提供过程、产品和服务的控制程序
- BDC-QESMS-B-022 客户满意度监测控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-041 合同评审记录
- BDC-QESMS-D-042 合同台账
- BDC-QESMS-D-043 客户沟通记录"""


class DesignDevGenerator(BaseProcedureGenerator):
    """B-016 产品和服务的设计开发程序"""
    
    @property
    def procedure_name(self) -> str:
        return "产品和服务的设计开发程序"
    
    @property
    def procedure_code(self) -> int:
        return 16
    
    @property
    def purpose(self) -> str:
        return """本程序规定了产品和服务设计和开发的策划、输入、输出、评审、验证、确认和更改控制的要求。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司新产品和服务的设计开发活动。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 总经理**
- 审批设计开发计划
- 审批设计开发输出

**3.2 技术部**
- 编制设计开发计划
- 组织设计开发活动
- 编制设计开发文件

**3.3 相关部门**
- 参与设计评审
- 配合设计验证"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 设计开发策划**

4.1.1 编制设计开发计划，确定：
   - 设计开发阶段
   - 评审、验证、确认活动
   - 职责和权限

**4.2 设计输入**

4.2.1 确定设计输入，包括：
   - 功能和性能要求
   - 法律法规要求
   - 类似设计信息

**4.3 设计输出**

4.3.1 设计输出应：
   - 满足设计输入要求
   - 为采购、生产提供信息
   - 包含产品接收准则

**4.4 设计评审**

在适宜阶段进行设计评审，评价设计结果满足要求的能力。

**4.5 设计验证**

设计输出应进行验证，确保满足设计输入要求。

**4.6 设计确认**

设计应进行确认，确保产品满足预期使用要求。

**4.7 设计更改**

设计更改应评审、验证、确认，并保存记录。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-015 与客户有关的过程控制程序
- BDC-QESMS-B-017 外部提供过程、产品和服务的控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-044 设计开发计划
- BDC-QESMS-D-045 设计输入清单
- BDC-QESMS-D-046 设计评审记录
- BDC-QESMS-D-047 设计验证记录
- BDC-QESMS-D-048 设计确认记录"""


class ExternalProviderGenerator(BaseProcedureGenerator):
    """B-017 外部提供过程、产品和服务的控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "外部提供过程、产品和服务的控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 17
    
    @property
    def purpose(self) -> str:
        return """本程序规定了外部供方的选择、评价、采购和验证的要求，确保外部提供的过程、产品和服务符合要求。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司原材料采购、外包过程和外部服务的控制。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 采购部**
- 负责供应商选择和评价
- 负责采购实施
- 管理供应商档案

**3.2 质量部**
- 参与供应商评价
- 负责进货检验

**3.3 使用部门**
- 提出采购需求
- 验证采购产品"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 供应商的选择和评价**

4.1.1 供应商评价准则：
   - 质量保证能力
   - 交付能力
   - 价格竞争力
   - 服务水平

4.1.2 评价合格的供应商列入合格供应商名录。

**4.2 采购信息**

4.2.1 采购文件应明确：
   - 产品规格、型号、数量
   - 质量要求
   - 交付要求

4.2.2 必要时，向供应商传达管理体系要求。

**4.3 采购产品的验证**

4.3.1 进货检验或验证。

4.3.2 验证方式：检验、查验合格证明、试用。

**4.4 供应商的再评价**

定期对供应商进行再评价，不合格者取消资格。

**4.5 外包过程控制**

对外包过程进行控制，确保符合要求。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-015 与客户有关的过程控制程序
- BDC-QESMS-B-018 服务提供控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-049 合格供应商名录
- BDC-QESMS-D-050 供应商评价记录
- BDC-QESMS-D-051 采购合同
- BDC-QESMS-D-052 进货检验记录"""


class ServiceProvisionGenerator(BaseProcedureGenerator):
    """B-018 服务提供控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "服务提供控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 18
    
    @property
    def purpose(self) -> str:
        return """本程序规定了服务提供的策划、控制、标识和追溯的要求，确保服务过程受控。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司产品和服务提供过程的控制。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 生产部**
- 负责生产计划编制
- 负责生产过程控制
- 负责产品标识

**3.2 质量部**
- 负责过程检验
- 负责产品放行

**3.3 各工序**
- 按作业指导书操作
- 做好过程记录"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 生产策划**

4.1.1 编制生产计划，确定：
   - 生产流程
   - 资源配置
   - 质量控制点

**4.2 生产过程控制**

4.2.1 按作业指导书操作。

4.2.2 监控过程参数。

4.2.3 做好过程记录。

**4.3 产品标识**

4.3.1 产品应有标识，标明名称、规格、批次。

4.3.2 检验状态应有标识（待检、合格、不合格）。

**4.4 产品追溯**

通过标识和记录实现产品追溯。

**4.5 产品防护**

产品在搬运、贮存、包装过程中应防护。

**4.6 产品放行**

检验合格后方可放行。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-017 外部提供过程、产品和服务的控制程序
- BDC-QESMS-B-019 服务监视和测量控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-053 生产计划
- BDC-QESMS-D-054 生产记录
- BDC-QESMS-D-055 产品标识卡"""


class ServiceMonitoringGenerator(BaseProcedureGenerator):
    """B-019 服务监视和测量控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "服务监视和测量控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 19
    
    @property
    def purpose(self) -> str:
        return """本程序规定了产品和服务监视和测量的要求，确保产品和服务符合要求。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司产品和服务的检验和试验活动。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 质量部**
- 编制检验规程
- 实施检验活动
- 出具检验报告

**3.2 生产部**
- 实施过程检验
- 处理不合格品

**3.3 检验员**
- 按规程检验
- 记录检验结果"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 进货检验**

4.1.1 对采购产品进行检验或验证。

4.1.2 检验合格后方可入库使用。

**4.2 过程检验**

4.2.1 在生产过程中进行检验。

4.2.2 发现不合格应标识、隔离、处置。

**4.3 最终检验**

4.3.1 产品完工后进行最终检验。

4.3.2 检验合格后方可交付。

**4.4 检验记录**

4.4.1 检验应记录，记录应真实、完整。

4.4.2 检验记录应保存。

**4.5 产品放行**

4.5.1 检验合格后由授权人员签发放行。

4.5.2 紧急放行应经批准并记录。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-007 监视和测量设备控制程序
- BDC-QESMS-B-018 服务提供控制程序
- BDC-QESMS-B-025 不合格（不符合）控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-056 进货检验记录
- BDC-QESMS-D-057 过程检验记录
- BDC-QESMS-D-058 最终检验记录
- BDC-QESMS-D-059 检验报告"""


class SystemMonitoringGenerator(BaseProcedureGenerator):
    """B-020 管理体系监视和测量控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "管理体系监视和测量控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 20
    
    @property
    def purpose(self) -> str:
        return """本程序规定了管理体系绩效的监视、测量、分析和评价的要求，确保管理体系的有效性。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司质量、环境、职业健康安全管理体系绩效的监视和测量。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 管理者代表**
- 组织绩效监视和测量
- 分析评价结果

**3.2 综合管理部**
- 收集绩效数据
- 编制绩效报告

**3.3 各部门**
- 提供绩效数据
- 参与绩效分析"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 监视和测量的内容**

4.1.1 质量绩效：
   - 产品合格率
   - 客户投诉率
   - 交付及时率

4.1.2 环境绩效：
   - 污染物排放达标率
   - 能源消耗
   - 废弃物处理

4.1.3 安全绩效：
   - 事故率
   - 隐患整改率
   - 职业病发生率

**4.2 监视和测量的方法**

4.2.1 定期统计和分析。

4.2.2 必要时进行专项检查。

**4.3 分析和评价**

4.3.1 对监测数据进行分析。

4.3.2 评价目标和指标的完成情况。

**4.4 报告**

编制绩效报告，提交管理评审。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-005 目标指标和管理方案控制程序
- BDC-QESMS-B-022 客户满意度监测控制程序
- BDC-QESMS-B-024 管理评审控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-060 绩效监测记录
- BDC-QESMS-D-061 内部审核年度计划"""


class ComplianceGenerator(BaseProcedureGenerator):
    """B-021 合规义务管理及合规性评价控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "合规义务管理及合规性评价控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 21
    
    @property
    def purpose(self) -> str:
        return """本程序规定了合规义务的识别、获取、更新和合规性评价的要求，确保公司遵守适用法律法规和其他要求。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司质量、环境、职业健康安全相关的法律法规和其他要求的管理。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 综合管理部**
- 获取法律法规
- 更新法规清单
- 组织合规性评价

**3.2 各部门**
- 识别本部门适用的法规
- 参与合规性评价"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 法律法规的获取**

4.1.1 通过政府网站、行业协会、咨询机构等渠道获取。

4.1.2 获取渠道应定期确认。

**4.2 法律法规的识别**

4.2.1 识别适用于公司的法律法规。

4.2.2 建立法律法规清单。

**4.3 法律法规的更新**

4.3.1 定期检查法律法规更新情况。

4.3.2 及时更新法律法规清单。

**4.4 合规性评价**

4.4.1 定期进行合规性评价。

4.4.2 评价公司活动是否符合法律法规要求。

**4.5 不合规的处理**

发现不合规情况应制定整改措施。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-001 组织环境分析控制程序
- BDC-QESMS-B-024 管理评审控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-062 法律法规清单
- BDC-QESMS-D-063 合规性评价记录"""


class CustomerSatisfactionGenerator(BaseProcedureGenerator):
    """B-022 客户满意度监测控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "客户满意度监测控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 22
    
    @property
    def purpose(self) -> str:
        return """本程序规定了客户满意度信息的获取、分析和利用的要求，持续改进产品和服务质量。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司客户满意度信息的收集、分析和改进活动。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 销售部**
- 收集客户满意度信息
- 分析客户满意度
- 处理客户投诉

**3.2 质量部**
- 参与客户满意度分析
- 制定改进措施

**3.3 管理者代表**
- 审批满意度报告"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 满意度信息的获取**

4.1.1 获取方式：
   - 客户满意度调查
   - 客户投诉
   - 客户回访
   - 市场反馈

**4.2 满意度调查**

4.2.1 定期进行客户满意度调查。

4.2.2 调查内容：产品质量、交付、服务、价格等。

**4.3 满意度分析**

4.3.1 统计分析满意度数据。

4.3.2 识别不满意项和改进机会。

**4.4 客户投诉处理**

4.4.1 及时受理客户投诉。

4.4.2 分析原因，制定纠正措施。

**4.5 改进**

根据满意度分析结果，制定改进措施。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-015 与客户有关的过程控制程序
- BDC-QESMS-B-025 不合格（不符合）控制程序
- BDC-QESMS-B-027 改进措施控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-064 客户满意度调查表
- BDC-QESMS-D-065 客户投诉处理记录"""


class InternalAuditGenerator(BaseProcedureGenerator):
    """B-023 内部审核控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "内部审核控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 23
    
    @property
    def purpose(self) -> str:
        return """本程序规定了内部审核的策划、实施、报告和跟踪的要求，验证管理体系是否符合标准和组织要求。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司质量、环境、职业健康安全管理体系内部审核活动。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 管理者代表**
- 审批审核计划
- 任命审核组长
- 审批审核报告

**3.2 审核组长**
- 编制审核计划
- 组织审核实施
- 编制审核报告

**3.3 审核员**
- 执行审核任务
- 编制检查表
- 记录审核发现

**3.4 受审核部门**
- 配合审核
- 制定纠正措施"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 审核策划**

4.1.1 编制年度审核计划。

4.1.2 每年至少进行一次完整的内部审核。

**4.2 审核准备**

4.2.1 任命审核组长和审核员。

4.2.2 编制审核检查表。

4.2.3 通知受审核部门。

**4.3 审核实施**

4.3.1 召开首次会议。

4.3.2 现场审核，收集证据。

4.3.3 召开末次会议。

**4.4 审核报告**

4.4.1 编制审核报告。

4.4.2 报告内容包括：审核范围、依据、发现、结论。

**4.5 纠正措施跟踪**

4.5.1 受审核部门制定纠正措施。

4.5.2 验证纠正措施的有效性。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-024 管理评审控制程序
- BDC-QESMS-B-027 改进措施控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-061 内部审核年度计划
- BDC-QESMS-D-066 内审报告
- BDC-QESMS-D-067 内审检查表
- BDC-QESMS-D-068 不符合报告"""


class ManagementReviewGenerator(BaseProcedureGenerator):
    """B-024 管理评审控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "管理评审控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 24
    
    @property
    def purpose(self) -> str:
        return """本程序规定了管理评审的策划、输入、输出和跟踪的要求，确保管理体系的持续适宜性、充分性和有效性。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司质量、环境、职业健康安全管理体系管理评审活动。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 总经理**
- 主持管理评审
- 审批评审报告
- 做出评审决策

**3.2 管理者代表**
- 组织管理评审
- 编制评审报告
- 跟踪评审决议

**3.3 各部门**
- 准备评审输入
- 参与评审
- 执行评审决议"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 评审策划**

4.1.1 每年至少进行一次管理评审。

4.1.2 制定评审计划，确定评审时间和内容。

**4.2 评审输入**

评审输入包括：
   - 以往管理评审的跟踪措施
   - 环境变化
   - 目标实现程度
   - 过程绩效和产品符合性
   - 不合格和纠正措施
   - 监视和测量结果
   - 审核结果
   - 相关方反馈
   - 改进建议

**4.3 评审实施**

4.3.1 总经理主持评审会议。

4.3.2 各部门汇报输入材料。

4.3.3 评审管理体系适宜性、充分性、有效性。

**4.4 评审输出**

评审输出包括：
   - 改进机会
   - 管理体系变更需求
   - 资源需求

**4.5 跟踪验证**

跟踪评审决议的执行情况。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-005 目标指标和管理方案控制程序
- BDC-QESMS-B-023 内部审核控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-069 管理评审计划
- BDC-QESMS-D-070 管理评审输入材料
- BDC-QESMS-D-071 管理评审报告"""


class NonconformityGenerator(BaseProcedureGenerator):
    """B-025 不合格（不符合）控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "不合格（不符合）控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 25
    
    @property
    def purpose(self) -> str:
        return """本程序规定了不合格品和不符合项的识别、评审、处置和纠正措施的要求，防止不合格品非预期使用和不符合项再次发生。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司采购产品、生产过程和交付产品的不合格控制，以及管理体系运行中的不符合控制。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 质量部**
- 识别不合格品
- 评审不合格品
- 监督处置

**3.2 生产部**
- 标识不合格品
- 隔离不合格品
- 执行处置决定

**3.3 综合管理部**
- 识别不符合项
- 组织纠正措施"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 不合格品的识别**

4.1.1 检验发现不合格品应立即标识。

4.1.2 不合格品应隔离存放。

**4.2 不合格品的评审**

4.2.1 评审不合格品的性质和程度。

4.2.2 确定处置方式：返工、返修、让步接收、降级、报废。

**4.3 不合格品的处置**

4.3.1 按评审决定处置。

4.3.2 返工返修后应重新检验。

**4.4 不符合的控制**

4.4.1 发现不符合项应记录。

4.4.2 分析原因，制定纠正措施。

**4.5 纠正措施**

4.5.1 针对原因制定措施。

4.5.2 验证措施有效性。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-019 服务监视和测量控制程序
- BDC-QESMS-B-027 改进措施控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-072 不合格品报告
- BDC-QESMS-D-073 不合格品处置记录
- BDC-QESMS-D-074 纠正措施记录"""


class AccidentReportGenerator(BaseProcedureGenerator):
    """B-026 事故报告调查处理控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "事故报告调查处理控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 26
    
    @property
    def purpose(self) -> str:
        return """本程序规定了事故和事件的报告、调查、处理和预防的要求，防止事故再次发生。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司范围内发生的各类事故和未遂事件的报告、调查和处理。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 总经理**
- 审批重大事故报告
- 确保事故调查资源

**3.2 管理者代表**
- 组织事故调查
- 审核事故报告

**3.3 综合管理部**
- 接收事故报告
- 组织事故调查
- 统计事故数据

**3.4 各部门**
- 及时报告事故
- 参与事故调查
- 执行整改措施"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 事故报告**

4.1.1 发生事故应立即报告。

4.1.2 重大事故应在规定时间内上报监管部门。

**4.2 事故调查**

4.2.1 成立调查组，进行调查。

4.2.2 调查内容：事故经过、原因、责任、损失。

**4.3 事故处理**

4.3.1 根据调查结果，确定处理意见。

4.3.2 对责任人员进行处理。

**4.4 整改措施**

4.4.1 制定整改措施，消除事故隐患。

4.4.2 验证整改措施的有效性。

**4.5 事故统计**

定期统计事故数据，分析事故趋势。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-014 应急准备和响应控制程序
- BDC-QESMS-B-027 改进措施控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-075 事故报告
- BDC-QESMS-D-076 事故调查报告
- BDC-QESMS-D-077 事故统计表"""


class ImprovementGenerator(BaseProcedureGenerator):
    """B-027 改进措施控制程序"""
    
    @property
    def procedure_name(self) -> str:
        return "改进措施控制程序"
    
    @property
    def procedure_code(self) -> int:
        return 27
    
    @property
    def purpose(self) -> str:
        return """本程序规定了纠正措施、预防措施和持续改进的要求，消除不合格原因，防止不合格发生，持续改进管理体系。"""
    
    @property
    def scope(self) -> str:
        return """本程序适用于公司质量、环境、职业健康安全管理体系的改进活动。"""
    
    @property
    def responsibilities(self) -> str:
        return """**3.1 管理者代表**
- 审批重大改进措施
- 监督改进实施

**3.2 综合管理部**
- 组织改进活动
- 跟踪改进措施
- 验证改进效果

**3.3 各部门**
- 提出改进建议
- 实施改进措施
- 验证改进效果"""
    
    @property
    def procedures(self) -> str:
        return """**4.1 改进机会的识别**

4.1.1 改进机会来源：
   - 不合格和投诉
   - 审核发现
   - 管理评审决议
   - 绩效监测结果
   - 风险评价结果

**4.2 纠正措施**

4.2.1 针对已发生的不合格，分析原因。

4.2.2 制定措施消除原因，防止再发生。

4.2.3 实施措施并验证有效性。

**4.3 预防措施**

4.3.1 针对潜在的不合格，分析原因。

4.3.2 制定措施消除原因，防止发生。

4.3.3 实施措施并验证有效性。

**4.4 持续改进**

4.4.1 通过管理方针、目标、审核结果、数据分析、纠正措施等实现持续改进。

4.4.2 改进活动应记录。"""
    
    @property
    def related_files(self) -> str:
        return """- BDC-QESMS-B-023 内部审核控制程序
- BDC-QESMS-B-024 管理评审控制程序
- BDC-QESMS-B-025 不合格（不符合）控制程序"""
    
    @property
    def records(self) -> str:
        return """- BDC-QESMS-D-078 纠正措施记录
- BDC-QESMS-D-079 预防措施记录
- BDC-QESMS-D-080 改进记录"""


# ============================================================
# 程序文件工厂函数
# ============================================================

def generate_procedure(company_info: CompanyInfo, procedure_code: int) -> GeneratedDocument:
    """
    生成指定序号的程序文件
    
    Args:
        company_info: 企业信息
        procedure_code: 程序文件序号（1-27）
        
    Returns:
        生成的程序文件
    """
    generators = {
        1: EnvironmentAnalysisGenerator,
        2: StakeholderNeedsGenerator,
        3: RiskOpportunityGenerator,
        4: EnvFactorHazardGenerator,
        5: ObjectiveProgramGenerator,
        6: InfrastructureGenerator,
        7: MonitoringDeviceGenerator,
        8: KnowledgeGenerator,
        9: HumanResourceGenerator,
        10: CommunicationGenerator,
        11: RecordControlGenerator,
        12: DocumentControlGenerator,
        13: OperationControlGenerator,
        14: EmergencyGenerator,
        15: CustomerProcessGenerator,
        16: DesignDevGenerator,
        17: ExternalProviderGenerator,
        18: ServiceProvisionGenerator,
        19: ServiceMonitoringGenerator,
        20: SystemMonitoringGenerator,
        21: ComplianceGenerator,
        22: CustomerSatisfactionGenerator,
        23: InternalAuditGenerator,
        24: ManagementReviewGenerator,
        25: NonconformityGenerator,
        26: AccidentReportGenerator,
        27: ImprovementGenerator,
    }
    
    generator_class = generators.get(procedure_code)
    if not generator_class:
        raise ValueError(f"未知的程序文件序号: {procedure_code}")
    
    generator = generator_class(company_info)
    return generator.generate()


def generate_all_procedures(company_info: CompanyInfo) -> List[GeneratedDocument]:
    """
    生成所有程序文件
    
    Args:
        company_info: 企业信息
        
    Returns:
        生成的程序文件列表
    """
    documents = []
    
    for code in range(1, 28):
        try:
            doc = generate_procedure(company_info, code)
            documents.append(doc)
        except Exception as e:
            print(f"生成程序文件 B-{code:03d} 失败: {e}")
    
    return documents
