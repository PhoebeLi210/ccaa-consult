#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档导出器 - 将GeneratedDocument转换为真实的.docx文件

使用python-docx库创建专业的Word文档
支持：
- 标题样式
- 段落格式
- 表格
- 列表
- 页眉页脚
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from app.modules.generator.base import GeneratedDocument, FileLevel, DocumentType


class DocxExporter:
    """Word文档导出器
    
    将GeneratedDocument对象导出为真实的.docx文件
    """
    
    def __init__(self, output_dir: str = "./output"):
        """
        初始化导出器
        
        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 默认字体配置
        self.default_font = {
            'ascii': 'Arial',
            'east_asia': 'SimSun',  # 宋体
            'h_ansi': 'Arial',
        }
        self.title_font = {
            'ascii': 'Arial',
            'east_asia': 'SimHei',  # 黑体
            'h_ansi': 'Arial',
        }
    
    def export(self, doc: GeneratedDocument, company_name: str = "") -> Path:
        """
        导出单个文档
        
        Args:
            doc: 生成的文档对象
            company_name: 公司名称（用于创建子目录）
            
        Returns:
            导出文件的路径
        """
        # 创建输出目录
        if company_name:
            output_path = self.output_dir / company_name / self._get_level_dir(doc.file_level)
        else:
            output_path = self.output_dir / self._get_level_dir(doc.file_level)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 创建Word文档
        word_doc = Document()
        
        # 设置页面
        self._setup_page(word_doc)
        
        # 设置样式
        self._setup_styles(word_doc)
        
        # 添加文档内容
        self._add_content(word_doc, doc)
        
        # 保存文件
        file_path = output_path / doc.file_name
        word_doc.save(str(file_path))
        
        return file_path
    
    def export_batch(
        self, 
        documents: List[GeneratedDocument], 
        company_name: str = ""
    ) -> List[Path]:
        """
        批量导出文档
        
        Args:
            documents: 文档列表
            company_name: 公司名称
            
        Returns:
            导出文件路径列表
        """
        exported_paths = []
        for doc in documents:
            try:
                path = self.export(doc, company_name)
                exported_paths.append(path)
            except Exception as e:
                print(f"导出文档失败: {doc.file_name}, 错误: {e}")
        return exported_paths
    
    def export_to_bytes(self, doc: GeneratedDocument) -> bytes:
        """
        导出为字节流（用于API下载）
        
        Args:
            doc: 生成的文档对象
            
        Returns:
            文档的字节内容
        """
        from io import BytesIO
        
        word_doc = Document()
        self._setup_page(word_doc)
        self._setup_styles(word_doc)
        self._add_content(word_doc, doc)
        
        buffer = BytesIO()
        word_doc.save(buffer)
        buffer.seek(0)
        
        return buffer.getvalue()
    
    def _get_level_dir(self, file_level: FileLevel) -> str:
        """获取层级目录名"""
        level_map = {
            FileLevel.LEVEL_1: "01-一级文件-管理手册",
            FileLevel.LEVEL_2: "02-二级文件-程序文件",
            FileLevel.LEVEL_3: "03-三级文件-作业指导书",
            FileLevel.LEVEL_4: "04-四级文件-记录表格",
        }
        return level_map.get(file_level, "04-四级文件-记录表格")
    
    def _setup_page(self, doc: Document):
        """设置页面格式"""
        section = doc.sections[0]
        
        # 页面大小（A4）
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        
        # 页边距
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.17)
        section.right_margin = Cm(3.17)
    
    def _setup_styles(self, doc: Document):
        """设置文档样式"""
        styles = doc.styles
        
        # 设置默认字体
        style = styles['Normal']
        style.font.name = self.default_font['ascii']
        style.font.size = Pt(12)
        style._element.rPr.rFonts.set(qn('w:eastAsia'), self.default_font['east_asia'])
        
        # 创建标题样式
        heading_styles = [
            ('Heading1', '文档标题', 22, True),
            ('Heading2', '一级标题', 16, True),
            ('Heading3', '二级标题', 14, True),
            ('Heading4', '三级标题', 12, True),
        ]
        
        for style_name, name, size, bold in heading_styles:
            try:
                style = styles[style_name]
            except KeyError:
                style = styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
            
            style.font.name = self.title_font['ascii']
            style.font.size = Pt(size)
            style.font.bold = bold
            style._element.rPr.rFonts.set(qn('w:eastAsia'), self.title_font['east_asia'])
    
    def _add_content(self, word_doc: Document, doc: GeneratedDocument):
        """添加文档内容"""
        # 添加文档标题
        self._add_title(word_doc, doc.title or doc.file_name.replace('.docx', ''))
        
        # 添加文件编号
        if doc.file_code:
            self._add_file_code(word_doc, doc.file_code)
        
        # 解析并添加正文内容
        content = doc.content
        if content:
            self._parse_and_add_content(word_doc, content)
    
    def _add_title(self, doc: Document, title: str):
        """添加文档标题"""
        # 添加空行
        doc.add_paragraph()
        
        # 添加标题
        title_para = doc.add_paragraph()
        title_run = title_para.add_run(title)
        title_run.font.size = Pt(22)
        title_run.font.bold = True
        title_run.font.name = self.title_font['ascii']
        title_run._element.rPr.rFonts.set(qn('w:eastAsia'), self.title_font['east_asia'])
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 添加空行
        doc.add_paragraph()
    
    def _add_file_code(self, doc: Document, file_code: str):
        """添加文件编号"""
        code_para = doc.add_paragraph()
        code_run = code_para.add_run(f"文件编号：{file_code}")
        code_run.font.size = Pt(12)
        code_run.font.name = self.default_font['ascii']
        code_run._element.rPr.rFonts.set(qn('w:eastAsia'), self.default_font['east_asia'])
        code_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()
    
    def _parse_and_add_content(self, doc: Document, content: str):
        """解析内容并添加到文档
        
        支持的内容格式：
        - Markdown标题（# ## ###）
        - 有序/无序列表
        - 表格
        - 普通段落
        """
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 空行
            if not line:
                i += 1
                continue
            
            # 标题
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title_text = line.lstrip('#').strip()
                self._add_heading(doc, title_text, level)
                i += 1
                continue
            
            # 表格（检测 | 分隔符）
            if '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
                table_lines = []
                while i < len(lines) and '|' in lines[i]:
                    table_lines.append(lines[i])
                    i += 1
                self._add_table(doc, table_lines)
                continue
            
            # 无序列表
            if line.startswith('- ') or line.startswith('* '):
                list_items = []
                while i < len(lines):
                    l = lines[i].strip()
                    if l.startswith('- ') or l.startswith('* '):
                        list_items.append(l[2:])
                        i += 1
                    elif l and not l.startswith('- ') and not l.startswith('* '):
                        break
                    else:
                        i += 1
                self._add_bullet_list(doc, list_items)
                continue
            
            # 有序列表
            if re.match(r'^\d+\.', line):
                list_items = []
                while i < len(lines):
                    l = lines[i].strip()
                    match = re.match(r'^(\d+)\.\s*(.*)', l)
                    if match:
                        list_items.append(match.group(2))
                        i += 1
                    elif l and not re.match(r'^\d+\.', l):
                        break
                    else:
                        i += 1
                self._add_numbered_list(doc, list_items)
                continue
            
            # 普通段落
            para_text = line
            i += 1
            # 合并连续的非特殊行
            while i < len(lines):
                next_line = lines[i].strip()
                if (next_line and 
                    not next_line.startswith('#') and 
                    not next_line.startswith('-') and 
                    not next_line.startswith('*') and
                    not re.match(r'^\d+\.', next_line) and
                    '|' not in next_line):
                    para_text += ' ' + next_line
                    i += 1
                else:
                    break
            
            self._add_paragraph(doc, para_text)
    
    def _add_heading(self, doc: Document, text: str, level: int):
        """添加标题"""
        # 限制级别
        level = min(level, 4)
        
        if level == 1:
            heading = doc.add_heading(text, level=1)
        elif level == 2:
            heading = doc.add_heading(text, level=2)
        elif level == 3:
            heading = doc.add_heading(text, level=3)
        else:
            heading = doc.add_heading(text, level=4)
        
        # 设置中文字体
        for run in heading.runs:
            run.font.name = self.title_font['ascii']
            run._element.rPr.rFonts.set(qn('w:eastAsia'), self.title_font['east_asia'])
    
    def _add_paragraph(self, doc: Document, text: str, indent: bool = True):
        """添加段落"""
        para = doc.add_paragraph()
        run = para.add_run(text)
        run.font.name = self.default_font['ascii']
        run.font.size = Pt(12)
        run._element.rPr.rFonts.set(qn('w:eastAsia'), self.default_font['east_asia'])
        
        # 首行缩进
        if indent and len(text) > 0:
            para.paragraph_format.first_line_indent = Cm(0.74)  # 两个字符
        
        para.paragraph_format.line_spacing = 1.5
    
    def _add_bullet_list(self, doc: Document, items: List[str]):
        """添加无序列表"""
        for item in items:
            para = doc.add_paragraph(style='List Bullet')
            run = para.add_run(item)
            run.font.name = self.default_font['ascii']
            run.font.size = Pt(12)
            run._element.rPr.rFonts.set(qn('w:eastAsia'), self.default_font['east_asia'])
    
    def _add_numbered_list(self, doc: Document, items: List[str]):
        """添加有序列表"""
        for item in items:
            para = doc.add_paragraph(style='List Number')
            run = para.add_run(item)
            run.font.name = self.default_font['ascii']
            run.font.size = Pt(12)
            run._element.rPr.rFonts.set(qn('w:eastAsia'), self.default_font['east_asia'])
    
    def _add_table(self, doc: Document, table_lines: List[str]):
        """添加表格"""
        if len(table_lines) < 2:
            return
        
        # 解析表格数据
        rows_data = []
        for line in table_lines:
            # 跳过分隔行（如 |---|---|）
            if re.match(r'^[\|\-\s:]+$', line):
                continue
            cells = [cell.strip() for cell in line.split('|')]
            # 移除首尾空元素
            cells = [c for c in cells if c or cells.index(c) not in [0, len(cells)-1]]
            if cells:
                rows_data.append(cells)
        
        if not rows_data:
            return
        
        # 确定列数
        num_cols = max(len(row) for row in rows_data)
        
        # 创建表格
        table = doc.add_table(rows=len(rows_data), cols=num_cols)
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # 填充数据
        for i, row_data in enumerate(rows_data):
            row = table.rows[i]
            for j, cell_text in enumerate(row_data):
                if j < num_cols:
                    cell = row.cells[j]
                    cell.text = cell_text
                    # 设置单元格字体
                    for para in cell.paragraphs:
                        for run in para.runs:
                            run.font.name = self.default_font['ascii']
                            run.font.size = Pt(10)
                            run._element.rPr.rFonts.set(qn('w:eastAsia'), self.default_font['east_asia'])
        
        # 表格后添加空行
        doc.add_paragraph()


class DocumentPackager:
    """文档打包器 - 将所有文档打包为ZIP"""
    
    import zipfile
    from io import BytesIO
    
    def __init__(self, exporter: DocxExporter):
        self.exporter = exporter
    
    def create_package(
        self, 
        documents: List[GeneratedDocument], 
        company_name: str
    ) -> Path:
        """
        创建文档包（ZIP格式）
        
        Args:
            documents: 文档列表
            company_name: 公司名称
            
        Returns:
            ZIP文件路径
        """
        import zipfile
        
        # 先导出所有文档
        exported_paths = self.exporter.export_batch(documents, company_name)
        
        # 创建ZIP文件
        zip_path = self.exporter.output_dir / f"{company_name}_体系文件.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for path in exported_paths:
                # 使用相对路径
                arcname = path.relative_to(self.exporter.output_dir)
                zf.write(path, arcname)
        
        return zip_path
    
    def create_package_bytes(
        self, 
        documents: List[GeneratedDocument]
    ) -> bytes:
        """
        创建文档包并返回字节流
        
        Args:
            documents: 文档列表
            
        Returns:
            ZIP文件的字节内容
        """
        import zipfile
        from io import BytesIO
        
        buffer = BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for doc in documents:
                doc_bytes = self.exporter.export_to_bytes(doc)
                # 按层级组织目录结构
                level_dir = self.exporter._get_level_dir(doc.file_level)
                file_path = f"{level_dir}/{doc.file_name}"
                zf.writestr(file_path, doc_bytes)
        
        buffer.seek(0)
        return buffer.getvalue()


# ============================================================
# 便捷函数
# ============================================================

def export_document(
    doc: GeneratedDocument, 
    output_dir: str = "./output",
    company_name: str = ""
) -> Path:
    """导出单个文档"""
    exporter = DocxExporter(output_dir)
    return exporter.export(doc, company_name)


def export_documents(
    documents: List[GeneratedDocument],
    output_dir: str = "./output",
    company_name: str = ""
) -> List[Path]:
    """批量导出文档"""
    exporter = DocxExporter(output_dir)
    return exporter.export_batch(documents, company_name)


def create_document_package(
    documents: List[GeneratedDocument],
    output_dir: str = "./output",
    company_name: str = "企业"
) -> Path:
    """创建文档包"""
    exporter = DocxExporter(output_dir)
    packager = DocumentPackager(exporter)
    return packager.create_package(documents, company_name)


def get_document_bytes(doc: GeneratedDocument) -> bytes:
    """获取文档字节流（用于API下载）"""
    exporter = DocxExporter()
    return exporter.export_to_bytes(doc)


def get_package_bytes(documents: List[GeneratedDocument]) -> bytes:
    """获取文档包字节流（用于API下载）"""
    exporter = DocxExporter()
    packager = DocumentPackager(exporter)
    return packager.create_package_bytes(documents)
