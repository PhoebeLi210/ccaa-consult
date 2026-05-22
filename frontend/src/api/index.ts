import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

/** 后端API基础URL */
const BASE_URL = '/api';

/** 自定义响应数据结构 */
interface ApiResponse<T = unknown> {
  code: number;
  message: string;
  data: T;
}

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
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response;
    if (data.code === 0 || data.code === 200) {
      return data.data as unknown as AxiosResponse;
    }
    // 业务错误
    return Promise.reject(new Error(data.message || '请求失败'));
  },
  (error) => {
    // HTTP错误
    const message =
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
  return request.get<unknown, ProjectInfo[]>('/projects', { params });
}

/** 获取项目详情 */
export function getProjectDetail(id: string) {
  return request.get<unknown, ProjectInfo>(`/projects/${id}`);
}

/** 创建项目 */
export function createProject(data: Partial<ProjectInfo>) {
  return request.post<unknown, ProjectInfo>('/projects', data);
}

/** 更新项目 */
export function updateProject(id: string, data: Partial<ProjectInfo>) {
  return request.put<unknown, ProjectInfo>(`/projects/${id}`, data);
}

/** 删除项目 */
export function deleteProject(id: string) {
  return request.delete<unknown, void>(`/projects/${id}`);
}

/** AI自然语言解析 */
export function parseNaturalLanguage(text: string) {
  return request.post<unknown, ParseResult>('/ai/parse', { text });
}

/** 获取项目文档列表 */
export function getProjectDocuments(projectId: string) {
  return request.get<unknown, DocumentInfo[]>(`/projects/${projectId}/documents`);
}

/** 确认文档 */
export function confirmDocument(documentId: string) {
  return request.put<unknown, DocumentInfo>(`/documents/${documentId}/confirm`);
}

/** 批量确认文档 */
export function batchConfirmDocuments(documentIds: string[]) {
  return request.post<unknown, void>('/documents/batch-confirm', { ids: documentIds });
}

/** 生成文档 */
export function generateDocuments(projectId: string) {
  return request.post<unknown, DocumentInfo[]>(`/projects/${projectId}/generate-documents`);
}

/** 上传文件 */
export function uploadFile(file: File, onProgress?: (progress: number) => void) {
  const formData = new FormData();
  formData.append('file', file);
  return request.post<unknown, UploadFileInfo>('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (event.total && onProgress) {
        onProgress(Math.round((event.loaded * 100) / event.total));
      }
    },
  });
}

/** 获取已上传文件列表 */
export function getUploadedFiles(params?: { projectId?: string }) {
  return request.get<unknown, UploadFileInfo[]>('/files', { params });
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

/* ==================== 流程图API ==================== */

/** 节点类型 */
export type NodeType = 'start' | 'end' | 'process' | 'decision' | 'document';

/** 流程图节点 */
export interface FlowchartNode {
  id: string;
  type: NodeType;
  label: string;
  x: number;
  y: number;
  description?: string;
}

/** 流程图边 */
export interface FlowchartEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

/** 流程图数据 */
export interface FlowchartData {
  nodes: FlowchartNode[];
  edges: FlowchartEdge[];
}

/** 流程图信息 */
export interface FlowchartInfo {
  id: string;
  name: string;
  description?: string;
  status: 'draft' | 'published';
  nodes: FlowchartNode[];
  edges: FlowchartEdge[];
  nodeCount?: number;
  edgeCount?: number;
  createdAt: string;
  updatedAt: string;
}

/** 创建流程图请求 */
export interface CreateFlowchartRequest {
  name: string;
  description?: string;
}

/** 更新流程图请求 */
export interface UpdateFlowchartRequest {
  name?: string;
  description?: string;
  data?: FlowchartData;
  status?: 'draft' | 'published';
}

/** 获取流程图列表 */
export function getFlowchartList() {
  return request.get<unknown, FlowchartInfo[]>('/v1/flowcharts');
}

/** 获取流程图详情 */
export function getFlowchartDetail(id: string) {
  return request.get<unknown, FlowchartInfo>(`/v1/flowcharts/${id}`);
}

/** 创建流程图 */
export function createFlowchart(data: CreateFlowchartRequest) {
  return request.post<unknown, FlowchartInfo>('/v1/flowcharts', data);
}

/** 更新流程图 */
export function updateFlowchart(id: string, data: UpdateFlowchartRequest) {
  return request.put<unknown, FlowchartInfo>(`/v1/flowcharts/${id}`, data);
}

/** 删除流程图 */
export function deleteFlowchart(id: string) {
  return request.delete<unknown, void>(`/v1/flowcharts/${id}`);
}

/** 发布流程图 */
export function publishFlowchart(id: string) {
  return request.post<unknown, FlowchartInfo>(`/v1/flowcharts/${id}/publish`);
}


/* ==================== 认证阶段API ==================== */

/** 认证阶段类型 */
export type CertStageType = 'initial' | 'surveillance_1' | 'surveillance_2' | 'recertification';

/** 认证阶段选项 */
export interface CertStageOption {
  key: CertStageType;
  name: string;
  description: string;
  year: string;
  documentScope: string[];
  updateScope: string[];
  requireOldFiles: boolean;
}

/** 文件范围信息 */
export interface DocumentScopeInfo {
  stage: CertStageType;
  generateFiles: Array<{
    category: string;
    files: string[];
  }>;
  updateFiles: Array<{
    category: string;
    files: string[];
  }>;
  skipFiles: string[];
}

/** 旧版文件提取结果 */
export interface OldFileExtractionResult {
  qualityPolicy: {
    text: string;
    source: string;
  };
  qualityObjectives: Array<{
    id: string;
    content: string;
    department: string;
    target: string;
    period: string;
  }>;
  fileNamingRules: Array<{
    prefix: string;
    category: string;
    format: string;
    example: string;
  }>;
  departments: Array<{
    name: string;
    code: string;
    description?: string;
    functions?: string[];
  }>;
  companyInfo: {
    companyName: string;
    address: string;
    legalPerson: string;
    registeredCapital: string;
    businessScope: string;
    establishedDate: string;
    unifiedSocialCreditCode: string;
  };
  rawFiles: Array<{
    fileName: string;
    fileType: string;
    extractedFields: string[];
  }>;
}

/** 文件分类结果 */
export interface FileClassificationResult {
  projectId: string;
  totalFiles: number;
  classifications: Array<{
    fileName: string;
    category: string;
    confidence: number;
    suggestedName?: string;
  }>;
  unclassifiedFiles: string[];
}

/** 获取认证阶段选项 */
export function getCertStageOptions() {
  return request.get<unknown, CertStageOption[]>('/v1/cert-stages/options');
}

/** 获取文件范围 */
export function getDocumentScope(stage: CertStageType) {
  return request.get<unknown, DocumentScopeInfo>(`/v1/cert-stages/${stage}/document-scope`);
}

/** AI建议认证阶段 */
export function suggestCertStage(companyInfo: {
  companyName?: string;
  certStartDate?: string;
  lastAuditDate?: string;
  certCycle?: number;
}) {
  return request.post<unknown, { suggestedStage: CertStageType; reason: string }>(
    '/v1/cert-stages/suggest',
    companyInfo,
  );
}

/** 上传旧版文件 */
export function uploadOldFiles(
  projectId: string,
  files: File[],
  onProgress?: (progress: number) => void,
) {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  formData.append('project_id', projectId);

  return request.post<unknown, { uploadedCount: number; fileIds: string[] }>(
    '/v1/old-files/upload',
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (event.total && onProgress) {
          onProgress(Math.round((event.loaded * 100) / event.total));
        }
      },
    },
  );
}

/** 提取旧版文件信息 */
export function extractOldFiles(projectId: string) {
  return request.post<unknown, OldFileExtractionResult>(
    `/v1/old-files/${projectId}/extract`,
  );
}

/** 获取提取结果 */
export function getExtractionResult(projectId: string) {
  return request.get<unknown, OldFileExtractionResult>(
    `/v1/old-files/${projectId}/result`,
  );
}

/** 分类文件 */
export function classifyFiles(projectId: string) {
  return request.post<unknown, FileClassificationResult>(
    `/v1/old-files/${projectId}/classify`,
  );
}

export default request;
