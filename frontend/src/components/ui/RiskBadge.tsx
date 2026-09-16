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
    LOW: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    MEDIUM: 'bg-amber-50 text-amber-700 border-amber-200',
    HIGH: 'bg-rose-50 text-rose-700 border-rose-200',
    CRITICAL: 'bg-red-100 text-red-900 border-red-300 font-bold animate-pulse',
    NEUTRAL: 'bg-slate-100 text-slate-700 border-slate-200',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border',
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
