# 智质通·咨询版 - MVP 1.0 Bug修复总结

> 修复日期：2026-05-21
> 修复范围：后端核心模块、模板系统、数据库集成、API端点

---

## 一、P0 级修复（3项，系统级阻断问题）

### P0-1：projects.py 文档更新端点 NameError
- **文件**：`app/api/v1/projects.py`
- **问题**：第332行使用 `content` 变量而非 `request.content`，导致文档保存时抛出 `NameError`
- **修复**：`content` → `request.content`

### P0-2：模板格式不统一（document_info 与 metadata 不兼容）
- **文件**：`app/utils/template_utils.py`、`app/modules/generator/unified_generator.py`
- **问题**：100+ 个模板使用 `document_info` 格式，但 `get_template_metadata()` 只读取 `metadata` 键，导致元数据提取返回空值
- **修复**：`get_template_metadata()` 和 `generate_from_template()` 添加 `document_info` 格式回退逻辑

### P0-3：生成器与数据库完全断裂
- **文件**：`app/api/v1/generator.py`
- **问题**：`/generate/all` 端点将生成结果存储在内存中，从未写入数据库 `documents` 表
- **修复**：
  - 生成端点添加 `project_id` 参数和数据库写入逻辑
  - `/export/zip` 改为从数据库读取已编辑/确认的文档
  - 新增 `/export/single/{document_id}` 单文档导出端点

---

## 二、P1 级修复（4项，功能缺陷）

### P1-1：一级文件模板变量名中英文不匹配
- **文件**：`app/utils/template_utils.py`
- **修复**：添加 31 个英文→中文变量名映射表

### P1-2：物业模板缺少 industry 标记
- **文件**：116 个 XCYWY 前缀的 YAML 模板
- **修复**：批量添加 `industry: property_service`

### P1-3：导出不检查文档确认状态
- **文件**：`app/api/v1/generator.py`、`app/api/v1/projects.py`
- **修复**：添加强制确认检查 + 确认进度查询端点

### P1-4：AI 扩写在异步上下文中崩溃
- **文件**：`app/modules/generator/unified_generator.py`
- **修复**：改用 `httpx` 同步 HTTP 客户端调用 DeepSeek API

---

## 三、P2 级修复（2项，代码质量）

### P2-1：Excel 解析结果存储格式不可靠
- **文件**：`app/api/v1/uploads.py`
- **修复**：`str()/ast.literal_eval()` → `json.dumps()/json.loads()`

### P2-2：两个自然语言解析器行业代码映射不一致
- **文件**：`app/modules/parser/natural_language_parser.py`
- **修复**：统一为与 `parse.py` 一致的英文行业代码映射

---

## 四、新增功能

| 功能 | API 端点 | 说明 |
|------|---------|------|
| 单文档导出 | `GET /generator/export/single/{document_id}` | 从数据库导出 .docx |
| 确认进度查询 | `GET /projects/{project_id}/confirmation-status` | 文档确认进度统计 |
| 强制导出 | `POST /generator/export/zip` (force_export=true) | 跳过确认检查 |

---

## 五、修改文件清单

| 文件路径 | 修改类型 |
|---------|---------|
| `backend/app/api/v1/generator.py` | 重构 |
| `backend/app/api/v1/projects.py` | 修改 |
| `backend/app/api/v1/uploads.py` | 修改 |
| `backend/app/modules/generator/unified_generator.py` | 修改 |
| `backend/app/utils/template_utils.py` | 修改 |
| `backend/app/modules/parser/natural_language_parser.py` | 修改 |
| `backend/templates_industry/**/XCYWY*.yaml` (116个) | 批量修改 |