#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行业配置初始化脚本 - V2.1

初始化11个行业的配置数据和特有文件。
运行方式：python -m app.core.init_industries
"""

from sqlalchemy.orm import Session
from app.core.database import get_db, init_db
from app.models.models import IndustryConfig, IndustrySpecialFile


# ==================== 行业基础配置 ====================

INDUSTRY_CONFIGS = [
    {
        "industry_code": "system_integration",
        "industry_name": "系统集成",
        "description": "信息系统集成服务，包括网络工程、安防工程、智能化工程等",
        "has_design_development": True,
        "has_equipment_operations": True,
        "has_multi_projects": True,
        "has_outsourcing": True,
        "internal_audit_by_dept": True,
        "emergency_plans": ["火灾", "触电", "高处坠落", "设备伤害"],
        "required_licenses": [],
        "certification_scope_classes": ["35.11", "35.12", "35.13"],
    },
    {
        "industry_code": "software_development",
        "industry_name": "软件开发",
        "description": "软件开发、信息技术服务",
        "has_design_development": True,
        "has_equipment_operations": False,
        "has_multi_projects": True,
        "has_outsourcing": True,
        "internal_audit_by_dept": True,
        "emergency_plans": ["火灾", "触电", "身体伤害"],
        "required_licenses": [],
        "certification_scope_classes": ["62.01", "62.02", "62.03"],
    },
    {
        "industry_code": "construction",
        "industry_name": "建筑工程",
        "description": "房屋建筑、市政工程、装饰装修等",
        "has_design_development": True,
        "has_equipment_operations": True,
        "has_multi_projects": True,
        "has_outsourcing": True,
        "internal_audit_by_dept": True,
        "emergency_plans": ["火灾", "触电", "高处坠落", "坍塌", "机械伤害", "物体打击"],
        "required_licenses": ["建筑业企业资质证书", "安全生产许可证"],
        "certification_scope_classes": ["41.10", "42.11", "42.12", "42.13", "42.21", "42.22", "42.99", "43.11", "43.12", "43.13", "43.21", "43.22", "43.29", "43.31", "43.32", "43.33", "43.34", "43.39", "43.91", "43.99"],
    },
    {
        "industry_code": "steel_structure",
        "industry_name": "钢结构",
        "description": "钢结构设计、制作、安装",
        "has_design_development": True,
        "has_equipment_operations": True,
        "has_multi_projects": True,
        "has_outsourcing": True,
        "internal_audit_by_dept": True,
        "emergency_plans": ["火灾", "触电", "高处坠落", "坍塌", "机械伤害", "物体打击"],
        "required_licenses": ["建筑业企业资质证书", "安全生产许可证"],
        "certification_scope_classes": ["25.11", "43.99"],
    },
    {
        "industry_code": "archive_digitalization",
        "industry_name": "档案数字化",
        "description": "档案整理、数字化加工、档案管理服务",
        "has_design_development": False,
        "has_equipment_operations": True,
        "has_multi_projects": True,
        "has_outsourcing": True,
        "internal_audit_by_dept": True,
        "emergency_plans": ["火灾", "触电", "身体伤害", "信息安全事件"],
        "required_licenses": ["档案服务外包资质"],
        "certification_scope_classes": ["35.11", "35.12"],
    },
    {
        "industry_code": "intelligent_manufacturing",
        "industry_name": "智能制造",
        "description": "智能装备、自动化设备、机器人制造",
        "has_design_development": True,
        "has_equipment_operations": True,
        "has_multi_projects": True,
        "has_outsourcing": True,
        "internal_audit_by_dept": True,
        "emergency_plans": ["火灾", "触电", "机械伤害", "高处坠落"],
        "required_licenses": [],
        "certification_scope_classes": ["28.11", "28.12", "28.13", "28.14", "28.15", "28.21", "28.22", "28.23", "28.24", "28.25", "28.29", "28.30", "28.41", "28.49", "28.91", "28.92", "28.93", "28.94", "28.95", "28.96", "28.99"],
    },
    {
        "industry_code": "food_production",
        "industry_name": "食品生产",
        "description": "食品、饮料生产加工",
        "has_design_development": False,
        "has_equipment_operations": True,
        "has_multi_projects": False,
        "has_outsourcing": True,
        "internal_audit_by_dept": True,
        "emergency_plans": ["火灾", "触电", "机械伤害", "食品安全事故"],
        "required_licenses": ["食品生产许可证", "食品经营许可证"],
        "certification_scope_classes": ["10.11", "10.12", "10.13", "10.20", "10.31", "10.32", "10.39", "10.41", "10.42", "10.43", "10.51", "10.52", "10.53", "10.61", "10.62", "10.63", "10.71", "10.72", "10.73", "10.81", "10.82", "10.83", "10.84", "10.85", "10.86", "10.89", "10.91", "10.92", "11.01", "11.02", "11.03", "11.04", "11.05", "11.06", "11.07"],
    },
    {
        "industry_code": "electromechanical",
        "industry_name": "机电设备",
        "description": "机电设备制造、安装、维修",
        "has_design_development": True,
        "has_equipment_operations": True,
        "has_multi_projects": True,
        "has_outsourcing": True,
        "internal_audit_by_dept": True,
        "emergency_plans": ["火灾", "触电", "机械伤害", "高处坠落"],
        "required_licenses": [],
        "certification_scope_classes": ["25.11", "25.12", "25.13", "25.21", "25.29", "25.30", "25.40", "25.50", "25.61", "25.62", "25.71", "25.72", "25.73", "25.91", "25.92", "25.93", "25.94", "25.99", "27.11", "27.12", "28.11", "28.12", "28.13", "28.14", "28.15", "29.10", "29.20", "29.31", "29.32"],
    },
    {
        "industry_code": "intelligent_tech",
        "industry_name": "智能科技",
        "description": "智能科技产品研发、物联网、人工智能应用",
        "has_design_development": True,
        "has_equipment_operations": False,
        "has_multi_projects": True,
        "has_outsourcing": True,
        "internal_audit_by_dept": True,
        "emergency_plans": ["火灾", "触电", "身体伤害"],
        "required_licenses": [],
        "certification_scope_classes": ["62.01", "62.02", "62.03", "62.09", "63.11", "63.12"],
    },
    {
        "industry_code": "property_management",
        "industry_name": "物业管理",
        "description": "物业服务、设施管理、保洁绿化",
        "has_design_development": True,
        "has_equipment_operations": False,
        "has_multi_projects": True,
        "has_outsourcing": True,
        "internal_audit_by_dept": True,
        "emergency_plans": ["火灾", "触电", "身体伤害", "高空坠落", "交通意外", "中暑"],
        "required_licenses": ["物业服务企业资质证书"],
        "certification_scope_classes": ["36.01", "36.02", "36.03"],
    },
    {
        "industry_code": "labor_dispatch",
        "industry_name": "劳务派遣",
        "description": "人力资源服务、劳务派遣、人员外包",
        "has_design_development": True,
        "has_equipment_operations": False,
        "has_multi_projects": True,
        "has_outsourcing": False,
        "internal_audit_by_dept": True,
        "emergency_plans": ["火灾", "触电", "身体伤害", "交通意外"],
        "required_licenses": ["人力资源服务许可证", "劳务派遣经营许可证"],
        "certification_scope_classes": ["35.02"],
    },
]


# ==================== 行业特有文件 ====================

INDUSTRY_SPECIAL_FILES = {
    "system_integration": [
        {"file_level": "C", "file_code": "C-010", "file_name": "项目实施方案编制规范", "category": "project_mgmt", "iso_clause": "8.1"},
        {"file_level": "C", "file_code": "C-011", "file_name": "系统集成测试规程", "category": "testing", "iso_clause": "8.6"},
        {"file_level": "C", "file_code": "C-012", "file_name": "客户现场施工安全规程", "category": "safety", "iso_clause": "8.1"},
        {"file_level": "C", "file_code": "C-013", "file_name": "系统验收与交付规程", "category": "delivery", "iso_clause": "8.5"},
        {"file_level": "C", "file_code": "C-014", "file_name": "售后服务与运维规程", "category": "service", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-077", "file_name": "项目实施方案", "category": "project_mgmt", "iso_clause": "8.1"},
        {"file_level": "D", "file_code": "D-078", "file_name": "系统测试报告", "category": "testing", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-079", "file_name": "客户验收单", "category": "delivery", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-080", "file_name": "设备巡检记录表", "category": "equipment", "iso_clause": "7.1"},
        {"file_level": "D", "file_code": "D-081", "file_name": "现场施工安全检查表", "category": "safety", "iso_clause": "8.1"},
    ],
    "software_development": [
        {"file_level": "C", "file_code": "C-010", "file_name": "软件设计开发管理制度", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "C", "file_code": "C-011", "file_name": "源代码管理制度", "category": "source_code", "iso_clause": "7.5"},
        {"file_level": "C", "file_code": "C-012", "file_name": "软件测试管理规程", "category": "testing", "iso_clause": "8.6"},
        {"file_level": "C", "file_code": "C-013", "file_name": "版本发布管理规程", "category": "release", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-077", "file_name": "软件需求规格说明书", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-078", "file_name": "软件设计说明书", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-079", "file_name": "代码评审记录", "category": "source_code", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-080", "file_name": "软件测试用例", "category": "testing", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-081", "file_name": "软件测试报告", "category": "testing", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-082", "file_name": "版本发布记录", "category": "release", "iso_clause": "8.5"},
    ],
    "construction": [
        {"file_level": "B", "file_code": "B-028", "file_name": "施工过程控制程序", "category": "construction", "iso_clause": "8.5"},
        {"file_level": "C", "file_code": "C-010", "file_name": "施工组织设计编制规程", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "C", "file_code": "C-011", "file_name": "施工安全技术规程", "category": "safety", "iso_clause": "8.1"},
        {"file_level": "C", "file_code": "C-012", "file_name": "材料进场检验规程", "category": "inspection", "iso_clause": "8.4"},
        {"file_level": "C", "file_code": "C-013", "file_name": "隐蔽工程验收规程", "category": "inspection", "iso_clause": "8.6"},
        {"file_level": "C", "file_code": "C-014", "file_name": "工程竣工验收规程", "category": "delivery", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-077", "file_name": "施工组织设计", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-078", "file_name": "施工日志", "category": "construction", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-079", "file_name": "材料进场检验记录", "category": "inspection", "iso_clause": "8.4"},
        {"file_level": "D", "file_code": "D-080", "file_name": "隐蔽工程验收记录", "category": "inspection", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-081", "file_name": "分部分项工程验收记录", "category": "inspection", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-082", "file_name": "工程竣工验收报告", "category": "delivery", "iso_clause": "8.6"},
    ],
    "steel_structure": [
        {"file_level": "C", "file_code": "C-010", "file_name": "钢结构制作工艺规程", "category": "manufacturing", "iso_clause": "8.5"},
        {"file_level": "C", "file_code": "C-011", "file_name": "钢结构安装技术规程", "category": "installation", "iso_clause": "8.5"},
        {"file_level": "C", "file_code": "C-012", "file_name": "焊接工艺评定规程", "category": "welding", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-077", "file_name": "钢结构制作检验记录", "category": "inspection", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-078", "file_name": "焊接工艺评定报告", "category": "welding", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-079", "file_name": "焊缝无损检测记录", "category": "inspection", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-080", "file_name": "钢结构安装验收记录", "category": "inspection", "iso_clause": "8.6"},
    ],
    "archive_digitalization": [
        {"file_level": "C", "file_code": "C-010", "file_name": "档案整理服务规范", "category": "service", "iso_clause": "8.5"},
        {"file_level": "C", "file_code": "C-011", "file_name": "档案数字化加工操作规程", "category": "operation", "iso_clause": "8.5"},
        {"file_level": "C", "file_code": "C-012", "file_name": "档案保密管理制度", "category": "security", "iso_clause": "8.1"},
        {"file_level": "C", "file_code": "C-013", "file_name": "档案信息安全管理规程", "category": "security", "iso_clause": "8.1"},
        {"file_level": "D", "file_code": "D-077", "file_name": "档案接收登记表", "category": "record", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-078", "file_name": "档案整理加工记录表", "category": "record", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-079", "file_name": "档案数字化加工记录表", "category": "record", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-080", "file_name": "档案移交清单", "category": "record", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-081", "file_name": "客户验收评价表", "category": "record", "iso_clause": "8.6"},
    ],
    "intelligent_manufacturing": [
        {"file_level": "C", "file_code": "C-010", "file_name": "设备操作规程总册", "category": "equipment", "iso_clause": "7.1"},
        {"file_level": "C", "file_code": "C-011", "file_name": "关键工序控制规程", "category": "process", "iso_clause": "8.5"},
        {"file_level": "C", "file_code": "C-012", "file_name": "产品检验规程", "category": "inspection", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-077", "file_name": "设备点检表", "category": "equipment", "iso_clause": "7.1"},
        {"file_level": "D", "file_code": "D-078", "file_name": "设备维护保养记录", "category": "equipment", "iso_clause": "7.1"},
        {"file_level": "D", "file_code": "D-079", "file_name": "关键工序监控记录", "category": "process", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-080", "file_name": "产品检验记录", "category": "inspection", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-081", "file_name": "不合格品处置记录", "category": "ncr", "iso_clause": "8.7"},
    ],
    "food_production": [
        {"file_level": "C", "file_code": "C-010", "file_name": "HACCP计划", "category": "food_safety", "iso_clause": "8.5"},
        {"file_level": "C", "file_code": "C-011", "file_name": "食品生产卫生标准操作程序(SSOP)", "category": "food_safety", "iso_clause": "8.1"},
        {"file_level": "C", "file_code": "C-012", "file_name": "原料验收规程", "category": "inspection", "iso_clause": "8.4"},
        {"file_level": "C", "file_code": "C-013", "file_name": "产品追溯与召回规程", "category": "traceability", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-077", "file_name": "原料验收记录", "category": "inspection", "iso_clause": "8.4"},
        {"file_level": "D", "file_code": "D-078", "file_name": "生产过程监控记录", "category": "process", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-079", "file_name": "产品检验报告", "category": "inspection", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-080", "file_name": "产品追溯记录", "category": "traceability", "iso_clause": "8.5"},
    ],
    "electromechanical": [
        {"file_level": "C", "file_code": "C-010", "file_name": "设备操作规程总册", "category": "equipment", "iso_clause": "7.1"},
        {"file_level": "C", "file_code": "C-011", "file_name": "关键工序控制规程", "category": "process", "iso_clause": "8.5"},
        {"file_level": "C", "file_code": "C-012", "file_name": "产品检验规程", "category": "inspection", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-077", "file_name": "设备点检表", "category": "equipment", "iso_clause": "7.1"},
        {"file_level": "D", "file_code": "D-078", "file_name": "设备维护保养记录", "category": "equipment", "iso_clause": "7.1"},
        {"file_level": "D", "file_code": "D-079", "file_name": "关键工序监控记录", "category": "process", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-080", "file_name": "产品检验记录", "category": "inspection", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-081", "file_name": "不合格品处置记录", "category": "ncr", "iso_clause": "8.7"},
    ],
    "intelligent_tech": [
        {"file_level": "C", "file_code": "C-010", "file_name": "智能硬件设计开发规程", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "C", "file_code": "C-011", "file_name": "嵌入式软件管理制度", "category": "software", "iso_clause": "7.5"},
        {"file_level": "C", "file_code": "C-012", "file_name": "产品测试验证规程", "category": "testing", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-077", "file_name": "硬件设计评审记录", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-078", "file_name": "软件测试报告", "category": "testing", "iso_clause": "8.6"},
        {"file_level": "D", "file_code": "D-079", "file_name": "产品可靠性测试记录", "category": "testing", "iso_clause": "8.6"},
    ],
    "property_management": [
        {"file_level": "B", "file_code": "B-028", "file_name": "噪音控制管理程序", "category": "environment", "iso_clause": "8.1"},
        {"file_level": "C", "file_code": "C-010", "file_name": "公共区域清洁规程", "category": "service", "iso_clause": "8.5"},
        {"file_level": "C", "file_code": "C-011", "file_name": "绿化养护规程", "category": "service", "iso_clause": "8.5"},
        {"file_level": "C", "file_code": "C-012", "file_name": "电梯困人应急预案", "category": "emergency", "iso_clause": "8.1"},
        {"file_level": "C", "file_code": "C-013", "file_name": "项目检查管理评价规程", "category": "inspection", "iso_clause": "9.1"},
        {"file_level": "C", "file_code": "C-014", "file_name": "物业管理服务方案编制规范", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "C", "file_code": "C-015", "file_name": "不合格服务处置规程", "category": "ncr", "iso_clause": "8.7"},
        {"file_level": "C", "file_code": "C-016", "file_name": "售后服务回访规程", "category": "service", "iso_clause": "8.5"},
        {"file_level": "D", "file_code": "D-077", "file_name": "项目检查管理评价表(公司级)", "category": "inspection", "iso_clause": "9.1"},
        {"file_level": "D", "file_code": "D-078", "file_name": "项目检查管理评价表(物业经理级)", "category": "inspection", "iso_clause": "9.1"},
        {"file_level": "D", "file_code": "D-079", "file_name": "项目检查管理评价表(客户级)", "category": "inspection", "iso_clause": "9.1"},
        {"file_level": "D", "file_code": "D-080", "file_name": "物业管理服务方案", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-081", "file_name": "设计策划书", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-082", "file_name": "设计输入要求", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-083", "file_name": "设计评审验证记录", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-084", "file_name": "设计确认单", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-085", "file_name": "设计输出清单", "category": "design_dev", "iso_clause": "8.3"},
    ],
    "labor_dispatch": [
        {"file_level": "C", "file_code": "C-010", "file_name": "劳务派遣服务方案编制规范", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "C", "file_code": "C-011", "file_name": "人员招聘与入职管理规程", "category": "hr", "iso_clause": "7.2"},
        {"file_level": "C", "file_code": "C-012", "file_name": "外派员工考核管理规程", "category": "hr", "iso_clause": "9.1"},
        {"file_level": "C", "file_code": "C-013", "file_name": "劳动合同管理规程", "category": "hr", "iso_clause": "7.2"},
        {"file_level": "C", "file_code": "C-014", "file_name": "上岗培训管理规程", "category": "hr", "iso_clause": "7.2"},
        {"file_level": "D", "file_code": "D-077", "file_name": "劳务派遣方案", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-078", "file_name": "人员信息登记表", "category": "hr", "iso_clause": "7.2"},
        {"file_level": "D", "file_code": "D-079", "file_name": "劳务派遣员工上岗通知", "category": "hr", "iso_clause": "7.2"},
        {"file_level": "D", "file_code": "D-080", "file_name": "新员工入职手续办理表", "category": "hr", "iso_clause": "7.2"},
        {"file_level": "D", "file_code": "D-081", "file_name": "外派考核表", "category": "hr", "iso_clause": "9.1"},
        {"file_level": "D", "file_code": "D-082", "file_name": "劳务派遣项目管理标准化考评表", "category": "hr", "iso_clause": "9.1"},
        {"file_level": "D", "file_code": "D-083", "file_name": "就业、劳动合同登记名册", "category": "hr", "iso_clause": "7.2"},
        {"file_level": "D", "file_code": "D-084", "file_name": "入职培训记录表", "category": "hr", "iso_clause": "7.2"},
        {"file_level": "D", "file_code": "D-085", "file_name": "产品设计策划书", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-086", "file_name": "设计输入要求", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-087", "file_name": "设计评审验证记录", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-088", "file_name": "产品设计确认单", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-089", "file_name": "设计输出清单", "category": "design_dev", "iso_clause": "8.3"},
        {"file_level": "D", "file_code": "D-090", "file_name": "方案验收报告单", "category": "design_dev", "iso_clause": "8.3"},
    ],
}


def init_industries(db: Session = None):
    """初始化行业配置
    
    Args:
        db: 数据库会话，None则自动创建
    """
    if db is None:
        db = next(get_db())
    
    print("开始初始化行业配置...")
    
    # 清空现有数据（可选，用于重新初始化）
    # db.query(IndustrySpecialFile).delete()
    # db.query(IndustryConfig).delete()
    # db.commit()
    
    created_count = 0
    
    for config_data in INDUSTRY_CONFIGS:
        industry_code = config_data["industry_code"]
        
        # 检查是否已存在
        existing = db.query(IndustryConfig).filter(
            IndustryConfig.industry_code == industry_code
        ).first()
        
        if existing:
            print(f"  行业已存在，跳过: {industry_code}")
            continue
        
        # 创建行业配置
        industry = IndustryConfig(**config_data)
        db.add(industry)
        db.flush()  # 获取ID
        
        # 创建行业特有文件
        special_files = INDUSTRY_SPECIAL_FILES.get(industry_code, [])
        for idx, file_data in enumerate(special_files):
            special_file = IndustrySpecialFile(
                industry_id=industry.id,
                sort_order=idx,
                **file_data
            )
            db.add(special_file)
        
        created_count += 1
        print(f"  创建行业: {industry_code} ({config_data['industry_name']}) - {len(special_files)}个特有文件")
    
    db.commit()
    print(f"\n行业初始化完成！共创建 {created_count} 个行业配置。")
    
    return created_count


def get_industry_stats(db: Session = None):
    """获取行业统计信息"""
    if db is None:
        db = next(get_db())
    
    industries = db.query(IndustryConfig).all()
    
    stats = []
    for industry in industries:
        file_count = db.query(IndustrySpecialFile).filter(
            IndustrySpecialFile.industry_id == industry.id
        ).count()
        
        stats.append({
            "industry_code": industry.industry_code,
            "industry_name": industry.industry_name,
            "special_file_count": file_count,
            "has_design_development": industry.has_design_development,
            "has_equipment_operations": industry.has_equipment_operations,
        })
    
    return stats


if __name__ == "__main__":
    # 直接运行初始化
    init_db()
    count = init_industries()
    
    if count > 0:
        print("\n行业统计:")
        stats = get_industry_stats()
        for stat in stats:
            print(f"  {stat['industry_name']}: {stat['special_file_count']}个特有文件")
