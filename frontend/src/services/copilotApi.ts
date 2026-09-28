import { apiRequest, getStoredToken } from './api';

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
  },

  chatStream: async (
    payload: CopilotChatRequest,
    onChunk: (text: string) => void,
    onDone: (suggestedFollowups: string[]) => void,
    onError: (err: any) => void
  ): Promise<void> => {
    const token = getStoredToken();
    try {
      const response = await fetch('/api/v1/copilot/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Stream request failed with status ${response.status}`);
      }

      if (!response.body) {
        throw new Error('ReadableStream not supported');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            try {
              const data = JSON.parse(trimmed.slice(6));
              if (data.type === 'chunk' && data.text) {
                onChunk(data.text);
              } else if (data.type === 'done') {
                onDone(data.suggested_followups || []);
              }
            } catch {
              // Ignore partial parse edge case
            }
          }
        }
      }
    } catch (err) {
      onError(err);
    }
  }
};
