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
  ShieldCheck,
  Cpu,
  Shield,
  TrendingUp,
  Sliders,
  Eye,
} from 'lucide-react';
import type { UserRole } from '../../types';

interface SidebarProps {
  userRole?: UserRole;
}

interface NavItem {
  label: string;
  path: string;
  icon: React.ElementType;
  roles: UserRole[];
  section?: string;
}

const NAV_ITEMS: NavItem[] = [
  // Analyst sections
  { section: 'DETECTION', label: 'Fraud Operations', path: '/', icon: LayoutDashboard, roles: ['FRAUD_ANALYST'] },
  { label: 'Transaction Intel', path: '/transactions', icon: Receipt, roles: ['FRAUD_ANALYST'] },
  { label: 'Alert Triage', path: '/alerts', icon: AlertTriangle, roles: ['FRAUD_ANALYST'] },
  { section: 'INVESTIGATION', label: 'Case Workspace', path: '/investigations', icon: Search, roles: ['FRAUD_ANALYST'] },
  { label: 'AI Copilot', path: '/copilot', icon: Bot, roles: ['FRAUD_ANALYST'] },

  // Risk Manager sections
  { section: 'OVERSIGHT', label: 'Risk Overview', path: '/', icon: TrendingUp, roles: ['RISK_MANAGER'] },
  { label: 'Risk Patterns', path: '/transactions', icon: Receipt, roles: ['RISK_MANAGER'] },
  { label: 'Alert Distribution', path: '/alerts', icon: AlertTriangle, roles: ['RISK_MANAGER'] },
  { label: 'Case Backlog', path: '/investigations', icon: Search, roles: ['RISK_MANAGER'] },
  { section: 'GOVERNANCE', label: 'Model Performance', path: '/models', icon: Cpu, roles: ['RISK_MANAGER'] },
  { label: 'AI Intelligence', path: '/copilot', icon: Bot, roles: ['RISK_MANAGER'] },
  { label: 'Risk Settings', path: '/settings', icon: Sliders, roles: ['RISK_MANAGER'] },

  // Admin sections
  { section: 'PLATFORM', label: 'Platform Overview', path: '/', icon: LayoutDashboard, roles: ['ADMIN'] },
  { label: 'Transactions', path: '/transactions', icon: Receipt, roles: ['ADMIN'] },
  { label: 'Alerts', path: '/alerts', icon: AlertTriangle, roles: ['ADMIN'] },
  { label: 'Investigations', path: '/investigations', icon: Search, roles: ['ADMIN'] },
  { section: 'ADMIN TOOLS', label: 'Model Registry', path: '/models', icon: Cpu, roles: ['ADMIN'] },
  { label: 'AI Copilot', path: '/copilot', icon: Bot, roles: ['ADMIN'] },
  { label: 'Audit Logs', path: '/audit-logs', icon: FileText, roles: ['ADMIN'] },
  { label: 'System Settings', path: '/settings', icon: Settings, roles: ['ADMIN'] },

  // Viewer sections
  { section: 'READ ONLY', label: 'Overview', path: '/', icon: Eye, roles: ['VIEWER'] },
  { label: 'Transactions', path: '/transactions', icon: Receipt, roles: ['VIEWER'] },
  { label: 'Alerts', path: '/alerts', icon: AlertTriangle, roles: ['VIEWER'] },
  { label: 'Investigations', path: '/investigations', icon: Search, roles: ['VIEWER'] },
];

const ROLE_MISSION: Record<UserRole, { tagline: string; color: string }> = {
  FRAUD_ANALYST: { tagline: 'Detect · Investigate · Decide', color: 'text-blue-400' },
  RISK_MANAGER: { tagline: 'Oversee · Govern · Optimize', color: 'text-amber-400' },
  ADMIN: { tagline: 'Configure · Audit · Control', color: 'text-purple-400' },
  VIEWER: { tagline: 'Observe · Review · Report', color: 'text-slate-400' },
};

const SECTION_COLORS: Record<string, string> = {
  DETECTION: 'text-blue-400',
  INVESTIGATION: 'text-indigo-400',
  OVERSIGHT: 'text-amber-400',
  GOVERNANCE: 'text-purple-400',
  PLATFORM: 'text-slate-400',
  'ADMIN TOOLS': 'text-purple-400',
  'READ ONLY': 'text-slate-500',
};

export const Sidebar: React.FC<SidebarProps> = ({ userRole = 'FRAUD_ANALYST' }) => {
  const allowedItems = NAV_ITEMS.filter((item) => item.roles.includes(userRole));
  const mission = ROLE_MISSION[userRole];

  // Render items grouped by section
  const rendered: React.ReactNode[] = [];
  let lastSection = '';

  allowedItems.forEach((item, idx) => {
    if (item.section && item.section !== lastSection) {
      lastSection = item.section;
      rendered.push(
        <div
          key={`section-${item.section}-${idx}`}
          className={`text-[9px] font-bold tracking-[0.15em] uppercase px-3 mt-5 mb-1 ${SECTION_COLORS[item.section] ?? 'text-slate-500'}`}
        >
          {item.section}
        </div>
      );
    }

    const Icon = item.icon;
    rendered.push(
      <NavLink
        key={`${item.path}-${item.label}`}
        to={item.path}
        end={item.path === '/'}
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
  });

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 min-h-screen">
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div>
          <span className="font-bold text-white text-base tracking-wide">FraudShield AI</span>
          <span className={`block text-[10px] font-semibold font-mono ${mission.color}`}>
            {mission.tagline}
          </span>
        </div>
      </div>

      <nav className="flex-1 px-4 py-4 space-y-0.5">
        {rendered}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-800/60 rounded-lg p-3 text-xs text-slate-400">
          <div className="flex items-center gap-1.5 mb-1">
            <Shield className="w-3.5 h-3.5 text-emerald-500" />
            <span className="font-semibold text-slate-300">Engine: Active</span>
          </div>
          <span className="block text-[11px]">XGBoost + Isolation Forest</span>
          <span className="block text-[10px] text-slate-500 mt-0.5">v1.0.0 Enterprise</span>
        </div>
      </div>
    </aside>
  );
};
