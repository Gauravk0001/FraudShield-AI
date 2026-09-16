import React from 'react';
import { clsx } from 'clsx';

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | 'NEUTRAL';

interface RiskBadgeProps {
  level: RiskLevel;
  score?: number;
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, className }) => {
  const styles = {
    LOW: 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
    MEDIUM: 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800',
    HIGH: 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800',
    CRITICAL: 'bg-red-100 dark:bg-red-950/60 text-red-900 dark:text-red-200 border-red-300 dark:border-red-700 font-bold animate-pulse',
    NEUTRAL: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border transition-colors',
        styles[level] || styles.NEUTRAL,
        className
      )}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      <span>{level}</span>
      {score !== undefined && (
        <span className="ml-1 opacity-80">({Math.round(score)})</span>
      )}
    </span>
  );
};
