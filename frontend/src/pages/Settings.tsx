import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { CheckCircle2, Settings as SettingsIcon, ShieldAlert } from 'lucide-react';
import { ApiError, apiRequest } from '../services/api';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import type { User } from '../types';

interface SystemSettings {
  organization_id: string;
  organization_name: string;
  environment: string;
  project_name: string;
  version: string;
  risk_threshold_medium: number;
  risk_threshold_high: number;
  risk_threshold_critical: number;
  xgboost_weight: number;
  isolation_forest_weight: number;
  rules_weight: number;
  auto_create_alerts: boolean;
  session_expire_minutes: number;
  gemini_copilot_enabled: boolean;
  gemini_api_key_configured: boolean;
}

export const SettingsPage: React.FC = () => {
  const { user } = useOutletContext<{ user: User | null }>();
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [mediumThreshold, setMediumThreshold] = useState(30);
  const [highThreshold, setHighThreshold] = useState(70);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [forbidden, setForbidden] = useState(false);
  const [saved, setSaved] = useState(false);

  const loadSettings = async () => {
    setLoading(true);
    setError(null);
    setForbidden(false);
    setSaved(false);
    try {
      const data = await apiRequest<SystemSettings>('/settings');
      setSettings(data);
      setMediumThreshold(data.risk_threshold_medium);
      setHighThreshold(data.risk_threshold_high);
    } catch (err) {
      setForbidden(err instanceof ApiError && err.status === 403);
      setError(err instanceof Error ? err.message : 'Failed to load settings.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const saveSettings = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setForbidden(false);
    setSaved(false);
    try {
      const updated = await apiRequest<SystemSettings>('/settings', {
        method: 'PATCH',
        body: JSON.stringify({
          risk_threshold_medium: mediumThreshold,
          risk_threshold_high: highThreshold,
        }),
      });
      setSettings(updated);
      setMediumThreshold(updated.risk_threshold_medium);
      setHighThreshold(updated.risk_threshold_high);
      setSaved(true);
    } catch (err) {
      setForbidden(err instanceof ApiError && err.status === 403);
      setError(err instanceof Error ? err.message : 'Failed to save settings.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-blue-600" />
          System Settings & Risk Configuration
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          {user?.role === 'RISK_MANAGER' ? 'Risk Manager threshold configuration & model operational settings.' : 'Administrative risk-engine configuration and service diagnostics.'}
        </p>
      </div>

      {loading ? (
        <Card><p className="py-6 text-center text-sm text-slate-500">Loading settings...</p></Card>
      ) : forbidden ? (
        <Card>
          <div className="py-6 text-center text-slate-700">
            <ShieldAlert className="w-8 h-8 mx-auto mb-3 text-amber-500" />
            <p className="font-semibold">Administrator or Risk Manager access required</p>
            <p className="text-sm text-slate-500 mt-1">
              Your role ({user?.role || 'FRAUD_ANALYST'}) does not have authorization to view or edit global system settings.
            </p>
          </div>
        </Card>
      ) : error ? (
        <Card>
          <div className="py-6 text-center text-red-600">
            <p>{error}</p>
            <Button variant="outline" size="sm" className="mt-3" onClick={loadSettings}>Retry</Button>
          </div>
        </Card>
      ) : settings && (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <Card className="xl:col-span-2" title="Risk thresholds" subtitle="Updates are audited and used by the live risk engine.">
            <form onSubmit={saveSettings} className="space-y-5">
              <label className="block">
                <span className="block text-xs font-semibold text-slate-700 mb-1">Medium-risk threshold</span>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={mediumThreshold}
                  onChange={(event) => setMediumThreshold(Number(event.target.value))}
                  className="w-full rounded-btn border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </label>
              <label className="block">
                <span className="block text-xs font-semibold text-slate-700 mb-1">High-risk threshold</span>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={highThreshold}
                  onChange={(event) => setHighThreshold(Number(event.target.value))}
                  className="w-full rounded-btn border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </label>
              <div className="flex items-center justify-between border-t border-slate-100 pt-4">
                {saved ? <span className="inline-flex items-center gap-1 text-xs text-emerald-700"><CheckCircle2 className="w-4 h-4" /> Saved and audited</span> : <span />}
                <Button type="submit" size="sm" isLoading={saving}>Save settings</Button>
              </div>
            </form>
          </Card>

          <Card title="Runtime status">
            <dl className="space-y-3 text-sm">
              <div><dt className="text-slate-500">Organization</dt><dd className="font-medium text-slate-900">{settings.organization_name}</dd></div>
              <div><dt className="text-slate-500">Environment</dt><dd className="font-medium text-slate-900">{settings.environment}</dd></div>
              <div><dt className="text-slate-500">Session duration</dt><dd className="font-medium text-slate-900">{settings.session_expire_minutes} minutes</dd></div>
              <div><dt className="text-slate-500">Automatic alerts</dt><dd className="font-medium text-slate-900">{settings.auto_create_alerts ? 'Enabled' : 'Disabled'}</dd></div>
              <div><dt className="text-slate-500">Copilot integration</dt><dd className="font-medium text-slate-900">{settings.gemini_api_key_configured ? 'Configured' : 'Not configured'}</dd></div>
            </dl>
          </Card>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;
