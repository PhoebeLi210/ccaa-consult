#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 文件分类器
根据文件名和内容关键词，将体系文件分类到对应的层级和类型。
不依赖audit模块，使用纯正则关键词匹配实现。
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum


class FileLevel(str, Enum):
    """文件层级"""
    LEVEL_1 = "一级文件"
    LEVEL_2 = "二级文件"
    LEVEL_3 = "三级文件"
    LEVEL_4 = "四级文件"
    OTHER = "其他"


@dataclass
class FileClassification:
    """文件分类结果"""
    file_name: str = ""
    file_level: FileLevel = FileLevel.OTHER
    file_type: str = ""           # 具体文件类型名称
    confidence: float = 0.0       # 置信度 0~1
    matched_keywords: List[str] = field(default_factory=list)
    sub_type: str = ""            # 二级分类（如"质量程序"/"环境程序"）


class FileClassifier:
    """
    文件分类器。

    分类规则：
    - 一级文件：管理手册、质量手册、环境手册、安全手册
    - 二级文件：程序文件（含"程序"关键词）
    - 三级文件：管理制度、作业指导书、操作规程（含"制度"/"指导书"/"规程"关键词）
    - 四级文件：记录表格、表单（含"记录"/"表格"/"表单"关键词）
    - 其他：营业执照、申请书、审核计划、合同等
    """

    # ==================== 一级文件规则 ====================
    LEVEL_1_RULES: List[Dict[str, Any]] = [
        {
            "file_type": "质量管理手册",
            "sub_type": "质量",
            "keywords": ["质量手册", "质量管理手册"],
            "name_patterns": [r"质量.{0,4}手册"],
        },
        {
            "file_type": "环境管理手册",
            "sub_type": "环境",
            "keywords": ["环境手册", "环境管理手册", "EMS手册"],
            "name_patterns": [r"环境.{0,4}手册"],
        },
        {
            "file_type": "职业健康安全管理手册",
            "sub_type": "安全",
            "keywords": ["安全手册", "职业健康安全管理手册", "OHSAS手册", "OHS手册"],
            "name_patterns": [r"(?:职业健康)?安全.{0,4}手册"],
        },
        {
            "file_type": "综合管理手册",
            "sub_type": "综合",
            "keywords": ["综合管理手册", "一体化手册", "三标一体手册", "管理手册"],
            "name_patterns": [r"综合.{0,4}手册", r"一体化.{0,4}手册", r"三标一体.{0,4}手册"],
        },
    ]

    # ==================== 二级文件规则（程序文件）====================
    LEVEL_2_RULES: List[Dict[str, Any]] = [
        # 通用程序
        {"file_type": "文件控制程序", "sub_type": "通用", "keywords": ["文件控制程序", "文件和资料控制程序"]},
        {"file_type": "记录控制程序", "sub_type": "通用", "keywords": ["记录控制程序"]},
        {"file_type": "内部审核程序", "sub_type": "通用", "keywords": ["内部审核程序", "内部审核控制程序", "内审程序"]},
        {"file_type": "管理评审程序", "sub_type": "通用", "keywords": ["管理评审程序"]},
        {"file_type": "纠正措施程序", "sub_type": "通用", "keywords": ["纠正措施程序", "纠正和预防措施程序"]},
        {"file_type": "预防措施程序", "sub_type": "通用", "keywords": ["预防措施程序"]},
        {"file_type": "培训控制程序", "sub_type": "通用", "keywords": ["培训控制程序", "人力资源管理程序", "培训管理程序"]},
        {"file_type": "沟通与协商程序", "sub_type": "通用", "keywords": ["沟通", "信息交流程序", "协商程序"]},

        # 质量程序
        {"file_type": "合同评审程序", "sub_type": "质量", "keywords": ["合同评审程序", "合同评审控制程序"]},
        {"file_type": "设计和开发控制程序", "sub_type": "质量", "keywords": ["设计和开发", "设计控制程序", "开发控制程序"]},
        {"file_type": "采购控制程序", "sub_type": "质量", "keywords": ["采购控制程序", "采购管理程序"]},
        {"file_type": "生产和服务提供控制程序", "sub_type": "质量", "keywords": ["生产和服务提供", "生产控制程序", "服务提供控制程序"]},
        {"file_type": "产品检验程序", "sub_type": "质量", "keywords": ["产品检验", "检验和试验程序", "检验控制程序", "监视和测量程序"]},
        {"file_type": "不合格品控制程序", "sub_type": "质量", "keywords": ["不合格品控制", "不合格控制程序"]},
        {"file_type": "顾客满意度测量程序", "sub_type": "质量", "keywords": ["顾客满意度", "客户满意度", "满意度调查程序"]},
        {"file_type": "标识和可追溯性程序", "sub_type": "质量", "keywords": ["标识和可追溯性", "产品标识程序"]},
        {"file_type": "顾客财产控制程序", "sub_type": "质量", "keywords": ["顾客财产", "客户财产"]},
        {"file_type": "过程确认程序", "sub_type": "质量", "keywords": ["过程确认", "特殊过程确认"]},

        # 环境程序
        {"file_type": "环境因素识别程序", "sub_type": "环境", "keywords": ["环境因素识别", "环境因素评价"]},
        {"file_type": "法律法规获取程序", "sub_type": "环境", "keywords": ["法律法规获取", "法律法规识别", "合规性评价"]},
        {"file_type": "能源资源管理程序", "sub_type": "环境", "keywords": ["能源管理", "资源管理程序", "节水节电"]},
        {"file_type": "废弃物管理程序", "sub_type": "环境", "keywords": ["废弃物管理", "废物处理程序", "固体废物"]},
        {"file_type": "污染防治程序", "sub_type": "环境", "keywords": ["污染防治", "水污染防治", "大气污染防治"]},
        {"file_type": "相关方管理程序", "sub_type": "环境", "keywords": ["相关方管理", "供方环境管理"]},

        # 安全程序
        {"file_type": "危险源辨识程序", "sub_type": "安全", "keywords": ["危险源辨识", "风险评价程序", "危险源识别"]},
        {"file_type": "事件调查程序", "sub_type": "安全", "keywords": ["事件调查", "事故调查", "事故处理程序", "事故报告程序"]},
        {"file_type": "应急准备和响应程序", "sub_type": "安全", "keywords": ["应急准备", "应急响应", "应急预案管理"]},
        {"file_type": "职业健康管理程序", "sub_type": "安全", "keywords": ["职业健康管理", "职业病防治"]},
        {"file_type": "个人防护用品管理程序", "sub_type": "安全", "keywords": ["个人防护用品", "劳保用品管理", "PPE管理"]},
        {"file_type": "安全检查程序", "sub_type": "安全", "keywords": ["安全检查程序", "隐患排查程序"]},
    ]

    # ==================== 三级文件规则 ====================
    LEVEL_3_RULES: List[Dict[str, Any]] = [
        # 管理制度
        {"file_type": "质量管理制度", "sub_type": "质量制度", "keywords": ["质量管理制度", "质量管理办法"]},
        {"file_type": "环境管理制度", "sub_type": "环境制度", "keywords": ["环境管理制度", "环境管理办法"]},
        {"file_type": "安全管理制度", "sub_type": "安全制度", "keywords": ["安全管理制度", "安全管理办法", "安全生产制度"]},
        {"file_type": "行政管理制度", "sub_type": "行政制度", "keywords": ["行政管理制度", "人事管理制度", "考勤制度", "薪酬制度"]},
        {"file_type": "财务管理制度", "sub_type": "财务制度", "keywords": ["财务管理制度", "财务管理办法"]},
        {"file_type": "设备管理制度", "sub_type": "设备制度", "keywords": ["设备管理制度", "设备管理办法", "设施管理制度"]},
        {"file_type": "库房管理制度", "sub_type": "库房制度", "keywords": ["库房管理制度", "仓库管理制度", "仓储管理制度"]},

        # 作业指导书
        {"file_type": "作业指导书", "sub_type": "作业指导", "keywords": ["作业指导书", "操作指导书", "工作指导书"]},
        {"file_type": "检验作业指导书", "sub_type": "检验指导", "keywords": ["检验作业指导书", "检验指导书", "检验规范"]},
        {"file_type": "设备操作规程", "sub_type": "设备操作", "keywords": ["设备操作规程", "设备操作规范", "设备使用规程"]},
        {"file_type": "安全操作规程", "sub_type": "安全操作", "keywords": ["安全操作规程", "安全操作规范"]},

        # 岗位职责
        {"file_type": "岗位职责", "sub_type": "岗位职责", "keywords": ["岗位职责", "岗位说明书", "岗位规范", "职务说明书"]},

        # 其他三级文件
        {"file_type": "服务规范", "sub_type": "服务规范", "keywords": ["服务规范", "服务标准", "服务准则"]},
        {"file_type": "技术标准", "sub_type": "技术标准", "keywords": ["技术标准", "技术规范", "工艺规程", "工艺标准"]},
        {"file_type": "检验标准", "sub_type": "检验标准", "keywords": ["检验标准", "验收标准", "质量标准"]},
        {"file_type": "管理制度", "sub_type": "通用制度", "keywords": ["管理制度", "管理办法", "管理规定", "管理细则"]},
    ]

    # ==================== 四级文件规则 ====================
    LEVEL_4_RULES: List[Dict[str, Any]] = [
        {"file_type": "培训记录表", "sub_type": "培训记录", "keywords": ["培训记录", "培训签到表", "培训考核记录"]},
        {"file_type": "检验记录表", "sub_type": "检验记录", "keywords": ["检验记录", "检验报告", "检验表"]},
        {"file_type": "内审检查表", "sub_type": "内审记录", "keywords": ["内审检查表", "内审记录", "审核检查表"]},
        {"file_type": "纠正措施单", "sub_type": "纠正记录", "keywords": ["纠正措施单", "纠正措施报告", "不合格品处理单"]},
        {"file_type": "管理评审记录", "sub_type": "评审记录", "keywords": ["管理评审记录", "管理评审报告"]},
        {"file_type": "合同评审记录", "sub_type": "合同记录", "keywords": ["合同评审记录", "合同评审表"]},
        {"file_type": "采购记录表", "sub_type": "采购记录", "keywords": ["采购记录", "采购验收单", "供方评价表"]},
        {"file_type": "顾客满意度调查表", "sub_type": "满意度记录", "keywords": ["满意度调查", "客户满意度", "顾客满意度"]},
        {"file_type": "设备维护保养记录", "sub_type": "设备记录", "keywords": ["设备维护", "设备保养", "设备维修记录"]},
        {"file_type": "危险源辨识记录", "sub_type": "安全记录", "keywords": ["危险源辨识", "风险评价记录"]},
        {"file_type": "环境因素识别记录", "sub_type": "环境记录", "keywords": ["环境因素识别", "环境因素评价记录"]},
        {"file_type": "法律法规合规性评价记录", "sub_type": "合规记录", "keywords": ["合规性评价", "法律法规评价"]},
        {"file_type": "应急预案演练记录", "sub_type": "应急记录", "keywords": ["应急演练", "应急预案演练"]},
        {"file_type": "事故调查记录", "sub_type": "事故记录", "keywords": ["事故调查", "事故报告", "事件报告"]},
        {"file_type": "文件发放记录", "sub_type": "文件记录", "keywords": ["文件发放", "文件回收", "文件清单"]},
        {"file_type": "记录表格", "sub_type": "通用记录", "keywords": ["记录表", "记录单", "记录表格", "表单"]},
    ]

    # ==================== 其他文件规则 ====================
    OTHER_RULES: List[Dict[str, Any]] = [
        {"file_type": "营业执照", "sub_type": "资质", "keywords": ["营业执照"]},
        {"file_type": "认证申请书", "sub_type": "认证", "keywords": ["认证申请", "申请书", "认证合同"]},
        {"file_type": "审核计划", "sub_type": "审核", "keywords": ["审核计划", "审核方案", "审核日程"]},
        {"file_type": "审核报告", "sub_type": "审核", "keywords": ["审核报告", "审核总结", "不符合报告"]},
        {"file_type": "租赁合同", "sub_type": "合同", "keywords": ["租赁合同", "租房合同", "房屋租赁"]},
        {"file_type": "组织架构图", "sub_type": "组织", "keywords": ["组织架构", "组织机构", "组织结构图"]},
        {"file_type": "工艺流程图", "sub_type": "流程", "keywords": ["工艺流程", "流程图", "业务流程"]},
        {"file_type": "法律法规清单", "sub_type": "法规", "keywords": ["法律法规清单", "法规清单", "适用法律法规"]},
        {"file_type": "目标指标方案", "sub_type": "目标", "keywords": ["目标指标", "管理目标", "目标方案"]},
        {"file_type": "管理方案", "sub_type": "方案", "keywords": ["管理方案", "实施方案", "工作方案"]},
        {"file_type": "岗位任职要求", "sub_type": "人事", "keywords": ["任职要求", "岗位资格", "能力要求"]},
        {"file_type": "供方名录", "sub_type": "采购", "keywords": ["供方名录", "合格供方", "供应商名录"]},
        {"file_type": "设备清单", "sub_type": "设备", "keywords": ["设备清单", "设备台账", "设备一览表"]},
        {"file_type": "监测设备清单", "sub_type": "监测", "keywords": ["监测设备", "测量设备", "监视测量设备"]},
        {"file_type": "年度内审计划", "sub_type": "内审", "keywords": ["年度内审", "内审计划", "年度审核计划"]},
        {"file_type": "管理评审计划", "sub_type": "评审", "keywords": ["管理评审计划", "评审计划"]},
        {"file_type": "员工花名册", "sub_type": "人事", "keywords": ["花名册", "员工名册", "人员名单"]},
        {"file_type": "特种作业人员清单", "sub_type": "人事", "keywords": ["特种作业", "特种设备", "持证人员"]},
        {"file_type": "危险废弃物清单", "sub_type": "环境", "keywords": ["危险废弃物", "危废清单", "废弃物清单"]},
        {"file_type": "能源消耗记录", "sub_type": "能源", "keywords": ["能源消耗", "水电费", "能耗记录"]},
    ]

    # ==================== 通用关键词兜底 ====================
    LEVEL_KEYWORDS = {
        FileLevel.LEVEL_1: ["手册"],
        FileLevel.LEVEL_2: ["程序"],
        FileLevel.LEVEL_3: ["制度", "指导书", "规程", "规范", "标准", "办法", "细则"],
        FileLevel.LEVEL_4: ["记录", "表格", "表单", "清单", "台账", "日志", "签到"],
    }

    def classify_file(
        self,
        file_name: str,
        content: str = "",
    ) -> FileClassification:
        """
        根据文件名和内容分类文件类型。

        Args:
            file_name: 文件名（含扩展名）
            content: 文件内容文本（可选，用于辅助分类）

        Returns:
            FileClassification 分类结果
        """
        name_lower = file_name.lower()
        name_no_ext = Path(file_name).stem
        # 合并文件名和内容用于匹配
        combined = f"{name_no_ext}\n{content}" if content else name_no_ext

        # 按层级依次匹配
        # 1. 一级文件
        result = self._match_rules(combined, name_no_ext, self.LEVEL_1_RULES, FileLevel.LEVEL_1)
        if result:
            return result

        # 2. 二级文件
        result = self._match_rules(combined, name_no_ext, self.LEVEL_2_RULES, FileLevel.LEVEL_2)
        if result:
            return result

        # 3. 三级文件
        result = self._match_rules(combined, name_no_ext, self.LEVEL_3_RULES, FileLevel.LEVEL_3)
        if result:
            return result

        # 4. 四级文件
        result = self._match_rules(combined, name_no_ext, self.LEVEL_4_RULES, FileLevel.LEVEL_4)
        if result:
            return result

        # 5. 其他类型
        result = self._match_rules(combined, name_no_ext, self.OTHER_RULES, FileLevel.OTHER)
        if result:
            return result

        # 6. 兜底：按关键词匹配层级
        result = self._fallback_classify(name_no_ext, combined)
        if result:
            return result

        # 7. 完全无法分类
        return FileClassification(
            file_name=file_name,
            file_level=FileLevel.OTHER,
            file_type="未分类文件",
            confidence=0.0,
        )

    def classify_batch(self, files: List[Dict[str, str]]) -> List[FileClassification]:
        """
        批量分类文件。

        Args:
            files: 文件列表，每个元素为 {"file_name": str, "content": str}
                   content 可选

        Returns:
            FileClassification 列表
        """
        results = []
        for f in files:
            file_name = f.get("file_name", "")
            content = f.get("content", "")
            results.append(self.classify_file(file_name, content))
        return results

    # ==================== 内部方法 ====================

    def _match_rules(
        self,
        combined: str,
        name_no_ext: str,
        rules: List[Dict[str, Any]],
        level: FileLevel,
    ) -> Optional[FileClassification]:
        """尝试用一组规则匹配，返回第一个匹配结果"""
        for rule in rules:
            matched_keywords = []
            score = 0.0

            # 关键词匹配
            for kw in rule.get("keywords", []):
                if kw in combined:
                    matched_keywords.append(kw)
                    # 文件名中匹配权重更高
                    if kw in name_no_ext:
                        score += 0.4
                    else:
                        score += 0.2

            # 正则模式匹配（仅匹配文件名）
            for pattern in rule.get("name_patterns", []):
                try:
                    if re.search(pattern, name_no_ext):
                        matched_keywords.append(f"regex:{pattern}")
                        score += 0.3
                except re.error:
                    continue

            if matched_keywords:
                # 置信度：限制在 0.5~1.0 之间
                confidence = min(1.0, max(0.5, score))
                return FileClassification(
                    file_name=name_no_ext,
                    file_level=level,
                    file_type=rule["file_type"],
                    confidence=confidence,
                    matched_keywords=matched_keywords,
                    sub_type=rule.get("sub_type", ""),
                )

        return None

    def _fallback_classify(self, name_no_ext: str, combined: str) -> Optional[FileClassification]:
        """兜底分类：按通用关键词匹配层级"""
        for level, keywords in self.LEVEL_KEYWORDS.items():
            for kw in keywords:
                if kw in name_no_ext:
                    return FileClassification(
                        file_name=name_no_ext,
                        file_level=level,
                        file_type=f"{name_no_ext}",
                        confidence=0.3,
                        matched_keywords=[kw],
                        sub_type="",
                    )
        return None


# ==================== 便捷函数 ====================

def classify_file(file_name: str, content: str = "") -> FileClassification:
    """便捷函数：分类单个文件"""
    return FileClassifier().classify_file(file_name, content)


def classify_batch(files: List[Dict[str, str]]) -> List[FileClassification]:
    """便捷函数：批量分类文件"""
    return FileClassifier().classify_batch(files)
