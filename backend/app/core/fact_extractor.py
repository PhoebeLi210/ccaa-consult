"""
事实提取器模块
用于从源文件中提取真实事实，包括人名、编号、数据指标、条款引用、部门名称等。
提取结果可用于与AI生成内容进行交叉验证，防止编造。
"""

import re
import logging
from enum import Enum
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


class FactType(Enum):
    """事实类型枚举"""
    PERSON_NAME = "person_name"           # 人名
    DOCUMENT_NUMBER = "document_number"   # 文件编号
    DATA_METRIC = "data_metric"           # 数据指标（数字、百分比、日期等）
    CLAUSE_REFERENCE = "clause_reference" # 标准条款引用
    DEPARTMENT_NAME = "department_name"   # 部门名称
    CERTIFICATE = "certificate"           # 证书信息
    DATE = "date"                         # 日期
    PERCENTAGE = "percentage"             # 百分比
    AMOUNT = "amount"                     # 金额
    OTHER = "other"                       # 其他


@dataclass
class Fact:
    """单个事实数据类"""
    type: FactType           # 事实类型
    value: str               # 事实值
    source: str = ""         # 来源文本片段（原文上下文）
    confidence: float = 1.0  # 置信度 (0.0 ~ 1.0)
    position: int = -1       # 在原文中的位置
    metadata: Dict[str, Any] = field(default_factory=dict)  # 附加元数据


@dataclass
class ExtractionCache:
    """提取结果缓存数据类"""
    source_text_hash: int = 0              # 源文本哈希值（用于缓存失效判断）
    facts: List[Fact] = field(default_factory=list)  # 提取到的事实列表
    fact_count_by_type: Dict[str, int] = field(default_factory=dict)  # 各类型事实数量
    extraction_time: float = 0.0           # 提取耗时（秒）
    text_length: int = 0                   # 源文本长度

    def get_facts_by_type(self, fact_type: FactType) -> List[Fact]:
        """按类型获取事实列表"""
        return [f for f in self.facts if f.type == fact_type]

    def get_unique_values(self, fact_type: Optional[FactType] = None) -> Set[str]:
        """获取去重后的值集合"""
        if fact_type:
            return {f.value for f in self.facts if f.type == fact_type}
        return {f.value for f in self.facts}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "source_text_hash": self.source_text_hash,
            "fact_count": len(self.facts),
            "fact_count_by_type": self.fact_count_by_type,
            "extraction_time": round(self.extraction_time, 4),
            "text_length": self.text_length,
            "facts": [
                {
                    "type": f.type.value,
                    "value": f.value,
                    "source": f.source,
                    "confidence": f.confidence,
                    "position": f.position,
                    "metadata": f.metadata
                }
                for f in self.facts
            ]
        }


class FactExtractor:
    """
    事实提取器

    从源文件文本中提取各类真实事实信息，用于后续与AI生成内容交叉验证。

    支持提取的事实类型:
    - 人名 (person_name)
    - 文件编号 (document_number)
    - 数据指标 (data_metric) - 包含数字、百分比、日期、金额
    - 标准条款引用 (clause_reference)
    - 部门名称 (department_name)

    使用方式:
        extractor = FactExtractor()
        facts = extractor.extract_all_facts(source_text)
        # 或按类型提取
        names = extractor.extract_person_names(source_text)
    """

    # ---- 常见中文姓氏（用于人名提取） ----
    _COMMON_SURNAMES: Set[str] = {
        "赵", "钱", "孙", "李", "周", "吴", "郑", "王", "冯", "陈",
        "褚", "卫", "蒋", "沈", "韩", "杨", "朱", "秦", "尤", "许",
        "何", "吕", "施", "张", "孔", "曹", "严", "华", "金", "魏",
        "陶", "姜", "戚", "谢", "邹", "喻", "柏", "水", "窦", "章",
        "云", "苏", "潘", "葛", "奚", "范", "彭", "郎", "鲁", "韦",
        "昌", "马", "苗", "凤", "花", "方", "俞", "任", "袁", "柳",
        "酆", "鲍", "史", "唐", "费", "廉", "岑", "薛", "雷", "贺",
        "倪", "汤", "滕", "殷", "罗", "毕", "郝", "邬", "安", "常",
        "乐", "于", "时", "傅", "皮", "卞", "齐", "康", "伍", "余",
        "元", "卜", "顾", "孟", "平", "黄", "和", "穆", "萧", "尹",
        "姚", "邵", "湛", "汪", "祁", "毛", "禹", "狄", "米", "贝",
        "明", "臧", "计", "伏", "成", "戴", "谈", "宋", "茅", "庞",
        "熊", "纪", "舒", "屈", "项", "祝", "董", "梁", "杜", "阮",
        "蓝", "闵", "席", "季", "麻", "强", "贾", "路", "娄", "危",
        "江", "童", "颜", "郭", "梅", "盛", "林", "刁", "钟", "徐",
        "邱", "骆", "高", "夏", "蔡", "田", "樊", "胡", "凌", "霍",
        "虞", "万", "支", "柯", "昝", "管", "卢", "莫", "经", "房",
        "裘", "缪", "干", "解", "应", "宗", "丁", "宣", "贲", "邓",
        "郁", "单", "杭", "洪", "包", "诸", "左", "石", "崔", "吉",
        "钮", "龚", "程", "嵇", "邢", "滑", "裴", "陆", "荣", "翁",
        "荀", "羊", "於", "惠", "甄", "曲", "家", "封", "芮", "羿",
        "储", "靳", "汲", "邴", "糜", "松", "井", "段", "富", "巫",
        "乌", "焦", "巴", "弓", "牧", "隗", "山", "谷", "车", "侯",
        "宓", "蓬", "全", "郗", "班", "仰", "秋", "仲", "伊", "宫",
        "宁", "仇", "栾", "暴", "甘", "钭", "厉", "戎", "祖", "武",
        "符", "刘", "景", "詹", "束", "龙", "叶", "幸", "司", "韶",
        "郜", "黎", "蓟", "溥", "印", "宿", "白", "怀", "蒲", "邰",
        "从", "鄂", "索", "咸", "籍", "赖", "卓", "蔺", "屠", "蒙",
        "池", "乔", "阴", "郁", "胥", "能", "苍", "双", "闻", "莘",
        "党", "翟", "谭", "贡", "劳", "逄", "姬", "申", "扶", "堵",
        "冉", "宰", "郦", "雍", "却", "璩", "桑", "桂", "濮", "牛",
        "寿", "通", "边", "扈", "燕", "冀", "郏", "浦", "尚", "农",
        "温", "别", "庄", "晏", "柴", "瞿", "阎", "充", "慕", "连",
        "茹", "习", "宦", "艾", "鱼", "容", "向", "古", "易", "慎",
        "戈", "廖", "庾", "终", "暨", "居", "衡", "步", "都", "耿",
        "满", "弘", "匡", "国", "文", "寇", "广", "禄", "阙", "东",
        "欧", "殳", "沃", "利", "蔚", "越", "夔", "隆", "师", "巩",
        "厍", "聂", "晁", "勾", "敖", "融", "冷", "訾", "辛", "阚",
        "那", "简", "饶", "空", "曾", "毋", "沙", "乜", "养", "鞠",
        "须", "丰", "巢", "关", "蒯", "相", "查", "后", "荆", "红",
        "游", "竺", "权", "逯", "盖", "益", "桓", "公",
        # 复姓
        "万俟", "司马", "上官", "欧阳", "夏侯", "诸葛", "闻人", "东方",
        "赫连", "皇甫", "尉迟", "公羊", "澹台", "公冶", "宗政", "濮阳",
        "淳于", "单于", "太叔", "申屠", "公孙", "仲孙", "轩辕", "令狐",
        "钟离", "宇文", "长孙", "慕容", "鲜于", "闾丘", "司徒", "司空",
    }

    # ---- 标准部门列表 ----
    _STANDARD_DEPARTMENTS: List[str] = [
        "总经理办公室", "综合管理部", "质量管理部", "质量控制部", "质量保证部",
        "生产管理部", "生产制造部", "生产技术部", "技术研发部", "技术部",
        "研发部", "采购部", "供应链管理部", "物流部", "仓储部",
        "销售部", "市场部", "客户服务部", "售后服务部", "人力资源部",
        "行政部", "财务部", "审计部", "设备管理部", "设备部",
        "安全环保部", "安环部", "信息部", "IT部", "项目管理部",
        "总经办", "企管部", "品管部", "品保部", "生管部",
        "物控部", "仓管部", "营销部", "国际业务部", "国内业务部",
        "法务部", "战略发展部", "投资部", "公关部", "品牌部",
        "设计部", "工艺部", "工程部", "维修部", "动力部",
        "环保部", "职业健康安全部", "食品安全部", "检测中心", "实验室",
        "前厅部", "客房部", "餐饮部", "工程部", "保安部",
        "物业部", "保洁部", "绿化部", "后勤部", "食堂",
    ]

    # ---- 非人名词汇（用于过滤误识别） ----
    _NON_NAME_WORDS: Set[str] = {
        "公司", "企业", "部门", "管理", "质量", "技术", "生产",
        "服务", "客户", "市场", "产品", "设备", "安全", "环境",
        "文件", "记录", "过程", "控制", "审核", "评审", "监督",
        "检查", "检验", "测量", "改进", "培训", "采购", "销售",
        "设计", "开发", "实施", "维护", "运行", "操作", "处置",
        "我们", "他们", "你们", "自己", "什么", "怎么", "这个",
        "那个", "因为", "所以", "但是", "而且", "或者", "如果",
        "可以", "应该", "需要", "能够", "已经", "正在", "将要",
        "根据", "按照", "通过", "进行", "开展", "组织", "建立",
        "保持", "确保", "达到", "满足", "符合", "遵守", "执行",
        "规定", "要求", "标准", "程序", "制度", "计划", "方案",
        "报告", "总结", "分析", "评价", "确认", "验证", "批准",
        "编制", "审核", "发布", "修订", "作废", "回收", "归档",
        "体系", "方针", "目标", "指标", "范围", "职责", "权限",
        "资源", "能力", "意识", "沟通", "文件化", "信息",
        "绩效", "评价", "监视", "不合格", "纠正", "预防",
        "内部", "外部", "供应商", "顾客", "相关方", "员工",
        "风险", "机遇", "变更", "创新", "知识", "能力",
        "基础设施", "工作环境", "监视测量", "计量", "校准",
    }

    # ---- 正则模式 ----

    # 人名模式
    _PERSON_NAME_PATTERN = re.compile(
        r'(?:'
        # 职务+姓名: 总经理张三, 质量负责人李四
        r'(?:总经理|副总经理|总工程师|管理者代表|质量负责人|技术负责人|安全负责人|部门负责人|审核组长|内审员)\s*[:：]?\s*([\u4e00-\u9fa5]{2,4})'
        r'|'
        # 姓名+职务: 张三担任, 李四负责
        r'([\u4e00-\u9fa5]{2,4})(?=担任|负责|主管|经理|主任|部长|组长|审核|批准|编制|实施|执行|参与|确认)'
        r'|'
        # 签名/签字区域
        r'(?:签名|签字|编制人|审核人|批准人)\s*[:：]?\s*([\u4e00-\u9fa5]{2,4})'
        r')'
    )

    # 文件编号模式
    _DOC_NUMBER_PATTERN = re.compile(
        r'(?:'
        r'[A-Z]{2,5}-[A-Z]{1,6}-[A-Z]-\d{3,4}'       # XXX-QESMS-A-001
        r'|[A-Z]{2,5}-[A-Z]{1,3}-\d{3,4}'             # XXX-ISO-001
        r'|[A-Z]{2,4}-[A-Z]{1,3}-\d{3,4}'             # XX-QM-001
        r')'
    )

    # 标准编号模式
    _STANDARD_NUMBER_PATTERN = re.compile(
        r'(?:ISO|GB|GB/T|HJ|QB|DB|Q|JG|SL|JT|YS|CJ|NY|AQ|SN|WS|T/CNAS|RB|RB/T)\s*[\d/.-]+'
    )

    # 证书编号模式
    _CERT_NUMBER_PATTERN = re.compile(
        r'(?:'
        r'CNAS-[A-Z]{2,4}-\d{4,6}'
        r'|证书编号\s*[:：]?\s*\S+'
        r'|注册号\s*[:：]?\s*\S+'
        r'|认可号\s*[:：]?\s*\S+'
        r')'
    )

    # 数字/百分比模式
    _NUMBER_PATTERN = re.compile(
        r'(?:'
        r'\d+\.?\d*\s*%'                        # 百分比
        r'|人民币\s*\d+\.?\d*\s*元'             # 人民币金额
        r'|\d+\.?\d*\s*万元'                    # 万元
        r'|\d+\.?\d*\s*亿'                      # 亿
        r'|\d{1,3}(?:,\d{3})+'                  # 千分位
        r'|\b\d+\.?\d*\b'                       # 普通数字
        r')'
    )

    # 日期模式
    _DATE_PATTERN = re.compile(
        r'(?:'
        r'\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日'
        r'|\d{4}\s*年\s*\d{1,2}\s*月'
        r'|\d{4}[-/]\d{1,2}[-/]\d{1,2}'
        r'|\d{4}[-/]\d{1,2}'
        r'|(?:19|20)\d{2}年'
        r'|Q[1-4]\s*[-/]?\s*(?:19|20)\d{2}'
        r'|第[一二三四1-4]季度'
        r')'
    )

    # 标准条款引用模式
    _CLAUSE_PATTERN = re.compile(
        r'(?:'
        # ISO标准条款: ISO 9001:2015 第4.1条, 4.2条款, 条款5.3
        r'(?:ISO|GB|GB/T|HJ)\s*\d+[:/]\d+\s*(?:第)?\s*(?:\d+\.?\d*(?:\.\d+)*)\s*(?:条|款|章|节|要求)'
        r'|'
        # 条款编号: 4.1, 5.3.2, 8.5.1
        r'(?:条款|标准|规范)\s*(?:第)?\s*(?:\d+\.){1,3}\d+\s*(?:条|款|章|节)?'
        r'|'
        # 引用格式: "见4.1", "参照5.3", "依据8.5.1"
        r'(?:见|参照|依据|按照|符合|满足|引用)\s*(?:第)?\s*(?:\d+\.){1,3}\d+'
        r'|'
        # 标准全文引用: ISO 9001:2015, GB/T 19001-2016
        r'(?:ISO|GB|GB/T|HJ|QB|DB|JG|SL|JT|YS|CJ|NY|AQ|SN|WS)\s*[\d]+(?:[/-][\d]+)*(?:[:\s]\d{4})?'
        r')'
    )

    # 部门名称模式
    _DEPARTMENT_PATTERN = re.compile(
        r'[\u4e00-\u9fa5]{2,8}(?:部|中心|室|科|处|课|所|院|组|办|站|队|车间|工区)'
    )

    def __init__(self):
        """初始化事实提取器"""
        self._logger = logging.getLogger(f"{__name__}.FactExtractor")
        self._cache: Optional[ExtractionCache] = None

    def extract_person_names(self, text: str) -> List[Fact]:
        """
        提取人名

        从文本中提取人名，使用常见姓氏列表进行辅助识别。
        支持以下格式:
        - "总经理张三"
        - "张三担任质量经理"
        - "编制人: 李四"
        - "签名: 王五"

        Args:
            text: 源文本

        Returns:
            List[Fact]: 人名事实列表
        """
        if not text:
            return []

        facts: List[Fact] = []
        seen_names: Set[str] = set()

        # 方法1: 使用结构化模式匹配
        for match in self._PERSON_NAME_PATTERN.finditer(text):
            # 获取匹配到的姓名（可能在不同的捕获组中）
            name = None
            for group in match.groups():
                if group and self._is_likely_name(group):
                    name = group
                    break

            if name and name not in seen_names:
                seen_names.add(name)
                context = self._extract_context(text, match.start(), match.end() - match.start())
                facts.append(Fact(
                    type=FactType.PERSON_NAME,
                    value=name,
                    source=context,
                    confidence=0.9,
                    position=match.start(),
                    metadata={"match_method": "pattern"}
                ))

        # 方法2: 基于姓氏的宽泛匹配（补充方法1遗漏的人名）
        surname_name_pattern = re.compile(
            r'([\u4e00-\u9fa5])([\u4e00-\u9fa5]{1,3})'
        )
        for match in surname_name_pattern.finditer(text):
            full_name = match.group(0)
            first_char = match.group(1)
            first_two = full_name[:2]

            if full_name in seen_names:
                continue

            # 检查是否为常见姓氏
            is_surname = (
                first_char in self._COMMON_SURNAMES
                or first_two in self._COMMON_SURNAMES
            )

            if is_surname and full_name not in self._NON_NAME_WORDS:
                # 检查上下文是否像人名（附近有职务、签名等关键词）
                local_context = text[max(0, match.start() - 20):min(len(text), match.end() + 20)]
                name_indicators = [
                    "担任", "负责", "主管", "经理", "主任", "部长", "组长",
                    "审核", "批准", "编制", "签名", "签字", "人员",
                    "员工", "内审员", "代表", "联系人"
                ]
                has_indicator = any(ind in local_context for ind in name_indicators)

                if has_indicator:
                    seen_names.add(full_name)
                    context = self._extract_context(text, match.start(), len(full_name))
                    facts.append(Fact(
                        type=FactType.PERSON_NAME,
                        value=full_name,
                        source=context,
                        confidence=0.7,
                        position=match.start(),
                        metadata={"match_method": "surname_context"}
                    ))

        self._logger.debug(f"提取到{len(facts)}个人名")
        return facts

    def extract_document_numbers(self, text: str) -> List[Fact]:
        """
        提取文件编号

        从文本中提取各种格式的文件编号，包括:
        - 体系文件编号: XXX-QESMS-A-001
        - 程序文件编号: XXX-B-001
        - 标准编号: ISO 9001:2015, GB/T 19001-2016
        - 证书编号: CNAS-XXXX-XXXXXX

        Args:
            text: 源文本

        Returns:
            List[Fact]: 文件编号事实列表
        """
        if not text:
            return []

        facts: List[Fact] = []
        seen: Set[str] = set()

        # 提取体系文件编号
        for match in self._DOC_NUMBER_PATTERN.finditer(text):
            num = match.group()
            if num not in seen:
                seen.add(num)
                context = self._extract_context(text, match.start(), len(num))
                facts.append(Fact(
                    type=FactType.DOCUMENT_NUMBER,
                    value=num,
                    source=context,
                    confidence=0.95,
                    position=match.start(),
                    metadata={"match_method": "doc_number_pattern", "format": "system_doc"}
                ))

        # 提取标准编号
        for match in self._STANDARD_NUMBER_PATTERN.finditer(text):
            num = match.group()
            if num not in seen:
                seen.add(num)
                context = self._extract_context(text, match.start(), len(num))
                facts.append(Fact(
                    type=FactType.DOCUMENT_NUMBER,
                    value=num,
                    source=context,
                    confidence=0.95,
                    position=match.start(),
                    metadata={"match_method": "standard_number_pattern", "format": "standard"}
                ))

        # 提取证书编号
        for match in self._CERT_NUMBER_PATTERN.finditer(text):
            num = match.group().strip()
            if num not in seen:
                seen.add(num)
                context = self._extract_context(text, match.start(), len(match.group()))
                facts.append(Fact(
                    type=FactType.CERTIFICATE,
                    value=num,
                    source=context,
                    confidence=0.9,
                    position=match.start(),
                    metadata={"match_method": "cert_number_pattern"}
                ))

        self._logger.debug(f"提取到{len(facts)}个文件编号/证书编号")
        return facts

    def extract_data_metrics(self, text: str) -> List[Fact]:
        """
        提取数据指标

        从文本中提取各类数据指标，包括:
        - 数字（整数、小数）
        - 百分比（95%, 99.5%）
        - 日期（2024年1月15日, 2024-01-15）
        - 金额（人民币100万元）

        Args:
            text: 源文本

        Returns:
            List[Fact]: 数据指标事实列表
        """
        if not text:
            return []

        facts: List[Fact] = []
        seen: Set[str] = set()

        # 提取百分比
        pct_pattern = re.compile(r'\d+\.?\d*\s*%')
        for match in pct_pattern.finditer(text):
            val = match.group()
            if val not in seen:
                seen.add(val)
                context = self._extract_context(text, match.start(), len(val))
                facts.append(Fact(
                    type=FactType.PERCENTAGE,
                    value=val,
                    source=context,
                    confidence=0.95,
                    position=match.start(),
                    metadata={"match_method": "percentage", "numeric_value": float(val.replace('%', '').replace(' ', ''))}
                ))

        # 提取金额
        amount_pattern = re.compile(
            r'(?:人民币\s*\d+\.?\d*\s*元|\d+\.?\d*\s*万元|\d+\.?\d*\s*亿(?:元)?)'
        )
        for match in amount_pattern.finditer(text):
            val = match.group()
            if val not in seen:
                seen.add(val)
                context = self._extract_context(text, match.start(), len(val))
                facts.append(Fact(
                    type=FactType.AMOUNT,
                    value=val,
                    source=context,
                    confidence=0.9,
                    position=match.start(),
                    metadata={"match_method": "amount"}
                ))

        # 提取日期
        for match in self._DATE_PATTERN.finditer(text):
            val = match.group()
            if val not in seen:
                seen.add(val)
                context = self._extract_context(text, match.start(), len(val))
                facts.append(Fact(
                    type=FactType.DATE,
                    value=val,
                    source=context,
                    confidence=0.95,
                    position=match.start(),
                    metadata={"match_method": "date"}
                ))

        # 提取其他数字（排除已提取的百分比、金额、日期）
        for match in self._NUMBER_PATTERN.finditer(text):
            val = match.group()
            if val not in seen:
                seen.add(val)
                context = self._extract_context(text, match.start(), len(val))
                facts.append(Fact(
                    type=FactType.DATA_METRIC,
                    value=val,
                    source=context,
                    confidence=0.8,
                    position=match.start(),
                    metadata={"match_method": "number"}
                ))

        self._logger.debug(f"提取到{len(facts)}个数据指标")
        return facts

    def extract_clause_references(self, text: str) -> List[Fact]:
        """
        提取标准条款引用

        从文本中提取标准条款引用，包括:
        - ISO标准条款: "ISO 9001:2015 第4.1条"
        - 条款编号: "条款4.1", "5.3.2"
        - 引用格式: "见4.1", "依据8.5.1"
        - 标准全文引用: "ISO 9001:2015", "GB/T 19001-2016"

        Args:
            text: 源文本

        Returns:
            List[Fact]: 条款引用事实列表
        """
        if not text:
            return []

        facts: List[Fact] = []
        seen: Set[str] = set()

        for match in self._CLAUSE_PATTERN.finditer(text):
            val = match.group().strip()
            if val not in seen:
                seen.add(val)
                context = self._extract_context(text, match.start(), len(match.group()))
                facts.append(Fact(
                    type=FactType.CLAUSE_REFERENCE,
                    value=val,
                    source=context,
                    confidence=0.9,
                    position=match.start(),
                    metadata={"match_method": "clause_pattern"}
                ))

        self._logger.debug(f"提取到{len(facts)}个标准条款引用")
        return facts

    def extract_department_names(self, text: str) -> List[Fact]:
        """
        提取部门名称

        从文本中提取部门名称，支持标准部门和自定义部门。
        匹配以"部"、"中心"、"室"、"科"等结尾的组织名称。

        Args:
            text: 源文本

        Returns:
            List[Fact]: 部门名称事实列表
        """
        if not text:
            return []

        facts: List[Fact] = []
        seen: Set[str] = set()

        # 方法1: 匹配标准部门列表
        for dept in self._STANDARD_DEPARTMENTS:
            if dept in text and dept not in seen:
                seen.add(dept)
                pos = text.find(dept)
                context = self._extract_context(text, pos, len(dept))
                is_standard = True
                facts.append(Fact(
                    type=FactType.DEPARTMENT_NAME,
                    value=dept,
                    source=context,
                    confidence=0.95 if is_standard else 0.7,
                    position=pos,
                    metadata={"match_method": "standard_list", "is_standard": is_standard}
                ))

        # 方法2: 正则模式匹配（补充非标准部门）
        for match in self._DEPARTMENT_PATTERN.finditer(text):
            dept = match.group()
            if dept not in seen:
                seen.add(dept)
                context = self._extract_context(text, match.start(), len(dept))
                is_standard = dept in self._STANDARD_DEPARTMENTS
                # 过滤明显非部门的词汇
                non_dept_words = {
                    "公安部", "国防部", "财政部", "教育部", "科技部", "工信部",
                    "国家", "政府", "社会", "世界", "国际", "全国",
                }
                is_gov = any(gw in dept for gw in non_dept_words)
                if not is_gov:
                    facts.append(Fact(
                        type=FactType.DEPARTMENT_NAME,
                        value=dept,
                        source=context,
                        confidence=0.7 if not is_standard else 0.95,
                        position=match.start(),
                        metadata={"match_method": "regex_pattern", "is_standard": is_standard}
                    ))

        self._logger.debug(f"提取到{len(facts)}个部门名称")
        return facts

    def extract_all_facts(self, text: str, use_cache: bool = True) -> ExtractionCache:
        """
        提取所有事实

        综合提取文本中的所有类型事实，包括人名、编号、数据指标、条款引用、部门名称。

        Args:
            text: 源文本
            use_cache: 是否使用缓存（相同文本不重复提取）

        Returns:
            ExtractionCache: 提取结果缓存
        """
        import time
        import hashlib

        if not text:
            return ExtractionCache(
                source_text_hash=0,
                facts=[],
                fact_count_by_type={},
                extraction_time=0.0,
                text_length=0
            )

        text_hash = hash(text)

        # 检查缓存
        if use_cache and self._cache and self._cache.source_text_hash == text_hash:
            self._logger.debug("使用缓存的事实提取结果")
            return self._cache

        start_time = time.time()

        # 按类型提取
        person_facts = self.extract_person_names(text)
        doc_facts = self.extract_document_numbers(text)
        data_facts = self.extract_data_metrics(text)
        clause_facts = self.extract_clause_references(text)
        dept_facts = self.extract_department_names(text)

        # 合并所有事实
        all_facts = person_facts + doc_facts + data_facts + clause_facts + dept_facts

        # 按位置排序
        all_facts.sort(key=lambda f: f.position)

        # 统计各类型数量
        count_by_type: Dict[str, int] = {}
        for fact in all_facts:
            type_key = fact.type.value
            count_by_type[type_key] = count_by_type.get(type_key, 0) + 1

        elapsed = time.time() - start_time

        cache = ExtractionCache(
            source_text_hash=text_hash,
            facts=all_facts,
            fact_count_by_type=count_by_type,
            extraction_time=elapsed,
            text_length=len(text)
        )

        if use_cache:
            self._cache = cache

        self._logger.info(
            f"事实提取完成: 共{len(all_facts)}个事实, "
            f"耗时{elapsed:.4f}s, 文本长度{len(text)}"
        )

        return cache

    def clear_cache(self) -> None:
        """清除提取缓存"""
        self._cache = None
        self._logger.debug("事实提取缓存已清除")

    def get_fact_values(self, text: str, fact_type: Optional[FactType] = None) -> Set[str]:
        """
        获取事实值集合（去重）

        便捷方法，直接返回去重后的事实值集合。

        Args:
            text: 源文本
            fact_type: 事实类型（为None时返回所有类型）

        Returns:
            Set[str]: 去重后的事实值集合
        """
        cache = self.extract_all_facts(text)
        return cache.get_unique_values(fact_type)

    def get_fact_summary(self, text: str) -> Dict[str, Any]:
        """
        获取事实提取摘要

        Args:
            text: 源文本

        Returns:
            Dict: 提取摘要信息
        """
        cache = self.extract_all_facts(text)
        return {
            "text_length": cache.text_length,
            "total_facts": len(cache.facts),
            "fact_count_by_type": cache.fact_count_by_type,
            "extraction_time": round(cache.extraction_time, 4),
            "unique_values": len(cache.get_unique_values()),
            "facts_by_type": {
                ft.value: [f.value for f in cache.get_facts_by_type(ft)]
                for ft in FactType
                if cache.get_facts_by_type(ft)
            }
        }

    # ---- 辅助方法 ----

    def _is_likely_name(self, text: str) -> bool:
        """判断文本是否像人名"""
        if not text or len(text) < 2 or len(text) > 4:
            return False
        # 纯中文
        if not re.match(r'^[\u4e00-\u9fa5]+$', text):
            return False
        # 排除非人名词汇
        if text in self._NON_NAME_WORDS:
            return False
        # 检查姓氏
        first_char = text[0]
        first_two = text[:2]
        return (
            first_char in self._COMMON_SURNAMES
            or first_two in self._COMMON_SURNAMES
        )

    def _extract_context(self, text: str, position: int, length: int, context_size: int = 30) -> str:
        """提取文本上下文片段"""
        if position < 0 or not text:
            return ""
        start = max(0, position - context_size)
        end = min(len(text), position + length + context_size)
        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        return context
