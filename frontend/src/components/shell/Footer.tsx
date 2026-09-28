import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Lock } from 'lucide-react';

interface FooterProps {
  className?: string;
  variant?: 'default' | 'minimal';
}

export const Footer: React.FC<FooterProps> = ({ className = '', variant = 'default' }) => {
  const currentYear = new Date().getFullYear();

  if (variant === 'minimal') {
    return (
      <footer className={`py-4 px-6 text-center text-xs text-slate-500 dark:text-slate-400 ${className}`}>
        <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-2">
          <span>&copy; {currentYear} FraudShield AI. All rights reserved.</span>
          <span className="hidden sm:inline text-slate-300 dark:text-slate-700">&bull;</span>
          <Link
            to="/terms"
            className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors font-medium"
          >
            Terms &amp; Conditions
          </Link>
          <span className="text-slate-300 dark:text-slate-700">&bull;</span>
          <Link
            to="/privacy"
            className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors font-medium"
          >
            Privacy Policy
          </Link>
        </div>
      </footer>
    );
  }

  return (
    <footer
      className={`border-t border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xs py-4 px-6 text-xs text-slate-500 dark:text-slate-400 transition-colors ${className}`}
    >
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded bg-blue-600/10 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 flex items-center justify-center">
            <ShieldCheck className="w-3.5 h-3.5" />
          </div>
          <span className="font-semibold text-slate-800 dark:text-slate-200">FraudShield AI</span>
          <span className="text-slate-400 dark:text-slate-600 hidden md:inline">|</span>
          <span className="hidden md:inline text-[11px] text-slate-500 dark:text-slate-400">
            Real-Time Fraud Operations &amp; Intelligence Platform
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-slate-600 dark:text-slate-400">
          <span>&copy; {currentYear} FraudShield AI</span>
          <span className="text-slate-300 dark:text-slate-700">&bull;</span>
          <Link
            to="/terms"
            className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors font-medium"
          >
            Terms &amp; Conditions
          </Link>
          <span className="text-slate-300 dark:text-slate-700">&bull;</span>
          <Link
            to="/privacy"
            className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors font-medium"
          >
            Privacy Policy
          </Link>
          <span className="text-slate-300 dark:text-slate-700 hidden sm:inline">&bull;</span>
          <span className="hidden sm:inline-flex items-center gap-1 text-[11px] text-slate-400 dark:text-slate-500">
            <Lock className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
            TLS Encrypted
          </span>
        </div>
      </div>
    </footer>
  );
};
