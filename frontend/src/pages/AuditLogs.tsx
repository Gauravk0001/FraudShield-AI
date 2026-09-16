import React, { useState, useEffect } from 'react';
import { FileText, Search, Shield, RefreshCw } from 'lucide-react';
import { apiRequest } from '../services/api';
import { Card } from '../components/ui/Card';

interface AuditLog {
  id: string;
  action: string;
  user_id?: string;
  resource_type?: string;
  resource_id?: string;
  details?: Record<string, any>;
  ip_address?: string;
  timestamp: string;
}

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest<AuditLog[]>('/audit-logs?limit=50');
      setLogs(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch audit logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filtered = logs.filter(l =>
    l.action.toLowerCase().includes(search.toLowerCase()) ||
    (l.user_id && l.user_id.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-7 h-7 text-blue-600" />
            System Audit Trail
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Immutable log of all user authentication, role changes, investigation decisions, and model events.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search action or user..."
              className="pl-9 pr-3 py-2 text-sm bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-60"
            />
          </div>
          <button
            onClick={fetchLogs}
            className="p-2 border border-slate-300 rounded-lg bg-white hover:bg-slate-50 text-slate-700"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      <Card>
        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Loading audit logs...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-600 text-sm">{error}</div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <Shield className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="font-semibold text-slate-700">No Audit Events Recorded</p>
            <p className="text-xs text-slate-400 mt-1">Actions performed by users will appear here automatically.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold text-xs uppercase">
                <tr>
                  <th className="px-5 py-3">Timestamp</th>
                  <th className="px-5 py-3">Action</th>
                  <th className="px-5 py-3">User ID</th>
                  <th className="px-5 py-3">Resource</th>
                  <th className="px-5 py-3">IP Address</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {filtered.map(log => (
                  <tr key={log.id} className="hover:bg-slate-50/80">
                    <td className="px-5 py-3 text-xs text-slate-500 whitespace-nowrap font-mono">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-5 py-3 font-medium text-slate-900">
                      <span className="px-2 py-1 rounded bg-slate-100 font-mono text-xs text-slate-800">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-xs text-slate-600">{log.user_id || 'System'}</td>
                    <td className="px-5 py-3 text-xs text-slate-600">
                      {log.resource_type ? `${log.resource_type} (${log.resource_id})` : '-'}
                    </td>
                    <td className="px-5 py-3 text-xs text-slate-500 font-mono">{log.ip_address || '127.0.0.1'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};

export default AuditLogsPage;
