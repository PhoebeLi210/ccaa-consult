#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 扩展数据模型
完整的企业信息、组织架构、业务流程等数据结构
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class IndustryType(Enum):
    """行业类型"""
    MANUFACTURING = "制造业"
    CONSTRUCTION = "建筑业"
    SERVICE = "服务业"
    TRADE = "贸易"
    IT = "IT"
    MEDICAL = "医疗"
    PROPERTY = "物业"
    EDUCATION = "教育"
    LOGISTICS = "物流"
    FINANCE = "金融"
    CATERING = "餐饮"
    RETAIL = "零售"
    OTHER = "其他"


class CertificationType(Enum):
    """认证类型"""
    INITIAL = "初次认证"
    SURVEILLANCE = "监督审核"
    RE_CERTIFICATION = "再认证"
    TRANSFER = "转机构"


class StandardType(Enum):
    """标准类型"""
    ISO9001 = "ISO9001"
    ISO14001 = "ISO14001"
    ISO45001 = "ISO45001"


@dataclass
class ContactInfo:
    """联系信息"""
    contact_person: Optional[str] = None      # 联系人
    contact_phone: Optional[str] = None       # 联系电话
    contact_mobile: Optional[str] = None      # 手机号码
    email: Optional[str] = None               # 电子邮箱
    fax: Optional[str] = None                 # 传真
    website: Optional[str] = None             # 网址


@dataclass
class Address:
    """地址信息"""
    province: Optional[str] = None            # 省份
    city: Optional[str] = None                # 城市
    district: Optional[str] = None            # 区县
    street: Optional[str] = None              # 街道地址
    postal_code: Optional[str] = None         # 邮编
    full_address: Optional[str] = None        # 完整地址
    
    def __str__(self) -> str:
        if self.full_address:
            return self.full_address
        parts = [self.province, self.city, self.district, self.street]
        return "".join(p for p in parts if p)


@dataclass
class Department:
    """部门信息"""
    dept_id: Optional[str] = None             # 部门ID
    name: str                                 # 部门名称
    parent_dept: Optional[str] = None         # 上级部门
    manager: Optional[str] = None             # 部门负责人
    employee_count: Optional[int] = None      # 员工人数
    responsibilities: List[str] = field(default_factory=list)  # 主要职责
    phone: Optional[str] = None               # 部门电话
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dept_id": self.dept_id,
            "name": self.name,
            "parent_dept": self.parent_dept,
            "manager": self.manager,
            "employee_count": self.employee_count,
            "responsibilities": self.responsibilities,
            "phone": self.phone,
        }


@dataclass
class Position:
    """岗位信息"""
    position_id: Optional[str] = None         # 岗位ID
    title: str                                # 岗位名称
    department: Optional[str] = None          # 所属部门
    reports_to: Optional[str] = None          # 汇报对象
    employee_name: Optional[str] = None       # 在职人员
    
    # 职责
    responsibilities: List[str] = field(default_factory=list)  # 主要职责
    authorities: List[str] = field(default_factory=list)       # 权限
    
    # 任职资格
    education: Optional[str] = None           # 学历要求
    experience: Optional[str] = None          # 经验要求
    certificates: List[str] = field(default_factory=list)      # 所需证书
    skills: List[str] = field(default_factory=list)            # 技能要求
    
    # 考核指标
    kpi: List[str] = field(default_factory=list)              # 关键绩效指标
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "position_id": self.position_id,
            "title": self.title,
            "department": self.department,
            "reports_to": self.reports_to,
            "employee_name": self.employee_name,
            "responsibilities": self.responsibilities,
            "authorities": self.authorities,
            "education": self.education,
            "experience": self.experience,
            "certificates": self.certificates,
            "skills": self.skills,
            "kpi": self.kpi,
        }


@dataclass
class Employee:
    """员工信息"""
    employee_id: Optional[str] = None         # 员工编号
    name: str                                 # 姓名
    gender: Optional[str] = None              # 性别
    birth_date: Optional[date] = None         # 出生日期
    id_card: Optional[str] = None             # 身份证号
    education: Optional[str] = None           # 学历
    major: Optional[str] = None               # 专业
    
    # 工作信息
    department: Optional[str] = None          # 部门
    position: Optional[str] = None            # 岗位
    hire_date: Optional[date] = None          # 入职日期
    employment_type: Optional[str] = None     # 用工类型（全职/兼职/劳务派遣）
    
    # 联系方式
    phone: Optional[str] = None               # 电话
    email: Optional[str] = None               # 邮箱
    emergency_contact: Optional[str] = None   # 紧急联系人
    emergency_phone: Optional[str] = None     # 紧急联系电话
    
    # 资质证书
    certificates: List[Dict[str, Any]] = field(default_factory=list)  # 证书列表
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "gender": self.gender,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "department": self.department,
            "position": self.position,
            "hire_date": self.hire_date.isoformat() if self.hire_date else None,
            "phone": self.phone,
            "certificates": self.certificates,
        }


@dataclass
class Equipment:
    """设备信息"""
    equipment_id: Optional[str] = None        # 设备编号
    name: str                                 # 设备名称
    model: Optional[str] = None               # 型号规格
    manufacturer: Optional[str] = None        # 制造商
    purchase_date: Optional[date] = None      # 购置日期
    quantity: int = 1                         # 数量
    
    # 状态信息
    status: str = "正常"                      # 状态（正常/维修/报废）
    location: Optional[str] = None            # 存放位置
    custodian: Optional[str] = None           # 保管人
    
    # 维护信息
    maintenance_cycle: Optional[str] = None   # 维护周期
    last_maintenance: Optional[date] = None   # 上次维护日期
    next_maintenance: Optional[date] = None   # 下次维护日期
    
    # 特种设备
    is_special: bool = False                  # 是否特种设备
    inspection_certificate: Optional[str] = None  # 检验证书编号
    inspection_date: Optional[date] = None    # 检验日期
    next_inspection: Optional[date] = None    # 下次检验日期
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "equipment_id": self.equipment_id,
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "quantity": self.quantity,
            "status": self.status,
            "location": self.location,
            "custodian": self.custodian,
            "is_special": self.is_special,
        }


@dataclass
class Process:
    """业务流程"""
    process_id: Optional[str] = None          # 流程ID
    name: str                                 # 流程名称
    description: Optional[str] = None         # 流程描述
    
    # 流程步骤
    steps: List[Dict[str, Any]] = field(default_factory=list)  # 流程步骤
    
    # 关键控制点
    control_points: List[str] = field(default_factory=list)    # 关键控制点
    
    # 相关文件
    related_documents: List[str] = field(default_factory=list) # 相关文件
    
    # 是否特殊过程
    is_special: bool = False                  # 是否特殊过程
    special_control: Optional[str] = None     # 特殊控制要求
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "process_id": self.process_id,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "control_points": self.control_points,
            "is_special": self.is_special,
        }


@dataclass
class HazardFactor:
    """危险源因素"""
    factor_id: Optional[str] = None           # 因素ID
    activity: str                             # 作业活动
    hazard: str                               # 危险源
    accident_type: str                        # 可能导致的事故
    
    # 风险评估
    likelihood: int = 1                       # 可能性（1-5）
    severity: int = 1                         # 严重性（1-5）
    risk_level: str = "低"                    # 风险等级（低/中/高/极高）
    
    # 控制措施
    control_measures: List[str] = field(default_factory=list)  # 控制措施
    responsible_person: Optional[str] = None  # 责任人
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "factor_id": self.factor_id,
            "activity": self.activity,
            "hazard": self.hazard,
            "accident_type": self.accident_type,
            "risk_level": self.risk_level,
            "control_measures": self.control_measures,
        }


@dataclass
class EnvironmentalFactor:
    """环境因素"""
    factor_id: Optional[str] = None           # 因素ID
    name: str                                 # 环境因素名称
    source: str                               # 排放源
    impact: str                               # 环境影响
    
    # 评价
    significance: str = "一般"                # 重要程度（重要/一般）
    
    # 控制措施
    control_measures: List[str] = field(default_factory=list)  # 控制措施
    target: Optional[str] = None              # 控制目标
    indicator: Optional[str] = None           # 控制指标
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "factor_id": self.factor_id,
            "name": self.name,
            "source": self.source,
            "impact": self.impact,
            "significance": self.significance,
            "control_measures": self.control_measures,
        }


@dataclass
class QualityGoal:
    """质量目标"""
    goal_id: Optional[str] = None             # 目标ID
    name: str                                 # 目标名称
    target_value: str                         # 目标值
    measurement: str                          # 计算方法
    frequency: str = "年度"                   # 考核周期
    responsible_dept: Optional[str] = None    # 责任部门
    current_value: Optional[float] = None     # 当前值
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "name": self.name,
            "target_value": self.target_value,
            "measurement": self.measurement,
            "frequency": self.frequency,
            "responsible_dept": self.responsible_dept,
            "current_value": self.current_value,
        }


@dataclass
class DocumentInfo:
    """文档信息"""
    doc_id: Optional[str] = None              # 文档ID
    name: str                                 # 文档名称
    doc_type: Optional[str] = None            # 文档类型
    doc_number: Optional[str] = None          # 文档编号
    version: str = "1.0"                      # 版本号
    
    # 日期
    issue_date: Optional[date] = None         # 发布日期
    effective_date: Optional[date] = None     # 生效日期
    review_date: Optional[date] = None        # 评审日期
    
    # 状态
    status: str = "有效"                      # 状态（有效/作废/修订中）
    controlled: bool = True                   # 是否受控
    
    # 文件信息
    file_path: Optional[str] = None           # 文件路径
    file_size: Optional[int] = None           # 文件大小
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "name": self.name,
            "doc_type": self.doc_type,
            "doc_number": self.doc_number,
            "version": self.version,
            "status": self.status,
        }


@dataclass
class CompanyInfo:
    """企业完整信息"""
    # === 基础信息 ===
    company_name: Optional[str] = None          # 公司名称
    company_name_en: Optional[str] = None       # 英文名称
    unified_credit_code: Optional[str] = None   # 统一社会信用代码
    legal_representative: Optional[str] = None  # 法定代表人
    registered_capital: Optional[float] = None  # 注册资本（万元）
    establishment_date: Optional[date] = None   # 成立日期
    business_scope: Optional[str] = None        # 经营范围
    company_type: Optional[str] = None          # 企业类型
    
    # === 联系信息 ===
    registered_address: Optional[Address] = None  # 注册地址
    office_address: Optional[Address] = None      # 办公地址
    contact_info: Optional[ContactInfo] = None    # 联系信息
    
    # === 规模信息 ===
    industry: Optional[str] = None              # 行业
    sub_industry: Optional[str] = None          # 细分行业
    employee_count: Optional[int] = None        # 员工人数
    office_area_sqm: Optional[float] = None     # 办公面积（㎡）
    production_area_sqm: Optional[float] = None # 生产面积（㎡）
    
    # === 组织架构 ===
    departments: List[Department] = field(default_factory=list)  # 部门列表
    positions: List[Position] = field(default_factory=list)      # 岗位列表
    employees: List[Employee] = field(default_factory=list)      # 员工列表
    organizational_chart: Optional[str] = None  # 组织架构图URL
    
    # === 认证信息 ===
    certification_type: Optional[str] = None    # 认证类型
    existing_standards: List[str] = field(default_factory=list)  # 已有标准
    target_standards: List[str] = field(default_factory=list)    # 目标标准
    last_audit_date: Optional[date] = None      # 上次审核日期
    certificate_expiry: Optional[date] = None   # 证书有效期
    
    # === 业务信息 ===
    main_products: List[str] = field(default_factory=list)       # 主要产品/服务
    main_processes: List[Process] = field(default_factory=list)  # 主要流程
    main_equipment: List[Equipment] = field(default_factory=list) # 主要设备
    key_customers: List[str] = field(default_factory=list)       # 主要客户
    key_suppliers: List[str] = field(default_factory=list)       # 主要供应商
    
    # === 体系信息 ===
    quality_policy: Optional[str] = None        # 质量方针
    quality_goals: List[QualityGoal] = field(default_factory=list)  # 质量目标
    environment_policy: Optional[str] = None    # 环境方针
    safety_policy: Optional[str] = None         # 安全方针
    
    # === 行业特定 ===
    special_processes: List[str] = field(default_factory=list)   # 特殊过程
    hazard_factors: List[HazardFactor] = field(default_factory=list)  # 危险源
    environmental_factors: List[EnvironmentalFactor] = field(default_factory=list)  # 环境因素
    
    # === 已有材料 ===
    existing_documents: List[DocumentInfo] = field(default_factory=list)  # 已有文档
    missing_documents: List[str] = field(default_factory=list)            # 缺失文档
    
    # === 原始输入 ===
    raw_text: Optional[str] = None              # 原始描述文本
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            # 基础信息
            "company_name": self.company_name,
            "company_name_en": self.company_name_en,
            "unified_credit_code": self.unified_credit_code,
            "legal_representative": self.legal_representative,
            "registered_capital": self.registered_capital,
            "establishment_date": self.establishment_date.isoformat() if self.establishment_date else None,
            "business_scope": self.business_scope,
            
            # 规模信息
            "industry": self.industry,
            "sub_industry": self.sub_industry,
            "employee_count": self.employee_count,
            "office_area_sqm": self.office_area_sqm,
            "production_area_sqm": self.production_area_sqm,
            
            # 联系信息
            "registered_address": str(self.registered_address) if self.registered_address else None,
            "office_address": str(self.office_address) if self.office_address else None,
            
            # 认证信息
            "certification_type": self.certification_type,
            "existing_standards": self.existing_standards,
            "target_standards": self.target_standards,
            
            # 组织信息
            "departments": [d.to_dict() for d in self.departments],
            "positions": [p.to_dict() for p in self.positions],
            "employee_count": self.employee_count,
            
            # 业务信息
            "main_products": self.main_products,
            "main_processes": [p.to_dict() for p in self.main_processes],
            "main_equipment": [e.to_dict() for e in self.main_equipment],
            
            # 体系信息
            "quality_policy": self.quality_policy,
            "quality_goals": [g.to_dict() for g in self.quality_goals],
            "environment_policy": self.environment_policy,
            "safety_policy": self.safety_policy,
            
            # 行业特定
            "special_processes": self.special_processes,
            "hazard_factors": [h.to_dict() for h in self.hazard_factors],
            "environmental_factors": [e.to_dict() for e in self.environmental_factors],
        }
    
    def get_missing_fields(self) -> List[str]:
        """获取缺失的关键字段"""
        missing = []
        
        # 必填字段
        required_fields = {
            "company_name": self.company_name,
            "industry": self.industry,
            "employee_count": self.employee_count,
            "legal_representative": self.legal_representative,
        }
        
        for field_name, value in required_fields.items():
            if not value:
                missing.append(field_name)
        
        # 条件必填
        if not self.departments:
            missing.append("departments")
        
        if not self.quality_policy and "ISO9001" in self.target_standards:
            missing.append("quality_policy")
        
        return missing
    
    def get_summary(self) -> str:
        """获取企业摘要"""
        parts = []
        
        if self.company_name:
            parts.append(f"公司名称：{self.company_name}")
        if self.industry:
            parts.append(f"行业：{self.industry}")
        if self.employee_count:
            parts.append(f"员工人数：{self.employee_count}人")
        if self.target_standards:
            parts.append(f"认证标准：{'、'.join(self.target_standards)}")
        if self.certification_type:
            parts.append(f"认证类型：{self.certification_type}")
        
        return "，".join(parts)


# 工厂函数
def create_company_info_from_dict(data: Dict[str, Any]) -> CompanyInfo:
    """从字典创建企业信息"""
    info = CompanyInfo()
    
    # 基础信息
    for field in ["company_name", "company_name_en", "unified_credit_code", 
                   "legal_representative", "business_scope", "industry", 
                   "sub_industry", "certification_type"]:
        if field in data:
            setattr(info, field, data[field])
    
    # 数值字段
    for field in ["registered_capital", "employee_count", "office_area_sqm", 
                   "production_area_sqm"]:
        if field in data and data[field] is not None:
            setattr(info, field, float(data[field]) if field != "employee_count" else int(data[field]))
    
    # 日期字段
    for field in ["establishment_date", "last_audit_date", "certificate_expiry"]:
        if field in data and data[field]:
            if isinstance(data[field], str):
                setattr(info, field, date.fromisoformat(data[field]))
            elif isinstance(data[field], date):
                setattr(info, field, data[field])
    
    # 列表字段
    for field in ["existing_standards", "target_standards", "main_products", 
                   "key_customers", "key_suppliers", "special_processes"]:
        if field in data and isinstance(data[field], list):
            setattr(info, field, data[field])
    
    # 部门列表
    if "departments" in data and isinstance(data["departments"], list):
        info.departments = [
            Department(**d) if isinstance(d, dict) else d
            for d in data["departments"]
        ]
    
    # 岗位列表
    if "positions" in data and isinstance(data["positions"], list):
        info.positions = [
            Position(**p) if isinstance(p, dict) else p
            for p in data["positions"]
        ]
    
    # 设备列表
    if "main_equipment" in data and isinstance(data["main_equipment"], list):
        info.main_equipment = [
            Equipment(**e) if isinstance(e, dict) else e
            for e in data["main_equipment"]
        ]
    
    return info


# 测试代码
if __name__ == "__main__":
    # 创建测试企业信息
    company = CompanyInfo(
        company_name="武汉鑫辰宇物业服务有限公司",
        industry="物业",
        employee_count=50,
        legal_representative="张三",
        target_standards=["ISO9001", "ISO14001", "ISO45001"],
        certification_type="初次认证",
        departments=[
            Department(name="综合管理部", manager="李四", employee_count=10),
            Department(name="工程部", manager="王五", employee_count=15),
            Department(name="安保部", manager="赵六", employee_count=15),
            Department(name="保洁部", manager="钱七", employee_count=10),
        ],
        main_products=["物业管理服务"],
        main_processes=[
            Process(name="客户服务", is_special=False),
            Process(name="设备维护", is_special=True, special_control="需持证上岗"),
        ],
    )
    
    print("企业摘要:", company.get_summary())
    print("缺失字段:", company.get_missing_fields())
    print("字典输出:", company.to_dict())
