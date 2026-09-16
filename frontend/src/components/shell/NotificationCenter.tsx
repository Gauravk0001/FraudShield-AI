import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, ShieldAlert, AlertTriangle, Info, CheckCheck, Radio } from 'lucide-react';
import { getStoredToken, apiRequest } from '../../services/api';
import type { Alert } from '../../types';

interface RealtimeNotification {
  id: string;
  alert_id: string;
  transaction_id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

export const NotificationCenter: React.FC = () => {
  const [notifications, setNotifications] = useState<RealtimeNotification[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const navigate = useNavigate();

  // Load initial recent alerts
  useEffect(() => {
    const fetchRecentAlerts = async () => {
      try {
        const alerts = await apiRequest<Alert[]>('/alerts?limit=10');
        const formatted: RealtimeNotification[] = alerts.map((a) => ({
          id: a.id,
          alert_id: a.id,
          transaction_id: a.transaction_id,
          severity: a.severity,
          title: `${a.severity} Fraud Alert`,
          message: `Transaction ${a.transaction_id.slice(0, 12)}... flagged (Score: ${Math.round(a.risk_score)})`,
          timestamp: a.created_at,
          read: a.status !== 'NEW',
        }));
        setNotifications(formatted);
      } catch {
        // Fallback silently if unauthenticated or offline
      }
    };

    fetchRecentAlerts();
  }, []);

  // WebSocket connection for real-time live alert broadcasts
  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;

    let socket: WebSocket | null = null;
    let reconnectTimeout: number | undefined;
    let retryCount = 0;
    let isDisposed = false;

    const connectWs = () => {
      if (isDisposed) return;
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // In local development, backend runs on port 8000
        const host = window.location.port === '5173' ? `${window.location.hostname}:8000` : window.location.host;
        const wsUrl = `${protocol}//${host}/ws/alerts?token=${encodeURIComponent(token)}`;

        socket = new WebSocket(wsUrl);
        wsRef.current = socket;

        socket.onopen = () => {
          if (!isDisposed) {
            setIsConnected(true);
            retryCount = 0; // Reset backoff upon successful connection
          }
        };

        socket.onmessage = (event) => {
          if (isDisposed) return;
          try {
            const data = JSON.parse(event.data);
            // Expected payload from alert_service WebSocket broadcast
            if (data.type === 'ALERT_CREATED' || data.alert_id) {
              const newNotif: RealtimeNotification = {
                id: data.alert_id || `ws-${Date.now()}`,
                alert_id: data.alert_id || '',
                transaction_id: data.transaction_id || '',
                severity: data.severity || 'HIGH',
                title: `Real-Time ${data.severity || 'HIGH'} Alert`,
                message: data.message || `Transaction flagged with risk score ${Math.round(data.risk_score || 85)}`,
                timestamp: new Date().toISOString(),
                read: false,
              };

              // Strictly enforce maximum 25 items to prevent unbounded memory growth
              setNotifications((prev) => [newNotif, ...prev.slice(0, 24)]);
            }
          } catch {
            // Heartbeat or plain text ping
          }
        };

        socket.onclose = () => {
          if (isDisposed) return;
          setIsConnected(false);
          // Exponential backoff: 2s, 4s, 8s, up to max 16s
          const backoffDelay = Math.min(2000 * Math.pow(2, retryCount), 16000);
          retryCount++;
          reconnectTimeout = window.setTimeout(connectWs, backoffDelay);
        };

        socket.onerror = () => {
          if (!isDisposed) setIsConnected(false);
        };
      } catch {
        if (!isDisposed) {
          setIsConnected(false);
          const backoffDelay = Math.min(2000 * Math.pow(2, retryCount), 16000);
          retryCount++;
          reconnectTimeout = window.setTimeout(connectWs, backoffDelay);
        }
      }
    };

    connectWs();

    return () => {
      isDisposed = true;
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (socket) {
        socket.onclose = null;
        socket.onerror = null;
        socket.close();
      }
    };
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const markAsRead = (id: string) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
  };

  const handleNotificationClick = (notif: RealtimeNotification) => {
    markAsRead(notif.id);
    setIsOpen(false);
    navigate('/alerts');
  };

  const getSeverityIcon = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return <ShieldAlert className="w-4 h-4 text-red-600 shrink-0" />;
      case 'HIGH':
        return <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0" />;
      case 'MEDIUM':
        return <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />;
      default:
        return <Info className="w-4 h-4 text-blue-500 shrink-0" />;
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Notification Center"
        className="relative p-2 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <>
            <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-red-500 rounded-full animate-ping" />
            <span className="absolute top-1 right-1 px-1 min-w-[16px] h-4 bg-red-600 text-[10px] font-bold text-white rounded-full flex items-center justify-center border-2 border-white dark:border-slate-900">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          </>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-card shadow-xl z-50 overflow-hidden animate-in fade-in duration-150">
          <div className="p-3.5 bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-xs text-slate-900 dark:text-slate-100 uppercase tracking-wider">
                Notification Center
              </span>
              <span
                className={`inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                  isConnected
                    ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300'
                    : 'bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                }`}
              >
                <Radio className={`w-2.5 h-2.5 ${isConnected ? 'animate-pulse text-emerald-600' : ''}`} />
                {isConnected ? 'Real-Time' : 'Connecting'}
              </span>
            </div>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-[11px] text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 font-medium"
              >
                <CheckCheck className="w-3.5 h-3.5" /> Mark read
              </button>
            )}
          </div>

          <div className="max-h-80 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800/60">
            {notifications.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400 dark:text-slate-500">
                No active notifications
              </div>
            ) : (
              notifications.map((notif) => (
                <div
                  key={notif.id}
                  onClick={() => handleNotificationClick(notif)}
                  className={`p-3 cursor-pointer transition-colors flex items-start gap-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 ${
                    !notif.read ? 'bg-blue-50/40 dark:bg-blue-950/20' : ''
                  }`}
                >
                  <div className="mt-0.5">{getSeverityIcon(notif.severity)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1">
                      <p className={`text-xs font-semibold truncate ${!notif.read ? 'text-slate-900 dark:text-slate-100' : 'text-slate-600 dark:text-slate-400'}`}>
                        {notif.title}
                      </p>
                      <span className="text-[10px] text-slate-400 shrink-0">
                        {new Date(notif.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 mt-0.5">
                      {notif.message}
                    </p>
                  </div>
                  {!notif.read && (
                    <span className="w-2 h-2 rounded-full bg-blue-600 shrink-0 mt-1.5" />
                  )}
                </div>
              ))
            )}
          </div>

          <div className="p-2.5 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-800 text-center">
            <button
              onClick={() => {
                setIsOpen(false);
                navigate('/alerts');
              }}
              className="text-xs font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
            >
              View all fraud alerts →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
