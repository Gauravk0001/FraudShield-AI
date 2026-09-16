import React from 'react';
import { ShieldCheck, Activity, FileText, Sliders, ArrowUpRight } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import type { DashboardStats, Transaction } from '../../types';

interface AdminOverviewProps {
  stats: DashboardStats | null;
  recentHighRisk: Transaction[];
  onRefresh: () => void;
  isLoading: boolean;
}

export const AdminOverview: React.FC<AdminOverviewProps> = ({
  stats,
  recentHighRisk,
  onRefresh,
  isLoading,
}) => {
  return (
    <div className="space-y-6">
      {/* Admin Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-emerald-50 via-slate-50 to-teal-50 dark:from-emerald-950 dark:via-slate-900 dark:to-slate-950 border border-emerald-200 dark:border-slate-800 p-6 rounded-card text-slate-900 dark:text-white shadow-xs transition-colors">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            <h2 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">Platform Administration & System Health</h2>
          </div>
          <p className="text-xs text-slate-600 dark:text-emerald-200 mt-1">
            Global system management, immutable audit log monitoring, and platform configuration control.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={onRefresh} isLoading={isLoading}>
            Refresh Platform Stats
          </Button>
          <a
            href="/settings"
            className="inline-flex items-center gap-1 text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1.5 rounded-btn transition-colors"
          >
            <Sliders className="w-3.5 h-3.5" /> Platform Settings
          </a>
        </div>
      </div>

      {/* Admin KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-emerald-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Total System Volume</span>
            <Activity className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats?.total_transactions.toLocaleString() || '0'}</span>
            <span className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">Evaluated</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-rose-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">High Risk Count</span>
            <Activity className="w-5 h-5 text-rose-600 dark:text-rose-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-rose-600 dark:text-rose-400">{stats?.high_risk_transactions.toLocaleString() || '0'}</span>
            <span className="text-xs text-rose-600 dark:text-rose-400 font-semibold">{stats?.fraud_rate_percentage}% Rate</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-blue-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Active Alerts</span>
            <Activity className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats?.active_alerts.toLocaleString() || '0'}</span>
            <span className="text-xs text-blue-600 dark:text-blue-400 font-medium">In Pipeline</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-purple-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Audit Security</span>
            <FileText className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900 dark:text-slate-100">Protected</span>
            <span className="text-xs text-purple-600 dark:text-purple-400 font-medium">Immutable</span>
          </div>
        </Card>
      </div>

      {/* Admin Quick Action Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Administrative Controls" subtitle="System configuration and security management">
          <div className="space-y-3 mt-2">
            <a href="/audit-logs" className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-btn flex items-center justify-between hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              <div>
                <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block">Immutable Audit Trail Logs</span>
                <span className="text-[11px] text-slate-500 dark:text-slate-400">Review security access, login events, and risk threshold adjustments.</span>
              </div>
              <ArrowUpRight className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            </a>
            <a href="/settings" className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-btn flex items-center justify-between hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              <div>
                <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block">System Settings & Risk Thresholds</span>
                <span className="text-[11px] text-slate-500 dark:text-slate-400">Configure medium/high risk thresholds and view engine diagnostics.</span>
              </div>
              <ArrowUpRight className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            </a>
          </div>
        </Card>

        <Card title="Live Transaction Feed" subtitle="Recent high-risk transactions evaluated by engine">
          <div className="space-y-2 mt-2">
            {recentHighRisk.slice(0, 3).map((tx) => (
              <div key={tx.id} className="p-2.5 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded text-xs flex justify-between items-center">
                <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">{tx.transaction_id}</span>
                <span className="text-slate-500 dark:text-slate-400 font-mono">${tx.amount.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
