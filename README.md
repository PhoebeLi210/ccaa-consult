# 智质通·咨询版

> 面向ISO咨询顾问的AI智能文书工作站

支持自然语言描述与文件上传双模态输入，一键生成全套体系文件，效率提升10倍。

---

## 产品定位

面向ISO体系咨询顾问，提供从企业信息收集到全套体系文件生成的一站式解决方案。

**核心价值**：
- 🚀 效率提升：传统方式需2-3天，智质通仅需30分钟
- 🎯 精准匹配：AI智能识别企业特征，匹配最合适的模板
- 📝 专业输出：基于ISO9001/14001/45001标准的专业文档
- 🔄 持续迭代：支持多轮对话补充信息，确保文档完整准确

---

## 核心功能

### 1. 自然语言解析（V1.0 ✅）
- 用户用口语描述企业情况，AI自动提取关键信息
- 支持多轮对话补充缺失信息
- 与文件上传信息融合

### 2. 多轮对话追问（V1.1 ✅）
- 智能识别缺失字段
- 自动生成追问问题
- 会话历史管理
- 信息完整度实时显示

### 3. 补充材料上传（V1.1 ✅）
- 组织架构图（自动提取部门设置）
- 设备清单（Excel自动解析）
- 工艺流程图
- 厂区平面图
- 资质证书（OCR识别）
- 历史认证证书

### 4. 项目管理（V1.0 ✅）
- 创建、查询、更新、删除项目
- 项目状态管理（草稿/进行中/已完成）
- 企业信息管理
- 文档确认状态追踪

### 5. 文档生成（V1.0 ✅）
- 一键生成全套体系文件
- 支持ISO9001/14001/45001
- 模板+变量替换
- AI扩写描述性内容
- 四级文件结构（手册/程序/指导书/记录）

### 6. 缺失项分析（V1.1 ✅）
- 基于ISO标准条款检查覆盖情况
- 输出缺失项报告
- 提供补充建议
- 快速覆盖率检查

### 7. 环境评估报告解析（V1.2 ✅）
- 自动提取环境因素
- 识别重要环境因素
- 合规性评价分析
- 生成ISO14001文档内容

### 8. 安全评估报告解析（V1.2 ✅）
- 自动提取危险源
- 识别重大危险源
- 事故记录分析
- 生成ISO45001文档内容

### 9. 防编造验证（V1.4 ✅）
- 质量方针/目标真实性验证
- 部门设置合理性检查
- 文件编号自动生成与校验
- 人员姓名真实性验证

### 10. 内容差异化生成（V1.4 ✅）
- 智能去重算法
- 同企业多文档差异化处理
- 同批次项目差异化生成
- 解决文档雷同问题

### 11. 专业代码查询（V1.4 ✅）
- 认证专业代码库集成
- 智能匹配企业所属专业
- 支持多专业组合查询
- 与认证范围联动

### 12. 认证范围选择（V1.4 ✅）
- 可视化认证范围勾选
- 支持多标准范围组合
- 智能范围推荐
- 范围变更历史追踪

### 13. 认证阶段确认（V1.4 ✅）
- 初次认证/监督审核1/监督审核2/再认证四种阶段
- 根据阶段自动判断文件生成范围
- AI智能建议认证阶段

### 14. 旧版文件提取（V1.4 ✅）
- 上传旧版体系文件自动提取信息
- 质量方针/目标自动提取
- 营业执照/租赁合同信息提取
- 文件智能分类到四级体系

---

## 技术栈

### 后端
- **Python**: 3.11+
- **FastAPI**: 高性能异步Web框架
- **SQLAlchemy**: ORM数据库操作
- **DeepSeek/OpenAI**: LLM大语言模型
- **python-docx**: Word文档生成
- **pandas**: Excel数据处理
- **ccaa-common**: 共享工具包（内部依赖，包含通用工具函数、模型定义等）

### 前端
- **React**: 18.3+
- **TypeScript**: 类型安全
- **Vite**: 构建工具
- **Ant Design**: PC端UI组件
- **Ant Design Mobile**: 移动端UI组件
- **Axios**: HTTP请求

---

## 项目结构

```
ccaa-consult/
├── backend/                          # 后端代码
│   ├── app/
│   │   ├── api/v1/                   # API路由层
│   │   │   ├── auth.py               # 认证相关
│   │   │   ├── projects.py           # 项目管理
│   │   │   ├── generator.py          # 文档生成
│   │   │   ├── parse.py              # 自然语言解析
│   │   │   ├── conversation.py       # 多轮对话（V1.1）
│   │   │   ├── materials.py          # 补充材料（V1.1）
│   │   │   ├── uploads.py            # 文件上传
│   │   │   ├── analyzer.py           # 缺失项分析
│   │   │   ├── templates.py          # 模板管理
│   │   │   └── company.py            # 企业信息
│   │   │
│   │   ├── core/                     # 核心配置
│   │   │   ├── config.py             # 全局配置
│   │   │   ├── database.py           # 数据库连接
│   │   │   └── security.py           # 安全相关
│   │   │
│   │   ├── models/                   # 数据模型
│   │   │   └── models.py             # SQLAlchemy模型
│   │   │
│   │   ├── modules/                  # 业务模块
│   │   │   ├── parser/               # 解析器模块
│   │   │   │   ├── natural_language_parser.py
│   │   │   │   └── excel_parser.py
│   │   │   │
│   │   │   ├── generator/            # 文档生成模块
│   │   │   │   ├── unified_generator.py
│   │   │   │   ├── docx_exporter.py
│   │   │   │   ├── llm_client.py
│   │   │   │   └── base.py
│   │   │   │
│   │   │   └── analyzer/             # 分析模块
│   │   │       ├── missing_item_analyzer.py
│   │   │       ├── environment_analyzer.py   # V1.2
│   │   │       └── safety_analyzer.py        # V1.2
│   │   │
│   │   ├── utils/                    # 工具函数
│   │   │   └── template_utils.py
│   │   │
│   │   └── main.py                   # 应用入口
│   │
│   ├── templates_industry/           # 行业模板库
│   │   ├── 一级文件/                 # 质量手册
│   │   ├── 二级文件/                 # 程序文件
│   │   ├── 三级文件/                 # 作业指导书
│   │   └── 四级文件/                 # 记录表单
│   │
│   ├── .env.example                  # 环境变量模板
│   └── requirements.txt              # 依赖列表
│
├── frontend/                         # 前端代码
│   ├── src/
│   │   ├── api/                      # API接口
│   │   │   └── index.ts
│   │   │
│   │   ├── components/               # 公共组件
│   │   │   ├── ConfirmBadge.tsx
│   │   │   ├── DocumentTree.tsx
│   │   │   ├── FileInfoCard.tsx
│   │   │   ├── NaturalLanguageInput.tsx
│   │   │   └── VoiceInput.tsx
│   │   │
│   │   ├── hooks/                    # 自定义Hooks
│   │   │   ├── useProject.ts
│   │   │   └── useResponsive.ts
│   │   │
│   │   ├── layouts/                  # 布局组件
│   │   │   ├── MobileLayout.tsx
│   │   │   └── PcLayout.tsx
│   │   │
│   │   ├── pages/                    # 页面
│   │   │   ├── home/                 # 首页
│   │   │   ├── project/              # 项目相关
│   │   │   │   ├── create/           # 创建项目
│   │   │   │   ├── detail/           # 项目详情
│   │   │   │   └── documents/        # 文档管理
│   │   │   ├── materials/            # 材料管理
│   │   │   └── upload/               # 文件上传
│   │   │
│   │   ├── styles/                   # 样式文件
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── MVP1.0_BUGFIX_SUMMARY.md          # MVP1.0修复总结
└── README.md                         # 本文件
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/PhoebeLi210/ccaa-consult.git
cd ccaa-consult
```

### 2. 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置LLM API密钥等

# 初始化数据库
python -c "from app.core.database import init_db; init_db()"

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问系统

- 前端页面: http://localhost:5173
- API文档: http://localhost:8000/docs
- API基础URL: http://localhost:8000/api/v1

---

## API接口

### 认证相关

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/register | 用户注册 |
| POST | /api/v1/auth/login | 用户登录 |
| POST | /api/v1/auth/logout | 用户登出 |

### 项目管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/projects | 创建项目 |
| GET | /api/v1/projects | 列出项目 |
| GET | /api/v1/projects/{id} | 获取项目详情 |
| PATCH | /api/v1/projects/{id} | 更新项目 |
| DELETE | /api/v1/projects/{id} | 删除项目 |
| GET | /api/v1/projects/{id}/confirmation-status | 确认状态查询 |

### 多轮对话（V1.1）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/conversation/start | 开始对话 |
| POST | /api/v1/conversation/continue | 继续对话 |
| GET | /api/v1/conversation/{id}/status | 会话状态 |
| POST | /api/v1/conversation/{id}/complete | 完成对话 |

### 补充材料（V1.1）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/materials/types | 材料类型列表 |
| POST | /api/v1/materials/upload | 上传材料 |
| GET | /api/v1/materials/project/{id} | 项目材料列表 |
| DELETE | /api/v1/materials/{id} | 删除材料 |

### 文档生成

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/generator/generate/all | 生成全部文档 |
| POST | /api/v1/generator/generate/batch | 批量生成 |
| POST | /api/v1/generator/export/zip | 导出ZIP |
| GET | /api/v1/generator/export/single/{id} | 导出单个文档 |

### 缺失项分析

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/analyzer/coverage/{id} | 条款覆盖分析 |
| POST | /api/v1/analyzer/coverage/quick | 快速覆盖检查 |
| POST | /api/v1/analyzer/environmental-report | 环境报告解析（V1.2） |
| POST | /api/v1/analyzer/safety-assessment | 安全报告解析（V1.2） |
| GET | /api/v1/analyzer/standards | 支持的标准列表 |

---

## 开发计划

### V1.0 MVP ✅ (已完成)
- [x] 自然语言输入+基础信息提取
- [x] 上传Excel收集表
- [x] 生成ISO9001全套文件（固定模板）
- [x] 在线编辑+强制确认
- [x] 批量导出Word

### V1.1 ✅ (已完成)
- [x] 多轮对话追问缺失信息
- [x] 补充材料上传（组织架构图、设备清单、工艺流程图等）
- [x] 缺失项分析（条款覆盖检查）
- [x] 项目确认状态追踪

### V1.2 ✅ (已完成)
- [x] 支持ISO14001/45001
- [x] 环境评估报告自动解析
- [x] 职业健康安全评估报告自动解析

### V1.3 ✅ (已完成)
- [x] 行业模板库（7大行业，145+模板）
- [x] 个性化配置（封面、编号）
- [x] 个人模板上传
- [x] 模板版本管理
- [x] 团队协作功能

### V1.4 ✅ (已完成)
- [x] 流程图配置与作业指导书生成
- [x] 防编造机制（质量方针/目标/部门/文件编号/人员姓名）
- [x] 内容差异化生成（解决雷同问题）
- [x] 专业代码查询集成
- [x] 认证范围勾选项
- [x] 企业信息字段补充（信用代码、地址）
- [x] 部门数据结构对齐
- [x] 文件层级命名对齐（管理制度）
- [x] 认证阶段确认（初审/监审1/监审2/再认证）
- [x] 旧版体系文件提取（方针/目标/编号/部门）
- [x] 文件智能分类器（40+文件类型）
- [x] 营业执照/租赁合同解析

### V1.5 (规划中)
- [ ] 逐级查资料原则集成（生成时引用上级文件编号）
- [ ] 客户管理CRM
- [ ] 数据统计分析
- [ ] 个人风格学习
- [ ] 移动端App

---

## 产品关系说明

### 与 audit 模块的关系

**智质通·咨询版**（本项目）与 **智质通·审核版**（audit 模块）是**背靠背独立产品**，分别服务于不同的用户群体：

| 产品 | 目标用户 | 核心功能 |
|------|----------|----------|
| 智质通·咨询版 | ISO咨询顾问 | 体系文件生成、企业信息管理 |
| 智质通·审核版 | 审核员/认证机构 | 审核计划、审核报告、不符合项管理 |

两者共享底层技术架构和 ccaa-common 共享包，但在业务逻辑和数据模型上保持独立，可根据实际需求分别部署或集成使用。

---

## 使用示例

### 自然语言输入

```python
from app.modules.parser.natural_language_parser import parse_company_info

text = """
我公司是一家生产塑料制品的制造企业，员工50人，办公室面积300平米，
有注塑机5台，电脑20台，去年通过ISO9001认证，今年要做监督审核。
主要产品为塑料包装盒，生产过程有注塑、修边、质检。
公司有独立的品质部和生产部。
"""

info = parse_company_info(text)
print(info.to_dict())
```

### 生成文档

```python
from app.modules.generator.unified_generator import UnifiedGenerator

generator = UnifiedGenerator(
    company_info={
        "company_name": "XX塑料制品有限公司",
        "industry": "制造业",
        "employee_count": 50,
    },
    target_standards=["ISO9001", "ISO14001"]
)

result = generator.generate_all()
```

### 缺失项分析

```python
from app.modules.analyzer.missing_item_analyzer import analyze_coverage

report = analyze_coverage(
    documents=generated_documents,
    standards=["ISO9001"]
)

print(f"覆盖率: {report['summary']['covered']}/{report['summary']['total_clauses']}")
```

---

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 许可证

[MIT License](LICENSE)

---

## 联系方式

- 项目主页: https://github.com/PhoebeLi210/ccaa-consult
- 问题反馈: https://github.com/PhoebeLi210/ccaa-consult/issues
