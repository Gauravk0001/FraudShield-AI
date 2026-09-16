import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Receipt,
  AlertTriangle,
  Search,
  Bot,
  FileText,
  Settings,
  ShieldCheck
} from 'lucide-react';
import type { UserRole } from '../../types';

interface SidebarProps {
  userRole?: UserRole;
}

export const Sidebar: React.FC<SidebarProps> = ({ userRole = 'FRAUD_ANALYST' }) => {
  const navItems = [
    { label: 'Overview', path: '/', icon: LayoutDashboard, roles: ['ADMIN', 'FRAUD_ANALYST', 'RISK_MANAGER', 'VIEWER'] },
    { label: 'Transactions', path: '/transactions', icon: Receipt, roles: ['ADMIN', 'FRAUD_ANALYST', 'RISK_MANAGER', 'VIEWER'] },
    { label: 'Alerts', path: '/alerts', icon: AlertTriangle, roles: ['ADMIN', 'FRAUD_ANALYST', 'RISK_MANAGER', 'VIEWER'] },
    { label: 'Investigations', path: '/investigations', icon: Search, roles: ['ADMIN', 'FRAUD_ANALYST', 'RISK_MANAGER'] },
    { label: 'AI Copilot', path: '/copilot', icon: Bot, roles: ['ADMIN', 'FRAUD_ANALYST', 'RISK_MANAGER'] },
    { label: 'Audit Logs', path: '/audit-logs', icon: FileText, roles: ['ADMIN'] },
    { label: 'Settings', path: '/settings', icon: Settings, roles: ['ADMIN'] },
  ];

  const allowedItems = navItems.filter((item) => item.roles.includes(userRole));

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 min-h-screen">
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div>
          <span className="font-bold text-white text-base tracking-wide">FraudShield AI</span>
          <span className="block text-[10px] text-slate-400 font-mono">v1.0.0 Enterprise</span>
        </div>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-1">
        {allowedItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-800/60 rounded-lg p-3 text-xs text-slate-400">
          <span className="font-semibold text-slate-300 block mb-1">Status: Active Engine</span>
          <span>XGBoost + Isolation Forest</span>
        </div>
      </div>
    </aside>
  );
};
