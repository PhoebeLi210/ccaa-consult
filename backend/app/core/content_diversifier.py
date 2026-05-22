"""
内容差异化模块
用于解决文档内容雷同问题，提供同义词替换、句子结构调整等功能
"""

import random
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class IndustryType(Enum):
    """行业类型枚举"""
    MANUFACTURING = "manufacturing"  # 制造业
    SERVICE = "service"              # 服务业
    CONSTRUCTION = "construction"    # 建筑业
    GENERAL = "general"              # 通用


@dataclass
class DiversificationResult:
    """差异化结果数据类"""
    original_text: str
    diversified_text: str
    changes_made: List[str]
    industry: str
    confidence_score: float


class ContentDiversifier:
    """内容差异化处理器类"""
    
    # 行业专业术语映射字典
    INDUSTRY_TERMS = {
        IndustryType.MANUFACTURING: {
            # 制造业术语映射
            "产品": ["制品", "制成品", "产出物", "生产物", "成品"],
            "生产": ["制造", "加工", "制作", "产出", "批量生产"],
            "设备": ["机器", "机械", "装置", "装备", "生产设备"],
            "工艺": ["工序", "流程", "制程", "技术路线", "加工方法"],
            "质量": ["品质", "品控", "质量水平", "良品率", "质量指标"],
            "检验": ["检测", "检查", "质检", "品检", "验收"],
            "原料": ["原材料", "物料", "材料", "基材", "原料件"],
            "供应商": ["供方", "供货方", "协作厂", "配套厂", "物料供应商"],
            "客户": ["客户方", "订货方", "采购方", "使用方", "需求方"],
            "改进": ["改善", "优化", "提升", "革新", "技术改造"],
            "管理": ["管控", "治理", "监督", "统筹", "协调"],
            "标准": ["规范", "规程", "准则", "基准", "技术要求"],
            "问题": ["异常", "缺陷", "不良", "偏差", "不符合项"],
            "解决": ["处理", "处置", "纠正", "整改", "修复"],
            "控制": ["管控", "调节", "把握", "掌握", "监控"],
            "流程": ["工序", "步骤", "环节", "程序", "作业顺序"],
            "效率": ["生产率", "产出率", "效能", "效益", "工作效率"],
            "安全": ["安健环", "安全生产", "职业安全", "安全防护", "风险防控"],
            "环境": ["环保", "环境保护", "清洁生产", "绿色制造", "节能减排"]
        },
        IndustryType.SERVICE: {
            # 服务业术语映射
            "产品": ["服务", "服务项目", "服务产品", "交付物", "成果"],
            "生产": ["提供", "交付", "实施", "执行", "完成"],
            "设备": ["设施", "硬件", "工具", "系统", "服务平台"],
            "工艺": ["流程", "服务流程", "作业规范", "服务标准", "操作规程"],
            "质量": ["服务质量", "满意度", "体验", "服务水准", "服务品质"],
            "检验": ["评价", "评估", "反馈", "回访", "满意度调查"],
            "原料": ["资源", "信息", "数据", "需求", "输入"],
            "供应商": ["合作方", "外包方", "服务商", "协作单位", "合作伙伴"],
            "客户": ["顾客", "用户", "服务对象", "委托方", "需求方"],
            "改进": ["优化", "提升", "完善", "精进", "服务升级"],
            "管理": ["运营", "统筹", "协调", "管控", "服务管理"],
            "标准": ["规范", "服务标准", "服务准则", "服务承诺", "服务条款"],
            "问题": ["投诉", "意见", "建议", "不满", "服务缺陷"],
            "解决": ["处理", "回应", "满足", "解决", "妥善处理"],
            "控制": ["把控", "掌握", "管理", "监督", "确保"],
            "流程": ["服务流程", "服务环节", "服务步骤", "服务程序", "服务链路"],
            "效率": ["响应速度", "处理时效", "服务效率", "办结率", "及时率"],
            "安全": ["信息安全", "隐私保护", "服务安全", "风险防控", "合规"],
            "环境": ["服务环境", "体验环境", "软环境", "氛围", "服务场景"]
        },
        IndustryType.CONSTRUCTION: {
            # 建筑业术语映射
            "产品": ["工程", "项目", "建筑物", "构筑物", "建设成果"],
            "生产": ["施工", "建造", "建设", "实施", "作业"],
            "设备": ["机械", "机具", "施工设备", "工程机械", "施工机械"],
            "工艺": ["工法", "施工方法", "施工工艺", "施工技术", "作业方法"],
            "质量": ["工程质量", "施工质量", "质量水平", "品质", "质量指标"],
            "检验": ["验收", "检查", "检测", "试验", "质量验收"],
            "原料": ["材料", "建材", "建筑材料", "构配件", "原材料"],
            "供应商": ["供货商", "材料商", "分包商", "协作单位", "供应单位"],
            "客户": ["业主", "建设单位", "甲方", "发包方", "委托方"],
            "改进": ["优化", "改良", "技术改进", "工艺改进", "质量提升"],
            "管理": ["管控", "监管", "治理", "统筹", "项目管理"],
            "标准": ["规范", "规程", "标准", "技术标准", "施工规范"],
            "问题": ["缺陷", "隐患", "不合格", "质量问题", "质量缺陷"],
            "解决": ["整改", "返工", "修复", "处理", "纠正"],
            "控制": ["管控", "把控", "监控", "管理", "质量监督"],
            "流程": ["工序", "施工流程", "作业流程", "施工顺序", "工艺流程"],
            "效率": ["进度", "工期", "施工效率", "作业效率", "工效"],
            "安全": ["施工安全", "安全生产", "安全文明", "安全防护", "安全管理"],
            "环境": ["文明施工", "环境保护", "绿色施工", "环保", "施工现场环境"]
        },
        IndustryType.GENERAL: {
            # 通用术语映射
            "产品": ["产品", "成果", "输出", "交付物"],
            "生产": ["生产", "制造", "提供", "完成"],
            "设备": ["设备", "设施", "工具", "资源"],
            "工艺": ["工艺", "流程", "方法", "技术"],
            "质量": ["质量", "品质", "水平", "标准"],
            "检验": ["检验", "检查", "检测", "验证"],
            "原料": ["原料", "材料", "资源", "输入"],
            "供应商": ["供应商", "供方", "合作方", "协作方"],
            "客户": ["客户", "顾客", "用户", "需求方"],
            "改进": ["改进", "改善", "优化", "提升"],
            "管理": ["管理", "管控", "治理", "监督"],
            "标准": ["标准", "规范", "准则", "要求"],
            "问题": ["问题", "缺陷", "异常", "不符合"],
            "解决": ["解决", "处理", "纠正", "整改"],
            "控制": ["控制", "管控", "管理", "监督"],
            "流程": ["流程", "程序", "步骤", "环节"],
            "效率": ["效率", "效益", "效能", "产出"],
            "安全": ["安全", "安健环", "防护", "保障"],
            "环境": ["环境", "环保", "生态", "绿色"]
        }
    }
    
    # 句式转换模板
    SENTENCE_TEMPLATES = {
        "active_to_passive": [
            ("我们", "由"),
            ("公司", "由本公司"),
            ("部门", "由该部门"),
            ("负责", "负责实施"),
            ("执行", "被执行"),
            ("完成", "被完成"),
            ("制定", "被制定"),
            ("实施", "被实施")
        ],
        "short_to_long": [
            "为进一步加强",
            "为了确保",
            "为了有效实施",
            "基于上述考虑",
            "鉴于此",
            "综上所述"
        ],
        "long_to_short": [
            "简言之",
            "即",
            "也就是说",
            "总之"
        ]
    }
    
    def __init__(self, random_seed: Optional[int] = None):
        """
        初始化内容差异化处理器
        
        Args:
            random_seed: 随机种子，用于可复现的结果
        """
        if random_seed is not None:
            random.seed(random_seed)
        self.processing_history: List[DiversificationResult] = []
    
    def diversify_expression(
        self, 
        text: str, 
        industry: str = "general",
        replacement_ratio: float = 0.3
    ) -> DiversificationResult:
        """
        根据行业替换同义词
        
        Args:
            text: 原始文本
            industry: 行业类型 (manufacturing/service/construction/general)
            replacement_ratio: 替换比例，0-1之间
            
        Returns:
            DiversificationResult: 差异化结果
        """
        # 映射行业字符串到枚举
        industry_map = {
            "manufacturing": IndustryType.MANUFACTURING,
            "制造业": IndustryType.MANUFACTURING,
            "service": IndustryType.SERVICE,
            "服务业": IndustryType.SERVICE,
            "construction": IndustryType.CONSTRUCTION,
            "建筑业": IndustryType.CONSTRUCTION,
            "general": IndustryType.GENERAL,
            "通用": IndustryType.GENERAL
        }
        
        industry_type = industry_map.get(industry.lower(), IndustryType.GENERAL)
        terms = self.INDUSTRY_TERMS[industry_type]
        
        diversified_text = text
        changes_made = []
        
        # 统计可替换的词
        replaceable_words = []
        for word, alternatives in terms.items():
            if word in diversified_text and len(alternatives) > 1:
                replaceable_words.append(word)
        
        # 根据替换比例选择要替换的词
        num_to_replace = max(1, int(len(replaceable_words) * replacement_ratio))
        words_to_replace = random.sample(
            replaceable_words, 
            min(num_to_replace, len(replaceable_words))
        ) if replaceable_words else []
        
        # 执行替换
        for word in words_to_replace:
            alternatives = [a for a in terms[word] if a != word]
            if alternatives:
                replacement = random.choice(alternatives)
                # 只替换部分出现，保持多样性
                occurrences = diversified_text.count(word)
                if occurrences > 0:
                    replace_count = max(1, occurrences // 2)
                    diversified_text = diversified_text.replace(
                        word, replacement, replace_count
                    )
                    changes_made.append(f"'{word}' -> '{replacement}'")
        
        # 计算置信度分数
        confidence = min(1.0, len(changes_made) / max(1, len(replaceable_words)) + 0.5)
        
        result = DiversificationResult(
            original_text=text,
            diversified_text=diversified_text,
            changes_made=changes_made,
            industry=industry_type.value,
            confidence_score=round(confidence, 2)
        )
        
        self.processing_history.append(result)
        return result
    
    def add_company_specifics(
        self, 
        text: str, 
        company_info: Dict[str, Any]
    ) -> DiversificationResult:
        """
        将企业具体信息融入内容
        
        Args:
            text: 原始文本
            company_info: 企业信息字典，可包含：
                - name: 公司名称
                - products: 产品列表
                - equipment: 设备列表
                - processes: 工艺列表
                - location: 地点
                - scale: 规模
                
        Returns:
            DiversificationResult: 差异化结果
        """
        diversified_text = text
        changes_made = []
        
        # 替换公司名称占位符或添加公司名
        if 'name' in company_info:
            company_name = company_info['name']
            # 替换通用占位符
            placeholders = ['[公司名称]', 'XX公司', '某某公司', '该公司']
            for placeholder in placeholders:
                if placeholder in diversified_text:
                    diversified_text = diversified_text.replace(placeholder, company_name)
                    changes_made.append(f"替换占位符 '{placeholder}' -> '{company_name}'")
            
            # 在适当位置插入公司名
            if company_name not in diversified_text and random.random() > 0.5:
                sentences = diversified_text.split('。')
                if len(sentences) > 1:
                    insert_pos = random.randint(0, min(2, len(sentences) - 1))
                    sentences[insert_pos] = f"{company_name}{sentences[insert_pos]}"
                    diversified_text = '。'.join(sentences)
                    changes_made.append(f"插入公司名称: {company_name}")
        
        # 融入产品信息
        if 'products' in company_info and company_info['products']:
            products = company_info['products']
            product_placeholders = ['[产品]', 'XX产品', '主要产品']
            for placeholder in product_placeholders:
                if placeholder in diversified_text:
                    product_str = '、'.join(products[:3])  # 最多3个产品
                    diversified_text = diversified_text.replace(placeholder, product_str)
                    changes_made.append(f"替换产品占位符 -> '{product_str}'")
        
        # 融入设备信息
        if 'equipment' in company_info and company_info['equipment']:
            equipment = company_info['equipment']
            equipment_placeholders = ['[设备]', 'XX设备', '主要设备']
            for placeholder in equipment_placeholders:
                if placeholder in diversified_text:
                    equipment_str = '、'.join(equipment[:3])
                    diversified_text = diversified_text.replace(placeholder, equipment_str)
                    changes_made.append(f"替换设备占位符 -> '{equipment_str}'")
        
        # 融入工艺信息
        if 'processes' in company_info and company_info['processes']:
            processes = company_info['processes']
            process_placeholders = ['[工艺]', 'XX工艺', '生产工艺']
            for placeholder in process_placeholders:
                if placeholder in diversified_text:
                    process_str = '、'.join(processes[:3])
                    diversified_text = diversified_text.replace(placeholder, process_str)
                    changes_made.append(f"替换工艺占位符 -> '{process_str}'")
        
        # 融入地点信息
        if 'location' in company_info:
            location = company_info['location']
            location_placeholders = ['[地点]', 'XX地区', '当地']
            for placeholder in location_placeholders:
                if placeholder in diversified_text:
                    diversified_text = diversified_text.replace(placeholder, location)
                    changes_made.append(f"替换地点占位符 -> '{location}'")
        
        # 融入规模信息
        if 'scale' in company_info:
            scale = company_info['scale']
            scale_placeholders = ['[规模]', 'XX规模']
            for placeholder in scale_placeholders:
                if placeholder in diversified_text:
                    diversified_text = diversified_text.replace(placeholder, scale)
                    changes_made.append(f"替换规模占位符 -> '{scale}'")
        
        confidence = min(1.0, 0.6 + len(changes_made) * 0.1)
        
        result = DiversificationResult(
            original_text=text,
            diversified_text=diversified_text,
            changes_made=changes_made,
            industry="custom",
            confidence_score=round(confidence, 2)
        )
        
        self.processing_history.append(result)
        return result
    
    def randomize_sentence_structure(self, text: str) -> DiversificationResult:
        """
        随机调整句子结构（主动/被动、长短句交替）
        
        Args:
            text: 原始文本
            
        Returns:
            DiversificationResult: 差异化结果
        """
        sentences = re.split(r'([。！？])', text)
        sentences = [''.join(i) for i in zip(sentences[::2], sentences[1::2] + [''])]
        sentences = [s for s in sentences if s.strip()]
        
        diversified_sentences = []
        changes_made = []
        
        for i, sentence in enumerate(sentences):
            diversified = sentence
            
            # 随机决定是否转换句式
            if random.random() > 0.6:
                # 主动转被动或被动转主动
                if '由' in sentence and random.random() > 0.5:
                    # 被动转主动
                    diversified = re.sub(r'由([^，。]+)(负责|执行|完成)', r'\1\2', diversified)
                    changes_made.append(f"句子{i+1}: 被动转主动")
                elif random.random() > 0.5:
                    # 主动转被动
                    diversified = re.sub(r'(我们|公司|部门)(负责|执行|完成)', r'由\1\2', diversified)
                    changes_made.append(f"句子{i+1}: 主动转被动")
            
            # 长短句交替调整
            if len(diversified) > 30 and random.random() > 0.7:
                # 长句拆分
                connectors = self.SENTENCE_TEMPLATES["long_to_short"]
                connector = random.choice(connectors)
                diversified = diversified.replace('，', f'，{connector}')
                changes_made.append(f"句子{i+1}: 长句简化")
            elif len(diversified) < 15 and i > 0 and random.random() > 0.7:
                # 短句扩展
                connectors = self.SENTENCE_TEMPLATES["short_to_long"]
                connector = random.choice(connectors)
                diversified = connector + '，' + diversified
                changes_made.append(f"句子{i+1}: 短句扩展")
            
            diversified_sentences.append(diversified)
        
        diversified_text = ''.join(diversified_sentences)
        
        result = DiversificationResult(
            original_text=text,
            diversified_text=diversified_text,
            changes_made=changes_made,
            industry="structure",
            confidence_score=0.75
        )
        
        self.processing_history.append(result)
        return result
    
    def generate_variants(
        self, 
        template: str, 
        count: int = 3,
        industry: str = "general",
        company_info: Optional[Dict[str, Any]] = None
    ) -> List[DiversificationResult]:
        """
        生成同一模板的多个不同变体
        
        Args:
            template: 模板文本
            count: 生成变体数量，默认3个
            industry: 行业类型
            company_info: 企业信息（可选）
            
        Returns:
            List[DiversificationResult]: 变体结果列表
        """
        variants = []
        
        for i in range(count):
            # 每次使用不同的随机策略
            current_text = template
            all_changes = []
            
            # 步骤1: 行业术语替换（不同比例）
            replacement_ratio = 0.2 + (i * 0.15)  # 0.2, 0.35, 0.5
            result1 = self.diversify_expression(
                current_text, 
                industry, 
                replacement_ratio
            )
            current_text = result1.diversified_text
            all_changes.extend(result1.changes_made)
            
            # 步骤2: 添加企业信息（如果有）
            if company_info:
                result2 = self.add_company_specifics(current_text, company_info)
                current_text = result2.diversified_text
                all_changes.extend(result2.changes_made)
            
            # 步骤3: 调整句子结构
            result3 = self.randomize_sentence_structure(current_text)
            current_text = result3.diversified_text
            all_changes.extend(result3.changes_made)
            
            # 创建变体结果
            variant = DiversificationResult(
                original_text=template,
                diversified_text=current_text,
                changes_made=all_changes,
                industry=industry,
                confidence_score=round(0.5 + len(all_changes) * 0.05, 2)
            )
            
            variants.append(variant)
        
        return variants
    
    def get_diversification_stats(self) -> Dict[str, Any]:
        """
        获取差异化处理统计信息
        
        Returns:
            Dict: 统计信息
        """
        if not self.processing_history:
            return {
                "total_processed": 0,
                "avg_changes": 0,
                "avg_confidence": 0
            }
        
        total = len(self.processing_history)
        total_changes = sum(len(r.changes_made) for r in self.processing_history)
        total_confidence = sum(r.confidence_score for r in self.processing_history)
        
        return {
            "total_processed": total,
            "avg_changes": round(total_changes / total, 2),
            "avg_confidence": round(total_confidence / total, 2),
            "industries_used": list(set(r.industry for r in self.processing_history))
        }


# 便捷函数接口
def diversify_expression(
    text: str, 
    industry: str = "general",
    replacement_ratio: float = 0.3
) -> DiversificationResult:
    """内容差异化的便捷函数"""
    diversifier = ContentDiversifier()
    return diversifier.diversify_expression(text, industry, replacement_ratio)


def add_company_specifics(
    text: str, 
    company_info: Dict[str, Any]
) -> DiversificationResult:
    """添加企业信息的便捷函数"""
    diversifier = ContentDiversifier()
    return diversifier.add_company_specifics(text, company_info)


def randomize_sentence_structure(text: str) -> DiversificationResult:
    """随机调整句子结构的便捷函数"""
    diversifier = ContentDiversifier()
    return diversifier.randomize_sentence_structure(text)


def generate_variants(
    template: str, 
    count: int = 3,
    industry: str = "general",
    company_info: Optional[Dict[str, Any]] = None
) -> List[DiversificationResult]:
    """生成变体的便捷函数"""
    diversifier = ContentDiversifier()
    return diversifier.generate_variants(template, count, industry, company_info)
