import { request } from './request';

/** Flowchart节点类型 */
export type NodeType = 'start' | 'end' | 'process' | 'decision' | 'document';

/** Flowchart节点 */
export interface FlowchartNode {
  id: string;
  type: NodeType;
  label: string;
  description?: string;
  x: number;
  y: number;
  // 其它可选字段保留，使用索引签名
  [key: string]: any;
}

/** Flowchart连线 */
export interface FlowchartEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  [key: string]: any;
}

/** Flowchart完整数据（仅节点与连线） */
export interface FlowchartData {
  nodes: FlowchartNode[];
  edges: FlowchartEdge[];
}

/** Flowchart列表项 */
export interface FlowchartInfo {
  id: string;
  project_id?: string;
  name: string;
  description?: string;
  nodes?: FlowchartNode[];
  edges?: FlowchartEdge[];
  status: string;
  version: number;
  created_at: string;
  updated_at: string;
  nodeCount?: number; // UI展示用
  edgeCount?: number;
}

/** 创建流程图请求 */
export interface CreateFlowchartRequest {
  project_id: string;
  name: string;
  description?: string;
  nodes?: FlowchartNode[];
  edges?: FlowchartEdge[];
}

/** 获取项目下的流程图列表（可选 projectId） */
export const getFlowchartList = async (projectId?: string, status?: string) => {
  const path = projectId ? `/v1/flowcharts/project/${projectId}` : '/v1/flowcharts/project/';
  const params: any = {};
  if (status) params.status = status;
  return request.get<unknown, FlowchartInfo[]>(path, { params });
};

/** 创建流程图 */
export const createFlowchart = (data: CreateFlowchartRequest) => {
  return request.post<unknown, FlowchartInfo>('/v1/flowcharts', data);
};

/** 删除流程图 */
export const deleteFlowchart = (id: string) => {
  return request.delete<unknown, void>(`/v1/flowcharts/${id}`);
};

/** 获取流程图详情 */
export const getFlowchartDetail = (id: string) => {
  return request.get<unknown, FlowchartInfo>(`/v1/flowcharts/${id}`);
};

/** 更新流程图（仅支持更新节点/连线） */
export const updateFlowchart = (id: string, data: Partial<FlowchartData>) => {
  return request.put<unknown, FlowchartInfo>(`/v1/flowcharts/${id}`, data);
};

/** 获取模板列表 */
export const getFlowchartTemplates = async (category?: string, include_system = true) => {
  const params: any = { include_system };
  if (category) params.category = category;
  return request.get<unknown, any>('/v1/flowcharts/templates/list', { params });
};

/** 应用模板创建流程图 */
export const applyTemplate = (templateId: string, data: { project_id: string; name?: string; description?: string }) => {
  return request.post<unknown, FlowchartInfo>(`/v1/flowcharts/templates/${templateId}/apply`, data);
};
