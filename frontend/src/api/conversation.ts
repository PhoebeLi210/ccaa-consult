import { request } from './request';

export interface FollowUpQuestion {
  field: string;
  question: string;
  example?: string;
  reason?: string;
}

export interface ConversationResponse {
  session_id: string;
  status: 'collecting' | 'complete';
  parsed_info: Record<string, any>;
  missing_fields: string[];
  follow_up_questions: FollowUpQuestion[];
  progress_percent: number;
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

export function getConversationStatus(session_id: string) {
  return request.get<unknown, {
    session_id: string;
    status: string;
    created_at: string;
    last_updated: string;
    message_count: number;
    current_info: Record<string, any>;
  }>(`/v1/conversation/${session_id}/status`);
}

export function completeConversation(session_id: string, projectId?: string) {
  return request.post<unknown, {
    message: string;
    session_id: string;
    project_id: string;
    final_info: Record<string, any>;
    remaining_missing: string[];
  }>(`/v1/conversation/${session_id}/complete`, { project_id: projectId });
}
