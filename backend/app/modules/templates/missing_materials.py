#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 缺失材料模板系统
管理企业需要提供的材料清单和模板下载
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class MaterialCategory(Enum):
    """材料类别"""
    BUSINESS_LICENSE = "证照类"
    PERSONNEL = "人事类"
    PREMISES = "场地类"
    EQUIPMENT = "设备类"
    TRAINING = "培训类"
    CONTRACT = "合同类"
    FINANCE = "财务类"
    SAFETY = "安全类"
    ENVIRONMENT = "环境类"
    OTHER = "其他"


class MaterialStatus(Enum):
    """材料状态"""
    MISSING = "缺失"
    UPLOADED = "已上传"
    TEMPLATE_AVAILABLE = "有模板"
    NOT_REQUIRED = "不适用"


@dataclass
class MaterialTemplate:
    """材料模板"""
    template_id: str                          # 模板ID
    name: str                                 # 材料名称
    category: MaterialCategory                # 材料类别
    required: bool = True                     # 是否必需
    description: Optional[str] = None         # 描述说明
    
    # 模板文件
    template_url: Optional[str] = None        # 模板文件URL
    template_fields: List[str] = field(default_factory=list)  # 需填写的字段
    
    # 适用条件
    standards: List[str] = field(default_factory=list)        # 适用标准
    industries: List[str] = field(default_factory=list)       # 适用行业
    conditions: Optional[str] = None          # 适用条件说明
    
    # 提交要求
    format_requirements: Optional[str] = None # 格式要求
    quantity: str = "1份"                     # 需要份数
    deadline_days: Optional[int] = None       # 提交期限（天）
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "category": self.category.value,
            "required": self.required,
            "description": self.description,
            "template_url": self.template_url,
            "template_fields": self.template_fields,
            "standards": self.standards,
            "industries": self.industries,
            "format_requirements": self.format_requirements,
            "quantity": self.quantity,
        }


@dataclass
class MaterialRequirement:
    """材料需求"""
    material: MaterialTemplate                # 材料模板
    status: MaterialStatus = MaterialStatus.MISSING  # 状态
    
    # 已上传信息
    uploaded_file: Optional[str] = None       # 已上传文件路径
    uploaded_at: Optional[str] = None         # 上传时间
    uploaded_by: Optional[str] = None         # 上传人
    
    # 审核信息
    reviewed: bool = False                    # 是否已审核
    review_result: Optional[str] = None       # 审核结果
    review_comment: Optional[str] = None      # 审核意见
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.material.to_dict(),
            "status": self.status.value,
            "uploaded_file": self.uploaded_file,
            "reviewed": self.reviewed,
            "review_result": self.review_result,
        }


class MaterialTemplateRegistry:
    """材料模板注册表"""
    
    # 所有材料模板定义
    TEMPLATES: Dict[str, MaterialTemplate] = {}
    
    @classmethod
    def register(cls, template: MaterialTemplate):
        """注册材料模板"""
        cls.TEMPLATES[template.template_id] = template
    
    @classmethod
    def get(cls, template_id: str) -> Optional[MaterialTemplate]:
        """获取材料模板"""
        return cls.TEMPLATES.get(template_id)
    
    @classmethod
    def get_all(cls) -> List[MaterialTemplate]:
        """获取所有材料模板"""
        return list(cls.TEMPLATES.values())


# ==================== 注册材料模板 ====================

# === 证照类 ===
MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="business_license",
    name="营业执照",
    category=MaterialCategory.BUSINESS_LICENSE,
    required=True,
    description="需提供最新年检的营业执照副本复印件（加盖公章）",
    template_url=None,  # 企业自行提供
    format_requirements="PDF或扫描件，清晰可辨",
    quantity="1份",
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="organization_code",
    name="组织机构代码证",
    category=MaterialCategory.BUSINESS_LICENSE,
    required=False,
    description="如已三证合一则无需提供",
    template_url=None,
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="tax_registration",
    name="税务登记证",
    category=MaterialCategory.BUSINESS_LICENSE,
    required=False,
    description="如已三证合一则无需提供",
    template_url=None,
))

# === 人事类 ===
MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="employee_roster",
    name="员工花名册",
    category=MaterialCategory.PERSONNEL,
    required=True,
    description="包含员工姓名、部门、岗位、入职日期等信息",
    template_url="/templates/forms/employee_roster_template.xlsx",
    template_fields=["序号", "姓名", "性别", "身份证号", "部门", "岗位", "入职日期", "联系电话"],
    format_requirements="Excel格式",
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="labor_contract",
    name="劳动合同",
    category=MaterialCategory.PERSONNEL,
    required=True,
    description="需提供所有员工的劳动合同（抽样检查）",
    template_url="/templates/forms/labor_contract_template.docx",
    template_fields=["甲方（用人单位）", "乙方（劳动者）", "合同期限", "工作岗位", "工作地点", "劳动报酬", "工作时间"],
    quantity="全员覆盖",
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="social_insurance",
    name="社保缴纳证明",
    category=MaterialCategory.PERSONNEL,
    required=True,
    description="近3个月的社保缴纳凭证，需包含员工名单",
    template_url=None,  # 社保局出具
    format_requirements="社保局出具的原件或电子凭证",
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="health_examination",
    name="员工体检报告",
    category=MaterialCategory.PERSONNEL,
    required=True,
    description="从事有职业危害作业的员工需提供职业健康体检报告",
    template_url=None,
    standards=["ISO45001"],
    conditions="涉及职业危害岗位",
))

# === 场地类 ===
MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="lease_contract",
    name="办公场所租赁合同",
    category=MaterialCategory.PREMISES,
    required=True,
    description="办公/生产场所的租赁合同或产权证明",
    template_url="/templates/forms/lease_contract_template.docx",
    template_fields=["出租方", "承租方", "租赁地址", "租赁面积", "租赁期限", "租金"],
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="property_certificate",
    name="房产证/产权证明",
    category=MaterialCategory.PREMISES,
    required=False,
    description="自有房产需提供房产证复印件",
    template_url=None,
    conditions="自有房产",
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="fire_safety_certificate",
    name="消防验收合格证",
    category=MaterialCategory.PREMISES,
    required=True,
    description="办公/生产场所的消防验收合格证明",
    template_url=None,
    standards=["ISO45001"],
))

# === 设备类 ===
MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="equipment_list",
    name="设备清单",
    category=MaterialCategory.EQUIPMENT,
    required=True,
    description="主要设备清单，包含设备名称、型号、数量、状态等",
    template_url="/templates/forms/equipment_list_template.xlsx",
    template_fields=["序号", "设备名称", "型号规格", "数量", "购置日期", "状态", "保管人"],
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="special_equipment_license",
    name="特种设备使用登记证",
    category=MaterialCategory.EQUIPMENT,
    required=False,
    description="特种设备（电梯、压力容器等）的使用登记证",
    template_url=None,
    conditions="有特种设备时需要",
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="equipment_maintenance_record",
    name="设备维护保养记录",
    category=MaterialCategory.EQUIPMENT,
    required=True,
    description="主要设备的维护保养记录",
    template_url="/templates/forms/equipment_maintenance_record.xlsx",
    template_fields=["设备名称", "维护日期", "维护内容", "维护人员", "验收人员"],
))

# === 培训类 ===
MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="training_plan",
    name="年度培训计划",
    category=MaterialCategory.TRAINING,
    required=True,
    description="年度培训计划，包含培训内容、时间、对象等",
    template_url="/templates/forms/training_plan_template.docx",
    template_fields=["培训主题", "培训对象", "培训时间", "培训方式", "考核方式"],
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="training_record",
    name="培训记录表",
    category=MaterialCategory.TRAINING,
    required=True,
    description="培训实施记录，包含签到表、考核结果等",
    template_url="/templates/forms/training_record_template.docx",
    template_fields=["培训主题", "培训日期", "讲师", "参训人员签到", "考核结果"],
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="safety_training_record",
    name="安全培训记录",
    category=MaterialCategory.TRAINING,
    required=True,
    description="安全生产相关培训记录",
    template_url="/templates/forms/safety_training_record_template.docx",
    template_fields=["培训主题", "培训日期", "讲师", "参训人员", "考核结果"],
    standards=["ISO45001"],
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="special_work_certificate",
    name="特种作业人员证书",
    category=MaterialCategory.TRAINING,
    required=False,
    description="电工、焊工、叉车工等特种作业人员的操作证书",
    template_url=None,
    conditions="有特种作业人员时需要",
))

# === 合同类 ===
MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="sales_contract_sample",
    name="销售合同样本",
    category=MaterialCategory.CONTRACT,
    required=True,
    description="销售/服务合同样本（脱敏处理）",
    template_url=None,
    standards=["ISO9001"],
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="purchase_contract_sample",
    name="采购合同样本",
    category=MaterialCategory.CONTRACT,
    required=True,
    description="采购合同样本（脱敏处理）",
    template_url=None,
    standards=["ISO9001"],
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="supplier_evaluation",
    name="供应商评价记录",
    category=MaterialCategory.CONTRACT,
    required=True,
    description="供应商选择、评价和重新评价记录",
    template_url="/templates/forms/supplier_evaluation_template.xlsx",
    template_fields=["供应商名称", "评价项目", "评价结果", "评价日期", "评价人"],
    standards=["ISO9001"],
))

# === 安全类 ===
MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="safety_inspection_record",
    name="安全检查记录",
    category=MaterialCategory.SAFETY,
    required=True,
    description="定期安全检查记录",
    template_url="/templates/forms/safety_inspection_record.xlsx",
    template_fields=["检查日期", "检查区域", "发现问题", "整改措施", "整改期限", "复查结果"],
    standards=["ISO45001"],
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="emergency_drill_record",
    name="应急演练记录",
    category=MaterialCategory.SAFETY,
    required=True,
    description="消防、安全等应急演练记录",
    template_url="/templates/forms/emergency_drill_record.docx",
    template_fields=["演练主题", "演练日期", "参演人员", "演练过程", "演练总结"],
    standards=["ISO45001", "ISO14001"],
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="accident_record",
    name="事故/事件记录",
    category=MaterialCategory.SAFETY,
    required=False,
    description="安全事故/事件的发生和处理记录",
    template_url="/templates/forms/accident_record_template.docx",
    template_fields=["发生时间", "发生地点", "事故类型", "伤亡情况", "原因分析", "处理措施"],
    standards=["ISO45001"],
))

# === 环境类 ===
MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="environmental_impact_assessment",
    name="环境影响评价报告",
    category=MaterialCategory.ENVIRONMENT,
    required=False,
    description="建设项目的环境影响评价报告",
    template_url=None,
    standards=["ISO14001"],
    conditions="特定行业需要",
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="pollutant_discharge_permit",
    name="排污许可证",
    category=MaterialCategory.ENVIRONMENT,
    required=False,
    description="污染物排放许可证",
    template_url=None,
    standards=["ISO14001"],
    conditions="有污染物排放时需要",
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="waste_disposal_contract",
    name="危废处置合同",
    category=MaterialCategory.ENVIRONMENT,
    required=False,
    description="危险废物处置合同和转移联单",
    template_url=None,
    standards=["ISO14001"],
    conditions="产生危险废物时需要",
))

MaterialTemplateRegistry.register(MaterialTemplate(
    template_id="environmental_monitoring_report",
    name="环境监测报告",
    category=MaterialCategory.ENVIRONMENT,
    required=False,
    description="废水、废气、噪声等监测报告",
    template_url=None,
    standards=["ISO14001"],
))


class MissingMaterialAnalyzer:
    """缺失材料分析器"""
    
    def __init__(self):
        self.registry = MaterialTemplateRegistry
    
    def analyze(
        self,
        standards: List[str],
        industry: Optional[str] = None,
        company_info: Optional[Dict[str, Any]] = None,
        existing_materials: Optional[List[str]] = None
    ) -> List[MaterialRequirement]:
        """
        分析缺失材料
        
        Args:
            standards: 目标标准列表
            industry: 行业类型
            company_info: 企业信息
            existing_materials: 已有材料ID列表
        
        Returns:
            材料需求列表
        """
        requirements = []
        existing = set(existing_materials or [])
        
        for template_id, template in self.registry.TEMPLATES.items():
            # 检查是否适用
            if not self._is_applicable(template, standards, industry, company_info):
                continue
            
            # 确定状态
            if template_id in existing:
                status = MaterialStatus.UPLOADED
            elif template.template_url:
                status = MaterialStatus.TEMPLATE_AVAILABLE
            else:
                status = MaterialStatus.MISSING
            
            requirements.append(MaterialRequirement(
                material=template,
                status=status,
            ))
        
        return requirements
    
    def _is_applicable(
        self,
        template: MaterialTemplate,
        standards: List[str],
        industry: Optional[str],
        company_info: Optional[Dict[str, Any]]
    ) -> bool:
        """检查材料是否适用"""
        # 检查标准适用性
        if template.standards:
            if not any(std in standards for std in template.standards):
                return False
        
        # 检查行业适用性
        if template.industries:
            if industry not in template.industries:
                return False
        
        return True
    
    def get_missing_materials(
        self,
        standards: List[str],
        industry: Optional[str] = None,
        company_info: Optional[Dict[str, Any]] = None,
        existing_materials: Optional[List[str]] = None
    ) -> List[MaterialRequirement]:
        """获取缺失材料列表"""
        all_requirements = self.analyze(standards, industry, company_info, existing_materials)
        
        return [
            r for r in all_requirements
            if r.status in [MaterialStatus.MISSING, MaterialStatus.TEMPLATE_AVAILABLE]
               and r.material.required
        ]
    
    def get_downloadable_templates(
        self,
        standards: List[str],
        industry: Optional[str] = None
    ) -> List[MaterialTemplate]:
        """获取可下载的模板列表"""
        templates = []
        
        for template in self.registry.get_all():
            if not template.template_url:
                continue
            
            # 检查适用性
            if template.standards:
                if not any(std in standards for std in template.standards):
                    continue
            
            if template.industries:
                if industry not in template.industries:
                    continue
            
            templates.append(template)
        
        return templates
    
    def get_summary(
        self,
        standards: List[str],
        industry: Optional[str] = None,
        existing_materials: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取材料摘要"""
        requirements = self.analyze(standards, industry, None, existing_materials)
        
        summary = {
            "total": len(requirements),
            "required": sum(1 for r in requirements if r.material.required),
            "uploaded": sum(1 for r in requirements if r.status == MaterialStatus.UPLOADED),
            "missing": sum(1 for r in requirements if r.status == MaterialStatus.MISSING and r.material.required),
            "template_available": sum(1 for r in requirements if r.status == MaterialStatus.TEMPLATE_AVAILABLE),
            "by_category": {},
        }
        
        for req in requirements:
            category = req.material.category.value
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        
        return summary


# 便捷函数
def get_required_materials(
    standards: List[str],
    industry: Optional[str] = None,
    existing_materials: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """获取所需材料列表的便捷函数"""
    analyzer = MissingMaterialAnalyzer()
    requirements = analyzer.get_missing_materials(standards, industry, None, existing_materials)
    return [r.to_dict() for r in requirements]


# 测试代码
if __name__ == "__main__":
    # 测试缺失材料分析
    analyzer = MissingMaterialAnalyzer()
    
    standards = ["ISO9001", "ISO14001", "ISO45001"]
    industry = "物业"
    
    # 获取材料清单
    requirements = analyzer.analyze(standards, industry)
    
    print("=" * 60)
    print(f"材料清单（{len(requirements)}项）")
    print("=" * 60)
    
    for req in requirements:
        status_icon = "✓" if req.status == MaterialStatus.UPLOADED else "✗"
        template_icon = "📄" if req.material.template_url else ""
        print(f"[{status_icon}] {req.material.name} ({req.material.category.value}) {template_icon}")
    
    # 获取摘要
    summary = analyzer.get_summary(standards, industry)
    
    print("\n" + "=" * 60)
    print("统计摘要")
    print("=" * 60)
    print(f"总数: {summary['total']}")
    print(f"必需: {summary['required']}")
    print(f"已上传: {summary['uploaded']}")
    print(f"缺失: {summary['missing']}")
    print(f"有模板: {summary['template_available']}")
    print(f"按类别: {summary['by_category']}")
