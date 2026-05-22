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

### 2. 页面结构
```
frontend/src/pages/
├── home/                 # 首页
│   └── index.tsx
├── project/              # 项目管理
│   ├── create/           # 创建项目
│   ├── detail/           # 项目详情
│   └── documents/        # 文档管理
├── materials/            # 材料管理（V1.0）
└── upload/               # 文件上传
```

### 3. API接口封装 (`src/api/index.ts`)

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
  - `uploadMaterial()` - 上传材料
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

## 待实现前端页面

### V1.1 功能页面

#### 1. 多轮对话页面
**路径**: `/pages/conversation/index.tsx`

**功能需求**:
- 自然语言输入框（支持语音输入）
- 对话历史展示（气泡式聊天界面）
- 追问问题卡片展示
- 信息完整度进度条
- 完成对话按钮

**参考组件**:
```tsx
// 需要创建的组件
- ConversationChat.tsx      // 对话聊天界面
- FollowUpQuestionCard.tsx  // 追问问题卡片
- ProgressIndicator.tsx     // 进度指示器
```

**API调用流程**:
1. 用户输入初始文本 → `startConversation()`
2. 展示追问问题 → 用户回答 → `continueConversation()`
3. 循环直到 `status === 'complete'`
4. 点击完成 → `completeConversation()` → 跳转到项目详情

#### 2. 补充材料上传页面（增强版）
**路径**: `/pages/materials/upload/index.tsx`（现有页面需增强）

**新增功能**:
- 材料类型选择器（图标+文字）
- 拖拽上传区域
- 上传进度显示
- 材料信息提取结果展示
- 已上传材料列表

**材料类型图标映射**:
```
org_chart      → 组织架构图  → TeamOutlined
equipment_list → 设备清单    → ToolOutlined
process_flow   → 工艺流程图  → NodeIndexOutlined
site_layout    → 厂区平面图  → EnvironmentOutlined
license_cert   → 资质证书    → SafetyCertificateOutlined
previous_cert  → 历史认证    → FileProtectOutlined
other          → 其他材料    → FileOutlined
```

### V1.2 功能页面

#### 3. 环境评估报告解析页面
**路径**: `/pages/analyzer/environmental/index.tsx`

**功能需求**:
- 报告文本粘贴区域
- 解析按钮
- 环境因素列表展示
- 重要环境因素标记
- 合规率图表
- 生成的ISO14001文档预览

#### 4. 安全评估报告解析页面
**路径**: `/pages/analyzer/safety/index.tsx`

**功能需求**:
- 报告文本粘贴区域
- 解析按钮
- 危险源列表展示（风险等级颜色标识）
- 事故记录时间线
- 合规率图表
- 生成的ISO45001文档预览

### V1.3 功能页面

#### 5. 文档确认页面（增强版）
**路径**: `/pages/project/documents/index.tsx`（现有页面需增强）

**新增功能**:
- 文档树形结构展示
- 确认状态批量操作
- 确认进度统计
- 强制确认提示

#### 6. 个人中心页面
**路径**: `/pages/profile/index.tsx`

**功能需求**:
- 用户信息展示
- 修改密码
- 我的模板管理
- 使用统计

---

## 前端开发建议

### 1. 状态管理
建议使用以下方案之一：
- **Zustand** - 轻量级状态管理
- **React Query** - 服务端状态管理（推荐）

### 2. 路由结构建议
```tsx
// App.tsx 路由配置建议
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/project/create" element={<ProjectCreate />} />
  <Route path="/project/:id" element={<ProjectDetail />} />
  <Route path="/project/:id/documents" element={<ProjectDocuments />} />
  
  {/* V1.1 新增 */}
  <Route path="/conversation" element={<Conversation />} />
  <Route path="/conversation/:sessionId" element={<ConversationDetail />} />
  <Route path="/materials/upload" element={<MaterialsUpload />} />
  <Route path="/materials/list" element={<MaterialsList />} />
  
  {/* V1.2 新增 */}
  <Route path="/analyzer/environmental" element={<EnvironmentalAnalyzer />} />
  <Route path="/analyzer/safety" element={<SafetyAnalyzer />} />
  <Route path="/analyzer/coverage/:projectId" element={<CoverageAnalysis />} />
  
  {/* V1.3 新增 */}
  <Route path="/profile" element={<Profile />} />
  <Route path="/templates/my" element={<MyTemplates />} />
</Routes>
```

### 3. UI组件库使用

#### PC端
```tsx
import { Button, Card, Form, Input, Upload, Progress, Timeline } from 'antd';
```

#### 移动端
```tsx
import { Button, Card, Form, Input, Uploader, Progress, Steps } from 'antd-mobile';
```

### 4. 响应式断点
```css
/* 建议断点 */
@media (max-width: 768px) {
  /* 移动端样式 */
}

@media (min-width: 769px) {
  /* PC端样式 */
}
```

---

## API接口测试

所有API已封装在 `src/api/index.ts` 中，可直接使用：

```tsx
import { 
  startConversation, 
  uploadMaterial, 
  analyzeCoverage,
  analyzeEnvironmentalReport 
} from '@/api';

// 示例：开始多轮对话
const handleStartConversation = async (text: string) => {
  try {
    const response = await startConversation(text);
    console.log('会话ID:', response.sessionId);
    console.log('追问问题:', response.followUpQuestions);
  } catch (error) {
    console.error('对话开始失败:', error);
  }
};
```

---

## 下一步开发优先级

1. **高优先级** - 多轮对话页面（V1.1核心功能）
2. **高优先级** - 补充材料上传页面增强
3. **中优先级** - 环境/安全评估报告解析页面
4. **中优先级** - 文档确认页面增强
5. **低优先级** - 个人中心页面

---

## 相关文档

- [README.md](./README.md) - 项目整体说明
- [MVP1.0_BUGFIX_SUMMARY.md](./MVP1.0_BUGFIX_SUMMARY.md) - MVP1.0修复总结
- Backend API文档: http://localhost:8000/docs
