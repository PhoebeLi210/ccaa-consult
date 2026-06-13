import { request } from './request';
import { DocumentInfo } from './projects';

export interface ExportOptions {
  include_watermark?: boolean;
  include_logo?: boolean;
  document_format?: 'docx' | 'pdf';
  force_export?: boolean;
}

export interface ExportStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  total_documents: number;
  processed_documents: number;
  download_url?: string;
  error?: string;
  created_at: string;
}

export interface GenerateOptions {
  levels?: number[];
  standards?: string[];
  template_ids?: string[];
  overwrite?: boolean;
}

export interface GenerateStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  total_documents: number;
  generated_documents: DocumentInfo[];
  errors: Array<{ document_name: string; error: string }>;
  created_at: string;
}

export function exportSingleDocument(documentId: string, format: 'docx' | 'pdf' = 'docx') {
  window.open(`/api/v1/generator/export/single/${documentId}?format=${format}`, '_blank');
  return Promise.resolve({ success: true });
}

export async function exportProjectDocuments(projectId: string, options?: ExportOptions): Promise<ExportStatus> {
  const response = await request.post<unknown, ExportStatus>('/v1/generator/export/zip', {
    project_id: projectId,
    include_watermark: options?.include_watermark ?? false,
    include_logo: options?.include_logo ?? false,
    force_export: options?.force_export ?? false,
  });
  return response;
}

export function getExportTaskStatus(taskId: string) {
  return request.get<unknown, ExportStatus>(`/v1/generator/task/${taskId}`);
}

export function downloadExportedFile(taskId: string) {
  window.open(`/api/v1/generator/export/download/${taskId}`, '_blank');
}

export function getAvailableTemplates(level?: number) {
  return request.get<unknown, Array<{
    template_id: string;
    name: string;
    level: number;
    category: string;
    standard?: string;
    description?: string;
  }>>('/v1/generator/templates/available', { params: { level } });
}

export function generateSingleDocument(projectId: string, template_id: string) {
  return request.post<unknown, DocumentInfo>('/v1/generator/generate', {
    project_id: projectId,
    template_id: template_id,
  });
}

export function generateBatchDocuments(projectId: string, template_ids: string[]) {
  return request.post<unknown, GenerateStatus>('/v1/generator/generate/batch', {
    project_id: projectId,
    template_ids: template_ids,
  });
}

export function generateByLevel(projectId: string, levels: number[], standards?: string[]) {
  return request.post<unknown, GenerateStatus>('/v1/generator/generate/level', {
    project_id: projectId,
    levels,
    standards,
  });
}

export function generateAllDocuments(projectId: string, options?: GenerateOptions) {
  return request.post<unknown, GenerateStatus>('/v1/generator/generate/all', {
    project_id: projectId,
    levels: options?.levels ?? [1, 2, 3, 4],
    standards: options?.standards ?? ['ISO9001', 'ISO14001', 'ISO45001'],
    overwrite: options?.overwrite ?? false,
  });
}

export function getGenerateTaskStatus(taskId: string) {
  return request.get<unknown, GenerateStatus>(`/v1/generator/task/${taskId}`);
}

export function getSupportedLevels() {
  return request.get<unknown, Array<{
    level: number;
    name: string;
    description: string;
    document_count: number;
  }>>('/v1/generator/levels');
}
