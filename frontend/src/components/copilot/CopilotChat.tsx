import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, Send, Bot, User as UserIcon, RefreshCw, AlertTriangle } from 'lucide-react';
import { copilotApi } from '../../services/copilotApi';
import type { ChatMessage } from '../../services/copilotApi';
import { Button } from '../ui/Button';

interface CopilotChatProps {
  investigationId?: string;
  transactionId?: string;
}

export const CopilotChat: React.FC<CopilotChatProps> = ({ investigationId, transactionId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello Analyst. I am FraudShield Copilot. Select a suggested prompt or ask me any question regarding transaction evidence, SHAP risk factors, or investigation recommendations.'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestedFollowups, setSuggestedFollowups] = useState<string[]>([
    'Explain this alert',
    'Summarize evidence',
    'What should I investigate next?',
    'Show unusual behavior'
  ]);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (messageToSend?: string) => {
    const text = messageToSend || inputMessage.trim();
    if (!text || loading) return;

    setError(null);
    setInputMessage('');

    const newMessages: ChatMessage[] = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const res = await copilotApi.chat({
        investigation_id: investigationId,
        transaction_id: transactionId,
        message: text,
        history: newMessages.slice(-6)
      });

      setMessages(prev => [...prev, { role: 'assistant', content: res.response }]);
      if (res.suggested_followups && res.suggested_followups.length > 0) {
        setSuggestedFollowups(res.suggested_followups);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to communicate with Copilot API');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Copilot Header */}
      <div className="px-5 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-semibold text-slate-900 text-sm">Gemini Fraud Copilot</h3>
              <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
                AI Assistance
              </span>
            </div>
            <p className="text-xs text-slate-500">Sanitized backend evidence context • Human decision mandatory</p>
          </div>
        </div>

        {transactionId && (
          <span className="text-xs font-mono bg-slate-200 text-slate-700 px-2.5 py-1 rounded-md">
            Tx: {transactionId}
          </span>
        )}
      </div>

      {/* Safety Disclaimer Banner */}
      <div className="px-4 py-2 bg-amber-50 border-b border-amber-200 flex items-center space-x-2 text-xs text-amber-800">
        <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
        <span>
          <strong>AI Safety Boundary:</strong> Copilot provides evidence decision-support only. Final fraud decision authority belongs to the human analyst.
        </span>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 p-5 overflow-y-auto space-y-4 bg-slate-50/50 min-h-[320px]">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex items-start space-x-3 ${
              msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-white ${
                msg.role === 'user' ? 'bg-slate-700' : 'bg-blue-600'
              }`}
            >
              {msg.role === 'user' ? <UserIcon className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div
              className={`max-w-[80%] rounded-xl px-4 py-3 text-sm shadow-sm ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-none'
                  : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none'
              }`}
            >
              <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
              <div
                className={`text-[10px] mt-1.5 text-right ${
                  msg.role === 'user' ? 'text-blue-100' : 'text-slate-400'
                }`}
              >
                {msg.role === 'user' ? 'Analyst' : 'Copilot AI'}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-3 text-slate-500 text-xs italic">
            <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center animate-pulse">
              <Sparkles className="w-4 h-4" />
            </div>
            <span>Analyzing evidence context...</span>
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center justify-between">
            <span>{error}</span>
            <Button size="sm" variant="secondary" onClick={() => handleSend()}>
              <RefreshCw className="w-3 h-3 mr-1" /> Retry
            </Button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Followups */}
      {suggestedFollowups.length > 0 && !loading && (
        <div className="px-5 py-2.5 bg-white border-t border-slate-100 flex items-center space-x-2 overflow-x-auto">
          <span className="text-xs text-slate-400 font-medium whitespace-nowrap">Suggested:</span>
          {suggestedFollowups.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(chip)}
              className="text-xs font-medium text-slate-700 bg-slate-100 hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 border border-slate-200 px-3 py-1 rounded-full whitespace-nowrap transition-colors"
            >
              {chip}
            </button>
          ))}
        </div>
      )}

      {/* Input Box */}
      <div className="p-4 bg-white border-t border-slate-200">
        <form
          onSubmit={e => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center space-x-2"
        >
          <input
            type="text"
            value={inputMessage}
            onChange={e => setInputMessage(e.target.value)}
            placeholder="Ask Copilot about risk signals, SHAP values, or resolution guidance..."
            className="flex-1 px-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white text-slate-900"
            disabled={loading}
          />
          <Button type="submit" disabled={loading || !inputMessage.trim()}>
            <Send className="w-4 h-4 mr-1" /> Send
          </Button>
        </form>
      </div>
    </div>
  );
};
