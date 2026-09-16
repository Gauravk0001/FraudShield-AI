import React from 'react';
import { Eye, ShieldCheck, Activity } from 'lucide-react';
import { Card } from '../ui/Card';
import { RiskBadge } from '../ui/RiskBadge';
import type { DashboardStats, Transaction } from '../../types';

interface ViewerOverviewProps {
  stats: DashboardStats | null;
  recentHighRisk: Transaction[];
  onRefresh: () => void;
  isLoading: boolean;
}

export const ViewerOverview: React.FC<ViewerOverviewProps> = ({
  stats,
  recentHighRisk,
}) => {
  return (
    <div className="space-y-6">
      {/* Viewer Header */}
      <div className="flex items-center justify-between bg-slate-900 border border-slate-800 p-6 rounded-card text-white shadow-md">
        <div>
          <div className="flex items-center gap-2">
            <Eye className="w-6 h-6 text-slate-400" />
            <h2 className="text-xl font-bold tracking-tight">Read-Only Operational View</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Read-only monitoring of live transaction evaluation metrics and platform activity.
          </p>
        </div>
      </div>

      {/* Viewer KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="border-l-4 border-l-slate-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Total Evaluated</span>
            <Activity className="w-5 h-5 text-slate-600 dark:text-slate-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats?.total_transactions.toLocaleString() || '0'}</span>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Transactions</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-rose-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">High Risk Count</span>
            <ShieldCheck className="w-5 h-5 text-rose-600 dark:text-rose-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-rose-600 dark:text-rose-400">{stats?.high_risk_transactions.toLocaleString() || '0'}</span>
            <span className="text-xs text-rose-600 dark:text-rose-400 font-semibold">{stats?.fraud_rate_percentage}% Rate</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-blue-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Avg Engine Latency</span>
            <Activity className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats?.avg_latency_ms || 42} ms</span>
            <span className="text-xs text-blue-600 dark:text-blue-400 font-medium">Real-Time Scoring</span>
          </div>
        </Card>
      </div>

      {/* Transactions Feed (Read Only) */}
      <Card title="Live Ingested Transactions" subtitle="Read-only view of transaction stream">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Transaction ID</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Risk Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {recentHighRisk.length === 0 ? (
                <tr><td colSpan={5} className="text-center py-6 text-slate-400 dark:text-slate-500">No transactions recorded</td></tr>
              ) : (
                recentHighRisk.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-slate-900 dark:text-slate-100">{tx.transaction_id}</td>
                    <td className="py-3 px-4 text-slate-700 dark:text-slate-300">{tx.customer_id}</td>
                    <td className="py-3 px-4 font-bold text-slate-900 dark:text-slate-100">${tx.amount.toLocaleString()}</td>
                    <td className="py-3 px-4">
                      {tx.risk_score ? <RiskBadge level={tx.risk_score.risk_level} /> : 'N/A'}
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-900 dark:text-slate-100">
                      {tx.risk_score ? Math.round(tx.risk_score.risk_score) : '-'} / 100
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
