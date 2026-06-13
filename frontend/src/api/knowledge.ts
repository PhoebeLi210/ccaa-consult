import request from './index';

/* ==================== 知识库相关类型定义 ==================== */

/** 知识分类类型 */
export type KnowledgeCategory = 'standard' | 'experience' | 'application' | 'user';

/** 知识项类型 */
export interface KnowledgeItem {
  id: string;
  title: string;
  category: KnowledgeCategory;
  sub_category?: string;
  standard?: string;  // 所属标准，如 ISO9001, ISO14001, ISO45001
  industry?: string;  // 所属行业代码
  industry_name?: string;
  tags: string[];
  summary: string;
  content?: string;
  view_count: number;
  created_at: string;
  updated_at: string;
}

/** 标准条款类型 */
export interface StandardClause {
  id: string;
  standard: string;  // ISO9001, ISO14001, ISO45001
  clause_number: string;  // 条款号，如 4.1, 5.2
  title: string;
  content: string;
  requirements: string[];  // 要求列表
  records: RecordRequirement[];  // 记录要求
  audit_points: AuditPoint[];  // 审核要点
  related_clauses: string[];  // 相关条款
  parent_clause?: string;  // 父条款
  level: number;  // 层级
}

/** 记录要求类型 */
export interface RecordRequirement {
  id: string;
  name: string;
  description: string;
  retention_period?: string;  // 保存期限
  template?: string;  // 模板文件名
  required: boolean;
}

/** 审核要点类型 */
export interface AuditPoint {
  id: string;
  content: string;
  method: 'document' | 'interview' | 'observation';  // 审核方法
  evidence: string[];  // 所需证据
  common_issues: string[];  // 常见问题
}

/** 行业知识类型 */
export interface IndustryKnowledge {
  id: string;
  industry_code: string;
  industry_name: string;
  category: string;
  title: string;
  content: string;
  applicable_standards: string[];
  risk_factors: string[];
  control_measures: string[];
  created_at: string;
  updated_at: string;
}

/** 知识搜索结果类型 */
export interface KnowledgeSearchResult {
  items: KnowledgeItem[];
  total: number;
  page: number;
  page_size: number;
  highlights?: Record<string, string[]>;  // 高亮字段
}

/** 知识分类树类型 */
export interface KnowledgeCategoryTree {
  key: string;
  title: string;
  icon?: string;
  children?: KnowledgeCategoryTree[];
  count?: number;
}

/* ==================== 知识库API ==================== */

/** 获取知识分类树 */
export function getKnowledgeCategoryTree() {
  return request.get<unknown, KnowledgeCategoryTree[]>('/v1/knowledge/categories');
}

/** 获取知识列表 */
export function getKnowledgeList(params?: {
  category?: KnowledgeCategory;
  sub_category?: string;
  standard?: string;
  industry?: string;
  page?: number;
  page_size?: number;
}) {
  return request.get<unknown, KnowledgeSearchResult>('/v1/knowledge/list', { params });
}

/** 获取知识详情 */
export function getKnowledgeDetail(id: string) {
  return request.get<unknown, KnowledgeItem>(`/v1/knowledge/${id}`);
}

/** 搜索知识 */
export function searchKnowledge(params: {
  query: string;
  category?: KnowledgeCategory;
  standard?: string;
  industry?: string;
  page?: number;
  page_size?: number;
}) {
  return request.get<unknown, KnowledgeSearchResult>('/v1/knowledge/search', { params });
}

/** 获取标准条款列表 */
export function getStandardClauses(params?: {
  standard?: string;
  parent_clause?: string;
}) {
  return request.get<unknown, StandardClause[]>('/v1/knowledge/standard-clauses', { params });
}

/** 获取单个标准条款详情 */
export function getStandardClauseDetail(id: string) {
  return request.get<unknown, StandardClause>(`/v1/knowledge/standard-clauses/${id}`);
}

/** 按标准获取条款树 */
export function getStandardClauseTree(standard: string) {
  return request.get<unknown, KnowledgeCategoryTree[]>(`/v1/knowledge/standard/${standard}/tree`);
}

/** 获取行业知识列表 */
export function getIndustryKnowledge(params?: {
  industry_code?: string;
  category?: string;
  page?: number;
  page_size?: number;
}) {
  return request.get<unknown, {
    items: IndustryKnowledge[];
    total: number;
    page: number;
    page_size: number;
  }>('/v1/knowledge/industry', { params });
}

/** 获取单个行业知识详情 */
export function getIndustryKnowledgeDetail(id: string) {
  return request.get<unknown, IndustryKnowledge>(`/v1/knowledge/industry/${id}`);
}

/** 获取支持的标准列表 */
export function getSupportedStandardsList() {
  return request.get<unknown, Array<{
    code: string;
    name: string;
    full_name: string;
    total_clauses: number;
    description: string;
  }>>('/v1/knowledge/standards');
}

/** 获取行业列表 */
export function getIndustryList() {
  return request.get<unknown, Array<{
    code: string;
    name: string;
    category: string;
    description?: string;
  }>>('/v1/knowledge/industries');
}

/** 增加知识查看次数 */
export function incrementViewCount(id: string) {
  return request.post<unknown, { view_count: number }>(`/v1/knowledge/${id}/view`);
}

/** 获取相关知识推荐 */
export function getRelatedKnowledge(id: string, limit?: number) {
  return request.get<unknown, KnowledgeItem[]>(`/v1/knowledge/${id}/related`, {
    params: { limit: limit || 5 }
  });
}

/* ==================== 用户知识管理API ==================== */

/** 创建用户知识 */
export function createUserKnowledge(data: {
  title: string;
  category: string;
  content: string;
  tags?: string[];
  industry?: string;
}) {
  return request.post<unknown, KnowledgeItem>('/v1/knowledge/user', data);
}

/** 更新用户知识 */
export function updateUserKnowledge(id: string, data: Partial<KnowledgeItem>) {
  return request.put<unknown, KnowledgeItem>(`/v1/knowledge/user/${id}`, data);
}

/** 删除用户知识 */
export function deleteUserKnowledge(id: string) {
  return request.delete<unknown, { message: string }>(`/v1/knowledge/user/${id}`);
}

/** 获取用户知识列表 */
export function getUserKnowledgeList(params?: {
  page?: number;
  page_size?: number;
}) {
  return request.get<unknown, KnowledgeSearchResult>('/v1/knowledge/user/list', { params });
}
