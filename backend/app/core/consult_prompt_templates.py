#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 咨询专用 Prompt 模板库

本模块为 ISO 管理体系咨询文档生成提供结构化 Prompt 模板，包含：
- 事实锁定系统提示词（约束 AI 只能使用已提取的真实数据）
- 四段式写作模板（目的-范围-职责-程序/内容）
- 各类文档生成 Prompt 构建函数
- 事实约束生成 Prompt（核心：注入真实数据，限制 AI 只负责语言组织）
- 咨询顾问常用表达库

设计原则：
1. 事实优先：所有 Prompt 强调基于已提取的企业真实信息，禁止编造
2. 结构化输出：模板定义清晰的文档结构框架
3. 可组合：各函数可独立使用，也可通过 build_fact_locked_prompt() 组合
"""

from typing import Dict, List, Optional, Any


# ===========================================================================
# 1. 事实锁定系统提示词
# ===========================================================================

FACT_LOCK_SYSTEM_PROMPT = """你是一位资深 ISO 管理体系认证咨询顾问，拥有 15 年以上咨询经验。
你正在为一家企业编写 ISO 管理体系认证文件。

## 核心约束（必须严格遵守）

### 事实锁定规则
1. **只使用提供的数据**：你只能使用下方「企业真实数据」区块中明确列出的信息。对于数据中未提及的内容，应使用通用、合规的表述，绝不允许编造具体名称、数字、日期或细节。
2. **禁止幻觉**：不得生成任何未在提供数据中出现的人名、地名、公司名、产品名、设备名、部门名、证书编号等具体实体。
3. **数据标注**：当引用企业真实数据时，保持原文；当使用通用表述时，使用自然语言，不添加任何标记。
4. **合理推断**：仅允许基于已有数据进行合理的逻辑推断（例如：有"生产部"可推断存在"生产活动"），但不得推断具体数字或未列出的实体。

### 写作规范
- 语言风格：正式、规范、简洁，符合 ISO 体系文件编写要求
- 术语使用：准确使用 ISO 标准术语（如"过程""确认""验证""纠正措施"等）
- 人称视角：使用第三人称，以企业为主体
- 格式要求：按提供的文档结构模板组织内容，保持层级清晰

### 输出要求
- 直接输出文档正文内容，不要输出任何解释、注释或元信息
- 严格按照指定的文档结构组织内容
- 每个章节/条款内容充实、具体，避免空洞泛泛"""


# ===========================================================================
# 2. 四段式写作模板
# ===========================================================================

FOUR_SECTION_TEMPLATE = """## 文档编写要求

请严格按照以下四段式结构编写文档内容：

### 第一段：目的
- 说明制定本文件的目的和意图
- 阐述本文件在管理体系中的作用和意义
- 格式："本文件规定了……的职责、方法和要求，以确保……"

### 第二段：范围
- 明确本文件适用的部门、过程、活动或场所
- 说明本文件不适用的情况（如有）
- 格式："本文件适用于……"

### 第三段：职责
- 按部门/岗位列出与本文件相关的职责
- 每项职责应明确"谁"负责"什么"
- 格式："XX部：负责……"

### 第四段：工作程序 / 具体内容
- 按照业务流程的逻辑顺序编写
- 每个步骤应包含：做什么、谁做、何时做、如何做、形成什么记录
- 必要时包含流程描述、控制要求、异常处理等内容"""


# ===========================================================================
# 3. 质量手册生成 Prompt
# ===========================================================================

def build_manual_prompt(
    company_name: str,
    standards: List[str],
    scope_description: str,
    extracted_data: Dict[str, Any],
    doc_number: str = "",
) -> str:
    """构建质量手册生成 Prompt

    Args:
        company_name: 企业名称
        standards: 适用的标准列表，如 ["ISO9001:2015", "ISO14001:2015"]
        scope_description: 认证范围描述
        extracted_data: 已提取的企业真实数据字典
        doc_number: 文件编号

    Returns:
        完整的用户 Prompt
    """
    standards_str = "、".join(standards)
    data_json = _format_extracted_data(extracted_data)

    return f"""请为以下企业编写《质量手册》。

## 企业基本信息
- 企业名称：{company_name}
- 适用标准：{standards_str}
- 认证范围：{scope_description}
- 文件编号：{doc_number or "QM-01"}

## 企业真实数据（事实来源）
{data_json}

## 文档结构要求
请按以下章节结构编写质量手册：

1. 发布令 / 批准页
2. 企业概况
3. 管理体系范围
4. 组织结构与职责分配
5. 管理体系要求
   5.1 领导作用与承诺
   5.2 方针与目标
   5.3 组织的角色、职责与权限
   5.4 策划（风险和机遇、目标及其实现的策划、变更的策划）
   5.5 支持（资源、能力、意识、沟通、成文信息）
   5.6 运行（运行策划和控制、产品和服务的要求、设计和开发、外部提供过程产品和服务的控制、生产和服务的提供、产品和服务的放行、不合格输出的控制）
   5.7 绩效评价（监视测量分析和评价、内部审核、管理评审）
   5.8 改进（总则、不合格和纠正措施、持续改进）
6. 附录（程序文件清单、组织架构图等）

## 写作要求
- 质量手册是体系的纲领性文件，内容应覆盖标准全部条款
- 各条款描述应与企业实际情况结合，体现企业特色
- 对于企业数据中未涉及的内容，使用通用合规表述
- 语言正式、规范，符合认证审核要求"""


# ===========================================================================
# 4. 程序文件生成 Prompt
# ===========================================================================

def build_procedure_prompt(
    procedure_name: str,
    company_name: str,
    clause_ref: str,
    extracted_data: Dict[str, Any],
    related_departments: Optional[List[str]] = None,
    doc_number: str = "",
) -> str:
    """构建程序文件生成 Prompt

    Args:
        procedure_name: 程序文件名称，如"文件控制程序"
        company_name: 企业名称
        clause_ref: 对应的标准条款号，如"7.5"
        extracted_data: 已提取的企业真实数据字典
        related_departments: 相关部门列表
        doc_number: 文件编号

    Returns:
        完整的用户 Prompt
    """
    departments_str = "、".join(related_departments) if related_departments else "（根据企业实际部门确定）"
    data_json = _format_extracted_data(extracted_data)

    return f"""请为以下企业编写程序文件。

## 文件信息
- 企业名称：{company_name}
- 文件名称：{procedure_name}
- 对应条款：{clause_ref}
- 相关部门：{departments_str}
- 文件编号：{doc_number or ""}

## 企业真实数据（事实来源）
{data_json}

## 文档结构要求

{FOUR_SECTION_TEMPLATE}

### 具体章节结构
1. 目的
2. 范围
3. 职责
4. 工作程序
   4.1 XXX的策划
   4.2 XXX的实施
   4.3 XXX的检查
   4.4 XXX的改进
5. 相关文件
6. 记录表单

## 写作要求
- 程序文件是描述跨部门业务流程的文件，应体现部门间的接口关系
- 工作程序部分应按 PDCA 逻辑编写
- 明确各环节的输入、输出和责任部门
- 涉及记录表单时，列出表单名称和编号"""


# ===========================================================================
# 5. 作业指导书生成 Prompt
# ===========================================================================

def build_instruction_prompt(
    instruction_name: str,
    company_name: str,
    process_description: str,
    extracted_data: Dict[str, Any],
    department: str = "",
    doc_number: str = "",
) -> str:
    """构建作业指导书生成 Prompt

    Args:
        instruction_name: 作业指导书名称，如"XX设备操作规程"
        company_name: 企业名称
        process_description: 作业/工序描述
        extracted_data: 已提取的企业真实数据字典
        department: 所属部门
        doc_number: 文件编号

    Returns:
        完整的用户 Prompt
    """
    data_json = _format_extracted_data(extracted_data)

    return f"""请为以下企业编写作业指导书。

## 文件信息
- 企业名称：{company_name}
- 文件名称：{instruction_name}
- 所属部门：{department or "（根据企业实际确定）"}
- 作业描述：{process_description}
- 文件编号：{doc_number or ""}

## 企业真实数据（事实来源）
{data_json}

## 文档结构要求
请按以下结构编写作业指导书：

1. 目的
2. 适用范围
3. 职责
4. 作业前准备
   - 人员要求
   - 设备/工具准备
   - 环境条件
   - 物料准备
5. 作业步骤
   - 步骤一：……
   - 步骤二：……
   - （按实际操作顺序逐一列出）
6. 质量控制要点
7. 安全注意事项
8. 异常处理
9. 相关记录

## 写作要求
- 作业指导书是指导具体操作的文件，应详细、具体、可操作
- 作业步骤应按时间顺序编写，每一步都要清晰明确
- 安全注意事项必须与作业内容紧密相关
- 如涉及设备参数、工艺参数，应标注合理的参考值范围"""


# ===========================================================================
# 6. 记录表单生成 Prompt
# ===========================================================================

def build_record_form_prompt(
    form_name: str,
    company_name: str,
    form_purpose: str,
    extracted_data: Dict[str, Any],
    required_fields: Optional[List[str]] = None,
    doc_number: str = "",
) -> str:
    """构建记录表单生成 Prompt

    Args:
        form_name: 表单名称，如"内部审核检查表"
        company_name: 企业名称
        form_purpose: 表单用途描述
        extracted_data: 已提取的企业真实数据字典
        required_fields: 必填字段列表
        doc_number: 表单编号

    Returns:
        完整的用户 Prompt
    """
    fields_str = ""
    if required_fields:
        fields_str = "\n".join(f"   - {f}" for f in required_fields)
    else:
        fields_str = "   - （根据表单用途和企业实际设计合理的字段）"

    data_json = _format_extracted_data(extracted_data)

    return f"""请为以下企业设计记录表单。

## 表单信息
- 企业名称：{company_name}
- 表单名称：{form_name}
- 表单用途：{form_purpose}
- 表单编号：{doc_number or ""}

## 企业真实数据（事实来源）
{data_json}

## 必填字段要求
{fields_str}

## 表单设计要求
请按以下结构输出表单设计：

1. 表头信息
   - 表单名称、编号
   - 企业名称
   - 日期、编号等管理字段

2. 主体内容区域
   - 根据表单用途设计合理的表格结构
   - 每个字段标注字段名称和填写说明
   - 包含必要的审核、批准签字栏

3. 表尾信息
   - 编制人/日期
   - 审核人/日期
   - 批准人/日期

## 输出格式
请以 Markdown 表格形式输出表单设计，每个字段包含：
| 序号 | 字段名称 | 填写说明 | 填写方式（手写/选择/打勾） | 是否必填 |"""


# ===========================================================================
# 7. 事实约束生成 Prompt（核心）
# ===========================================================================

def build_fact_locked_prompt(
    doc_type: str,
    doc_title: str,
    extracted_data: Dict[str, Any],
    template_structure: str = "",
    additional_requirements: str = "",
) -> str:
    """构建事实约束生成 Prompt

    这是本模块的核心函数。它将已提取的企业真实数据注入到 Prompt 中，
    并通过严格的约束条件限制 AI 只负责语言组织，不编造任何事实。

    Args:
        doc_type: 文档类型，如 "质量手册"、"程序文件"、"作业指导书"、"记录表单"
        doc_title: 文档标题
        extracted_data: 已提取的企业真实数据字典（核心数据源）
        template_structure: 可选的自定义文档结构模板
        additional_requirements: 额外的写作要求

    Returns:
        完整的用户 Prompt（不含 system prompt，需配合 FACT_LOCK_SYSTEM_PROMPT 使用）
    """
    data_json = _format_extracted_data(extracted_data)

    # 根据文档类型选择默认结构
    if not template_structure:
        template_structure = _get_default_structure(doc_type)

    prompt = f"""请为 {doc_type}《{doc_title}》编写内容。

## 企业真实数据（事实来源 —— 这是唯一可引用的数据源）

以下数据已从企业提供的材料中提取，是编写本文件的唯一事实依据。
你可以对这些数据进行合理的语言组织和逻辑展开，但不得添加任何未列出的具体信息。

{data_json}

## 文档结构

{template_structure}

## 事实约束声明

- 上面「企业真实数据」区块中的所有信息均为已验证的真实数据，你可以放心引用。
- 对于数据中未提及的内容，请使用以下策略：
  (a) 使用通用、合规的行业表述（如"按规定执行""按相关标准要求"）
  (b) 使用占位描述（如"相关部门""相关人员"）而非编造具体名称
  (c) 如某条款确实缺乏数据支撑，可简要说明并给出通用建议
- 严禁行为：编造企业名称以外的公司名、虚构人名、编造设备型号、编造具体数值、编造证书编号等
"""

    if additional_requirements:
        prompt += f"""
## 额外要求
{additional_requirements}
"""

    return prompt


# ===========================================================================
# 8. 咨询顾问常用表达库
# ===========================================================================

CONSULT_EXPRESSIONS: Dict[str, List[str]] = {
    # ---- 开头类 ----
    "开头": [
        "为确保{process}的规范运行，特制定本文件。",
        "本文件依据{standard}标准要求，结合公司实际情况编制。",
        "为有效控制{process}，实现{goal}，制定本程序。",
        "本文件旨在规范{process}的管理，确保符合{standard}要求。",
        "为满足认证审核要求，对{process}进行系统化管理，特编制本文件。",
        "根据公司管理体系运行需要，为明确{process}的职责和方法，制定本文件。",
    ],

    # ---- 描述类 ----
    "描述": [
        "公司应建立、实施并保持{process}，以确保{goal}。",
        "各部门应按照本文件规定的职责和程序，有效开展{process}相关工作。",
        "公司对{process}进行策划，确定需要实现的目标及所需的资源和过程。",
        "公司通过{method}对{process}进行监视和测量，以确保其有效运行。",
        "当{process}发生变更时，公司应评审变更的后果，必要时采取措施减轻不利影响。",
        "公司保留适当的成文信息，作为{process}已按策划实施的证据。",
        "公司确定与{process}相关的内部和外部沟通需求，确保信息的及时传递。",
        "最高管理者应通过以下方式证实其对管理体系的领导作用和承诺。",
    ],

    # ---- 引用类 ----
    "引用": [
        "本文件的编制依据为{standard}标准第{clause}条款的要求。",
        "相关文件：《{related_doc}》（编号：{doc_no}）",
        "本文件引用的记录表单见附录A。",
        "本文件与《{related_doc}》相互支撑，共同构成{process}的管理框架。",
        "详见{standard}标准第{clause}条款。",
        "本文件是对{standard}标准{clause}条款的具体化和展开。",
    ],

    # ---- 过渡类 ----
    "过渡": [
        "在此基础上，",
        "为确保上述要求的有效实施，",
        "在具体执行过程中，",
        "针对上述情况，",
        "结合公司实际，",
        "经公司研究决定，",
        "根据以往运行经验，",
        "在管理体系运行中，",
        "为持续改进管理体系绩效，",
        "在满足法规要求的前提下，",
    ],

    # ---- 结尾类 ----
    "结尾": [
        "本文件由{department}负责解释。",
        "本文件自发布之日起实施，原《{old_doc}》同时废止。",
        "本文件每年评审一次，必要时进行修订。",
        "相关记录应按《记录控制程序》的要求进行管理。",
        "本文件经管理者代表审核、最高管理者批准后发布实施。",
        "各部门应严格遵照执行，如有问题及时反馈至{department}。",
        "本文件的修改需经原审批程序批准后方可生效。",
    ],
}


# ===========================================================================
# 内部辅助函数
# ===========================================================================

def _format_extracted_data(data: Dict[str, Any], indent: int = 2) -> str:
    """将提取的数据字典格式化为可读的文本块

    Args:
        data: 提取的数据字典
        indent: 缩进空格数

    Returns:
        格式化后的文本
    """
    import json

    if not data:
        return "（暂无提取数据，请使用通用合规表述）"

    lines = []
    prefix = " " * indent

    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}**{key}**：")
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, list):
                    items = "、".join(str(v) for v in sub_value)
                    lines.append(f"{prefix}  - {sub_key}：{items}")
                else:
                    lines.append(f"{prefix}  - {sub_key}：{sub_value}")
        elif isinstance(value, list):
            items = "、".join(str(v) for v in value)
            lines.append(f"{prefix}- {key}：{items}")
        else:
            lines.append(f"{prefix}- {key}：{value}")

    return "\n".join(lines)


def _get_default_structure(doc_type: str) -> str:
    """根据文档类型返回默认的结构模板

    Args:
        doc_type: 文档类型

    Returns:
        结构模板字符串
    """
    structures = {
        "质量手册": """1. 发布令
2. 企业概况
3. 管理体系范围与删减说明
4. 组织结构与职责
5. 管理体系要求（按标准条款逐条展开）
6. 附录""",

        "程序文件": FOUR_SECTION_TEMPLATE + """

### 具体章节
1. 目的
2. 范围
3. 职责
4. 工作程序（按PDCA展开）
5. 相关文件
6. 记录表单""",

        "作业指导书": """1. 目的
2. 适用范围
3. 职责
4. 作业前准备
5. 作业步骤
6. 质量控制要点
7. 安全注意事项
8. 异常处理
9. 相关记录""",

        "记录表单": """1. 表头信息（表单名称、编号、企业名称）
2. 主体内容区域（根据用途设计字段）
3. 审核批准栏
4. 表尾信息（编制/审核/批准）""",
    }

    return structures.get(doc_type, FOUR_SECTION_TEMPLATE)


# ===========================================================================
# 便捷函数：随机选择表达
# ===========================================================================

def pick_expression(category: str, **kwargs) -> str:
    """从表达库中随机选择一条表达并填充变量

    Args:
        category: 表达类别，可选值：开头、描述、引用、过渡、结尾
        **kwargs: 填充变量，如 process="文件控制", standard="ISO9001:2015"

    Returns:
        填充后的表达字符串
    """
    import random

    expressions = CONSULT_EXPRESSIONS.get(category, [])
    if not expressions:
        return ""

    template = random.choice(expressions)
    try:
        return template.format(**kwargs)
    except KeyError:
        # 缺少变量时返回原始模板
        return template


def get_all_expressions(category: Optional[str] = None) -> Dict[str, List[str]]:
    """获取表达库

    Args:
        category: 可选，指定类别。为 None 时返回全部。

    Returns:
        表达字典
    """
    if category:
        return {category: CONSULT_EXPRESSIONS.get(category, [])}
    return CONSULT_EXPRESSIONS.copy()
