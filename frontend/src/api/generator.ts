import { request } from './request';
import { DocumentInfo } from './projects';

export interface ExportOptions {
  includeWatermark?: boolean;
  includeLogo?: boolean;
  documentFormat?: 'docx' | 'pdf';
  forceExport?: boolean;
}

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

export interface GenerateOptions {
  levels?: number[];
  standards?: string[];
  templateIds?: string[];
  overwrite?: boolean;
}

export interface GenerateStatus {
  taskId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  totalDocuments: number;
  generatedDocuments: DocumentInfo[];
  errors: Array<{ documentName: string; error: string }>;
  createdAt: string;
}

export function exportSingleDocument(documentId: string, format: 'docx' | 'pdf' = 'docx') {
  window.open(`/api/v1/generator/export/single/${documentId}?format=${format}`, '_blank');
  return Promise.resolve({ success: true });
}

export async function exportProjectDocuments(projectId: string, options?: ExportOptions): Promise<ExportStatus> {
  const response = await request.post<unknown, ExportStatus>('/v1/generator/export/zip', {
    project_id: projectId,
    include_watermark: options?.includeWatermark ?? false,
    include_logo: options?.includeLogo ?? false,
    force_export: options?.forceExport ?? false,
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
    templateId: string;
    name: string;
    level: number;
    category: string;
    standard?: string;
    description?: string;
  }>>('/v1/generator/templates/available', { params: { level } });
}

export function generateSingleDocument(projectId: string, templateId: string) {
  return request.post<unknown, DocumentInfo>('/v1/generator/generate', {
    project_id: projectId,
    template_id: templateId,
  });
}

export function generateBatchDocuments(projectId: string, templateIds: string[]) {
  return request.post<unknown, GenerateStatus>('/v1/generator/generate/batch', {
    project_id: projectId,
    template_ids: templateIds,
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
    documentCount: number;
  }>>('/v1/generator/levels');
}
