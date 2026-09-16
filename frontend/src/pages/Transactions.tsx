import React, { useEffect, useState } from 'react';
import { Search, Filter, RefreshCw, X } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { RiskBadge } from '../components/ui/RiskBadge';
import { Button } from '../components/ui/Button';
import { apiRequest } from '../services/api';
import type { Transaction } from '../types';

export const Transactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');
  const [isLoading, setIsLoading] = useState(true);

  const fetchTransactions = async () => {
    setIsLoading(true);
    try {
      let endpoint = '/transactions?limit=100';
      if (riskFilter !== 'ALL') {
        endpoint += `&risk_level=${riskFilter}`;
      }
      const data = await apiRequest<Transaction[]>(endpoint);
      setTransactions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [riskFilter]);

  const filteredTransactions = transactions.filter((tx) => {
    const term = searchTerm.toLowerCase();
    return (
      tx.transaction_id.toLowerCase().includes(term) ||
      tx.customer_id.toLowerCase().includes(term) ||
      tx.merchant_id.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Transaction Intelligence</h2>
          <p className="text-xs text-slate-500 mt-0.5">Real-time evaluated transactions with ML probability & SHAP signals</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchTransactions} isLoading={isLoading}>
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Refresh
        </Button>
      </div>

      {/* Filter Bar */}
      <Card className="!p-4">
        <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search ID, customer, merchant..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 text-xs border border-slate-300 rounded-btn focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-xs text-slate-500 font-medium">Risk Filter:</span>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="text-xs border border-slate-300 rounded-btn px-2.5 py-1.5 bg-white font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Risk Levels</option>
              <option value="CRITICAL">CRITICAL Risk</option>
              <option value="HIGH">HIGH Risk</option>
              <option value="MEDIUM">MEDIUM Risk</option>
              <option value="LOW">LOW Risk</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Transactions Table */}
      <Card className="!p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Transaction ID</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Merchant</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Score</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredTransactions.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-10 text-slate-400">
                    No matching transactions found
                  </td>
                </tr>
              ) : (
                filteredTransactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-medium text-slate-900">{tx.transaction_id}</td>
                    <td className="py-3.5 px-4 text-slate-500">{new Date(tx.timestamp).toLocaleString()}</td>
                    <td className="py-3.5 px-4 text-slate-700">{tx.customer_id}</td>
                    <td className="py-3.5 px-4 text-slate-700">{tx.merchant_id}</td>
                    <td className="py-3.5 px-4 font-bold text-slate-900">${tx.amount.toLocaleString()}</td>
                    <td className="py-3.5 px-4">
                      {tx.risk_score ? (
                        <RiskBadge level={tx.risk_score.risk_level} />
                      ) : (
                        <span className="text-slate-400">N/A</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-bold text-slate-900">
                      {tx.risk_score ? Math.round(tx.risk_score.risk_score) : '-'} / 100
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Button variant="outline" size="sm" onClick={() => setSelectedTx(tx)}>
                        Inspect
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Transaction Detail & SHAP Explanation Drawer */}
      {selectedTx && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex justify-end">
          <div className="w-full max-w-xl bg-white h-full shadow-2xl overflow-y-auto flex flex-col p-6 border-l border-slate-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-200">
              <div>
                <span className="text-xs text-slate-500 font-mono">ID: {selectedTx.transaction_id}</span>
                <h3 className="text-lg font-bold text-slate-900 mt-0.5">Transaction Detail & SHAP Explanation</h3>
              </div>
              <button
                onClick={() => setSelectedTx(null)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-md"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="py-6 space-y-6 flex-1">
              {/* Risk Summary Header Card */}
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-card flex items-center justify-between">
                <div>
                  <span className="text-xs text-slate-500 font-medium block">Overall Risk Score</span>
                  <div className="text-3xl font-extrabold text-slate-900 mt-1">
                    {selectedTx.risk_score ? Math.round(selectedTx.risk_score.risk_score) : 0} <span className="text-sm font-normal text-slate-500">/ 100</span>
                  </div>
                </div>
                {selectedTx.risk_score && <RiskBadge level={selectedTx.risk_score.risk_level} className="text-sm px-3 py-1" />}
              </div>

              {/* Metadata Grid */}
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div className="p-3 bg-white border border-slate-200 rounded-btn">
                  <span className="text-slate-400 block mb-0.5">Amount & Currency</span>
                  <span className="font-bold text-slate-900 text-sm">${selectedTx.amount.toLocaleString()} {selectedTx.currency}</span>
                </div>
                <div className="p-3 bg-white border border-slate-200 rounded-btn">
                  <span className="text-slate-400 block mb-0.5">Transaction Type</span>
                  <span className="font-bold text-slate-900">{selectedTx.transaction_type}</span>
                </div>
                <div className="p-3 bg-white border border-slate-200 rounded-btn">
                  <span className="text-slate-400 block mb-0.5">Customer ID</span>
                  <span className="font-medium text-slate-900">{selectedTx.customer_id}</span>
                </div>
                <div className="p-3 bg-white border border-slate-200 rounded-btn">
                  <span className="text-slate-400 block mb-0.5">Merchant ID</span>
                  <span className="font-medium text-slate-900">{selectedTx.merchant_id}</span>
                </div>
              </div>

              {/* WHY WAS THIS FLAGGED? SHAP Breakdown */}
              <div>
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
                  Why Was This Flagged? (SHAP Feature Contributions)
                </h4>
                {selectedTx.risk_score?.explanation?.top_factors ? (
                  <div className="space-y-2">
                    {selectedTx.risk_score.explanation.top_factors.map((factor, idx) => (
                      <div key={idx} className="p-3 bg-red-50/60 border border-red-100 rounded-btn text-xs">
                        <div className="flex items-center justify-between font-semibold text-slate-900">
                          <span>{factor.explanation || factor.feature_name}</span>
                          <span className="text-rose-700 font-bold">+{factor.contribution}</span>
                        </div>
                        <span className="text-[11px] text-slate-500 block mt-1">Feature: {factor.feature_name} = {factor.feature_value}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-xs text-slate-400 italic">No SHAP explanation factors available</div>
                )}
              </div>
            </div>

            <div className="pt-4 border-t border-slate-200 flex gap-3">
              <Button variant="outline" className="flex-1" onClick={() => setSelectedTx(null)}>Close</Button>
              <Button variant="primary" className="flex-1" onClick={() => alert('Investigation workflow started for ' + selectedTx.transaction_id)}>
                Start Investigation
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
