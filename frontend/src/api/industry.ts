import { request } from './request';

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

export interface FileListResponse {
  industry_code: string;
  industry_name: string;
  total_count: number;
  level_counts: Record<string, number>;
  files: FileListItem[];
}

export function getIndustryConfigs(params?: { active_only?: boolean }) {
  return request.get<unknown, IndustryConfig[]>('/v1/industry/list', { params });
}

export function getIndustryConfig(code: string) {
  return request.get<unknown, IndustryDetail>(`/v1/industry/${code}`);
}

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

export function getEquipmentCategories() {
  return request.get<unknown, Array<{ code: string; name: string; equipments: string[] }>>('/v1/generator/equipment-categories');
}

export function getEmergencyPlanCategories() {
  return request.get<unknown, Array<{ code: string; name: string; plans: string[] }>>('/v1/generator/emergency-plan-categories');
}
