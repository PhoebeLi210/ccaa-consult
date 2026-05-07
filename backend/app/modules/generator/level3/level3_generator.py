#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三级文件生成器 - 作业指导书和制度

三级文件分为两类：
1. 管理制度（BDC-QESMS-C-001 ~ C-025）
2. 设备操作规程（BDC-QESMS-C-002 ~ C-019）

每个文件独立生成，便于维护和扩展。
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


class BaseLevel3Generator(BaseGenerator):
    """三级文件生成器基类"""
    
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


# ============================================================
# 管理制度生成器
# ============================================================

class RegulationGenerator(BaseLevel3Generator):
    """管理制度生成器基类"""
    
    def _render_regulation(self, content: str) -> str:
        """渲染制度文件"""
        template = f"""
# {{公司名称}} {{file_name}}

**文件编号**：{{company_code}}-QESMS-C-{self.file_code:03d}

**版本**：A/0

**生效日期**：{{effective_date}}

---

{content}

---

**编制/日期**：
**审核/日期**：
**批准/日期**：
"""
        return self.render(template)
    
    def generate(self) -> GeneratedDocument:
        """生成制度文件"""
        content = self._render_regulation(self._get_content())
        
        return GeneratedDocument(
            file_level=FileLevel.LEVEL_3,
            document_type=DocumentType.REGULATION,
            file_code=self.get_level3_file_code(self.file_code),
            file_name=f"{self.file_name}.docx",
            title=self.file_name,
            content=content,
        )
    
    @abstractmethod
    def _get_content(self) -> str:
        """获取制度内容"""
        pass


class EquipmentManagementGenerator(RegulationGenerator):
    """C-001 检验、计量设备管理制度"""
    
    @property
    def file_name(self) -> str:
        return "检验、计量设备管理制度"
    
    @property
    def file_code(self) -> int:
        return 1
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为规范公司检验、计量设备的管理，确保设备的准确性和可靠性，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有检验、计量设备的管理，包括采购、验收、使用、维护、报废等全过程。

## 第三条 职责

**综合管理部**负责设备的统一管理，包括：
- 编制设备台账
- 制定检定计划
- 组织设备检定
- 设备档案管理

**使用部门**负责设备的日常使用和维护，包括：
- 按规程操作设备
- 日常维护保养
- 异常情况报告

## 第四条 设备采购

4.1 各部门因工作需要添置检验、计量设备时，应提出申请，经审批后采购。

4.2 采购的设备必须具有有效的计量检定证书或出厂合格证。

## 第五条 设备验收

5.1 新购设备到货后，由综合管理部组织验收。

5.2 验收内容包括：外观检查、功能测试、计量检定。

5.3 验收合格后，登记入账，建立设备档案。

## 第六条 设备使用

6.1 使用人员必须经过培训，熟悉设备操作规程后方可上岗。

6.2 使用前应检查设备状态，确保设备正常后方可使用。

6.3 使用过程中应做好记录。

## 第七条 设备维护

7.1 使用部门负责设备的日常维护保养。

7.2 综合管理部编制《设备维护保养计划》（BDC-QESMS-D-022），定期组织设备保养。

7.3 设备故障时应及时报修，填写《设备维保记录》（BDC-QESMS-D-021）。

## 第八条 设备检定

8.1 综合管理部编制《计量器具周期检定计划》（BDC-QESMS-D-024）。

8.2 强制检定设备必须按期送检，取得检定证书。

8.3 非强制检定设备应进行自检或送检，确保量值准确。

## 第九条 设备报废

9.1 设备损坏或技术落后无法使用时，应申请报废。

9.2 报废设备应填写《设备报废申请单》（BDC-QESMS-D-020）。

9.3 报废设备应从台账中注销。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class SafetyRegulationGenerator(RegulationGenerator):
    """C-022 消防管理制度"""
    
    @property
    def file_name(self) -> str:
        return "消防管理制度"
    
    @property
    def file_code(self) -> int:
        return 22
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为预防火灾事故，保障公司财产和员工生命安全，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有区域的消防安全管理。

## 第三条 职责

**综合管理部**职责：
- 制定消防管理制度
- 配置消防器材
- 组织消防检查
- 开展消防培训

**各部门**职责：
- 执行消防制度
- 管理本部门消防器材
- 组织员工参加消防演练

## 第四条 消防设施配置

4.1 公司配置以下消防设施：
- 灭火器（按规范配置）
- 消防栓
- 烟雾探测器
- 应急照明
- 疏散指示标志

4.2 消防设施应定期检查，确保完好有效。

## 第五条 用火用电管理

5.1 严禁私拉乱接电线。

5.2 严禁超负荷用电。

5.3 动火作业必须办理《动火许可证》，采取防护措施。

5.4 禁止在禁烟区吸烟。

## 第六条 消防检查

6.1 综合管理部每月组织一次消防检查。

6.2 检查内容包括：
- 消防设施状态
- 用电安全情况
- 疏散通道畅通情况
- 隐患整改情况

6.3 检查结果记录于《安全运行检查记录》（BDC-QESMS-D-040）。

## 第七条 消防演练

7.1 公司每年至少组织一次消防演练。

7.2 演练内容包括：
- 报警和疏散
- 灭火器使用
- 人员救护

7.3 演练记录归档保存。

## 第八条 火灾应急

8.1 发生火灾时，发现人员应立即报警并扑救初期火灾。

8.2 火灾应急预案详见《火灾应急预案及演练》（BDC-QESMS-D-041）。

## 第九条 考核与奖惩

9.1 对违反消防管理制度的行为，视情节给予批评教育或处罚。

9.2 对防止火灾事故发生或扑救火灾的有功人员给予奖励。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


# ============================================================
# 设备操作规程生成器
# ============================================================

class BaseOperationGenerator(BaseLevel3Generator):
    """设备操作规程生成器基类"""
    
    @property
    def equipment_name(self) -> str:
        """设备名称"""
        return self.file_name.replace("操作规程", "")
    
    def _render_operation(self, content: str) -> str:
        """渲染操作规程"""
        template = f"""
# {{company_name}} {{file_name}}

**文件编号**：{{company_code}}-QESMS-C-{self.file_code:03d}

**版本**：A/0

**生效日期**：{{effective_date}}

---

## 目的

制定本规程的目的是规范{{equipment_name}}的操作，确保设备安全运行，防止事故发生。

## 一、安全操作基本注意事项

1. 操作人员必须经过培训，熟悉设备性能和操作方法后方可上岗。
2. 操作前应检查设备外观是否正常，有无损坏或异常。
3. 严格按照操作规程操作，严禁违章操作。
4. 设备运行过程中，不得擅自离开岗位。
5. 发现异常应立即停机，报告处理。

## 二、工作前的准备工作

1. 检查设备电源线是否完好，有无破损。
2. 检查设备接地是否可靠。
3. 检查设备各部件是否安装牢固。
4. 清洁设备表面，确保无杂物。
5. 接通电源，检查设备是否正常启动。

{content}

## 三、工作完成后的注意事项

1. 关闭设备电源。
2. 清理设备周围的杂物。
3. 对设备进行日常清洁维护。
4. 填写设备使用记录。
5. 如实记录设备运行情况。

## 四、常见问题处理方法

| 问题 | 可能原因 | 处理方法 |
|------|----------|----------|
| 无法启动 | 电源未接通 | 检查电源连接 |
| 异响 | 部件松动 | 停机紧固 |
| 过热 | 连续运行时间过长 | 停机冷却 |

## 五、设备保养维护要求

1. 定期清洁设备表面。
2. 定期检查各部件紧固情况。
3. 定期润滑运动部件。
4. 做好防尘、防潮措施。
5. 维修保养记录归档保存。

---

**编制/日期**：
**审核/日期**：
**批准/日期**：
"""
        return self.render(template)
    
    def generate(self) -> GeneratedDocument:
        """生成操作规程"""
        content = self._render_operation(self._get_operation_steps())
        
        return GeneratedDocument(
            file_level=FileLevel.LEVEL_3,
            document_type=DocumentType.INSTRUCTION,
            file_code=self.get_level3_file_code(self.file_code),
            file_name=f"{self.file_name}.docx",
            title=self.file_name,
            content=content,
        )
    
    @abstractmethod
    def _get_operation_steps(self) -> str:
        """获取操作步骤"""
        pass


class ComputerOperationGenerator(BaseOperationGenerator):
    """C-003 电脑操作规程"""
    
    @property
    def file_name(self) -> str:
        return "电脑操作规程"
    
    @property
    def file_code(self) -> int:
        return 3
    
    def _get_operation_steps(self) -> str:
        return """## 二、工作过程中的安全注意事项

1. 保持正确的坐姿，眼睛与屏幕保持适当距离。
2. 避免长时间连续使用，每工作1-2小时应休息10-15分钟。
3. 不得随意安装未经授权的软件。
4. 定期备份重要数据。
5. 使用正版杀毒软件，定期更新病毒库。
6. 离开时应锁定屏幕或关机。
7. 严禁访问非法网站。
8. 不得将公司数据外泄。"""


class AirConditionerOperationGenerator(BaseOperationGenerator):
    """C-019 空调操作规程"""
    
    @property
    def file_name(self) -> str:
        return "空调操作规程"
    
    @property
    def file_code(self) -> int:
        return 19
    
    def _get_operation_steps(self) -> str:
        return """## 二、工作过程中的安全注意事项

1. 设置适宜的温度，夏季不低于26℃，冬季不高于20℃。
2. 定期清洁空调滤网，保持空气流通。
3. 禁止在空调运行状态下打开机器外壳。
4. 发现异常声音或气味应立即关闭空调。
5. 雷雨天气应关闭空调，切断电源。
6. 长时间不使用时应拔掉电源插头。"""


# ============================================================
# 工厂函数
# ============================================================

def generate_regulation(company_info: CompanyInfo, file_code: int) -> GeneratedDocument:
    """生成指定管理制度"""
    generators = {
        1: EquipmentManagementGenerator,
        22: SafetyRegulationGenerator,
        # 可继续添加
    }
    
    generator_class = generators.get(file_code)
    if not generator_class:
        raise ValueError(f"未知的制度序号: {file_code}")
    
    generator = generator_class(company_info)
    return generator.generate()


def generate_operation(company_info: CompanyInfo, file_code: int) -> GeneratedDocument:
    """生成指定操作规程"""
    generators = {
        3: ComputerOperationGenerator,
        19: AirConditionerOperationGenerator,
        # 可继续添加
    }
    
    generator_class = generators.get(file_code)
    if not generator_class:
        raise ValueError(f"未知的操作规程序号: {file_code}")
    
    generator = generator_class(company_info)
    return generator.generate()
