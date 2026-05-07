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

export default request;
