import { useState, useCallback } from 'react';
import {
  getProjectList,
  getProjectDetail,
  createProject,
  updateProject,
  deleteProject,
  type ProjectInfo,
  type ParseResult,
  parseNaturalLanguage,
  generateDocuments,
  getProjectDocuments,
  confirmDocument,
  batchConfirmDocuments,
  type DocumentInfo,
} from '@/api';

/** 项目管理Hook返回值 */
interface UseProjectReturn {
  /** 项目列表 */
  projects: ProjectInfo[];
  /** 当前项目详情 */
  currentProject: ProjectInfo | null;
  /** 当前项目文档列表 */
  documents: DocumentInfo[];
  /** 加载状态 */
  loading: boolean;
  /** 错误信息 */
  error: string | null;
  /** 获取项目列表 */
  fetchProjects: (keyword?: string) => Promise<void>;
  /** 获取项目详情 */
  fetchProjectDetail: (id: string) => Promise<void>;
  /** 创建新项目 */
  createNewProject: (data: Partial<ProjectInfo>) => Promise<ProjectInfo>;
  /** 更新项目 */
  editProject: (id: string, data: Partial<ProjectInfo>) => Promise<void>;
  /** 删除项目 */
  removeProject: (id: string) => Promise<void>;
  /** AI自然语言解析 */
  parseText: (text: string) => Promise<ParseResult>;
  /** 生成项目文档 */
  generateProjectDocuments: (projectId: string) => Promise<DocumentInfo[]>;
  /** 获取项目文档 */
  fetchDocuments: (projectId: string) => Promise<void>;
  /** 确认单个文档 */
  confirmSingleDocument: (documentId: string) => Promise<void>;
  /** 批量确认文档 */
  confirmMultipleDocuments: (documentIds: string[]) => Promise<void>;
}

/**
 * 项目管理Hook
 * 封装项目相关的所有API操作和状态管理
 */
export function useProject(): UseProjectReturn {
  const [projects, setProjects] = useState<ProjectInfo[]>([]);
  const [currentProject, setCurrentProject] = useState<ProjectInfo | null>(null);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** 获取项目列表 */
  const fetchProjects = useCallback(async (keyword?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getProjectList({ keyword });
      setProjects(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取项目列表失败');
    } finally {
      setLoading(false);
    }
  }, []);

  /** 获取项目详情 */
  const fetchProjectDetail = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getProjectDetail(id);
      setCurrentProject(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取项目详情失败');
    } finally {
      setLoading(false);
    }
  }, []);

  /** 创建新项目 */
  const createNewProject = useCallback(async (data: Partial<ProjectInfo>) => {
    setLoading(true);
    setError(null);
    try {
      const newProject = await createProject(data);
      setProjects((prev) => [newProject, ...prev]);
      return newProject;
    } catch (err) {
      const msg = err instanceof Error ? err.message : '创建项目失败';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  /** 更新项目 */
  const editProject = useCallback(async (id: string, data: Partial<ProjectInfo>) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await updateProject(id, data);
      setCurrentProject(updated);
      setProjects((prev) =>
        prev.map((p) => (p.id === id ? updated : p)),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : '更新项目失败');
    } finally {
      setLoading(false);
    }
  }, []);

  /** 删除项目 */
  const removeProject = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      await deleteProject(id);
      setProjects((prev) => prev.filter((p) => p.id !== id));
      if (currentProject?.id === id) {
        setCurrentProject(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除项目失败');
    } finally {
      setLoading(false);
    }
  }, [currentProject]);

  /** AI自然语言解析 */
  const parseText = useCallback(async (text: string) => {
    setError(null);
    try {
      const result = await parseNaturalLanguage(text);
      return result;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'AI解析失败';
      setError(msg);
      throw new Error(msg);
    }
  }, []);

  /** 生成项目文档 */
  const generateProjectDocuments = useCallback(async (projectId: string) => {
    setLoading(true);
    setError(null);
    try {
      const docs = await generateDocuments(projectId);
      setDocuments(docs);
      return docs;
    } catch (err) {
      const msg = err instanceof Error ? err.message : '生成文档失败';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  /** 获取项目文档列表 */
  const fetchDocuments = useCallback(async (projectId: string) => {
    setLoading(true);
    setError(null);
    try {
      const docs = await getProjectDocuments(projectId);
      setDocuments(Array.isArray(docs) ? docs : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取文档列表失败');
    } finally {
      setLoading(false);
    }
  }, []);

  /** 确认单个文档 */
  const confirmSingleDocument = useCallback(async (documentId: string) => {
    try {
      const updated = await confirmDocument(documentId);
      setDocuments((prev) =>
        prev.map((d) => (d.id === documentId ? updated : d)),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : '确认文档失败');
    }
  }, []);

  /** 批量确认文档 */
  const confirmMultipleDocuments = useCallback(async (documentIds: string[]) => {
    try {
      await batchConfirmDocuments(documentIds);
      setDocuments((prev) =>
        prev.map((d) =>
          documentIds.includes(d.id) ? { ...d, status: 'confirmed' as const } : d,
        ),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : '批量确认文档失败');
    }
  }, []);

  return {
    projects,
    currentProject,
    documents,
    loading,
    error,
    fetchProjects,
    fetchProjectDetail,
    createNewProject,
    editProject,
    removeProject,
    parseText,
    generateProjectDocuments,
    fetchDocuments,
    confirmSingleDocument,
    confirmMultipleDocuments,
  };
}

export default useProject;
