import { request } from './request';

/** 知识分类 */
export type KnowledgeCategory = 'standard' | 'experience' | 'application' | 'user';

/** 行业数据状态 */
export type IndustryDataStatus = 'complete' | 'partial' | 'template' | 'empty';

/** 行业上下文 */
export interface IndustryContext {
  industry: {
    code: string;
    name: string;
    name_en?: string;
    data_status: IndustryDataStatus;
    sub_categories_count?: number;
    keywords?: string[];
    key_processes?: string[];
  };
  audit_points: AuditPoint[];
  typical_ncs: TypicalNC[];
  checklists: ChecklistItem[];
  regulations: Regulation[];
  cases: CompanyCase[];
  [key: string]: any;
}

/** 典型不符合项 */
export interface TypicalNC {
  id?: string;
  clause?: string;
  title?: string;
  description?: string;
  risk_level?: string;
  frequency?: string;
  [key: string]: any;
}

/** 检查清单项 */
export interface ChecklistItem {
  id?: string;
  item?: string;
  description?: string;
  method?: string;
  standard_reference?: string;
  [key: string]: any;
}

/** 法规 */
export interface Regulation {
  id?: string;
  name?: string;
  scope?: string;
  effective_date?: string;
  key_requirements?: string[];
  [key: string]: any;
}

/** 公司案例 */
export interface CompanyCase {
  id?: string;
  company_name?: string;
  industry?: string;
  description?: string;
  result?: string;
  [key: string]: any;
}

/** 审核点 */
export interface AuditPoint {
  id?: string;
  clause?: string;
  title?: string;
  description?: string;
  risk_level?: string;
  audit_method?: string;
  evidence?: string[];
  common_issues?: string[];
  [key: string]: any;
}

/** 标准条款 */
export interface StandardClause {
  id?: string;
  clause_number?: string;
  title?: string;
  description?: string;
  standard?: string;
  requirements?: string[];
  records?: RecordRequirement[];
  related_clauses?: string[];
  audit_points?: AuditPoint[];
  record_requirements?: RecordRequirement[];
  [key: string]: any;
}

/** 记录要求 */
export interface RecordRequirement {
  id?: string;
  type?: string;
  description?: string;
  template?: string;
  [key: string]: any;
}

/** 知识库项目 */
export interface KnowledgeItem {
  id: string;
  title: string;
  summary?: string;
  category?: KnowledgeCategory;
  industry_name?: string;
  tags?: string[];
  content?: string;
  view_count?: number;
  created_at?: string;
  updated_at?: string;
  [key: string]: any;
}

/** 知识分类树节点 */
export interface KnowledgeCategoryTree {
  key: string;
  title: string;
  category?: KnowledgeCategory;
  children?: KnowledgeCategoryTree[];
  [key: string]: any;
}

/** 行业信息 */
export interface KnowledgeIndustry {
  code: string;
  name: string;
  name_en?: string;
  data_status?: IndustryDataStatus;
  keywords?: string[];
  sub_categories_count?: number;
  [key: string]: any;
}

// ============ API Functions ============

export function getIndustryContext(code: string) {
  return request.get<unknown, IndustryContext>(`/v1/knowledge/industry/${code}/context`);
}

export function getIndustryList(params?: any) {
  return request.get<unknown, KnowledgeIndustry[]>('/v1/knowledge/industries', { params });
}

export function getIndustryDataStatus(params?: any) {
  return request.get<unknown, IndustryDataStatus>('/v1/knowledge/industry/status', { params });
}

/** 知识库分页响应 */
export interface KnowledgeListResponse {
  items: KnowledgeItem[];
  total: number;
}

export function getKnowledgeList(params?: any) {
  return request.get<unknown, KnowledgeListResponse>('/v1/knowledge/list', { params });
}

export function getKnowledgeCategoryTree() {
  return request.get<unknown, KnowledgeCategoryTree[]>('/v1/knowledge/categories/tree');
}

export function searchKnowledge(params: { q?: string; query?: string; [key: string]: any }) {
  return request.get<unknown, KnowledgeListResponse>('/v1/knowledge/search', { params });
}

export function getSupportedStandardsList() {
  return request.get<unknown, { code: string; name: string }[]>('/v1/knowledge/standards/list');
}

export function getKnowledgeDetail(id: string) {
  return request.get<unknown, KnowledgeItem>(`/v1/knowledge/${id}`);
}

export function getRelatedKnowledge(id: string, limit?: number) {
  return request.get<unknown, KnowledgeItem[]>(`/v1/knowledge/${id}/related`, { params: limit ? { limit } : undefined });
}

export function incrementViewCount(id: string) {
  return request.post<unknown, void>(`/v1/knowledge/${id}/view`);
}

export function getStandardClauseDetail(id: string) {
  return request.get<unknown, StandardClause>(`/v1/knowledge/standards/${id}`);
}
