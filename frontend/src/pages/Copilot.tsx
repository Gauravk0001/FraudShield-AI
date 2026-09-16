import React, { useState } from 'react';
import { Sparkles, Search } from 'lucide-react';
import { CopilotChat } from '../components/copilot/CopilotChat';

export const CopilotPage: React.FC = () => {
  const [targetTxId, setTargetTxId] = useState('');
  const [activeTxId, setActiveTxId] = useState<string | undefined>(undefined);

  const handleSetContext = (e: React.FormEvent) => {
    e.preventDefault();
    if (targetTxId.trim()) {
      setActiveTxId(targetTxId.trim());
    }
  };

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)] flex flex-col">
      {/* Top Page Header & Context Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 flex-shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-7 h-7 text-blue-600" />
            Gemini Investigation Copilot
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time AI evidence summarization and investigation decision-support assistant.
          </p>
        </div>

        <form onSubmit={handleSetContext} className="flex items-center space-x-2">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              value={targetTxId}
              onChange={e => setTargetTxId(e.target.value)}
              placeholder="Enter Transaction ID..."
              className="pl-9 pr-3 py-2 text-sm bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-56"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-2 text-sm font-medium bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            Load Context
          </button>
        </form>
      </div>

      {/* Main Chat Container */}
      <div className="flex-1 min-h-0">
        <CopilotChat transactionId={activeTxId} />
      </div>
    </div>
  );
};

export default CopilotPage;
