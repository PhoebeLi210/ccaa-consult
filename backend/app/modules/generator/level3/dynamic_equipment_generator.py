#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态设备操作规程生成器 - V2.1

根据用户输入的设备列表，动态生成对应的设备操作规程。
支持通用设备和自定义设备。
"""

from typing import List, Dict, Optional
from ..base import BaseGenerator, CompanyInfo, GeneratedDocument, FileLevel, DocumentType


# ==================== 设备操作规程模板库 ====================

EQUIPMENT_TEMPLATES = {
    "电脑": {
        "category": "office",
        "steps": """### 开机操作：

1. 检查电源线、显示器连接线是否连接牢固。
2. 打开显示器电源，再打开主机电源。
3. 等待系统启动完成，输入用户名和密码登录。
4. 检查网络连接是否正常。

### 日常使用：

1. 保持正确的坐姿，眼睛与屏幕保持50-70厘米距离。
2. 避免长时间连续使用，每1-2小时休息10-15分钟。
3. 定期保存工作文件，防止数据丢失。
4. 不随意下载和安装不明软件。

### 关机操作：

1. 关闭所有正在运行的应用程序。
2. 通过系统菜单正常关机，严禁直接断电。
3. 关闭显示器电源。
4. 长时间不用时应拔掉电源插头。""",
        "hazards": ["触电", "视力下降", "颈椎劳损"],
        "iso_clause": "7.1",
    },
    "空调": {
        "category": "office",
        "steps": """### 开机操作：

1. 检查电源插头是否插好，遥控器电池是否有电。
2. 用遥控器对准空调接收器，按下开机键。
3. 设置合适的温度（夏季26℃，冬季20℃）。
4. 选择合适的风速和模式。

### 日常使用：

1. 定期清洗过滤网（每月一次）。
2. 保持室内通风，避免长时间密闭使用。
3. 发现异常声音或气味应立即停机检查。
4. 雷雨天气建议关闭空调并拔掉电源。

### 关机操作：

1. 用遥控器关闭空调。
2. 等待几分钟后再关闭电源。
3. 长期不用时应清洁过滤网并盖好防尘罩。""",
        "hazards": ["触电", "高处坠落（清洗时）"],
        "iso_clause": "7.1",
    },
    "打印机": {
        "category": "office",
        "steps": """### 开机操作：

1. 检查电源线、数据线是否连接正常。
2. 确认纸盒内有足够的纸张。
3. 检查墨盒/碳粉盒是否安装正确。
4. 打开电源开关，等待初始化完成。

### 日常使用：

1. 使用符合规格的纸张，避免卡纸。
2. 定期清洁进纸轮和出纸口。
3. 更换耗材时应按照说明书操作。
4. 发现卡纸时应先关闭电源再取出卡纸。

### 关机操作：

1. 等待当前打印任务完成。
2. 关闭电源开关。
3. 长期不用时应盖上防尘罩。""",
        "hazards": ["触电", "粉尘吸入", "高温烫伤"],
        "iso_clause": "7.1",
    },
    "复印机": {
        "category": "office",
        "steps": """### 开机操作：

1. 检查电源线是否连接牢固。
2. 确认纸盒内有足够的纸张。
3. 检查碳粉盒状态。
4. 打开主电源开关，等待预热完成。

### 日常使用：

1. 放置原稿时注意方向和位置。
2. 选择合适的复印参数（份数、缩放、浓淡）。
3. 大批量复印时注意设备散热。
4. 定期清洁扫描玻璃和进纸通道。

### 关机操作：

1. 等待设备进入待机状态。
2. 关闭主电源开关。
3. 清理设备周围的纸张和杂物。""",
        "hazards": ["触电", "强光辐射", "臭氧吸入"],
        "iso_clause": "7.1",
    },
    "投影仪": {
        "category": "office",
        "steps": """### 开机操作：

1. 检查电源线和信号线连接。
2. 打开投影幕布或确保投影墙面平整。
3. 按下电源键，等待灯泡预热。
4. 调整投影角度和焦距。

### 日常使用：

1. 避免频繁开关机，每次间隔至少5分钟。
2. 保持通风良好，不要遮挡散热口。
3. 定期清洁滤网和镜头。
4. 灯泡寿命到期后及时更换。

### 关机操作：

1. 按下关机键，等待散热完成（风扇停止）。
2. 关闭电源开关。
3. 待设备冷却后再移动或收纳。""",
        "hazards": ["触电", "高温烫伤", "强光刺眼"],
        "iso_clause": "7.1",
    },
    "碎纸机": {
        "category": "office",
        "steps": """### 开机操作：

1. 检查电源线是否完好。
2. 确认碎纸桶已安装到位。
3. 检查进纸口是否有异物。
4. 打开电源开关。

### 日常使用：

1. 按照额定容量进纸，不要一次放入过多纸张。
2. 不要碎订书钉、回形针等金属物品。
3. 定期清理碎纸桶，避免过满。
4. 发现卡纸时应先关闭电源再处理。

### 关机操作：

1. 确认所有纸张已碎完。
2. 关闭电源开关。
3. 清空碎纸桶。""",
        "hazards": ["触电", "机械伤害"],
        "iso_clause": "7.1",
    },
    "饮水机": {
        "category": "office",
        "steps": """### 开机操作：

1. 检查电源线是否完好，接地是否可靠。
2. 确认水桶安装正确，无漏水。
3. 打开电源开关。
4. 等待加热/制冷完成（指示灯变化）。

### 日常使用：

1. 定期更换水桶，注意卫生。
2. 定期清洗水嘴和接水盘。
3. 发现异味或杂质应立即停用。
4. 长时间不用时应排空存水。

### 关机操作：

1. 关闭电源开关。
2. 长期不用时应拔掉电源插头。""",
        "hazards": ["触电", "烫伤（热水）"],
        "iso_clause": "7.1",
    },
    "消防器材": {
        "category": "safety",
        "steps": """### 灭火器使用：

1. **提**：提起灭火器，检查压力表是否在绿色区域。
2. **拔**：拔掉保险销。
3. **握**：握住喷管前端。
4. **压**：压下把手，对准火焰根部喷射。

### 消防栓使用：

1. 打开消防栓箱门。
2. 取出水带，展开并连接水枪。
3. 打开阀门，对准火源喷射。
4. 注意保持安全距离。

### 日常检查：

1. 每月检查灭火器压力是否正常。
2. 检查消防栓水带是否完好。
3. 检查应急照明和疏散指示是否正常。
4. 发现问题及时报告综合管理部。""",
        "hazards": ["火灾", "烟雾窒息"],
        "iso_clause": "8.1",
    },
    "急救设备": {
        "category": "safety",
        "steps": """### 急救箱使用：

1. 急救箱应放置在明显、易取的位置。
2. 使用前应检查药品有效期。
3. 按照药品说明书使用。
4. 使用后及时补充消耗的药品。

### 自动体外除颤器(AED)使用：

1. 确认患者无意识、无呼吸。
2. 打开AED电源，按照语音提示操作。
3. 贴好电极片，确保无人接触患者。
4. 按下除颤按钮（如提示）。

### 日常检查：

1. 每月检查急救箱物品是否齐全。
2. 检查药品有效期，及时更换过期药品。
3. 检查AED电池电量。
4. 记录检查情况。""",
        "hazards": ["感染风险"],
        "iso_clause": "8.1",
    },
    "监控设备": {
        "category": "safety",
        "steps": """### 监控系统操作：

1. 监控系统应由专人操作管理。
2. 开机前检查各设备连接是否正常。
3. 登录系统时输入正确的用户名和密码。
4. 监控画面应定期巡视，发现异常及时报告。

### 摄像头维护：

1. 定期清洁摄像头镜头。
2. 检查摄像头固定是否牢固。
3. 发现摄像头故障应及时报修。

### 门禁系统操作：

1. 门禁卡应妥善保管，不得转借他人。
2. 进出门禁区域应刷卡。
3. 门禁卡丢失应及时报告并注销。

### 注意事项：

1. 监控资料涉及隐私，不得外泄。
2. 监控系统应24小时运行。
3. 定期检查系统运行状态。""",
        "hazards": ["触电"],
        "iso_clause": "8.1",
    },
    "电焊机": {
        "category": "production",
        "steps": """### 操作前准备：

1. 检查电焊机外壳接地是否良好。
2. 检查电缆线有无破损，接头是否牢固。
3. 检查焊钳绝缘是否完好。
4. 穿戴好防护用品（面罩、手套、防护服）。
5. 清理作业区域易燃物。

### 焊接操作：

1. 根据焊接材料和厚度调节电流。
2. 引弧时焊条与工件保持适当角度。
3. 保持稳定的电弧长度和焊接速度。
4. 注意通风，避免吸入焊接烟尘。

### 操作后：

1. 关闭电焊机电源。
2. 整理好电缆线。
3. 清理焊渣和飞溅物。
4. 检查作业区域无火灾隐患。""",
        "hazards": ["触电", "弧光灼伤", "火灾", "烟尘吸入", "烫伤"],
        "iso_clause": "8.5",
    },
    "切割机": {
        "category": "production",
        "steps": """### 操作前准备：

1. 检查设备各部件是否完好。
2. 检查切割片是否有裂纹或磨损。
3. 检查防护罩是否安装到位。
4. 穿戴好防护用品（护目镜、手套）。

### 切割操作：

1. 固定好工件，防止滑动。
2. 启动设备，待转速稳定后再切割。
3. 均匀用力，不要强行切割。
4. 切割时站在侧面，不要正对切割片。

### 操作后：

1. 关闭电源，待设备完全停止。
2. 清理切屑和杂物。
3. 检查切割片磨损情况。
4. 做好设备保养。""",
        "hazards": ["机械伤害", "飞溅物伤害", "噪声"],
        "iso_clause": "8.5",
    },
    "行车/起重机": {
        "category": "production",
        "steps": """### 操作前检查：

1. 检查钢丝绳有无断丝、磨损。
2. 检查吊钩有无裂纹、变形。
3. 检查限位器、制动器是否有效。
4. 检查遥控器或操作手柄是否正常。
5. 空载试运行，确认各机构正常。

### 起重操作：

1. 确认吊物重量不超过额定起重量。
2. 吊物应捆扎牢固，重心平稳。
3. 起吊时先离地100-200mm试吊。
4. 吊物下方严禁站人。
5. 运行中保持吊物平稳，不要晃动。

### 操作后：

1. 将吊钩升至上限位置。
2. 切断电源。
3. 做好运行记录。
4. 交班时说明设备状况。""",
        "hazards": ["起重伤害", "物体打击", "高处坠落"],
        "iso_clause": "8.5",
    },
    "叉车": {
        "category": "production",
        "steps": """### 操作前检查：

1. 检查轮胎气压和磨损情况。
2. 检查液压系统有无泄漏。
3. 检查货叉有无变形、裂纹。
4. 检查制动系统是否有效。
5. 检查灯光、喇叭是否正常。

### 驾驶操作：

1. 系好安全带。
2. 起步前观察周围环境，鸣笛示意。
3. 行驶速度不超过5km/h（室内）。
4. 转弯时减速，注意行人。
5. 货叉离地15-20cm行驶。

### 装卸操作：

1. 货叉对准托盘插孔，缓慢进入。
2. 起升货物后稍微后倾门架。
3. 堆垛时注意稳定性，不要超高。
4. 卸货时缓慢下降，确认稳定后再退出。

### 操作后：

1. 货叉落地，门架前倾。
2. 拉手刹，关闭电源。
3. 做好运行记录。""",
        "hazards": ["车辆伤害", "物体打击", "倾覆"],
        "iso_clause": "8.5",
    },
    "通用设备": {
        "category": "general",
        "steps": """### 操作前准备：

1. 检查设备外观是否完好，有无损坏。
2. 检查电源线、接地线是否连接可靠。
3. 检查各部件是否安装牢固。
4. 阅读设备使用说明书，了解操作方法。
5. 穿戴好必要的劳动防护用品。

### 启动操作：

1. 确认设备周围无人员靠近。
2. 按照说明书要求启动设备。
3. 观察设备运行是否正常，有无异常声音或振动。
4. 空载运行一段时间，确认正常后再加载。

### 运行操作：

1. 严格按照操作规程操作。
2. 不得超负荷运行。
3. 运行中不得离开岗位。
4. 发现异常应立即停机检查。

### 停机操作：

1. 先卸载，再停机。
2. 按照说明书要求关闭设备。
3. 切断电源。
4. 清理设备和工作区域。""",
        "hazards": ["触电", "机械伤害"],
        "iso_clause": "7.1",
    },
}


# ==================== 动态生成器 ====================

class DynamicEquipmentOperationGenerator(BaseGenerator):
    """动态设备操作规程生成器
    
    根据用户输入的设备列表，动态生成对应的操作规程。
    """
    
    def __init__(self, company_info: CompanyInfo, equipment_list: List[Dict]):
        """
        初始化
        
        Args:
            company_info: 企业信息
            equipment_list: 设备列表，每个设备为一个字典
                [{"name": "设备名称", "model": "型号", "quantity": 数量}, ...]
        """
        super().__init__(company_info)
        self.equipment_list = equipment_list
    
    def _get_equipment_template(self, equipment_name: str) -> Dict:
        """获取设备模板
        
        先精确匹配，再模糊匹配，最后返回通用模板
        """
        # 精确匹配
        if equipment_name in EQUIPMENT_TEMPLATES:
            return EQUIPMENT_TEMPLATES[equipment_name]
        
        # 模糊匹配
        for key, template in EQUIPMENT_TEMPLATES.items():
            if key in equipment_name or equipment_name in key:
                return template
        
        # 返回通用模板
        return EQUIPMENT_TEMPLATES["通用设备"]
    
    def _generate_single_operation(self, equipment: Dict, seq: int) -> GeneratedDocument:
        """生成单个设备的操作规程"""
        name = equipment.get("name", "未知设备")
        model = equipment.get("model", "")
        quantity = equipment.get("quantity", 1)
        
        # 获取模板
        template = self._get_equipment_template(name)
        steps = template["steps"]
        hazards = template["hazards"]
        iso_clause = template.get("iso_clause", "7.1")
        
        # 构建文件名称
        file_name = f"{name}操作规程"
        if model:
            file_name = f"{name}({model})操作规程"
        
        # 构建危险源列表
        hazards_text = "、".join(hazards)
        
        # 构建内容
        content = f"""# {{公司名称}} {file_name}

**文件编号**：{{公司代号}}-QESMS-C-{seq:03d}

**版本**：A/0

**生效日期**：{{生效日期}}

---

## 目的

制定本规程的目的是规范{name}的操作，确保设备安全运行，防止事故发生。

## 适用范围

本规程适用于公司所有{name}的操作和维护。

## 设备信息

- **设备名称**：{name}
- **设备型号**：{model or "详见设备台账"}
- **数量**：{quantity}台
- **管理部门**：综合管理部
- **使用部门**：各使用部门

## 危险源识别

操作{name}时可能存在以下危险源：

{chr(10).join(f"- {h}" for h in hazards)}

## 一、安全操作基本注意事项

1. 操作人员必须经过培训，熟悉设备性能和操作方法后方可上岗。
2. 操作前应检查设备外观是否正常，有无损坏或异常。
3. 严格按照操作规程操作，严禁违章操作。
4. 设备运行过程中，不得擅自离开岗位。
5. 发现异常应立即停机，报告处理。

## 二、操作步骤

{steps}

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
| 运行不稳定 | 部件磨损 | 报修更换 |

## 五、设备保养维护要求

1. 定期清洁设备表面。
2. 定期检查各部件紧固情况。
3. 定期润滑运动部件。
4. 做好防尘、防潮措施。
5. 维修保养记录归档保存。

## 六、应急处理

发生以下情况时应立即停机并采取应急措施：

1. **触电事故**：立即切断电源，用绝缘物使触电者脱离电源，进行急救并拨打120。
2. **机械伤害**：立即停机，对伤口进行包扎，严重时送医治疗。
3. **火灾**：立即使用灭火器扑救，拨打119报警，组织人员疏散。

---

**编制/日期**：
**审核/日期**：
**批准/日期**：
"""
        
        # 渲染模板变量
        rendered_content = self.render(content)
        
        return GeneratedDocument(
            file_level=FileLevel.LEVEL_3,
            document_type=DocumentType.INSTRUCTION,
            file_code=f"{{公司代号}}-QESMS-C-{seq:03d}",
            file_name=f"{file_name}.docx",
            title=file_name,
            content=rendered_content,
            related_clauses=[iso_clause],
        )
    
    def generate(self) -> List[GeneratedDocument]:
        """生成所有设备的操作规程
        
        Returns:
            生成的文档列表
        """
        documents = []
        start_seq = 50  # 动态生成的操作规程从C-050开始，避免与固定模板冲突
        
        for idx, equipment in enumerate(self.equipment_list):
            seq = start_seq + idx
            doc = self._generate_single_operation(equipment, seq)
            documents.append(doc)
        
        return documents
    
    def generate_summary(self) -> GeneratedDocument:
        """生成设备操作规程目录/总册
        
        当设备较多时，生成一个总册方便查阅。
        """
        equipment_items = []
        for idx, equipment in enumerate(self.equipment_list):
            seq = 50 + idx
            name = equipment.get("name", "未知设备")
            model = equipment.get("model", "")
            code = f"{{公司代号}}-QESMS-C-{seq:03d}"
            if model:
                equipment_items.append(f"{idx+1}. {code} {name}({model})操作规程")
            else:
                equipment_items.append(f"{idx+1}. {code} {name}操作规程")
        
        content = f"""# {{公司名称}} 设备操作规程目录

**文件编号**：{{公司代号}}-QESMS-C-049

**版本**：A/0

**生效日期**：{{生效日期}}

---

## 目录

{chr(10).join(equipment_items)}

---

## 说明

1. 本目录所列设备操作规程均为公司现行有效版本。
2. 各使用部门应严格按照操作规程操作设备。
3. 操作规程的修订由综合管理部统一管理。
4. 新增设备的操作规程应在设备投入使用前编制完成。

---

**编制/日期**：
**审核/日期**：
**批准/日期**：
"""
        
        rendered_content = self.render(content)
        
        return GeneratedDocument(
            file_level=FileLevel.LEVEL_3,
            document_type=DocumentType.INSTRUCTION,
            file_code="{{公司代号}}-QESMS-C-049",
            file_name="设备操作规程目录.docx",
            title="设备操作规程目录",
            content=rendered_content,
        )


# ==================== 便捷函数 ====================

def generate_equipment_operations(
    company_info: CompanyInfo,
    equipment_list: List[Dict],
    include_summary: bool = True,
) -> List[GeneratedDocument]:
    """生成设备操作规程的便捷函数
    
    Args:
        company_info: 企业信息
        equipment_list: 设备列表
        include_summary: 是否包含目录总册
        
    Returns:
        生成的文档列表
    """
    generator = DynamicEquipmentOperationGenerator(company_info, equipment_list)
    documents = generator.generate()
    
    if include_summary and len(equipment_list) > 1:
        summary = generator.generate_summary()
        documents.insert(0, summary)
    
    return documents


# 设备名称映射表（用于前端选择）
EQUIPMENT_NAME_MAP = {
    "office": {
        "name": "办公设备",
        "equipments": ["电脑", "空调", "打印机", "复印机", "投影仪", "碎纸机", "饮水机"],
    },
    "safety": {
        "name": "安全设备",
        "equipments": ["消防器材", "急救设备", "监控设备"],
    },
    "production": {
        "name": "生产设备",
        "equipments": ["电焊机", "切割机", "行车/起重机", "叉车"],
    },
    "general": {
        "name": "通用设备",
        "equipments": ["通用设备"],
    },
}


def get_equipment_categories() -> List[Dict]:
    """获取设备分类列表（供前端使用）"""
    return [
        {"code": key, "name": value["name"], "equipments": value["equipments"]}
        for key, value in EQUIPMENT_NAME_MAP.items()
    ]


def get_all_equipment_names() -> List[str]:
    """获取所有支持的设备名称"""
    names = []
    for category in EQUIPMENT_NAME_MAP.values():
        names.extend(category["equipments"])
    return names
