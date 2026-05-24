#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三级文件生成器 - 作业指导书和制度

三级文件分为两类：
1. 管理制度（{company_code}-QESMS-C-001 ~ C-015）
2. 设备操作规程（{company_code}-QESMS-C-016 ~ C-025）

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
        # 三级文件编号：企业缩写-QESMS-C-编号（如 BDC-QESMS-C-001）
        file_code = self.get_level3_file_code(self.file_code)
        
        template = f"""
# {{公司名称}} {self.file_name}

**文件编号**：{file_code}

**版本**：A/0

**生效日期**：{{生效日期}}

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


# ============================================================
# 管理制度类（15个）
# ============================================================

class InspectionEquipmentManagementGenerator(RegulationGenerator):
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

7.2 综合管理部编制《设备维护保养计划》（{company_code}-022），定期组织设备保养。

7.3 设备故障时应及时报修，填写《设备维保记录》（{company_code}-021）。

## 第八条 设备检定

8.1 综合管理部编制《计量器具周期检定计划》（{company_code}-024）。

8.2 强制检定设备必须按期送检，取得检定证书。

8.3 非强制检定设备应进行自检或送检，确保量值准确。

## 第九条 设备报废

9.1 设备损坏或技术落后无法使用时，应申请报废。

9.2 报废设备应填写《设备报废申请单》（{company_code}-020）。

9.3 报废设备应从台账中注销。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class FireSafetyManagementGenerator(RegulationGenerator):
    """C-002 消防管理制度"""
    
    @property
    def file_name(self) -> str:
        return "消防管理制度"
    
    @property
    def file_code(self) -> int:
        return 2
    
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

6.3 检查结果记录于《安全运行检查记录》（{company_code}-040）。

## 第七条 消防演练

7.1 公司每年至少组织一次消防演练。

7.2 演练内容包括：
- 报警和疏散
- 灭火器使用
- 人员救护

7.3 演练记录归档保存。

## 第八条 火灾应急

8.1 发生火灾时，发现人员应立即报警并扑救初期火灾。

8.2 火灾应急预案详见《火灾应急预案及演练》（{company_code}-041）。

## 第九条 考核与奖惩

9.1 对违反消防管理制度的行为，视情节给予批评教育或处罚。

9.2 对防止火灾事故发生或扑救火灾的有功人员给予奖励。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class SafetyProductionManagementGenerator(RegulationGenerator):
    """C-003 安全生产管理制度"""
    
    @property
    def file_name(self) -> str:
        return "安全生产管理制度"
    
    @property
    def file_code(self) -> int:
        return 3
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为加强安全生产管理，预防和减少生产安全事故，保障员工生命安全和公司财产安全，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有生产经营活动的安全管理。

## 第三条 安全生产方针

公司安全生产方针：安全第一、预防为主、综合治理。

## 第四条 组织保障

4.1 公司成立安全生产领导小组，由公司主要负责人担任组长。

4.2 各部门负责人为本部门安全生产第一责任人。

4.3 设专职或兼职安全管理人员，负责日常安全管理工作。

## 第五条 安全教育培训

5.1 新员工入职必须接受三级安全教育（公司级、部门级、班组级）。

5.2 特种作业人员必须持证上岗，定期参加复审培训。

5.3 转岗、复工人员必须接受岗位安全培训。

5.4 安全培训记录归档保存。

## 第六条 安全检查

6.1 公司每月组织一次综合性安全检查。

6.2 各部门每周进行一次安全自查。

6.3 班组每日进行班前安全检查。

6.4 检查发现的问题应及时整改，并做好记录。

## 第七条 危险作业管理

7.1 高处作业、动火作业、有限空间作业等危险作业必须办理审批手续。

7.2 危险作业前必须进行风险评估，制定安全措施。

7.3 危险作业现场必须有专人监护。

## 第八条 劳动防护

8.1 公司按规定为员工配备劳动防护用品。

8.2 员工必须正确佩戴和使用劳动防护用品。

8.3 劳动防护用品应定期检查、更换。

## 第九条 事故管理

9.1 发生事故后，应立即报告并组织救援。

9.2 事故调查应坚持"四不放过"原则。

9.3 事故处理结果应记录归档。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class EquipmentManagementGenerator(RegulationGenerator):
    """C-004 设备管理制度"""
    
    @property
    def file_name(self) -> str:
        return "设备管理制度"
    
    @property
    def file_code(self) -> int:
        return 4
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为规范公司设备管理，确保设备安全、高效运行，延长设备使用寿命，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有设备的管理，包括办公设备、生产设备、辅助设备等。

## 第三条 职责

**综合管理部**职责：
- 设备采购审批
- 设备台账管理
- 设备报废审核
- 设备档案管理

**使用部门**职责：
- 设备日常使用
- 设备日常维护
- 设备故障报修

## 第四条 设备采购

4.1 设备采购应编制采购计划，明确技术要求和预算。

4.2 采购设备应选择合格供应商，签订采购合同。

4.3 设备到货后应组织验收，验收合格方可入库。

## 第五条 设备验收

5.1 验收内容包括：外观检查、技术参数核对、功能测试。

5.2 验收合格后，填写《设备验收单》，建立设备档案。

5.3 验收不合格的设备，应及时联系供应商处理。

## 第六条 设备使用

6.1 设备使用人员应经过培训，熟悉设备操作规程。

6.2 重要设备应实行定人、定机操作。

6.3 设备使用应做好运行记录。

## 第七条 设备维护保养

7.1 设备维护保养分为日常保养、定期保养和专项保养。

7.2 使用部门负责设备日常保养，保持设备清洁、润滑。

7.3 综合管理部编制《设备维护保养计划》，组织定期保养。

7.4 维护保养应做好记录，归档保存。

## 第八条 设备维修

8.1 设备故障时，应及时报修，填写《设备维修申请单》。

8.2 设备维修应由专业人员或厂家进行。

8.3 维修完成后应进行验收，做好维修记录。

## 第九条 设备报废

9.1 符合以下条件之一的设备可申请报废：
- 超过使用年限，无法修复
- 技术落后，无使用价值
- 损坏严重，维修成本过高

9.2 设备报废应填写《设备报废申请单》，经审批后执行。

9.3 报废设备应从台账中注销，妥善处理。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class WarehouseManagementGenerator(RegulationGenerator):
    """C-005 仓库管理制度"""
    
    @property
    def file_name(self) -> str:
        return "仓库管理制度"
    
    @property
    def file_code(self) -> int:
        return 5
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为规范仓库管理，确保物资安全、账物相符，提高物资周转效率，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有仓库的管理，包括原材料库、成品库、备品备件库等。

## 第三条 职责

**仓库管理员**职责：
- 物资出入库管理
- 库存盘点
- 仓库日常管理
- 账务处理

**采购部门**职责：
- 物资采购
- 入库验收配合

**使用部门**职责：
- 物资领用申请
- 物资使用管理

## 第四条 入库管理

4.1 物资到货后，仓库管理员应核对送货单与采购订单。

4.2 组织验收，检查物资数量、质量、规格是否符合要求。

4.3 验收合格后，办理入库手续，填写《入库单》。

4.4 入库物资应分类存放，标识清晰。

## 第五条 出库管理

5.1 物资出库应凭《领料单》或《出库单》办理。

5.2 出库物资应遵循"先进先出"原则。

5.3 出库时应核对数量、规格，确认无误后方可放行。

5.4 出库后应及时更新库存台账。

## 第六条 库存管理

6.1 仓库应建立库存台账，做到账物相符。

6.2 定期进行库存盘点，每月小盘，每年大盘。

6.3 盘点差异应查明原因，按规定处理。

6.4 库存物资应合理储备，避免积压或短缺。

## 第七条 仓库环境管理

7.1 仓库应保持整洁、干燥、通风。

7.2 物资应分类存放，标识清晰，堆放整齐。

7.3 仓库应配备消防器材，定期检查。

7.4 仓库内严禁吸烟、动火。

## 第八条 安全管理

8.1 仓库应实行封闭管理，非工作人员不得入内。

8.2 危险化学品应单独存放，专人管理。

8.3 仓库应定期进行安全检查，消除隐患。

## 第九条 账务管理

9.1 仓库应建立健全账务管理制度。

9.2 出入库单据应妥善保管，定期归档。

9.3 库存报表应定期编制，及时上报。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class ChemicalManagementGenerator(RegulationGenerator):
    """C-006 化学品管理制度"""
    
    @property
    def file_name(self) -> str:
        return "化学品管理制度"
    
    @property
    def file_code(self) -> int:
        return 6
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为规范公司化学品管理，预防化学品事故，保障员工健康和环境安全，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有化学品的管理，包括易燃易爆品、腐蚀品、毒害品等。

## 第三条 职责

**综合管理部**职责：
- 化学品采购审批
- 化学品安全培训
- 化学品应急演练
- 监督检查

**使用部门**职责：
- 化学品使用管理
- 安全操作执行
- 废弃物处理

## 第四条 化学品采购

4.1 化学品采购应选择具有资质的供应商。

4.2 采购时应索取化学品安全技术说明书（MSDS）。

4.3 化学品包装应完好，标识清晰。

## 第五条 化学品验收

5.1 化学品到货后，应核对品名、数量、规格。

5.2 检查包装是否完好，标识是否清晰。

5.3 查验MSDS，了解化学品危险特性。

5.4 验收合格后，办理入库手续。

## 第六条 化学品储存

6.1 化学品应分类存放，禁忌物品不得混放。

6.2 储存场所应通风良好，配备消防器材。

6.3 化学品应标识清晰，建立台账。

6.4 易制毒、易制爆化学品应单独存放，专人管理。

## 第七条 化学品使用

7.1 使用化学品前应了解其危险特性。

7.2 使用时应佩戴相应的劳动防护用品。

7.3 使用场所应通风良好，配备应急设施。

7.4 使用过程中应做好记录。

## 第八条 化学品废弃

8.1 化学品废弃物应分类收集，不得随意丢弃。

8.2 危险化学品废弃物应委托有资质单位处理。

8.3 废弃处理应做好记录，保存凭证。

## 第九条 应急处置

9.1 发生化学品泄漏时，应立即启动应急预案。

9.2 泄漏处置应佩戴防护用品，采取有效措施。

9.3 应急处置后应做好记录，分析原因。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class LaborProtectionManagementGenerator(RegulationGenerator):
    """C-007 劳动防护用品管理制度"""
    
    @property
    def file_name(self) -> str:
        return "劳动防护用品管理制度"
    
    @property
    def file_code(self) -> int:
        return 7
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为规范公司劳动防护用品管理，保障员工在生产过程中的安全与健康，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有员工劳动防护用品的采购、发放、使用、维护和报废管理。

## 第三条 职责

**综合管理部**职责：
- 劳动防护用品采购
- 发放标准制定
- 使用情况监督

**各部门**职责：
- 领用申请
- 日常使用管理
- 损坏更换申请

## 第四条 防护用品分类

4.1 头部防护：安全帽、工作帽等。

4.2 眼面部防护：护目镜、面罩等。

4.3 呼吸防护：防尘口罩、防毒面具等。

4.4 听力防护：耳塞、耳罩等。

4.5 手部防护：防护手套等。

4.6 足部防护：安全鞋、防护鞋等。

4.7 身体防护：工作服、防护服等。

4.8 坠落防护：安全带、安全绳等。

## 第五条 采购管理

5.1 劳动防护用品应选择具有生产资质的厂家。

5.2 采购产品应符合国家或行业标准。

5.3 特种劳动防护用品应具有安全标志证书。

## 第六条 发放管理

6.1 根据岗位特点确定防护用品配备标准。

6.2 按规定周期发放，建立发放台账。

6.3 员工领用时应签字确认。

## 第七条 使用管理

7.1 员工应正确佩戴和使用劳动防护用品。

7.2 不得擅自拆除、改装防护用品。

7.3 发现防护用品损坏应及时更换。

## 第八条 维护保养

8.1 劳动防护用品应定期清洁、维护。

8.2 存放应避免阳光直射、潮湿、腐蚀。

8.3 特种防护用品应定期检验。

## 第九条 报废管理

9.1 符合以下条件之一的防护用品应报废：
- 超过使用期限
- 损坏无法修复
- 防护性能失效

9.2 报废的防护用品应及时更换。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class TrainingManagementGenerator(RegulationGenerator):
    """C-008 培训管理制度"""
    
    @property
    def file_name(self) -> str:
        return "培训管理制度"
    
    @property
    def file_code(self) -> int:
        return 8
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为规范公司培训管理，提高员工素质和能力，满足公司发展需要，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有员工的培训管理。

## 第三条 职责

**综合管理部**职责：
- 制定年度培训计划
- 组织实施培训
- 培训效果评估
- 培训档案管理

**各部门**职责：
- 提出培训需求
- 配合培训实施
- 部门内部培训

## 第四条 培训类别

4.1 新员工培训：公司概况、规章制度、安全教育等。

4.2 岗位培训：岗位技能、操作规程、专业知识等。

4.3 管理培训：管理知识、领导能力、团队建设等。

4.4 专项培训：质量、环境、安全等专项培训。

4.5 外派培训：外部培训机构培训、考察学习等。

## 第五条 培训计划

5.1 每年初制定年度培训计划，明确培训内容、对象、时间、方式。

5.2 培训计划应经审批后实施。

5.3 培训计划可根据实际情况调整。

## 第六条 培训实施

6.1 培训前应做好准备工作，包括教材、场地、讲师等。

6.2 培训过程中应做好签到、记录。

6.3 培训结束后应进行考核或评估。

## 第七条 培训考核

7.1 培训后应进行考核，检验培训效果。

7.2 考核方式包括笔试、实操、问答等。

7.3 考核结果应记录归档。

## 第八条 培训效果评估

8.1 培训后应进行效果评估。

8.2 评估内容包括培训满意度、知识掌握程度、工作改善情况。

8.3 评估结果作为改进培训工作的依据。

## 第九条 培训档案

9.1 建立员工培训档案，记录培训经历。

9.2 培训档案包括培训记录、考核成绩、证书等。

9.3 培训档案应妥善保管。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class FileArchiveManagementGenerator(RegulationGenerator):
    """C-009 文件档案管理制度"""
    
    @property
    def file_name(self) -> str:
        return "文件档案管理制度"
    
    @property
    def file_code(self) -> int:
        return 9
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为规范公司文件档案管理，确保文件档案的完整、安全、有效利用，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有文件档案的管理，包括文书档案、技术档案、财务档案、人事档案等。

## 第三条 职责

**综合管理部**职责：
- 制定档案管理制度
- 档案集中管理
- 档案借阅服务
- 档案鉴定销毁

**各部门**职责：
- 本部门文件整理
- 文件归档移交
- 档案利用配合

## 第四条 文件归档范围

4.1 公司正式发文：决定、通知、通报等。

4.2 合同协议：各类合同、协议书等。

4.3 证照资质：营业执照、资质证书等。

4.4 财务资料：财务报表、凭证、账簿等。

4.5 人事资料：员工档案、劳动合同等。

4.6 技术资料：图纸、工艺文件等。

4.7 会议资料：会议记录、决议等。

## 第五条 归档要求

5.1 文件办理完毕后应及时归档。

5.2 归档文件应完整、准确、系统。

5.3 电子文件应与纸质文件同步归档。

5.4 归档时应填写《文件归档清单》。

## 第六条 档案保管

6.1 档案室应保持适宜的温度、湿度。

6.2 档案应分类存放，标识清晰。

6.3 档案室应配备消防、防盗设施。

6.4 定期检查档案保管状况。

## 第七条 档案借阅

7.1 借阅档案应办理借阅手续。

7.2 借阅档案应妥善保管，不得涂改、损毁。

7.3 借阅期限一般不超过一周，逾期应办理续借。

7.4 机密档案借阅应经审批。

## 第八条 档案保密

8.1 档案管理人员应严格遵守保密规定。

8.2 机密档案应单独存放，专人管理。

8.3 不得擅自复制、外传机密档案。

## 第九条 档案销毁

9.1 超过保管期限的档案应进行鉴定。

9.2 确无保存价值的档案可销毁。

9.3 销毁档案应编制销毁清册，经审批后执行。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class MeetingManagementGenerator(RegulationGenerator):
    """C-010 会议管理制度"""
    
    @property
    def file_name(self) -> str:
        return "会议管理制度"
    
    @property
    def file_code(self) -> int:
        return 10
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为规范公司会议管理，提高会议效率，确保会议决议的有效执行，特制定本制度。

## 第二条 适用范围

本制度适用于公司各类会议的组织和管理。

## 第三条 会议分类

3.1 公司级会议：股东会、董事会、总经理办公会等。

3.2 部门会议：部门例会、专题会议等。

3.3 专项会议：质量分析会、安全例会、培训会议等。

## 第四条 会议组织

4.1 会议组织者应提前确定会议主题、时间、地点、参会人员。

4.2 会议通知应提前发送，明确会议议程。

4.3 会议材料应提前准备，确保参会人员知悉。

## 第五条 会议准备

5.1 会议组织者应提前布置会场，检查设备。

5.2 参会人员应准时参会，做好参会准备。

5.3 会议记录人员应提前到位。

## 第六条 会议纪律

6.1 参会人员应准时参会，不得迟到、早退。

6.2 会议期间应将手机调至静音或关机。

6.3 发言应围绕主题，简明扼要。

6.4 会议期间不得随意进出、交头接耳。

## 第七条 会议记录

7.1 重要会议应做好会议记录。

7.2 会议记录应准确、完整。

7.3 会议记录应及时整理、归档。

## 第八条 会议决议执行

8.1 会议决议应明确责任人、完成时限。

8.2 责任部门应按时完成决议事项。

8.3 综合管理部应跟踪决议执行情况。

## 第九条 会议费用

9.1 会议费用应纳入预算管理。

9.2 会议费用应合理控制，厉行节约。

9.3 会议费用报销应提供相关凭证。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class HygieneManagementGenerator(RegulationGenerator):
    """C-011 卫生管理制度"""
    
    @property
    def file_name(self) -> str:
        return "卫生管理制度"
    
    @property
    def file_code(self) -> int:
        return 11
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为改善公司环境卫生状况，保障员工身体健康，树立良好企业形象，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有区域的卫生管理。

## 第三条 职责

**综合管理部**职责：
- 制定卫生管理制度
- 组织卫生检查
- 卫生设施维护

**各部门**职责：
- 本部门区域卫生
- 卫生值日安排
- 卫生问题整改

## 第四条 办公区域卫生

4.1 办公区域应保持整洁，物品摆放有序。

4.2 桌面应保持清洁，文件资料分类存放。

4.3 地面应保持干净，无垃圾、污渍。

4.4 门窗应保持清洁，玻璃明亮。

## 第五条 公共区域卫生

5.1 走廊、楼梯应保持清洁畅通。

5.2 卫生间应保持清洁，定期消毒。

5.3 茶水间应保持整洁，设备完好。

5.4 会议室使用后应及时清理。

## 第六条 垃圾处理

6.1 垃圾应分类投放。

6.2 垃圾桶应定期清理，保持清洁。

6.3 有害垃圾应按规定处理。

## 第七条 绿化环境

7.1 办公区域应适当绿化。

7.2 绿化植物应定期养护。

7.3 不得在办公区域种植违规植物。

## 第八条 卫生检查

8.1 综合管理部每周组织一次卫生检查。

8.2 检查结果应记录并公布。

8.3 卫生不达标的部门应限期整改。

## 第九条 卫生奖惩

9.1 卫生评比优秀的部门给予表扬或奖励。

9.2 卫生不达标的部门给予批评或处罚。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class EnergySavingManagementGenerator(RegulationGenerator):
    """C-012 节能管理制度"""
    
    @property
    def file_name(self) -> str:
        return "节能管理制度"
    
    @property
    def file_code(self) -> int:
        return 12
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为加强公司节能管理，降低能源消耗，提高能源利用效率，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有能源的使用和管理。

## 第三条 节能原则

3.1 节约优先，效率为本。

3.2 全员参与，持续改进。

3.3 科学管理，技术进步。

## 第四条 职责

**综合管理部**职责：
- 制定节能管理制度
- 编制节能计划
- 能源统计分析
- 节能检查考核

**各部门**职责：
- 执行节能制度
- 节能措施落实
- 能源消耗统计

## 第五条 用电管理

5.1 合理使用空调，夏季温度不低于26℃，冬季不高于20℃。

5.2 照明应充分利用自然光，人走灯灭。

5.3 办公设备应设置节能模式，下班关闭电源。

5.4 禁止使用大功率电器。

## 第六条 用水管理

6.1 加强用水设备维护，杜绝跑、冒、滴、漏。

6.2 培养节水习惯，随手关闭水龙头。

6.3 鼓励循环用水，一水多用。

## 第七条 办公用品管理

7.1 推行无纸化办公，减少纸张使用。

7.2 纸张应双面打印、复印。

7.3 办公用品应合理使用，避免浪费。

## 第八条 节能检查

8.1 综合管理部每月进行一次节能检查。

8.2 检查内容包括：用电、用水、办公用品使用情况。

8.3 发现浪费现象应及时纠正。

## 第九条 节能考核

9.1 将节能指标纳入部门考核。

9.2 对节能成效显著的部门和个人给予奖励。

9.3 对浪费能源的行为给予批评或处罚。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class EnvironmentalProtectionManagementGenerator(RegulationGenerator):
    """C-013 环境保护管理制度"""
    
    @property
    def file_name(self) -> str:
        return "环境保护管理制度"
    
    @property
    def file_code(self) -> int:
        return 13
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为加强公司环境保护管理，防治污染，保护生态环境，履行社会责任，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有生产经营活动中的环境管理。

## 第三条 环境方针

公司环境方针：遵守法规、预防污染、节能降耗、持续改进。

## 第四条 职责

**综合管理部**职责：
- 制定环境管理制度
- 环境因素识别评价
- 环境监测管理
- 环保培训教育

**各部门**职责：
- 执行环保制度
- 污染防治措施落实
- 环保设施运行维护

## 第五条 污染防治

5.1 废水管理：
- 生产废水应处理达标后排放
- 生活污水应排入市政管网
- 禁止私设排污口

5.2 废气管理：
- 废气应处理后达标排放
- 定期检测废气排放情况

5.3 噪声管理：
- 控制噪声源，采取降噪措施
- 厂界噪声应符合标准

5.4 固废管理：
- 固废应分类收集、妥善处置
- 危险废物应委托有资质单位处理

## 第六条 环境监测

6.1 定期进行环境监测，掌握污染排放情况。

6.2 监测数据应记录保存。

6.3 发现超标应及时整改。

## 第七条 环境应急

7.1 制定环境应急预案，配备应急物资。

7.2 定期开展环境应急演练。

7.3 发生环境事故应立即启动应急预案。

## 第八条 环保培训

8.1 开展环保法律法规培训。

8.2 提高员工环保意识。

8.3 培训记录应归档保存。

## 第九条 合规性评价

9.1 定期进行环保合规性评价。

9.2 识别并获取适用的环保法律法规。

9.3 确保公司活动符合法规要求。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class OccupationalHealthManagementGenerator(RegulationGenerator):
    """C-014 职业健康管理制度"""
    
    @property
    def file_name(self) -> str:
        return "职业健康管理制度"
    
    @property
    def file_code(self) -> int:
        return 14
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为预防、控制和消除职业病危害，保护员工健康，特制定本制度。

## 第二条 适用范围

本制度适用于公司所有员工的职业健康管理。

## 第三条 职责

**综合管理部**职责：
- 职业健康管理制度制定
- 职业健康检查组织
- 职业健康档案管理
- 职业病危害因素检测

**各部门**职责：
- 职业危害防护措施落实
- 员工健康监护配合
- 职业健康培训

## 第四条 职业病危害因素识别

4.1 识别工作场所存在的职业病危害因素。

4.2 建立职业病危害因素台账。

4.3 对职业病危害因素进行评价和控制。

## 第五条 职业健康检查

5.1 组织从事职业病危害作业的员工进行上岗前、在岗期间、离岗时职业健康检查。

5.2 检查结果应告知员工本人。

5.3 建立员工职业健康监护档案。

## 第六条 职业病危害防护

6.1 采取工程技术措施，消除或降低职业病危害。

6.2 为员工配备符合标准的劳动防护用品。

6.3 在职业病危害作业场所设置警示标识。

## 第七条 作业场所管理

7.1 保持作业场所整洁、通风。

7.2 定期检测职业病危害因素。

7.3 职业病危害因素浓度（强度）应符合国家标准。

## 第八条 职业健康培训

8.1 对员工进行职业健康培训。

8.2 培训内容包括：职业病危害知识、防护措施、急救知识等。

8.3 培训记录应归档保存。

## 第九条 职业病诊断与报告

9.1 对疑似职业病员工应及时安排诊断。

9.2 确诊职业病应按规定报告。

9.3 安排职业病员工进行治疗和康复。

## 第十条 附则

本制度由综合管理部负责解释，自发布之日起施行。"""


class EmergencyPlanManagementGenerator(RegulationGenerator):
    """C-015 应急预案管理制度"""
    
    @property
    def file_name(self) -> str:
        return "应急预案管理制度"
    
    @property
    def file_code(self) -> int:
        return 15
    
    def _get_content(self) -> str:
        return """## 第一条 目的

为规范公司应急预案管理，提高应急处置能力，预防和减少事故损失，特制定本制度。

## 第二条 适用范围

本制度适用于公司各类应急预案的编制、评审、发布、培训、演练和修订管理。

## 第三条 职责

**综合管理部**职责：
- 应急预案编制组织
- 应急预案评审
- 应急演练组织
- 应急预案备案

**各部门**职责：
- 参与应急预案编制
- 应急预案执行
- 应急演练配合

## 第四条 应急预案分类

4.1 综合应急预案：公司总体应急预案。

4.2 专项应急预案：火灾、泄漏、自然灾害等专项预案。

4.3 现场处置方案：重点岗位现场处置方案。

## 第五条 应急预案编制

5.1 应急预案应结合公司实际情况编制。

5.2 应急预案内容应包括：应急组织、职责分工、处置程序、保障措施等。

5.3 应急预案应符合国家相关标准和规范。

## 第六条 应急预案评审

6.1 应急预案编制完成后应组织评审。

6.2 评审人员应包括公司领导、部门负责人、专业人员等。

6.3 评审意见应记录并修改完善预案。

## 第七条 应急预案发布

7.1 应急预案经批准后发布实施。

7.2 应急预案应发放到相关部门和人员。

7.3 涉及重大危险源的应急预案应向主管部门备案。

## 第八条 应急培训

8.1 组织员工学习应急预案。

8.2 使员工熟悉应急职责和处置程序。

8.3 培训记录应归档保存。

## 第九条 应急演练

9.1 每年至少组织一次综合应急演练。

9.2 专项应急预案应定期组织演练。

9.3 演练后应进行评估，改进预案。

## 第十条 应急预案修订

10.1 发生以下情况应及时修订应急预案：
- 法律法规变化
- 公司情况变化
- 演练发现问题
- 事故教训

10.2 修订后的应急预案应重新评审发布。

## 第十一条 附则

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
        # 三级文件编号：企业缩写-QESMS-C-编号（如 BDC-QESMS-C-016）
        file_code = self.get_level3_file_code(self.file_code)
        
        template = f"""
# {{公司名称}} {self.file_name}

**文件编号**：{file_code}

**版本**：A/0

**生效日期**：{{生效日期}}

---

## 目的

制定本规程的目的是规范{self.equipment_name}的操作，确保设备安全运行，防止事故发生。

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


# ============================================================
# 设备操作规程类（10个）
# ============================================================

class ComputerOperationGenerator(BaseOperationGenerator):
    """C-016 电脑操作规程"""
    
    @property
    def file_name(self) -> str:
        return "电脑操作规程"
    
    @property
    def file_code(self) -> int:
        return 16
    
    def _get_operation_steps(self) -> str:
        return """## 二、工作过程中的安全注意事项

1. 保持正确的坐姿，眼睛与屏幕保持适当距离（约50-70厘米）。
2. 避免长时间连续使用，每工作1-2小时应休息10-15分钟。
3. 不得随意安装未经授权的软件。
4. 定期备份重要数据，防止数据丢失。
5. 使用正版杀毒软件，定期更新病毒库。
6. 离开时应锁定屏幕或关机，防止信息泄露。
7. 严禁访问非法网站，防止病毒感染。
8. 不得将公司数据外泄，遵守保密规定。
9. 使用U盘等移动存储设备前应进行病毒扫描。
10. 发现电脑异常应及时报告IT部门处理。"""


class AirConditionerOperationGenerator(BaseOperationGenerator):
    """C-017 空调操作规程"""
    
    @property
    def file_name(self) -> str:
        return "空调操作规程"
    
    @property
    def file_code(self) -> int:
        return 17
    
    def _get_operation_steps(self) -> str:
        return """## 二、工作过程中的安全注意事项

1. 设置适宜的温度，夏季不低于26℃，冬季不高于20℃。
2. 定期清洁空调滤网，保持空气流通，建议每月清洁一次。
3. 禁止在空调运行状态下打开机器外壳或进行维修。
4. 发现异常声音或气味应立即关闭空调并报告。
5. 雷雨天气应关闭空调，切断电源，防止雷击损坏。
6. 长时间不使用时应拔掉电源插头，节约能源。
7. 空调运行时应关闭门窗，提高制冷/制热效率。
8. 出风口不应直接对着人员吹，防止感冒。
9. 定期检查空调排水管，防止堵塞漏水。
10. 空调出现故障应由专业人员维修，禁止自行拆卸。"""


class PrinterOperationGenerator(BaseOperationGenerator):
    """C-018 打印机操作规程"""
    
    @property
    def file_name(self) -> str:
        return "打印机操作规程"
    
    @property
    def file_code(self) -> int:
        return 18
    
    def _get_operation_steps(self) -> str:
        return """## 二、工作过程中的安全注意事项

1. 打印时应注意纸张放置方向和数量，避免卡纸。
2. 打印机工作时不要打开机盖，防止高温烫伤。
3. 更换墨盒或硒鼓时应按照说明书操作，避免墨粉污染。
4. 打印机过热时应暂停使用，待冷却后再继续。
5. 不要在打印机上放置杂物，保持通风散热。
6. 使用符合规格的打印纸，避免使用潮湿或折叠的纸张。
7. 打印完成后及时取走文件，防止信息泄露。
8. 发现卡纸时应按照说明取出，禁止硬拉硬拽。
9. 定期清洁打印机内部，保持打印质量。
10. 废旧墨盒、硒鼓应按规定回收处理，不得随意丢弃。"""


class CopierOperationGenerator(BaseOperationGenerator):
    """C-019 复印机操作规程"""
    
    @property
    def file_name(self) -> str:
        return "复印机操作规程"
    
    @property
    def file_code(self) -> int:
        return 19
    
    def _get_operation_steps(self) -> str:
        return """## 二、工作过程中的安全注意事项

1. 复印前应检查原稿是否完整，设置好复印参数。
2. 复印机工作时不要打开机盖，防止强光伤害眼睛。
3. 复印机预热时应等待，不要频繁开关机。
4. 更换墨粉时应戴手套，避免墨粉污染皮肤和衣物。
5. 复印大量文件时应分批进行，避免机器过热。
6. 发现卡纸时应按照指示取出，禁止硬拉硬拽。
7. 复印完成后应及时取走原稿和复印件。
8. 涉及机密文件的复印应遵守保密规定。
9. 定期清洁复印机玻璃面板，保持复印清晰。
10. 废旧墨粉盒应按规定回收处理。"""


class ProjectorOperationGenerator(BaseOperationGenerator):
    """C-020 投影仪操作规程"""
    
    @property
    def file_name(self) -> str:
        return "投影仪操作规程"
    
    @property
    def file_code(self) -> int:
        return 20
    
    def _get_operation_steps(self) -> str:
        return """## 二、工作过程中的安全注意事项

1. 开机前应确认投影仪放置稳定，镜头对准屏幕。
2. 开机后应等待预热，不要立即调整焦距。
3. 使用过程中不要直视投影仪镜头，防止强光伤害眼睛。
4. 投影仪工作时不要移动，防止灯泡损坏。
5. 使用时间不宜过长，一般不超过3小时，防止过热。
6. 关机后应等待风扇停止转动后再切断电源。
7. 定期清洁投影仪滤网，保持散热良好。
8. 更换灯泡时应等待投影仪完全冷却后进行。
9. 投影仪应存放在干燥、通风处，防止受潮。
10. 发现异常应立即关闭电源，联系专业人员维修。"""


class ShredderOperationGenerator(BaseOperationGenerator):
    """C-021 碎纸机操作规程"""
    
    @property
    def file_name(self) -> str:
        return "碎纸机操作规程"
    
    @property
    def file_code(self) -> int:
        return 21
    
    def _get_operation_steps(self) -> str:
        return """## 二、工作过程中的安全注意事项

1. 碎纸时应将纸张平整放入，不要折叠或揉皱。
2. 不要一次放入过多纸张，避免卡纸或电机过载。
3. 碎纸过程中不要将手指伸入进纸口，防止夹伤。
4. 不要将订书钉、回形针等金属物品放入碎纸机。
5. 碎纸机工作时不要打开机盖。
6. 发现卡纸时应先关闭电源，再按照说明清理。
7. 碎纸机连续工作时间不宜过长，应间歇使用。
8. 定期清理碎纸箱，避免碎纸溢出。
9. 碎纸机应放置在平稳处，防止倾倒。
10. 碎纸机出现异常噪音或异味时应停止使用并报告。"""


class WaterDispenserOperationGenerator(BaseOperationGenerator):
    """C-022 饮水机操作规程"""
    
    @property
    def file_name(self) -> str:
        return "饮水机操作规程"
    
    @property
    def file_code(self) -> int:
        return 22
    
    def _get_operation_steps(self) -> str:
        return """## 二、工作过程中的安全注意事项

1. 饮水机应放置在平稳、通风处，避免阳光直射。
2. 换水时应先关闭电源，防止干烧。
3. 饮水机水桶应轻拿轻放，避免碰撞。
4. 定期清洗饮水机内胆，建议每季度清洗一次。
5. 饮水机长时间不使用时应关闭电源并排空存水。
6. 发现饮水机漏水应立即关闭电源并报告。
7. 不要在饮水机上放置杂物，保持清洁。
8. 取用热水时应注意防烫，使用纸杯或自带杯子。
9. 饮水机出现故障应由专业人员维修。
10. 定期更换滤芯，保证饮用水质量。"""


class FireEquipmentOperationGenerator(BaseOperationGenerator):
    """C-023 消防器材操作规程"""
    
    @property
    def file_name(self) -> str:
        return "消防器材操作规程"
    
    @property
    def file_code(self) -> int:
        return 23
    
    def _get_operation_steps(self) -> str:
        return """## 二、工作过程中的安全注意事项

### 灭火器使用方法：

1. 使用前检查灭火器压力表是否在绿色区域。
2. 提起灭火器，拔出保险销。
3. 一手握住喷管，对准火焰根部。
4. 另一手按下压把，左右扫射灭火。
5. 灭火时应站在上风或侧风方向。

### 消防栓使用方法：

1. 打开消防栓箱门，取出水带。
2. 将水带一端连接消防栓，另一端连接水枪。
3. 逆时针打开消防栓阀门。
4. 双手握住水枪，对准火源灭火。
5. 使用完毕后关闭阀门，整理水带归位。

### 注意事项：

1. 消防器材应定期检查，确保完好有效。
2. 灭火器应定期送检，过期及时更换。
3. 非火灾情况不得擅自使用消防器材。
4. 发现消防器材损坏应及时报告。"""


class FirstAidEquipmentOperationGenerator(BaseOperationGenerator):
    """C-024 急救设备操作规程"""
    
    @property
    def file_name(self) -> str:
        return "急救设备操作规程"
    
    @property
    def file_code(self) -> int:
        return 24
    
    def _get_operation_steps(self) -> str:
        return """## 二、工作过程中的安全注意事项

### 急救箱使用：

1. 急救箱应放置在明显、易取的位置。
2. 定期检查急救箱物品，及时补充过期或缺失物品。
3. 使用急救物品后应及时记录使用情况。
4. 急救箱应专人管理，定期检查维护。

### 自动体外除颤器（AED）使用：

1. 发现有人心脏骤停，立即拨打120并取用AED。
2. 打开AED电源，按照语音提示操作。
3. 按图示贴好电极片，确保皮肤干燥。
4. 分析心律时不要触碰患者。
5. 如需除颤，确认无人触碰患者后按下除颤键。
6. 除颤后立即继续心肺复苏。

### 注意事项：

1. 急救设备应定期检查，确保完好可用。
2. 使用急救设备应接受过培训。
3. 急救后应及时补充消耗物品。
4. 急救设备故障应及时报告维修。"""


class SecurityMonitorOperationGenerator(BaseOperationGenerator):
    """C-025 安全监控设备操作规程"""
    
    @property
    def file_name(self) -> str:
        return "安全监控设备操作规程"
    
    @property
    def file_code(self) -> int:
        return 25
    
    def _get_operation_steps(self) -> str:
        return """## 二、工作过程中的安全注意事项

### 监控系统操作：

1. 监控系统应由专人操作管理，非授权人员不得操作。
2. 开机前检查各设备连接是否正常。
3. 登录系统时应输入正确的用户名和密码。
4. 监控画面应定期巡视，发现异常及时报告。
5. 录像资料应按规定保存，不得擅自删除。

### 摄像头维护：

1. 定期清洁摄像头镜头，保持画面清晰。
2. 检查摄像头固定是否牢固，角度是否正确。
3. 发现摄像头故障应及时报修。

### 门禁系统操作：

1. 门禁卡应妥善保管，不得转借他人。
2. 进出门禁区域应刷卡，不得尾随他人进入。
3. 门禁卡丢失应及时报告并注销。
4. 门禁系统故障应及时报修。

### 注意事项：

1. 监控资料涉及隐私，不得外泄或用于非法用途。
2. 监控系统应24小时运行，确保安全。
3. 定期检查系统运行状态，做好维护保养。
4. 发现异常情况应及时报告并做好记录。"""


# ============================================================
# 工厂函数
# ============================================================

def generate_regulation(company_info: CompanyInfo, file_code: int) -> GeneratedDocument:
    """生成指定管理制度"""
    generators = {
        1: InspectionEquipmentManagementGenerator,
        2: FireSafetyManagementGenerator,
        3: SafetyProductionManagementGenerator,
        4: EquipmentManagementGenerator,
        5: WarehouseManagementGenerator,
        6: ChemicalManagementGenerator,
        7: LaborProtectionManagementGenerator,
        8: TrainingManagementGenerator,
        9: FileArchiveManagementGenerator,
        10: MeetingManagementGenerator,
        11: HygieneManagementGenerator,
        12: EnergySavingManagementGenerator,
        13: EnvironmentalProtectionManagementGenerator,
        14: OccupationalHealthManagementGenerator,
        15: EmergencyPlanManagementGenerator,
    }
    
    generator_class = generators.get(file_code)
    if not generator_class:
        raise ValueError(f"未知的制度序号: {file_code}")
    
    generator = generator_class(company_info)
    return generator.generate()


def generate_operation(company_info: CompanyInfo, file_code: int) -> GeneratedDocument:
    """生成指定操作规程"""
    generators = {
        16: ComputerOperationGenerator,
        17: AirConditionerOperationGenerator,
        18: PrinterOperationGenerator,
        19: CopierOperationGenerator,
        20: ProjectorOperationGenerator,
        21: ShredderOperationGenerator,
        22: WaterDispenserOperationGenerator,
        23: FireEquipmentOperationGenerator,
        24: FirstAidEquipmentOperationGenerator,
        25: SecurityMonitorOperationGenerator,
    }
    
    generator_class = generators.get(file_code)
    if not generator_class:
        raise ValueError(f"未知的操作规程序号: {file_code}")
    
    generator = generator_class(company_info)
    return generator.generate()


def generate_all_regulations(company_info: CompanyInfo) -> List[GeneratedDocument]:
    """生成所有管理制度"""
    documents = []
    
    regulation_generators = [
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
    ]
    
    for generator_class in regulation_generators:
        generator = generator_class(company_info)
        documents.append(generator.generate())
    
    return documents


def generate_all_operations(company_info: CompanyInfo) -> List[GeneratedDocument]:
    """生成所有操作规程"""
    documents = []
    
    operation_generators = [
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
    ]
    
    for generator_class in operation_generators:
        generator = generator_class(company_info)
        documents.append(generator.generate())
    
    return documents


def generate_all_level3_documents(company_info: CompanyInfo) -> List[GeneratedDocument]:
    """生成所有三级文件（管理制度+操作规程）"""
    documents = []
    documents.extend(generate_all_regulations(company_info))
    documents.extend(generate_all_operations(company_info))
    return documents


# ============================================================
# 导出类和函数
# ============================================================

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
