#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 四级文件层次生成器
根据企业信息和认证标准，自动确定需要生成的文档清单
"""
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from .template_manager import DocumentLevel, StandardType, TemplateIDs


@dataclass
class DocumentRequirement:
    """文档需求"""
    template_id: str                          # 模板ID
    name: str                                 # 文档名称
    document_level: DocumentLevel             # 文档层级
    standard: Optional[StandardType]          # 适用标准
    required: bool = True                     # 是否必需
    industry_specific: bool = False           # 是否行业特定
    industry: Optional[str] = None            # 适用行业
    description: Optional[str] = None         # 描述
    
    # 依赖关系
    depends_on: List[str] = field(default_factory=list)  # 依赖的文档


class DocumentHierarchyConfig:
    """文档层次配置"""
    
    # ==================== 一级文件：管理手册 ====================
    LEVEL_1_DOCUMENTS = {
        # ISO9001 质量管理手册
        "iso9001_quality_manual": DocumentRequirement(
            template_id=TemplateIDs.QUALITY_MANUAL,
            name="质量管理手册",
            document_level=DocumentLevel.LEVEL_1,
            standard=StandardType.ISO9001,
            required=True,
            description="依据ISO9001标准编制的质量管理手册",
        ),
        
        # ISO14001 环境管理手册
        "iso14001_environment_manual": DocumentRequirement(
            template_id=TemplateIDs.ENVIRONMENT_MANUAL,
            name="环境管理手册",
            document_level=DocumentLevel.LEVEL_1,
            standard=StandardType.ISO14001,
            required=True,
            description="依据ISO14001标准编制的环境管理手册",
        ),
        
        # ISO45001 职业健康安全管理手册
        "iso45001_safety_manual": DocumentRequirement(
            template_id=TemplateIDs.SAFETY_MANUAL,
            name="职业健康安全管理手册",
            document_level=DocumentLevel.LEVEL_1,
            standard=StandardType.ISO45001,
            required=True,
            description="依据ISO45001标准编制的职业健康安全管理手册",
        ),
        
        # 三标一体管理手册
        "integrated_manual": DocumentRequirement(
            template_id=TemplateIDs.INTEGRATED_MANUAL,
            name="质量环境安全综合管理手册",
            document_level=DocumentLevel.LEVEL_1,
            standard=None,  # 适用于多标一体
            required=False,
            description="三标一体化管理手册",
        ),
    }
    
    # ==================== 二级文件：程序文件 ====================
    LEVEL_2_DOCUMENTS = {
        # === 通用程序文件（所有标准都适用）===
        "doc_control": DocumentRequirement(
            template_id=TemplateIDs.DOC_CONTROL_PROCEDURE,
            name="文件控制程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=None,  # 通用
            required=True,
            description="规定文件的编制、审批、发放、使用、修订、回收等控制要求",
        ),
        
        "record_control": DocumentRequirement(
            template_id=TemplateIDs.RECORD_CONTROL_PROCEDURE,
            name="记录控制程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=None,
            required=True,
            description="规定记录的标识、贮存、保护、检索、保存期限和处置等要求",
        ),
        
        "internal_audit": DocumentRequirement(
            template_id=TemplateIDs.INTERNAL_AUDIT_PROCEDURE,
            name="内部审核程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=None,
            required=True,
            description="规定内部审核的计划、实施、报告和跟踪验证等要求",
        ),
        
        "management_review": DocumentRequirement(
            template_id=TemplateIDs.MANAGEMENT_REVIEW_PROCEDURE,
            name="管理评审程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=None,
            required=True,
            description="规定管理评审的计划、输入、输出和跟踪措施等要求",
        ),
        
        "corrective_action": DocumentRequirement(
            template_id=TemplateIDs.CORRECTIVE_ACTION_PROCEDURE,
            name="纠正措施控制程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=None,
            required=True,
            description="规定不合格的识别、原因分析、纠正措施的制定和实施等要求",
        ),
        
        "training": DocumentRequirement(
            template_id=TemplateIDs.TRAINING_PROCEDURE,
            name="培训控制程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=None,
            required=True,
            description="规定培训需求的识别、计划、实施、评价和记录等要求",
        ),
        
        # === ISO9001 特定程序文件 ===
        "contract_review": DocumentRequirement(
            template_id=TemplateIDs.CONTRACT_REVIEW_PROCEDURE,
            name="合同评审程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=StandardType.ISO9001,
            required=True,
            description="规定产品要求的确定、评审和沟通等要求",
        ),
        
        "purchasing": DocumentRequirement(
            template_id=TemplateIDs.PURCHASING_PROCEDURE,
            name="采购控制程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=StandardType.ISO9001,
            required=True,
            description="规定供方评价、采购信息、采购产品的验证等要求",
        ),
        
        "production_control": DocumentRequirement(
            template_id=TemplateIDs.PRODUCTION_CONTROL_PROCEDURE,
            name="生产和服务提供控制程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=StandardType.ISO9001,
            required=True,
            description="规定生产和服务提供的策划、控制、标识、防护等要求",
        ),
        
        "inspection": DocumentRequirement(
            template_id=TemplateIDs.INSPECTION_PROCEDURE,
            name="产品检验控制程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=StandardType.ISO9001,
            required=True,
            description="规定进货检验、过程检验、最终检验等要求",
        ),
        
        "customer_satisfaction": DocumentRequirement(
            template_id=TemplateIDs.CUSTOMER_SATISFACTION_PROCEDURE,
            name="顾客满意度测量程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=StandardType.ISO9001,
            required=True,
            description="规定顾客满意度信息的获取、分析和利用等要求",
        ),
        
        # === ISO14001 特定程序文件 ===
        "environmental_factors": DocumentRequirement(
            template_id=TemplateIDs.ENVIRONMENTAL_FACTORS_PROCEDURE,
            name="环境因素识别与评价程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=StandardType.ISO14001,
            required=True,
            description="规定环境因素的识别、评价和更新等要求",
        ),
        
        "legal_requirements": DocumentRequirement(
            template_id=TemplateIDs.LEGAL_REQUIREMENTS_PROCEDURE,
            name="法律法规获取与更新程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=StandardType.ISO14001,
            required=True,
            description="规定环境法律法规的获取、识别、更新和合规性评价等要求",
        ),
        
        "emergency_response_env": DocumentRequirement(
            template_id=TemplateIDs.EMERGENCY_RESPONSE_PROCEDURE,
            name="应急准备和响应程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=StandardType.ISO14001,
            required=True,
            description="规定环境突发事件的应急准备和响应要求",
        ),
        
        # === ISO45001 特定程序文件 ===
        "hazard_identification": DocumentRequirement(
            template_id=TemplateIDs.HAZARD_IDENTIFICATION_PROCEDURE,
            name="危险源辨识与风险评价程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=StandardType.ISO45001,
            required=True,
            description="规定危险源的辨识、风险评价和控制措施的确定等要求",
        ),
        
        "incident_investigation": DocumentRequirement(
            template_id=TemplateIDs.INCIDENT_INVESTIGATION_PROCEDURE,
            name="事件调查与处理程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=StandardType.ISO45001,
            required=True,
            description="规定事件的报告、调查、处理和预防措施等要求",
        ),
        
        "emergency_response_safety": DocumentRequirement(
            template_id=TemplateIDs.EMERGENCY_RESPONSE_PROCEDURE,
            name="应急准备和响应程序",
            document_level=DocumentLevel.LEVEL_2,
            standard=StandardType.ISO45001,
            required=True,
            description="规定职业健康安全突发事件的应急准备和响应要求",
        ),
    }
    
    # ==================== 三级文件：作业指导书 ====================
    LEVEL_3_DOCUMENTS = {
        # 岗位职责说明书
        "job_description": DocumentRequirement(
            template_id=TemplateIDs.JOB_DESCRIPTION,
            name="岗位职责说明书",
            document_level=DocumentLevel.LEVEL_3,
            standard=None,
            required=True,
            description="各岗位的职责、权限、任职资格和考核指标",
        ),
        
        # 作业指导书（根据行业和过程生成）
        "work_instruction": DocumentRequirement(
            template_id=TemplateIDs.WORK_INSTRUCTION,
            name="作业指导书",
            document_level=DocumentLevel.LEVEL_3,
            standard=None,
            required=False,  # 根据实际情况确定
            description="具体作业的操作步骤和要求",
        ),
        
        # 设备操作规程
        "equipment_operation": DocumentRequirement(
            template_id=TemplateIDs.EQUIPMENT_OPERATION,
            name="设备操作规程",
            document_level=DocumentLevel.LEVEL_3,
            standard=None,
            required=False,  # 有设备时需要
            description="设备的操作步骤、安全注意事项和维护要求",
        ),
        
        # 检验标准
        "inspection_standard": DocumentRequirement(
            template_id=TemplateIDs.INSPECTION_STANDARD,
            name="检验标准",
            document_level=DocumentLevel.LEVEL_3,
            standard=StandardType.ISO9001,
            required=False,
            description="产品/服务的检验标准和判定准则",
        ),
        
        # 安全操作规程
        "safety_procedure": DocumentRequirement(
            template_id=TemplateIDs.SAFETY_PROCEDURE,
            name="安全操作规程",
            document_level=DocumentLevel.LEVEL_3,
            standard=StandardType.ISO45001,
            required=True,
            description="各岗位的安全操作要求和注意事项",
        ),
    }
    
    # ==================== 四级文件：记录表格 ====================
    LEVEL_4_DOCUMENTS = {
        # 培训记录
        "training_record": DocumentRequirement(
            template_id=TemplateIDs.TRAINING_RECORD,
            name="培训记录表",
            document_level=DocumentLevel.LEVEL_4,
            standard=None,
            required=True,
            description="培训实施和考核的记录",
        ),
        
        # 检验记录
        "inspection_record": DocumentRequirement(
            template_id=TemplateIDs.INSPECTION_RECORD,
            name="检验记录表",
            document_level=DocumentLevel.LEVEL_4,
            standard=StandardType.ISO9001,
            required=True,
            description="产品/服务检验的记录",
        ),
        
        # 内审检查表
        "audit_checklist": DocumentRequirement(
            template_id=TemplateIDs.AUDIT_CHECKLIST,
            name="内审检查表",
            document_level=DocumentLevel.LEVEL_4,
            standard=None,
            required=True,
            description="内部审核的检查表",
        ),
        
        # 纠正措施单
        "corrective_action_form": DocumentRequirement(
            template_id=TemplateIDs.CORRECTIVE_ACTION_FORM,
            name="纠正措施单",
            document_level=DocumentLevel.LEVEL_4,
            standard=None,
            required=True,
            description="纠正措施的申请、实施和验证记录",
        ),
        
        # 管理评审记录
        "management_review_record": DocumentRequirement(
            template_id=TemplateIDs.MANAGEMENT_REVIEW_RECORD,
            name="管理评审记录",
            document_level=DocumentLevel.LEVEL_4,
            standard=None,
            required=True,
            description="管理评审的输入、输出和决议记录",
        ),
    }
    
    # ==================== 行业特定文档 ====================
    INDUSTRY_SPECIFIC_DOCUMENTS = {
        # 物业行业
        "property": {
            "LEVEL_3": [
                DocumentRequirement(
                    template_id="property_service_standard",
                    name="物业服务标准",
                    document_level=DocumentLevel.LEVEL_3,
                    standard=None,
                    required=True,
                    industry_specific=True,
                    industry="物业",
                    description="物业服务的标准和规范",
                ),
                DocumentRequirement(
                    template_id="equipment_maintenance_instruction",
                    name="设备维护作业指导书",
                    document_level=DocumentLevel.LEVEL_3,
                    standard=None,
                    required=True,
                    industry_specific=True,
                    industry="物业",
                    description="设备维护的操作步骤和要求",
                ),
                DocumentRequirement(
                    template_id="security_patrol_instruction",
                    name="安保巡逻作业指导书",
                    document_level=DocumentLevel.LEVEL_3,
                    standard=None,
                    required=True,
                    industry_specific=True,
                    industry="物业",
                    description="安保巡逻的路线、频次和要求",
                ),
            ],
            "LEVEL_4": [
                DocumentRequirement(
                    template_id="property_inspection_record",
                    name="物业巡查记录表",
                    document_level=DocumentLevel.LEVEL_4,
                    standard=None,
                    required=True,
                    industry_specific=True,
                    industry="物业",
                    description="物业日常巡查的记录",
                ),
                DocumentRequirement(
                    template_id="equipment_maintenance_record",
                    name="设备维护保养记录",
                    document_level=DocumentLevel.LEVEL_4,
                    standard=None,
                    required=True,
                    industry_specific=True,
                    industry="物业",
                    description="设备维护保养的记录",
                ),
            ],
        },
        
        # 制造业
        "manufacturing": {
            "LEVEL_3": [
                DocumentRequirement(
                    template_id="production_work_instruction",
                    name="生产作业指导书",
                    document_level=DocumentLevel.LEVEL_3,
                    standard=None,
                    required=True,
                    industry_specific=True,
                    industry="制造业",
                    description="生产作业的操作步骤和要求",
                ),
                DocumentRequirement(
                    template_id="quality_inspection_instruction",
                    name="质量检验作业指导书",
                    document_level=DocumentLevel.LEVEL_3,
                    standard=StandardType.ISO9001,
                    required=True,
                    industry_specific=True,
                    industry="制造业",
                    description="质量检验的方法和判定标准",
                ),
            ],
            "LEVEL_4": [
                DocumentRequirement(
                    template_id="production_record",
                    name="生产记录表",
                    document_level=DocumentLevel.LEVEL_4,
                    standard=StandardType.ISO9001,
                    required=True,
                    industry_specific=True,
                    industry="制造业",
                    description="生产过程的记录",
                ),
            ],
        },
    }


class DocumentHierarchyGenerator:
    """四级文件层次生成器"""
    
    def __init__(self):
        self.config = DocumentHierarchyConfig()
    
    def generate_document_list(
        self,
        standards: List[str],
        industry: Optional[str] = None,
        company_info: Optional[Dict[str, Any]] = None
    ) -> List[DocumentRequirement]:
        """
        生成文档需求清单
        
        Args:
            standards: 目标标准列表，如 ["ISO9001", "ISO14001", "ISO45001"]
            industry: 行业类型
            company_info: 企业信息（用于判断是否需要某些文档）
        
        Returns:
            文档需求列表
        """
        documents = []
        added_ids: Set[str] = set()
        
        # 转换标准类型
        standard_enums = []
        for std in standards:
            try:
                standard_enums.append(StandardType(std))
            except ValueError:
                pass
        
        # 1. 生成一级文件（管理手册）
        level_1_docs = self._get_level_1_documents(standard_enums)
        for doc in level_1_docs:
            if doc.template_id not in added_ids:
                documents.append(doc)
                added_ids.add(doc.template_id)
        
        # 2. 生成二级文件（程序文件）
        level_2_docs = self._get_level_2_documents(standard_enums)
        for doc in level_2_docs:
            if doc.template_id not in added_ids:
                documents.append(doc)
                added_ids.add(doc.template_id)
        
        # 3. 生成三级文件（作业指导书）
        level_3_docs = self._get_level_3_documents(standard_enums, industry, company_info)
        for doc in level_3_docs:
            if doc.template_id not in added_ids:
                documents.append(doc)
                added_ids.add(doc.template_id)
        
        # 4. 生成四级文件（记录表格）
        level_4_docs = self._get_level_4_documents(standard_enums, industry)
        for doc in level_4_docs:
            if doc.template_id not in added_ids:
                documents.append(doc)
                added_ids.add(doc.template_id)
        
        return documents
    
    def _get_level_1_documents(
        self,
        standards: List[StandardType]
    ) -> List[DocumentRequirement]:
        """获取一级文件"""
        documents = []
        
        # 如果是多标一体，生成综合手册
        if len(standards) >= 2:
            documents.append(self.config.LEVEL_1_DOCUMENTS["integrated_manual"])
        else:
            # 单独生成各标准的管理手册
            for standard in standards:
                if standard == StandardType.ISO9001:
                    documents.append(self.config.LEVEL_1_DOCUMENTS["iso9001_quality_manual"])
                elif standard == StandardType.ISO14001:
                    documents.append(self.config.LEVEL_1_DOCUMENTS["iso14001_environment_manual"])
                elif standard == StandardType.ISO45001:
                    documents.append(self.config.LEVEL_1_DOCUMENTS["iso45001_safety_manual"])
        
        return documents
    
    def _get_level_2_documents(
        self,
        standards: List[StandardType]
    ) -> List[DocumentRequirement]:
        """获取二级文件"""
        documents = []
        
        for doc_id, doc_req in self.config.LEVEL_2_DOCUMENTS.items():
            # 通用程序文件
            if doc_req.standard is None:
                documents.append(doc_req)
            # 标准特定程序文件
            elif doc_req.standard in standards:
                documents.append(doc_req)
        
        return documents
    
    def _get_level_3_documents(
        self,
        standards: List[StandardType],
        industry: Optional[str],
        company_info: Optional[Dict[str, Any]]
    ) -> List[DocumentRequirement]:
        """获取三级文件"""
        documents = []
        
        # 基础三级文件
        for doc_id, doc_req in self.config.LEVEL_3_DOCUMENTS.items():
            # 通用三级文件
            if doc_req.standard is None:
                documents.append(doc_req)
            # 标准特定三级文件
            elif doc_req.standard in standards:
                documents.append(doc_req)
        
        # 行业特定三级文件
        if industry and industry in self.config.INDUSTRY_SPECIFIC_DOCUMENTS:
            industry_docs = self.config.INDUSTRY_SPECIFIC_DOCUMENTS[industry].get("LEVEL_3", [])
            documents.extend(industry_docs)
        
        # 根据企业信息补充
        if company_info:
            # 如果有设备，添加设备操作规程
            if company_info.get("main_equipment"):
                existing_ids = {d.template_id for d in documents}
                if "equipment_operation" not in existing_ids:
                    documents.append(self.config.LEVEL_3_DOCUMENTS["equipment_operation"])
        
        return documents
    
    def _get_level_4_documents(
        self,
        standards: List[StandardType],
        industry: Optional[str]
    ) -> List[DocumentRequirement]:
        """获取四级文件"""
        documents = []
        
        # 基础四级文件
        for doc_id, doc_req in self.config.LEVEL_4_DOCUMENTS.items():
            # 通用四级文件
            if doc_req.standard is None:
                documents.append(doc_req)
            # 标准特定四级文件
            elif doc_req.standard in standards:
                documents.append(doc_req)
        
        # 行业特定四级文件
        if industry and industry in self.config.INDUSTRY_SPECIFIC_DOCUMENTS:
            industry_docs = self.config.INDUSTRY_SPECIFIC_DOCUMENTS[industry].get("LEVEL_4", [])
            documents.extend(industry_docs)
        
        return documents
    
    def get_document_summary(
        self,
        standards: List[str],
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取文档摘要统计"""
        documents = self.generate_document_list(standards, industry)
        
        summary = {
            "total": len(documents),
            "by_level": {},
            "by_standard": {},
            "required_count": 0,
            "optional_count": 0,
        }
        
        for doc in documents:
            # 按层级统计
            level = doc.document_level.value
            summary["by_level"][level] = summary["by_level"].get(level, 0) + 1
            
            # 按标准统计
            std = doc.standard.value if doc.standard else "通用"
            summary["by_standard"][std] = summary["by_standard"].get(std, 0) + 1
            
            # 必需/可选统计
            if doc.required:
                summary["required_count"] += 1
            else:
                summary["optional_count"] += 1
        
        return summary


# 便捷函数
def get_required_documents(
    standards: List[str],
    industry: Optional[str] = None,
    company_info: Optional[Dict[str, Any]] = None
) -> List[DocumentRequirement]:
    """获取所需文档列表的便捷函数"""
    generator = DocumentHierarchyGenerator()
    return generator.generate_document_list(standards, industry, company_info)


# 测试代码
if __name__ == "__main__":
    # 测试生成文档列表
    generator = DocumentHierarchyGenerator()
    
    # 测试三标一体
    standards = ["ISO9001", "ISO14001", "ISO45001"]
    industry = "物业"
    
    documents = generator.generate_document_list(standards, industry)
    summary = generator.get_document_summary(standards, industry)
    
    print("=" * 60)
    print(f"文档清单（{len(documents)}份）")
    print("=" * 60)
    
    for doc in documents:
        print(f"[{doc.document_level.value}] {doc.name} - {'必需' if doc.required else '可选'}")
    
    print("\n" + "=" * 60)
    print("统计摘要")
    print("=" * 60)
    print(f"总数: {summary['total']}")
    print(f"按层级: {summary['by_level']}")
    print(f"按标准: {summary['by_standard']}")
    print(f"必需: {summary['required_count']}, 可选: {summary['optional_count']}")
