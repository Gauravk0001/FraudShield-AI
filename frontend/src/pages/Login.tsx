import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, Mail, AlertCircle, Eye, UserCheck, ShieldAlert } from 'lucide-react';
import { apiRequest, setStoredToken } from '../services/api';
import { Button } from '../components/ui/Button';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@shieldbank.com');
  const [password, setPassword] = useState('AdminPass123!');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const res = await apiRequest<{ access_token: string }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      setStoredToken(res.access_token);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const fillDemoAccount = (role: 'analyst' | 'manager' | 'admin' | 'viewer') => {
    if (role === 'analyst') {
      setEmail('analyst@shieldbank.com');
      setPassword('AnalystPass123!');
    } else if (role === 'manager') {
      setEmail('manager@shieldbank.com');
      setPassword('ManagerPass123!');
    } else if (role === 'admin') {
      setEmail('admin@shieldbank.com');
      setPassword('AdminPass123!');
    } else if (role === 'viewer') {
      setEmail('viewer@shieldbank.com');
      setPassword('ViewerPass123!');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-6 bg-white dark:bg-slate-900 p-8 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-blue-600 text-white mb-3 shadow-md">
            <Shield className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">FraudShield AI</h2>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Enterprise Real-Time Fraud Operations Platform</p>
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 p-3 rounded-btn text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form className="mt-6 space-y-4" onSubmit={handleLogin}>
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
              Email Address
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Mail className="h-4 w-4" />
              </div>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-10 w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-btn text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="name@company.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
              Password
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Lock className="h-4 w-4" />
              </div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-10 w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-btn text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="••••••••"
              />
            </div>
          </div>

          <Button type="submit" variant="primary" className="w-full mt-2" isLoading={isLoading}>
            Sign In to Console
          </Button>
        </form>

        <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
          <p className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider mb-2">Quick Demo Personas:</p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => fillDemoAccount('analyst')}
              className="px-2.5 py-1.5 bg-blue-50 dark:bg-blue-950/40 hover:bg-blue-100 dark:hover:bg-blue-900/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 rounded-btn font-medium transition-colors text-left flex items-center gap-1.5"
            >
              <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
              <span>Fraud Analyst</span>
            </button>
            <button
              type="button"
              onClick={() => fillDemoAccount('manager')}
              className="px-2.5 py-1.5 bg-amber-50 dark:bg-amber-950/40 hover:bg-amber-100 dark:hover:bg-amber-900/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 rounded-btn font-medium transition-colors text-left flex items-center gap-1.5"
            >
              <UserCheck className="w-3.5 h-3.5 shrink-0" />
              <span>Risk Manager</span>
            </button>
            <button
              type="button"
              onClick={() => fillDemoAccount('admin')}
              className="px-2.5 py-1.5 bg-purple-50 dark:bg-purple-950/40 hover:bg-purple-100 dark:hover:bg-purple-900/60 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800 rounded-btn font-medium transition-colors text-left flex items-center gap-1.5"
            >
              <Shield className="w-3.5 h-3.5 shrink-0" />
              <span>Admin</span>
            </button>
            <button
              type="button"
              onClick={() => fillDemoAccount('viewer')}
              className="px-2.5 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-btn font-medium transition-colors text-left flex items-center gap-1.5"
            >
              <Eye className="w-3.5 h-3.5 shrink-0" />
              <span>Viewer</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
