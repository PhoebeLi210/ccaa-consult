"""
L4 用户知识库模块

实现第四层知识库 - 用户知识层，包含:
- 用户自定义模板
- 个人风格学习
- 历史项目数据
- 用户偏好设置

特点:
- 个性化: 针对特定用户定制
- 学习性: 能够学习和适应用户风格
- 私有性: 用户数据隔离存储
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os

from .knowledge_base import (
    KnowledgeBase,
    KnowledgeItem,
    KnowledgeLevel,
    KnowledgeQuery,
    KnowledgeResult,
)


class UserPreferenceType(Enum):
    """用户偏好类型枚举"""
    WRITING_STYLE = "写作风格"
    REPORT_FORMAT = "报告格式"
    TERMINOLOGY = "术语偏好"
    TEMPLATE_PREFERENCE = "模板偏好"
    INDUSTRY_FOCUS = "行业侧重"


@dataclass
class UserTemplate:
    """
    用户自定义模板数据类
    
    Attributes:
        name: 模板名称
        user_id: 用户ID
        base_template_id: 基础模板ID（如果是从系统模板修改而来）
        content: 模板内容
        description: 模板描述
        created_at: 创建时间
        updated_at: 更新时间
        usage_count: 使用次数
        tags: 标签
    """
    
    name: str
    user_id: str
    base_template_id: str = ""
    content: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    tags: List[str] = field(default_factory=list)
    
    def to_knowledge_item(self) -> KnowledgeItem:
        """转换为知识项"""
        return KnowledgeItem(
            level=KnowledgeLevel.L4_USER,
            title=f"用户模板: {self.name}",
            content=self.content,
            category="用户模板",
            tags=["用户模板", self.user_id] + self.tags,
            source=f"用户 {self.user_id}",
            confidence=0.7,
            metadata={
                "user_id": self.user_id,
                "base_template_id": self.base_template_id,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "usage_count": self.usage_count,
            }
        )


@dataclass
class UserPreference:
    """
    用户偏好数据类
    
    Attributes:
        user_id: 用户ID
        preference_type: 偏好类型
        preference_value: 偏好值
        description: 偏好描述
        learned_from: 学习来源
        confidence: 置信度
    """
    
    user_id: str
    preference_type: str
    preference_value: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    learned_from: str = ""
    confidence: float = 0.5
    
    def to_knowledge_item(self) -> KnowledgeItem:
        """转换为知识项"""
        content = f"""
## 用户偏好: {self.preference_type}

### 用户ID
{self.user_id}

### 偏好值
{json.dumps(self.preference_value, ensure_ascii=False, indent=2)}

### 描述
{self.description}

### 学习来源
{self.learned_from}

### 置信度
{self.confidence}
"""
        
        return KnowledgeItem(
            level=KnowledgeLevel.L4_USER,
            title=f"用户偏好: {self.preference_type}",
            content=content.strip(),
            category="用户偏好",
            tags=["用户偏好", self.user_id, self.preference_type],
            source=f"用户 {self.user_id}",
            confidence=self.confidence,
            metadata={
                "user_id": self.user_id,
                "preference_type": self.preference_type,
                "preference_value": self.preference_value,
                "learned_from": self.learned_from,
            }
        )


@dataclass
class ProjectHistory:
    """
    项目历史数据类
    
    Attributes:
        project_id: 项目ID
        user_id: 用户ID
        project_name: 项目名称
        project_type: 项目类型
        client_info: 客户信息
        start_date: 开始日期
        end_date: 结束日期
        standards: 涉及标准
        key_findings: 主要发现
        recommendations: 建议内容
        lessons_learned: 经验教训
        documents: 相关文档
    """
    
    project_id: str
    user_id: str
    project_name: str = ""
    project_type: str = ""
    client_info: str = ""
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    standards: List[str] = field(default_factory=list)
    key_findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    lessons_learned: str = ""
    documents: List[str] = field(default_factory=list)
    
    def to_knowledge_item(self) -> KnowledgeItem:
        """转换为知识项"""
        content = f"""
## 项目历史: {self.project_name}

### 项目信息
- 项目ID: {self.project_id}
- 项目类型: {self.project_type}
- 客户信息: {self.client_info}
- 开始日期: {self.start_date.strftime('%Y-%m-%d')}
- 结束日期: {self.end_date.strftime('%Y-%m-%d') if self.end_date else '进行中'}

### 涉及标准
{', '.join(self.standards) if self.standards else '无'}

### 主要发现
{chr(10).join(f'- {f}' for f in self.key_findings) if self.key_findings else '无'}

### 建议
{chr(10).join(f'- {r}' for r in self.recommendations) if self.recommendations else '无'}

### 经验教训
{self.lessons_learned if self.lessons_learned else '无'}

### 相关文档
{chr(10).join(f'- {d}' for d in self.documents) if self.documents else '无'}
"""
        
        return KnowledgeItem(
            level=KnowledgeLevel.L4_USER,
            title=f"项目历史: {self.project_name}",
            content=content.strip(),
            category="项目历史",
            tags=["项目历史", self.user_id, self.project_type] + self.standards,
            source=f"用户 {self.user_id}",
            confidence=0.6,
            metadata={
                "project_id": self.project_id,
                "user_id": self.user_id,
                "project_type": self.project_type,
                "standards": self.standards,
            }
        )


@dataclass
class WritingStyle:
    """
    写作风格数据类
    
    Attributes:
        user_id: 用户ID
        style_name: 风格名称
        characteristics: 风格特征
        vocabulary: 常用词汇
        sentence_patterns: 句式模式
        formatting_preferences: 格式偏好
        sample_texts: 示例文本
    """
    
    user_id: str
    style_name: str = "默认风格"
    characteristics: List[str] = field(default_factory=list)
    vocabulary: Dict[str, int] = field(default_factory=dict)
    sentence_patterns: List[str] = field(default_factory=list)
    formatting_preferences: Dict[str, Any] = field(default_factory=dict)
    sample_texts: List[str] = field(default_factory=list)
    
    def to_knowledge_item(self) -> KnowledgeItem:
        """转换为知识项"""
        chars = self.characteristics
        chars_text = chr(10).join('- ' + c for c in chars) if chars else '无'
        vocab_text = ', '.join(list(self.vocabulary.keys())[:20]) if self.vocabulary else '无'
        patterns = self.sentence_patterns
        patterns_text = chr(10).join('- ' + p for p in patterns[:10]) if patterns else '无'
        fmt_text = json.dumps(self.formatting_preferences, ensure_ascii=False, indent=2)
        samples = self.sample_texts
        samples_text = chr(10).join('---\n' + s + '\n' for s in samples[:3]) if samples else '无'
        
        content = (
            f"## 写作风格: {self.style_name}\n\n"
            f"### 用户ID\n{self.user_id}\n\n"
            f"### 风格特征\n{chars_text}\n\n"
            f"### 常用词汇\n{vocab_text}\n\n"
            f"### 句式模式\n{patterns_text}\n\n"
            f"### 格式偏好\n{fmt_text}\n\n"
            f"### 示例文本\n{samples_text}"
        )
        
        return KnowledgeItem(
            level=KnowledgeLevel.L4_USER,
            title=f"写作风格: {self.style_name}",
            content=content.strip(),
            category="写作风格",
            tags=["写作风格", self.user_id],
            source=f"用户 {self.user_id}",
            confidence=0.8,
            metadata={
                "user_id": self.user_id,
                "style_name": self.style_name,
                "characteristics": self.characteristics,
                "vocabulary": self.vocabulary,
                "sentence_patterns": self.sentence_patterns,
                "formatting_preferences": self.formatting_preferences,
            }
        )


class UserKB(KnowledgeBase):
    """
    L4 用户知识库
    
    管理用户个人知识，包括:
    - 用户自定义模板
    - 用户偏好设置
    - 项目历史数据
    - 写作风格学习
    
    特点:
    - 用户数据隔离
    - 支持学习和适应
    - 可导入导出
    """
    
    def __init__(self, user_id: str = ""):
        """
        初始化用户知识库
        
        Args:
            user_id: 用户ID，为空表示管理所有用户数据
        """
        super().__init__(KnowledgeLevel.L4_USER)
        self._current_user_id = user_id
        self._user_templates: Dict[str, Dict[str, UserTemplate]] = {}
        self._user_preferences: Dict[str, Dict[str, UserPreference]] = {}
        self._project_histories: Dict[str, Dict[str, ProjectHistory]] = {}
        self._writing_styles: Dict[str, WritingStyle] = {}
    
    def initialize(self) -> bool:
        """
        初始化用户知识库
        
        Returns:
            初始化是否成功
        """
        try:
            items = self.load_knowledge()
            for item in items:
                self.add_item(item)
            
            self._initialized = True
            return True
        except Exception as e:
            print(f"用户知识库初始化失败: {e}")
            return False
    
    def load_knowledge(self) -> List[KnowledgeItem]:
        """
        加载用户知识数据
        
        Returns:
            用户知识项列表
        """
        items = []
        
        # 加载用户模板
        for user_id, templates in self._user_templates.items():
            for template in templates.values():
                items.append(template.to_knowledge_item())
        
        # 加载用户偏好
        for user_id, preferences in self._user_preferences.items():
            for preference in preferences.values():
                items.append(preference.to_knowledge_item())
        
        # 加载项目历史
        for user_id, projects in self._project_histories.items():
            for project in projects.values():
                items.append(project.to_knowledge_item())
        
        # 加载写作风格
        for user_id, style in self._writing_styles.items():
            items.append(style.to_knowledge_item())
        
        return items
    
    def set_current_user(self, user_id: str):
        """
        设置当前用户
        
        Args:
            user_id: 用户ID
        """
        self._current_user_id = user_id
    
    def add_user_template(self, template: UserTemplate) -> bool:
        """
        添加用户模板
        
        Args:
            template: 用户模板对象
            
        Returns:
            添加是否成功
        """
        import uuid
        template_id = str(uuid.uuid4())
        
        user_id = template.user_id
        if user_id not in self._user_templates:
            self._user_templates[user_id] = {}
        
        self._user_templates[user_id][template_id] = template
        return self.add_item(template.to_knowledge_item())
    
    def get_user_templates(self, user_id: str = None) -> List[UserTemplate]:
        """
        获取用户模板列表
        
        Args:
            user_id: 用户ID，为None则使用当前用户
            
        Returns:
            用户模板列表
        """
        target_user = user_id or self._current_user_id
        if target_user not in self._user_templates:
            return []
        return list(self._user_templates[target_user].values())
    
    def set_user_preference(self, preference: UserPreference) -> bool:
        """
        设置用户偏好
        
        Args:
            preference: 用户偏好对象
            
        Returns:
            设置是否成功
        """
        import uuid
        pref_id = str(uuid.uuid4())
        
        user_id = preference.user_id
        if user_id not in self._user_preferences:
            self._user_preferences[user_id] = {}
        
        self._user_preferences[user_id][preference.preference_type] = preference
        return self.add_item(preference.to_knowledge_item())
    
    def get_user_preference(self, preference_type: str, user_id: str = None) -> Optional[UserPreference]:
        """
        获取用户偏好
        
        Args:
            preference_type: 偏好类型
            user_id: 用户ID，为None则使用当前用户
            
        Returns:
            用户偏好对象或None
        """
        target_user = user_id or self._current_user_id
        if target_user not in self._user_preferences:
            return None
        return self._user_preferences[target_user].get(preference_type)
    
    def add_project_history(self, project: ProjectHistory) -> bool:
        """
        添加项目历史
        
        Args:
            project: 项目历史对象
            
        Returns:
            添加是否成功
        """
        user_id = project.user_id
        if user_id not in self._project_histories:
            self._project_histories[user_id] = {}
        
        self._project_histories[user_id][project.project_id] = project
        return self.add_item(project.to_knowledge_item())
    
    def get_user_projects(self, user_id: str = None) -> List[ProjectHistory]:
        """
        获取用户项目历史列表
        
        Args:
            user_id: 用户ID，为None则使用当前用户
            
        Returns:
            项目历史列表
        """
        target_user = user_id or self._current_user_id
        if target_user not in self._project_histories:
            return []
        return list(self._project_histories[target_user].values())
    
    def set_writing_style(self, style: WritingStyle) -> bool:
        """
        设置用户写作风格
        
        Args:
            style: 写作风格对象
            
        Returns:
            设置是否成功
        """
        self._writing_styles[style.user_id] = style
        return self.add_item(style.to_knowledge_item())
    
    def get_writing_style(self, user_id: str = None) -> Optional[WritingStyle]:
        """
        获取用户写作风格
        
        Args:
            user_id: 用户ID，为None则使用当前用户
            
        Returns:
            写作风格对象或None
        """
        target_user = user_id or self._current_user_id
        return self._writing_styles.get(target_user)
    
    def learn_from_text(self, text: str, user_id: str = None):
        """
        从文本学习用户写作风格
        
        Args:
            text: 输入文本
            user_id: 用户ID，为None则使用当前用户
        """
        target_user = user_id or self._current_user_id
        
        # 获取或创建写作风格
        style = self._writing_styles.get(target_user)
        if not style:
            style = WritingStyle(user_id=target_user)
        
        # 分析文本特征
        # 1. 词汇统计
        words = text.split()
        for word in words:
            word = word.strip('.,!?;:"\'()[]{}')
            if word:
                style.vocabulary[word] = style.vocabulary.get(word, 0) + 1
        
        # 2. 识别风格特征
        if '建议' in text or '应当' in text:
            if '建议性语气' not in style.characteristics:
                style.characteristics.append('建议性语气')
        
        if '必须' in text or '应当' in text:
            if '规范性表达' not in style.characteristics:
                style.characteristics.append('规范性表达')
        
        # 3. 保存示例文本
        if len(style.sample_texts) < 10:
            style.sample_texts.append(text[:500])
        
        self._writing_styles[target_user] = style
    
    def learn_from_feedback(self, item_id: str, feedback: Dict[str, Any], user_id: str = None):
        """
        从用户反馈学习
        
        Args:
            item_id: 知识项ID
            feedback: 反馈信息
            user_id: 用户ID，为None则使用当前用户
        """
        target_user = user_id or self._current_user_id
        
        # 根据反馈调整偏好
        feedback_type = feedback.get('type', '')
        
        if feedback_type == 'positive':
            # 正面反馈，增强相关知识的置信度
            item = self.get_item(item_id)
            if item:
                item.confidence = min(1.0, item.confidence + 0.1)
        
        elif feedback_type == 'negative':
            # 负面反馈，降低相关知识的置信度
            item = self.get_item(item_id)
            if item:
                item.confidence = max(0.1, item.confidence - 0.1)
    
    def query_user_knowledge(self, query: KnowledgeQuery, user_id: str = None) -> KnowledgeResult:
        """
        查询用户知识
        
        Args:
            query: 查询对象
            user_id: 用户ID，为None则使用当前用户
            
        Returns:
            查询结果
        """
        target_user = user_id or self._current_user_id
        
        # 设置标签过滤
        if not query.tags:
            query.tags = [target_user]
        else:
            query.tags.append(target_user)
        
        return self.query(query)
    
    def export_user_data(self, user_id: str = None) -> Dict[str, Any]:
        """
        导出用户数据
        
        Args:
            user_id: 用户ID，为None则使用当前用户
            
        Returns:
            用户数据字典
        """
        target_user = user_id or self._current_user_id
        
        export_data = {
            "user_id": target_user,
            "templates": [],
            "preferences": [],
            "projects": [],
            "writing_style": None,
        }
        
        # 导出模板
        if target_user in self._user_templates:
            for template in self._user_templates[target_user].values():
                export_data["templates"].append({
                    "name": template.name,
                    "content": template.content,
                    "description": template.description,
                    "tags": template.tags,
                })
        
        # 导出偏好
        if target_user in self._user_preferences:
            for pref in self._user_preferences[target_user].values():
                export_data["preferences"].append({
                    "type": pref.preference_type,
                    "value": pref.preference_value,
                    "description": pref.description,
                })
        
        # 导出项目历史
        if target_user in self._project_histories:
            for project in self._project_histories[target_user].values():
                export_data["projects"].append({
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "project_type": project.project_type,
                    "standards": project.standards,
                    "key_findings": project.key_findings,
                    "recommendations": project.recommendations,
                })
        
        # 导出写作风格
        if target_user in self._writing_styles:
            style = self._writing_styles[target_user]
            export_data["writing_style"] = {
                "style_name": style.style_name,
                "characteristics": style.characteristics,
                "formatting_preferences": style.formatting_preferences,
            }
        
        return export_data
    
    def import_user_data(self, data: Dict[str, Any], user_id: str = None) -> bool:
        """
        导入用户数据
        
        Args:
            data: 用户数据字典
            user_id: 用户ID，为None则使用当前用户
            
        Returns:
            导入是否成功
        """
        target_user = user_id or self._current_user_id
        
        try:
            # 导入模板
            for template_data in data.get("templates", []):
                template = UserTemplate(
                    name=template_data["name"],
                    user_id=target_user,
                    content=template_data.get("content", ""),
                    description=template_data.get("description", ""),
                    tags=template_data.get("tags", []),
                )
                self.add_user_template(template)
            
            # 导入偏好
            for pref_data in data.get("preferences", []):
                preference = UserPreference(
                    user_id=target_user,
                    preference_type=pref_data["type"],
                    preference_value=pref_data.get("value", {}),
                    description=pref_data.get("description", ""),
                )
                self.set_user_preference(preference)
            
            # 导入写作风格
            style_data = data.get("writing_style")
            if style_data:
                style = WritingStyle(
                    user_id=target_user,
                    style_name=style_data.get("style_name", "默认风格"),
                    characteristics=style_data.get("characteristics", []),
                    formatting_preferences=style_data.get("formatting_preferences", {}),
                )
                self.set_writing_style(style)
            
            return True
        except Exception as e:
            print(f"导入用户数据失败: {e}")
            return False
    
    def clear_user_data(self, user_id: str = None):
        """
        清除用户数据
        
        Args:
            user_id: 用户ID，为None则使用当前用户
        """
        target_user = user_id or self._current_user_id
        
        if target_user in self._user_templates:
            del self._user_templates[target_user]
        
        if target_user in self._user_preferences:
            del self._user_preferences[target_user]
        
        if target_user in self._project_histories:
            del self._project_histories[target_user]
        
        if target_user in self._writing_styles:
            del self._writing_styles[target_user]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        stats = super().get_statistics()
        stats["user_count"] = len(set(
            list(self._user_templates.keys()) +
            list(self._user_preferences.keys()) +
            list(self._project_histories.keys()) +
            list(self._writing_styles.keys())
        ))
        stats["current_user"] = self._current_user_id
        return stats
