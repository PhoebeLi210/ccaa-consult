# 智质通·咨询版

> 面向ISO咨询顾问的AI智能文书工作站

## 产品定位

支持自然语言描述与文件上传双模态输入，一键生成全套体系文件，效率提升10倍。

## 核心功能

### 1. 自然语言解析
- 用户用口语描述企业情况，AI自动提取关键信息
- 支持多轮对话补充缺失信息
- 与文件上传信息融合

### 2. 项目管理
- 创建、查询、更新、删除项目
- 项目状态管理
- 企业信息管理

### 3. 文档生成
- 一键生成全套体系文件
- 支持ISO9001/14001/45001
- 模板+变量替换
- AI扩写描述性内容

### 4. 缺失项分析
- 基于ISO标准条款检查覆盖情况
- 输出缺失项报告
- 提供补充建议

## 技术栈

- **后端**: Python 3.11+, FastAPI, SQLAlchemy
- **前端**: React/Vue (待开发)
- **AI**: DeepSeek-V3 / OpenAI API
- **文档**: python-docx

## 项目结构

```
zhizhitong-consulting/
├── backend/
│   ├── app/
│   │   ├── api/              # API路由
│   │   │   └── v1/
│   │   ├── core/             # 核心配置
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/           # 数据模型
│   │   │   └── models.py
│   │   ├── modules/          # 业务模块
│   │   │   ├── parser/       # 自然语言解析器
│   │   │   ├── project/      # 项目管理
│   │   │   ├── generator/    # 文档生成器
│   │   │   ├── analyzer/     # 缺失项分析
│   │   │   └── editor/       # 在线编辑器
│   │   ├── schemas/          # Pydantic模型
│   │   └── main.py           # 入口文件
│   ├── templates/            # 文档模板
│   │   ├── iso9001/
│   │   ├── iso14001/
│   │   └── iso45001/
│   └── requirements.txt
├── frontend/                 # 前端代码
└── docs/                     # 文档
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，配置LLM API等
```

### 3. 初始化数据库

```bash
python -c "from app.core.database import init_db; init_db()"
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload
```

### 5. 访问API文档

打开浏览器访问: http://localhost:8000/docs

## API接口

### 项目管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/projects | 创建项目 |
| GET | /api/v1/projects | 列出项目 |
| GET | /api/v1/projects/{id} | 获取项目 |
| PATCH | /api/v1/projects/{id} | 更新项目 |
| DELETE | /api/v1/projects/{id} | 删除项目 |
| POST | /api/v1/projects/{id}/confirm | 确认项目 |

### 文档生成

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/documents/generate | 生成文档 |
| GET | /api/v1/documents | 列出文档 |
| GET | /api/v1/documents/{id} | 获取文档 |
| POST | /api/v1/documents/{id}/confirm | 确认文档 |

### 文件上传

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/uploads | 上传文件 |
| GET | /api/v1/uploads | 列出上传 |
| GET | /api/v1/uploads/{id} | 获取上传 |

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
from app.modules.generator.document_generator import generate_documents

company_info = {
    "company_name": "XX塑料制品有限公司",
    "industry": "制造业",
    "employee_count": 50,
    # ...
}

result = generate_documents(
    company_info=company_info,
    standards=["ISO9001", "ISO14001"]
)
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

## 开发计划

### V1.0 MVP (当前)
- [x] 自然语言输入+基础信息提取
- [x] 上传Excel收集表
- [x] 生成ISO9001全套文件（固定模板）
- [ ] 在线编辑+强制确认
- [ ] 批量导出Word

### V1.1
- [ ] 多轮对话追问缺失信息
- [ ] 补充材料上传（组织架构图、设备清单）
- [ ] 缺失项分析（条款覆盖检查）

### V1.2
- [ ] 支持ISO14001/45001
- [ ] 环境评估报告自动解析
- [ ] 流程图配置与作业指导书生成

### V1.3
- [ ] 行业模板库（6大行业）
- [ ] 个性化配置（封面、编号）
- [ ] 个人模板上传

## 许可证

MIT License
