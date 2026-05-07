#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业必需文件清单

根据QES认证审核要求，企业需要提供以下文件：
1. 企业基础证照
2. 人员管理文件
3. 场所管理文件
4. 合同管理文件
5. 设备管理文件
6. 认证申请文件

当企业缺少某些文件时，系统可以自动生成相应的模板。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict
from ..base import GeneratedDocument, FileLevel, DocumentType


class RequiredDocCategory(Enum):
    """必需文件类别"""
    LICENSE = "license"  # 证照类
    PERSONNEL = "personnel"  # 人员管理类
    PREMISES = "premises"  # 场所管理类
    CONTRACT = "contract"  # 合同管理类
    EQUIPMENT = "equipment"  # 设备管理类
    CERTIFICATION = "certification"  # 认证申请类


class RequiredDocStatus(Enum):
    """文件状态"""
    PROVIDED = "provided"  # 已提供
    MISSING = "missing"  # 缺失
    GENERATED = "generated"  # 已生成模板
    NOT_APPLICABLE = "not_applicable"  # 不适用


@dataclass
class RequiredDocument:
    """必需文件定义"""
    name: str  # 文件名称
    code: str  # 文件编号
    category: RequiredDocCategory  # 所属类别
    description: str  # 说明
    required: bool  # 是否必须提供
    template_available: bool  # 是否有模板
    file_format: str = "docx"  # 文件格式
    related_standard: str = ""  # 关联标准条款
    remarks: str = ""  # 备注


@dataclass
class RequiredDocCheckResult:
    """文件检查结果"""
    document: RequiredDocument
    status: RequiredDocStatus
    file_path: Optional[str] = None  # 企业提供的文件路径
    generated_path: Optional[str] = None  # 系统生成的模板路径
    remarks: str = ""  # 备注


# ============================================================
# 企业必需文件清单定义
# ============================================================

REQUIRED_DOCUMENTS = [
    # ========== 证照类 ==========
    RequiredDocument(
        name="营业执照",
        code="LICENSE-001",
        category=RequiredDocCategory.LICENSE,
        description="企业法人营业执照副本",
        required=True,
        template_available=False,
        file_format="jpg/png",
        related_standard="ISO9001 7.1.2",
        remarks="需加盖公章"
    ),
    RequiredDocument(
        name="公司章程",
        code="LICENSE-002",
        category=RequiredDocCategory.LICENSE,
        description="企业公司章程",
        required=True,
        template_available=True,
        file_format="docx",
        related_standard="ISO9001 5.3",
        remarks="需加盖公章"
    ),
    RequiredDocument(
        name="信用查询报告",
        code="LICENSE-003",
        category=RequiredDocCategory.LICENSE,
        description="企业信用查询报告",
        required=True,
        template_available=False,
        file_format="pdf",
        related_standard="ISO9001 4.2",
        remarks="可在信用中国网站查询"
    ),
    
    # ========== 人员管理类 ==========
    RequiredDocument(
        name="员工花名册",
        code="PERSONNEL-001",
        category=RequiredDocCategory.PERSONNEL,
        description="全体员工基本信息清单",
        required=True,
        template_available=True,
        file_format="xlsx",
        related_standard="ISO9001 7.2",
        remarks="包含姓名、部门、职位、入职日期等"
    ),
    RequiredDocument(
        name="劳动合同",
        code="PERSONNEL-002",
        category=RequiredDocCategory.PERSONNEL,
        description="员工劳动合同（含保密条款）",
        required=True,
        template_available=True,
        file_format="docx",
        related_standard="ISO9001 7.2",
        remarks="涉密岗位需包含保密协议"
    ),
    RequiredDocument(
        name="员工保密协议",
        code="PERSONNEL-003",
        category=RequiredDocCategory.PERSONNEL,
        description="涉密岗位人员保密承诺书",
        required=True,
        template_available=True,
        file_format="docx",
        related_standard="ISO9001 7.3",
        remarks="涉密岗位必须签署"
    ),
    RequiredDocument(
        name="人员资质证书",
        code="PERSONNEL-004",
        category=RequiredDocCategory.PERSONNEL,
        description="员工职业资格证书汇总",
        required=True,
        template_available=True,
        file_format="xlsx",
        related_standard="ISO9001 7.2",
        remarks="包含证书名称、证书编号、发证日期等"
    ),
    RequiredDocument(
        name="社保缴费证明",
        code="PERSONNEL-005",
        category=RequiredDocCategory.PERSONNEL,
        description="近3个月社会保险参保证明",
        required=True,
        template_available=False,
        file_format="pdf",
        related_standard="ISO9001 7.1.2",
        remarks="需从社保局获取"
    ),
    RequiredDocument(
        name="员工体检报告",
        code="PERSONNEL-006",
        category=RequiredDocCategory.PERSONNEL,
        description="涉密岗位人员职业健康体检报告",
        required=True,
        template_available=False,
        file_format="pdf",
        related_standard="ISO45001 6.1.2",
        remarks="需在指定体检机构进行"
    ),
    RequiredDocument(
        name="年度培训计划",
        code="PERSONNEL-007",
        category=RequiredDocCategory.PERSONNEL,
        description="年度培训计划表",
        required=True,
        template_available=True,
        file_format="docx",
        related_standard="ISO9001 7.2",
        remarks="系统可直接生成"
    ),
    RequiredDocument(
        name="培训记录",
        code="PERSONNEL-008",
        category=RequiredDocCategory.PERSONNEL,
        description="培训签到表和培训记录",
        required=True,
        template_available=True,
        file_format="docx",
        related_standard="ISO9001 7.2",
        remarks="每次培训后需归档"
    ),
    
    # ========== 场所管理类 ==========
    RequiredDocument(
        name="办公场所租赁合同",
        code="PREMISES-001",
        category=RequiredDocCategory.PREMISES,
        description="办公场所租赁合同",
        required=True,
        template_available=True,
        file_format="pdf",
        related_standard="ISO9001 7.1.3",
        remarks="需加盖租赁双方公章"
    ),
    RequiredDocument(
        name="场所平面图",
        code="PREMISES-002",
        category=RequiredDocCategory.PREMISES,
        description="保密场所平面图",
        required=True,
        template_available=True,
        file_format="pdf/visio",
        related_standard="ISO14001 7.1 / ISO45001 7.1",
        remarks="需标注保密区域划分"
    ),
    RequiredDocument(
        name="消防验收证明",
        code="PREMISES-003",
        category=RequiredDocCategory.PREMISES,
        description="消防验收合格证明",
        required=True,
        template_available=False,
        file_format="pdf",
        related_standard="ISO45001 8.1",
        remarks="需从消防部门获取"
    ),
    RequiredDocument(
        name="场所安全检查记录",
        code="PREMISES-004",
        category=RequiredDocCategory.PREMISES,
        description="办公场所安全检查记录",
        required=True,
        template_available=True,
        file_format="docx",
        related_standard="ISO45001 9.1.1",
        remarks="系统可直接生成"
    ),
    
    # ========== 合同管理类 ==========
    RequiredDocument(
        name="销售合同",
        code="CONTRACT-001",
        category=RequiredDocCategory.CONTRACT,
        description="近半年销售合同（不少于3份）",
        required=True,
        template_available=True,
        file_format="pdf",
        related_standard="ISO9001 8.2",
        remarks="需包含保密条款"
    ),
    RequiredDocument(
        name="采购合同",
        code="CONTRACT-002",
        category=RequiredDocCategory.CONTRACT,
        description="近半年采购合同（不少于2份）",
        required=True,
        template_available=True,
        file_format="pdf",
        related_standard="ISO9001 8.4",
        remarks="需包含保密条款"
    ),
    RequiredDocument(
        name="供应商评审记录",
        code="CONTRACT-003",
        category=RequiredDocCategory.CONTRACT,
        description="合格供应商评审记录",
        required=True,
        template_available=True,
        file_format="docx",
        related_standard="ISO9001 8.4",
        remarks="系统可直接生成"
    ),
    RequiredDocument(
        name="顾客满意度调查",
        code="CONTRACT-004",
        category=RequiredDocCategory.CONTRACT,
        description="顾客满意度调查表和统计表",
        required=True,
        template_available=True,
        file_format="docx",
        related_standard="ISO9001 9.1.2",
        remarks="系统可直接生成"
    ),
    
    # ========== 设备管理类 ==========
    RequiredDocument(
        name="设备设施清单",
        code="EQUIPMENT-001",
        category=RequiredDocCategory.EQUIPMENT,
        description="用于业务的设备和设施清单",
        required=True,
        template_available=True,
        file_format="xlsx",
        related_standard="ISO9001 7.1.3",
        remarks="系统可直接生成"
    ),
    RequiredDocument(
        name="设备维保记录",
        code="EQUIPMENT-002",
        category=RequiredDocCategory.EQUIPMENT,
        description="设备维护保养记录",
        required=True,
        template_available=True,
        file_format="docx",
        related_standard="ISO9001 7.1.3",
        remarks="系统可直接生成"
    ),
    RequiredDocument(
        name="计量器具检定证书",
        code="EQUIPMENT-003",
        category=RequiredDocCategory.EQUIPMENT,
        description="计量器具周期检定证书",
        required=True,
        template_available=False,
        file_format="pdf",
        related_standard="ISO9001 7.1.5",
        remarks="需从计量检定机构获取"
    ),
    
    # ========== 认证申请类 ==========
    RequiredDocument(
        name="认证申请书",
        code="CERT-001",
        category=RequiredDocCategory.CERTIFICATION,
        description="QES认证申请书",
        required=True,
        template_available=True,
        file_format="docx",
        related_standard="ISO9001 4.1",
        remarks="系统可直接生成"
    ),
    RequiredDocument(
        name="认证合同",
        code="CERT-002",
        category=RequiredDocCategory.CERTIFICATION,
        description="与认证机构签订的认证合同",
        required=True,
        template_available=False,
        file_format="pdf",
        related_standard="",
        remarks="需与认证机构签订"
    ),
    RequiredDocument(
        name="管理体系运行情况",
        code="CERT-003",
        category=RequiredDocCategory.CERTIFICATION,
        description="质量/环境/职业健康安全管理体系运行情况说明",
        required=True,
        template_available=True,
        file_format="docx",
        related_standard="ISO9001 4.1",
        remarks="系统可直接生成"
    ),
]


class RequiredDocChecker:
    """必需文件检查器"""
    
    def __init__(self):
        self.documents = REQUIRED_DOCUMENTS
    
    def get_documents_by_category(self, category: RequiredDocCategory) -> List[RequiredDocument]:
        """按类别获取文件清单"""
        return [doc for doc in self.documents if doc.category == category]
    
    def get_required_only(self) -> List[RequiredDocument]:
        """获取必须提供的文件"""
        return [doc for doc in self.documents if doc.required]
    
    def get_with_template(self) -> List[RequiredDocument]:
        """获取有模板的文件"""
        return [doc for doc in self.documents if doc.template_available]
    
    def check_documents(
        self,
        provided_files: Dict[str, str]
    ) -> List[RequiredDocCheckResult]:
        """
        检查文件提供情况
        
        Args:
            provided_files: 企业已提供的文件，格式 {文件编号: 文件路径}
            
        Returns:
            检查结果列表
        """
        results = []
        
        for doc in self.documents:
            if doc.code in provided_files:
                # 文件已提供
                result = RequiredDocCheckResult(
                    document=doc,
                    status=RequiredDocStatus.PROVIDED,
                    file_path=provided_files[doc.code],
                )
            elif doc.template_available:
                # 缺失但有模板
                result = RequiredDocCheckResult(
                    document=doc,
                    status=RequiredDocStatus.MISSING,
                    remarks="企业未提供，系统可生成模板",
                )
            else:
                # 缺失且无模板
                result = RequiredDocCheckResult(
                    document=doc,
                    status=RequiredDocStatus.MISSING,
                    remarks="企业需自行准备或从相关机构获取",
                )
            
            results.append(result)
        
        return results
    
    def get_missing_summary(self, results: List[RequiredDocCheckResult]) -> Dict[str, any]:
        """获取缺失文件汇总"""
        missing = [r for r in results if r.status == RequiredDocStatus.MISSING]
        with_template = [r for r in missing if r.document.template_available]
        without_template = [r for r in missing if not r.document.template_available]
        
        return {
            "total": len(self.documents),
            "provided": len([r for r in results if r.status == RequiredDocStatus.PROVIDED]),
            "missing": len(missing),
            "missing_with_template": len(with_template),
            "missing_without_template": len(without_template),
            "missing_documents": [r.document.name for r in missing],
            "documents_with_template": [r.document.name for r in with_template],
            "documents_without_template": [r.document.name for r in without_template],
        }


# ============================================================
# 模板生成器
# ============================================================

class RequiredDocTemplateGenerator:
    """必需文件模板生成器"""
    
    TEMPLATE_TEMPLATES = {
        # 人员管理类
        "PERSONNEL-001": """# 员工花名册

| 序号 | 姓名 | 性别 | 出生日期 | 部门 | 职位 | 入职日期 | 证件类型 | 证件号码 | 备注 |
|------|------|------|----------|------|------|----------|----------|----------|------|
| 1 | | | | | | | | | |
| 2 | | | | | | | | | |

编制：                审核：                批准：
日期：                日期：                日期：
""",
        "PERSONNEL-002": """# 劳动合同

甲方（用人单位）：{{公司名称}}
乙方（劳动者）：________________

根据《中华人民共和国劳动法》等相关法律法规，甲乙双方经平等协商，签订本合同。

## 一、合同期限
本合同期限为____年，自____年____月____日起至____年____月____日止。

## 二、工作内容
乙方同意在甲方______部门担任______工作。

## 三、劳动报酬
甲方按月支付乙方工资，每月____元。

## 四、工作时间和休息休假
按照国家规定执行。

## 五、社会保险
甲方按照规定为乙方缴纳社会保险。

## 六、保密条款
1. 乙方在工作期间及离职后____年内，对在工作过程中知悉的甲方商业秘密负有保密义务。
2. 未经甲方书面同意，乙方不得向任何第三方披露甲方商业秘密。
3. 乙方违反保密义务，给甲方造成损失的，应当承担赔偿责任。

## 七、合同变更、解除和终止
按照国家法律规定执行。

## 八、争议解决
本合同履行过程中发生的争议，协商不成的，向劳动争议仲裁委员会申请仲裁。

## 九、其他
本合同一式两份，甲乙双方各执一份。

甲方（盖章）：                乙方（签名）：
日期：                        日期：
""",
        "PERSONNEL-003": """# 员工保密协议

甲方：{{公司名称}}
乙方：________________ 身份证号码：________________

鉴于乙方在甲方任职期间将接触、知悉甲方商业秘密，为保护甲方的合法权益，双方经协商一致，签订本协议。

## 一、保密信息范围
乙方承诺对以下信息承担保密义务：
1. 技术信息：技术方案、设计图纸、工艺流程等
2. 经营信息：客户资料、合同文件、财务数据等
3. 管理信息：内部管理制度、人事信息等
4. 其他甲方标明为保密的信息

## 二、保密义务
1. 乙方应当严格保守甲方的保密信息，不得向任何第三方披露。
2. 乙方不得利用甲方的保密信息为自己或第三方谋取利益。
3. 乙方不得复制、摘录或转移甲方的保密信息。

## 三、保密期限
本协议项下的保密义务在乙方离职后____年内仍然有效。

## 四、违约责任
乙方违反本协议约定的，应当向甲方支付违约金____元，并赔偿甲方因此遭受的全部损失。

## 五、其他
本协议自双方签字（盖章）之日起生效。

甲方（盖章）：                乙方（签名）：
日期：                        日期：
""",
        "PERSONNEL-007": """# 年度培训计划

编制部门：综合管理部    年度：{{年份}}

| 序号 | 培训项目 | 培训内容 | 培训对象 | 培训方式 | 计划时间 | 培训教师 | 预算费用 | 备注 |
|------|----------|----------|----------|----------|----------|----------|----------|------|
| 1 | 三体系标准培训 | ISO9001/14001/45001标准解析 | 管理人员 | 内部培训 | 第一季度 | | | |
| 2 | 安全风险辨识 | 危险源识别和风险评价 | 全体员工 | 内部培训 | 第一季度 | | | |
| 3 | 档案管理培训 | 档案整理和数字化规范 | 相关人员 | 内部培训 | 第二季度 | | | |
| 4 | 节能降耗培训 | 能源节约和环境保护 | 管理人员 | 内部培训 | 第二季度 | | | |
| 5 | 服务技能培训 | 客户服务规范和技能 | 客服人员 | 内部培训 | 第三季度 | | | |
| 6 | 法律法规培训 | 适用法规更新培训 | 管理人员 | 外部培训 | 第四季度 | | | |

编制：                审核：                批准：
日期：                日期：                日期：
""",
        
        # 场所管理类
        "PREMISES-001": """# 办公场所租赁合同

出租方（甲方）：________________
承租方（乙方）：{{公司名称}}

根据《中华人民共和国民法典》等相关法律法规，甲乙双方经协商一致，就乙方向甲方租赁办公场所事宜签订本合同。

## 一、租赁标的
甲方将位于________________的房屋出租给乙方使用，建筑面积约______平方米。

## 二、租赁用途
乙方租赁该房屋仅作为________________使用。

## 三、租赁期限
租赁期限为____年，自____年____月____日起至____年____月____日止。

## 四、租金及支付方式
1. 租金：每月人民币____元（大写：____________）。
2. 支付方式：每____月支付一次，提前____日支付。

## 五、押金
乙方在签订本合同之日向甲方支付押金人民币____元。

## 六、双方权利义务
（详见合同正文）

## 七、合同变更和解除
（详见合同正文）

## 八、违约责任
（详见合同正文）

## 九、其他
本合同一式两份，甲乙双方各执一份。

甲方（盖章）：                乙方（盖章）：
法定代表人：                法定代表人：
日期：                        日期：
""",
        
        # 认证申请类
        "CERT-001": """# QES认证申请书

申请单位：{{公司名称}}

## 一、基本信息

| 项目 | 内容 |
|------|------|
| 单位名称 | {{公司名称}} |
| 法定代表人 | {{法定代表人}} |
| 联系人 | {{联系人}} |
| 联系电话 | {{联系电话}} |
| 单位地址 | {{地址}} |
| 企业类型 | |
| 注册资本 | |
| 成立日期 | |
| 职工人数 | {{员工人数}}人 |

## 二、申请认证范围

{{公司名称}}的质量、环境、职业健康安全管理体系

适用范围：{{行业}}服务

## 三、质量管理体系情况

{{公司名称}}依据ISO 9001:2015《质量管理体系 要求》建立了质量管理体系，于____年____月____日发布实施。

体系覆盖范围：{{行业}}相关的所有活动。

## 四、环境管理体系情况

{{公司名称}}依据ISO 14001:2018《环境管理体系 要求及使用指南》建立了环境管理体系，于____年____月____日发布实施。

## 五、职业健康安全管理体系情况

{{公司名称}}依据ISO 45001:2018《职业健康安全管理体系 要求》建立了职业健康安全管理体系，于____年____月____日发布实施。

## 六、附件

1. 营业执照复印件
2. 管理体系文件清单
3. 近一年运行记录（部分）
4. 其他相关材料

申请人：________________
日期：________________

（单位盖章）
""",
    }
    
    def generate_template(self, doc_code: str, company_info) -> Optional[GeneratedDocument]:
        """
        生成指定文件的模板
        
        Args:
            doc_code: 文件编号
            company_info: 企业信息
            
        Returns:
            生成的模板文档
        """
        if doc_code not in self.TEMPLATE_TEMPLATES:
            return None
        
        template_content = self.TEMPLATE_TEMPLATES[doc_code]
        
        # 替换变量
        from ..base import TemplateEngine
        engine = TemplateEngine()
        content = engine.render(template_content, company_info)
        
        # 查找文档定义
        doc_def = None
        for doc in REQUIRED_DOCUMENTS:
            if doc.code == doc_code:
                doc_def = doc
                break
        
        if not doc_def:
            return None
        
        return GeneratedDocument(
            file_level=FileLevel.LEVEL_4,
            document_type=DocumentType.FORM,
            file_code=doc_code,
            file_name=f"{doc_def.name}.docx",
            title=doc_def.name,
            content=content,
        )
    
    def generate_all_templates(self, company_info) -> List[GeneratedDocument]:
        """生成所有可用模板"""
        documents = []
        
        for doc_code in self.TEMPLATE_TEMPLATES.keys():
            doc = self.generate_template(doc_code, company_info)
            if doc:
                documents.append(doc)
        
        return documents
