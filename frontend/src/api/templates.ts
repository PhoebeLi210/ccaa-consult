import { request } from './request';

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

export interface TemplateVersion {
  version: string;
  content: string;
  updatedAt: string;
}

export function getCustomTemplates(params?: { category?: string; status?: string }) {
  return request.get<unknown, CustomTemplate[]>('/v1/custom-templates', { params });
}

export function getCustomTemplate(templateId: string) {
  return request.get<unknown, CustomTemplate & { content: string; versionHistory: TemplateVersion[] }>(
    `/v1/custom-templates/${templateId}`
  );
}

export function uploadCustomTemplate(data: {
  name: string;
  description?: string;
  category: string;
  industry?: string;
  content: string;
}) {
  return request.post<unknown, CustomTemplate>('/v1/custom-templates/upload', data);
}

export function updateCustomTemplate(templateId: string, data: Partial<CustomTemplate>) {
  return request.put<unknown, CustomTemplate>(`/v1/custom-templates/${templateId}`, data);
}

export function updateTemplateContent(templateId: string, content: string) {
  return request.post<unknown, CustomTemplate>(`/v1/custom-templates/${templateId}/update-content`, {
    content,
  });
}

export function deleteCustomTemplate(templateId: string) {
  return request.delete<unknown, { message: string }>(`/v1/custom-templates/${templateId}`);
}

export function getTemplateVersions(templateId: string) {
  return request.get<unknown, TemplateVersion[]>(`/v1/custom-templates/${templateId}/versions`);
}

export function rollbackTemplate(templateId: string, version: string) {
  return request.post<unknown, CustomTemplate>(`/v1/custom-templates/${templateId}/rollback`, {
    version,
  });
}
