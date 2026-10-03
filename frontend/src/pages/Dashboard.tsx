import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { apiRequest } from '../services/api';
import type { DashboardStats, Transaction, Alert, Investigation, User } from '../types';
import { AnalystOverview } from '../components/dashboard/AnalystOverview';
import { RiskManagerOverview } from '../components/dashboard/RiskManagerOverview';
import { AdminOverview } from '../components/dashboard/AdminOverview';
import { ViewerOverview } from '../components/dashboard/ViewerOverview';
import { LiveScoringDashboard } from '../components/dashboard/LiveScoringDashboard';
import { Activity, Shield } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user } = useOutletContext<{ user: User | null }>();
  const [activeTab, setActiveTab] = useState<'live' | 'role'>('live');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [recentHighRisk, setRecentHighRisk] = useState<Transaction[]>([]);
  const [activeAlerts, setActiveAlerts] = useState<Alert[]>([]);
  const [openInvestigations, setOpenInvestigations] = useState<Investigation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [statsData, trendsData, recentTx, alertsData, invData] = await Promise.all([
        apiRequest<DashboardStats>('/dashboard/stats'),
        apiRequest<any[]>('/dashboard/trends'),
        apiRequest<Transaction[]>('/transactions?limit=10'),
        apiRequest<Alert[]>('/alerts?limit=10&status=NEW'),
        apiRequest<Investigation[]>('/investigations?limit=10').catch(() => []),
      ]);

      setStats(statsData);
      setTrends(trendsData);
      setRecentHighRisk(recentTx);
      setActiveAlerts(alertsData);
      setOpenInvestigations(invData);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const role = user?.role || 'FRAUD_ANALYST';

  return (
    <div className="space-y-6">
      {/* Top Level Mode Tabs */}
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('live')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-2 transition-all ${
              activeTab === 'live'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            Live Detection Stream & Triage
          </button>
          <button
            onClick={() => setActiveTab('role')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-2 transition-all ${
              activeTab === 'role'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
            }`}
          >
            <Shield className="w-3.5 h-3.5" />
            Role Operations Overview
          </button>
        </div>
        <div className="text-[11px] font-mono text-slate-400 dark:text-slate-500">
          Engine: Decision-Support • Active
        </div>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 p-4 rounded-card text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
          <Button size="sm" variant="outline" onClick={fetchDashboardData}>Retry</Button>
        </div>
      )}

      {activeTab === 'live' ? (
        <LiveScoringDashboard />
      ) : role === 'RISK_MANAGER' ? (
        <RiskManagerOverview
          stats={stats}
          trends={trends}
          openInvestigations={openInvestigations}
          onRefresh={fetchDashboardData}
          isLoading={isLoading}
        />
      ) : role === 'ADMIN' ? (
        <AdminOverview
          stats={stats}
          recentHighRisk={recentHighRisk}
          onRefresh={fetchDashboardData}
          isLoading={isLoading}
        />
      ) : role === 'VIEWER' ? (
        <ViewerOverview
          stats={stats}
          recentHighRisk={recentHighRisk}
          onRefresh={fetchDashboardData}
          isLoading={isLoading}
        />
      ) : (
        <AnalystOverview
          stats={stats}
          activeAlerts={activeAlerts}
          recentHighRisk={recentHighRisk}
          openInvestigations={openInvestigations}
          onRefresh={fetchDashboardData}
          isLoading={isLoading}
        />
      )}
    </div>
  );
};

export default Dashboard;
