#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四级文件生成器 - 记录表格

四级文件（记录表格）按ISO条款分类：

| ISO条款 | 文件编号 | 文件名称 |
|---------|----------|----------|
| 4.1 理解组织及其环境 | D-001, D-002 | 组织内外部环境分析表 |
| 4.2 相关方 | D-003 | 相关方需求和期望识别表 |
| 5.3 职责权限 | D-079 | 各部门负责人及内审员任命书 |
| 6.1 风险和机遇 | D-004 | 风险与机遇评价与应对措施表 |
| 6.1.2 环境因素 | D-005~D-007 | 环境因素识别与评价表 |
| 6.1.2 危险源 | D-008~D-010 | 危险源识别与评价表 |
| 6.1.3 合规义务 | D-011 | 法律法规和其他要求清单 |
| 6.2 目标 | D-012~D-017 | 目标管理方案表 |
| 7.1.3 基础设施 | D-018~D-022 | 设备台账、维保记录 |
| 7.1.5 监视测量资源 | D-023~D-024 | 计量器具台账、检定计划 |
| 7.1.6 组织知识 | D-025 | 知识管理清单 |
| 7.2 能力 | D-026~D-028 | 培训计划、记录、能力确认 |
| 7.4 信息交流 | D-029 | 相关方告知书 |
| 7.5 文件控制 | D-030~D-035 | 受控文件清单、记录控制一览表 |
| 8.1 运行控制 | D-036~D-040 | 固废处置、运行检查、能耗统计 |
| 8.2 应急准备 | D-041~D-044 | 应急预案 |
| 8.4 外部提供 | D-049~D-051 | 供应商评审、绩效记录 |
| 9.1.2 合规评价 | D-058~D-060 | 合规性评价 |
| 9.2 内部审核 | D-061~D-067 | 内审计划、报告、检查表 |
| 9.3 管理评审 | D-053, D-068~D-073 | 管评输入、报告、改进计划 |
| 10.2 不合格 | D-074~D-078 | 纠正措施单、事故报告 |

每个记录表格独立生成，便于维护和扩展。
"""

from abc import abstractmethod
from typing import List, Optional, Dict
from ..base import (
    BaseGenerator,
    CompanyInfo,
    GeneratedDocument,
    FileLevel,
    DocumentType,
)


class BaseLevel4Generator(BaseGenerator):
    """四级文件生成器基类"""
    
    @property
    @abstractmethod
    def file_name(self) -> str:
        """文件名称"""
        pass
    
    @property
    @abstractmethod
    def file_code(self) -> int:
        """文件序号"""
        pass
    
    @property
    @abstractmethod
    def iso_clause(self) -> str:
        """对应ISO条款"""
        pass
    
    @property
    def system_category(self) -> str:
        """体系类别"""
        return "■质量管理体系 / ■环境管理体系 / ■职业健康安全管理体系"


# ============================================================
# 记录表格生成器
# ============================================================

class FormGenerator(BaseLevel4Generator):
    """通用记录表格生成器"""
    
    def _render_form(self, table_structure: str, signature_fields: List[str] = None) -> str:
        """渲染记录表格"""
        if signature_fields is None:
            signature_fields = ["编制", "审核", "批准"]
        
        template = f"""
# {{company_name}} {{file_name}}

**文件编号**：{{company_code}}-QESMS-D-{self.file_code:03d}

**类别**：{self.system_category}

---

## 表格信息

| 项目 | 内容 |
|------|------|
| ISO条款 | {self.iso_clause} |
| 版本 | A/0 |
| 生效日期 | {{effective_date}} |

---

{table_structure}

---

## 签字栏

| 岗位 | 姓名 | 日期 | 签名 |
|------|------|------|------|
""" + "\n".join([f"| {field} | | | |" for field in signature_fields])
        
        return self.render(template)
    
    def generate(self) -> GeneratedDocument:
        """生成记录表格"""
        content = self._render_form(self._get_table_structure())
        
        return GeneratedDocument(
            file_level=FileLevel.LEVEL_4,
            document_type=DocumentType.FORM,
            file_code=self.get_level4_file_code(self.file_code),
            file_name=f"{self.file_name}.docx",
            title=self.file_name,
            content=content,
        )
    
    @abstractmethod
    def _get_table_structure(self) -> str:
        """获取表格结构"""
        pass


# 具体记录表格生成器

class EnvironmentAnalysisFormGenerator(FormGenerator):
    """D-001 组织内外部环境分析表"""
    
    @property
    def file_name(self) -> str:
        return "组织内外部环境分析表"
    
    @property
    def file_code(self) -> int:
        return 1
    
    @property
    def iso_clause(self) -> str:
        return "4.1 理解组织及其环境"
    
    def _get_table_structure(self) -> str:
        return """
## 分析内容

| 序号 | 类别 | 分析项目 | 具体内容 | 影响分析 | 应对措施 |
|------|------|----------|----------|----------|----------|
| 1 | 内部环境 | 组织结构 | | | |
| 2 | 内部环境 | 资源状况 | | | |
| 3 | 内部环境 | 企业文化 | | | |
| 4 | 内部环境 | 技术能力 | | | |
| 5 | 外部环境 | 法律法规 | | | |
| 6 | 外部环境 | 行业发展 | | | |
| 7 | 外部环境 | 市场竞争 | | | |
| 8 | 外部环境 | 技术发展 | | | |
"""


class StakeholderFormGenerator(FormGenerator):
    """D-003 相关方需求和期望识别表"""
    
    @property
    def file_name(self) -> str:
        return "相关方需求和期望识别表"
    
    @property
    def file_code(self) -> int:
        return 3
    
    @property
    def iso_clause(self) -> str:
        return "4.2 理解相关方的需求和期望"
    
    def _get_table_structure(self) -> str:
        return """
## 相关方识别

| 序号 | 相关方名称 | 相关方类型 | 需求和期望 | 是否合规 | 应对措施 |
|------|------------|------------|------------|----------|----------|
| 1 | 顾客 | 外部 | | | |
| 2 | 员工 | 内部 | | | |
| 3 | 供应商 | 外部 | | | |
| 4 | 政府 | 外部 | | | |
| 5 | 社区 | 外部 | | | |
| 6 | 股东 | 内部 | | | |
"""


class ObjectiveDecompositionFormGenerator(FormGenerator):
    """D-012 目标分解表"""
    
    @property
    def file_name(self) -> str:
        return "目标分解表"
    
    @property
    def file_code(self) -> int:
        return 12
    
    @property
    def iso_clause(self) -> str:
        return "6.2 目标及其实现的策划"
    
    def _get_table_structure(self) -> str:
        return """
## 目标分解

| 序号 | 目标类别 | 公司级目标 | 分解部门 | 部门目标 | 指标 | 目标值 | 评价周期 |
|------|----------|------------|----------|----------|------|--------|----------|
| 1 | 质量目标 | | | | | | |
| 2 | 环境目标 | | | | | | |
| 3 | 安全目标 | | | | | | |
"""


class TrainingPlanFormGenerator(FormGenerator):
    """D-026 年度培训计划表"""
    
    @property
    def file_name(self) -> str:
        return "年度培训计划表"
    
    @property
    def file_code(self) -> int:
        return 26
    
    @property
    def iso_clause(self) -> str:
        return "7.2 能力"
    
    def _get_table_structure(self) -> str:
        return """
## 培训计划

| 序号 | 培训项目 | 培训内容 | 培训对象 | 培训方式 | 计划时间 | 培训教师 | 预算费用 | 备注 |
|------|----------|----------|----------|----------|----------|----------|----------|------|
| 1 | | | | | | | | |
| 2 | | | | | | | | |
| 3 | | | | | | | | |
"""


class TrainingRecordFormGenerator(FormGenerator):
    """D-027 培训记录表"""
    
    @property
    def file_name(self) -> str:
        return "培训记录表"
    
    @property
    def file_code(self) -> int:
        return 27
    
    @property
    def iso_clause(self) -> str:
        return "7.2 能力"
    
    def _get_table_structure(self) -> str:
        return """
## 培训记录

| 序号 | 培训项目 | 培训内容 | 培训时间 | 培训地点 | 培训教师 | 培训方式 | 培训学时 |
|------|----------|----------|----------|----------|----------|----------|----------|
| 1 | | | | | | | |
| 2 | | | | | | | |

## 培训签到

| 序号 | 姓名 | 部门 | 职位 | 签到 | 考核成绩 | 备注 |
|------|------|------|------|------|----------|------|
| 1 | | | | | | |
| 2 | | | | | | |
"""


class InternalAuditPlanFormGenerator(FormGenerator):
    """D-061 内部审核年度计划"""
    
    @property
    def file_name(self) -> str:
        return "内部审核年度计划"
    
    @property
    def file_code(self) -> int:
        return 61
    
    @property
    def iso_clause(self) -> str:
        return "9.2 内部审核"
    
    def _get_table_structure(self) -> str:
        return """
## 审核目的

验证公司质量、环境、职业健康安全管理体系是否符合标准要求和文件规定，是否得到有效实施和保持。

## 审核范围

质量、环境、职业健康安全管理体系所覆盖的所有部门和过程。

## 审核依据

1. ISO 9001:2015标准
2. ISO 14001:2018标准
3. ISO 45001:2018标准
4. 公司管理体系文件
5. 适用法律法规

## 审核计划

| 序号 | 审核时间 | 审核范围 | 审核组 | 审核类型 | 备注 |
|------|----------|----------|--------|----------|------|
| 1 | | | | 内审 | |
| 2 | | | | 内审 | |

---

**编制**：
**审核**：
**批准**：
"""


class InternalAuditReportFormGenerator(FormGenerator):
    """D-066 内审报告"""
    
    @property
    def file_name(self) -> str:
        return "内审报告"
    
    @property
    def file_code(self) -> int:
        return 66
    
    @property
    def iso_clause(self) -> str:
        return "9.2 内部审核"
    
    def _get_table_structure(self) -> str:
        return """
## 审核基本信息

| 项目 | 内容 |
|------|------|
| 审核日期 | |
| 审核范围 | |
| 审核依据 | |
| 审核组长 | |
| 审核组员 | |

## 审核概况

### 审核过程概述

（描述审核过程）

### 主要发现

（描述审核中发现的问题）

## 审核结论

### 体系符合性评价

（评价体系是否符合标准要求）

### 体系有效性评价

（评价体系是否有效实施）

### 主要不符合项

（列出主要不符合项）

## 改进建议

（提出改进建议）

## 附件

1. 不符合报告汇总表
2. 审核签到表
3. 审核检查表

---

**编写**：
**审核**：
**批准**：
**日期**：
"""


class ManagementReviewReportFormGenerator(FormGenerator):
    """D-071 管理评审报告"""
    
    @property
    def file_name(self) -> str:
        return "管理评审报告"
    
    @property
    def file_code(self) -> int:
        return 71
    
    @property
    def iso_clause(self) -> str:
        return "9.3 管理评审"
    
    def _get_table_structure(self) -> str:
        return """
## 管理评审基本信息

| 项目 | 内容 |
|------|------|
| 评审日期 | |
| 评审周期 | |
| 主持人 | |
| 参加人员 | |

## 评审输入

### 1. 以往管理评审跟踪措施的情况

（跟踪以往评审决议的执行情况）

### 2. 与质量、环境、职业健康安全管理体系相关的内外部因素变化

（内外部环境变化情况）

### 3. 相关方需求和期望的变化

（顾客、供应商等需求变化）

### 4. 顾客满意和有关相关方的反馈

（顾客满意度情况）

### 5. 质量管理目标的实现程度

（质量目标完成情况）

### 6. 过程绩效和产品的符合性

（过程和产品符合性情况）

### 7. 不合格和纠正措施的状况

（不合格和纠正措施情况）

### 8. 审核结果

（内部审核、外部审核结果）

### 9. 资源需求

（资源需求情况）

### 10. 应对风险和机遇的措施

（风险和机遇应对情况）

## 评审输出

### 1. 持续适宜性、充分性和有效性的决定

（评审结论）

### 2. 管理体系变更的需求

（需要变更的内容）

### 3. 资源需求

（需要增加或调整的资源）

### 4. 改进的机会

（改进建议）

---

**编制**：
**审核**：
**批准**：
**日期**：
"""


# ============================================================
# 工厂函数
# ============================================================

def generate_level4_form(company_info: CompanyInfo, file_code: int) -> GeneratedDocument:
    """生成指定记录表格"""
    generators = {
        1: EnvironmentAnalysisFormGenerator,
        3: StakeholderFormGenerator,
        12: ObjectiveDecompositionFormGenerator,
        26: TrainingPlanFormGenerator,
        27: TrainingRecordFormGenerator,
        61: InternalAuditPlanFormGenerator,
        66: InternalAuditReportFormGenerator,
        71: ManagementReviewReportFormGenerator,
        # 可继续添加更多
    }
    
    generator_class = generators.get(file_code)
    if not generator_class:
        raise ValueError(f"未知的四级文件序号: {file_code}")
    
    generator = generator_class(company_info)
    return generator.generate()


def generate_all_level4_forms(company_info: CompanyInfo) -> List[GeneratedDocument]:
    """生成所有四级文件"""
    documents = []
    
    # 可按需生成所有或部分四级文件
    implemented = [
        EnvironmentAnalysisFormGenerator,
        StakeholderFormGenerator,
        ObjectiveDecompositionFormGenerator,
        TrainingPlanFormGenerator,
        TrainingRecordFormGenerator,
        InternalAuditPlanFormGenerator,
        InternalAuditReportFormGenerator,
        ManagementReviewReportFormGenerator,
    ]
    
    for generator_class in implemented:
        generator = generator_class(company_info)
        documents.append(generator.generate())
    
    return documents
