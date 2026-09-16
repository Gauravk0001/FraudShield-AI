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

export const Dashboard: React.FC = () => {
  const { user } = useOutletContext<{ user: User | null }>();
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
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-card text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
          <Button size="sm" variant="outline" onClick={fetchDashboardData}>Retry</Button>
        </div>
      )}

      {role === 'RISK_MANAGER' ? (
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
