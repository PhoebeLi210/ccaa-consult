/**
 * 知识库相关 API
 */
import request from './index';

/* ==================== 类型定义 ==================== */

/** 行业数据状态 */
export type IndustryDataStatus = 'complete' | 'partial' | 'template' | 'empty';

/** 行业信息 */
export interface KnowledgeIndustry {
  code: string;
  name: string;
  name_en?: string;
  description?: string;
  data_status: IndustryDataStatus;
  keywords?: string[];
  key_processes?: string[];
  sub_categories_count?: number;
  audit_points_count?: number;
  typical_ncs_count?: number;
  checklist_count?: number;
  regulations_count?: number;
  priority_clauses?: string[];
}

/** 审核要点 */
export interface AuditPoint {
  clause: string;
  title: string;
  description: string;
  risk_level: string;
  audit_focus: string;
}

/** 典型不符合项 */
export interface TypicalNC {
  clause: string;
  nc_type: string;
  description: string;
  frequency: string;
  root_cause: string;
  corrective_action: string;
}

/** 检查清单项 */
export interface ChecklistItem {
  clause: string;
  department: string;
  check_item: string;
  evidence: string;
  method: string;
  risk_level: string;
}

/** 法规要求 */
export interface Regulation {
  code: string;
  name: string;
  scope: string;
  effective_date: string;
  key_requirements?: string[];
}

/** 公司案例 */
export interface CompanyCase {
  company_name: string;
  audit_type: string;
  severity: string;
  findings: string;
  date: string;
}

/** 行业上下文（详情页完整数据） */
export interface IndustryContext {
  industry: KnowledgeIndustry;
  audit_points: AuditPoint[];
  typical_ncs: TypicalNC[];
  checklist: ChecklistItem[];
  regulations: Regulation[];
  company_cases?: CompanyCase[];
}

/** 行业匹配请求 */
export interface MatchIndustryRequest {
  company_name?: string;
  business_scope?: string;
  industry_hint?: string;
}

/** 行业匹配结果 */
export interface MatchIndustryResult {
  code: string;
  name: string;
  confidence: number;
  reasons: string[];
}

/** 条款知识查询参数 */
export interface ClauseKnowledgeParams {
  standard?: string;
  clause?: string;
  keyword?: string;
}

/** 条款知识 */
export interface ClauseKnowledge {
  standard: string;
  clause: string;
  title: string;
  content: string;
  interpretation?: string;
  audit_guidance?: string;
  common_ncs?: string[];
}

/* ==================== API 接口 ==================== */

/** 获取行业列表 */
export function getIndustries() {
  return request.get<unknown, KnowledgeIndustry[]>('/v1/knowledge/industries');
}

/** 获取行业详情 */
export function getIndustryDetail(code: string) {
  return request.get<unknown, KnowledgeIndustry>(`/v1/knowledge/industries/${code}`);
}

/** 获取行业文档生成上下文 */
export function getIndustryContext(code: string) {
  return request.get<unknown, IndustryContext>(`/v1/knowledge/industries/${code}/context`);
}

/** 匹配行业 */
export function matchIndustry(companyInfo: MatchIndustryRequest) {
  return request.post<unknown, MatchIndustryResult[]>('/v1/knowledge/match-industry', companyInfo);
}

/** 查询条款知识 */
export function getClauseKnowledge(params: ClauseKnowledgeParams) {
  return request.get<unknown, ClauseKnowledge[]>('/v1/knowledge/clauses', { params });
}
