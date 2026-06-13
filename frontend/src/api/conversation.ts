import { request } from './request';

export interface FollowUpQuestion {
  field: string;
  question: string;
  example?: string;
  reason?: string;
}

export interface ConversationResponse {
  sessionId: string;
  status: 'collecting' | 'complete';
  parsedInfo: Record<string, any>;
  missingFields: string[];
  followUpQuestions: FollowUpQuestion[];
  progressPercent: number;
  message: string;
}

export function startConversation(initialText: string, projectId?: string) {
  return request.post<unknown, ConversationResponse>('/v1/conversation/start', {
    initial_text: initialText,
    project_id: projectId,
  });
}

export function continueConversation(sessionId: string, answer: string) {
  return request.post<unknown, ConversationResponse>('/v1/conversation/continue', {
    session_id: sessionId,
    answer,
  });
}

export function getConversationStatus(sessionId: string) {
  return request.get<unknown, {
    sessionId: string;
    status: string;
    createdAt: string;
    lastUpdated: string;
    messageCount: number;
    currentInfo: Record<string, any>;
  }>(`/v1/conversation/${sessionId}/status`);
}

export function completeConversation(sessionId: string, projectId?: string) {
  return request.post<unknown, {
    message: string;
    sessionId: string;
    projectId: string;
    finalInfo: Record<string, any>;
    remainingMissing: string[];
  }>(`/v1/conversation/${sessionId}/complete`, { project_id: projectId });
}
