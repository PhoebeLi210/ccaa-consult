"""
风格学习服务模块

用于学习咨询顾问的写作风格，并生成适用于文档生成的风格提示词。
主要针对体系文件生成场景（质量手册、程序文件、作业指导书）。
"""

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import difflib
from collections import Counter


@dataclass
class StyleProfile:
    """用户风格画像数据类"""
    user_id: str
    # 句子长度统计
    avg_sentence_length: float = 0.0
    sentence_length_variance: float = 0.0
    
    # 语态统计
    passive_voice_ratio: float = 0.0
    active_voice_ratio: float = 1.0
    
    # 列表偏好
    prefers_list_format: bool = False
    list_item_avg_length: float = 0.0
    
    # 常用短语（按使用频率排序）
    common_phrases: List[Tuple[str, int]] = field(default_factory=list)
    
    # 详细程度（1-5，5为最详细）
    detail_level: float = 3.0
    
    # 专业术语偏好
    technical_terms: List[Tuple[str, int]] = field(default_factory=list)
    
    # 段落平均长度
    avg_paragraph_length: float = 0.0
    
    # 格式化偏好
    formatting_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # 创建和更新时间
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 样本数量（用于加权平均）
    sample_count: int = 0


@dataclass
class StyleEvent:
    """风格学习事件数据类"""
    event_id: str
    user_id: str
    document_id: str
    
    # AI生成的原始文本
    ai_generated_text: str
    
    # 用户修改后的文本
    user_modified_text: str
    
    # 事件类型：document_confirmed, section_edited, feedback_given
    event_type: str = "document_confirmed"
    
    # 差异指标
    edit_distance: int = 0
    modification_ratio: float = 0.0
    
    # 修改的段落/章节信息
    section_type: Optional[str] = None
    section_title: Optional[str] = None
    
    # 时间戳
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)


class StyleLearningService:
    """风格学习服务类"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化风格学习服务
        
        Args:
            storage_path: 数据存储路径，默认为当前目录下的 style_data
        """
        if storage_path is None:
            storage_path = Path(__file__).parent / "style_data"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.profiles_dir = self.storage_path / "profiles"
        self.events_dir = self.storage_path / "events"
        self.profiles_dir.mkdir(exist_ok=True)
        self.events_dir.mkdir(exist_ok=True)
    
    # ==================== 风格画像管理 ====================
    
    def _get_profile_path(self, user_id: str) -> Path:
        """获取用户画像文件路径"""
        return self.profiles_dir / f"{user_id}.json"
    
    def save_profile(self, profile: StyleProfile) -> None:
        """保存用户风格画像"""
        profile.updated_at = datetime.now().isoformat()
        profile_path = self._get_profile_path(profile.user_id)
        
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(asdict(profile), f, ensure_ascii=False, indent=2)
    
    def load_profile(self, user_id: str) -> Optional[StyleProfile]:
        """加载用户风格画像"""
        profile_path = self._get_profile_path(user_id)
        
        if not profile_path.exists():
            return None
        
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return StyleProfile(**data)
    
    def get_or_create_profile(self, user_id: str) -> StyleProfile:
        """获取或创建用户风格画像"""
        profile = self.load_profile(user_id)
        if profile is None:
            profile = StyleProfile(user_id=user_id)
            self.save_profile(profile)
        return profile
    
    def delete_profile(self, user_id: str) -> bool:
        """删除用户风格画像"""
        profile_path = self._get_profile_path(user_id)
        if profile_path.exists():
            profile_path.unlink()
            return True
        return False
    
    # ==================== 事件记录 ====================
    
    def _get_event_path(self, event_id: str) -> Path:
        """获取事件文件路径"""
        return self.events_dir / f"{event_id}.json"
    
    def _calculate_edit_distance(self, text1: str, text2: str) -> int:
        """
        计算编辑距离（Levenshtein距离）
        """
        # 使用difflib计算差异
        seq_matcher = difflib.SequenceMatcher(None, text1, text2)
        # 获取操作码，计算总的修改量
        opcodes = seq_matcher.get_opcodes()
        distance = 0
        for tag, i1, i2, j1, j2 in opcodes:
            if tag != "equal":
                distance += max(i2 - i1, j2 - j1)
        return distance
    
    def _calculate_modification_ratio(self, text1: str, text2: str) -> float:
        """
        计算修改比例
        """
        if not text1:
            return 1.0 if text2 else 0.0
        
        distance = self._calculate_edit_distance(text1, text2)
        max_len = max(len(text1), len(text2))
        
        return min(distance / max_len, 1.0)
    
    def save_event(self, event: StyleEvent) -> None:
        """保存学习事件"""
        # 自动计算差异指标
        if event.edit_distance == 0 and event.ai_generated_text and event.user_modified_text:
            event.edit_distance = self._calculate_edit_distance(
                event.ai_generated_text, 
                event.user_modified_text
            )
            event.modification_ratio = self._calculate_modification_ratio(
                event.ai_generated_text, 
                event.user_modified_text
            )
        
        event_path = self._get_event_path(event.event_id)
        
        with open(event_path, "w", encoding="utf-8") as f:
            json.dump(asdict(event), f, ensure_ascii=False, indent=2)
    
    def load_event(self, event_id: str) -> Optional[StyleEvent]:
        """加载学习事件"""
        event_path = self._get_event_path(event_id)
        
        if not event_path.exists():
            return None
        
        with open(event_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return StyleEvent(**data)
    
    def query_events(
        self, 
        user_id: Optional[str] = None,
        document_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[StyleEvent]:
        """
        查询学习事件
        
        Args:
            user_id: 用户ID筛选
            document_id: 文档ID筛选
            event_type: 事件类型筛选
            start_time: 开始时间（ISO格式）
            end_time: 结束时间（ISO格式）
            limit: 返回数量限制
        """
        events = []
        
        for event_file in self.events_dir.glob("*.json"):
            with open(event_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 应用筛选条件
            if user_id and data.get("user_id") != user_id:
                continue
            if document_id and data.get("document_id") != document_id:
                continue
            if event_type and data.get("event_type") != event_type:
                continue
            if start_time and data.get("created_at", "") < start_time:
                continue
            if end_time and data.get("created_at", "") > end_time:
                continue
            
            events.append(StyleEvent(**data))
        
        # 按时间排序，最新的在前
        events.sort(key=lambda e: e.created_at, reverse=True)
        
        return events[:limit]
    
    def delete_event(self, event_id: str) -> bool:
        """删除学习事件"""
        event_path = self._get_event_path(event_id)
        if event_path.exists():
            event_path.unlink()
            return True
        return False
    
    # ==================== 文本分析 ====================
    
    def _split_sentences(self, text: str) -> List[str]:
        """将文本分割成句子"""
        # 中文句子分隔符
        pattern = r"[。！？；\n]+"
        sentences = re.split(pattern, text)
        # 过滤空句子
        return [s.strip() for s in sentences if s.strip()]
    
    def _analyze_sentence_length(self, text: str) -> Tuple[float, float]:
        """
        分析句子长度
        
        Returns:
            (平均长度, 方差)
        """
        sentences = self._split_sentences(text)
        if not sentences:
            return 0.0, 0.0
        
        lengths = [len(s) for s in sentences]
        avg = sum(lengths) / len(lengths)
        variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
        
        return avg, variance
    
    def _detect_passive_voice(self, text: str) -> float:
        """
        检测被动语态比例
        
        中文被动语态常见标记：被、由、受到、得到、予以、加以、得到、为...所
        """
        sentences = self._split_sentences(text)
        if not sentences:
            return 0.0
        
        passive_markers = ["被", "由", "受到", "得到", "予以", "加以", "为", "所"]
        passive_count = 0
        
        for sentence in sentences:
            for marker in passive_markers:
                if marker in sentence:
                    passive_count += 1
                    break
        
        return passive_count / len(sentences)
    
    def _analyze_list_preference(self, text: str) -> Tuple[bool, float]:
        """
        分析列表格式偏好
        
        Returns:
            (是否偏好列表, 列表项平均长度)
        """
        # 检测列表格式（数字编号、项目符号等）
        list_patterns = [
            r"^\s*[\d一二三四五六七八九十]+[.、)）]\s*",  # 数字编号
            r"^\s*[•\-\*·]\s*",  # 项目符号
            r"^\s*[(（][\d一二三四五六七八九十]+[)）]\s*",  # 括号编号
        ]
        
        lines = text.split("\n")
        list_items = []
        
        for line in lines:
            for pattern in list_patterns:
                if re.match(pattern, line):
                    content = re.sub(pattern, "", line).strip()
                    if content:
                        list_items.append(content)
                    break
        
        if not list_items:
            return False, 0.0
        
        avg_length = sum(len(item) for item in list_items) / len(list_items)
        # 如果列表项超过3个，认为偏好列表格式
        prefers_list = len(list_items) >= 3
        
        return prefers_list, avg_length
    
    def _extract_common_phrases(self, text: str, top_n: int = 20) -> List[Tuple[str, int]]:
        """
        提取常用短语
        
        提取2-4字的常用短语组合
        """
        # 清理文本
        text = re.sub(r"[^\u4e00-\u9fa5]", "", text)  # 只保留中文字符
        
        phrases = []
        
        # 提取2-4字短语
        for length in range(2, 5):
            for i in range(len(text) - length + 1):
                phrase = text[i:i+length]
                phrases.append(phrase)
        
        # 统计频率
        phrase_counts = Counter(phrases)
        
        # 过滤低频短语（至少出现2次）
        common_phrases = [(phrase, count) for phrase, count in phrase_counts.most_common(top_n * 2) if count >= 2]
        
        return common_phrases[:top_n]
    
    def _extract_technical_terms(self, text: str, top_n: int = 15) -> List[Tuple[str, int]]:
        """
        提取专业术语
        
        基于常见体系文件术语模式识别
        """
        # 常见体系文件术语模式
        term_patterns = [
            r"[\u4e00-\u9fa5]{2,8}程序",
            r"[\u4e00-\u9fa5]{2,8}文件",
            r"[\u4e00-\u9fa5]{2,8}记录",
            r"[\u4e00-\u9fa5]{2,8}标准",
            r"[\u4e00-\u9fa5]{2,8}规范",
            r"[\u4e00-\u9fa5]{2,8}要求",
            r"[\u4e00-\u9fa5]{2,8}流程",
            r"[\u4e00-\u9fa5]{2,8}制度",
            r"ISO\s*\d+",
            r"GB[/T]?\s*\d+",
        ]
        
        terms = []
        for pattern in term_patterns:
            matches = re.findall(pattern, text)
            terms.extend(matches)
        
        term_counts = Counter(terms)
        return [(term, count) for term, count in term_counts.most_common(top_n) if count >= 1]
    
    def _analyze_detail_level(self, text: str) -> float:
        """
        分析详细程度（1-5分）
        
        基于以下指标：
        - 句子数量
        - 段落长度
        - 专业术语密度
        - 列表使用
        """
        sentences = self._split_sentences(text)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        
        if not sentences:
            return 3.0
        
        # 句子密度评分
        sentence_density = len(sentences) / max(len(text) / 100, 1)
        sentence_score = min(sentence_density / 2, 1.0) * 5
        
        # 段落长度评分
        if paragraphs:
            avg_para_length = sum(len(p) for p in paragraphs) / len(paragraphs)
            para_score = min(avg_para_length / 200, 1.0) * 5
        else:
            para_score = 3.0
        
        # 术语密度评分
        terms = self._extract_technical_terms(text)
        term_density = len(terms) / max(len(sentences), 1)
        term_score = min(term_density * 5, 5.0)
        
        # 综合评分
        detail_level = (sentence_score * 0.3 + para_score * 0.4 + term_score * 0.3)
        
        return round(max(1.0, min(5.0, detail_level)), 2)
    
    # ==================== 风格画像更新 ====================
    
    def update_profile_from_event(self, event: StyleEvent) -> StyleProfile:
        """
        从文档确认事件更新用户风格画像
        
        使用用户修改后的文本作为学习样本
        """
        profile = self.get_or_create_profile(event.user_id)
        text = event.user_modified_text
        
        if not text:
            return profile
        
        # 分析句子长度
        avg_len, variance = self._analyze_sentence_length(text)
        
        # 分析被动语态
        passive_ratio = self._detect_passive_voice(text)
        
        # 分析列表偏好
        prefers_list, list_avg_len = self._analyze_list_preference(text)
        
        # 提取常用短语
        common_phrases = self._extract_common_phrases(text)
        
        # 提取专业术语
        technical_terms = self._extract_technical_terms(text)
        
        # 分析详细程度
        detail_level = self._analyze_detail_level(text)
        
        # 分析段落长度
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        avg_para_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        # 使用加权平均更新画像
        n = profile.sample_count
        new_n = n + 1
        
        if n == 0:
            # 首次更新
            profile.avg_sentence_length = avg_len
            profile.sentence_length_variance = variance
            profile.passive_voice_ratio = passive_ratio
            profile.active_voice_ratio = 1.0 - passive_ratio
            profile.prefers_list_format = prefers_list
            profile.list_item_avg_length = list_avg_len
            profile.common_phrases = common_phrases
            profile.technical_terms = technical_terms
            profile.detail_level = detail_level
            profile.avg_paragraph_length = avg_para_length
        else:
            # 加权平均更新
            weight_old = n / new_n
            weight_new = 1 / new_n
            
            profile.avg_sentence_length = (
                profile.avg_sentence_length * weight_old + avg_len * weight_new
            )
            profile.sentence_length_variance = (
                profile.sentence_length_variance * weight_old + variance * weight_new
            )
            profile.passive_voice_ratio = (
                profile.passive_voice_ratio * weight_old + passive_ratio * weight_new
            )
            profile.active_voice_ratio = 1.0 - profile.passive_voice_ratio
            profile.detail_level = (
                profile.detail_level * weight_old + detail_level * weight_new
            )
            profile.avg_paragraph_length = (
                profile.avg_paragraph_length * weight_old + avg_para_length * weight_new
            )
            
            # 列表偏好采用多数投票
            profile.prefers_list_format = (
                (profile.prefers_list_format and n >= 2) or prefers_list
            )
            profile.list_item_avg_length = (
                profile.list_item_avg_length * weight_old + list_avg_len * weight_new
            )
            
            # 合并常用短语频率
            phrase_counter = Counter(dict(profile.common_phrases))
            phrase_counter.update(dict(common_phrases))
            profile.common_phrases = phrase_counter.most_common(20)
            
            # 合并专业术语频率
            term_counter = Counter(dict(profile.technical_terms))
            term_counter.update(dict(technical_terms))
            profile.technical_terms = term_counter.most_common(15)
        
        profile.sample_count = new_n
        
        # 更新格式化偏好
        if event.section_type:
            if "formatting_preferences" not in profile.formatting_preferences:
                profile.formatting_preferences["section_types"] = []
            if event.section_type not in profile.formatting_preferences.get("section_types", []):
                profile.formatting_preferences.setdefault("section_types", []).append(event.section_type)
        
        # 保存更新后的画像
        self.save_profile(profile)
        
        return profile
    
    def update_profile_from_events(self, user_id: str, event_ids: Optional[List[str]] = None) -> StyleProfile:
        """
        从多个事件批量更新用户风格画像
        
        Args:
            user_id: 用户ID
            event_ids: 事件ID列表，如果为None则使用所有该用户的事件
        """
        if event_ids is None:
            events = self.query_events(user_id=user_id, limit=1000)
        else:
            events = []
            for event_id in event_ids:
                event = self.load_event(event_id)
                if event:
                    events.append(event)
        
        profile = None
        for event in events:
            profile = self.update_profile_from_event(event)
        
        return profile or self.get_or_create_profile(user_id)
    
    # ==================== 风格提示词生成 ====================
    
    def generate_style_prompt(self, user_id: str, document_type: Optional[str] = None) -> str:
        """
        根据用户画像生成风格注入提示词
        
        Args:
            user_id: 用户ID
            document_type: 文档类型（quality_manual, procedure, work_instruction等）
        
        Returns:
            风格提示词字符串
        """
        profile = self.load_profile(user_id)
        
        if profile is None or profile.sample_count == 0:
            # 没有学习数据时返回默认提示词
            return self._generate_default_style_prompt(document_type)
        
        prompt_parts = []
        
        # 基础风格指导
        prompt_parts.append("【写作风格指导】")
        prompt_parts.append("")
        
        # 句子长度指导
        if profile.avg_sentence_length > 0:
            if profile.avg_sentence_length < 20:
                prompt_parts.append("- 使用简洁短句，每句话控制在20字以内")
            elif profile.avg_sentence_length < 40:
                prompt_parts.append("- 使用中等长度句子，每句话控制在20-40字")
            else:
                prompt_parts.append("- 可适当使用较长句子，详细阐述观点")
        
        # 语态指导
        if profile.passive_voice_ratio > 0.6:
            prompt_parts.append("- 优先使用被动语态，强调动作的承受者")
        elif profile.passive_voice_ratio < 0.3:
            prompt_parts.append("- 优先使用主动语态，强调动作的执行者")
        else:
            prompt_parts.append("- 主动语态和被动语态灵活使用")
        
        # 列表偏好
        if profile.prefers_list_format:
            prompt_parts.append("- 善用列表格式组织内容，条理清晰")
            if profile.list_item_avg_length < 15:
                prompt_parts.append("- 列表项保持简洁，每项控制在15字以内")
            elif profile.list_item_avg_length > 30:
                prompt_parts.append("- 列表项可适当详细，充分说明要点")
        
        # 详细程度
        if profile.detail_level >= 4:
            prompt_parts.append("- 内容详细全面，充分展开每个要点")
        elif profile.detail_level <= 2:
            prompt_parts.append("- 内容简明扼要，突出重点")
        else:
            prompt_parts.append("- 内容详略得当，平衡深度与简洁")
        
        # 段落长度
        if profile.avg_paragraph_length > 0:
            if profile.avg_paragraph_length < 100:
                prompt_parts.append("- 使用短段落，每段控制在100字以内")
            elif profile.avg_paragraph_length > 300:
                prompt_parts.append("- 段落可适当较长，充分展开论述")
        
        # 常用短语建议
        if profile.common_phrases:
            top_phrases = [p[0] for p in profile.common_phrases[:5]]
            prompt_parts.append(f"- 可适当使用以下常用表达：{', '.join(top_phrases)}")
        
        # 专业术语
        if profile.technical_terms:
            top_terms = [t[0] for t in profile.technical_terms[:5]]
            prompt_parts.append(f"- 注意准确使用专业术语：{', '.join(top_terms)}")
        
        # 文档类型特定指导
        doc_type_guidance = self._get_document_type_guidance(document_type)
        if doc_type_guidance:
            prompt_parts.append("")
            prompt_parts.append(doc_type_guidance)
        
        return "\n".join(prompt_parts)
    
    def _generate_default_style_prompt(self, document_type: Optional[str] = None) -> str:
        """生成默认风格提示词"""
        prompt_parts = [
            "【写作风格指导】",
            "",
            "- 使用规范、正式的书面语",
            "- 句子长度适中，表达清晰准确",
            "- 主动语态和被动语态灵活使用",
            "- 善用列表格式组织内容",
            "- 内容详略得当，突出重点",
            "- 使用标准的专业术语",
            "- 段落结构清晰，逻辑连贯",
        ]
        
        doc_type_guidance = self._get_document_type_guidance(document_type)
        if doc_type_guidance:
            prompt_parts.append("")
            prompt_parts.append(doc_type_guidance)
        
        return "\n".join(prompt_parts)
    
    def _get_document_type_guidance(self, document_type: Optional[str]) -> str:
        """获取文档类型特定的风格指导"""
        guidance_map = {
            "quality_manual": """【质量手册特定要求】
- 采用高层级、概括性的描述
- 强调管理体系的整体框架
- 使用"应"、"须"等规范性词汇
- 明确各部门职责和接口关系
- 体现持续改进的理念""",
            
            "procedure": """【程序文件特定要求】
- 明确目的、适用范围、职责
- 使用5W1H方法描述流程
- 详细规定活动的顺序和接口
- 明确输入、输出和所需资源
- 使用流程图辅助说明（如适用）""",
            
            "work_instruction": """【作业指导书特定要求】
- 操作步骤详细、具体、可执行
- 明确操作标准和技术要求
- 规定所需的设备和工具
- 说明质量检查点和验收标准
- 包含安全注意事项（如适用）""",
            
            "record": """【记录表格特定要求】
- 设计简洁、便于填写
- 包含必要的信息字段
- 明确填写要求和规范
- 便于追溯和检索""",
        }
        
        return guidance_map.get(document_type, "")
    
    def generate_full_prompt_with_style(
        self, 
        user_id: str, 
        base_prompt: str, 
        document_type: Optional[str] = None
    ) -> str:
        """
        将风格提示词与基础提示词结合
        
        Args:
            user_id: 用户ID
            base_prompt: 基础提示词（任务描述、文档要求等）
            document_type: 文档类型
        
        Returns:
            完整的提示词
        """
        style_prompt = self.generate_style_prompt(user_id, document_type)
        
        full_prompt = f"""{base_prompt}

{style_prompt}

请根据以上要求生成文档内容。"""
        
        return full_prompt
    
    # ==================== 统计和报告 ====================
    
    def get_learning_stats(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户学习统计信息
        """
        profile = self.load_profile(user_id)
        events = self.query_events(user_id=user_id, limit=1000)
        
        stats = {
            "user_id": user_id,
            "has_profile": profile is not None,
            "sample_count": profile.sample_count if profile else 0,
            "total_events": len(events),
            "event_types": {},
            "avg_modification_ratio": 0.0,
            "recent_activity": [],
        }
        
        if events:
            # 事件类型统计
            type_counts = Counter(e.event_type for e in events)
            stats["event_types"] = dict(type_counts)
            
            # 平均修改比例
            modification_ratios = [e.modification_ratio for e in events if e.modification_ratio > 0]
            if modification_ratios:
                stats["avg_modification_ratio"] = sum(modification_ratios) / len(modification_ratios)
            
            # 最近活动
            recent_events = sorted(events, key=lambda e: e.created_at, reverse=True)[:5]
            stats["recent_activity"] = [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type,
                    "document_id": e.document_id,
                    "created_at": e.created_at,
                    "modification_ratio": e.modification_ratio,
                }
                for e in recent_events
            ]
        
        if profile:
            stats["profile_summary"] = {
                "avg_sentence_length": round(profile.avg_sentence_length, 2),
                "passive_voice_ratio": round(profile.passive_voice_ratio, 2),
                "prefers_list_format": profile.prefers_list_format,
                "detail_level": round(profile.detail_level, 2),
                "common_phrases_count": len(profile.common_phrases),
                "technical_terms_count": len(profile.technical_terms),
            }
        
        return stats


# ==================== 便捷函数 ====================

def create_style_event(
    user_id: str,
    document_id: str,
    ai_generated_text: str,
    user_modified_text: str,
    event_type: str = "document_confirmed",
    section_type: Optional[str] = None,
    section_title: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> StyleEvent:
    """
    便捷函数：创建风格学习事件
    
    Args:
        user_id: 用户ID
        document_id: 文档ID
        ai_generated_text: AI生成的原始文本
        user_modified_text: 用户修改后的文本
        event_type: 事件类型
        section_type: 章节类型
        section_title: 章节标题
        metadata: 额外元数据
    """
    import uuid
    
    return StyleEvent(
        event_id=str(uuid.uuid4()),
        user_id=user_id,
        document_id=document_id,
        ai_generated_text=ai_generated_text,
        user_modified_text=user_modified_text,
        event_type=event_type,
        section_type=section_type,
        section_title=section_title,
        metadata=metadata or {},
    )


# 单例实例
_style_learning_service: Optional[StyleLearningService] = None


def get_style_learning_service(storage_path: Optional[str] = None) -> StyleLearningService:
    """获取风格学习服务单例"""
    global _style_learning_service
    if _style_learning_service is None:
        _style_learning_service = StyleLearningService(storage_path)
    return _style_learning_service
