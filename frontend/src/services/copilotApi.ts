import { apiRequest } from './api';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface CopilotChatRequest {
  investigation_id?: string;
  transaction_id?: string;
  message: string;
  history?: ChatMessage[];
}

export interface CopilotChatResponse {
  response: string;
  evidence_summary: Record<string, any>;
  disclaimer: string;
  suggested_followups: string[];
}

export const copilotApi = {
  chat: async (payload: CopilotChatRequest): Promise<CopilotChatResponse> => {
    return apiRequest<CopilotChatResponse>('/copilot/chat', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }
};
