import React, { useState, useEffect, useRef } from 'react';
import {
  Globe,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Terminal,
  Lock,
  ShieldAlert,
  ArrowRight,
  Copy,
  Check,
  ExternalLink,
  Info,
  ChevronDown,
  ChevronUp,
  Cpu,
  Clock,
  Fingerprint,
  AlertOctagon
} from 'lucide-react';
import { api } from '../services/api';
import { UrlAssessmentResult, UrlFinding, UrlCheckItem } from '../types';
import { useApp } from '../context/AppContext';

export const UrlSecurityCheckPage: React.FC = () => {
  const { showToast, setUrlAssessmentResult, clearUrlAssessment, activeAssessment } = useApp();
  const [urlInput, setUrlInput] = useState('http://127.0.0.1:8000');
  const [authorized, setAuthorized] = useState(true);
  const [loading, setLoading] = useState(false);
  const [reverifying, setReverifying] = useState(false);
  const [assessment, setAssessment] = useState<UrlAssessmentResult | null>(null);
  const [evidenceMode, setEvidenceMode] = useState<'simple' | 'technical'>('simple');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showDiagnostics, setShowDiagnostics] = useState(false);

  // Request sequencing ref to prevent stale async responses from overwriting newer runs
  const scanSeqRef = useRef<number>(0);

  useEffect(() => {
    // Restore last scan from backend on mount
    api.getLatestUrlAssessment()
      .then((data) => {
        if (data && data.target_url) {
          setAssessment(data);
          setUrlInput(data.target_url);
          setUrlAssessmentResult(data);
        }
      })
      .catch(() => {});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput.trim()) {
      showToast('error', 'URL Required', 'Please enter a valid website URL or local development address.');
      return;
    }
    if (!authorized) {
      showToast('error', 'Scope Confirmation Required', 'Please acknowledge that you are authorized to assess this target.');
      return;
    }

    const currentSeq = ++scanSeqRef.current;
    setLoading(true);
    clearUrlAssessment();

    try {
      const res = await api.scanUrl(urlInput.trim(), activeAssessment?.id);
      // Discard response if a newer scan was initiated in the meantime
      if (currentSeq !== scanSeqRef.current) return;

      setAssessment(res);
      setUrlAssessmentResult(res);

      const fCount = res.findings?.length ?? 0;
      const statusText = res.assessment_status || 'COMPLETE';

      if (statusText === 'PARTIAL') {
        showToast(
          'warning',
          'Assessment Partial',
          `Completed ${res.completed_checks}/${res.supported_checks} checks. ${res.failed_checks || 0} detector(s) had network timeouts. Valid findings retained.`
        );
      } else if (statusText === 'FAILED') {
        showToast(
          'error',
          'Assessment Failed',
          res.assessment_message || 'Target host unreachable.'
        );
      } else {
        showToast(
          'success',
          'Assessment Completed',
          `Evaluated ${res.supported_checks} checks against ${res.hostname}. ${
            fCount > 0 ? `${fCount} finding(s) detected.` : 'No security findings detected.'
          }`
        );
      }
    } catch (err: any) {
      if (currentSeq === scanSeqRef.current) {
        showToast('error', 'Assessment Error', err.message || 'Failed to complete URL security assessment.');
      }
    } finally {
      if (currentSeq === scanSeqRef.current) {
        setLoading(false);
      }
    }
  };

  const handleReverify = async () => {
    if (!assessment || !assessment.target_url) return;
    const currentSeq = ++scanSeqRef.current;
    setReverifying(true);

    try {
      const res = await api.reverifyUrl(assessment.target_url);
      if (currentSeq !== scanSeqRef.current) return;

      setAssessment(res);
      setUrlAssessmentResult(res);
      const resCount = res.reverification?.resolved_count || 0;
      showToast(
        'info',
        'Re-verification Complete',
        `Re-evaluated target. ${resCount} finding(s) verified as resolved.`
      );
    } catch (err: any) {
      if (currentSeq === scanSeqRef.current) {
        showToast('error', 'Re-check Failed', err.message || 'Failed to re-verify target.');
      }
    } finally {
      if (currentSeq === scanSeqRef.current) {
        setReverifying(false);
      }
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/[0.08] pb-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-white/[0.08] text-white border border-white/15">
              DETECTION 1: WEB SECURITY
            </span>
            <span className="px-2 py-0.5 rounded text-xs bg-neutral-900 text-neutral-400 font-mono border border-white/[0.06]">
              RFC 9110 & RFC 8446
            </span>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <Globe className="w-8 h-8 text-white" />
            URL Security Assessment
          </h1>
          <p className="text-neutral-400 text-sm mt-1">
            Deterministic observation of transport encryption, TLS certificate validity, and HTTP defensive headers.
          </p>
        </div>

        {assessment && assessment.target_url && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowDiagnostics((prev) => !prev)}
              className="btn-secondary flex items-center gap-2 px-3 py-2 text-xs font-semibold"
            >
              <Cpu className="w-3.5 h-3.5 text-neutral-400" />
              {showDiagnostics ? 'Hide Diagnostics' : 'Dev Diagnostics'}
            </button>
            <button
              onClick={handleReverify}
              disabled={reverifying || loading}
              className="btn-secondary flex items-center gap-2 px-4 py-2 text-xs font-semibold disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${reverifying ? 'animate-spin text-white' : ''}`} />
              {reverifying ? 'Re-checking...' : 'Re-check Target'}
            </button>
          </div>
        )}
      </div>

      {/* Active Assessment Context & Run Attribution Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs font-mono">
        <div className="flex items-center gap-2">
          <span className="text-neutral-400">Active Assessment:</span>
          {activeAssessment ? (
            <span className="px-2.5 py-1 rounded bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              {activeAssessment.id}
              {activeAssessment.assessment_type && (
                <span className="text-[10px] text-cyan-400/80 font-normal">({activeAssessment.assessment_type})</span>
              )}
            </span>
          ) : (
            <span className="text-neutral-500 italic">None (Stand-alone URL Check)</span>
          )}
        </div>

        {assessment?.run_id && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-neutral-400">URL Check Run:</span>
            <span className="px-2.5 py-1 rounded bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 font-bold flex items-center gap-1.5">
              <Fingerprint className="w-3.5 h-3.5 text-indigo-400" />
              {assessment.run_id}
              <span className="text-[10px] text-indigo-400/80 font-normal">({assessment.run_type || 'URL_CHECK'})</span>
            </span>
            {assessment.parent_assessment_id && (
              <span className="text-[11px] text-neutral-400 flex items-center gap-1">
                ↳ linked to <span className="text-cyan-400 font-semibold">{assessment.parent_assessment_id}</span>
              </span>
            )}
          </div>
        )}
      </div>

      {/* Scope Notice & Target Input Form */}
      <div className="glass-level-2 rounded-2xl p-6 shadow-xl">
        <form onSubmit={handleScan} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-2">
              Target Website URL / Host Endpoint
            </label>
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Globe className="absolute left-3.5 top-3 w-5 h-5 text-neutral-500" />
                <input
                  type="text"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://example.com or http://127.0.0.1:8000"
                  className="w-full glass-input rounded-xl pl-11 pr-4 py-2.5 text-sm text-white placeholder-neutral-500 font-mono"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="btn-primary px-6 py-2.5 font-semibold text-sm rounded-xl transition flex items-center justify-center gap-2 min-w-[150px] disabled:opacity-50 cursor-pointer"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Checking...
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4" />
                    Check Target
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="flex items-center gap-2 pt-1 text-xs text-neutral-400">
            <input
              type="checkbox"
              id="scope-check"
              checked={authorized}
              onChange={(e) => setAuthorized(e.target.checked)}
              className="rounded border-white/20 bg-neutral-900 text-white focus:ring-0 focus:ring-offset-0 cursor-pointer"
            />
            <label htmlFor="scope-check" className="cursor-pointer select-none">
              I confirm authorization or own the specified host. KAVACH executes safe, non-destructive observations only.
            </label>
          </div>
        </form>
      </div>

      {/* Assessment Running Banner */}
      {loading && (
        <div className="p-4 glass-level-1 border border-cyan-500/30 rounded-2xl flex items-center gap-3 animate-pulse">
          <RefreshCw className="w-5 h-5 text-cyan-400 animate-spin" />
          <div className="text-xs">
            <p className="font-bold text-cyan-300 uppercase tracking-wider">Assessment In Progress</p>
            <p className="text-neutral-400">Executing safe TLS and HTTP response header observations. Results are locked until all checks finish.</p>
          </div>
        </div>
      )}

      {/* Assessment Results Section */}
      {assessment && assessment.target_url && !loading && (
        <div className="space-y-6">
          {/* Run Isolation & Status Banner */}
          <div className="glass-level-2 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border border-white/[0.08]">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-black/60 border border-white/10 font-mono text-xs text-neutral-300">
                <Fingerprint className="w-3.5 h-3.5 text-neutral-400" />
                <span>Run ID:</span>
                <strong className="text-white">{assessment.run_id || 'ASM-URL-PRIMARY'}</strong>
              </div>
              <button
                onClick={() => copyToClipboard(assessment.run_id || '', 'run_id')}
                className="text-neutral-400 hover:text-white text-xs flex items-center gap-1 transition"
                title="Copy Run ID"
              >
                {copiedId === 'run_id' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>

            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-1 text-xs font-bold font-mono rounded-full border uppercase ${
                assessment.assessment_status === 'COMPLETE' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                assessment.assessment_status === 'PARTIAL' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                'bg-red-500/10 text-red-400 border-red-500/30'
              }`}>
                STATUS: {assessment.assessment_status || 'COMPLETE'}
              </span>
              <span className="text-xs text-neutral-400 font-mono">
                {assessment.completed_checks}/{assessment.supported_checks} checks executed
              </span>
            </div>
          </div>

          {/* Partial Execution Notice if any checks had network limits */}
          {assessment.assessment_status === 'PARTIAL' && (
            <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-start gap-3 text-xs text-neutral-200">
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-amber-300 uppercase tracking-wider">Partial Assessment Notice</p>
                <p className="text-neutral-300 mt-0.5">
                  {assessment.assessment_message || 'Some checks encountered network or timeout constraints.'}
                  Valid findings are preserved and not silently deleted. Check Developer Diagnostics below for detector details.
                </p>
              </div>
            </div>
          )}

          {/* Top Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Score */}
            <div className="glass-level-2 rounded-2xl p-5 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Security Score</p>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-3xl font-extrabold text-white">{assessment.security_score}</span>
                  <span className="text-xs text-neutral-500">/ 100</span>
                </div>
                <p className={`text-xs font-semibold mt-1 ${
                  assessment.security_score >= 80 ? 'text-emerald-400' : assessment.security_score >= 50 ? 'text-amber-400' : 'text-red-400'
                }`}>
                  {assessment.score_label}
                </p>
              </div>
              <div className={`w-12 h-12 rounded-full flex items-center justify-center border ${
                assessment.security_score >= 80 ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400' :
                assessment.security_score >= 50 ? 'border-amber-500/40 bg-amber-500/10 text-amber-400' :
                'border-red-500/40 bg-red-500/10 text-red-400'
              }`}>
                <ShieldCheck className="w-6 h-6" />
              </div>
            </div>

            {/* Checks Completed */}
            <div className="glass-level-2 rounded-2xl p-5">
              <p className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Checks Executed</p>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-3xl font-extrabold text-white">{assessment.completed_checks}</span>
                <span className="text-xs text-neutral-500">of {assessment.supported_checks}</span>
              </div>
              <p className="text-xs text-neutral-400 mt-1">100% Safe observations</p>
            </div>

            {/* Findings Count */}
            <div className="glass-level-2 rounded-2xl p-5">
              <p className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Security Findings</p>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-3xl font-extrabold text-white">{assessment.findings_count}</span>
                <span className="text-xs text-neutral-500">detected</span>
              </div>
              <p className="text-xs text-amber-400 mt-1">Deterministic identities</p>
            </div>

            {/* Target Details */}
            <div className="glass-level-2 rounded-2xl p-5">
              <p className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Target Endpoint</p>
              <p className="text-sm font-mono text-white truncate mt-1 font-semibold">{assessment.hostname}</p>
              <p className="text-xs text-neutral-400 truncate mt-1">{assessment.timestamp}</p>
            </div>
          </div>

          {/* Re-verification Resolution Notification */}
          {assessment.reverification && (
            <div className="p-4 glass-level-1 border border-white/10 rounded-2xl space-y-2 text-xs text-neutral-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Info className="w-4 h-4 text-white shrink-0" />
                  <span>
                    Re-verified at <strong>{assessment.reverification.rechecked_at}</strong>.
                    Previous findings: <strong>{assessment.reverification.previous_findings_count}</strong>,
                    Current: <strong>{assessment.reverification.current_findings_count}</strong>.
                  </span>
                </div>
                <span className="px-2.5 py-1 bg-white/10 rounded-full font-semibold text-white border border-white/20">
                  {assessment.reverification.resolved_count} Resolved
                </span>
              </div>

              {/* Explicit Resolved Findings Diff Breakdown */}
              {assessment.reverification.resolved_findings && assessment.reverification.resolved_findings.length > 0 && (
                <div className="mt-2 pt-2 border-t border-white/[0.08] space-y-1">
                  <p className="text-[11px] font-mono uppercase tracking-wider text-emerald-400 font-bold">Resolved Since Previous Run:</p>
                  {assessment.reverification.resolved_findings.map((rf) => (
                    <div key={rf.id} className="flex items-center justify-between bg-black/40 px-3 py-1.5 rounded-lg border border-emerald-500/20">
                      <span className="font-mono text-white text-xs">{rf.id}: {rf.title}</span>
                      <span className="text-emerald-300 text-[11px]">{rf.reason}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Developer Diagnostics View */}
          {showDiagnostics && (
            <div className="glass-level-2 rounded-2xl p-6 space-y-4 border border-cyan-500/30">
              <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
                <div className="flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                    Developer Diagnostics & Detector Trace
                  </h3>
                </div>
                <span className="text-xs font-mono text-cyan-300">Run ID: {assessment.run_id}</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-white/10 text-neutral-400">
                      <th className="pb-2">Check ID</th>
                      <th className="pb-2">Detector / Check</th>
                      <th className="pb-2">Category</th>
                      <th className="pb-2">Status</th>
                      <th className="pb-2">Execution</th>
                      <th className="pb-2">Duration</th>
                      <th className="pb-2">Observation / Error</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/[0.04]">
                    {assessment.checks.map((chk: UrlCheckItem) => (
                      <tr key={chk.id} className="hover:bg-white/[0.02]">
                        <td className="py-2.5 text-neutral-300 font-semibold">{chk.id}</td>
                        <td className="py-2.5 text-white">{chk.name}</td>
                        <td className="py-2.5 text-neutral-400">{chk.category}</td>
                        <td className="py-2.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                            chk.status === 'PASS' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                            chk.status === 'WARNING' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                            'bg-red-500/10 text-red-400 border-red-500/30'
                          }`}>
                            {chk.status}
                          </span>
                        </td>
                        <td className="py-2.5 text-neutral-300">
                          {chk.execution_status || 'SUCCESS'}
                        </td>
                        <td className="py-2.5 text-cyan-300">
                          {chk.duration_ms !== undefined ? `${chk.duration_ms}ms` : '—'}
                        </td>
                        <td className="py-2.5 text-neutral-400 max-w-xs truncate" title={chk.observed}>
                          {chk.error_reason ? (
                            <span className="text-red-400">{chk.error_reason}</span>
                          ) : (
                            chk.observed
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Standard Checklist Grid */}
          <div className="glass-level-2 rounded-2xl p-6">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Standard Observation Checklist ({assessment.checks.length})
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {assessment.checks.map((chk: UrlCheckItem) => (
                <div key={chk.id} className="p-3.5 glass-panel rounded-xl flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-neutral-500">{chk.id}</span>
                      <span className="text-xs font-semibold text-white">{chk.name}</span>
                    </div>
                    <p className="text-xs text-neutral-400 line-clamp-1">{chk.observed}</p>
                  </div>
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded border uppercase shrink-0 ${
                    chk.status === 'PASS' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                    chk.status === 'WARNING' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                    'bg-red-500/10 text-red-400 border-red-500/30'
                  }`}>
                    {chk.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Findings & Evidence Section */}
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/[0.08] pb-3">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-amber-400" />
                <h3 className="text-base font-bold text-white">
                  Security Findings & Evidence ({assessment.findings.length})
                </h3>
              </div>

              {/* Segmented Control: Simple vs Technical */}
              <div className="flex items-center glass-level-1 p-1 rounded-xl">
                <button
                  onClick={() => setEvidenceMode('simple')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
                    evidenceMode === 'simple'
                      ? 'bg-white text-black shadow-sm font-bold'
                      : 'text-neutral-400 hover:text-white'
                  }`}
                >
                  Simple Explanation
                </button>
                <button
                  onClick={() => setEvidenceMode('technical')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
                    evidenceMode === 'technical'
                      ? 'bg-white text-black shadow-sm font-bold'
                      : 'text-neutral-400 hover:text-white'
                  }`}
                >
                  Technical Evidence
                </button>
              </div>
            </div>

            {assessment.findings.length === 0 ? (
              <div className="p-8 text-center glass-level-1 rounded-2xl">
                <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
                <h4 className="text-white font-semibold">No Security Flaws Detected</h4>
                <p className="text-xs text-neutral-400 mt-1">
                  All supported transport and security header baseline checks passed successfully.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {assessment.findings.map((f: UrlFinding) => (
                  <div
                    key={f.id}
                    className="glass-card glass-card-interactive rounded-2xl p-5 space-y-4 transition-all"
                  >
                    {/* Finding Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/[0.06] pb-3">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-mono text-cyan-400 font-semibold">{f.id}</span>
                          <span className={`px-2 py-0.5 text-[10px] font-bold rounded uppercase ${
                            f.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                            f.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                            'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                          }`}>
                            {f.severity}
                          </span>
                          <span className="text-xs text-neutral-400">{f.category}</span>
                          {f.reverification_status && (
                            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-white/10 text-neutral-300 border border-white/15">
                              {f.reverification_status}
                            </span>
                          )}
                        </div>
                        <h4 className="text-base font-bold text-white">{f.title}</h4>
                      </div>
                      <div className="flex items-center gap-2 text-xs font-mono text-neutral-400">
                        <span>{f.cwe_id}</span>
                        <span>•</span>
                        <span>{f.owasp_category.split('-')[0]}</span>
                      </div>
                    </div>

                    {/* Mode Content: Simple Explanation */}
                    {evidenceMode === 'simple' && f.simple_evidence && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs glass-panel p-4 rounded-xl">
                        <div>
                          <p className="font-semibold text-neutral-400 uppercase text-[10px] tracking-wider mb-1">What was found</p>
                          <p className="text-neutral-200">{f.simple_evidence.what_found}</p>
                        </div>
                        <div>
                          <p className="font-semibold text-neutral-400 uppercase text-[10px] tracking-wider mb-1">Where found</p>
                          <p className="text-white font-mono">{f.simple_evidence.where_found}</p>
                        </div>
                        <div>
                          <p className="font-semibold text-neutral-400 uppercase text-[10px] tracking-wider mb-1">Why it matters</p>
                          <p className="text-neutral-300">{f.simple_evidence.why_matters}</p>
                        </div>
                        <div>
                          <p className="font-semibold text-neutral-400 uppercase text-[10px] tracking-wider mb-1">Possible impact</p>
                          <p className="text-amber-300">{f.simple_evidence.possible_impact}</p>
                        </div>
                      </div>
                    )}

                    {/* Mode Content: Technical Evidence */}
                    {evidenceMode === 'technical' && f.technical_evidence && (
                      <div className="space-y-3">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-2 text-xs font-mono glass-panel p-3 rounded-xl">
                          <div>
                            <span className="text-neutral-500 block text-[10px]">RUN ID:</span>
                            <span className="text-white font-semibold">{f.run_id || assessment.run_id}</span>
                          </div>
                          <div>
                            <span className="text-neutral-500 block text-[10px]">TARGET:</span>
                            <span className="text-neutral-200">{f.technical_evidence.target}</span>
                          </div>
                          <div>
                            <span className="text-neutral-500 block text-[10px]">SCANNER RULE:</span>
                            <span className="text-neutral-200">{f.technical_evidence.rule}</span>
                          </div>
                          <div>
                            <span className="text-neutral-500 block text-[10px]">SHA-256 INTEGRITY:</span>
                            <span className="text-emerald-400 truncate block font-mono text-[11px]" title={f.evidence.integrity_hash}>
                              {f.evidence.integrity_hash.substring(0, 16)}...
                            </span>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                          <div className="glass-panel border-red-500/20 p-3 rounded-xl">
                            <span className="text-[10px] font-semibold text-red-400 uppercase block mb-1">Observed Response</span>
                            <p className="text-neutral-300 font-mono">{f.technical_evidence.observed}</p>
                          </div>
                          <div className="glass-panel border-emerald-500/20 p-3 rounded-xl">
                            <span className="text-[10px] font-semibold text-emerald-400 uppercase block mb-1">Expected Baseline</span>
                            <p className="text-neutral-300 font-mono">{f.technical_evidence.expected}</p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Terminal Reproduction Verification Box */}
                    {f.terminal_verification && (
                      <div className="glass-terminal rounded-xl p-3.5">
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-[11px] font-semibold text-neutral-300 flex items-center gap-1.5 font-mono">
                            <Terminal className="w-3.5 h-3.5 text-white" />
                            Safe Terminal Reproduction Command
                          </span>
                          <button
                            onClick={() => copyToClipboard(f.terminal_verification.command, f.id)}
                            className="text-neutral-400 hover:text-white text-[11px] flex items-center gap-1 transition cursor-pointer"
                          >
                            {copiedId === f.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                            {copiedId === f.id ? 'Copied' : 'Copy'}
                          </button>
                        </div>
                        <pre className="text-xs text-neutral-200 font-mono glass-code p-2.5 rounded-lg overflow-x-auto">
                          {f.terminal_verification.command}
                        </pre>
                      </div>
                    )}

                    {/* Remediation Box */}
                    {f.remediation && (
                      <div className="glass-panel border-emerald-500/20 rounded-xl p-3.5 text-xs space-y-1">
                        <p className="font-semibold text-emerald-400 flex items-center gap-1.5">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          Recommended Remediation Action
                        </p>
                        <p className="text-neutral-200 font-mono">{f.remediation.how_to_fix}</p>
                        <p className="text-neutral-400 text-[11px] mt-1">{f.remediation.why_matters}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
