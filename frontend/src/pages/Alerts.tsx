import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  AlertTriangle, Filter, RefreshCw, Search, ShieldAlert,
  BarChart2, CheckCircle2, Plus, ChevronRight, Clock, X,
} from 'lucide-react';
import { apiRequest } from '../services/api';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { RiskBadge } from '../components/ui/RiskBadge';
import type { Alert, AlertStatus, RiskLevel, User } from '../types';

const statusOptions: Array<AlertStatus | 'ALL'> = [
  'ALL', 'NEW', 'ACKNOWLEDGED', 'INVESTIGATING', 'RESOLVED', 'DISMISSED',
];

const severityOptions: Array<RiskLevel | 'ALL'> = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

// ─── Severity Distribution Bar (Risk Manager) ─────────────────────────────────

const SeverityBar: React.FC<{ label: RiskLevel; count: number; total: number; color: string }> = ({
  label, count, total, color,
}) => {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div className="flex items-center gap-3 text-xs">
      <span className={`w-16 font-bold ${color} shrink-0`}>{label}</span>
      <div className="flex-1 h-3 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${
            label === 'CRITICAL' ? 'bg-purple-600 dark:bg-purple-500' :
            label === 'HIGH' ? 'bg-rose-600 dark:bg-rose-500' :
            label === 'MEDIUM' ? 'bg-amber-500 dark:bg-amber-400' : 'bg-emerald-500 dark:bg-emerald-400'
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-20 text-right text-slate-600 dark:text-slate-400 font-semibold shrink-0">
        {count} ({pct}%)
      </span>
    </div>
  );
};

// ─── Triage Side Panel (Analyst) ──────────────────────────────────────────────

const TriagePanel: React.FC<{
  alert: Alert;
  onClose: () => void;
  onAcknowledge: (id: string) => void;
  onEscalate: (alert: Alert) => void;
  isActing: boolean;
}> = ({ alert, onClose, onAcknowledge, onEscalate, isActing }) => (
  <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-end sm:items-center justify-center p-4">
    <div className="bg-white dark:bg-slate-900 w-full max-w-lg rounded-modal shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4 p-6 max-h-[90vh] overflow-y-auto">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-rose-600 dark:text-rose-400" />
          Alert Triage Investigation
        </h3>
        <button
          onClick={onClose}
          aria-label="Close panel"
          className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-md hover:bg-slate-100 dark:hover:bg-slate-800"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Alert summary */}
      <div className="p-3.5 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-btn space-y-3">
        <div className="flex items-start justify-between">
          <div>
            <p className="font-bold text-slate-900 dark:text-slate-100 text-sm">{alert.title}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{alert.description}</p>
          </div>
          <RiskBadge level={alert.severity} score={alert.risk_score} />
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-slate-400 block">Transaction</span>
            <span className="font-mono font-medium text-slate-900 dark:text-slate-100">{alert.transaction_id}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Customer</span>
            <span className="font-medium text-slate-900 dark:text-slate-100">{alert.customer_id}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Amount</span>
            <span className="font-bold text-slate-900 dark:text-slate-100">${alert.amount.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Risk Score</span>
            <span className="font-bold text-rose-600 dark:text-rose-400">{Math.round(alert.risk_score)} / 100</span>
          </div>
        </div>
      </div>

      {/* SHAP Risk Factors */}
      {alert.primary_risk_factors && alert.primary_risk_factors.length > 0 && (
        <div>
          <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">Primary Risk Factors (SHAP)</h4>
          <div className="space-y-2">
            {alert.primary_risk_factors.slice(0, 4).map((factor, i) => {
              const isPositive = factor.direction === 'POSITIVE';
              const pct = Math.min(Math.abs(factor.contribution) * 100, 100);
              return (
                <div key={i} className="space-y-0.5">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="font-mono text-slate-700 dark:text-slate-300">{factor.feature_name}</span>
                    <span className={`font-bold ml-2 ${isPositive ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400'}`}>
                      {isPositive ? '+' : ''}{(factor.contribution * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${isPositive ? 'bg-rose-500' : 'bg-emerald-500'}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <p className="text-[10px] text-slate-400 dark:text-slate-500">{factor.explanation}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Triage Actions */}
      {alert.status === 'NEW' && (
        <div className="flex gap-3 pt-2 border-t border-slate-100 dark:border-slate-800">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={() => onAcknowledge(alert.id)}
            isLoading={isActing}
          >
            <CheckCircle2 className="w-4 h-4 mr-1.5" />
            Acknowledge
          </Button>
          <Button
            variant="primary"
            size="sm"
            className="flex-1"
            onClick={() => onEscalate(alert)}
            isLoading={isActing}
          >
            <Plus className="w-4 h-4 mr-1.5" />
            Open Investigation
          </Button>
        </div>
      )}

      {alert.status !== 'NEW' && (
        <div className="text-xs text-center text-slate-500 dark:text-slate-400 py-2">
          Alert is <span className="font-semibold text-slate-700 dark:text-slate-300">{alert.status}</span> — no triage actions available.
        </div>
      )}
    </div>
  </div>
);

// ─── MAIN PAGE ─────────────────────────────────────────────────────────────────

export const AlertsPage: React.FC = () => {
  const { user } = useOutletContext<{ user: User | null }>();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [statusFilter, setStatusFilter] = useState<AlertStatus | 'ALL'>('ALL');
  const [severityFilter, setSeverityFilter] = useState<RiskLevel | 'ALL'>('ALL');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [triageAlert, setTriageAlert] = useState<Alert | null>(null);
  const [isActing, setIsActing] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const isRiskManager = user?.role === 'RISK_MANAGER';
  const isAnalyst = user?.role === 'FRAUD_ANALYST' || user?.role === 'ADMIN';

  const fetchAlerts = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ limit: '100' });
      if (statusFilter !== 'ALL') params.set('status', statusFilter);
      if (severityFilter !== 'ALL') params.set('severity', severityFilter);
      setAlerts(await apiRequest<Alert[]>(`/alerts?${params.toString()}`));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load alerts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter, severityFilter]);

  const visibleAlerts = alerts.filter((alert) => {
    const term = search.trim().toLowerCase();
    return !term || [alert.title, alert.transaction_id, alert.customer_id, alert.description]
      .some((v) => v.toLowerCase().includes(term));
  });

  // Severity counts for Risk Manager view
  const criticalCount = alerts.filter((a) => a.severity === 'CRITICAL').length;
  const highCount = alerts.filter((a) => a.severity === 'HIGH').length;
  const mediumCount = alerts.filter((a) => a.severity === 'MEDIUM').length;
  const lowCount = alerts.filter((a) => a.severity === 'LOW').length;
  const newCount = alerts.filter((a) => a.status === 'NEW').length;

  const handleAcknowledge = async (alertId: string) => {
    setIsActing(true);
    try {
      await apiRequest(`/alerts/${alertId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: 'ACKNOWLEDGED' }),
      });
      setTriageAlert(null);
      setActionSuccess('Alert acknowledged.');
      setTimeout(() => setActionSuccess(null), 3000);
      fetchAlerts();
    } catch (err: any) {
      setError(err.message || 'Failed to acknowledge alert');
    } finally {
      setIsActing(false);
    }
  };

  const handleEscalate = async (alert: Alert) => {
    setIsActing(true);
    try {
      await apiRequest('/investigations', {
        method: 'POST',
        body: JSON.stringify({ alert_id: alert.id }),
      });
      setTriageAlert(null);
      setActionSuccess(`Investigation opened for alert ${alert.id.slice(0, 8)}.`);
      setTimeout(() => setActionSuccess(null), 4000);
      fetchAlerts();
    } catch (err: any) {
      setError(err.message || 'Failed to open investigation');
    } finally {
      setIsActing(false);
    }
  };

  const hoursSince = (dateStr: string) =>
    Math.floor((Date.now() - new Date(dateStr).getTime()) / 3_600_000);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            {isRiskManager
              ? <BarChart2 className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              : <ShieldAlert className="w-5 h-5 text-rose-600 dark:text-rose-400" />}
            {isRiskManager ? 'Alert Volume & Severity Oversight' : 'Fraud Alert Triage Stream'}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            {isRiskManager
              ? 'Portfolio alert distribution, severity trends, and investigation backlog monitoring.'
              : 'Real-time alert triage queue — acknowledge and escalate to investigation in one click.'}
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchAlerts} isLoading={loading}>
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />Refresh
        </Button>
      </div>

      {/* Success banner */}
      {actionSuccess && (
        <div className="flex items-center gap-2 px-4 py-2.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs font-medium rounded-btn">
          <CheckCircle2 className="w-4 h-4 shrink-0" />{actionSuccess}
        </div>
      )}

      {/* Risk Manager: Severity Distribution */}
      {isRiskManager && alerts.length > 0 && (
        <Card title="Severity Distribution" subtitle="Portfolio-wide alert breakdown by severity level">
          <div className="space-y-3 mt-3">
            <SeverityBar label="CRITICAL" count={criticalCount} total={alerts.length} color="text-purple-700 dark:text-purple-400" />
            <SeverityBar label="HIGH" count={highCount} total={alerts.length} color="text-rose-700 dark:text-rose-400" />
            <SeverityBar label="MEDIUM" count={mediumCount} total={alerts.length} color="text-amber-700 dark:text-amber-400" />
            <SeverityBar label="LOW" count={lowCount} total={alerts.length} color="text-emerald-700 dark:text-emerald-400" />
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
            <span>
              Investigation conversion rate:{' '}
              <span className="font-bold text-slate-900 dark:text-slate-100">
                {newCount > 0 ? Math.round(((alerts.length - newCount) / alerts.length) * 100) : 0}%
              </span>{' '}
              of alerts escalated
            </span>
            <span className="text-slate-400 dark:text-slate-500">{alerts.length} total alerts</span>
          </div>
        </Card>
      )}

      {/* Filter Bar */}
      <Card className="!p-4">
        <div className="flex flex-col lg:flex-row gap-3 lg:items-center lg:justify-between">
          <div className="relative w-full lg:w-80">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search title, transaction, customer..."
              className="w-full pl-9 pr-4 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-btn text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              aria-label="Filter alerts by status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as AlertStatus | 'ALL')}
              className="text-xs border border-slate-300 dark:border-slate-700 rounded-btn px-2.5 py-1.5 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200"
            >
              {statusOptions.map((s) => <option key={s} value={s}>{s === 'ALL' ? 'All statuses' : s}</option>)}
            </select>
            <select
              aria-label="Filter alerts by severity"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value as RiskLevel | 'ALL')}
              className="text-xs border border-slate-300 dark:border-slate-700 rounded-btn px-2.5 py-1.5 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200"
            >
              {severityOptions.map((s) => <option key={s} value={s}>{s === 'ALL' ? 'All severities' : s}</option>)}
            </select>
          </div>
        </div>
      </Card>

      {/* Alerts Table */}
      <Card className="!p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Alert</th>
                <th className="py-3 px-4">Transaction</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Risk Score</th>
                <th className="py-3 px-4">Status</th>
                {isRiskManager && <th className="py-3 px-4">Age</th>}
                <th className="py-3 px-4">Created</th>
                {isAnalyst && <th className="py-3 px-4 text-right">Action</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {loading ? (
                <tr><td colSpan={isAnalyst ? 8 : isRiskManager ? 8 : 7} className="text-center py-10 text-slate-500">Loading alerts...</td></tr>
              ) : error ? (
                <tr>
                  <td colSpan={8} className="text-center py-10 text-red-600 dark:text-red-400">
                    <p>{error}</p>
                    <Button variant="outline" size="sm" className="mt-3" onClick={fetchAlerts}>Retry</Button>
                  </td>
                </tr>
              ) : visibleAlerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-10 text-slate-500">
                    <AlertTriangle className="w-7 h-7 mx-auto mb-2 text-slate-300 dark:text-slate-600" />
                    No alerts match the current filters.
                  </td>
                </tr>
              ) : (
                visibleAlerts.map((alert) => (
                  <tr key={alert.id} className={`hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition-colors ${
                    isAnalyst && alert.status === 'NEW' ? 'border-l-2 border-l-rose-400 dark:border-l-rose-500' : ''
                  }`}>
                    <td className="py-3 px-4 max-w-xs">
                      <p className="font-semibold text-slate-900 dark:text-slate-100">{alert.title}</p>
                      <p className="text-slate-500 dark:text-slate-400 mt-0.5 truncate">{alert.description}</p>
                    </td>
                    <td className="py-3 px-4">
                      <p className="font-mono text-slate-800 dark:text-slate-200">{alert.transaction_id}</p>
                      <p className="text-slate-500 dark:text-slate-400 mt-0.5">{alert.customer_id}</p>
                    </td>
                    <td className="py-3 px-4"><RiskBadge level={alert.severity} /></td>
                    <td className="py-3 px-4 font-semibold text-slate-900 dark:text-slate-100">{Math.round(alert.risk_score)} / 100</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                        alert.status === 'NEW' ? 'bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300' :
                        alert.status === 'ACKNOWLEDGED' ? 'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300' :
                        alert.status === 'INVESTIGATING' ? 'bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300' :
                        alert.status === 'RESOLVED' ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300' :
                        'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
                      }`}>
                        {alert.status}
                      </span>
                    </td>
                    {isRiskManager && (
                      <td className="py-3 px-4">
                        <span className={`flex items-center gap-1 text-xs font-semibold ${
                          hoursSince(alert.created_at) >= 24 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-600 dark:text-slate-400'
                        }`}>
                          <Clock className="w-3.5 h-3.5" />{hoursSince(alert.created_at)}h
                        </span>
                      </td>
                    )}
                    <td className="py-3 px-4 text-slate-500 dark:text-slate-400 whitespace-nowrap">
                      {new Date(alert.created_at).toLocaleString()}
                    </td>
                    {isAnalyst && (
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => setTriageAlert(alert)}
                          className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline"
                        >
                          Triage <ChevronRight className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Analyst Triage Panel */}
      {triageAlert && isAnalyst && (
        <TriagePanel
          alert={triageAlert}
          onClose={() => setTriageAlert(null)}
          onAcknowledge={handleAcknowledge}
          onEscalate={handleEscalate}
          isActing={isActing}
        />
      )}
    </div>
  );
};

export default AlertsPage;
