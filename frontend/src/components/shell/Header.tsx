import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, User as UserIcon, Bell } from 'lucide-react';
import type { User } from '../../types';
import { clearStoredToken } from '../../services/api';

interface HeaderProps {
  user?: User | null;
}

const ROLE_CONFIG: Record<string, { title: string; subtitle: string; titleColor: string }> = {
  FRAUD_ANALYST: {
    title: 'Fraud Operations Center',
    subtitle: 'DETECT · TRIAGE · INVESTIGATE · DOCUMENT',
    titleColor: 'text-slate-900',
  },
  RISK_MANAGER: {
    title: 'Risk Intelligence Command',
    subtitle: 'OVERSEE · MONITOR · GOVERN · OPTIMIZE',
    titleColor: 'text-purple-900',
  },
  ADMIN: {
    title: 'Platform Administration',
    subtitle: 'CONFIGURE · AUDIT · MANAGE · CONTROL',
    titleColor: 'text-slate-900',
  },
  VIEWER: {
    title: 'FraudShield — Read-Only View',
    subtitle: 'OBSERVE · REVIEW · REPORT',
    titleColor: 'text-slate-600',
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
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-10 shadow-xs">
      <div className="flex flex-col justify-center">
        <h1 className={`text-base font-bold leading-tight ${config.titleColor}`}>
          {config.title}
        </h1>
        <span className="text-[10px] font-semibold tracking-widest text-slate-400 leading-tight">
          {config.subtitle}
        </span>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5">
          <span className="hidden sm:inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="hidden sm:inline text-[10px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
            Live Real-Time Stream
          </span>
        </div>

        <button className="relative p-2 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100 transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full animate-ping" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full" />
        </button>

        <div className="h-6 w-px bg-slate-200" />

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-600">
            <UserIcon className="w-4 h-4" />
          </div>
          <div className="text-left hidden sm:block">
            <span className="block text-xs font-semibold text-slate-900">
              {user?.full_name || 'Fraud Analyst'}
            </span>
            <span className={`inline-block text-[10px] font-bold px-1.5 py-0.2 rounded border uppercase tracking-wider ${
              user?.role === 'ADMIN' ? 'bg-purple-50 text-purple-700 border-purple-200' :
              user?.role === 'RISK_MANAGER' ? 'bg-amber-50 text-amber-700 border-amber-200' :
              user?.role === 'VIEWER' ? 'bg-slate-100 text-slate-600 border-slate-300' :
              'bg-blue-50 text-blue-700 border-blue-200'
            }`}>
              {user?.role ? user.role.replace('_', ' ') : 'FRAUD ANALYST'}
            </span>
          </div>
          <button
            onClick={handleLogout}
            title="Log out"
            className="p-2 text-slate-400 hover:text-red-600 rounded-md hover:bg-red-50 transition-colors ml-2"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
