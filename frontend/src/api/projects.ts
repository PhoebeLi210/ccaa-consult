import { request } from './request';

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

export interface UploadFileInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  status: 'uploading' | 'success' | 'error';
  progress: number;
}

export function getProjectList(params?: {
  page?: number;
  pageSize?: number;
  keyword?: string;
}) {
  return request.get<unknown, ProjectInfo[]>('/v1/projects', { params });
}

export function getProjectDetail(id: string) {
  return request.get<unknown, ProjectInfo>(`/v1/projects/${id}`);
}

export function createProject(data: Partial<ProjectInfo>) {
  return request.post<unknown, ProjectInfo>('/v1/projects', data);
}

export function updateProject(id: string, data: Partial<ProjectInfo>) {
  return request.put<unknown, ProjectInfo>(`/v1/projects/${id}`, data);
}

export function deleteProject(id: string) {
  return request.delete<unknown, void>(`/v1/projects/${id}`);
}

export function parseNaturalLanguage(text: string) {
  return request.post<unknown, ParseResult>('/v1/parse', { text });
}

export function getProjectDocuments(projectId: string) {
  return request.get<unknown, DocumentInfo[]>(`/v1/projects/${projectId}/documents`);
}

export function confirmDocument(projectId: string, documentId: string) {
  return request.post<unknown, DocumentInfo>(`/v1/projects/${projectId}/documents/${documentId}/confirm`);
}

export function batchConfirmDocuments(projectId: string, documentIds: string[]) {
  return request.post<unknown, void>(`/v1/projects/${projectId}/documents/batch-confirm`, { document_ids: documentIds });
}

export function generateDocuments(projectId: string) {
  return request.post<unknown, DocumentInfo[]>('/v1/generator/generate/all', { project_id: projectId });
}

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

export function getUploadedFiles(projectId: string) {
  return request.get<unknown, UploadFileInfo[]>(`/v1/uploads/${projectId}`);
}
