# 智质通·咨询版 - 前端功能说明

本文档说明前端已实现和待实现的功能。

---

## 已实现功能

### 1. 基础架构
- ✅ React 18 + TypeScript
- ✅ Vite 构建工具
- ✅ Ant Design (PC端) + Ant Design Mobile (移动端)
- ✅ Axios HTTP请求封装
- ✅ 响应式布局（PC/移动端双布局）
- ✅ CSS Modules 样式管理

### 2. 页面结构
```
frontend/src/pages/
├── home/                 # 首页
│   └── index.tsx
├── project/              # 项目管理
│   ├── create/           # 创建项目
│   ├── detail/           # 项目详情
│   └── documents/        # 文档管理
├── materials/            # 材料管理
│   ├── index.tsx         # 材料清单页面 (V1.0)
│   └── upload.tsx        # 补充材料上传 (V1.1) ✅
├── conversation/         # 多轮对话 (V1.1) ✅
│   ├── index.tsx
│   └── style.module.css
├── analyzer/             # 评估报告解析 (V1.2) ✅
│   ├── index.tsx
│   └── style.module.css
└── upload/               # 文件上传
    └── index.tsx
```

### 3. 新增页面功能详情

#### 3.1 多轮对话页面 (`/conversation`)

**访问路径**: `/conversation?projectId=xxx`

**功能特性**:
- 💬 自然语言输入框（支持多行文本）
- 🔄 对话历史展示（气泡式聊天界面）
- ❓ 追问问题卡片展示（带示例回答）
- 📊 信息收集进度条（实时显示百分比）
- 🏷️ 缺失字段标签展示
- ✨ 快速使用示例回答功能
- ✅ 完成对话并保存到项目

**使用流程**:
1. 用户输入初始企业描述
2. AI识别缺失字段，生成追问问题
3. 用户回答追问，进度实时更新
4. 信息收集完成后，点击"完成并保存"

**响应式设计**:
- PC端：左右分栏布局，消息最大宽度70%
- 移动端：全屏布局，消息最大宽度85%

#### 3.2 补充材料上传页面 (`/materials/upload`)

**访问路径**: `/materials/upload?projectId=xxx`

**功能特性**:
- 📁 材料类型选择器（7种类型，带图标）
- 🖱️ 拖拽上传区域（支持点击上传）
- 📋 材料类型说明和格式限制提示
- 📈 上传进度实时显示
- 📄 已上传材料列表（带图标、大小、状态）
- 🔄 重新处理功能
- 🗑️ 删除功能（带确认弹窗）

**支持的材料类型**:
| 类型 | 图标 | 说明 |
|------|------|------|
| org_chart | TeamOutlined | 组织架构图 |
| equipment_list | ToolOutlined | 设备清单 |
| process_flow | NodeIndexOutlined | 工艺流程图 |
| site_layout | EnvironmentOutlined | 厂区平面图 |
| license_cert | SafetyCertificateOutlined | 资质证书 |
| previous_cert | FileProtectOutlined | 历史认证证书 |
| other | FileOutlined | 其他材料 |

#### 3.3 评估报告解析页面 (`/analyzer`)

**访问路径**: `/analyzer`

**功能特性**:
- 🌍 环境评估报告解析（ISO14001）
- 🛡️ 职业健康安全评估解析（ISO45001）
- 📝 报告文本粘贴区域
- 📊 解析结果统计卡片
- 📋 环境因素/危险源列表
- 📄 生成的体系文件展示
- ✅ 合规率可视化展示

**解析结果展示**:
- 统计概览（总数、重要项、合规率）
- 详细列表（带风险等级标签）
- 生成的文档清单

### 4. API接口封装 (`src/api/index.ts`)

#### V1.0 基础功能
- ✅ 项目管理（CRUD）
- ✅ 文档生成与确认
- ✅ 文件上传
- ✅ 行业材料清单

#### V1.1 新增功能
- ✅ **多轮对话API**
  - `startConversation()` - 开始对话
  - `continueConversation()` - 继续对话
  - `getConversationStatus()` - 获取会话状态
  - `completeConversation()` - 完成对话

- ✅ **补充材料API**
  - `getMaterialTypes()` - 获取材料类型
  - `uploadMaterial()` - 上传材料（带进度回调）
  - `getProjectMaterials()` - 获取项目材料
  - `deleteMaterial()` - 删除材料
  - `reprocessMaterial()` - 重新处理

- ✅ **缺失项分析API**
  - `analyzeCoverage()` - 条款覆盖分析
  - `quickCoverageCheck()` - 快速检查
  - `getSupportedStandards()` - 支持的标准

#### V1.2 新增功能
- ✅ **环境/安全评估报告解析API**
  - `analyzeEnvironmentalReport()` - 环境报告解析
  - `analyzeSafetyAssessment()` - 安全报告解析

---

## 页面路由汇总

| 路径 | 页面 | 功能版本 |
|------|------|---------|
| `/` | 首页 | V1.0 |
| `/project/create` | 创建项目 | V1.0 |
| `/project/:id` | 项目详情 | V1.0 |
| `/project/:id/documents` | 文档管理 | V1.0 |
| `/upload` | 文件上传 | V1.0 |
| `/materials` | 材料清单 | V1.0 |
| `/materials/upload` | 补充材料上传 | V1.1 ✅ |
| `/conversation` | 多轮对话 | V1.1 ✅ |
| `/analyzer` | 评估报告解析 | V1.2 ✅ |

---

## 前端开发规范

### 1. 组件结构
```tsx
// 页面组件基本结构
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button } from 'antd';
import { useResponsive } from '../../hooks/useResponsive';
import { apiFunction } from '../../api';
import styles from './style.module.css';

const PageName: React.FC = () => {
  const navigate = useNavigate();
  const { isMobile } = useResponsive();
  
  // 状态管理
  const [loading, setLoading] = useState(false);
  
  // 方法定义
  const handleAction = async () => {
    // ...
  };
  
  // 渲染
  return (
    <div className={styles.container}>
      {/* 页面内容 */}
    </div>
  );
};

export default PageName;
```

### 2. 样式规范
- 使用 CSS Modules (`style.module.css`)
- 类名使用驼峰命名法
- 响应式断点：`768px`
- 颜色使用 Ant Design 变量

### 3. 响应式设计
```css
/* PC端默认样式 */
.container {
  padding: 24px;
  max-width: 1200px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .container {
    padding: 12px;
  }
}
```

---

## 下一步开发建议

### 高优先级
1. **文档确认页面增强** (`/project/:id/documents`)
   - 添加确认状态批量操作
   - 确认进度可视化
   - 文档对比功能

2. **首页项目列表增强**
   - 添加项目状态筛选
   - 项目搜索功能
   - 项目卡片信息展示优化

### 中优先级
3. **个人中心页面** (`/profile`)
   - 用户信息展示
   - 修改密码
   - 使用统计

4. **缺失项分析结果页面** (`/analyzer/coverage/:projectId`)
   - 条款覆盖可视化
   - 缺失项详细报告
   - 补充建议展示

### 低优先级
5. **模板管理页面** (`/templates`)
   - 个人模板上传
   - 模板预览
   - 模板版本管理

---

## API接口测试

所有API已封装在 `src/api/index.ts` 中，可直接使用：

```tsx
import { 
  startConversation, 
  uploadMaterial, 
  analyzeEnvironmentalReport 
} from '@/api';

// 示例：开始多轮对话
const handleStart = async (text: string) => {
  try {
    const response = await startConversation(text);
    console.log('会话ID:', response.sessionId);
    console.log('追问问题:', response.followUpQuestions);
  } catch (error) {
    console.error('对话开始失败:', error);
  }
};

// 示例：上传材料
const handleUpload = async (file: File) => {
  try {
    const response = await uploadMaterial(
      projectId,
      'org_chart',
      file,
      (progress) => console.log(`上传进度: ${progress}%`)
    );
    console.log('上传成功:', response.materialId);
  } catch (error) {
    console.error('上传失败:', error);
  }
};
```

---

## 相关文档

- [README.md](./README.md) - 项目整体说明
- [MVP1.0_BUGFIX_SUMMARY.md](./MVP1.0_BUGFIX_SUMMARY.md) - MVP1.0修复总结
- Backend API文档: http://localhost:8000/docs

---

## 更新日志

### 2024-05-22
- ✅ 新增多轮对话页面 (`/conversation`)
- ✅ 新增补充材料上传页面 (`/materials/upload`)
- ✅ 新增评估报告解析页面 (`/analyzer`)
- ✅ 更新 API 接口封装（新增 V1.1/V1.2 API）
- ✅ 更新路由配置
- ✅ 更新本文档
