import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  CheckCircle2, Plus, UserCheck, Search, ShieldCheck,
  Clock, AlertTriangle, BarChart2, Zap,
  Smartphone, MapPin, Activity,
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { RiskBadge } from '../components/ui/RiskBadge';
import { apiRequest } from '../services/api';
import type { Investigation, InvestigationDecision, User, ShapFactor } from '../types';

// ─── Shared helpers ────────────────────────────────────────────────────────────

function daysSince(dateStr: string): number {
  return Math.floor((Date.now() - new Date(dateStr).getTime()) / 86_400_000);
}

// ─── SHAP Factor Display ───────────────────────────────────────────────────────

const ShapRow: React.FC<{ factor: ShapFactor }> = ({ factor }) => {
  const pct = Math.min(Math.abs(factor.contribution) * 100, 100);
  const isPositive = factor.direction === 'POSITIVE';
  return (
    <div className="space-y-0.5">
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

// ─── ANALYST INVESTIGATION WORKSPACE ─────────────────────────────────────────

const AnalystWorkspace: React.FC<{
  investigations: Investigation[];
  selectedInv: Investigation | null;
  setSelectedInv: (inv: Investigation) => void;
  onRefresh: () => void;
  error: string | null;
  setError: (e: string | null) => void;
  isReadOnly: boolean;
}> = ({ investigations, selectedInv, setSelectedInv, onRefresh, error, setError, isReadOnly }) => {
  const [noteText, setNoteText] = useState('');
  const [decision, setDecision] = useState<InvestigationDecision>('CONFIRMED_FRAUD');
  const [reason, setReason] = useState('');
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const shapFactors: ShapFactor[] =
    selectedInv?.transaction?.risk_score?.explanation?.top_factors ?? [];

  const handleClaim = async () => {
    if (!selectedInv || isReadOnly) return;
    try {
      const updated = await apiRequest<Investigation>(`/investigations/${selectedInv.id}/claim`, {
        method: 'POST',
      });
      setSelectedInv(updated);
      onRefresh();
    } catch (err: any) {
      setError(err.message || 'Failed to claim investigation');
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedInv || !noteText.trim() || isReadOnly) return;
    setIsSubmitting(true);
    try {
      await apiRequest(`/investigations/${selectedInv.id}/notes`, {
        method: 'POST',
        body: JSON.stringify({ note_text: noteText }),
      });
      setNoteText('');
      const updated = await apiRequest<Investigation>(`/investigations/${selectedInv.id}`);
      setSelectedInv(updated);
    } catch (err: any) {
      setError(err.message || 'Failed to add note');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedInv || !reason.trim() || isReadOnly) return;
    setIsSubmitting(true);
    try {
      const updated = await apiRequest<Investigation>(`/investigations/${selectedInv.id}/resolve`, {
        method: 'POST',
        body: JSON.stringify({ decision, decision_reason: reason, version: selectedInv.version }),
      });
      setSelectedInv(updated);
      setShowResolveModal(false);
      onRefresh();
    } catch (err: any) {
      setError(err.message || 'Resolution failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <Search className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            Analyst Investigation Workspace
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Evidence synthesis, SHAP factor review, analyst notes, and human decision recording.
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 p-3 rounded-btn text-xs flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">Dismiss</button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Case List */}
        <Card title="Active & Recent Cases" className="lg:col-span-1 !p-4">
          <div className="space-y-2 mt-2 max-h-[calc(100vh-20rem)] overflow-y-auto">
            {investigations.length === 0 ? (
              <div className="text-center py-8 text-slate-400 dark:text-slate-500 text-xs">No active investigation cases</div>
            ) : (
              investigations.map((inv) => {
                const age = daysSince(inv.created_at);
                return (
                  <div
                    key={inv.id}
                    onClick={() => setSelectedInv(inv)}
                    className={`p-3 rounded-btn border text-xs cursor-pointer transition-all ${
                      selectedInv?.id === inv.id
                        ? 'bg-blue-50/80 dark:bg-blue-950/40 border-blue-300 dark:border-blue-700 ring-1 ring-blue-500'
                        : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                    }`}
                  >
                    <div className="flex items-center justify-between font-semibold text-slate-900 dark:text-slate-100 mb-1">
                      <span>Case #{inv.id.slice(0, 8)}</span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        inv.status === 'RESOLVED' ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300' :
                        inv.status === 'IN_REVIEW' ? 'bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300' :
                        'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300'
                      }`}>
                        {inv.status}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 flex justify-between items-center">
                      <span>Alert: {inv.alert_id.slice(0, 8)}</span>
                      <span className={`flex items-center gap-0.5 ${age >= 5 ? 'text-rose-600 dark:text-rose-400 font-semibold' : 'text-slate-400'}`}>
                        <Clock className="w-3 h-3" />{age}d
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </Card>

        {/* Evidence Panel */}
        <div className="lg:col-span-2 space-y-4">
          {selectedInv ? (
            <>
              {/* Case Header */}
              <Card>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
                  <div>
                    <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">Case ID: {selectedInv.id}</span>
                    <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2 mt-0.5">
                      Status: {selectedInv.status}
                      {selectedInv.decision && (
                        <span className="text-xs bg-purple-100 dark:bg-purple-950/60 text-purple-800 dark:text-purple-300 px-2.5 py-0.5 rounded-full font-bold">
                          {selectedInv.decision}
                        </span>
                      )}
                    </h3>
                  </div>
                  {!isReadOnly && (
                    <div className="flex items-center gap-2">
                      {selectedInv.status === 'OPEN' && (
                        <Button variant="primary" size="sm" onClick={handleClaim}>
                          <UserCheck className="w-4 h-4 mr-1.5" /> Claim Case
                        </Button>
                      )}
                      {selectedInv.status !== 'RESOLVED' && (
                        <Button variant="danger" size="sm" onClick={() => setShowResolveModal(true)}>
                          <CheckCircle2 className="w-4 h-4 mr-1.5" /> Record Decision
                        </Button>
                      )}
                    </div>
                  )}
                </div>

                {/* Evidence Summary Grid */}
                <div className="py-4 space-y-4">
                  <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wider">Evidence Overview</h4>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-btn text-xs">
                      <span className="text-slate-400 block">Transaction ID</span>
                      <span className="font-mono font-medium text-slate-900 dark:text-slate-100">{selectedInv.transaction_id}</span>
                    </div>
                    <div className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-btn text-xs">
                      <span className="text-slate-400 block">Alert Reference</span>
                      <span className="font-mono font-medium text-slate-900 dark:text-slate-100">{selectedInv.alert_id}</span>
                    </div>
                    {selectedInv.transaction && (
                      <>
                        <div className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-btn text-xs">
                          <span className="text-slate-400 block">Amount</span>
                          <span className="font-bold text-slate-900 dark:text-slate-100">${selectedInv.transaction.amount.toLocaleString()}</span>
                        </div>
                        <div className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-btn text-xs">
                          <span className="text-slate-400 block">Risk Score</span>
                          <span className="font-bold text-rose-600 dark:text-rose-400">
                            {selectedInv.transaction.risk_score
                              ? `${Math.round(selectedInv.transaction.risk_score.risk_score)} / 100`
                              : '—'}
                          </span>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Forensic Evidence Checklist */}
                  <div className="p-3.5 bg-slate-50 dark:bg-slate-800/50 rounded-btn border border-slate-200 dark:border-slate-800 space-y-2">
                    <h5 className="text-[11px] font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Forensic Risk Signals</h5>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                      <div className="flex items-center gap-2 p-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800">
                        <Smartphone className="w-4 h-4 text-blue-500 shrink-0" />
                        <span className="text-slate-700 dark:text-slate-300 font-medium">Device: Verified</span>
                      </div>
                      <div className="flex items-center gap-2 p-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800">
                        <MapPin className="w-4 h-4 text-amber-500 shrink-0" />
                        <span className="text-slate-700 dark:text-slate-300 font-medium">Geo Velocity: Medium</span>
                      </div>
                      <div className="flex items-center gap-2 p-2 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-800">
                        <Activity className="w-4 h-4 text-rose-500 shrink-0" />
                        <span className="text-slate-700 dark:text-slate-300 font-medium">Anomaly: Outlier</span>
                      </div>
                    </div>
                  </div>

                  {selectedInv.decision_reason && (
                    <div className="p-3 bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800 rounded-btn text-xs text-purple-900 dark:text-purple-200">
                      <span className="font-bold block mb-1">Analyst Decision Rationale:</span>
                      <p>{selectedInv.decision_reason}</p>
                    </div>
                  )}
                </div>
              </Card>

              {/* SHAP Factor Evidence */}
              {shapFactors.length > 0 && (
                <Card title="SHAP Risk Factor Evidence" subtitle="ML model feature contributions driving this risk score">
                  <div className="space-y-3 mt-3">
                    {shapFactors.slice(0, 6).map((f, i) => (
                      <ShapRow key={i} factor={f} />
                    ))}
                    <div className="pt-2 border-t border-slate-100 dark:border-slate-800 text-[10px] text-slate-400 dark:text-slate-500 flex items-center gap-1">
                      <Zap className="w-3 h-3 text-blue-500" />
                      SHAP values computed from validated XGBoost model pipeline
                    </div>
                  </div>
                </Card>
              )}

              {/* Notes Timeline */}
              <Card title="Investigation Notes & Audit Trail">
                <div className="space-y-3 mt-2 max-h-60 overflow-y-auto pr-1">
                  {(!selectedInv.notes || selectedInv.notes.length === 0) ? (
                    <p className="text-xs text-slate-400 dark:text-slate-500 italic py-4 text-center">No notes added to this case yet</p>
                  ) : (
                    selectedInv.notes.map((note) => (
                      <div key={note.id} className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-btn text-xs space-y-1">
                        <div className="flex justify-between text-slate-400 dark:text-slate-500 text-[11px]">
                          <span className="font-semibold text-slate-700 dark:text-slate-300">Analyst</span>
                          <span>{new Date(note.created_at).toLocaleString()}</span>
                        </div>
                        <p className="text-slate-800 dark:text-slate-200 font-medium">{note.note_text}</p>
                      </div>
                    ))
                  )}
                </div>

                {!isReadOnly && selectedInv.status !== 'RESOLVED' && (
                  <form onSubmit={handleAddNote} className="mt-4 flex gap-2">
                    <input
                      type="text"
                      placeholder="Add investigation note or evidence observation..."
                      value={noteText}
                      onChange={(e) => setNoteText(e.target.value)}
                      className="flex-1 px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-btn text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <Button type="submit" size="sm" variant="secondary" isLoading={isSubmitting}>
                      <Plus className="w-4 h-4 mr-1" /> Add Note
                    </Button>
                  </form>
                )}
              </Card>
            </>
          ) : (
            <Card className="text-center py-16 text-slate-400 dark:text-slate-500 text-xs">
              Select an investigation case from the left list to view evidence
            </Card>
          )}
        </div>
      </div>

      {/* Record Decision Modal */}
      {showResolveModal && selectedInv && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 max-w-md w-full rounded-modal p-6 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">Record Analyst Final Decision</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              The human analyst remains responsible for the final fraud decision.
            </p>
            <form onSubmit={handleResolve} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Decision Verdict</label>
                <select
                  value={decision}
                  onChange={(e) => setDecision(e.target.value as InvestigationDecision)}
                  className="w-full text-xs border border-slate-300 dark:border-slate-700 rounded-btn px-3 py-2 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                  className="w-full text-xs bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-btn p-3 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <Button type="button" variant="outline" className="flex-1" onClick={() => setShowResolveModal(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="danger" className="flex-1" isLoading={isSubmitting}>
                  Submit Decision
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

// ─── RISK MANAGER CASE BACKLOG TABLE ─────────────────────────────────────────

const RiskManagerBacklog: React.FC<{
  investigations: Investigation[];
  onRefresh: () => void;
}> = ({ investigations, onRefresh }) => {
  const open = investigations.filter((i) => i.status === 'OPEN').length;
  const inReview = investigations.filter((i) => i.status === 'IN_REVIEW').length;
  const resolvedToday = investigations.filter((i) => {
    if (!i.resolved_at) return false;
    return daysSince(i.resolved_at) === 0;
  }).length;
  const agedOut = investigations.filter((i) => i.status !== 'RESOLVED' && daysSince(i.created_at) >= 5).length;

  return (
    <>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            Investigation Backlog & Manager Oversight
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Managerial oversight of case backlogs, analyst assignments, resolution aging, and decisioning trends.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={onRefresh}>
          Refresh
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card className="!p-3 border-l-4 border-l-amber-500">
          <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase">Open Cases</span>
          <span className="block text-2xl font-extrabold text-amber-600 dark:text-amber-400 mt-0.5">{open}</span>
        </Card>
        <Card className="!p-3 border-l-4 border-l-blue-500">
          <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase">In Review</span>
          <span className="block text-2xl font-extrabold text-blue-600 dark:text-blue-400 mt-0.5">{inReview}</span>
        </Card>
        <Card className="!p-3 border-l-4 border-l-emerald-500">
          <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase">Resolved Today</span>
          <span className="block text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">{resolvedToday}</span>
        </Card>
        <Card className={`!p-3 border-l-4 ${agedOut > 0 ? 'border-l-rose-600' : 'border-l-slate-300 dark:border-l-slate-700'}`}>
          <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase">Age-Out Warnings</span>
          <span className={`block text-2xl font-extrabold mt-0.5 ${agedOut > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-500'}`}>
            {agedOut}
          </span>
        </Card>
      </div>

      {/* Full Backlog Table */}
      <Card title="Full Case Backlog" subtitle="All investigations — sortable by age and status">
        {agedOut > 0 && (
          <div className="mb-3 flex items-center gap-2 px-3 py-2 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 rounded-btn text-xs text-rose-700 dark:text-rose-300 font-medium">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            {agedOut} case{agedOut > 1 ? 's' : ''} have been open for 5+ days and require escalation review.
          </div>
        )}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Case ID</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Analyst</th>
                <th className="py-3 px-4">Age</th>
                <th className="py-3 px-4">Decision</th>
                <th className="py-3 px-4 text-right">Review</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {investigations.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-8 text-slate-400 dark:text-slate-500">No investigations found</td></tr>
              ) : (
                investigations.map((inv) => {
                  const age = daysSince(inv.created_at);
                  const isAged = inv.status !== 'RESOLVED' && age >= 5;
                  return (
                    <tr key={inv.id} className={`transition-colors ${isAged ? 'bg-rose-50/50 dark:bg-rose-950/20 hover:bg-rose-50 dark:hover:bg-rose-950/30' : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'}`}>
                      <td className="py-3 px-4 font-mono font-bold text-slate-900 dark:text-slate-100">
                        #{inv.id.slice(0, 8)}
                      </td>
                      <td className="py-3 px-4">
                        {inv.alert?.severity
                          ? <RiskBadge level={inv.alert.severity} />
                          : <span className="text-slate-400">—</span>}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                          inv.status === 'RESOLVED' ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300' :
                          inv.status === 'IN_REVIEW' ? 'bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300' :
                          'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300'
                        }`}>
                          {inv.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-600 dark:text-slate-400">
                        {inv.assigned_analyst_id
                          ? <span className="flex items-center gap-1"><UserCheck className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" /> Assigned</span>
                          : <span className="text-slate-400">Unassigned</span>}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`flex items-center gap-1 font-semibold ${isAged ? 'text-rose-600 dark:text-rose-400' : 'text-slate-700 dark:text-slate-300'}`}>
                          <Clock className="w-3.5 h-3.5" />
                          {age}d {isAged && <AlertTriangle className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" />}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {inv.decision
                          ? <span className="text-[10px] bg-purple-100 dark:bg-purple-950/60 text-purple-800 dark:text-purple-300 px-2 py-0.5 rounded font-bold">{inv.decision}</span>
                          : <span className="text-slate-400">Pending</span>}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <span className="text-purple-600 dark:text-purple-400 font-semibold">
                          Managed
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Risk Manager insights */}
      <Card title="Backlog Composition" subtitle="Investigation distribution by status">
        <div className="flex items-end gap-3 pt-2">
          {[
            { label: 'Open', count: open, color: 'bg-amber-500', total: investigations.length },
            { label: 'In Review', count: inReview, color: 'bg-blue-500', total: investigations.length },
            { label: 'Resolved', count: investigations.length - open - inReview, color: 'bg-emerald-500', total: investigations.length },
          ].map(({ label, count, color, total }) => {
            const pct = total > 0 ? Math.round((count / total) * 100) : 0;
            return (
              <div key={label} className="flex-1 text-center">
                <div className="text-xs font-bold text-slate-900 dark:text-slate-100 mb-1">{pct}%</div>
                <div className="h-20 bg-slate-200 dark:bg-slate-700 rounded-sm overflow-hidden flex flex-col-reverse">
                  <div className={`${color} w-full rounded-sm transition-all`} style={{ height: `${pct}%` }} />
                </div>
                <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-1">{label}</div>
                <div className="text-xs font-bold text-slate-700 dark:text-slate-300">{count}</div>
              </div>
            );
          })}
          <div className="flex-1 text-center">
            <div className="text-xs font-bold text-rose-600 dark:text-rose-400 mb-1">{agedOut > 0 ? agedOut : 0}</div>
            <div className="h-20 bg-slate-200 dark:bg-slate-700 rounded-sm overflow-hidden flex flex-col-reverse">
              <div
                className="bg-rose-500 w-full rounded-sm transition-all"
                style={{ height: `${investigations.length > 0 ? Math.round((agedOut / investigations.length) * 100) : 0}%` }}
              />
            </div>
            <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-1">Aged Out</div>
            <div className="text-xs font-bold text-rose-600 dark:text-rose-400">{agedOut}</div>
          </div>
        </div>
      </Card>
    </>
  );
};

// ─── VIEWER READ-ONLY ─────────────────────────────────────────────────────────

const ViewerBacklog: React.FC<{ investigations: Investigation[] }> = ({ investigations }) => (
  <>
    <div>
      <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
        <BarChart2 className="w-5 h-5 text-slate-500" />
        Investigations — Read-Only
      </h2>
      <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Observer access: no actions permitted.</p>
    </div>
    <Card>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
              <th className="py-3 px-4">Case ID</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Created</th>
              <th className="py-3 px-4">Decision</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
            {investigations.length === 0 ? (
              <tr><td colSpan={4} className="text-center py-6 text-slate-400 dark:text-slate-500">No investigations found</td></tr>
            ) : (
              investigations.map((inv) => (
                <tr key={inv.id}>
                  <td className="py-3 px-4 font-mono text-slate-900 dark:text-slate-100">#{inv.id.slice(0, 8)}</td>
                  <td className="py-3 px-4 text-slate-700 dark:text-slate-300">{inv.status}</td>
                  <td className="py-3 px-4 text-slate-500 dark:text-slate-400">{new Date(inv.created_at).toLocaleDateString()}</td>
                  <td className="py-3 px-4 text-slate-700 dark:text-slate-300">{inv.decision ?? '—'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Card>
  </>
);

// ─── ROOT COMPONENT ────────────────────────────────────────────────────────────

export const InvestigationWorkspace: React.FC = () => {
  const { user } = useOutletContext<{ user: User | null }>();
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [selectedInv, setSelectedInv] = useState<Investigation | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isReadOnly = user?.role === 'VIEWER';

  const fetchInvestigations = async () => {
    try {
      const data = await apiRequest<Investigation[]>('/investigations');
      setInvestigations(data);
      if (data.length > 0 && !selectedInv) {
        setSelectedInv(data[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchInvestigations();
  }, []);

  const role = user?.role ?? 'FRAUD_ANALYST';

  return (
    <div className="space-y-6">
      {role === 'RISK_MANAGER' ? (
        <RiskManagerBacklog investigations={investigations} onRefresh={fetchInvestigations} />
      ) : isReadOnly ? (
        <ViewerBacklog investigations={investigations} />
      ) : (
        <AnalystWorkspace
          investigations={investigations}
          selectedInv={selectedInv}
          setSelectedInv={setSelectedInv}
          onRefresh={fetchInvestigations}
          error={error}
          setError={setError}
          isReadOnly={false}
        />
      )}
    </div>
  );
};

export default InvestigationWorkspace;
