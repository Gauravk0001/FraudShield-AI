import React, { useEffect, useState } from 'react';
import { CheckCircle2, Plus, UserCheck } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { apiRequest } from '../services/api';
import type { Investigation, InvestigationDecision } from '../types';

export const InvestigationWorkspace: React.FC = () => {
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [selectedInv, setSelectedInv] = useState<Investigation | null>(null);
  const [noteText, setNoteText] = useState('');
  const [decision, setDecision] = useState<InvestigationDecision>('CONFIRMED_FRAUD');
  const [reason, setReason] = useState('');
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const handleClaim = async () => {
    if (!selectedInv) return;
    try {
      const updated = await apiRequest<Investigation>(`/investigations/${selectedInv.id}/claim`, {
        method: 'POST'
      });
      setSelectedInv(updated);
      fetchInvestigations();
    } catch (err: any) {
      setError(err.message || 'Failed to claim investigation');
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedInv || !noteText.trim()) return;
    setIsSubmitting(true);
    try {
      await apiRequest(`/investigations/${selectedInv.id}/notes`, {
        method: 'POST',
        body: JSON.stringify({ note_text: noteText })
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
    if (!selectedInv || !reason.trim()) return;
    setIsSubmitting(true);
    try {
      const updated = await apiRequest<Investigation>(`/investigations/${selectedInv.id}/resolve`, {
        method: 'POST',
        body: JSON.stringify({
          decision,
          decision_reason: reason,
          version: selectedInv.version
        })
      });
      setSelectedInv(updated);
      setShowResolveModal(false);
      fetchInvestigations();
    } catch (err: any) {
      setError(err.message || 'Resolution failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Analyst Investigation Workspace</h2>
          <p className="text-xs text-slate-500 mt-0.5">Evidence synthesis, analyst notes, and human decision recording</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-btn text-xs flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-slate-400 hover:text-slate-600">Dismiss</button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Investigation Case List */}
        <Card title="Active & Recent Cases" className="lg:col-span-1 !p-4">
          <div className="space-y-2 mt-2">
            {investigations.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-xs">No active investigation cases</div>
            ) : (
              investigations.map((inv) => (
                <div
                  key={inv.id}
                  onClick={() => setSelectedInv(inv)}
                  className={`p-3 rounded-btn border text-xs cursor-pointer transition-all ${
                    selectedInv?.id === inv.id
                      ? 'bg-blue-50/80 border-blue-300 ring-1 ring-blue-500'
                      : 'bg-white border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between font-semibold text-slate-900 mb-1">
                    <span>Case #{inv.id.slice(0, 8)}</span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      inv.status === 'RESOLVED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                    }`}>
                      {inv.status}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500 flex justify-between items-center">
                    <span>Alert ID: {inv.alert_id.slice(0, 8)}</span>
                    <span>{new Date(inv.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* Right Column: Case Evidence & Decision Panel */}
        <div className="lg:col-span-2 space-y-6">
          {selectedInv ? (
            <>
              <Card>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
                  <div>
                    <span className="text-xs text-slate-400 font-mono">Case ID: {selectedInv.id}</span>
                    <h3 className="text-base font-bold text-slate-900 flex items-center gap-2 mt-0.5">
                      Status: {selectedInv.status}
                      {selectedInv.decision && (
                        <span className="text-xs bg-purple-100 text-purple-800 px-2.5 py-0.5 rounded-full font-bold">
                          {selectedInv.decision}
                        </span>
                      )}
                    </h3>
                  </div>

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
                </div>

                {/* Evidence Summary */}
                <div className="py-4 space-y-4">
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Evidence Overview</h4>
                  <div className="p-3 bg-slate-50 border border-slate-200 rounded-btn text-xs grid grid-cols-2 gap-3">
                    <div>
                      <span className="text-slate-400 block">Transaction ID</span>
                      <span className="font-mono font-medium text-slate-900">{selectedInv.transaction_id}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Alert Reference</span>
                      <span className="font-mono font-medium text-slate-900">{selectedInv.alert_id}</span>
                    </div>
                  </div>

                  {selectedInv.decision_reason && (
                    <div className="p-3 bg-purple-50 border border-purple-200 rounded-btn text-xs text-purple-900">
                      <span className="font-bold block mb-1">Analyst Decision Rationale:</span>
                      <p>{selectedInv.decision_reason}</p>
                    </div>
                  )}
                </div>
              </Card>

              {/* Notes Timeline */}
              <Card title="Investigation Notes & Audit Trail">
                <div className="space-y-3 mt-2 max-h-60 overflow-y-auto pr-1">
                  {(!selectedInv.notes || selectedInv.notes.length === 0) ? (
                    <p className="text-xs text-slate-400 italic py-4 text-center">No notes added to this case yet</p>
                  ) : (
                    selectedInv.notes.map((note) => (
                      <div key={note.id} className="p-3 bg-slate-50 border border-slate-200 rounded-btn text-xs space-y-1">
                        <div className="flex justify-between text-slate-400 text-[11px]">
                          <span className="font-semibold text-slate-700">Analyst</span>
                          <span>{new Date(note.created_at).toLocaleString()}</span>
                        </div>
                        <p className="text-slate-800 font-medium">{note.note_text}</p>
                      </div>
                    ))
                  )}
                </div>

                {selectedInv.status !== 'RESOLVED' && (
                  <form onSubmit={handleAddNote} className="mt-4 flex gap-2">
                    <input
                      type="text"
                      placeholder="Add investigation note or evidence observation..."
                      value={noteText}
                      onChange={(e) => setNoteText(e.target.value)}
                      className="flex-1 px-3 py-2 text-xs border border-slate-300 rounded-btn focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <Button type="submit" size="sm" variant="secondary" isLoading={isSubmitting}>
                      <Plus className="w-4 h-4 mr-1" /> Add Note
                    </Button>
                  </form>
                )}
              </Card>
            </>
          ) : (
            <Card className="text-center py-16 text-slate-400 text-xs">
              Select an investigation case from the left list to view evidence
            </Card>
          )}
        </div>
      </div>

      {/* Record Decision Modal */}
      {showResolveModal && selectedInv && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white max-w-md w-full rounded-modal p-6 shadow-2xl border border-slate-200 space-y-4">
            <h3 className="text-base font-bold text-slate-900">Record Analyst Final Decision</h3>
            <p className="text-xs text-slate-500">
              The human analyst remains responsible for the final fraud decision.
            </p>

            <form onSubmit={handleResolve} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Decision Verdict</label>
                <select
                  value={decision}
                  onChange={(e) => setDecision(e.target.value as InvestigationDecision)}
                  className="w-full text-xs border border-slate-300 rounded-btn px-3 py-2 bg-white font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="CONFIRMED_FRAUD">CONFIRMED_FRAUD — Confirmed Unauthorized Activity</option>
                  <option value="FALSE_POSITIVE">FALSE_POSITIVE — Legitimate Customer Activity</option>
                  <option value="SUSPICIOUS_MONITORED">SUSPICIOUS_MONITORED — Keep Under Monitoring</option>
                  <option value="NO_ACTION_REQUIRED">NO_ACTION_REQUIRED — No Action Required</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Mandatory Decision Reason</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Explain why this decision was reached based on evidence..."
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full text-xs border border-slate-300 rounded-btn p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
    </div>
  );
};
