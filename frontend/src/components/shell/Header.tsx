import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, User as UserIcon } from 'lucide-react';
import type { User } from '../../types';
import { clearStoredToken } from '../../services/api';
import { NotificationCenter } from './NotificationCenter';
import { ThemeToggle } from './ThemeToggle';

interface HeaderProps {
  user?: User | null;
}

const ROLE_CONFIG: Record<string, { title: string; subtitle: string; titleColor: string; darkTitleColor: string }> = {
  FRAUD_ANALYST: {
    title: 'Fraud Operations Center',
    subtitle: 'DETECT · TRIAGE · INVESTIGATE · DOCUMENT',
    titleColor: 'text-slate-900',
    darkTitleColor: 'dark:text-slate-100',
  },
  RISK_MANAGER: {
    title: 'Risk Intelligence Command',
    subtitle: 'OVERSEE · MONITOR · GOVERN · OPTIMIZE',
    titleColor: 'text-purple-900',
    darkTitleColor: 'dark:text-purple-300',
  },
  ADMIN: {
    title: 'Platform Administration',
    subtitle: 'CONFIGURE · AUDIT · MANAGE · CONTROL',
    titleColor: 'text-slate-900',
    darkTitleColor: 'dark:text-slate-100',
  },
  VIEWER: {
    title: 'FraudShield — Read-Only View',
    subtitle: 'OBSERVE · REVIEW · REPORT',
    titleColor: 'text-slate-600',
    darkTitleColor: 'dark:text-slate-300',
  },
};

export const Header: React.FC<HeaderProps> = ({ user }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    clearStoredToken();
    navigate('/login');
  };

  const roleKey = user?.role || 'FRAUD_ANALYST';
  const config = ROLE_CONFIG[roleKey] ?? ROLE_CONFIG['FRAUD_ANALYST'];

  return (
    <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-6 flex items-center justify-between sticky top-0 z-20 shadow-xs transition-colors">
      <div className="flex flex-col justify-center">
        <h1 className={`text-base font-bold leading-tight ${config.titleColor} ${config.darkTitleColor}`}>
          {config.title}
        </h1>
        <span className="text-[10px] font-semibold tracking-widest text-slate-400 dark:text-slate-500 leading-tight">
          {config.subtitle}
        </span>
      </div>

      <div className="flex items-center gap-3 sm:gap-4">
        <div className="hidden md:flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[10px] font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800 px-2 py-0.5 rounded-full">
            Real-Time Engine Stream
          </span>
        </div>

        {/* Theme Switcher Toggle */}
        <ThemeToggle />

        {/* Real-time WebSocket Notification Center */}
        <NotificationCenter />

        <div className="h-6 w-px bg-slate-200 dark:bg-slate-800" />

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 flex items-center justify-center text-slate-600 dark:text-slate-300">
            <UserIcon className="w-4 h-4" />
          </div>
          <div className="text-left hidden sm:block">
            <span className="block text-xs font-semibold text-slate-900 dark:text-slate-100">
              {user?.full_name || 'Fraud Analyst'}
            </span>
            <span
              className={`inline-block text-[10px] font-bold px-1.5 py-0.2 rounded border uppercase tracking-wider ${
                user?.role === 'ADMIN'
                  ? 'bg-purple-50 dark:bg-purple-950/50 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800'
                  : user?.role === 'RISK_MANAGER'
                  ? 'bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800'
                  : user?.role === 'VIEWER'
                  ? 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-300 dark:border-slate-700'
                  : 'bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800'
              }`}
            >
              {user?.role ? user.role.replace('_', ' ') : 'FRAUD ANALYST'}
            </span>
          </div>
          <button
            onClick={handleLogout}
            title="Log out"
            aria-label="Log out of application"
            className="p-2 text-slate-400 hover:text-red-600 dark:hover:text-red-400 rounded-md hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors ml-1"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
