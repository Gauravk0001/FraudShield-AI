import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, Send, Bot, User as UserIcon, RefreshCw, AlertTriangle } from 'lucide-react';
import { copilotApi } from '../../services/copilotApi';
import type { ChatMessage } from '../../services/copilotApi';
import { Button } from '../ui/Button';
import type { UserRole } from '../../types';

interface CopilotChatProps {
  investigationId?: string;
  transactionId?: string;
  userRole?: UserRole;
}

export const CopilotChat: React.FC<CopilotChatProps> = ({ investigationId, transactionId, userRole = 'FRAUD_ANALYST' }) => {
  const getRoleFollowups = (role: UserRole) => {
    if (role === 'RISK_MANAGER') {
      return [
        'Summarize current fraud risk trends',
        'Explain alert volume changes',
        'Summarize investigation backlog',
        'Explain model performance metrics'
      ];
    }
    return [
      'Why was this transaction flagged?',
      'Summarize evidence',
      'What should I investigate next?',
      'Explain SHAP risk factors'
    ];
  };

  const getRoleGreeting = (role: UserRole) => {
    if (role === 'RISK_MANAGER') {
      return 'Hello Risk Manager. I am FraudShield Copilot. Ask me about overall fraud portfolio trends, model calibration metrics, or backlog aging.';
    }
    return 'Hello Analyst. I am FraudShield Copilot. Select a suggested prompt or ask me any question regarding transaction evidence, SHAP risk factors, or investigation recommendations.';
  };

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: getRoleGreeting(userRole)
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestedFollowups, setSuggestedFollowups] = useState<string[]>(getRoleFollowups(userRole));
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
    <div className="flex flex-col h-full bg-white dark:bg-slate-900 rounded-card border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
      {/* Copilot Header */}
      <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-xs">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-sm">Gemini Fraud Copilot</h3>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                AI Assistance
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">Sanitized backend evidence context • Human decision mandatory</p>
          </div>
        </div>

        {transactionId && (
          <span className="text-xs font-mono bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2.5 py-1 rounded-md">
            Tx: {transactionId}
          </span>
        )}
      </div>

      {/* Safety & Responsibility Disclaimer Banner */}
      <div className="px-4 py-2.5 bg-amber-50 dark:bg-amber-950/30 border-b border-amber-200 dark:border-amber-800/60 space-y-1.5 text-xs text-amber-900 dark:text-amber-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 flex-shrink-0" />
            <span className="font-bold">Decision Authority Boundary:</span>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-bold">
            <span className="px-1.5 py-0.5 bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300 rounded border border-blue-200 dark:border-blue-800">1. MODEL EVIDENCE</span>
            <span className="px-1.5 py-0.5 bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 rounded border border-amber-200 dark:border-amber-800">2. AI INTERPRETATION</span>
            <span className="px-1.5 py-0.5 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 rounded border border-emerald-200 dark:border-emerald-800">3. HUMAN DECISION</span>
          </div>
        </div>
        <p className="text-[11px] text-amber-800 dark:text-amber-300">
          Copilot provides evidence interpretation and assistant suggestions only. Final fraud decision authority rests strictly with authorized human personnel.
        </p>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 p-5 overflow-y-auto space-y-4 bg-slate-50/40 dark:bg-slate-950/40 min-h-[320px]">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex items-start space-x-3 ${
              msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-white ${
                msg.role === 'user' ? 'bg-slate-700 dark:bg-slate-800' : 'bg-blue-600'
              }`}
            >
              {msg.role === 'user' ? <UserIcon className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div
              className={`max-w-[80%] rounded-card px-4 py-3 text-xs shadow-xs ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-none'
                  : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 rounded-tl-none'
              }`}
            >
              <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
              <div
                className={`text-[10px] mt-1.5 text-right ${
                  msg.role === 'user' ? 'text-blue-100' : 'text-slate-400 dark:text-slate-500'
                }`}
              >
                {msg.role === 'user' ? 'Analyst' : 'Copilot AI'}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-3 text-slate-500 dark:text-slate-400 text-xs italic">
            <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center animate-pulse">
              <Sparkles className="w-4 h-4" />
            </div>
            <span>Analyzing evidence context...</span>
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-lg text-xs text-red-700 dark:text-red-300 flex items-center justify-between">
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
        <div className="px-5 py-2.5 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800 flex items-center space-x-2 overflow-x-auto">
          <span className="text-xs text-slate-400 dark:text-slate-500 font-medium whitespace-nowrap">Suggested:</span>
          {suggestedFollowups.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(chip)}
              className="text-xs font-medium text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-blue-50 dark:hover:bg-blue-950/50 hover:text-blue-600 dark:hover:text-blue-400 border border-slate-200 dark:border-slate-700 px-3 py-1 rounded-full whitespace-nowrap transition-colors"
            >
              {chip}
            </button>
          ))}
        </div>
      )}

      {/* Input Box */}
      <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
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
            className="flex-1 px-4 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-btn focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-900 dark:text-slate-100"
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
