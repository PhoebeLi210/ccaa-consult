import { request } from './request';

export interface MaterialTypeConfig {
  type: string;
  name: string;
  description: string;
  allowed_extensions: string[];
  max_size_mb: number;
  extract_fields: string[];
}

export interface MaterialInfo {
  materialId: string;
  materialType: string;
  fileName: string;
  fileSize: number;
  status: string;
  extractedInfo?: Record<string, any>;
  uploadedAt: string;
}

export interface MaterialUploadResponse {
  materialId: string;
  materialType: string;
  fileName: string;
  fileSize: number;
  status: string;
  extractedInfo?: Record<string, any>;
  message: string;
}

export interface Industry {
  code: string;
  name: string;
  description: string;
}

export interface MaterialItem {
  name: string;
  required: boolean;
  description: string;
  template_available: boolean;
  template_file?: string;
}

export interface MaterialListResponse {
  industry_code: string;
  industry_name: string;
  materials: {
    industry_specific: Record<string, MaterialItem[]>;
    common: Record<string, MaterialItem[]>;
  };
}

export function getMaterialTypes() {
  return request.get<unknown, MaterialTypeConfig[]>('/v1/materials/types');
}

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

export function getProjectMaterials(projectId: string, materialType?: string) {
  return request.get<unknown, { projectId: string; materials: MaterialInfo[]; totalCount: number }>(
    `/v1/materials/project/${projectId}`,
    { params: { material_type: materialType } }
  );
}

export function getMaterialDetail(materialId: string) {
  return request.get<unknown, MaterialInfo>(`/v1/materials/${materialId}`);
}

export function deleteMaterial(materialId: string) {
  return request.delete<unknown, { message: string; materialId: string }>(`/v1/materials/${materialId}`);
}

export function reprocessMaterial(materialId: string) {
  return request.post<unknown, MaterialUploadResponse>(`/v1/materials/${materialId}/reprocess`);
}

export const getIndustries = () => request.get<unknown, Industry[]>('/v1/materials/industries');

export const getMaterialList = (industryCode: string) =>
  request.get<unknown, MaterialListResponse>(`/v1/materials/list/${industryCode}`);

export const getDownloadableTemplates = (industryCode?: string) =>
  request.get<unknown, MaterialItem[]>('/v1/materials/templates/downloadable', {
    params: { industry_code: industryCode },
  });

export const downloadTemplate = (materialName: string) => {
  window.open(`/api/v1/materials/template/download/${encodeURIComponent(materialName)}`, '_blank');
};
