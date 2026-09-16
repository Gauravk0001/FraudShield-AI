import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Activity,
  Clock,
  ArrowUpRight,
  RefreshCw
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Card } from '../components/ui/Card';
import { RiskBadge } from '../components/ui/RiskBadge';
import { Button } from '../components/ui/Button';
import { apiRequest } from '../services/api';
import type { DashboardStats, Transaction, Alert } from '../types';

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [recentHighRisk, setRecentHighRisk] = useState<Transaction[]>([]);
  const [activeAlerts, setActiveAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [statsData, trendsData, recentTx, alertsData] = await Promise.all([
        apiRequest<DashboardStats>('/dashboard/stats'),
        apiRequest<any[]>('/dashboard/trends'),
        apiRequest<Transaction[]>('/transactions?limit=5'),
        apiRequest<Alert[]>('/alerts?limit=5&status=NEW'),
      ]);

      setStats(statsData);
      setTrends(trendsData);
      setRecentHighRisk(recentTx);
      setActiveAlerts(alertsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Executive Operations Dashboard</h2>
          <p className="text-xs text-slate-500 mt-0.5">Real-time ML risk scoring & anomaly detection summary</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchDashboardData} isLoading={isLoading}>
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Refresh Data
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-card text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
          <Button size="sm" variant="outline" onClick={fetchDashboardData}>Retry</Button>
        </div>
      )}

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-blue-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Volume</span>
            <Activity className="w-5 h-5 text-blue-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{stats?.total_transactions.toLocaleString() || '0'}</span>
            <span className="text-xs text-slate-500 font-medium">Processed</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-rose-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">High-Risk Flagged</span>
            <ShieldAlert className="w-5 h-5 text-rose-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-rose-700">{stats?.high_risk_transactions.toLocaleString() || '0'}</span>
            <span className="text-xs text-rose-600 font-semibold">{stats?.fraud_rate_percentage}% (Score ≥70)</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-amber-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Alerts</span>
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{stats?.active_alerts.toLocaleString() || '0'}</span>
            <span className="text-xs text-amber-600 font-medium">Policy: Score ≥30</span>
          </div>
        </Card>

        <Card className="border-l-4 border-l-emerald-600">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Avg Latency</span>
            <Clock className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{stats?.avg_latency_ms || 42} ms</span>
            <span className="text-xs text-emerald-600 font-medium">Real-Time ML</span>
          </div>
        </Card>
      </div>

      {/* Risk Trend Chart & Active Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="7-Day Risk & Fraud Trends" subtitle="Volume vs High-Risk Flagged Transactions" className="lg:col-span-2">
          <div className="h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563EB" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorHigh" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#DC2626" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#DC2626" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="date" stroke="#94A3B8" fontSize={11} />
                <YAxis stroke="#94A3B8" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderRadius: '8px', border: 'none', color: '#fff', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="total_volume" name="Total Volume" stroke="#2563EB" fillOpacity={1} fill="url(#colorTotal)" strokeWidth={2} />
                <Area type="monotone" dataKey="high_risk" name="High Risk Flagged" stroke="#DC2626" fillOpacity={1} fill="url(#colorHigh)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Active Alerts List */}
        <Card title="New Triggered Alerts" subtitle="Requires Analyst Triage">
          <div className="space-y-3 mt-2">
            {activeAlerts.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-xs">
                <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-80" />
                No unhandled alerts pending
              </div>
            ) : (
              activeAlerts.map((alert) => (
                <div key={alert.id} className="p-3 bg-slate-50 border border-slate-200 rounded-btn flex items-center justify-between hover:bg-slate-100/80 transition-colors">
                  <div className="space-y-1 min-w-0 pr-2">
                    <div className="flex items-center gap-2">
                      <RiskBadge level={alert.severity} score={alert.risk_score} />
                      <span className="text-xs font-semibold text-slate-900 truncate">${alert.amount.toLocaleString()}</span>
                    </div>
                    <p className="text-[11px] text-slate-600 truncate">{alert.title}</p>
                  </div>
                  <a href={`/alerts`} className="p-1.5 text-slate-400 hover:text-blue-600 rounded-md">
                    <ArrowUpRight className="w-4 h-4" />
                  </a>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Recent High Risk Transactions Table */}
      <Card title="Recent Ingested Transactions" subtitle="Live stream of evaluated financial transactions">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Transaction ID</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Risk Score</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recentHighRisk.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-6 text-slate-400">No transactions recorded yet</td>
                </tr>
              ) : (
                recentHighRisk.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-slate-900">{tx.transaction_id}</td>
                    <td className="py-3 px-4 text-slate-500">{new Date(tx.timestamp).toLocaleTimeString()}</td>
                    <td className="py-3 px-4 text-slate-700">{tx.customer_id}</td>
                    <td className="py-3 px-4 font-semibold text-slate-900">${tx.amount.toLocaleString()}</td>
                    <td className="py-3 px-4">
                      {tx.risk_score ? (
                        <RiskBadge level={tx.risk_score.risk_level} />
                      ) : (
                        <span className="text-slate-400">N/A</span>
                      )}
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-900">
                      {tx.risk_score ? Math.round(tx.risk_score.risk_score) : '-'} / 100
                    </td>
                    <td className="py-3 px-4 text-right">
                      <a href={`/transactions?id=${tx.id}`} className="text-blue-600 hover:text-blue-800 font-semibold">
                        View Details →
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
