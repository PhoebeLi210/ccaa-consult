"""
逐级查资料原则模块 - 文件层级引用关系管理

实现四级文件体系的层级引用关系管理：
- 一级文件：管理手册
- 二级文件：程序文件
- 三级文件：管理制度
- 四级文件：记录表格
"""

from enum import IntEnum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


class DocumentLevel(IntEnum):
    """文件层级 - 四级文件体系"""
    LEVEL_1 = 1  # 管理手册
    LEVEL_2 = 2  # 程序文件
    LEVEL_3 = 3  # 管理制度
    LEVEL_4 = 4  # 记录表格


class DocumentLevelConfig:
    """文件层级配置"""
    CONFIG = {
        DocumentLevel.LEVEL_1: {
            "name": "管理手册",
            "code_prefix": "A",
            "parent_level": None,  # 一级文件没有上级
            "reference_format": "{standard}标准{clause}条款",
        },
        DocumentLevel.LEVEL_2: {
            "name": "程序文件",
            "code_prefix": "B",
            "parent_level": DocumentLevel.LEVEL_1,
            "reference_format": "《{parent_name}》（{parent_code}）{clause}条款",
        },
        DocumentLevel.LEVEL_3: {
            "name": "管理制度",
            "code_prefix": "C",
            "parent_level": DocumentLevel.LEVEL_2,
            "reference_format": "《{parent_name}》（{parent_code}）",
        },
        DocumentLevel.LEVEL_4: {
            "name": "记录表格",
            "code_prefix": "D",
            "parent_level": DocumentLevel.LEVEL_3,
            "reference_format": "《{parent_name}》（{parent_code}）",
        },
    }

    @classmethod
    def get_config(cls, level: DocumentLevel) -> Dict[str, Any]:
        """获取指定层级的配置"""
        return cls.CONFIG.get(level, {})

    @classmethod
    def get_name(cls, level: DocumentLevel) -> str:
        """获取层级名称"""
        return cls.get_config(level).get("name", "")

    @classmethod
    def get_code_prefix(cls, level: DocumentLevel) -> str:
        """获取层级代码前缀"""
        return cls.get_config(level).get("code_prefix", "")

    @classmethod
    def get_parent_level(cls, level: DocumentLevel) -> Optional[DocumentLevel]:
        """获取上级层级"""
        return cls.get_config(level).get("parent_level")

    @classmethod
    def get_reference_format(cls, level: DocumentLevel) -> str:
        """获取引用格式"""
        return cls.get_config(level).get("reference_format", "")


@dataclass
class DocumentInfo:
    """文档信息"""
    doc_id: str
    level: DocumentLevel
    name: str
    code: str
    clause_mapping: Dict[str, str] = field(default_factory=dict)
    parent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "doc_id": self.doc_id,
            "level": self.level.value,
            "name": self.name,
            "code": self.code,
            "clause_mapping": self.clause_mapping,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentInfo":
        """从字典创建"""
        return cls(
            doc_id=data["doc_id"],
            level=DocumentLevel(data["level"]),
            name=data["name"],
            code=data["code"],
            clause_mapping=data.get("clause_mapping", {}),
            parent_id=data.get("parent_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ReferenceInfo:
    """引用信息"""
    source_doc_id: str
    target_doc_id: str
    reference_text: str
    clause: Optional[str] = None
    standard: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "source_doc_id": self.source_doc_id,
            "target_doc_id": self.target_doc_id,
            "reference_text": self.reference_text,
            "clause": self.clause,
            "standard": self.standard,
            "created_at": self.created_at.isoformat(),
        }


class DocumentReferenceManager:
    """文档引用管理器

    管理四级文件体系的引用关系，实现逐级查资料原则。

    文档引用链示例：
    生成三级文件《设备管理制度》时：
    - 引用二级文件：《设备管理程序》（XXX-QESMS-B-005）
    - 引用一级文件：《质量手册》（XXX-QESMS-A-001）4.4条款
    - 引用标准：ISO9001:2015标准7.1条款
    """

    def __init__(self, project_id: str):
        """初始化文档引用管理器

        Args:
            project_id: 项目ID
        """
        self.project_id = project_id
        self._documents: Dict[str, DocumentInfo] = {}  # doc_id -> DocumentInfo
        self._level_documents: Dict[DocumentLevel, List[str]] = {
            level: [] for level in DocumentLevel
        }  # level -> [doc_ids]
        self._references: Dict[str, List[ReferenceInfo]] = {}  # doc_id -> [ReferenceInfo]
        self._standard_clause_mapping: Dict[str, str] = {}  # 标准条款映射

    def register_document(
        self,
        doc_id: str,
        level: DocumentLevel,
        name: str,
        code: str,
        clause_mapping: Optional[Dict[str, str]] = None,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DocumentInfo:
        """注册文档

        Args:
            doc_id: 文档唯一标识
            level: 文档层级
            name: 文档名称
            code: 文档编号
            clause_mapping: 条款映射关系 {当前条款: 上级条款}
            parent_id: 上级文档ID（可选，自动推断）
            metadata: 元数据

        Returns:
            DocumentInfo: 文档信息对象
        """
        # 如果没有指定parent_id，尝试自动查找
        if parent_id is None and level != DocumentLevel.LEVEL_1:
            parent_doc = self._find_parent_document(level, name)
            if parent_doc:
                parent_id = parent_doc.doc_id

        doc_info = DocumentInfo(
            doc_id=doc_id,
            level=level,
            name=name,
            code=code,
            clause_mapping=clause_mapping or {},
            parent_id=parent_id,
            metadata=metadata or {},
        )

        self._documents[doc_id] = doc_info
        self._level_documents[level].append(doc_id)
        self._references[doc_id] = []

        return doc_info

    def _find_parent_document(
        self, level: DocumentLevel, name: str
    ) -> Optional[DocumentInfo]:
        """根据名称查找上级文档

        Args:
            level: 当前层级
            name: 文档名称

        Returns:
            Optional[DocumentInfo]: 上级文档信息
        """
        parent_level = DocumentLevelConfig.get_parent_level(level)
        if parent_level is None:
            return None

        # 获取上级层级的所有文档
        parent_docs = self.get_documents_by_level(parent_level)

        # 根据名称关键词匹配（简单匹配，可根据需要优化）
        name_keywords = self._extract_keywords(name)
        for doc in parent_docs:
            doc_keywords = self._extract_keywords(doc.name)
            # 如果有共同关键词，认为是相关文档
            if name_keywords & doc_keywords:
                return doc

        # 如果没有匹配到，返回第一个（默认）
        return parent_docs[0] if parent_docs else None

    def _extract_keywords(self, name: str) -> set:
        """提取名称关键词

        Args:
            name: 文档名称

        Returns:
            set: 关键词集合
        """
        # 移除常见后缀，提取核心关键词
        stop_words = {"管理", "程序", "制度", "表格", "记录", "办法", "规范", "规定"}
        keywords = set()
        for word in stop_words:
            if word in name:
                # 提取关键词前的部分
                idx = name.find(word)
                if idx > 0:
                    keywords.add(name[:idx])
        return keywords if keywords else {name}

    def get_parent_document(self, doc_id: str) -> Optional[DocumentInfo]:
        """获取上级文档

        Args:
            doc_id: 文档ID

        Returns:
            Optional[DocumentInfo]: 上级文档信息
        """
        doc = self._documents.get(doc_id)
        if doc and doc.parent_id:
            return self._documents.get(doc.parent_id)
        return None

    def generate_reference(
        self,
        level: DocumentLevel,
        clause: Optional[str] = None,
        standard: Optional[str] = None,
        doc_id: Optional[str] = None,
        custom_format: Optional[str] = None,
    ) -> str:
        """生成引用文本

        Args:
            level: 文档层级
            clause: 条款号
            standard: 标准名称（仅一级文件使用）
            doc_id: 当前文档ID（用于获取父文档信息）
            custom_format: 自定义格式

        Returns:
            str: 引用文本
        """
        if custom_format:
            format_str = custom_format
        else:
            format_str = DocumentLevelConfig.get_reference_format(level)

        # 一级文件引用标准
        if level == DocumentLevel.LEVEL_1:
            if standard and clause:
                return format_str.format(standard=standard, clause=clause)
            return ""

        # 其他层级引用上级文件
        if doc_id:
            parent_doc = self.get_parent_document(doc_id)
            if parent_doc:
                # 获取映射后的条款号
                mapped_clause = clause
                if clause and doc_id in self._documents:
                    doc = self._documents[doc_id]
                    mapped_clause = doc.clause_mapping.get(clause, clause)

                if mapped_clause:
                    return format_str.format(
                        parent_name=parent_doc.name,
                        parent_code=parent_doc.code,
                        clause=mapped_clause,
                    )
                else:
                    # 三级和四级文件不需要条款号
                    return format_str.format(
                        parent_name=parent_doc.name,
                        parent_code=parent_doc.code,
                    )

        return ""

    def get_document_chain(self, doc_id: str) -> List[DocumentInfo]:
        """获取文档引用链（从一级到当前级别）

        Args:
            doc_id: 文档ID

        Returns:
            List[DocumentInfo]: 文档链列表（从一级开始）
        """
        chain = []
        current_doc = self._documents.get(doc_id)

        if not current_doc:
            return chain

        # 收集所有上级文档
        docs_to_add = []
        while current_doc:
            docs_to_add.append(current_doc)
            if current_doc.parent_id:
                current_doc = self._documents.get(current_doc.parent_id)
            else:
                break

        # 反转，使一级文档在前
        chain = list(reversed(docs_to_add))
        return chain

    def validate_reference(self, level: DocumentLevel, reference_text: str) -> bool:
        """验证引用是否正确

        Args:
            level: 文档层级
            reference_text: 引用文本

        Returns:
            bool: 验证结果
        """
        if not reference_text:
            return False

        config = DocumentLevelConfig.get_config(level)
        format_str = config.get("reference_format", "")

        # 简单验证：检查是否包含必要的占位符内容
        if level == DocumentLevel.LEVEL_1:
            # 一级文件应包含"标准"和"条款"
            return "标准" in reference_text and "条款" in reference_text
        else:
            # 其他层级应包含书名号和括号
            return "《" in reference_text and "》" in reference_text and "（" in reference_text

    def get_documents_by_level(self, level: DocumentLevel) -> List[DocumentInfo]:
        """按层级获取文档列表

        Args:
            level: 文档层级

        Returns:
            List[DocumentInfo]: 文档列表
        """
        doc_ids = self._level_documents.get(level, [])
        return [self._documents[doc_id] for doc_id in doc_ids if doc_id in self._documents]

    def build_hierarchy(self) -> Dict[str, Any]:
        """构建文档层级结构

        Returns:
            Dict[str, Any]: 层级结构树
        """
        hierarchy = {
            "project_id": self.project_id,
            "levels": {},
            "total_documents": len(self._documents),
        }

        for level in DocumentLevel:
            docs = self.get_documents_by_level(level)
            level_config = DocumentLevelConfig.get_config(level)

            hierarchy["levels"][level.name] = {
                "name": level_config.get("name"),
                "code_prefix": level_config.get("code_prefix"),
                "documents": [doc.to_dict() for doc in docs],
                "count": len(docs),
            }

        return hierarchy

    def export_references(self) -> Dict[str, Any]:
        """导出所有引用关系

        Returns:
            Dict[str, Any]: 引用关系数据
        """
        export_data = {
            "project_id": self.project_id,
            "export_time": datetime.now().isoformat(),
            "documents": {},
            "references": {},
            "hierarchy": self.build_hierarchy(),
        }

        # 导出所有文档
        for doc_id, doc in self._documents.items():
            export_data["documents"][doc_id] = doc.to_dict()

        # 导出引用关系
        for doc_id, refs in self._references.items():
            export_data["references"][doc_id] = [ref.to_dict() for ref in refs]

        return export_data

    def add_reference(
        self,
        source_doc_id: str,
        target_doc_id: str,
        reference_text: str,
        clause: Optional[str] = None,
        standard: Optional[str] = None,
    ) -> ReferenceInfo:
        """添加引用关系

        Args:
            source_doc_id: 源文档ID
            target_doc_id: 目标文档ID
            reference_text: 引用文本
            clause: 条款号
            standard: 标准名称

        Returns:
            ReferenceInfo: 引用信息
        """
        ref_info = ReferenceInfo(
            source_doc_id=source_doc_id,
            target_doc_id=target_doc_id,
            reference_text=reference_text,
            clause=clause,
            standard=standard,
        )

        if source_doc_id not in self._references:
            self._references[source_doc_id] = []

        self._references[source_doc_id].append(ref_info)
        return ref_info

    def get_references(self, doc_id: str) -> List[ReferenceInfo]:
        """获取文档的引用关系

        Args:
            doc_id: 文档ID

        Returns:
            List[ReferenceInfo]: 引用列表
        """
        return self._references.get(doc_id, [])

    def get_document(self, doc_id: str) -> Optional[DocumentInfo]:
        """获取文档信息

        Args:
            doc_id: 文档ID

        Returns:
            Optional[DocumentInfo]: 文档信息
        """
        return self._documents.get(doc_id)

    def generate_full_references(
        self, doc_id: str, standard: Optional[str] = None, clause: Optional[str] = None
    ) -> Dict[str, str]:
        """生成完整的引用链文本

        生成从当前文档到一级文件及标准的完整引用链。

        Args:
            doc_id: 文档ID
            standard: 标准名称
            clause: 当前条款号

        Returns:
            Dict[str, str]: 各级引用文本
        """
        doc = self._documents.get(doc_id)
        if not doc:
            return {}

        references = {}
        chain = self.get_document_chain(doc_id)

        # 生成每级的引用
        for i, chain_doc in enumerate(chain):
            level = chain_doc.level

            if level == DocumentLevel.LEVEL_1:
                # 一级文件引用标准
                if standard and clause:
                    ref_text = self.generate_reference(
                        level, clause=clause, standard=standard
                    )
                    references["standard"] = ref_text
            else:
                # 获取当前文档在父文档中的对应条款
                parent_clause = None
                if i > 0 and clause:
                    # 查找条款映射
                    current_in_chain = chain[i] if i < len(chain) else doc
                    parent_clause = current_in_chain.clause_mapping.get(clause, clause)

                ref_text = self.generate_reference(
                    level, clause=parent_clause, doc_id=chain_doc.doc_id
                )
                references[f"level_{level.value}"] = ref_text

        return references

    def save_to_file(self, filepath: str) -> None:
        """保存到文件

        Args:
            filepath: 文件路径
        """
        data = self.export_references()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath: str) -> None:
        """从文件加载

        Args:
            filepath: 文件路径
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.project_id = data.get("project_id", self.project_id)

        # 加载文档
        for doc_id, doc_data in data.get("documents", {}).items():
            doc_info = DocumentInfo.from_dict(doc_data)
            self._documents[doc_id] = doc_info
            self._level_documents[doc_info.level].append(doc_id)

        # 加载引用关系
        for doc_id, refs_data in data.get("references", {}).items():
            self._references[doc_id] = [
                ReferenceInfo(
                    source_doc_id=ref["source_doc_id"],
                    target_doc_id=ref["target_doc_id"],
                    reference_text=ref["reference_text"],
                    clause=ref.get("clause"),
                    standard=ref.get("standard"),
                    created_at=datetime.fromisoformat(ref["created_at"]),
                )
                for ref in refs_data
            ]


# 便捷函数
def create_document_manager(project_id: str) -> DocumentReferenceManager:
    """创建文档引用管理器

    Args:
        project_id: 项目ID

    Returns:
        DocumentReferenceManager: 文档引用管理器实例
    """
    return DocumentReferenceManager(project_id)


def get_level_name(level: DocumentLevel) -> str:
    """获取层级名称

    Args:
        level: 文档层级

    Returns:
        str: 层级名称
    """
    return DocumentLevelConfig.get_name(level)


def get_level_by_code_prefix(prefix: str) -> Optional[DocumentLevel]:
    """根据代码前缀获取层级

    Args:
        prefix: 代码前缀

    Returns:
        Optional[DocumentLevel]: 文档层级
    """
    for level in DocumentLevel:
        if DocumentLevelConfig.get_code_prefix(level) == prefix.upper():
            return level
    return None
