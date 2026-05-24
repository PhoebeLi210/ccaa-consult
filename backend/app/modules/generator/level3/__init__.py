# -*- coding: utf-8 -*-
"""三级文件生成器 - 作业指导书和制度"""

from .level3_generator import (
    # 基类
    BaseLevel3Generator,
    RegulationGenerator,
    BaseOperationGenerator,
    # 管理制度生成器（15个）
    InspectionEquipmentManagementGenerator,
    FireSafetyManagementGenerator,
    SafetyProductionManagementGenerator,
    EquipmentManagementGenerator,
    WarehouseManagementGenerator,
    ChemicalManagementGenerator,
    LaborProtectionManagementGenerator,
    TrainingManagementGenerator,
    FileArchiveManagementGenerator,
    MeetingManagementGenerator,
    HygieneManagementGenerator,
    EnergySavingManagementGenerator,
    EnvironmentalProtectionManagementGenerator,
    OccupationalHealthManagementGenerator,
    EmergencyPlanManagementGenerator,
    # 设备操作规程生成器（10个）
    ComputerOperationGenerator,
    AirConditionerOperationGenerator,
    PrinterOperationGenerator,
    CopierOperationGenerator,
    ProjectorOperationGenerator,
    ShredderOperationGenerator,
    WaterDispenserOperationGenerator,
    FireEquipmentOperationGenerator,
    FirstAidEquipmentOperationGenerator,
    SecurityMonitorOperationGenerator,
    # 工厂函数
    generate_regulation,
    generate_operation,
    generate_all_regulations,
    generate_all_operations,
    generate_all_level3_documents,
)

__all__ = [
    # 基类
    'BaseLevel3Generator',
    'RegulationGenerator',
    'BaseOperationGenerator',
    # 管理制度生成器
    'InspectionEquipmentManagementGenerator',
    'FireSafetyManagementGenerator',
    'SafetyProductionManagementGenerator',
    'EquipmentManagementGenerator',
    'WarehouseManagementGenerator',
    'ChemicalManagementGenerator',
    'LaborProtectionManagementGenerator',
    'TrainingManagementGenerator',
    'FileArchiveManagementGenerator',
    'MeetingManagementGenerator',
    'HygieneManagementGenerator',
    'EnergySavingManagementGenerator',
    'EnvironmentalProtectionManagementGenerator',
    'OccupationalHealthManagementGenerator',
    'EmergencyPlanManagementGenerator',
    # 操作规程生成器
    'ComputerOperationGenerator',
    'AirConditionerOperationGenerator',
    'PrinterOperationGenerator',
    'CopierOperationGenerator',
    'ProjectorOperationGenerator',
    'ShredderOperationGenerator',
    'WaterDispenserOperationGenerator',
    'FireEquipmentOperationGenerator',
    'FirstAidEquipmentOperationGenerator',
    'SecurityMonitorOperationGenerator',
    # 工厂函数
    'generate_regulation',
    'generate_operation',
    'generate_all_regulations',
    'generate_all_operations',
    'generate_all_level3_documents',
]
