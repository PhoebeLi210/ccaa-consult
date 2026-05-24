#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 事实提取器
从文本和文档中提取关键事实信息
"""

import re
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FactType(str, Enum):
    """事实类型枚举"""
    ENTERPRISE_NAME = "企业名称"
    ADDRESS = "地址"
    EMPLOYEE_COUNT = "人数"
    DEPARTMENT = "部门"
    EQUIPMENT = "设备"
    PRODUCT = "产品"
    PERSON_NAME = "人名"
    PHONE = "电话"
    EMAIL = "邮箱"
    DATE = "日期"
    CERTIFICATE = "证书"
    PROCESS = "工艺"
    MATERIAL = "材料"
    STANDARD = "标准"
    REGULATION = "法规"
    RISK = "风险"
    HAZARD = "危险源"
    ORGANIZATION = "组织架构"
    POSITION = "职位"
    OTHER = "其他"


class FactSource(str, Enum):
    """事实来源枚举"""
    USER_INPUT = "用户输入"
    DOCUMENT = "文档提取"
    SYSTEM_INFERENCE = "系统推断"
    EXTERNAL_API = "外部接口"
    MANUAL_ENTRY = "手动录入"


@dataclass
class Fact:
    """事实数据类"""
    fact_id: str
    fact_type: FactType
    content: str
    source: FactSource
    confidence: float = 1.0
    context: str = ""
    position: Tuple[int, int] = (0, 0)  # 在原文中的位置
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_verified: bool = False
    verification_source: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "fact_id": self.fact_id,
            "fact_type": self.fact_type.value,
            "content": self.content,
            "source": self.source.value,
            "confidence": self.confidence,
            "context": self.context,
            "position": self.position,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_verified": self.is_verified,
            "verification_source": self.verification_source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Fact":
        """从字典创建"""
        return cls(
            fact_id=data["fact_id"],
            fact_type=FactType(data["fact_type"]),
            content=data["content"],
            source=FactSource(data["source"]),
            confidence=data.get("confidence", 1.0),
            context=data.get("context", ""),
            position=tuple(data.get("position", (0, 0))),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data.get("updated_at"), str) else datetime.now(),
            is_verified=data.get("is_verified", False),
            verification_source=data.get("verification_source", "")
        )


class FactExtractor:
    """事实提取器类"""
    
    # 常见姓氏列表（500个）
    COMMON_SURNAMES = [
        # 前100大姓
        "王", "李", "张", "刘", "陈", "杨", "黄", "赵", "吴", "周",
        "徐", "孙", "马", "朱", "胡", "郭", "何", "林", "罗", "高",
        "郑", "梁", "谢", "宋", "唐", "许", "邓", "冯", "韩", "曹",
        "曾", "彭", "萧", "蔡", "潘", "田", "董", "袁", "于", "余",
        "叶", "蒋", "杜", "苏", "魏", "程", "吕", "丁", "沈", "任",
        "姚", "卢", "傅", "钟", "姜", "崔", "谭", "廖", "范", "汪",
        "陆", "金", "石", "戴", "贾", "韦", "夏", "邱", "方", "侯",
        "邹", "熊", "孟", "秦", "白", "江", "阎", "薛", "尹", "段",
        "雷", "黎", "史", "龙", "贺", "顾", "毛", "郝", "龚", "邵",
        "万", "钱", "严", "覃", "武", "戚", "柳", "乔", "齐", "欧阳",
        # 101-200
        "洪", "康", "施", "龚", "颜", "倪", "龙", "万", "段", "雷",
        "钱", "汤", "尹", "黎", "易", "常", "武", "乔", "贺", "赖",
        "龚", "文", "庞", "樊", "兰", "殷", "施", "陶", "洪", "翟",
        "安", "颜", "倪", "严", "温", "芦", "季", "俞", "章", "鲁",
        "葛", "伍", "韦", "申", "尚", "董", "傅", "卜", "戚", "乌",
        "焦", "巴", "弓", "牧", "隗", "山", "谷", "车", "侯", "宓",
        "蓬", "全", "郗", "班", "仰", "秋", "仲", "伊", "宫", "宁",
        "仇", "栾", "暴", "甘", "钭", "厉", "戎", "祖", "武", "符",
        "刘", "景", "詹", "束", "龙", "叶", "幸", "司", "韶", "郜",
        "黎", "蓟", "薄", "印", "宿", "白", "怀", "蒲", "台", "丛",
        # 201-300
        "鄂", "索", "咸", "籍", "赖", "卓", "蔺", "屠", "蒙", "池",
        "乔", "阴", "郁", "胥", "能", "苍", "双", "闻", "莘", "党",
        "翟", "谭", "贡", "劳", "逄", "姬", "申", "扶", "堵", "冉",
        "宰", "郦", "雍", "却", "璩", "桑", "桂", "濮", "牛", "寿",
        "通", "边", "扈", "燕", "冀", "郏", "浦", "尚", "农", "温",
        "别", "庄", "晏", "柴", "瞿", "阎", "充", "慕", "连", "茹",
        "习", "宦", "艾", "鱼", "容", "向", "古", "易", "慎", "戈",
        "廖", "庚", "终", "暨", "居", "衡", "步", "都", "耿", "满",
        "弘", "匡", "国", "文", "寇", "广", "禄", "阙", "东", "殴",
        "殳", "沃", "利", "蔚", "越", "夔", "隆", "师", "巩", "厍",
        # 301-400
        "聂", "晁", "勾", "敖", "融", "冷", "訾", "辛", "阚", "那",
        "简", "饶", "空", "曾", "毋", "沙", "乜", "养", "鞠", "须",
        "丰", "巢", "关", "蒯", "相", "查", "後", "荆", "红", "游",
        "竺", "权", "逯", "盖", "益", "桓", "公", "万俟", "司马", "上官",
        "欧阳", "夏侯", "诸葛", "闻人", "东方", "赫连", "皇甫", "尉迟", "公羊", "澹台",
        "公冶", "宗政", "濮阳", "淳于", "单于", "太叔", "申屠", "公孙", "仲孙", "轩辕",
        "令狐", "钟离", "宇文", "长孙", "慕容", "鲜于", "闾丘", "司徒", "司空", "亓官",
        "司寇", "仉", "督", "子车", "颛孙", "端木", "巫马", "公西", "漆雕", "乐正",
        "壤驷", "公良", "拓跋", "夹谷", "宰父", "谷梁", "晋", "楚", "闫", "法",
        "汝", "鄢", "涂", "钦", "段干", "百里", "东郭", "南门", "呼延", "归海",
        # 401-500
        "羊舌", "微生", "岳", "帅", "缑", "亢", "况", "郈", "有", "琴",
        "梁丘", "左丘", "东门", "西门", "商", "牟", "佘", "佴", "伯", "赏",
        "南宫", "墨", "哈", "谯", "笪", "年", "爱", "阳", "佟", "言",
        "福", "南", "火", "铁", "迟", "漆", "卞", "康", "韦", "昌",
        "苗", "凤", "花", "方", "俞", "任", "袁", "柳", "酆", "鲍",
        "史", "唐", "费", "廉", "岑", "薛", "雷", "贺", "倪", "汤",
        "滕", "殷", "罗", "毕", "郝", "邬", "安", "常", "乐", "于",
        "时", "傅", "皮", "卞", "齐", "康", "伍", "余", "元", "卜",
        "顾", "孟", "平", "黄", "和", "穆", "萧", "尹", "姚", "邵",
        "湛", "汪", "祁", "毛", "禹", "狄", "米", "贝", "明", "臧",
    ]
    
    # 标准部门名称列表（30个）
    STANDARD_DEPARTMENTS = [
        "总经理办公室",
        "行政部",
        "人力资源部",
        "财务部",
        "采购部",
        "销售部",
        "市场部",
        "生产部",
        "质量管理部",
        "技术研发部",
        "工程部",
        "设备部",
        "安全环保部",
        "仓储物流部",
        "客户服务部",
        "审计部",
        "法务部",
        "信息技术部",
        "战略规划部",
        "品牌推广部",
        "供应链管理部",
        "品质保证部",
        "检验检测中心",
        "研发中心",
        "实验室",
        "培训中心",
        "售后服务部",
        "进出口部",
        "项目管理部",
        "综合管理部"
    ]
    
    # 设备关键词
    EQUIPMENT_KEYWORDS = [
        "设备", "机器", "仪器", "装置", "系统", "生产线", "机械",
        "压缩机", "泵", "阀门", "管道", "锅炉", "压力容器", "电梯",
        "起重机", "叉车", "输送带", "反应釜", "储罐", "换热器",
        "冷却塔", "风机", "空调", "变压器", "发电机", "配电柜"
    ]
    
    # 产品关键词
    PRODUCT_KEYWORDS = [
        "产品", "制品", "零件", "组件", "配件", "材料", "原料",
        "成品", "半成品", "零部件", "元器件", "包装", "辅料"
    ]
    
    def __init__(self):
        """初始化事实提取器"""
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        # 企业名称模式
        self.enterprise_pattern = re.compile(
            r'([^\s，。！？、]+(?:公司|集团|企业|厂|店|中心|研究院|研究所|事务所|合作社))'
        )
        
        # 地址模式
        self.address_pattern = re.compile(
            r'((?:中国)?[^\s，。！？、]*(?:省|市|自治区|特别行政区|县|区|镇|乡|街道|路|街|号|栋|层|室))'
        )
        
        # 电话模式
        self.phone_pattern = re.compile(
            r'(?:电话|联系方式|手机|固话|Tel|Phone)[：:]\s*([0-9\-+()\s]{7,20})|'
            r'(\+?86[-\s]?1[3-9]\d{9})|'
            r'(\d{3,4}[-\s]?\d{7,8})'
        )
        
        # 邮箱模式
        self.email_pattern = re.compile(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        )
        
        # 人数模式
        self.employee_count_pattern = re.compile(
            r'(?:员工|职工|人员|人数|职工人数|员工总数)[：:]*\s*(\d+)[人名]?|'
            r'(?:现有|共有|拥有)\s*(\d+)\s*(?:名|位|个)?(?:员工|职工|人员)'
        )
        
        # 日期模式
        self.date_pattern = re.compile(
            r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)|'
            r'(\d{1,2}[-/月]\d{1,2}[-/日]?)'
        )
        
        # 证书模式
        self.certificate_pattern = re.compile(
            r'([^\s，。！？、]*(?:证书|认证|许可证|资质|执照|资格证书))'
        )
        
        # 人名模式（中文姓名）
        self.person_name_pattern = re.compile(
            r'(?:负责人|经理|主管|主任|工程师|技术员|操作员|员工|联系人)[：:]\s*([^\s，。！？、]{2,4})'
        )
        
        # 部门模式
        self.department_pattern = re.compile(
            r'([^\s，。！？、]*(?:部|处|科|室|中心|组|班|车间|分公司|分厂))'
        )
    
    def extract_from_text(self, text: str, source: FactSource = FactSource.USER_INPUT) -> List[Fact]:
        """
        从文本提取事实
        
        Args:
            text: 输入文本
            source: 事实来源
            
        Returns:
            提取的事实列表
        """
        facts = []
        fact_id_counter = 0
        
        # 提取企业名称
        enterprise_facts = self._extract_enterprise_names(text, source)
        for fact in enterprise_facts:
            fact.fact_id = f"fact_{fact_id_counter}"
            fact_id_counter += 1
            facts.append(fact)
        
        # 提取地址
        address_facts = self._extract_addresses(text, source)
        for fact in address_facts:
            fact.fact_id = f"fact_{fact_id_counter}"
            fact_id_counter += 1
            facts.append(fact)
        
        # 提取人数
        employee_facts = self._extract_employee_count(text, source)
        for fact in employee_facts:
            fact.fact_id = f"fact_{fact_id_counter}"
            fact_id_counter += 1
            facts.append(fact)
        
        # 提取部门名称
        dept_facts = self.extract_department_names(text, source)
        for fact in dept_facts:
            fact.fact_id = f"fact_{fact_id_counter}"
            fact_id_counter += 1
            facts.append(fact)
        
        # 提取人名
        person_facts = self.extract_person_names(text, source)
        for fact in person_facts:
            fact.fact_id = f"fact_{fact_id_counter}"
            fact_id_counter += 1
            facts.append(fact)
        
        # 提取电话
        phone_facts = self._extract_phones(text, source)
        for fact in phone_facts:
            fact.fact_id = f"fact_{fact_id_counter}"
            fact_id_counter += 1
            facts.append(fact)
        
        # 提取邮箱
        email_facts = self._extract_emails(text, source)
        for fact in email_facts:
            fact.fact_id = f"fact_{fact_id_counter}"
            fact_id_counter += 1
            facts.append(fact)
        
        # 提取日期
        date_facts = self._extract_dates(text, source)
        for fact in date_facts:
            fact.fact_id = f"fact_{fact_id_counter}"
            fact_id_counter += 1
            facts.append(fact)
        
        # 提取设备清单
        equipment_facts = self.extract_equipment_list(text, source)
        for fact in equipment_facts:
            fact.fact_id = f"fact_{fact_id_counter}"
            fact_id_counter += 1
            facts.append(fact)
        
        # 提取产品信息
        product_facts = self.extract_product_info(text, source)
        for fact in product_facts:
            fact.fact_id = f"fact_{fact_id_counter}"
            fact_id_counter += 1
            facts.append(fact)
        
        logger.info(f"从文本中提取了 {len(facts)} 个事实")
        return facts
    
    def extract_from_document(self, document_path: str, source: FactSource = FactSource.DOCUMENT) -> List[Fact]:
        """
        从文档提取事实
        
        Args:
            document_path: 文档路径
            source: 事实来源
            
        Returns:
            提取的事实列表
        """
        import os
        
        facts = []
        
        try:
            # 根据文件类型选择解析方式
            _, ext = os.path.splitext(document_path)
            ext = ext.lower()
            
            if ext in ['.txt', '.md']:
                with open(document_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                facts = self.extract_from_text(text, source)
            
            elif ext in ['.docx', '.doc']:
                # 使用python-docx解析Word文档
                try:
                    from docx import Document
                    doc = Document(document_path)
                    text = '\n'.join([para.text for para in doc.paragraphs])
                    facts = self.extract_from_text(text, source)
                except ImportError:
                    logger.warning("未安装python-docx库，无法解析Word文档")
            
            elif ext in ['.xlsx', '.xls']:
                # 使用openpyxl解析Excel文档
                try:
                    import openpyxl
                    wb = openpyxl.load_workbook(document_path)
                    text_parts = []
                    for sheet in wb.worksheets:
                        for row in sheet.iter_rows(values_only=True):
                            text_parts.append(' '.join([str(cell) if cell else '' for cell in row]))
                    text = '\n'.join(text_parts)
                    facts = self.extract_from_text(text, source)
                except ImportError:
                    logger.warning("未安装openpyxl库，无法解析Excel文档")
            
            elif ext == '.pdf':
                # 使用PyPDF2解析PDF文档
                try:
                    import PyPDF2
                    with open(document_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text_parts = [page.extract_text() for page in reader.pages]
                        text = '\n'.join(text_parts)
                        facts = self.extract_from_text(text, source)
                except ImportError:
                    logger.warning("未安装PyPDF2库，无法解析PDF文档")
            
            else:
                logger.warning(f"不支持的文件类型: {ext}")
            
            # 添加文档元数据
            for fact in facts:
                fact.metadata['document_path'] = document_path
                fact.metadata['document_type'] = ext
            
        except Exception as e:
            logger.error(f"从文档提取事实失败: {e}")
        
        return facts
    
    def extract_person_names(self, text: str, source: FactSource = FactSource.USER_INPUT) -> List[Fact]:
        """
        提取人名
        
        Args:
            text: 输入文本
            source: 事实来源
            
        Returns:
            人名事实列表
        """
        facts = []
        
        # 方法1：通过职位关键词提取
        matches = self.person_name_pattern.finditer(text)
        for match in matches:
            name = match.group(1)
            if self._is_valid_person_name(name):
                fact = Fact(
                    fact_id="",
                    fact_type=FactType.PERSON_NAME,
                    content=name,
                    source=source,
                    confidence=0.8,
                    context=text[max(0, match.start()-20):match.end()+20],
                    position=(match.start(), match.end())
                )
                facts.append(fact)
        
        # 方法2：通过姓氏匹配提取
        for surname in self.COMMON_SURNAMES:
            # 匹配姓氏+1-2个字的模式
            pattern = re.compile(f'{surname}[\u4e00-\u9fa5]{{1,2}}')
            matches = pattern.finditer(text)
            for match in matches:
                name = match.group()
                # 检查是否已被提取
                if not any(f.content == name for f in facts):
                    if self._is_valid_person_name(name):
                        fact = Fact(
                            fact_id="",
                            fact_type=FactType.PERSON_NAME,
                            content=name,
                            source=source,
                            confidence=0.7,
                            context=text[max(0, match.start()-10):match.end()+10],
                            position=(match.start(), match.end())
                        )
                        facts.append(fact)
        
        return facts
    
    def _is_valid_person_name(self, name: str) -> bool:
        """
        验证是否为有效人名
        
        Args:
            name: 待验证的姓名
            
        Returns:
            是否为有效人名
        """
        if not name or len(name) < 2 or len(name) > 4:
            return False
        
        # 检查是否以常见姓氏开头
        has_valid_surname = any(name.startswith(surname) for surname in self.COMMON_SURNAMES)
        if not has_valid_surname:
            return False
        
        # 检查是否包含非姓名字符
        invalid_chars = ['公司', '部门', '企业', '有限', '责任', '集团', '股份']
        if any(char in name for char in invalid_chars):
            return False
        
        return True
    
    def extract_department_names(self, text: str, source: FactSource = FactSource.USER_INPUT) -> List[Fact]:
        """
        提取部门名称
        
        Args:
            text: 输入文本
            source: 事实来源
            
        Returns:
            部门名称事实列表
        """
        facts = []
        
        # 方法1：匹配标准部门名称
        for dept in self.STANDARD_DEPARTMENTS:
            if dept in text:
                matches = [m.start() for m in re.finditer(re.escape(dept), text)]
                for start in matches:
                    fact = Fact(
                        fact_id="",
                        fact_type=FactType.DEPARTMENT,
                        content=dept,
                        source=source,
                        confidence=0.95,
                        context=text[max(0, start-20):start+len(dept)+20],
                        position=(start, start + len(dept))
                    )
                    facts.append(fact)
        
        # 方法2：通过正则模式匹配
        matches = self.department_pattern.finditer(text)
        for match in matches:
            dept_name = match.group(1)
            # 检查是否已被提取
            if not any(f.content == dept_name for f in facts):
                # 验证是否为有效部门名称
                if self._is_valid_department(dept_name):
                    fact = Fact(
                        fact_id="",
                        fact_type=FactType.DEPARTMENT,
                        content=dept_name,
                        source=source,
                        confidence=0.8,
                        context=text[max(0, match.start()-20):match.end()+20],
                        position=(match.start(), match.end())
                    )
                    facts.append(fact)
        
        return facts
    
    def _is_valid_department(self, dept_name: str) -> bool:
        """
        验证是否为有效部门名称
        
        Args:
            dept_name: 待验证的部门名称
            
        Returns:
            是否为有效部门名称
        """
        if not dept_name or len(dept_name) < 3:
            return False
        
        # 排除一些误匹配
        invalid_patterns = ['全部', '部分', '大部', '支部', '支部书记']
        if any(pattern in dept_name for pattern in invalid_patterns):
            return False
        
        return True
    
    def extract_equipment_list(self, text: str, source: FactSource = FactSource.USER_INPUT) -> List[Fact]:
        """
        提取设备清单
        
        Args:
            text: 输入文本
            source: 事实来源
            
        Returns:
            设备事实列表
        """
        facts = []
        
        # 设备名称模式
        equipment_pattern = re.compile(
            r'([^\s，。！？、]{2,20}(?:' + '|'.join(self.EQUIPMENT_KEYWORDS) + '))'
        )
        
        matches = equipment_pattern.finditer(text)
        for match in matches:
            equipment_name = match.group(1)
            fact = Fact(
                fact_id="",
                fact_type=FactType.EQUIPMENT,
                content=equipment_name,
                source=source,
                confidence=0.8,
                context=text[max(0, match.start()-30):match.end()+30],
                position=(match.start(), match.end()),
                metadata={"equipment_type": self._classify_equipment(equipment_name)}
            )
            facts.append(fact)
        
        # 提取设备数量信息
        quantity_pattern = re.compile(
            r'([^\s，。！？、]{2,10}(?:设备|机器|仪器|装置))[：:]*\s*(\d+)[台套件]'
        )
        matches = quantity_pattern.finditer(text)
        for match in matches:
            equipment_name = match.group(1)
            quantity = int(match.group(2))
            
            # 更新已有事实或创建新事实
            existing = next((f for f in facts if f.content == equipment_name), None)
            if existing:
                existing.metadata['quantity'] = quantity
            else:
                fact = Fact(
                    fact_id="",
                    fact_type=FactType.EQUIPMENT,
                    content=equipment_name,
                    source=source,
                    confidence=0.85,
                    context=text[max(0, match.start()-30):match.end()+30],
                    position=(match.start(), match.end()),
                    metadata={"quantity": quantity}
                )
                facts.append(fact)
        
        return facts
    
    def _classify_equipment(self, equipment_name: str) -> str:
        """
        分类设备类型
        
        Args:
            equipment_name: 设备名称
            
        Returns:
            设备类型
        """
        if any(kw in equipment_name for kw in ['压缩', '泵', '风机']):
            return "动力设备"
        elif any(kw in equipment_name for kw in ['锅炉', '压力容器', '储罐']):
            return "特种设备"
        elif any(kw in equipment_name for kw in ['电梯', '起重', '叉车']):
            return "起重运输设备"
        elif any(kw in equipment_name for kw in ['配电', '变压器', '发电机']):
            return "电气设备"
        elif any(kw in equipment_name for kw in ['检测', '检验', '测量', '仪器']):
            return "检测设备"
        else:
            return "生产设备"
    
    def extract_product_info(self, text: str, source: FactSource = FactSource.USER_INPUT) -> List[Fact]:
        """
        提取产品信息
        
        Args:
            text: 输入文本
            source: 事实来源
            
        Returns:
            产品事实列表
        """
        facts = []
        
        # 产品名称模式
        product_pattern = re.compile(
            r'(?:主要|主营|生产|销售)?[产品][：:]*\s*([^\s，。！？、]{2,30})|'
            r'([^\s，。！？、]{2,20}(?:产品|制品|零件|组件))'
        )
        
        matches = product_pattern.finditer(text)
        for match in matches:
            product_name = match.group(1) or match.group(2)
            if product_name:
                fact = Fact(
                    fact_id="",
                    fact_type=FactType.PRODUCT,
                    content=product_name,
                    source=source,
                    confidence=0.8,
                    context=text[max(0, match.start()-30):match.end()+30],
                    position=(match.start(), match.end())
                )
                facts.append(fact)
        
        # 提取产品规格信息
        spec_pattern = re.compile(
            r'([^\s，。！？、]{2,20})[：:]*\s*(?:规格|型号|参数)[：:]*\s*([^\s，。！？、]+)'
        )
        matches = spec_pattern.finditer(text)
        for match in matches:
            product_name = match.group(1)
            spec = match.group(2)
            
            # 更新已有事实或创建新事实
            existing = next((f for f in facts if product_name in f.content), None)
            if existing:
                existing.metadata['specification'] = spec
            else:
                fact = Fact(
                    fact_id="",
                    fact_type=FactType.PRODUCT,
                    content=product_name,
                    source=source,
                    confidence=0.75,
                    context=text[max(0, match.start()-30):match.end()+30],
                    position=(match.start(), match.end()),
                    metadata={"specification": spec}
                )
                facts.append(fact)
        
        return facts
    
    def _extract_enterprise_names(self, text: str, source: FactSource) -> List[Fact]:
        """提取企业名称"""
        facts = []
        matches = self.enterprise_pattern.finditer(text)
        for match in matches:
            name = match.group(1)
            if len(name) >= 4:  # 企业名称至少4个字符
                fact = Fact(
                    fact_id="",
                    fact_type=FactType.ENTERPRISE_NAME,
                    content=name,
                    source=source,
                    confidence=0.9,
                    context=text[max(0, match.start()-20):match.end()+20],
                    position=(match.start(), match.end())
                )
                facts.append(fact)
        return facts
    
    def _extract_addresses(self, text: str, source: FactSource) -> List[Fact]:
        """提取地址"""
        facts = []
        matches = self.address_pattern.finditer(text)
        for match in matches:
            address = match.group(1)
            if len(address) >= 4:  # 地址至少4个字符
                fact = Fact(
                    fact_id="",
                    fact_type=FactType.ADDRESS,
                    content=address,
                    source=source,
                    confidence=0.85,
                    context=text[max(0, match.start()-20):match.end()+20],
                    position=(match.start(), match.end())
                )
                facts.append(fact)
        return facts
    
    def _extract_employee_count(self, text: str, source: FactSource) -> List[Fact]:
        """提取人数"""
        facts = []
        matches = self.employee_count_pattern.finditer(text)
        for match in matches:
            count = match.group(1) or match.group(2)
            if count:
                fact = Fact(
                    fact_id="",
                    fact_type=FactType.EMPLOYEE_COUNT,
                    content=count + "人",
                    source=source,
                    confidence=0.9,
                    context=text[max(0, match.start()-20):match.end()+20],
                    position=(match.start(), match.end()),
                    metadata={"count": int(count)}
                )
                facts.append(fact)
        return facts
    
    def _extract_phones(self, text: str, source: FactSource) -> List[Fact]:
        """提取电话"""
        facts = []
        matches = self.phone_pattern.finditer(text)
        for match in matches:
            phone = match.group(1) or match.group(2) or match.group(3)
            if phone:
                fact = Fact(
                    fact_id="",
                    fact_type=FactType.PHONE,
                    content=phone.strip(),
                    source=source,
                    confidence=0.9,
                    context=text[max(0, match.start()-20):match.end()+20],
                    position=(match.start(), match.end())
                )
                facts.append(fact)
        return facts
    
    def _extract_emails(self, text: str, source: FactSource) -> List[Fact]:
        """提取邮箱"""
        facts = []
        matches = self.email_pattern.finditer(text)
        for match in matches:
            email = match.group()
            fact = Fact(
                fact_id="",
                fact_type=FactType.EMAIL,
                content=email,
                source=source,
                confidence=0.95,
                context=text[max(0, match.start()-20):match.end()+20],
                position=(match.start(), match.end())
            )
            facts.append(fact)
        return facts
    
    def _extract_dates(self, text: str, source: FactSource) -> List[Fact]:
        """提取日期"""
        facts = []
        matches = self.date_pattern.finditer(text)
        for match in matches:
            date_str = match.group(1) or match.group(2)
            if date_str:
                fact = Fact(
                    fact_id="",
                    fact_type=FactType.DATE,
                    content=date_str,
                    source=source,
                    confidence=0.85,
                    context=text[max(0, match.start()-20):match.end()+20],
                    position=(match.start(), match.end())
                )
                facts.append(fact)
        return facts
    
    def get_fact_summary(self, facts: List[Fact]) -> Dict[str, Any]:
        """
        获取事实摘要
        
        Args:
            facts: 事实列表
            
        Returns:
            摘要字典
        """
        summary = {
            "total_count": len(facts),
            "by_type": {},
            "by_source": {},
            "high_confidence_count": 0,
            "verified_count": 0
        }
        
        for fact in facts:
            # 按类型统计
            type_name = fact.fact_type.value
            if type_name not in summary["by_type"]:
                summary["by_type"][type_name] = []
            summary["by_type"][type_name].append(fact.content)
            
            # 按来源统计
            source_name = fact.source.value
            summary["by_source"][source_name] = summary["by_source"].get(source_name, 0) + 1
            
            # 高置信度统计
            if fact.confidence >= 0.8:
                summary["high_confidence_count"] += 1
            
            # 已验证统计
            if fact.is_verified:
                summary["verified_count"] += 1
        
        return summary
