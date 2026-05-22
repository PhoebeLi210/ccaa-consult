#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 文件提取器
从各类文档（docx/pdf/xlsx/txt）中提取结构化信息。
不依赖audit模块的AIClient，使用纯正则和python-docx/pdfplumber/openpyxl实现。
"""

import re
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field


@dataclass
class ExtractedDocument:
    """提取后的文档结构化数据"""
    file_name: str = ""
    file_type: str = ""          # docx / pdf / xlsx / txt
    content: str = ""            # 全文文本
    paragraphs: List[str] = field(default_factory=list)
    tables: List[List[List[str]]] = field(default_factory=list)  # 三维列表：表 -> 行 -> 列
    metadata: Dict[str, Any] = field(default_factory=dict)


class FileExtractor:
    """通用文件提取器，支持 docx / pdf / xlsx / txt"""

    # ==================== 公共入口 ====================

    def parse_document(self, file_path: str) -> ExtractedDocument:
        """
        通用文件解析入口，根据扩展名自动分发。

        Args:
            file_path: 文件绝对路径

        Returns:
            ExtractedDocument 实例
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        suffix = path.suffix.lower()
        name = path.name

        if suffix == ".docx":
            return self.parse_docx(file_path)
        elif suffix == ".pdf":
            return self.parse_pdf(file_path)
        elif suffix in (".xlsx", ".xls"):
            return self.parse_xlsx(file_path)
        elif suffix == ".txt":
            return self._parse_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}，支持 .docx/.pdf/.xlsx/.txt")

    # ==================== DOCX 解析 ====================

    def parse_docx(self, file_path: str) -> ExtractedDocument:
        """
        解析 Word 文档，提取段落、表格和元数据。

        Args:
            file_path: .docx 文件路径

        Returns:
            ExtractedDocument
        """
        from docx import Document

        doc = Document(file_path)

        paragraphs: List[str] = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs.append(text)

        tables: List[List[List[str]]] = []
        for table in doc.tables:
            table_data: List[List[str]] = []
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                table_data.append(row_data)
            tables.append(table_data)

        # 提取元数据
        core_props = doc.core_properties
        metadata: Dict[str, Any] = {
            "author": core_props.author or "",
            "title": core_props.title or "",
            "subject": core_props.subject or "",
            "created": str(core_props.created) if core_props.created else "",
            "modified": str(core_props.modified) if core_props.modified else "",
            "last_modified_by": core_props.last_modified_by or "",
        }

        full_text = "\n".join(paragraphs)
        for tbl in tables:
            for row in tbl:
                full_text += "\n" + " | ".join(row)

        return ExtractedDocument(
            file_name=Path(file_path).name,
            file_type="docx",
            content=full_text,
            paragraphs=paragraphs,
            tables=tables,
            metadata=metadata,
        )

    # ==================== PDF 解析 ====================

    def parse_pdf(self, file_path: str) -> ExtractedDocument:
        """
        解析 PDF 文件，提取文本和表格。

        Args:
            file_path: .pdf 文件路径

        Returns:
            ExtractedDocument
        """
        import pdfplumber

        paragraphs: List[str] = []
        tables: List[List[List[str]]] = []
        full_text_parts: List[str] = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # 提取文本
                page_text = page.extract_text()
                if page_text:
                    lines = [line.strip() for line in page_text.split("\n") if line.strip()]
                    paragraphs.extend(lines)
                    full_text_parts.append(page_text)

                # 提取表格
                page_tables = page.extract_tables()
                if page_tables:
                    for tbl in page_tables:
                        # pdfplumber 返回的表格单元格可能是 None
                        cleaned = []
                        for row in tbl:
                            cleaned.append([str(cell).strip() if cell else "" for cell in row])
                        tables.append(cleaned)
                        for row in cleaned:
                            full_text_parts.append(" | ".join(row))

        return ExtractedDocument(
            file_name=Path(file_path).name,
            file_type="pdf",
            content="\n".join(full_text_parts),
            paragraphs=paragraphs,
            tables=tables,
            metadata={},
        )

    # ==================== XLSX 解析 ====================

    def parse_xlsx(self, file_path: str) -> ExtractedDocument:
        """
        解析 Excel 文件，提取所有工作表的文本和表格数据。

        Args:
            file_path: .xlsx/.xls 文件路径

        Returns:
            ExtractedDocument
        """
        from openpyxl import load_workbook

        wb = load_workbook(file_path, data_only=True)

        paragraphs: List[str] = []
        tables: List[List[List[str]]] = []
        full_text_parts: List[str] = []

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            table_data: List[List[str]] = []

            for row in ws.iter_rows(values_only=True):
                row_data = [str(cell).strip() if cell is not None else "" for cell in row]
                # 跳过完全空行
                if any(row_data):
                    table_data.append(row_data)
                    line = " | ".join(row_data)
                    paragraphs.append(line)
                    full_text_parts.append(f"[{sheet_name}] {line}")

            if table_data:
                tables.append(table_data)

        return ExtractedDocument(
            file_name=Path(file_path).name,
            file_type="xlsx",
            content="\n".join(full_text_parts),
            paragraphs=paragraphs,
            tables=tables,
            metadata={"sheets": wb.sheetnames},
        )

    # ==================== TXT 解析 ====================

    def _parse_txt(self, file_path: str) -> ExtractedDocument:
        """解析纯文本文件"""
        encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
        content = ""

        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, LookupError):
                continue

        paragraphs = [line.strip() for line in content.split("\n") if line.strip()]

        return ExtractedDocument(
            file_name=Path(file_path).name,
            file_type="txt",
            content=content,
            paragraphs=paragraphs,
            tables=[],
            metadata={},
        )

    # ==================== 营业执照解析 ====================

    def parse_business_license(self, file_path: str) -> Dict[str, Any]:
        """
        解析营业执照，提取关键字段。

        提取字段：公司名称、统一社会信用代码、注册地址、法定代表人

        Args:
            file_path: 营业执照文件路径（支持 docx/pdf/xlsx/txt）

        Returns:
            包含提取字段的字典
        """
        doc = self.parse_document(file_path)
        content = doc.content
        result: Dict[str, Any] = {"file_name": doc.file_name}

        # 公司名称
        result["company_name"] = self._extract_by_patterns(content, [
            r"名\s*称[：:]\s*(.+?)(?:\n|$)",
            r"企业名称[：:]\s*(.+?)(?:\n|$)",
            r"公司名称[：:]\s*(.+?)(?:\n|$)",
            r"经营者[：:]\s*(.+?)(?:\n|$)",
        ])

        # 统一社会信用代码
        result["credit_code"] = self._extract_by_patterns(content, [
            r"统一社会信用代码[：:]\s*([0-9A-Z]{18})",
            r"信用代码[：:]\s*([0-9A-Z]{18})",
            r"([0-9A-Z]{18})",  # 兜底：18位大写字母数字
        ])

        # 注册地址
        result["registered_address"] = self._extract_by_patterns(content, [
            r"住\s*所[：:]\s*(.+?)(?:\n|$)",
            r"注册地址[：:]\s*(.+?)(?:\n|$)",
            r"经营场所[：:]\s*(.+?)(?:\n|$)",
            r"地址[：:]\s*(.+?)(?:\n|$)",
        ])

        # 法定代表人
        result["legal_representative"] = self._extract_by_patterns(content, [
            r"法定代表人[：:]\s*(.+?)(?:\n|$)",
            r"负责人[：:]\s*(.+?)(?:\n|$)",
            r"经营者[：:]\s*(.+?)(?:\n|$)",
        ])

        # 注册资本
        result["registered_capital"] = self._extract_by_patterns(content, [
            r"注册资本[：:]\s*(.+?)(?:\n|$)",
        ])

        # 成立日期
        result["establishment_date"] = self._extract_by_patterns(content, [
            r"成立日期[：:]\s*(.+?)(?:\n|$)",
            r"(?:营业|经营)期限[：:自]\s*(\d{4}年\d{1,2}月\d{1,2}日)",
        ])

        # 经营范围
        result["business_scope"] = self._extract_by_patterns(content, [
            r"经营范围[：:]\s*(.+?)(?:\n(?:名|统|住|法|注|成|类|营业))",
            r"经营范围[：:]\s*(.+)",
        ])

        # 公司类型
        result["company_type"] = self._extract_by_patterns(content, [
            r"类\s*型[：:]\s*(.+?)(?:\n|$)",
            r"公司类型[：:]\s*(.+?)(?:\n|$)",
        ])

        return result

    # ==================== 质量手册解析 ====================

    def parse_quality_manual(self, file_path: str) -> Dict[str, Any]:
        """
        解析质量手册，提取关键字段。

        提取字段：手册编号、质量方针、质量目标、发布日期、版本号

        Args:
            file_path: 质量手册文件路径

        Returns:
            包含提取字段的字典
        """
        doc = self.parse_document(file_path)
        content = doc.content
        result: Dict[str, Any] = {"file_name": doc.file_name}

        # 手册编号
        result["manual_number"] = self._extract_by_patterns(content, [
            r"手册编号[：:]\s*([A-Z0-9\-/]+)",
            r"编号[：:]\s*([A-Z0-9\-/]+)",
            r"文件编号[：:]\s*([A-Z0-9\-/]+)",
        ])

        # 质量方针
        result["quality_policy"] = self._extract_by_patterns(content, [
            r"质量方针[：:]\s*(.+?)(?:\n\n|\n(?:[一二三四五六七八九十\d]+[、.]))",
            r"质量方针[：:]\s*(.+?)(?:\n|$)",
        ])

        # 质量目标
        result["quality_goals"] = self._extract_multiple_by_patterns(content, [
            r"质量目标[：:]\s*(.+?)(?:\n\n|\n(?:[一二三四五六七八九十\d]+[、.]))",
            r"质量目标[：:]\s*(.+?)(?:\n|$)",
        ])

        # 发布日期
        result["release_date"] = self._extract_by_patterns(content, [
            r"发布日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)",
            r"发布日期[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
            r"发布.*?日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)",
            r"实施日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)",
        ])

        # 版本号
        result["version"] = self._extract_by_patterns(content, [
            r"版本[：:]\s*([Vv]?\d+\.?\d*)",
            r"版次[：:]\s*([A-Z]?\d+)",
            r"第\s*([一二三四五六七八九十\d]+)\s*版",
        ])

        # 发布令 / 批准人
        result["approver"] = self._extract_by_patterns(content, [
            r"批准[人：:]\s*(.+?)(?:\n|$)",
            r"发布人[：:]\s*(.+?)(?:\n|$)",
        ])

        # 编制人
        result["author"] = self._extract_by_patterns(content, [
            r"编制[人：:]\s*(.+?)(?:\n|$)",
            r"编写[人：:]\s*(.+?)(?:\n|$)",
        ])

        # 适用范围
        result["scope"] = self._extract_by_patterns(content, [
            r"适用范围[：:]\s*(.+?)(?:\n\n|\n(?:[一二三四五六七八九十\d]+[、.]))",
            r"适用范围[：:]\s*(.+?)(?:\n|$)",
        ])

        return result

    # ==================== 租赁合同解析 ====================

    def parse_lease_contract(self, file_path: str) -> Dict[str, Any]:
        """
        解析租赁合同，提取关键字段。

        提取字段：办公地址、租赁期限、面积

        Args:
            file_path: 租赁合同文件路径

        Returns:
            包含提取字段的字典
        """
        doc = self.parse_document(file_path)
        content = doc.content
        result: Dict[str, Any] = {"file_name": doc.file_name}

        # 办公地址 / 租赁地址
        result["office_address"] = self._extract_by_patterns(content, [
            r"(?:房屋)?(?:租赁)?地址[：:]\s*(.+?)(?:\n|$)",
            r"租赁场所[：:]\s*(.+?)(?:\n|$)",
            r"坐落[：:]\s*(.+?)(?:\n|$)",
            r"位于[：:]\s*(.+?)(?:\n|$)",
        ])

        # 租赁期限
        result["lease_term"] = self._extract_by_patterns(content, [
            r"租赁期限[：:]\s*(.+?)(?:\n|$)",
            r"租期[：:]\s*(.+?)(?:\n|$)",
            r"租赁时间[：:]\s*(.+?)(?:\n|$)",
        ])

        # 起始日期
        result["start_date"] = self._extract_by_patterns(content, [
            r"(?:自|起)[：:]?\s*(\d{4}年\d{1,2}月\d{1,2}日)",
            r"起始日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)",
        ])

        # 截止日期
        result["end_date"] = self._extract_by_patterns(content, [
            r"(?:至|止|到)[：:]?\s*(\d{4}年\d{1,2}月\d{1,2}日)",
            r"截止日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)",
        ])

        # 面积
        result["area"] = self._extract_by_patterns(content, [
            r"(?:建筑面积|租赁面积|面积)[：:]\s*(\d+(?:\.\d+)?)\s*(?:平方米|㎡|m2|m²)?",
            r"(\d+(?:\.\d+)?)\s*(?:平方米|㎡|m2|m²)",
        ])

        # 月租金
        result["monthly_rent"] = self._extract_by_patterns(content, [
            r"(?:月租金|租金)[：:]\s*(.+?)(?:\n|$)",
            r"每月租金[：:]\s*(.+?)(?:\n|$)",
        ])

        # 出租方
        result["lessor"] = self._extract_by_patterns(content, [
            r"(?:出租方|甲方)[：:]\s*(.+?)(?:\n|$)",
        ])

        # 承租方
        result["lessee"] = self._extract_by_patterns(content, [
            r"(?:承租方|乙方)[：:]\s*(.+?)(?:\n|$)",
        ])

        return result

    # ==================== 方针提取 ====================

    def extract_policy(self, content: str, policy_type: str) -> Optional[str]:
        """
        从文本中提取指定类型的方针。

        Args:
            content: 文档全文
            policy_type: 方针类型，支持 "质量方针" / "环境方针" / "安全方针"

        Returns:
            提取到的方针文本，未找到返回 None
        """
        patterns_map = {
            "质量方针": [
                r"质量方针[：:]\s*(.+?)(?:\n\n|\n(?:[一二三四五六七八九十\d]+[、.\s]))",
                r"质量方针[：:]\s*(.+?)(?:\n|$)",
                r"质量方针\s+(.{10,80}?)(?:\n|$)",
            ],
            "环境方针": [
                r"环境方针[：:]\s*(.+?)(?:\n\n|\n(?:[一二三四五六七八九十\d]+[、.\s]))",
                r"环境方针[：:]\s*(.+?)(?:\n|$)",
                r"环境方针\s+(.{10,80}?)(?:\n|$)",
            ],
            "安全方针": [
                r"(?:职业健康)?安全方针[：:]\s*(.+?)(?:\n\n|\n(?:[一二三四五六七八九十\d]+[、.\s]))",
                r"(?:职业健康)?安全方针[：:]\s*(.+?)(?:\n|$)",
                r"(?:职业健康)?安全方针\s+(.{10,80}?)(?:\n|$)",
            ],
        }

        patterns = patterns_map.get(policy_type, [])
        return self._extract_by_patterns(content, patterns)

    def extract_all_policies(self, files: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        从多个文件中提取所有方针。

        Args:
            files: 文件路径列表

        Returns:
            按方针类型组织的字典，如:
            {
                "质量方针": {"value": "...", "source": "file.docx"},
                "环境方针": {"value": "...", "source": "file.docx"},
                "安全方针": {"value": "...", "source": "file.docx"},
            }
        """
        policy_types = ["质量方针", "环境方针", "安全方针"]
        results: Dict[str, Dict[str, Any]] = {}

        for policy_type in policy_types:
            results[policy_type] = {"value": None, "source": None}

        for file_path in files:
            try:
                doc = self.parse_document(file_path)
                for policy_type in policy_types:
                    if results[policy_type]["value"] is None:
                        value = self.extract_policy(doc.content, policy_type)
                        if value:
                            results[policy_type] = {
                                "value": value,
                                "source": doc.file_name,
                            }
            except Exception:
                # 单个文件解析失败不影响其他文件
                continue

        return results

    # ==================== 内部工具方法 ====================

    @staticmethod
    def _extract_by_patterns(content: str, patterns: List[str]) -> Optional[str]:
        """
        按优先级依次尝试正则匹配，返回第一个匹配结果。

        Args:
            content: 待匹配文本
            patterns: 正则表达式列表（按优先级排列）

        Returns:
            匹配到的字符串，去除首尾空白；全部不匹配返回 None
        """
        for pattern in patterns:
            try:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    value = match.group(1).strip()
                    # 过滤掉明显无效的值
                    if value and value not in ("", "nan", "None", "无", "/"):
                        return value
            except re.error:
                continue
        return None

    @staticmethod
    def _extract_multiple_by_patterns(content: str, patterns: List[str]) -> List[str]:
        """
        按正则提取多个匹配项（用于质量目标等列表型字段）。

        Args:
            content: 待匹配文本
            patterns: 正则表达式列表

        Returns:
            匹配到的字符串列表
        """
        for pattern in patterns:
            try:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    raw = match.group(1).strip()
                    # 尝试按序号分割
                    items = re.split(r"(?:[一二三四五六七八九十\d]+[、.）)])\s*", raw)
                    items = [item.strip() for item in items if item.strip()]
                    if items:
                        return items
                    return [raw]
            except re.error:
                continue
        return []


# ==================== 便捷函数 ====================

def parse_document(file_path: str) -> ExtractedDocument:
    """便捷函数：解析文件"""
    return FileExtractor().parse_document(file_path)


def parse_business_license(file_path: str) -> Dict[str, Any]:
    """便捷函数：解析营业执照"""
    return FileExtractor().parse_business_license(file_path)


def parse_quality_manual(file_path: str) -> Dict[str, Any]:
    """便捷函数：解析质量手册"""
    return FileExtractor().parse_quality_manual(file_path)


def parse_lease_contract(file_path: str) -> Dict[str, Any]:
    """便捷函数：解析租赁合同"""
    return FileExtractor().parse_lease_contract(file_path)


def extract_all_policies(files: List[str]) -> Dict[str, Dict[str, Any]]:
    """便捷函数：从多个文件中提取所有方针"""
    return FileExtractor().extract_all_policies(files)
