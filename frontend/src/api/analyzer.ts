import { request } from './request';

export interface CoverageAnalysisResponse {
  projectId: string;
  projectName: string;
  standards: string[];
  summary: {
    totalClauses: number;
    covered: number;
    partial: number;
    missing: number;
    coverageRate: number;
  };
  clauses: Array<{
    clause: string;
    title: string;
    status: 'covered' | 'partial' | 'missing';
    relatedDocuments: string[];
  }>;
  suggestions: string[];
}

export interface QuickCoverageResponse {
  projectId: string;
  standard: string;
  totalClauses: number;
  covered: number;
  partial: number;
  missing: number;
  coverageRate: number;
  documentCount: number;
}

export interface EnvironmentalReportResponse {
  companyName: string;
  aspectsCount: number;
  significantAspectsCount: number;
  complianceRate: number;
  environmentalAspects: Array<{
    activity: string;
    aspect: string;
    impact: string;
    significance: string;
  }>;
  generatedDocuments?: Record<string, any>;
}

export interface SafetyAssessmentResponse {
  companyName: string;
  hazardsCount: number;
  significantHazardsCount: number;
  incidentsCount: number;
  complianceRate: number;
  hazards: Array<{
    activity: string;
    hazardSource: string;
    riskDescription: string;
    riskScore: number;
    riskLevel: string;
  }>;
  generatedDocuments?: Record<string, any>;
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
      totalClauses: number;
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
