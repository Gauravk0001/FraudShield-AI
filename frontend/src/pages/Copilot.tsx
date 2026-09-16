import React, { useState, useEffect } from 'react';
import { useOutletContext, useLocation } from 'react-router-dom';
import { Sparkles, Search } from 'lucide-react';
import { CopilotChat } from '../components/copilot/CopilotChat';
import type { User } from '../types';

export const CopilotPage: React.FC = () => {
  const { user } = useOutletContext<{ user: User | null }>();
  const location = useLocation();
  const stateTxId = (location.state as any)?.transactionId || '';

  const [targetTxId, setTargetTxId] = useState(stateTxId);
  const [activeTxId, setActiveTxId] = useState<string | undefined>(stateTxId || undefined);

  useEffect(() => {
    if (stateTxId) {
      setTargetTxId(stateTxId);
      setActiveTxId(stateTxId);
    }
  }, [stateTxId]);

  const handleSetContext = (e: React.FormEvent) => {
    e.preventDefault();
    if (targetTxId.trim()) {
      setActiveTxId(targetTxId.trim());
    }
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
              className="pl-9 pr-3 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-btn text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 w-56"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-1.5 text-xs font-semibold bg-slate-900 dark:bg-slate-800 text-white rounded-btn hover:bg-slate-800 dark:hover:bg-slate-700 transition-colors"
          >
            Load Context
          </button>
        </form>
      </div>

      {/* Main Chat Container */}
      <div className="flex-1 min-h-0">
        <CopilotChat transactionId={activeTxId} userRole={user?.role} />
      </div>
    </div>
  );
};

export default CopilotPage;
