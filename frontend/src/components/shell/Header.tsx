import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, User as UserIcon, Bell } from 'lucide-react';
import type { User } from '../../types';
import { clearStoredToken } from '../../services/api';

interface HeaderProps {
  user?: User | null;
}

export const Header: React.FC<HeaderProps> = ({ user }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    clearStoredToken();
    navigate('/login');
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-10 shadow-xs">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-semibold text-slate-900">Fraud Operations Center</h1>
        <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full font-medium border border-emerald-200">
          Live Real-Time Stream
        </span>
      </div>

      <div className="flex items-center gap-4">
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
            <span className="block text-[10px] text-slate-500 font-medium">
              {user?.role || 'FRAUD_ANALYST'}
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
