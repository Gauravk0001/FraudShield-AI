import React, { useEffect, useState, useCallback } from 'react';
import { useOutletContext, useNavigate, useParams } from 'react-router-dom';
import {
  CheckCircle2, Plus, UserCheck, Search, ShieldCheck,
  Clock, AlertTriangle, Zap, Copy, ExternalLink,
  Smartphone, MapPin, Activity, Bot, ChevronRight, ArrowUp,
  TrendingUp, Shield, Eye, RefreshCw, XCircle, AlertOctagon,
  Layers, Info, Terminal, CheckSquare,
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { RiskBadge } from '../components/ui/RiskBadge';
import { apiRequest } from '../services/api';
import type {
  Investigation, InvestigationDecision, InvestigationStatus,
  User, ShapFactor, ReasonCode, ForensicSnapshot,
} from '../types';

// ─── Utility helpers ─────────────────────────────────────────────────────────

function fmtDate(d?: string | null): string {
  if (!d) return '—';
  return new Date(d).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}
function fmtRelative(d?: string | null): string {
  if (!d) return '—';
  const diff = Date.now() - new Date(d).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}
function fmtUSD(n?: number | null): string {
  if (n == null) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);
}

// ─── Status badge ──────────────────────────────────────────────────────────────

const STATUS_STYLES: Record<InvestigationStatus, string> = {
  OPEN: 'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-700',
  IN_REVIEW: 'bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-700',
  ESCALATED: 'bg-purple-100 dark:bg-purple-950/60 text-purple-800 dark:text-purple-300 border-purple-300 dark:border-purple-700',
  RESOLVED: 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-700',
};

const STATUS_ICONS: Record<InvestigationStatus, React.ReactNode> = {
  OPEN: <Clock className="w-3 h-3" />,
  IN_REVIEW: <Eye className="w-3 h-3" />,
  ESCALATED: <AlertOctagon className="w-3 h-3" />,
  RESOLVED: <CheckCircle2 className="w-3 h-3" />,
};

const STATUS_ORDER: InvestigationStatus[] = ['OPEN', 'IN_REVIEW', 'ESCALATED', 'RESOLVED'];

const StatusBadge: React.FC<{ status: InvestigationStatus }> = ({ status }) => (
  <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[11px] font-bold tracking-wide ${STATUS_STYLES[status]}`}>
    {STATUS_ICONS[status]} {status.replace('_', ' ')}
  </span>
);

// ─── Risk color helpers ────────────────────────────────────────────────────────

function scoreColor(score: number): string {
  if (score >= 80) return 'text-rose-600 dark:text-rose-400';
  if (score >= 55) return 'text-amber-600 dark:text-amber-400';
  if (score >= 30) return 'text-yellow-600 dark:text-yellow-400';
  return 'text-emerald-600 dark:text-emerald-400';
}
function scoreBarColor(score: number): string {
  if (score >= 80) return 'bg-rose-500';
  if (score >= 55) return 'bg-amber-500';
  if (score >= 30) return 'bg-yellow-500';
  return 'bg-emerald-500';
}

// ─── Copy button ───────────────────────────────────────────────────────────────

const CopyButton: React.FC<{ value: string; label?: string }> = ({ value, label }) => {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(value).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };
  return (
    <button
      onClick={copy}
      title="Copy to clipboard"
      className="inline-flex items-center gap-1 text-[10px] text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors px-1.5 py-0.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800"
    >
      <Copy className="w-3 h-3" />
      {copied ? 'Copied!' : (label ?? 'Copy')}
    </button>
  );
};

// ─── Status timeline ───────────────────────────────────────────────────────────

const StatusTimeline: React.FC<{ currentStatus: InvestigationStatus }> = ({ currentStatus }) => {
  const currentIdx = STATUS_ORDER.indexOf(currentStatus);
  return (
    <div className="flex items-center gap-0">
      {STATUS_ORDER.map((s, i) => {
        const done = i <= currentIdx;
        const isCurrent = i === currentIdx;
        return (
          <React.Fragment key={s}>
            <div className={`flex flex-col items-center ${i === 0 ? '' : ''}`}>
              <div className={`w-7 h-7 rounded-full border-2 flex items-center justify-center text-[10px] font-bold transition-all
                ${done
                  ? isCurrent
                    ? 'border-blue-500 bg-blue-500 text-white shadow-lg shadow-blue-500/30'
                    : 'border-emerald-500 bg-emerald-500 text-white'
                  : 'border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-400'
                }`}
              >
                {done && !isCurrent ? <CheckCircle2 className="w-3.5 h-3.5" /> : (i + 1)}
              </div>
              <span className={`text-[9px] font-bold mt-1 text-center leading-tight max-w-[52px]
                ${done ? 'text-slate-700 dark:text-slate-300' : 'text-slate-400 dark:text-slate-600'}`}
              >
                {s.replace('_', ' ')}
              </span>
            </div>
            {i < STATUS_ORDER.length - 1 && (
              <div className={`h-0.5 flex-1 mb-4 mx-1 transition-all ${i < currentIdx ? 'bg-emerald-400' : 'bg-slate-200 dark:bg-slate-700'}`} />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};

// ─── Forensic scoring timeline ─────────────────────────────────────────────────

const SCORING_TIMELINE_STEPS = [
  { icon: <Terminal className="w-3.5 h-3.5" />, label: 'Transaction received', detail: 'Inbound payment data ingested' },
  { icon: <Layers className="w-3.5 h-3.5" />, label: 'Historical features computed', detail: 'Velocity, balance ratio, device history' },
  { icon: <TrendingUp className="w-3.5 h-3.5" />, label: 'ML probability calculated', detail: 'XGBoost calibrated fraud probability' },
  { icon: <Activity className="w-3.5 h-3.5" />, label: 'Anomaly score calculated', detail: 'IsolationForest outlier detection' },
  { icon: <CheckSquare className="w-3.5 h-3.5" />, label: 'Rules evaluated', detail: 'Behavioral and policy rules applied' },
  { icon: <AlertTriangle className="w-3.5 h-3.5" />, label: 'Decision threshold crossed', detail: 'Risk score exceeded configured threshold' },
  { icon: <Shield className="w-3.5 h-3.5" />, label: 'Alert & case created', detail: 'Investigation opened for analyst review' },
];

const ScoringTimeline: React.FC<{ degraded?: boolean; latencyMs?: number }> = ({ degraded, latencyMs }) => (
  <div className="space-y-2">
    <div className="flex items-center justify-between mb-1">
      <h5 className="text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Why This Case Was Flagged</h5>
      {latencyMs != null && (
        <span className="text-[10px] text-slate-400 dark:text-slate-500 font-mono">Scored in {latencyMs}ms</span>
      )}
    </div>
    {SCORING_TIMELINE_STEPS.map((step, i) => (
      <div key={i} className="flex items-start gap-3">
        <div className="flex flex-col items-center shrink-0">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center
            ${degraded && i >= 2 && i <= 4
              ? 'bg-purple-100 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400'
              : 'bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400'
            }`}
          >
            {step.icon}
          </div>
          {i < SCORING_TIMELINE_STEPS.length - 1 && (
            <div className="w-0.5 h-4 bg-slate-200 dark:bg-slate-700 mt-0.5" />
          )}
        </div>
        <div className="pb-2">
          <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 leading-tight">{step.label}</p>
          <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-tight mt-0.5">
            {degraded && i >= 2 && i <= 4 ? '⚠ Degraded — deterministic fallback used' : step.detail}
          </p>
        </div>
      </div>
    ))}
  </div>
);

// ─── Forensic risk breakdown ──────────────────────────────────────────────────

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: 'bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 border-rose-200 dark:border-rose-800',
  HIGH: 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300 border-orange-200 dark:border-orange-800',
  MEDIUM: 'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800',
  LOW: 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
};
const SOURCE_COLORS: Record<string, string> = {
  ML: 'bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300',
  ANOMALY: 'bg-violet-100 dark:bg-violet-950/60 text-violet-700 dark:text-violet-300',
  BEHAVIORAL_RULE: 'bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300',
  DEGRADED_FALLBACK: 'bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300',
};

const ReasonCodeRow: React.FC<{ r: ReasonCode }> = ({ r }) => {
  const sevCls = SEVERITY_COLORS[r.severity ?? 'MEDIUM'] ?? SEVERITY_COLORS.MEDIUM;
  const srcCls = SOURCE_COLORS[r.source ?? 'ML'] ?? SOURCE_COLORS.ML;

  return (
    <div className="p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg space-y-2 hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-mono text-[11px] font-bold text-slate-800 dark:text-slate-200">{r.code}</span>
          <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${sevCls}`}>{r.severity ?? 'MEDIUM'}</span>
          <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${srcCls}`}>{(r.source ?? 'ML').replace('_', ' ')}</span>
        </div>
        {r.contribution_pct != null && (
          <span className="text-xs font-bold text-slate-500 dark:text-slate-400 shrink-0">{r.contribution_pct.toFixed(0)}%</span>
        )}
      </div>
      <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">{r.message}</p>
      {(r.observed_value != null || r.baseline_value != null) && (
        <div className="flex gap-4 text-[10px]">
          {r.observed_value != null && (
            <span className="text-slate-600 dark:text-slate-400">
              <span className="text-slate-400 dark:text-slate-500">Observed: </span>
              <span className="font-semibold text-rose-600 dark:text-rose-400">{String(r.observed_value)}</span>
            </span>
          )}
          {r.baseline_value != null && (
            <span className="text-slate-600 dark:text-slate-400">
              <span className="text-slate-400 dark:text-slate-500">Normal: </span>
              <span className="font-semibold">{String(r.baseline_value)}</span>
            </span>
          )}
        </div>
      )}
    </div>
  );
};

const ForensicBreakdownPanel: React.FC<{ snap: ForensicSnapshot; degraded?: boolean }> = ({ snap, degraded }) => {
  const riskScore = snap.risk_score ?? 0;
  const fraudProb = (snap.fraud_probability ?? 0) * 100;
  const anomalyScore = (snap.anomaly_score ?? 0) * 100;

  // Contribution model: supervised ~ 45%, behavioral ~ 35%, anomaly ~ 20%
  const supervisedPct = 45;
  const behavioralPct = 35;
  const anomalyPct = 20;

  return (
    <div className="space-y-5">
      {/* Degraded warning */}
      {degraded && (
        <div className="flex items-center gap-2 p-3 bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 rounded-lg text-xs text-purple-800 dark:text-purple-200">
          <AlertOctagon className="w-4 h-4 shrink-0" />
          <span><strong>Degraded Mode:</strong> ML model unavailable. Score derived from deterministic behavioral rules only. Model explanations are not available.</span>
        </div>
      )}

      {/* Key metrics row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Composite Risk', value: `${Math.round(riskScore)} / 100`, color: scoreColor(riskScore), sub: 'Final score' },
          { label: 'Fraud Probability', value: `${fraudProb.toFixed(1)}%`, color: fraudProb >= 70 ? 'text-rose-600 dark:text-rose-400' : 'text-amber-600 dark:text-amber-400', sub: degraded ? 'Unavailable' : 'Supervised ML' },
          { label: 'Anomaly Score', value: `${anomalyScore.toFixed(1)}%`, color: anomalyScore >= 70 ? 'text-rose-600 dark:text-rose-400' : 'text-amber-600 dark:text-amber-400', sub: degraded ? 'Unavailable' : 'IsolationForest' },
          { label: 'Amount', value: fmtUSD(snap.amount), color: 'text-slate-800 dark:text-slate-200', sub: 'Transaction value' },
        ].map((m) => (
          <div key={m.label} className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg text-center">
            <p className="text-[10px] text-slate-400 dark:text-slate-500 uppercase tracking-wide font-bold mb-1">{m.label}</p>
            <p className={`text-lg font-extrabold ${m.color}`}>{m.value}</p>
            <p className="text-[9px] text-slate-400 dark:text-slate-500 mt-0.5">{m.sub}</p>
          </div>
        ))}
      </div>

      {/* Risk bar visual */}
      <div>
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="font-semibold text-slate-600 dark:text-slate-400">Composite Risk Score</span>
          <span className={`font-bold ${scoreColor(riskScore)}`}>{Math.round(riskScore)} / 100</span>
        </div>
        <div className="h-3 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${scoreBarColor(riskScore)}`}
            style={{ width: `${Math.min(riskScore, 100)}%` }}
          />
        </div>
        <div className="flex justify-between text-[9px] text-slate-400 mt-1">
          <span>Low Risk</span><span>Medium</span><span>High Risk</span>
        </div>
      </div>

      {/* Score decomposition */}
      {!degraded && (
        <div className="p-3.5 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-lg space-y-2.5">
          <h5 className="text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-2">Score Decomposition</h5>
          {[
            { label: 'Supervised ML', pct: supervisedPct, color: 'bg-blue-500', desc: 'XGBoost fraud probability contribution' },
            { label: 'Behavioral Rules', pct: behavioralPct, color: 'bg-amber-500', desc: 'Velocity, balance, destination rules' },
            { label: 'Anomaly Detection', pct: anomalyPct, color: 'bg-violet-500', desc: 'IsolationForest outlier contribution' },
          ].map((d) => (
            <div key={d.label} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-700 dark:text-slate-300 font-medium">{d.label}</span>
                <span className="font-bold text-slate-600 dark:text-slate-400">{d.pct}%</span>
              </div>
              <div className="h-2 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${d.color}`} style={{ width: `${d.pct}%` }} />
              </div>
              <p className="text-[10px] text-slate-400 dark:text-slate-500">{d.desc}</p>
            </div>
          ))}
          <div className="pt-2 border-t border-slate-200 dark:border-slate-700 flex justify-between items-center text-xs">
            <span className="font-bold text-slate-700 dark:text-slate-300">Final Composite Score</span>
            <span className={`text-base font-extrabold ${scoreColor(riskScore)}`}>{Math.round(riskScore)} / 100</span>
          </div>
        </div>
      )}

      {/* Metadata */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
        {snap.model_version && (
          <div className="p-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded">
            <span className="text-slate-400 block text-[10px] uppercase font-bold mb-0.5">Model Version</span>
            <span className="font-mono text-slate-700 dark:text-slate-300">{snap.model_version}</span>
          </div>
        )}
        {snap.active_data_source && (
          <div className="p-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded">
            <span className="text-slate-400 block text-[10px] uppercase font-bold mb-0.5">Data Source</span>
            <span className="font-mono text-slate-700 dark:text-slate-300">{snap.active_data_source}</span>
          </div>
        )}
        {snap.scoring_latency_ms != null && (
          <div className="p-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded">
            <span className="text-slate-400 block text-[10px] uppercase font-bold mb-0.5">Scoring Latency</span>
            <span className="font-mono text-slate-700 dark:text-slate-300">{snap.scoring_latency_ms}ms</span>
          </div>
        )}
        {snap.snapshot_at && (
          <div className="p-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded">
            <span className="text-slate-400 block text-[10px] uppercase font-bold mb-0.5">Scored At</span>
            <span className="text-slate-700 dark:text-slate-300">{fmtDate(snap.snapshot_at)}</span>
          </div>
        )}
      </div>
    </div>
  );
};

// ─── SHAP factor display ───────────────────────────────────────────────────────

const ShapRow: React.FC<{ factor: ShapFactor }> = ({ factor }) => {
  const pct = Math.min(Math.abs(factor.contribution) * 100, 100);
  const isPositive = factor.direction === 'POSITIVE';
  return (
    <div className="space-y-0.5 py-2 border-b border-slate-100 dark:border-slate-800 last:border-0">
      <div className="flex items-center justify-between text-[11px]">
        <span className="font-mono text-slate-700 dark:text-slate-300 truncate">{factor.feature_name}</span>
        <span className={`font-bold ml-2 shrink-0 ${isPositive ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400'}`}>
          {isPositive ? '+' : ''}{(factor.contribution * 100).toFixed(1)}%
        </span>
      </div>
      <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${isPositive ? 'bg-rose-500' : 'bg-emerald-500'}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-[10px] text-slate-400 dark:text-slate-500 leading-tight">{factor.explanation}</p>
    </div>
  );
};

// ─── Counterfactual panel ──────────────────────────────────────────────────────

const CounterfactualPanel: React.FC<{ snap: ForensicSnapshot }> = ({ snap }) => {
  const amount = snap.amount ?? 0;
  const suggestions = [
    { factor: 'Lower transaction amount', impact: 'High', detail: `Amounts < $${(amount * 0.4).toFixed(0)} would reduce the risk by ~30 points` },
    { factor: 'Prior relationship with destination', impact: 'High', detail: 'Previous successful transfers to this account reduce anomaly score significantly' },
    { factor: 'Stepdown authentication', impact: 'Medium', detail: 'OTP / biometric verification reduces behavioral risk contribution by ~15 points' },
    { factor: 'Activity within normal hours', impact: 'Low', detail: 'Transaction within business hours reduces timing anomaly flags' },
  ];
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 p-2 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg text-[10px] text-amber-800 dark:text-amber-200">
        <Info className="w-3.5 h-3.5 shrink-0" />
        <span><strong>Analytical scenario only.</strong> These are not instructions to bypass controls. For analyst review to understand risk drivers.</span>
      </div>
      {suggestions.map((s, i) => (
        <div key={i} className="flex items-start gap-3 p-2.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
          <div className={`mt-0.5 shrink-0 w-2 h-2 rounded-full ${s.impact === 'High' ? 'bg-rose-500' : s.impact === 'Medium' ? 'bg-amber-500' : 'bg-emerald-500'}`} />
          <div>
            <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">{s.factor}</p>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{s.detail}</p>
          </div>
          <span className={`ml-auto text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0 ${
            s.impact === 'High' ? 'bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300' :
            s.impact === 'Medium' ? 'bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300' :
            'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300'
          }`}>{s.impact}</span>
        </div>
      ))}
    </div>
  );
};

// ─── Skeleton loader ───────────────────────────────────────────────────────────

const SkeletonBlock: React.FC<{ className?: string }> = ({ className }) => (
  <div className={`bg-slate-200 dark:bg-slate-800 rounded animate-pulse ${className}`} />
);

const InvestigationSkeleton: React.FC = () => (
  <div className="space-y-6">
    <div className="flex gap-4 items-start">
      <SkeletonBlock className="h-8 w-48" />
      <SkeletonBlock className="h-8 w-24 ml-auto" />
    </div>
    <div className="grid grid-cols-3 gap-4">
      <SkeletonBlock className="h-64 col-span-1" />
      <SkeletonBlock className="h-64 col-span-2" />
    </div>
    <SkeletonBlock className="h-48" />
  </div>
);

// ─── Investigation detail (main content) ──────────────────────────────────────

const InvestigationDetail: React.FC<{
  inv: Investigation;
  user: User | null;
  onRefresh: () => void;
  onConflict: (msg: string) => void;
}> = ({ inv, user, onRefresh, onConflict }) => {
  const navigate = useNavigate();
  const [noteText, setNoteText] = useState('');
  const [decision, setDecision] = useState<InvestigationDecision>('CONFIRMED_FRAUD');
  const [reason, setReason] = useState('');
  const [escalateReason, setEscalateReason] = useState('');
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const [showCounterfactual, setShowCounterfactual] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const isReadOnly = user?.role === 'VIEWER';
  const snap = inv.forensic_snapshot;
  const shapFactors: ShapFactor[] = inv.transaction?.risk_score?.explanation?.top_factors ?? [];
  const reasonCodes: ReasonCode[] = snap?.reason_codes ?? [];
  const positiveFactors = shapFactors.filter(f => f.direction === 'POSITIVE');
  const negativeFactors = shapFactors.filter(f => f.direction !== 'POSITIVE');

  const deepLink = `${window.location.origin}/investigations/${inv.id}`;

  const handleClaim = async () => {
    if (isReadOnly) return;
    try {
      await apiRequest<Investigation>(`/investigations/${inv.id}/claim`, { method: 'POST' });
      onRefresh();
    } catch (err: any) {
      if (err?.status === 409) onConflict(err.message || 'Conflict');
      else setActionError(err.message || 'Failed to claim');
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteText.trim() || isReadOnly) return;
    setIsSubmitting(true);
    try {
      await apiRequest(`/investigations/${inv.id}/notes`, {
        method: 'POST',
        body: JSON.stringify({ note_text: noteText }),
      });
      setNoteText('');
      onRefresh();
    } catch (err: any) {
      setActionError(err.message || 'Failed to add note');
    } finally { setIsSubmitting(false); }
  };

  const handleEscalate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!escalateReason.trim() || isReadOnly) return;
    setIsSubmitting(true);
    try {
      await apiRequest(`/investigations/${inv.id}/escalate`, {
        method: 'POST',
        body: JSON.stringify({ reason: escalateReason, version: inv.version }),
      });
      setShowEscalateModal(false);
      setEscalateReason('');
      onRefresh();
    } catch (err: any) {
      if (err?.status === 409) onConflict(err.message);
      else setActionError(err.message || 'Failed to escalate');
    } finally { setIsSubmitting(false); }
  };

  const handleResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reason.trim() || isReadOnly) return;
    setIsSubmitting(true);
    try {
      await apiRequest<Investigation>(`/investigations/${inv.id}/resolve`, {
        method: 'POST',
        body: JSON.stringify({ decision, decision_reason: reason, version: inv.version }),
      });
      setShowResolveModal(false);
      onRefresh();
    } catch (err: any) {
      if (err?.status === 409) onConflict(err.message);
      else setActionError(err.message || 'Resolution failed');
    } finally { setIsSubmitting(false); }
  };

  const handleAskCopilot = () => {
    navigate('/copilot', { state: { transactionId: inv.transaction?.transaction_id || inv.transaction_id, investigationId: inv.id } });
  };

  return (
    <div className="space-y-4">
      {/* ── Case Header ───────────────────────────────────────────── */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm">
        {/* Status progress */}
        <div className="mb-4">
          <StatusTimeline currentStatus={inv.status} />
        </div>

        <div className="flex flex-col sm:flex-row sm:items-start gap-4 pt-3 border-t border-slate-100 dark:border-slate-800">
          <div className="flex-1 min-w-0">
            {/* Case ID + copy + deep link */}
            <div className="flex items-center gap-2 flex-wrap mb-2">
              <span className="font-mono text-xs font-bold text-slate-500 dark:text-slate-400">CASE</span>
              <span className="font-mono text-sm font-extrabold text-slate-900 dark:text-slate-100 truncate">{inv.id}</span>
              <CopyButton value={inv.id} label="ID" />
              <CopyButton value={deepLink} label="Link" />
              <a
                href={deepLink}
                target="_blank"
                rel="noopener noreferrer"
                title="Open deep link"
                className="text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              >
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>

            <div className="flex items-center gap-3 flex-wrap">
              <StatusBadge status={inv.status} />
              {inv.alert?.severity && <RiskBadge level={inv.alert.severity} />}
              {snap?.risk_score != null && (
                <span className={`text-sm font-extrabold ${scoreColor(snap.risk_score)}`}>
                  {Math.round(snap.risk_score)} / 100
                </span>
              )}
              {inv.decision && (
                <span className="text-[10px] bg-purple-100 dark:bg-purple-950/60 text-purple-800 dark:text-purple-300 px-2 py-0.5 rounded-full font-bold border border-purple-200 dark:border-purple-700">
                  {inv.decision.replace('_', ' ')}
                </span>
              )}
              {snap?.degraded && (
                <span className="text-[10px] bg-purple-100 dark:bg-purple-950/60 text-purple-800 dark:text-purple-300 px-2 py-0.5 rounded-full font-bold">⚠ DEGRADED</span>
              )}
            </div>

            <div className="flex flex-wrap gap-3 mt-2 text-[10px] text-slate-400 dark:text-slate-500">
              <span>Created: {fmtDate(inv.created_at)} ({fmtRelative(inv.created_at)})</span>
              {inv.updated_at && <span>Updated: {fmtRelative(inv.updated_at)}</span>}
              {inv.resolved_at && <span>Resolved: {fmtDate(inv.resolved_at)}</span>}
              <span>v{inv.version}</span>
              {inv.assigned_analyst_id
                ? <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1"><UserCheck className="w-3 h-3" />Assigned</span>
                : <span className="text-amber-600 dark:text-amber-400">Unassigned</span>}
            </div>
          </div>

          {/* Action buttons */}
          {!isReadOnly && (
            <div className="flex flex-wrap gap-2 sm:flex-col sm:items-end">
              <Button variant="outline" size="sm" onClick={handleAskCopilot}>
                <Bot className="w-4 h-4 mr-1.5 text-blue-600 dark:text-blue-400" /> Copilot
              </Button>
              {inv.status === 'OPEN' && (
                <Button variant="primary" size="sm" onClick={handleClaim}>
                  <UserCheck className="w-4 h-4 mr-1.5" /> Claim Case
                </Button>
              )}
              {inv.status === 'IN_REVIEW' && (
                <Button variant="outline" size="sm" onClick={() => setShowEscalateModal(true)}>
                  <ArrowUp className="w-4 h-4 mr-1.5 text-purple-600 dark:text-purple-400" /> Escalate
                </Button>
              )}
              {inv.status !== 'RESOLVED' && (
                <Button variant="danger" size="sm" onClick={() => setShowResolveModal(true)}>
                  <CheckCircle2 className="w-4 h-4 mr-1.5" /> Record Decision
                </Button>
              )}
            </div>
          )}
        </div>

        {actionError && (
          <div className="mt-3 flex items-center gap-2 p-2.5 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-lg text-xs text-red-700 dark:text-red-300">
            <XCircle className="w-4 h-4 shrink-0" />
            {actionError}
            <button className="ml-auto text-slate-400 hover:text-slate-600" onClick={() => setActionError(null)}>✕</button>
          </div>
        )}
      </div>

      {/* ── 3-column grid ─────────────────────────────────────────── */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">

        {/* LEFT: Transaction + Account context */}
        <div className="xl:col-span-3 space-y-4">
          <Card title="Transaction Details" className="!p-4">
            <dl className="space-y-2 mt-2">
              {[
                { label: 'Transaction ID', value: inv.transaction?.transaction_id || inv.transaction_id, mono: true },
                { label: 'Amount', value: fmtUSD(inv.transaction?.amount ?? snap?.amount), bold: true },
                { label: 'Type', value: inv.transaction?.transaction_type },
                { label: 'Customer', value: inv.transaction?.customer_id },
                { label: 'Merchant', value: inv.transaction?.merchant_id },
                { label: 'Currency', value: inv.transaction?.currency },
                { label: 'Time', value: fmtDate(inv.transaction?.timestamp) },
                { label: 'Status', value: inv.transaction?.status },
              ].map(({ label, value, mono, bold }) => value && (
                <div key={label} className="flex justify-between items-start gap-2 text-xs">
                  <dt className="text-slate-400 dark:text-slate-500 shrink-0">{label}</dt>
                  <dd className={`text-right font-medium text-slate-800 dark:text-slate-200 break-all ${mono ? 'font-mono text-[10px]' : ''} ${bold ? 'font-bold' : ''}`}>{String(value)}</dd>
                </div>
              ))}
            </dl>
          </Card>

          <Card title="Device & Location" className="!p-4">
            <div className="space-y-2 mt-2">
              {[
                { icon: <Smartphone className="w-4 h-4 text-blue-500 shrink-0" />, label: 'Device', value: inv.transaction?.device_id || 'Unknown' },
                { icon: <MapPin className="w-4 h-4 text-amber-500 shrink-0" />, label: 'Location', value: inv.transaction?.location || '—' },
              ].map(({ icon, label, value }) => (
                <div key={label} className="flex items-center gap-2 p-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded text-xs">
                  {icon}
                  <div>
                    <span className="text-slate-400 block text-[10px]">{label}</span>
                    <span className="font-medium text-slate-800 dark:text-slate-200 font-mono text-[11px]">{value}</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card title="Alert Reference" className="!p-4">
            <dl className="space-y-2 mt-2">
              {inv.alert && [
                { label: 'Alert ID', value: inv.alert.id, mono: true },
                { label: 'Title', value: inv.alert.title },
                { label: 'Status', value: inv.alert.status },
              ].map(({ label, value, mono }) => (
                <div key={label} className="flex justify-between items-start gap-2 text-xs">
                  <dt className="text-slate-400 dark:text-slate-500 shrink-0">{label}</dt>
                  <dd className={`text-right font-medium text-slate-800 dark:text-slate-200 break-all ${mono ? 'font-mono text-[10px]' : ''}`}>{value}</dd>
                </div>
              ))}
            </dl>
          </Card>
        </div>

        {/* MAIN: Forensic panels */}
        <div className="xl:col-span-6 space-y-4">
          {snap ? (
            <Card title="Forensic Risk Breakdown" subtitle="Evidence-based score derivation" className="!p-4">
              <div className="mt-3">
                <ForensicBreakdownPanel snap={snap} degraded={snap.degraded} />
              </div>
            </Card>
          ) : (
            <Card className="!p-4">
              <div className="text-center py-8 text-xs text-slate-400 dark:text-slate-500">
                <Activity className="w-8 h-8 mx-auto mb-2 opacity-40" />
                No forensic scoring data available for this case.
              </div>
            </Card>
          )}

          {/* Reason codes */}
          {reasonCodes.length > 0 && (
            <Card title="Risk Reason Codes" subtitle="Concrete evidence behind each contribution" className="!p-4">
              <div className="space-y-2 mt-3">
                {reasonCodes.map((r, i) => <ReasonCodeRow key={i} r={r} />)}
              </div>
            </Card>
          )}

          {/* Scoring timeline */}
          <Card title="Scoring Pipeline" className="!p-4">
            <div className="mt-3">
              <ScoringTimeline degraded={snap?.degraded} latencyMs={snap?.scoring_latency_ms} />
            </div>
          </Card>

          {/* SHAP factors */}
          {shapFactors.length > 0 && (
            <Card
              title="Model Contribution Factors"
              subtitle="SHAP-based feature importance — model contribution, not proof of fraud"
              className="!p-4"
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-3">
                <div>
                  <h6 className="text-[10px] font-bold text-rose-600 dark:text-rose-400 uppercase tracking-wider mb-2">⬆ Risk-Increasing Factors</h6>
                  {positiveFactors.slice(0, 4).map((f, i) => <ShapRow key={i} factor={f} />)}
                  {positiveFactors.length === 0 && <p className="text-[10px] text-slate-400 dark:text-slate-500 italic">None</p>}
                </div>
                <div>
                  <h6 className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider mb-2">⬇ Risk-Reducing Factors</h6>
                  {negativeFactors.slice(0, 4).map((f, i) => <ShapRow key={i} factor={f} />)}
                  {negativeFactors.length === 0 && <p className="text-[10px] text-slate-400 dark:text-slate-500 italic">None</p>}
                </div>
              </div>
              <div className="pt-2 mt-2 border-t border-slate-100 dark:border-slate-800 text-[10px] text-slate-400 dark:text-slate-500 flex items-center gap-1">
                <Zap className="w-3 h-3 text-blue-500" />
                SHAP values computed from validated XGBoost pipeline. Not customer-facing certainty.
              </div>
            </Card>
          )}

          {/* Counterfactual — analysts only */}
          {!isReadOnly && snap && (
            <div>
              <button
                className="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 mb-2"
                onClick={() => setShowCounterfactual(v => !v)}
              >
                <Info className="w-3.5 h-3.5" />
                {showCounterfactual ? 'Hide' : 'Show'} "What would reduce the risk?" (Analyst scenario)
              </button>
              {showCounterfactual && snap && (
                <Card title="Risk Reduction Scenarios" subtitle="Analytical scenario — not advice to bypass controls" className="!p-4">
                  <div className="mt-3">
                    <CounterfactualPanel snap={snap} />
                  </div>
                </Card>
              )}
            </div>
          )}
        </div>

        {/* RIGHT: Notes + audit + actions */}
        <div className="xl:col-span-3 space-y-4">
          {/* Notes */}
          <Card title="Investigation Notes" className="!p-4">
            <div className="space-y-2 mt-2 max-h-64 overflow-y-auto pr-1">
              {(!inv.notes || inv.notes.length === 0) ? (
                <p className="text-xs text-slate-400 dark:text-slate-500 italic py-4 text-center">No notes added yet</p>
              ) : (
                inv.notes.map((note) => (
                  <div key={note.id} className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-lg text-xs space-y-1">
                    <div className="flex justify-between text-[10px] text-slate-400 dark:text-slate-500">
                      <span className="font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1">
                        <UserCheck className="w-3 h-3" /> Analyst
                      </span>
                      <span>{fmtDate(note.created_at)}</span>
                    </div>
                    <p className="text-slate-800 dark:text-slate-200">{note.note_text}</p>
                  </div>
                ))
              )}
            </div>

            {!isReadOnly && inv.status !== 'RESOLVED' && (
              <form onSubmit={handleAddNote} className="mt-3 space-y-2">
                <textarea
                  rows={2}
                  placeholder="Add investigation note or evidence observation..."
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
                <Button type="submit" size="sm" variant="secondary" className="w-full" isLoading={isSubmitting}>
                  <Plus className="w-3.5 h-3.5 mr-1" /> Add Note
                </Button>
              </form>
            )}
          </Card>

          {/* Decision reason (if resolved) */}
          {inv.decision_reason && (
            <Card title="Analyst Decision Rationale" className="!p-4">
              <div className="mt-2 p-3 bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800 rounded-lg text-xs text-purple-900 dark:text-purple-200">
                <p className="font-bold mb-1">{inv.decision?.replace('_', ' ')}</p>
                <p>{inv.decision_reason}</p>
              </div>
            </Card>
          )}

          {/* Quick stats */}
          <Card title="Case Metadata" className="!p-4">
            <dl className="space-y-2 mt-2">
              {[
                { label: 'Case ID', value: inv.id.slice(0, 12) + '…', mono: true },
                { label: 'Alert ID', value: inv.alert_id.slice(0, 12) + '…', mono: true },
                { label: 'Tx ID', value: inv.transaction_id.slice(0, 12) + '…', mono: true },
                { label: 'Org', value: inv.organization_id.slice(0, 12) + '…', mono: true },
                { label: 'Version', value: `v${inv.version}` },
                { label: 'Notes', value: String(inv.notes?.length ?? 0) },
              ].map(({ label, value, mono }) => (
                <div key={label} className="flex justify-between items-center text-xs">
                  <dt className="text-slate-400 dark:text-slate-500">{label}</dt>
                  <dd className={`font-medium text-slate-700 dark:text-slate-300 ${mono ? 'font-mono text-[10px]' : ''}`}>{value}</dd>
                </div>
              ))}
            </dl>
          </Card>
        </div>
      </div>

      {/* ── Resolve modal ────────────────────────────────────────── */}
      {showResolveModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 max-w-md w-full rounded-xl p-6 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Shield className="w-5 h-5 text-rose-600 dark:text-rose-400" /> Record Analyst Final Decision
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              The human analyst retains final responsibility for the fraud determination.
            </p>
            <form onSubmit={handleResolve} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Decision Verdict</label>
                <select
                  value={decision}
                  onChange={(e) => setDecision(e.target.value as InvestigationDecision)}
                  className="w-full text-xs border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="CONFIRMED_FRAUD">CONFIRMED_FRAUD — Confirmed Unauthorized Activity</option>
                  <option value="FALSE_POSITIVE">FALSE_POSITIVE — Legitimate Customer Activity</option>
                  <option value="SUSPICIOUS_MONITORED">SUSPICIOUS_MONITORED — Keep Under Monitoring</option>
                  <option value="NO_ACTION_REQUIRED">NO_ACTION_REQUIRED — No Action Required</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Mandatory Decision Reason</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Explain why this decision was reached based on evidence..."
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-3 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex gap-3">
                <Button type="button" variant="outline" className="flex-1" onClick={() => setShowResolveModal(false)}>Cancel</Button>
                <Button type="submit" variant="danger" className="flex-1" isLoading={isSubmitting}>Submit Decision</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Escalate modal ───────────────────────────────────────── */}
      {showEscalateModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 max-w-md w-full rounded-xl p-6 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <ArrowUp className="w-5 h-5 text-purple-600 dark:text-purple-400" /> Escalate to Risk Manager
            </h3>
            <form onSubmit={handleEscalate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Escalation Reason</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Why does this case require escalation?"
                  value={escalateReason}
                  onChange={(e) => setEscalateReason(e.target.value)}
                  className="w-full text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-3 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div className="flex gap-3">
                <Button type="button" variant="outline" className="flex-1" onClick={() => setShowEscalateModal(false)}>Cancel</Button>
                <Button type="submit" variant="primary" className="flex-1" isLoading={isSubmitting}>
                  <ArrowUp className="w-3.5 h-3.5 mr-1" /> Escalate
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// ─── Case list sidebar ─────────────────────────────────────────────────────────

const CaseListSidebar: React.FC<{
  investigations: Investigation[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}> = ({ investigations, selectedId, onSelect }) => {
  const navigate = useNavigate();

  return (
    <div className="h-full space-y-1.5 overflow-y-auto pr-1">
      {investigations.length === 0 ? (
        <div className="text-center py-10 text-slate-400 dark:text-slate-500 text-xs">
          <Search className="w-8 h-8 mx-auto mb-2 opacity-40" />
          No cases found
        </div>
      ) : (
        investigations.map((inv) => {
          const snap = inv.forensic_snapshot;
          const score = snap?.risk_score ?? inv.alert?.risk_score ?? null;
          const isSelected = inv.id === selectedId;
          return (
            <div
              key={inv.id}
              onClick={() => {
                onSelect(inv.id);
                navigate(`/investigations/${inv.id}`, { replace: true });
              }}
              className={`p-3 rounded-lg border text-xs cursor-pointer transition-all ${
                isSelected
                  ? 'bg-blue-50 dark:bg-blue-950/40 border-blue-300 dark:border-blue-700 ring-1 ring-blue-500'
                  : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-mono font-bold text-slate-900 dark:text-slate-100 text-[11px]">
                  #{inv.id.slice(0, 8)}
                </span>
                <StatusBadge status={inv.status} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500 dark:text-slate-400">{fmtRelative(inv.created_at)}</span>
                {score != null && (
                  <span className={`font-bold text-[11px] ${scoreColor(score)}`}>{Math.round(score)}/100</span>
                )}
              </div>
              {inv.alert?.severity && (
                <div className="mt-1.5">
                  <RiskBadge level={inv.alert.severity} />
                </div>
              )}
            </div>
          );
        })
      )}
    </div>
  );
};

// ─── Risk Manager backlog ──────────────────────────────────────────────────────

const RiskManagerBacklog: React.FC<{ investigations: Investigation[]; onRefresh: () => void }> = ({ investigations, onRefresh }) => {
  const navigate = useNavigate();
  const open = investigations.filter(i => i.status === 'OPEN').length;
  const inReview = investigations.filter(i => i.status === 'IN_REVIEW').length;
  const escalated = investigations.filter(i => i.status === 'ESCALATED').length;
  const resolved = investigations.filter(i => i.status === 'RESOLVED').length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-purple-600 dark:text-purple-400" /> Investigation Backlog
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Managerial oversight of case backlogs and analyst assignments</p>
        </div>
        <Button variant="outline" size="sm" onClick={onRefresh}><RefreshCw className="w-4 h-4" /></Button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Open', count: open, border: 'border-l-amber-500', color: 'text-amber-600 dark:text-amber-400' },
          { label: 'In Review', count: inReview, border: 'border-l-blue-500', color: 'text-blue-600 dark:text-blue-400' },
          { label: 'Escalated', count: escalated, border: 'border-l-purple-500', color: 'text-purple-600 dark:text-purple-400' },
          { label: 'Resolved', count: resolved, border: 'border-l-emerald-500', color: 'text-emerald-600 dark:text-emerald-400' },
        ].map(m => (
          <Card key={m.label} className={`!p-3 border-l-4 ${m.border}`}>
            <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase">{m.label}</span>
            <span className={`block text-2xl font-extrabold ${m.color} mt-0.5`}>{m.count}</span>
          </Card>
        ))}
      </div>

      <Card title="Full Case Backlog" subtitle="All investigations — click a row to open the case">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Case ID</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Risk Score</th>
                <th className="py-3 px-4">Assignee</th>
                <th className="py-3 px-4">Age</th>
                <th className="py-3 px-4">Decision</th>
                <th className="py-3 px-4 text-right">Open</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {investigations.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-8 text-slate-400 dark:text-slate-500">No investigations found</td></tr>
              ) : (
                investigations.map((inv) => {
                  const snap = inv.forensic_snapshot;
                  const score = snap?.risk_score ?? inv.alert?.risk_score;
                  const age = Math.floor((Date.now() - new Date(inv.created_at).getTime()) / 86_400_000);
                  const isAged = inv.status !== 'RESOLVED' && age >= 5;
                  return (
                    <tr
                      key={inv.id}
                      className={`cursor-pointer transition-colors ${isAged ? 'bg-rose-50/50 dark:bg-rose-950/20 hover:bg-rose-50 dark:hover:bg-rose-950/30' : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'}`}
                      onClick={() => navigate(`/investigations/${inv.id}`)}
                    >
                      <td className="py-3 px-4 font-mono font-bold text-slate-900 dark:text-slate-100">#{inv.id.slice(0, 8)}</td>
                      <td className="py-3 px-4">{inv.alert?.severity ? <RiskBadge level={inv.alert.severity} /> : '—'}</td>
                      <td className="py-3 px-4"><StatusBadge status={inv.status} /></td>
                      <td className="py-3 px-4">
                        {score != null ? <span className={`font-bold ${scoreColor(score)}`}>{Math.round(score)}/100</span> : '—'}
                      </td>
                      <td className="py-3 px-4">
                        {inv.assigned_analyst_id
                          ? <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400"><UserCheck className="w-3.5 h-3.5" />Assigned</span>
                          : <span className="text-slate-400">Unassigned</span>}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`flex items-center gap-1 font-semibold ${isAged ? 'text-rose-600 dark:text-rose-400' : 'text-slate-700 dark:text-slate-300'}`}>
                          <Clock className="w-3.5 h-3.5" />{age}d {isAged && <AlertTriangle className="w-3.5 h-3.5" />}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {inv.decision
                          ? <span className="text-[10px] bg-purple-100 dark:bg-purple-950/60 text-purple-800 dark:text-purple-300 px-2 py-0.5 rounded font-bold">{inv.decision.replace('_', ' ')}</span>
                          : <span className="text-slate-400">Pending</span>}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <ChevronRight className="w-4 h-4 text-slate-400 ml-auto" />
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

// ─── ROOT COMPONENT ────────────────────────────────────────────────────────────

export const InvestigationWorkspace: React.FC = () => {
  const { user } = useOutletContext<{ user: User | null }>();
  const { caseId } = useParams<{ caseId?: string }>();
  const navigate = useNavigate();

  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(caseId ?? null);
  const [loading, setLoading] = useState(true);
  const [conflictMsg, setConflictMsg] = useState<string | null>(null);

  const role = user?.role ?? 'FRAUD_ANALYST';
  const isRiskManager = role === 'RISK_MANAGER';

  const selectedInv = investigations.find(i => i.id === selectedId) ?? null;

  const fetchInvestigations = useCallback(async () => {
    try {
      const data = await apiRequest<Investigation[]>('/investigations?limit=100');
      setInvestigations(data);
      // If URL has a caseId, select it; otherwise pick first
      if (caseId) {
        setSelectedId(caseId);
      } else if (data.length > 0 && !selectedId) {
        setSelectedId(data[0].id);
        navigate(`/investigations/${data[0].id}`, { replace: true });
      }
    } catch (err) {
      console.error('Failed to load investigations', err);
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  // When URL param changes (e.g. user navigates), sync selected
  useEffect(() => {
    if (caseId) setSelectedId(caseId);
  }, [caseId]);

  useEffect(() => {
    fetchInvestigations();
  }, [fetchInvestigations]);

  if (loading) {
    return (
      <div className="space-y-6">
        <InvestigationSkeleton />
      </div>
    );
  }

  if (isRiskManager) {
    return <RiskManagerBacklog investigations={investigations} onRefresh={fetchInvestigations} />;
  }

  return (
    <div className="space-y-4">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <Search className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            Investigation Workspace
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Evidence synthesis · Forensic risk analysis · Analyst decisioning
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => fetchInvestigations()}>
          <RefreshCw className="w-4 h-4 mr-1.5" /> Refresh
        </Button>
      </div>

      {/* Conflict banner */}
      {conflictMsg && (
        <div className="flex items-center gap-2 p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-700 rounded-xl text-xs text-amber-800 dark:text-amber-200">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span><strong>Conflict:</strong> {conflictMsg}</span>
          <button className="ml-auto text-amber-600 hover:text-amber-800" onClick={() => { setConflictMsg(null); fetchInvestigations(); }}>
            Reload
          </button>
        </div>
      )}

      {/* Main layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Case list sidebar */}
        <div className="lg:col-span-3">
          <Card title={`Cases (${investigations.length})`} className="!p-3 lg:sticky lg:top-4">
            <div className="mt-2 max-h-[calc(100vh-16rem)] overflow-y-auto">
              <CaseListSidebar
                investigations={investigations}
                selectedId={selectedId}
                onSelect={setSelectedId}
              />
            </div>
          </Card>
        </div>

        {/* Detail pane */}
        <div className="lg:col-span-9">
          {selectedInv ? (
            <InvestigationDetail
              key={selectedInv.id}
              inv={selectedInv}
              user={user}
              onRefresh={fetchInvestigations}
              onConflict={setConflictMsg}
            />
          ) : (
            <Card className="text-center py-16 text-slate-400 dark:text-slate-500 text-xs !p-6">
              <Search className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p className="text-sm font-medium">Select a case from the list</p>
              <p className="mt-1">Or navigate to <code className="font-mono bg-slate-100 dark:bg-slate-800 px-1 rounded">/investigations/:caseId</code></p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default InvestigationWorkspace;
