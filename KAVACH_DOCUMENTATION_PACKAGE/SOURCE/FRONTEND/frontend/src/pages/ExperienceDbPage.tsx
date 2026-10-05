import React, { useState, useEffect } from 'react';
import { 
  Database, 
  History, 
  ShieldCheck, 
  CheckCircle2, 
  AlertTriangle, 
  FileCode2, 
  Search, 
  ArrowRight, 
  RotateCcw,
  Sparkles,
  Info,
  Clock,
  BookOpen
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';

export const ExperienceDbPage: React.FC = () => {
  const { showToast, setSelectedFindingId, navigate } = useApp();
  const [activeTab, setActiveTab] = useState<'reverifications' | 'false_positives'>('reverifications');
  const [summary, setSummary] = useState<any>(null);
  const [reverifications, setReverifications] = useState<any[]>([]);
  const [falsePositives, setFalsePositives] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Mark False Positive Modal State
  const [markModalOpen, setMarkModalOpen] = useState(false);
  const [selectedFindingToMark, setSelectedFindingToMark] = useState('');
  const [markRationale, setMarkRationale] = useState('');
  const [submittingMark, setSubmittingMark] = useState(false);

  const fetchData = async () => {
    try {
      const [sumRes, revRes, fpRes] = await Promise.all([
        api.getExperienceSummary(),
        api.getReverificationHistory(),
        api.getFalsePositivesLibrary()
      ]);
      if (sumRes.success) setSummary(sumRes);
      if (revRes.success) setReverifications(revRes.re_verifications);
      if (fpRes.success) setFalsePositives(fpRes.false_positives);
    } catch {
      showToast('error', 'Sync Failed', 'Could not load Experience DB records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCommitFalsePositive = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFindingToMark.trim() || !markRationale.trim()) return;
    setSubmittingMark(true);
    try {
      const res = await api.markFalsePositive({
        finding_id: selectedFindingToMark.trim(),
        rationale: markRationale.trim()
      });
      if (res.success) {
        showToast('success', 'Committed to Experience DB', 'Finding logged as false positive with rationale.');
        setMarkModalOpen(false);
        setSelectedFindingToMark('');
        setMarkRationale('');
        fetchData();
      }
    } catch {
      showToast('error', 'Error', 'Failed to commit false positive record.');
    } finally {
      setSubmittingMark(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Header & Principle Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3 mb-1">
            <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
              <Database className="w-5 h-5 text-purple-400" />
              <span>Module 7: Experience DB</span>
            </h1>
            <Badge variant="outline">KAVACH Enterprise</Badge>
            <span className="px-2 py-0.5 text-xs font-mono rounded bg-purple-950 text-purple-300 border border-purple-800">
              REMEMBER
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Historical security memory engine retaining confirmed remediation outcomes, differential re-verification diffs, and false-positive lessons learned.
          </p>
        </div>

        <div className="flex items-center space-x-2 bg-slate-900/80 border border-slate-800 px-3 py-2 rounded-lg text-xs font-mono text-slate-400">
          <Clock className="w-4 h-4 text-purple-400" />
          <span>Loop: ASSIGN → FIX → RE-VERIFY → <strong className="text-purple-300">REMEMBER</strong></span>
        </div>
      </div>

      {/* Experience Memory Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
        <GlassCard className="p-3 border-slate-800/80 bg-slate-900/40">
          <div className="text-[10px] font-mono uppercase text-slate-500">Assessments</div>
          <div className="text-xl font-bold font-mono text-slate-100 mt-1">
            {summary?.metrics?.total_assessments ?? 0}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Historical cycles</div>
        </GlassCard>

        <GlassCard className="p-3 border-slate-800/80 bg-slate-900/40">
          <div className="text-[10px] font-mono uppercase text-slate-500">Total Cataloged</div>
          <div className="text-xl font-bold font-mono text-cyan-400 mt-1">
            {summary?.metrics?.total_findings_cataloged ?? 0}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Unique hypotheses</div>
        </GlassCard>

        <GlassCard className="p-3 border-slate-800/80 bg-slate-900/40">
          <div className="text-[10px] font-mono uppercase text-slate-500">Confirmed Flaws</div>
          <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
            {summary?.metrics?.confirmed_flaws ?? 0}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Evidence-backed</div>
        </GlassCard>

        <GlassCard className="p-3 border-slate-800/80 bg-slate-900/40">
          <div className="text-[10px] font-mono uppercase text-slate-500">Re-Verifications</div>
          <div className="text-xl font-bold font-mono text-indigo-400 mt-1">
            {summary?.metrics?.resolved_re_verifications ?? 0}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Patches proven</div>
        </GlassCard>

        <GlassCard className="p-3 border-slate-800/80 bg-slate-900/40">
          <div className="text-[10px] font-mono uppercase text-slate-500">False Positives</div>
          <div className="text-xl font-bold font-mono text-purple-400 mt-1">
            {summary?.metrics?.false_positives_prevented ?? 0}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Disproved & logged</div>
        </GlassCard>

        <GlassCard className="p-3 border-slate-800/80 bg-slate-900/40">
          <div className="text-[10px] font-mono uppercase text-slate-500">In Validation</div>
          <div className="text-xl font-bold font-mono text-amber-400 mt-1">
            {summary?.metrics?.under_analysis ?? 0}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Awaiting evidence</div>
        </GlassCard>
      </div>

      {/* Tabs & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab('reverifications')}
            className={`px-3 py-1.5 text-xs font-mono rounded-lg transition-all flex items-center space-x-2 ${
              activeTab === 'reverifications'
                ? 'bg-purple-950/80 text-purple-300 border border-purple-700/80 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 border border-transparent'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Re-Verification Diffs ({reverifications.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('false_positives')}
            className={`px-3 py-1.5 text-xs font-mono rounded-lg transition-all flex items-center space-x-2 ${
              activeTab === 'false_positives'
                ? 'bg-purple-950/80 text-purple-300 border border-purple-700/80 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 border border-transparent'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>False Positives Knowledge Bank ({falsePositives.length})</span>
          </button>
        </div>

        <button
          onClick={() => setMarkModalOpen(true)}
          className="px-3 py-1.5 text-xs font-mono rounded border border-purple-800/80 bg-purple-950/40 text-purple-300 hover:bg-purple-900/50 flex items-center space-x-1.5 self-start sm:self-auto"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Commit False Positive Lesson</span>
        </button>
      </div>

      {/* Tab 1: Re-Verification Differential History */}
      {activeTab === 'reverifications' && (
        <div className="space-y-4">
          {reverifications.length === 0 ? (
            <GlassCard className="p-8 text-center border-slate-800">
              <CheckCircle2 className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-slate-400 text-sm font-mono">No differential re-verification runs committed yet.</p>
            </GlassCard>
          ) : (
            reverifications.map((r, i) => (
              <GlassCard key={i} className="p-5 border-slate-800/90 bg-slate-950/50 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                  <div className="flex items-center space-x-2.5">
                    <span className="font-mono text-xs text-purple-400 font-bold">{r.finding_id}</span>
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {r.previous_status} → <strong className="text-emerald-400">{r.new_status}</strong>
                    </span>
                    <h3 className="text-sm font-semibold text-slate-200">{r.finding_title}</h3>
                  </div>
                  <span className="text-xs font-mono text-slate-500">{r.timestamp}</span>
                </div>

                <p className="text-xs text-slate-300">{r.summary}</p>

                {/* Command executed */}
                <div className="bg-slate-900/90 border border-slate-800 rounded p-2 text-xs font-mono text-slate-400">
                  <span className="text-slate-500 mr-2">$</span>
                  <span className="text-emerald-400">{r.command_executed}</span>
                </div>

                {/* Side by side Before vs After */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                  <div className="space-y-1">
                    <div className="text-[10px] font-mono uppercase tracking-wider text-rose-400 flex items-center space-x-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-400 inline-block" />
                      <span>Observed Before Fix</span>
                    </div>
                    <pre className="p-2.5 rounded bg-rose-950/20 border border-rose-900/40 text-[11px] font-mono text-rose-300 overflow-x-auto whitespace-pre-wrap max-h-32">
                      {r.output_before}
                    </pre>
                  </div>

                  <div className="space-y-1">
                    <div className="text-[10px] font-mono uppercase tracking-wider text-emerald-400 flex items-center space-x-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" />
                      <span>Observed After Patch (Verified)</span>
                    </div>
                    <pre className="p-2.5 rounded bg-emerald-950/20 border border-emerald-900/40 text-[11px] font-mono text-emerald-300 overflow-x-auto whitespace-pre-wrap max-h-32">
                      {r.output_after}
                    </pre>
                  </div>
                </div>
              </GlassCard>
            ))
          )}
        </div>
      )}

      {/* Tab 2: False Positives Knowledge Bank */}
      {activeTab === 'false_positives' && (
        <div className="space-y-3">
          {falsePositives.length === 0 ? (
            <GlassCard className="p-8 text-center border-slate-800">
              <ShieldCheck className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-slate-400 text-sm font-mono">No findings flagged as false positive yet.</p>
            </GlassCard>
          ) : (
            falsePositives.map((fp, i) => (
              <GlassCard key={i} className="p-4 border-slate-800/90 bg-slate-950/40">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/60 pb-2.5 mb-2.5">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs text-purple-400 font-bold">{fp.finding_id}</span>
                    <span className="px-2 py-0.5 text-xs font-mono rounded bg-purple-950/60 text-purple-400 border border-purple-800/50">
                      FALSE_POSITIVE
                    </span>
                    <h3 className="text-sm font-semibold text-slate-100">{fp.title}</h3>
                  </div>
                  <span className="text-xs font-mono text-slate-400 border border-slate-800 px-2 py-0.5 rounded">
                    {fp.category}
                  </span>
                </div>

                <div className="space-y-1.5">
                  <div className="text-xs font-mono text-slate-400">
                    <strong className="text-purple-300">Technical Disproof & Boundary Rationale:</strong>
                  </div>
                  <p className="text-xs text-slate-300 bg-slate-900/80 border border-slate-800/80 rounded p-2.5 font-mono">
                    {fp.why_disproved}
                  </p>
                </div>
              </GlassCard>
            ))
          )}
        </div>
      )}

      {/* Commit False Positive Modal */}
      {markModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
          <div className="bg-slate-950 border border-slate-800 rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                <span>Commit False Positive Lesson</span>
              </h3>
              <button
                onClick={() => setMarkModalOpen(false)}
                className="text-slate-500 hover:text-slate-300 font-mono text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCommitFalsePositive} className="space-y-3">
              <div>
                <label className="text-xs font-mono uppercase tracking-wider text-slate-400 block mb-1">
                  Target Finding ID
                </label>
                <input
                  type="text"
                  placeholder="e.g. FINDING-001, DEMO-SEC-01"
                  value={selectedFindingToMark}
                  onChange={e => setSelectedFindingToMark(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-purple-500"
                  required
                />
              </div>

              <div>
                <label className="text-xs font-mono uppercase tracking-wider text-slate-400 block mb-1">
                  Technical Disproof Rationale & Boundary Justification
                </label>
                <textarea
                  rows={3}
                  placeholder="Explain why the probe confirmed safety (e.g., proper authentication barrier in place, intended internal microservice token, or non-exploitable configuration)..."
                  value={markRationale}
                  onChange={e => setMarkRationale(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-purple-500"
                  required
                />
              </div>

              <div className="flex flex-col sm:flex-row justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setMarkModalOpen(false)}
                  className="px-3 py-1.5 text-xs font-mono rounded border border-slate-800 text-slate-400 hover:bg-slate-900 justify-center text-center"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingMark}
                  className="px-4 py-1.5 text-xs font-mono rounded bg-purple-600 hover:bg-purple-500 text-white font-medium disabled:opacity-50 justify-center text-center"
                >
                  {submittingMark ? 'Saving...' : 'Commit to Memory'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Module Scope & Limitations */}
      <div className="border border-slate-800/80 rounded-lg p-3 bg-slate-900/30 text-xs text-slate-500 font-mono flex items-start space-x-2">
        <Info className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-400">Experience DB Scope:</strong> Retains verifiable historical differential outcomes and false positive lessons. Historical lessons enhance detection accuracy across recurring assessments without overwriting raw evidence files.
        </div>
      </div>
    </div>
  );
};
