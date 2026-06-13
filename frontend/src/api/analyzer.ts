import { request } from './request';

export interface CoverageAnalysisResponse {
  project_id: string;
  project_name: string;
  standards: string[];
  summary: {
    total_clauses: number;
    covered: number;
    partial: number;
    missing: number;
    coverage_rate: number;
  };
  clauses: Array<{
    clause: string;
    title: string;
    status: 'covered' | 'partial' | 'missing';
    related_documents: string[];
  }>;
  suggestions: string[];
}

export interface QuickCoverageResponse {
  project_id: string;
  standard: string;
  total_clauses: number;
  covered: number;
  partial: number;
  missing: number;
  coverage_rate: number;
  document_count: number;
}

export interface EnvironmentalReportResponse {
  company_name: string;
  aspects_count: number;
  significant_aspects_count: number;
  compliance_rate: number;
  environmental_aspects: Array<{
    activity: string;
    aspect: string;
    impact: string;
    significance: string;
  }>;
  generated_documents?: Record<string, any>;
}

export interface SafetyAssessmentResponse {
  company_name: string;
  hazards_count: number;
  significant_hazards_count: number;
  incidents_count: number;
  compliance_rate: number;
  hazards: Array<{
    activity: string;
    hazard_source: string;
    risk_description: string;
    risk_score: number;
    risk_level: string;
  }>;
  generated_documents?: Record<string, any>;
}

export function analyzeCoverage(projectId: string, standards?: string[]) {
  return request.post<unknown, CoverageAnalysisResponse>(`/v1/analyzer/coverage/${projectId}`, {
    standards,
  });
}

export function quickCoverageCheck(projectId: string, standard: string = 'ISO9001') {
  return request.post<unknown, QuickCoverageResponse>('/v1/analyzer/coverage/quick', {
    project_id: projectId,
    standard,
  });
}

export function getSupportedStandards() {
  return request.get<unknown, {
    standards: Array<{
      code: string;
      name: string;
      total_clauses: number;
      description: string;
    }>;
  }>('/v1/analyzer/standards');
}

export function analyzeEnvironmentalReport(reportText: string, generateDocuments: boolean = true) {
  return request.post<unknown, EnvironmentalReportResponse>('/v1/analyzer/environmental-report', {
    report_text: reportText,
    generate_documents: generateDocuments,
  });
}

export function analyzeSafetyAssessment(reportText: string, generateDocuments: boolean = true) {
  return request.post<unknown, SafetyAssessmentResponse>('/v1/analyzer/safety-assessment', {
    report_text: reportText,
    generate_documents: generateDocuments,
  });
}
