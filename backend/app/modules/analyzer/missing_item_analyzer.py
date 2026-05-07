#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 缺失项分析器

核心功能：
1. 基于ISO标准条款检查已生成文件的覆盖情况
2. 输出缺失项报告
3. 提供补充建议
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ClauseAnalysis:
    """条款分析结果"""
    clause: str  # 条款号
    title: str  # 条款标题
    status: str  # covered/partial/missing
    document: Optional[str] = None  # 所在文档
    evidence: Optional[str] = None  # 证据描述
    suggestion: Optional[str] = None  # 补充建议


class MissingItemAnalyzer:
    """缺失项分析器"""

    # ISO9001条款清单
    ISO9001_CLAUSES = [
        ("4.1", "理解组织及其环境"),
        ("4.2", "理解相关方的需求和期望"),
        ("4.3", "确定质量管理体系的范围"),
        ("4.4", "质量管理体系及其过程"),
        ("5.1", "领导作用和承诺"),
        ("5.2", "方针"),
        ("5.3", "组织的岗位、职责和权限"),
        ("6.1", "应对风险和机遇的措施"),
        ("6.2", "质量目标及其实现的策划"),
        ("6.3", "变更的策划"),
        ("7.1.1", "总则（资源）"),
        ("7.1.2", "人员"),
        ("7.1.3", "基础设施"),
        ("7.1.4", "过程运行环境"),
        ("7.1.5", "监视和测量资源"),
        ("7.1.6", "组织的知识"),
        ("7.2", "能力"),
        ("7.3", "意识"),
        ("7.4", "沟通"),
        ("7.5", "文件化信息"),
        ("8.1", "运行策划和控制"),
        ("8.2", "产品和服务要求"),
        ("8.3", "产品和服务的设计和开发"),
        ("8.4", "外部提供的过程、产品和服务的控制"),
        ("8.5.1", "生产和服务提供的控制"),
        ("8.5.2", "标识和可追溯性"),
        ("8.5.3", "顾客或外部供方的财产"),
        ("8.5.4", "防护"),
        ("8.5.5", "交付后活动"),
        ("8.5.6", "更改控制"),
        ("8.6", "产品和服务的放行"),
        ("8.7", "不合格输出的控制"),
        ("9.1.1", "监视、测量、分析和评价总则"),
        ("9.1.2", "顾客满意"),
        ("9.1.3", "分析与评价"),
        ("9.2", "内部审核"),
        ("9.3", "管理评审"),
        ("10.1", "总则（改进）"),
        ("10.2", "不合格和纠正措施"),
        ("10.3", "持续改进"),
    ]

    # ISO14001条款清单
    ISO14001_CLAUSES = [
        ("4.1", "理解组织及其环境"),
        ("4.2", "理解相关方的需求和期望"),
        ("4.3", "确定环境管理体系的范围"),
        ("4.4", "环境管理体系"),
        ("5.1", "领导作用和承诺"),
        ("5.2", "环境方针"),
        ("5.3", "组织的岗位、职责和权限"),
        ("6.1.1", "总则（策划）"),
        ("6.1.2", "环境因素"),
        ("6.1.3", "合规义务"),
        ("6.1.4", "措施的策划"),
        ("6.2", "环境目标及其实现的策划"),
        ("7.1", "资源"),
        ("7.2", "能力"),
        ("7.3", "意识"),
        ("7.4", "信息交流"),
        ("7.5", "文件化信息"),
        ("8.1", "运行策划和控制"),
        ("8.2", "应急准备和响应"),
        ("9.1.1", "监视、测量、分析和评价总则"),
        ("9.1.2", "合规性评价"),
        ("9.2", "内部审核"),
        ("9.3", "管理评审"),
        ("10.1", "总则（改进）"),
        ("10.2", "不合格和纠正措施"),
        ("10.3", "持续改进"),
    ]

    # ISO45001条款清单
    ISO45001_CLAUSES = [
        ("4.1", "理解组织及其环境"),
        ("4.2", "理解工作人员和其他相关方的需求和期望"),
        ("4.3", "确定职业健康安全管理体系的范围"),
        ("4.4", "职业健康安全管理体系"),
        ("5.1", "领导作用和承诺"),
        ("5.2", "职业健康安全方针"),
        ("5.3", "组织的岗位、职责和权限"),
        ("5.4", "工作人员的协商和参与"),
        ("6.1.1", "总则（策划）"),
        ("6.1.2", "危险源辨识"),
        ("6.1.3", "合规义务"),
        ("6.1.4", "措施的策划"),
        ("6.2", "职业健康安全目标及其实现的策划"),
        ("7.1", "资源"),
        ("7.2", "能力"),
        ("7.3", "意识"),
        ("7.4", "信息交流"),
        ("7.5", "文件化信息"),
        ("8.1", "运行策划和控制"),
        ("8.2", "应急准备和响应"),
        ("9.1.1", "监视、测量、分析和评价总则"),
        ("9.1.2", "合规性评价"),
        ("9.2", "内部审核"),
        ("9.3", "管理评审"),
        ("10.1", "总则（改进）"),
        ("10.2", "事件、不合格和纠正措施"),
        ("10.3", "持续改进"),
    ]

    def __init__(self):
        self.clauses_map = {
            "ISO9001": self.ISO9001_CLAUSES,
            "ISO14001": self.ISO14001_CLAUSES,
            "ISO45001": self.ISO45001_CLAUSES,
        }

    def analyze(
        self,
        documents: List[Dict[str, Any]],
        standards: List[str]
    ) -> Dict[str, Any]:
        """
        分析文档覆盖情况

        Args:
            documents: 已生成的文档列表
            standards: 目标标准列表

        Returns:
            分析报告
        """
        result = {
            "summary": {
                "total_clauses": 0,
                "covered": 0,
                "partial": 0,
                "missing": 0,
            },
            "details": [],
            "missing_items": [],
            "suggestions": [],
        }

        # 获取所有需要检查的条款
        all_clauses = []
        for standard in standards:
            clauses = self.clauses_map.get(standard, [])
            for clause_num, clause_title in clauses:
                all_clauses.append({
                    "clause": clause_num,
                    "title": clause_title,
                    "standard": standard,
                })

        result["summary"]["total_clauses"] = len(all_clauses)

        # 检查每个条款的覆盖情况
        for clause_info in all_clauses:
            analysis = self._check_clause_coverage(clause_info, documents)
            result["details"].append(analysis)

            if analysis.status == "covered":
                result["summary"]["covered"] += 1
            elif analysis.status == "partial":
                result["summary"]["partial"] += 1
                result["missing_items"].append({
                    "clause": analysis.clause,
                    "title": analysis.title,
                    "suggestion": analysis.suggestion,
                })
            else:
                result["summary"]["missing"] += 1
                result["missing_items"].append({
                    "clause": analysis.clause,
                    "title": analysis.title,
                    "suggestion": analysis.suggestion,
                })

        # 生成补充建议
        result["suggestions"] = self._generate_suggestions(result["missing_items"])

        return result

    def _check_clause_coverage(
        self,
        clause_info: Dict[str, Any],
        documents: List[Dict[str, Any]]
    ) -> ClauseAnalysis:
        """检查单个条款的覆盖情况"""
        clause_num = clause_info["clause"]
        clause_title = clause_info["title"]

        # 在文档中搜索条款号
        for doc in documents:
            content = doc.get("content", "") or ""
            title = doc.get("title", "")

            # 检查条款号是否在文档中
            if clause_num in content or clause_num in title:
                return ClauseAnalysis(
                    clause=clause_num,
                    title=clause_title,
                    status="covered",
                    document=title,
                    evidence=f"在《{title}》中找到条款{clause_num}",
                )

            # 检查条款标题关键词
            keywords = self._extract_keywords(clause_title)
            matched_keywords = [kw for kw in keywords if kw in content]
            if len(matched_keywords) >= len(keywords) * 0.5:
                return ClauseAnalysis(
                    clause=clause_num,
                    title=clause_title,
                    status="partial",
                    document=title,
                    evidence=f"在《{title}》中找到部分相关内容",
                    suggestion=f"建议在《{title}》中补充条款{clause_num}的具体要求",
                )

        # 未找到覆盖
        return ClauseAnalysis(
            clause=clause_num,
            title=clause_title,
            status="missing",
            suggestion=self._generate_missing_suggestion(clause_info),
        )

    def _extract_keywords(self, title: str) -> List[str]:
        """从条款标题提取关键词"""
        # 停用词
        stop_words = ["的", "和", "与", "及", "其", "总则", "策划", "控制"]

        keywords = []
        # 分词（简化处理）
        words = re.findall(r"[\u4e00-\u9fa5]{2,}", title)
        for word in words:
            if word not in stop_words and len(word) >= 2:
                keywords.append(word)

        return keywords

    def _generate_missing_suggestion(self, clause_info: Dict[str, Any]) -> str:
        """生成缺失项的补充建议"""
        clause_num = clause_info["clause"]
        clause_title = clause_info["title"]

        suggestions = {
            "4.1": "建议在管理手册中补充组织环境分析内容",
            "4.2": "建议在管理手册中补充相关方需求和期望分析",
            "6.1.2": "建议编制《环境因素识别与评价表》",
            "6.1.3": "建议编制《法律法规清单》",
            "8.2": "建议编制《应急准备和响应控制程序》",
        }

        return suggestions.get(
            clause_num,
            f"建议补充条款{clause_num}（{clause_title}）相关内容"
        )

    def _generate_suggestions(self, missing_items: List[Dict[str, Any]]) -> List[str]:
        """生成补充建议列表"""
        suggestions = []

        # 按文档类型分组
        missing_by_type = {
            "manual": [],
            "procedure": [],
            "record": [],
        }

        for item in missing_items:
            clause = item["clause"]
            if clause.startswith("4.") or clause.startswith("5.") or clause.startswith("6."):
                missing_by_type["manual"].append(item)
            elif clause.startswith("8."):
                missing_by_type["procedure"].append(item)
            else:
                missing_by_type["record"].append(item)

        if missing_by_type["manual"]:
            suggestions.append(
                f"建议在管理手册中补充{len(missing_by_type['manual'])}个条款的内容"
            )

        if missing_by_type["procedure"]:
            suggestions.append(
                f"建议补充{len(missing_by_type['procedure'])}份程序文件"
            )

        if missing_by_type["record"]:
            suggestions.append(
                f"建议补充{len(missing_by_type['record'])}份记录表格"
            )

        return suggestions

    def generate_missing_templates(
        self,
        missing_items: List[Dict[str, Any]],
        output_dir: str
    ) -> List[str]:
        """
        生成缺失项的空白模板

        Args:
            missing_items: 缺失项列表
            output_dir: 输出目录

        Returns:
            生成的模板文件列表
        """
        templates = []

        for item in missing_items:
            template_content = self._create_template(item)
            template_name = f"{item['clause']}_{item['title']}_模板.docx"
            template_path = f"{output_dir}/{template_name}"

            # 这里可以调用文档生成器创建实际文件
            templates.append(template_path)

        return templates

    def _create_template(self, item: Dict[str, Any]) -> str:
        """创建空白模板内容"""
        return f"""
# {item['clause']} {item['title']}

## 条款要求
（请根据标准要求填写）

## 实施情况
（请描述企业实际实施情况）

## 证据材料
- [ ] 相关记录
- [ ] 相关文件
- [ ] 其他证据

## 备注
（其他需要说明的内容）
"""


# 便捷函数
def analyze_coverage(
    documents: List[Dict[str, Any]],
    standards: List[str]
) -> Dict[str, Any]:
    """
    分析文档覆盖情况的便捷函数

    Args:
        documents: 已生成的文档列表
        standards: 目标标准列表

    Returns:
        分析报告
    """
    analyzer = MissingItemAnalyzer()
    return analyzer.analyze(documents, standards)
