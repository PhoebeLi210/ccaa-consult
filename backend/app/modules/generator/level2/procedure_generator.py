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
# {{公司名称}} {{procedure_name}}

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

4.2.2 风险评价方法可采用风险矩阵法：

| 风险等级 | 说明 | 处理要求 |
|----------|------|----------|
| 重大风险 | 发生概率高，后果严重 | 必须采取控制措施 |
| 中等风险 | 发生概率中等，后果较重 | 应采取控制措施 |
| 低风险 | 发生概率低，后果轻微 | 保持监视 |

**4.3 风险应对**

4.3.1 根据风险评价结果，制定风险应对措施。

4.3.2 风险应对措施包括：
   - 规避：消除风险源
   - 降低：采取控制措施减少风险
   - 转移：购买保险或外包
   - 接受：保留风险但加强监视

**4.4 机遇的把握**

4.4.1 识别的机遇应进行评估，确定把握机遇的行动计划。

4.4.2 机遇行动计划应纳入管理方案的策划。"""
    
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

4.1.2 环境因素包括：
   - 大气污染
   - 水污染
   - 固体废弃物
   - 噪声污染
   - 能源消耗
   - 材料消耗

4.1.3 评价重要环境因素，确定需重点控制的因素。

**4.2 危险源辨识**

4.2.1 各部门识别本部门活动中的危险源。

4.2.2 危险源包括：
   - 机械伤害
   - 电气伤害
   - 火灾爆炸
   - 中毒窒息
   - 高处坠落
   - 物体打击

4.2.3 评价不可接受风险，制定控制措施。

**4.3 重要环境因素清单**

综合管理部编制《重要环境因素清单》（BDC-QESMS-D-007）。

**4.4 不可接受风险清单**

综合管理部编制《不可接受风险清单》（BDC-QESMS-D-010）。"""
    
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

4.1.2 目标应：
   - 与管理方针一致
   - 可测量和可实现
   - 考虑适用要求
   - 得到监视

**4.2 目标的分解**

4.2.1 各部门根据公司级目标，分解制定部门目标。

4.2.2 目标分解应 SMART：
   - Specific（具体）
   - Measurable（可测量）
   - Achievable（可实现）
   - Relevant（相关）
   - Time-bound（有时限）

**4.3 指标**

4.3.1 为实现目标，制定相应的指标。

4.3.2 指标应可测量。

**4.4 管理方案**

4.4.1 为实现目标和指标，制定管理方案。

4.4.2 管理方案包括：
   - 措施内容
   - 责任部门
   - 完成时间
   - 资源需求

**4.5 监视和测量**

综合管理部定期监视目标完成情况，编制《目标统计表》（BDC-QESMS-D-013）。"""
    
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
        # ... 可继续添加更多
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
    
    # 已实现的程序文件生成器
    implemented = [
        EnvironmentAnalysisGenerator,
        StakeholderNeedsGenerator,
        RiskOpportunityGenerator,
        EnvFactorHazardGenerator,
        ObjectiveProgramGenerator,
    ]
    
    for generator_class in implemented:
        generator = generator_class(company_info)
        documents.append(generator.generate())
    
    return documents
