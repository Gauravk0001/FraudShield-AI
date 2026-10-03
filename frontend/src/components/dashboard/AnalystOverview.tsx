import React from 'react';
import { ShieldAlert, AlertTriangle, Search, Activity, ArrowUpRight } from 'lucide-react';
import { Card } from '../ui/Card';
import { RiskBadge } from '../ui/RiskBadge';
import { Button } from '../ui/Button';
import type { DashboardStats, Transaction, Alert, Investigation } from '../../types';

interface AnalystOverviewProps {
  stats: DashboardStats | null;
  activeAlerts: Alert[];
  recentHighRisk: Transaction[];
  openInvestigations: Investigation[];
  onRefresh: () => void;
  isLoading: boolean;
}

export const AnalystOverview: React.FC<AnalystOverviewProps> = ({
  stats,
  activeAlerts,
  recentHighRisk,
  openInvestigations,
  onRefresh,
  isLoading,
}) => {
  return (
    <div className="space-y-6">
      {/* Analyst Operational Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-blue-50 via-indigo-50/70 to-slate-50 dark:from-blue-950 dark:via-slate-900 dark:to-indigo-950 border border-blue-200 dark:border-slate-800 p-6 rounded-card text-slate-900 dark:text-white shadow-xs transition-colors">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            <h2 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">Fraud Operations & Triage Workspace</h2>
          </div>
          <p className="text-xs text-slate-600 dark:text-blue-200 mt-1">
            Detect suspicious transactions, triage real-time alerts, and execute end-to-end evidence investigations.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={onRefresh} isLoading={isLoading}>
            Refresh Operational Data
          </Button>
        </div>
      </div>

      {/* Analyst KPI Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-amber-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Unassigned Alerts</span>
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats?.active_alerts.toLocaleString() || '0'}</span>
            <span className="text-xs text-amber-600 dark:text-amber-400 font-medium">Requires Triage</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-rose-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">High Risk Stream</span>
            <ShieldAlert className="w-5 h-5 text-rose-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-rose-600 dark:text-rose-400">{stats?.high_risk_transactions.toLocaleString() || '0'}</span>
            <span className="text-xs text-rose-600 dark:text-rose-400 font-semibold">Score ≥ 70</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-blue-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Open Investigations</span>
            <Search className="w-5 h-5 text-blue-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats?.open_investigations || openInvestigations.length}</span>
            <span className="text-xs text-blue-600 dark:text-blue-400 font-medium">In Queue</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-emerald-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Scoring Latency</span>
            <Activity className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats?.avg_latency_ms || 42} ms</span>
            <span className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">Real-Time Pipeline</span>
          </div>
        </Card>
      </div>

      {/* Main Operational Split: Alert Triage & Active Case Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Triage Priority Alerts */}
        <Card title="Alert Triage Queue" subtitle="High & Critical severity alerts requiring analyst review" className="lg:col-span-2">
          <div className="space-y-3 mt-3">
            {activeAlerts.length === 0 ? (
              <div className="text-center py-10 text-slate-500 dark:text-slate-400 text-xs">
                No active pending alerts requiring triage.
              </div>
            ) : (
              activeAlerts.slice(0, 5).map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/60 rounded-btn border border-slate-200 dark:border-slate-800 text-xs hover:border-blue-400 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <RiskBadge level={alert.severity} score={alert.risk_score} />
                    <div>
                      <span className="font-semibold text-slate-900 dark:text-slate-100">{alert.title}</span>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 font-mono mt-0.5">
                        Tx: {alert.transaction_id.slice(0, 16)}... • ${alert.amount.toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <a
                    href="/alerts"
                    className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                  >
                    Triage <ArrowUpRight className="w-3.5 h-3.5" />
                  </a>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* Active Investigations Quick List */}
        <Card title="Investigation Backlog" subtitle="Active cases assigned or pending">
          <div className="space-y-3 mt-3">
            {openInvestigations.length === 0 ? (
              <div className="text-center py-10 text-slate-500 dark:text-slate-400 text-xs">
                No active investigations currently open.
              </div>
            ) : (
              openInvestigations.slice(0, 4).map((inv) => (
                <div
                  key={inv.id}
                  className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-btn border border-slate-200 dark:border-slate-800 text-xs space-y-1"
                >
                  <div className="flex items-center justify-between font-semibold">
                    <span className="font-mono text-slate-900 dark:text-slate-100">Case #{inv.id.slice(0, 8)}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300">
                      {inv.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
                    <span>Alert: {inv.alert_id.slice(0, 8)}</span>
                    <a href="/investigations" className="text-blue-600 dark:text-blue-400 font-semibold hover:underline">
                      Review →
                    </a>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Real-time High Risk Transactions Table */}
      <Card title="Live Evaluated High-Risk Transactions" subtitle="Top transactions flagged by ML XGBoost & Isolation Forest with SHAP attributions">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-3">Transaction ID</th>
                <th className="py-2.5 px-3">Customer</th>
                <th className="py-2.5 px-3">Amount</th>
                <th className="py-2.5 px-3">Risk Level</th>
                <th className="py-2.5 px-3">Score</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {recentHighRisk.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-6 text-slate-400 dark:text-slate-500">
                    No high-risk transactions recorded.
                  </td>
                </tr>
              ) : (
                recentHighRisk.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition-colors">
                    <td className="py-2.5 px-3 font-mono text-slate-900 dark:text-slate-100">{tx.transaction_id}</td>
                    <td className="py-2.5 px-3 text-slate-600 dark:text-slate-400">{tx.customer_id}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-900 dark:text-slate-100">${tx.amount.toLocaleString()}</td>
                    <td className="py-2.5 px-3">
                      {tx.risk_score ? (
                        <RiskBadge level={tx.risk_score.risk_level} />
                      ) : (
                        <span className="text-slate-400">N/A</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 font-bold text-rose-600 dark:text-rose-400">
                      {tx.risk_score ? Math.round(tx.risk_score.risk_score) : '-'} / 100
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <a href="/transactions" className="text-blue-600 dark:text-blue-400 font-semibold hover:underline">
                        Inspect
                      </a>
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
