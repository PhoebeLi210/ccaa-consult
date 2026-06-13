import axios, { AxiosInstance, AxiosResponse } from 'axios';

/** 后端API基础URL */
const BASE_URL = '/api';

/** 创建axios实例 */
const request: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/** 请求拦截器 - 可在此添加token等认证信息 */
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

/** 响应拦截器 - 统一处理错误 */
request.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data;
  },
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '网络异常，请稍后重试';
    return Promise.reject(new Error(message));
  },
);

/* ==================== 项目相关API ==================== */

/** 项目信息类型 */
export interface ProjectInfo {
  id: string;
  name: string;
  companyName: string;
  industry: string;
  employeeCount: string;
  registeredCapital: string;
  address: string;
  contactPerson: string;
  contactPhone: string;
  status: 'draft' | 'in_progress' | 'completed';
  createdAt: string;
  updatedAt: string;
}

/** AI解析结果类型 */
export interface ParseResult {
  companyName: string;
  industry: string;
  employeeCount: string;
  registeredCapital: string;
  address: string;
  contactPerson: string;
  contactPhone: string;
  businessScope: string;
  missingFields: string[];
}

/** 文档信息类型 */
export interface DocumentInfo {
  id: string;
  projectId: string;
  name: string;
  type: string;
  status: 'confirmed' | 'pending' | 'draft';
  url: string;
  createdAt: string;
  updatedAt: string;
}

/** 上传文件信息类型 */
export interface UploadFileInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  status: 'uploading' | 'success' | 'error';
  progress: number;
}

/** 获取项目列表 */
export function getProjectList(params?: {
  page?: number;
  pageSize?: number;
  keyword?: string;
}) {
  return request.get<unknown, ProjectInfo[]>('/v1/projects', { params });
}

/** 获取项目详情 */
export function getProjectDetail(id: string) {
  return request.get<unknown, ProjectInfo>(`/v1/projects/${id}`);
}

/** 创建项目 */
export function createProject(data: Partial<ProjectInfo>) {
  return request.post<unknown, ProjectInfo>('/v1/projects', data);
}

/** 更新项目 */
export function updateProject(id: string, data: Partial<ProjectInfo>) {
  return request.put<unknown, ProjectInfo>(`/v1/projects/${id}`, data);
}

/** 删除项目 */
export function deleteProject(id: string) {
  return request.delete<unknown, void>(`/v1/projects/${id}`);
}

/** AI自然语言解析 */
export function parseNaturalLanguage(text: string) {
  return request.post<unknown, ParseResult>('/v1/parse', { text });
}

/** 获取项目文档列表 */
export function getProjectDocuments(projectId: string) {
  return request.get<unknown, DocumentInfo[]>(`/v1/projects/${projectId}/documents`);
}

/** 确认文档 */
export function confirmDocument(projectId: string, documentId: string) {
  return request.post<unknown, DocumentInfo>(`/v1/projects/${projectId}/documents/${documentId}/confirm`);
}

/** 批量确认文档 */
export function batchConfirmDocuments(projectId: string, documentIds: string[]) {
  return request.post<unknown, void>(`/v1/projects/${projectId}/documents/batch-confirm`, { document_ids: documentIds });
}

/** 生成文档 */
export function generateDocuments(projectId: string) {
  return request.post<unknown, DocumentInfo[]>('/v1/generator/generate/all', { project_id: projectId });
}

/** 上传文件 */
export function uploadFile(projectId: string, file: File, onProgress?: (progress: number) => void) {
  const formData = new FormData();
  formData.append('file', file);
  return request.post<unknown, UploadFileInfo>(`/v1/uploads/${projectId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (event.total && onProgress) {
        onProgress(Math.round((event.loaded * 100) / event.total));
      }
    },
  });
}

/** 获取已上传文件列表 */
export function getUploadedFiles(projectId: string) {
  return request.get<unknown, UploadFileInfo[]>(`/v1/uploads/${projectId}`);
}

/* ==================== 多轮对话API (V1.1) ==================== */

/** 追问问题类型 */
export interface FollowUpQuestion {
  field: string;
  question: string;
  example?: string;
  reason?: string;
}

/** 对话响应类型 */
export interface ConversationResponse {
  sessionId: string;
  status: 'collecting' | 'complete';
  parsedInfo: Record<string, any>;
  missingFields: string[];
  followUpQuestions: FollowUpQuestion[];
  progressPercent: number;
  message: string;
}

/** 开始多轮对话 */
export function startConversation(initialText: string, projectId?: string) {
  return request.post<unknown, ConversationResponse>('/v1/conversation/start', {
    initial_text: initialText,
    project_id: projectId,
  });
}

/** 继续对话 */
export function continueConversation(sessionId: string, answer: string) {
  return request.post<unknown, ConversationResponse>('/v1/conversation/continue', {
    session_id: sessionId,
    answer,
  });
}

/** 获取会话状态 */
export function getConversationStatus(sessionId: string) {
  return request.get<unknown, {
    sessionId: string;
    status: string;
    createdAt: string;
    lastUpdated: string;
    messageCount: number;
    currentInfo: Record<string, any>;
  }>(`/v1/conversation/${sessionId}/status`);
}

/** 完成对话 */
export function completeConversation(sessionId: string, projectId?: string) {
  return request.post<unknown, {
    message: string;
    sessionId: string;
    projectId: string;
    finalInfo: Record<string, any>;
    remainingMissing: string[];
  }>(`/v1/conversation/${sessionId}/complete`, { project_id: projectId });
}

/* ==================== 补充材料API (V1.1) ==================== */

/** 材料类型配置 */
export interface MaterialTypeConfig {
  type: string;
  name: string;
  description: string;
  allowed_extensions: string[];
  max_size_mb: number;
  extract_fields: string[];
}

/** 材料信息类型 */
export interface MaterialInfo {
  materialId: string;
  materialType: string;
  fileName: string;
  fileSize: number;
  status: string;
  extractedInfo?: Record<string, any>;
  uploadedAt: string;
}

/** 材料上传响应 */
export interface MaterialUploadResponse {
  materialId: string;
  materialType: string;
  fileName: string;
  fileSize: number;
  status: string;
  extractedInfo?: Record<string, any>;
  message: string;
}

/** 获取材料类型列表 */
export function getMaterialTypes() {
  return request.get<unknown, MaterialTypeConfig[]>('/v1/materials/types');
}

/** 上传补充材料 */
export function uploadMaterial(
  projectId: string,
  materialType: string,
  file: File,
  onProgress?: (progress: number) => void
) {
  const formData = new FormData();
  formData.append('project_id', projectId);
  formData.append('material_type', materialType);
  formData.append('file', file);
  
  return request.post<unknown, MaterialUploadResponse>('/v1/materials/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (event.total && onProgress) {
        onProgress(Math.round((event.loaded * 100) / event.total));
      }
    },
  });
}

/** 获取项目材料列表 */
export function getProjectMaterials(projectId: string, materialType?: string) {
  return request.get<unknown, { projectId: string; materials: MaterialInfo[]; totalCount: number }>(
    `/v1/materials/project/${projectId}`,
    { params: { material_type: materialType } }
  );
}

/** 获取材料详情 */
export function getMaterialDetail(materialId: string) {
  return request.get<unknown, MaterialInfo>(`/v1/materials/${materialId}`);
}

/** 删除材料 */
export function deleteMaterial(materialId: string) {
  return request.delete<unknown, { message: string; materialId: string }>(`/v1/materials/${materialId}`);
}

/** 重新处理材料 */
export function reprocessMaterial(materialId: string) {
  return request.post<unknown, MaterialUploadResponse>(`/v1/materials/${materialId}/reprocess`);
}

/* ==================== 缺失项分析API (V1.1) ==================== */

/** 条款覆盖分析响应 */
export interface CoverageAnalysisResponse {
  projectId: string;
  projectName: string;
  standards: string[];
  summary: {
    totalClauses: number;
    covered: number;
    partial: number;
    missing: number;
    coverageRate: number;
  };
  clauses: Array<{
    clause: string;
    title: string;
    status: 'covered' | 'partial' | 'missing';
    relatedDocuments: string[];
  }>;
  suggestions: string[];
}

/** 快速覆盖检查响应 */
export interface QuickCoverageResponse {
  projectId: string;
  standard: string;
  totalClauses: number;
  covered: number;
  partial: number;
  missing: number;
  coverageRate: number;
  documentCount: number;
}

/** 分析条款覆盖情况 */
export function analyzeCoverage(projectId: string, standards?: string[]) {
  return request.post<unknown, CoverageAnalysisResponse>(`/v1/analyzer/coverage/${projectId}`, {
    standards,
  });
}

/** 快速覆盖检查 */
export function quickCoverageCheck(projectId: string, standard: string = 'ISO9001') {
  return request.post<unknown, QuickCoverageResponse>('/v1/analyzer/coverage/quick', {
    project_id: projectId,
    standard,
  });
}

/** 获取支持的标准列表 */
export function getSupportedStandards() {
  return request.get<unknown, {
    standards: Array<{
      code: string;
      name: string;
      totalClauses: number;
      description: string;
    }>;
  }>('/v1/analyzer/standards');
}

/* ==================== 环境/安全评估报告解析API (V1.2) ==================== */

/** 环境评估报告解析响应 */
export interface EnvironmentalReportResponse {
  companyName: string;
  aspectsCount: number;
  significantAspectsCount: number;
  complianceRate: number;
  environmentalAspects: Array<{
    activity: string;
    aspect: string;
    impact: string;
    significance: string;
  }>;
  generatedDocuments?: Record<string, any>;
}

/** 安全评估报告解析响应 */
export interface SafetyAssessmentResponse {
  companyName: string;
  hazardsCount: number;
  significantHazardsCount: number;
  incidentsCount: number;
  complianceRate: number;
  hazards: Array<{
    activity: string;
    hazardSource: string;
    riskDescription: string;
    riskScore: number;
    riskLevel: string;
  }>;
  generatedDocuments?: Record<string, any>;
}

/** 解析环境评估报告 */
export function analyzeEnvironmentalReport(reportText: string, generateDocuments: boolean = true) {
  return request.post<unknown, EnvironmentalReportResponse>('/v1/analyzer/environmental-report', {
    report_text: reportText,
    generate_documents: generateDocuments,
  });
}

/** 解析安全评估报告 */
export function analyzeSafetyAssessment(reportText: string, generateDocuments: boolean = true) {
  return request.post<unknown, SafetyAssessmentResponse>('/v1/analyzer/safety-assessment', {
    report_text: reportText,
    generate_documents: generateDocuments,
  });
}

/* ==================== 材料管理相关API (V1.0) ==================== */

/** 行业信息类型 */
export interface Industry {
  code: string;
  name: string;
  description: string;
}

/** 材料项类型 */
export interface MaterialItem {
  name: string;
  required: boolean;
  description: string;
  template_available: boolean;
  template_file?: string;
}

/** 材料清单响应类型 */
export interface MaterialListResponse {
  industry_code: string;
  industry_name: string;
  materials: {
    industry_specific: Record<string, MaterialItem[]>;
    common: Record<string, MaterialItem[]>;
  };
}

/** 获取行业列表 */
export const getIndustries = () => request.get<unknown, Industry[]>('/v1/materials/industries');

/** 获取材料清单 */
export const getMaterialList = (industryCode: string) =>
  request.get<unknown, MaterialListResponse>(`/v1/materials/list/${industryCode}`);

/** 获取可下载的模板列表 */
export const getDownloadableTemplates = (industryCode?: string) =>
  request.get<unknown, MaterialItem[]>('/v1/materials/templates/downloadable', {
    params: { industry_code: industryCode },
  });

/** 下载模板文件（直接浏览器下载） */
export const downloadTemplate = (materialName: string) => {
  window.open(`/api/v1/materials/template/download/${encodeURIComponent(materialName)}`, '_blank');
};

/* ==================== 自定义模板API (V1.3) ==================== */

/** 自定义模板类型 */
export interface CustomTemplate {
  templateId: string;
  name: string;
  description?: string;
  category: string;
  industry?: string;
  variables: string[];
  version: string;
  status: 'active' | 'disabled' | 'archived';
  createdAt: string;
  updatedAt: string;
}

/** 模板版本历史 */
export interface TemplateVersion {
  version: string;
  content: string;
  updatedAt: string;
}

/** 获取自定义模板列表 */
export function getCustomTemplates(params?: { category?: string; status?: string }) {
  return request.get<unknown, CustomTemplate[]>('/v1/custom-templates', { params });
}

/** 获取自定义模板详情 */
export function getCustomTemplate(templateId: string) {
  return request.get<unknown, CustomTemplate & { content: string; versionHistory: TemplateVersion[] }>(
    `/v1/custom-templates/${templateId}`
  );
}

/** 上传自定义模板 */
export function uploadCustomTemplate(data: {
  name: string;
  description?: string;
  category: string;
  industry?: string;
  content: string;
}) {
  return request.post<unknown, CustomTemplate>('/v1/custom-templates/upload', data);
}

/** 更新自定义模板 */
export function updateCustomTemplate(templateId: string, data: Partial<CustomTemplate>) {
  return request.put<unknown, CustomTemplate>(`/v1/custom-templates/${templateId}`, data);
}

/** 更新模板内容（自动创建新版本） */
export function updateTemplateContent(templateId: string, content: string) {
  return request.post<unknown, CustomTemplate>(`/v1/custom-templates/${templateId}/update-content`, {
    content,
  });
}

/** 删除自定义模板 */
export function deleteCustomTemplate(templateId: string) {
  return request.delete<unknown, { message: string }>(`/v1/custom-templates/${templateId}`);
}

/** 获取模板版本历史 */
export function getTemplateVersions(templateId: string) {
  return request.get<unknown, TemplateVersion[]>(`/v1/custom-templates/${templateId}/versions`);
}

/** 回滚到指定版本 */
export function rollbackTemplate(templateId: string, version: string) {
  return request.post<unknown, CustomTemplate>(`/v1/custom-templates/${templateId}/rollback`, {
    version,
  });
}

/* ==================== 团队协作API (V1.3) ==================== */

/** 团队成员角色 */
export type TeamRole = 'owner' | 'admin' | 'member' | 'viewer';

/** 团队信息 */
export interface Team {
  teamId: string;
  name: string;
  description?: string;
  ownerId: string;
  settings: {
    allowMemberInvite: boolean;
    defaultRole: TeamRole;
  };
  createdAt: string;
  updatedAt: string;
}

/** 团队成员 */
export interface TeamMember {
  id: string;
  teamId: string;
  userId: string;
  role: TeamRole;
  permissions: Record<string, boolean>;
  joinedAt: string;
  userName?: string;
  userEmail?: string;
}

/** 权限配置 */
export interface RolePermissions {
  canManageTeam: boolean;
  canInviteMember: boolean;
  canRemoveMember: boolean;
  canManageProject: boolean;
  canEditDocument: boolean;
  canViewDocument: boolean;
  canDeleteProject: boolean;
}

/** 获取我的团队列表 */
export function getMyTeams() {
  return request.get<unknown, Team[]>('/v1/teams/my');
}

/** 获取团队详情 */
export function getTeamDetail(teamId: string) {
  return request.get<unknown, Team & { members: TeamMember[] }>(`/v1/teams/${teamId}`);
}

/** 创建团队 */
export function createTeam(data: { name: string; description?: string }) {
  return request.post<unknown, Team>('/v1/teams', data);
}

/** 更新团队 */
export function updateTeam(teamId: string, data: Partial<Team>) {
  return request.put<unknown, Team>(`/v1/teams/${teamId}`, data);
}

/** 删除团队 */
export function deleteTeam(teamId: string) {
  return request.delete<unknown, { message: string }>(`/v1/teams/${teamId}`);
}

/** 邀请成员 */
export function inviteTeamMember(teamId: string, data: { email: string; role?: TeamRole }) {
  return request.post<unknown, TeamMember>(`/v1/teams/${teamId}/members`, data);
}

/** 更新成员角色 */
export function updateMemberRole(teamId: string, userId: string, role: TeamRole) {
  return request.put<unknown, TeamMember>(`/v1/teams/${teamId}/members/${userId}/role`, {
    role,
  });
}

/** 移除成员 */
export function removeTeamMember(teamId: string, userId: string) {
  return request.delete<unknown, { message: string }>(`/v1/teams/${teamId}/members/${userId}`);
}

/** 获取我的权限 */
export function getMyPermissions(teamId: string) {
  return request.get<unknown, RolePermissions>(`/v1/teams/${teamId}/my-permissions`);
}

/** 将项目分配给团队 */
export function assignProjectToTeam(projectId: string, teamId: string) {
  return request.post<unknown, { message: string }>(`/v1/teams/${teamId}/projects`, {
    project_id: projectId,
  });
}

/** 从团队移除项目 */
export function removeProjectFromTeam(teamId: string, projectId: string) {
  return request.delete<unknown, { message: string }>(`/v1/teams/${teamId}/projects/${projectId}`);
}

/* ==================== 文档导出API (V1.5) ==================== */

/** 导出选项 */
export interface ExportOptions {
  includeWatermark?: boolean;
  includeLogo?: boolean;
  documentFormat?: 'docx' | 'pdf';
  forceExport?: boolean;  // 即使有未确认文档也导出
}

/** 导出状态 */
export interface ExportStatus {
  taskId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  totalDocuments: number;
  processedDocuments: number;
  downloadUrl?: string;
  error?: string;
  createdAt: string;
}

/** 导出单个文档 */
export function exportSingleDocument(documentId: string, format: 'docx' | 'pdf' = 'docx') {
  // 直接下载
  window.open(`/api/v1/generator/export/single/${documentId}?format=${format}`, '_blank');
  return Promise.resolve({ success: true });
}

/** 导出项目全部文档为ZIP */
export async function exportProjectDocuments(projectId: string, options?: ExportOptions): Promise<ExportStatus> {
  const response = await request.post<unknown, ExportStatus>('/v1/generator/export/zip', {
    project_id: projectId,
    include_watermark: options?.includeWatermark ?? false,
    include_logo: options?.includeLogo ?? false,
    force_export: options?.forceExport ?? false,
  });
  return response;
}

/** 查询导出任务状态 */
export function getExportTaskStatus(taskId: string) {
  return request.get<unknown, ExportStatus>(`/v1/generator/task/${taskId}`);
}

/** 下载导出的文件 */
export function downloadExportedFile(taskId: string) {
  window.open(`/api/v1/generator/export/download/${taskId}`, '_blank');
}

/* ==================== 文档生成API (V1.5) ==================== */

/** 生成选项 */
export interface GenerateOptions {
  levels?: number[];  // 1-4，指定要生成的层级
  standards?: string[];  // ISO9001, ISO14001, ISO45001
  templateIds?: string[];  // 指定模板ID
  overwrite?: boolean;  // 是否覆盖已有文档
}

/** 生成状态 */
export interface GenerateStatus {
  taskId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  totalDocuments: number;
  generatedDocuments: DocumentInfo[];
  errors: Array<{ documentName: string; error: string }>;
  createdAt: string;
}

/** 获取可用模板列表 */
export function getAvailableTemplates(level?: number) {
  return request.get<unknown, Array<{
    templateId: string;
    name: string;
    level: number;
    category: string;
    standard?: string;
    description?: string;
  }>>('/v1/generator/templates/available', { params: { level } });
}

/** 生成单个文档 */
export function generateSingleDocument(projectId: string, templateId: string) {
  return request.post<unknown, DocumentInfo>('/v1/generator/generate', {
    project_id: projectId,
    template_id: templateId,
  });
}

/** 批量生成文档 */
export function generateBatchDocuments(projectId: string, templateIds: string[]) {
  return request.post<unknown, GenerateStatus>('/v1/generator/generate/batch', {
    project_id: projectId,
    template_ids: templateIds,
  });
}

/** 按层级生成文档 */
export function generateByLevel(projectId: string, levels: number[], standards?: string[]) {
  return request.post<unknown, GenerateStatus>('/v1/generator/generate/level', {
    project_id: projectId,
    levels,
    standards,
  });
}

/** 生成全套体系文件 */
export function generateAllDocuments(projectId: string, options?: GenerateOptions) {
  return request.post<unknown, GenerateStatus>('/v1/generator/generate/all', {
    project_id: projectId,
    levels: options?.levels ?? [1, 2, 3, 4],
    standards: options?.standards ?? ['ISO9001', 'ISO14001', 'ISO45001'],
    overwrite: options?.overwrite ?? false,
  });
}

/** 查询生成任务状态 */
export function getGenerateTaskStatus(taskId: string) {
  return request.get<unknown, GenerateStatus>(`/v1/generator/task/${taskId}`);
}

/** 获取支持的文档层级 */
export function getSupportedLevels() {
  return request.get<unknown, Array<{
    level: number;
    name: string;
    description: string;
    documentCount: number;
  }>>('/v1/generator/levels');
}

export default request;

/* ==================== 用户认证API ==================== */

/** 登录请求 */
export interface LoginRequest {
  username: string;
  password: string;
}

/** 注册请求 */
export interface RegisterRequest {
  username: string;
  password: string;
  email?: string;
  full_name?: string;
  company?: string;
}

/** 用户信息 */
export interface UserInfo {
  user_id: string;
  username: string;
  email?: string;
  full_name?: string;
  company?: string;
  role: string;
  status: string;
  created_at: string;
}

/** 令牌响应 */
export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

/** 用户注册 */
export function register(data: RegisterRequest) {
  return request.post<unknown, UserInfo>('/v1/auth/register', data);
}

/** 用户登录（表单格式） */
export function login(username: string, password: string) {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  return request.post<unknown, TokenResponse>('/v1/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
}

/** 用户登录（JSON格式） */
export function loginJson(data: LoginRequest) {
  return request.post<unknown, TokenResponse>('/v1/auth/login/json', data);
}

/** 获取当前用户信息 */
export function getCurrentUser() {
  return request.get<unknown, UserInfo>('/v1/auth/me');
}

/** 退出登录 */
export function logout() {
  return request.post<unknown, { message: string }>('/v1/auth/logout');
}

/* ==================== 行业配置 API (V2.2) ==================== */

/** 行业配置类型 */
export interface IndustryConfig {
  id: number;
  industry_code: string;
  industry_name: string;
  description: string;
  has_design_development: boolean;
  has_equipment_operations: boolean;
  has_multi_projects: boolean;
  has_outsourcing: boolean;
  internal_audit_by_dept: boolean;
  emergency_plans: string[];
  required_licenses: string[];
  certification_scope_classes: string[];
  is_active: boolean;
  special_file_count: number;
}

/** 行业详情（含特殊文件列表） */
export interface IndustryDetail extends IndustryConfig {
  special_files: Array<{
    id: number;
    file_level: string;
    file_code: string;
    file_name: string;
    description: string;
    category: string;
    iso_clause: string;
    sort_order: number;
  }>;
}

/** 文件清单项 */
export interface FileListItem {
  file_code: string;
  file_name: string;
  file_level: string;
  category: string;
  iso_clause: string | null;
  is_industry_specific: boolean;
  is_dynamic: boolean;
  description: string | null;
}

/** 文件清单响应 */
export interface FileListResponse {
  industry_code: string;
  industry_name: string;
  total_count: number;
  level_counts: Record<string, number>;
  files: FileListItem[];
}

/** 获取行业列表 */
export function getIndustryConfigs(params?: { active_only?: boolean }) {
  return request.get<unknown, IndustryConfig[]>('/v1/industry/list', { params });
}

/** 获取行业详情 */
export function getIndustryConfig(code: string) {
  return request.get<unknown, IndustryDetail>(`/v1/industry/${code}`);
}

/** 获取行业特征检测 */
export function checkIndustryFeatures(code: string) {
  return request.get<unknown, {
    industry_code: string;
    industry_name: string;
    has_design_development: boolean;
    has_equipment_operations: boolean;
    has_multi_projects: boolean;
    has_outsourcing: boolean;
    emergency_plans: string[];
    required_licenses: string[];
  }>(`/v1/industry/${code}/check-features`);
}

/** 生成文件清单 */
export function generateFileList(data: {
  industry_code: string;
  company_info: Record<string, unknown>;
  include_equipment?: boolean;
  include_emergency_plans?: boolean;
  equipment_list?: Array<Record<string, unknown>>;
  levels?: string[];
}) {
  return request.post<unknown, FileListResponse>('/v1/generator/file-list', data);
}

/** 获取设备分类列表 */
export function getEquipmentCategories() {
  return request.get<unknown, Array<{ code: string; name: string; equipments: string[] }>>('/v1/generator/equipment-categories');
}

/** 获取预案分类列表 */
export function getEmergencyPlanCategories() {
  return request.get<unknown, Array<{ code: string; name: string; plans: string[] }>>('/v1/generator/emergency-plan-categories');
}
