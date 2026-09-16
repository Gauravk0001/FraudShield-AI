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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-blue-900 via-slate-900 to-indigo-950 p-6 rounded-card text-white shadow-md">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-blue-400" />
            <h2 className="text-xl font-bold tracking-tight">Fraud Operations & Triage Workspace</h2>
          </div>
          <p className="text-xs text-blue-200 mt-1">
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
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Unassigned Alerts</span>
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{stats?.active_alerts.toLocaleString() || '0'}</span>
            <span className="text-xs text-amber-600 font-medium">Requires Triage</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-rose-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">High Risk Stream</span>
            <ShieldAlert className="w-5 h-5 text-rose-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-rose-700">{stats?.high_risk_transactions.toLocaleString() || '0'}</span>
            <span className="text-xs text-rose-600 font-semibold">Score ≥ 70</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-blue-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Open Investigations</span>
            <Search className="w-5 h-5 text-blue-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{stats?.open_investigations || openInvestigations.length}</span>
            <span className="text-xs text-blue-600 font-medium">In Queue</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-emerald-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Scoring Latency</span>
            <Activity className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{stats?.avg_latency_ms || 42} ms</span>
            <span className="text-xs text-emerald-600 font-medium">Real-Time Pipeline</span>
          </div>
        </Card>
      </div>

      {/* Main Operational Split: Alert Triage & Active Case Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Triage Priority Alerts */}
        <Card title="Alert Triage Queue" subtitle="High & Critical severity alerts requiring analyst review" className="lg:col-span-2">
          <div className="space-y-3 mt-3">
            {activeAlerts.length === 0 ? (
              <div className="text-center py-10 text-slate-500 text-xs">
                No active pending alerts requiring triage.
              </div>
            ) : (
              activeAlerts.map((alert) => (
                <div key={alert.id} className="p-4 bg-slate-50 border border-slate-200 rounded-btn flex items-center justify-between hover:bg-slate-100/90 transition-colors">
                  <div className="space-y-1 min-w-0 pr-4">
                    <div className="flex items-center gap-2">
                      <RiskBadge level={alert.severity} score={alert.risk_score} />
                      <span className="text-xs font-bold text-slate-900 truncate">${alert.amount.toLocaleString()}</span>
                      <span className="text-[10px] text-slate-500 font-mono">({alert.transaction_id})</span>
                    </div>
                    <p className="text-xs font-medium text-slate-800">{alert.title}</p>
                    <p className="text-[11px] text-slate-500 truncate">{alert.description}</p>
                  </div>
                  <a
                    href={`/alerts`}
                    className="inline-flex items-center gap-1 text-xs font-semibold bg-blue-600 text-white px-3 py-1.5 rounded-md hover:bg-blue-700 shrink-0"
                  >
                    Triage Alert <ArrowUpRight className="w-3.5 h-3.5" />
                  </a>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* Active Investigation Workload */}
        <Card title="Assigned Case Workload" subtitle="Active cases assigned to your team">
          <div className="space-y-3 mt-3">
            {openInvestigations.length === 0 ? (
              <div className="text-center py-10 text-slate-400 text-xs">
                No active open investigations in queue.
              </div>
            ) : (
              openInvestigations.slice(0, 4).map((inv) => (
                <div key={inv.id} className="p-3 bg-white border border-slate-200 rounded-btn shadow-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-slate-900">Case #{inv.id.slice(0, 8)}</span>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                      inv.status === 'OPEN' ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'
                    }`}>
                      {inv.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 mt-1 truncate">
                    Assigned: {inv.assigned_analyst_id ? 'Analyst' : 'Unassigned'}
                  </p>
                  <div className="mt-2 text-right">
                    <a href={`/investigations`} className="text-xs font-semibold text-blue-600 hover:text-blue-800">
                      Open Workspace →
                    </a>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Flagged Transactions Feed */}
      <Card title="Critical & High-Risk Transaction Feed" subtitle="Transactions flagged with Risk Score ≥ 70">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Transaction ID</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Location</th>
                <th className="py-3 px-4">Risk Score</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recentHighRisk.length === 0 ? (
                <tr><td colSpan={6} className="text-center py-6 text-slate-400">No high-risk transactions recorded</td></tr>
              ) : (
                recentHighRisk.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-slate-900">{tx.transaction_id}</td>
                    <td className="py-3 px-4 text-slate-700">{tx.customer_id}</td>
                    <td className="py-3 px-4 font-bold text-slate-900">${tx.amount.toLocaleString()}</td>
                    <td className="py-3 px-4 text-slate-600">{tx.location}</td>
                    <td className="py-3 px-4 font-bold text-rose-700">
                      {tx.risk_score ? Math.round(tx.risk_score.risk_score) : '-'} / 100
                    </td>
                    <td className="py-3 px-4 text-right">
                      <a href={`/transactions?id=${tx.id}`} className="text-blue-600 font-semibold hover:text-blue-800">
                        View Evidence & SHAP →
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
