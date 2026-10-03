import React, { useState, useEffect } from 'react';
import { useOutletContext, useLocation, useSearchParams } from 'react-router-dom';
import { Sparkles, Search, X } from 'lucide-react';
import { CopilotChat } from '../components/copilot/CopilotChat';
import type { User } from '../types';

export const CopilotPage: React.FC = () => {
  const { user } = useOutletContext<{ user: User | null }>();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();

  // Extract from query params (?transactionId=..., ?tx=..., ?transaction_id=...) or route state
  const queryTxId = searchParams.get('transactionId') || searchParams.get('tx') || searchParams.get('transaction_id') || '';
  const queryInvId = searchParams.get('investigationId') || searchParams.get('inv') || '';
  const stateTxId = (location.state as any)?.transactionId || (location.state as any)?.txId || '';
  const stateInvId = (location.state as any)?.investigationId || '';

  const initialTxId = stateTxId || queryTxId || '';
  const initialInvId = stateInvId || queryInvId || '';

  const [targetTxId, setTargetTxId] = useState(initialTxId);
  const [activeTxId, setActiveTxId] = useState<string | undefined>(initialTxId || undefined);
  const [activeInvId, setActiveInvId] = useState<string | undefined>(initialInvId || undefined);

  useEffect(() => {
    const nextTxId = (location.state as any)?.transactionId || (location.state as any)?.txId || searchParams.get('transactionId') || searchParams.get('tx') || searchParams.get('transaction_id') || '';
    const nextInvId = (location.state as any)?.investigationId || searchParams.get('investigationId') || searchParams.get('inv') || '';
    if (nextTxId) {
      setTargetTxId(nextTxId);
      setActiveTxId(nextTxId);
    }
    if (nextInvId) {
      setActiveInvId(nextInvId);
    }
  }, [location.state, searchParams]);

  const handleSetContext = (e: React.FormEvent) => {
    e.preventDefault();
    const clean = targetTxId.trim();
    if (clean) {
      setActiveTxId(clean);
      setSearchParams(prev => {
        const next = new URLSearchParams(prev);
        next.set('transactionId', clean);
        return next;
      });
    }
  };

  const handleClearContext = () => {
    setTargetTxId('');
    setActiveTxId(undefined);
    setActiveInvId(undefined);
    setSearchParams(prev => {
      const next = new URLSearchParams(prev);
      next.delete('transactionId');
      next.delete('tx');
      next.delete('transaction_id');
      next.delete('investigationId');
      next.delete('inv');
      return next;
    });
  };

  const isRiskManager = user?.role === 'RISK_MANAGER';

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)] flex flex-col">
      {/* Top Page Header & Context Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 flex-shrink-0">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            {isRiskManager ? 'Risk Intelligence Copilot' : 'Gemini Investigation Copilot'}
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {isRiskManager
              ? 'AI assistant for portfolio risk distribution analysis, drift detection, and threshold sensitivity insights.'
              : 'Real-time AI evidence summarization and investigation decision-support assistant.'}
          </p>
        </div>

        <form onSubmit={handleSetContext} className="flex items-center space-x-2">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={targetTxId}
              onChange={e => setTargetTxId(e.target.value)}
              placeholder="Enter Transaction ID..."
              className="pl-9 pr-8 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-btn text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 w-60"
            />
            {targetTxId && (
              <button
                type="button"
                onClick={handleClearContext}
                className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                title="Clear Context"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
          <button
            type="submit"
            className="px-3 py-1.5 text-xs font-semibold bg-slate-900 dark:bg-slate-800 text-white rounded-btn hover:bg-slate-800 dark:hover:bg-slate-700 transition-colors shadow-xs"
          >
            Load Context
          </button>
        </form>
      </div>

      {/* Main Chat Container */}
      <div className="flex-1 min-h-0">
        <CopilotChat
          transactionId={activeTxId}
          investigationId={activeInvId}
          userRole={user?.role}
          onClearContext={activeTxId ? handleClearContext : undefined}
        />
      </div>
    </div>
  );
};

export default CopilotPage;
