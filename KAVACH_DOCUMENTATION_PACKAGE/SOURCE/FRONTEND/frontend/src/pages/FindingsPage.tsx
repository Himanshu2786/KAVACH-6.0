import React, { useState, useEffect } from 'react';
import {
  AlertOctagon,
  Search,
  ArrowRight,
  CheckCircle2,
  FileCheck2,
  ShieldAlert,
  Globe,
  Clock,
  Hash
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { Finding, WorldCorrelationItem } from '../types';

export const FindingsPage: React.FC = () => {
  const {
    activeAssessment, navigate, isDemoMode,
    urlAssessmentState, urlFindingsCount,
    setSelectedUrlFindingId, markUrlFindingsViewed,
    setSelectedWorldEventId,
  } = useApp();

  // ── Backend findings (for active backend assessment) ──────────────────────
  const [backendFindings, setBackendFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(false);
  const [correlations, setCorrelations] = useState<WorldCorrelationItem[]>([]);

  // ── UI filters ────────────────────────────────────────────────────────────
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');

  // ── Source mode selection ─────────────────────────────────────────────────
  // Rule:
  // 1. active real/historical assessment exists -> 'backend'
  // 2. explicit URL source chosen by user or only URL data exists without active assessment -> 'url'
  // 3. no active assessment -> 'backend' (empty state or demo mode if enabled)
  const urlResult = urlAssessmentState.result;
  const hasUrlData = Boolean(urlResult && urlResult.findings && urlResult.findings.length > 0);
  const [selectedSource, setSelectedSource] = useState<'auto' | 'backend' | 'url'>('auto');

  const sourceMode: 'url' | 'backend' =
    selectedSource === 'url' ? 'url' :
    selectedSource === 'backend' ? 'backend' :
    activeAssessment ? 'backend' :
    (hasUrlData ? 'url' : 'backend');

  // Mark as viewed when this page mounts
  useEffect(() => {
    markUrlFindingsViewed();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Load backend findings strictly for active assessment
  useEffect(() => {
    if (sourceMode === 'backend') {
      if (activeAssessment) {
        setLoading(true);
        api.getFindings({ assessment_id: activeAssessment.id })
          .then((data) => { setBackendFindings(data); setLoading(false); })
          .catch(() => { setBackendFindings([]); setLoading(false); });
      } else if (isDemoMode) {
        setLoading(true);
        api.getFindings({ is_demo: true })
          .then((data) => { setBackendFindings(data); setLoading(false); })
          .catch(() => { setBackendFindings([]); setLoading(false); });
      } else {
        setBackendFindings([]);
        setLoading(false);
      }
    }
  }, [activeAssessment, sourceMode, isDemoMode]);

  // Load World Monitor correlations for active findings
  useEffect(() => {
    const currentFindings = sourceMode === 'url' ? (urlResult?.findings ?? []) : backendFindings;
    if (currentFindings && currentFindings.length > 0) {
      const targetUrl = sourceMode === 'url' ? urlResult?.target_url : activeAssessment?.target_url;
      api.correlateWorldEvents({
        target_url: targetUrl || 'localhost',
        findings: currentFindings,
        mode: 'live'
      })
        .then((res) => {
          if (res && res.correlations) {
            setCorrelations(res.correlations);
          }
        })
        .catch(() => {
          // silently handle if offline
        });
    } else {
      setCorrelations([]);
    }
  }, [sourceMode, urlResult, backendFindings, activeAssessment]);

  // ── URL findings rendering ────────────────────────────────────────────────
  const urlFindings = urlResult?.findings ?? [];
  const filteredUrlFindings = urlFindings.filter((f) => {
    const matchSearch =
      f.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchSev = severityFilter === 'ALL' || f.severity === severityFilter;
    return matchSearch && matchSev;
  });

  // ── Backend findings rendering ────────────────────────────────────────────
  const filteredBackendFindings = backendFindings.filter((f) => {
    const matchSearch =
      f.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.affected_component.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchSev = severityFilter === 'ALL' || f.base_severity === severityFilter;
    return matchSearch && matchSev;
  });

  const getSeverityColor = (sev: string) => {
    switch (sev?.toUpperCase()) {
      case 'CRITICAL': case 'HIGH': return { dot: 'bg-red-400', text: 'text-red-400' };
      case 'MEDIUM':               return { dot: 'bg-amber-400', text: 'text-amber-400' };
      default:                     return { dot: 'bg-emerald-400', text: 'text-emerald-400' };
    }
  };

  const displayCount = sourceMode === 'url' ? filteredUrlFindings.length : filteredBackendFindings.length;

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-20">

      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-xs font-mono text-neutral-500 uppercase tracking-widest mb-1">
            Security Intelligence
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            Findings Catalog
          </h1>
          <p className="text-xs text-neutral-400 mt-1">
            Deterministic security observations with cryptographic evidence backing.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-neutral-400">
          {/* Source switch toggle if both exist */}
          {urlResult && activeAssessment && (
            <div className="flex items-center bg-white/[0.04] p-1 rounded-lg border border-white/[0.08]">
              <button
                onClick={() => setSelectedSource('backend')}
                className={`px-2.5 py-1 rounded text-xs transition-colors cursor-pointer ${
                  sourceMode === 'backend' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-neutral-400 hover:text-white'
                }`}
              >
                Assessment ({activeAssessment.id})
              </button>
              <button
                onClick={() => setSelectedSource('url')}
                className={`px-2.5 py-1 rounded text-xs transition-colors cursor-pointer ${
                  sourceMode === 'url' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-neutral-400 hover:text-white'
                }`}
              >
                URL Check ({urlResult.run_id || 'Scan'})
              </button>
            </div>
          )}

          {/* Source badge */}
          {sourceMode === 'url' && urlResult && !activeAssessment && (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/[0.05] border border-white/[0.1]">
              <Globe className="w-3 h-3 text-neutral-400" />
              <span className="text-neutral-300 truncate max-w-[180px]" title={urlResult.target_url}>
                {urlResult.hostname}
              </span>
            </div>
          )}
          <span>
            Showing: <span className="px-1.5 py-0.5 rounded bg-white/[0.08] text-white font-semibold">{displayCount}</span>
          </span>
        </div>
      </div>

      {/* ── What is a Finding? — Contextual guidance ── */}
      <details className="rounded-xl border border-white/[0.08] glass-panel overflow-hidden">
        <summary className="flex items-center justify-between px-4 py-3 cursor-pointer select-none text-xs font-mono text-neutral-400 hover:text-neutral-200 transition-colors list-none">
          <span className="flex items-center gap-2">
            <ShieldAlert className="w-3.5 h-3.5 text-neutral-400" />
            <span className="font-semibold text-neutral-300">What is a Finding?</span>
            <span className="hidden sm:inline text-neutral-500">— How to use this page</span>
          </span>
          <span className="text-neutral-500 text-[10px]">Click to expand</span>
        </summary>
        <div className="px-4 pb-4 pt-1 space-y-3 border-t border-white/[0.06]">
          <p className="text-xs text-neutral-400 leading-relaxed">
            A <strong className="text-white">Finding</strong> is a security condition detected by KAVACH that requires
            validation and evidence before it should be treated as a confirmed issue. Findings are{' '}
            <em>observations</em>, not guarantees — each must be backed by technical proof.
          </p>
          <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono">
            {['URL Check', 'Finding', 'Evidence', 'Verification', 'Remediation', 'Re-Verify'].map((step, i, arr) => (
              <React.Fragment key={step}>
                <span className="px-2 py-0.5 rounded bg-white/[0.06] border border-white/[0.08] text-neutral-300">{step}</span>
                {i < arr.length - 1 && <ArrowRight className="w-3 h-3 text-neutral-600 flex-shrink-0" />}
              </React.Fragment>
            ))}
          </div>
          <div className="p-3 rounded-lg glass-terminal text-[11px] font-mono space-y-1">
            <div className="text-neutral-500 uppercase text-[10px] tracking-wider mb-1">Example</div>
            <p className="text-neutral-400"><span className="text-white">1.</span> Run URL Check on your target.</p>
            <p className="text-neutral-400"><span className="text-white">2.</span> Findings appear here with severity and location.</p>
            <p className="text-neutral-400"><span className="text-white">3.</span> Click <span className="text-white">View Evidence</span> to see what KAVACH actually observed.</p>
            <p className="text-neutral-400"><span className="text-white">4.</span> Run the verification command in your terminal to confirm independently.</p>
            <p className="text-neutral-400"><span className="text-white">5.</span> After fixing, go back to URL Check and click <span className="text-white">Re-check</span>.</p>
          </div>
        </div>
      </details>

      {/* ── Active Assessment context banner (Backend Mode) ── */}
      {sourceMode === 'backend' && activeAssessment && (
        <div className="flex flex-wrap items-center gap-4 px-4 py-3 rounded-xl glass-level-1 text-[11px] font-mono">
          <div className="flex items-center gap-1.5">
            <Hash className="w-3 h-3 text-cyan-400" />
            <span className="text-neutral-500">ASSESSMENT:</span>
            <span className="text-cyan-300 font-semibold">{activeAssessment.id}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Globe className="w-3 h-3 text-neutral-500" />
            <span className="text-neutral-500">TARGET:</span>
            <span className="text-neutral-200 truncate max-w-[240px]">{activeAssessment.target_url}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Clock className="w-3 h-3 text-neutral-500" />
            <span className="text-neutral-500">STAGE:</span>
            <span className="text-neutral-300 font-semibold">{activeAssessment.current_stage || 'REPORT'}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
              activeAssessment.is_demo
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
            }`}>
              {activeAssessment.is_demo ? 'DEMO MODE' : 'REAL ASSESSMENT'}
            </span>
          </div>
        </div>
      )}

      {/* ── Assessment context banner (URL Mode) ── */}
      {sourceMode === 'url' && urlResult && (
        <div className="flex flex-wrap items-center gap-4 px-4 py-3 rounded-xl glass-level-1 text-[11px] font-mono">
          {urlResult.run_id && (
            <div className="flex items-center gap-1.5">
              <Hash className="w-3 h-3 text-cyan-400" />
              <span className="text-neutral-500">RUN:</span>
              <span className="text-cyan-300 font-semibold">{urlResult.run_id}</span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <Globe className="w-3 h-3 text-neutral-500" />
            <span className="text-neutral-500">TARGET:</span>
            <span className="text-neutral-200 truncate max-w-[240px]">{urlResult.target_url}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Clock className="w-3 h-3 text-neutral-500" />
            <span className="text-neutral-500">ASSESSED:</span>
            <span className="text-neutral-400">{urlResult.timestamp}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-3 h-3 text-neutral-500" />
            <span className="text-neutral-500">SCORE:</span>
            <span className={`font-semibold ${urlResult.security_score >= 80 ? 'text-emerald-400' : urlResult.security_score >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
              {urlResult.security_score}/100 — {urlResult.score_label}
            </span>
          </div>
        </div>
      )}

      {/* ── Filters ── */}
      <div className="p-3 rounded-xl glass-level-2">
        <div className="flex flex-col sm:flex-row gap-2.5 text-xs font-mono">
          <div className="relative flex-1">
            <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-neutral-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search findings, category, or ID..."
              className="w-full pl-9 pr-3 py-2 rounded-lg glass-input text-white placeholder-neutral-500 outline-none"
            />
          </div>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 rounded-lg glass-select text-neutral-300 outline-none"
          >
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((s) => (
              <option key={s} value={s}>Severity: {s}</option>
            ))}
          </select>
        </div>
      </div>

      {/* ══════════════════════════════════════════
          URL ASSESSMENT FINDINGS (primary path)
         ══════════════════════════════════════════ */}
      {sourceMode === 'url' && (
        <div className="space-y-3">
          {filteredUrlFindings.length === 0 && (
            <div className="text-center py-16 rounded-xl border border-white/[0.06] glass-level-1 font-mono text-xs text-neutral-500 space-y-2">
              {urlFindings.length === 0 ? (
                <>
                  <FileCheck2 className="w-8 h-8 mx-auto text-neutral-600 mb-3" />
                  <p className="text-neutral-300 font-semibold">No findings were generated from this assessment.</p>
                  <p className="text-neutral-500 max-w-sm mx-auto">
                    The target passed all evaluated security checks. Run a URL Check to generate new results.
                  </p>
                </>
              ) : (
                <p>No findings matching current filters.</p>
              )}
            </div>
          )}

          {filteredUrlFindings.map((f, idx) => {
            const sev = getSeverityColor(f.severity);
            const hasEvidence = Boolean(f.evidence?.raw_observation);

            return (
              <div
                key={f.id}
                style={{ animationDelay: `${idx * 35}ms` }}
                className="p-5 rounded-xl glass-card glass-card-interactive flex flex-col md:flex-row md:items-center justify-between gap-4 group animate-in fade-in slide-in-from-bottom-2 duration-300"
              >
                {/* Left: severity, title, location, evidence status */}
                <div className="flex-1 space-y-2">
                  {/* Status line */}
                  <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
                    <div className="flex items-center gap-1.5">
                      <span className={`w-2 h-2 rounded-full ${sev.dot}`} />
                      <span className={`font-semibold ${sev.text}`}>{f.severity}</span>
                    </div>
                    <span className="text-neutral-600">/</span>
                    <span className="text-neutral-400">{f.id}</span>
                    <span className="text-neutral-600">/</span>
                    <span className="px-2 py-0.5 rounded bg-white/[0.04] border border-white/[0.06] text-neutral-400">
                      {f.category}
                    </span>
                    {hasEvidence && (
                      <>
                        <span className="text-neutral-600">/</span>
                        <div className="flex items-center gap-1">
                          <Hash className="w-3 h-3 text-neutral-500" />
                          <span className="text-neutral-500 font-mono text-[10px]">
                            {f.evidence.integrity_hash.slice(0, 12)}…
                          </span>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Title */}
                  <h3 className="text-base font-semibold tracking-tight text-white">{f.title}</h3>

                  {/* Simple evidence summary */}
                  {f.simple_evidence?.what_found && (
                    <p className="text-xs text-neutral-400 leading-relaxed max-w-2xl">
                      {f.simple_evidence.what_found}
                    </p>
                  )}

                  {/* Location & CWE */}
                  <div className="flex flex-wrap items-center gap-4 text-[11px] font-mono text-neutral-500 pt-0.5">
                    <div>
                      <span className="text-neutral-600 uppercase">Where: </span>
                      <span className="text-neutral-300">{f.technical_evidence?.target ?? urlResult?.hostname}</span>
                    </div>
                    {f.cwe_id && (
                      <div>
                        <span className="text-neutral-600 uppercase">CWE: </span>
                        <span className="text-neutral-300">{f.cwe_id}</span>
                      </div>
                    )}
                    {f.owasp_category && (
                      <div>
                        <span className="text-neutral-600 uppercase">OWASP: </span>
                        <span className="text-neutral-300">{f.owasp_category}</span>
                      </div>
                    )}
                  </div>

                  {/* World Monitor External Correlation (if correlated) */}
                  {correlations.filter((c) => c.related_finding_id === f.id || c.matched_finding_ids?.includes(f.id)).map((corr, cIdx) => (
                    <div key={cIdx} className="mt-3 p-3 rounded-lg glass-panel border-cyan-500/20 text-xs font-mono space-y-2">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2 text-cyan-400">
                          <Globe className="w-3.5 h-3.5" />
                          <span className="font-semibold tracking-wider uppercase text-[10px]">World Monitor Correlation</span>
                          <span className={`px-1.5 py-0.5 text-[9px] rounded font-bold uppercase ${
                            corr.confidence === 'HIGH' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                            corr.confidence === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                            'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                          }`}>
                            {corr.confidence} CONFIDENCE
                          </span>
                        </div>
                        <button
                          onClick={() => {
                            setSelectedWorldEventId(corr.event_id || corr.event?.id || null);
                            navigate('world-monitor');
                          }}
                          className="px-2.5 py-1 rounded bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/30 text-[11px] flex items-center gap-1.5 transition-colors cursor-pointer"
                        >
                          <span>View in World Monitor</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      </div>
                      <p className="text-neutral-300 text-[11px] leading-relaxed">
                        {corr.explanation}
                      </p>
                      {corr.distinction_note && (
                        <div className="text-neutral-500 text-[10px] italic">
                          {corr.distinction_note}
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Right: View Evidence button */}
                <div className="flex items-center gap-2 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-white/[0.06]">
                  {hasEvidence ? (
                    <button
                      onClick={() => {
                        setSelectedUrlFindingId(f.id);
                        navigate('evidence');
                      }}
                      title={`View evidence for: ${f.title}`}
                      className="px-4 py-2 rounded-lg bg-white text-black hover:bg-neutral-200 text-xs font-mono font-semibold flex items-center gap-1.5 transition-all shadow-sm cursor-pointer"
                    >
                      <FileCheck2 className="w-3.5 h-3.5" />
                      <span>View Evidence</span>
                      <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                    </button>
                  ) : (
                    <span className="px-3 py-1.5 rounded-lg glass-panel text-neutral-500 text-xs font-mono">
                      No Evidence
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ══════════════════════════════════════════
          BACKEND ASSESSMENT FINDINGS (fallback)
         ══════════════════════════════════════════ */}
      {sourceMode === 'backend' && (
        <div className="space-y-3">
          {/* Empty state — no URL assessment yet */}
          {!activeAssessment && !loading && (
            <div className="text-center py-16 rounded-xl glass-level-1 space-y-3">
              <AlertOctagon className="w-8 h-8 mx-auto text-neutral-600" />
              <p className="text-sm font-semibold text-neutral-300">No assessment results available yet.</p>
              <p className="text-xs text-neutral-500 max-w-sm mx-auto leading-relaxed">
                Run a <strong className="text-neutral-300">URL Check</strong> to generate findings and evidence.
                Results will appear here automatically after the scan completes.
              </p>
              <button
                onClick={() => navigate('url-check')}
                className="mt-2 btn-primary px-4 py-2 rounded-lg text-xs font-semibold cursor-pointer"
              >
                Go to URL Check →
              </button>
            </div>
          )}

          {loading && (
            <div className="text-center py-16 text-neutral-500 text-xs font-mono animate-pulse">
              Loading findings…
            </div>
          )}

          {filteredBackendFindings.map((f, idx) => {
            const sev = getSeverityColor(f.base_severity);
            return (
              <div
                key={f.id}
                style={{ animationDelay: `${idx * 35}ms` }}
                className="p-5 rounded-xl glass-card glass-card-interactive flex flex-col md:flex-row md:items-center justify-between gap-4 group animate-in fade-in duration-300"
              >
                <div className="flex-1 space-y-2">
                  <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
                    <div className="flex items-center gap-1.5">
                      <span className={`w-2 h-2 rounded-full ${sev.dot}`} />
                      <span className={`font-semibold ${sev.text}`}>{f.base_severity}</span>
                    </div>
                    <span className="text-neutral-600">/</span>
                    <span className="text-neutral-400">{f.id}</span>
                    <span className="text-neutral-600">/</span>
                    <span className="text-neutral-400">Evidence: {f.evidence_status}</span>
                  </div>
                  <h3 className="text-base font-semibold text-white">{f.title}</h3>
                  <p className="text-xs text-neutral-400 max-w-2xl">{f.description}</p>
                  <div className="text-[11px] font-mono text-neutral-500">
                    <span className="text-neutral-600 uppercase">Location: </span>
                    <span className="text-neutral-300">{f.affected_component}</span>
                  </div>

                  {/* World Monitor External Correlation (if correlated) */}
                  {correlations.filter((c) => c.related_finding_id === f.id || c.matched_finding_ids?.includes(f.id)).map((corr, cIdx) => (
                    <div key={cIdx} className="mt-3 p-3 rounded-lg glass-panel border-cyan-500/20 text-xs font-mono space-y-2">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2 text-cyan-400">
                          <Globe className="w-3.5 h-3.5" />
                          <span className="font-semibold tracking-wider uppercase text-[10px]">World Monitor Correlation</span>
                          <span className={`px-1.5 py-0.5 text-[9px] rounded font-bold uppercase ${
                            corr.confidence === 'HIGH' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                            corr.confidence === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                            'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                          }`}>
                            {corr.confidence} CONFIDENCE
                          </span>
                        </div>
                        <button
                          onClick={() => {
                            setSelectedWorldEventId(corr.event_id || corr.event?.id || null);
                            navigate('world-monitor');
                          }}
                          className="px-2.5 py-1 rounded bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/30 text-[11px] flex items-center gap-1.5 transition-colors cursor-pointer"
                        >
                          <span>View in World Monitor</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      </div>
                      <p className="text-neutral-300 text-[11px] leading-relaxed">
                        {corr.explanation}
                      </p>
                      {corr.distinction_note && (
                        <div className="text-neutral-500 text-[10px] italic">
                          {corr.distinction_note}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                <div className="shrink-0">
                  <button
                    onClick={() => navigate('evidence', f.id)}
                    className="btn-primary px-4 py-2 rounded-lg text-xs font-mono font-semibold flex items-center gap-1.5 transition-all cursor-pointer"
                  >
                    <span>View Evidence</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            );
          })}

          {filteredBackendFindings.length === 0 && !loading && activeAssessment && (
            <div className="text-center py-16 rounded-xl glass-level-1 space-y-3 font-mono">
              <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-400" />
              <p className="text-sm font-semibold text-slate-100">
                {backendFindings.length === 0
                  ? "No findings generated for this assessment."
                  : "No findings match current filters."}
              </p>
              <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
                {backendFindings.length === 0 ? (
                  <>
                    Assessment <strong className="text-cyan-300">{activeAssessment.id}</strong> targeting{" "}
                    <span className="text-slate-300">{activeAssessment.target_url}</span> has zero security vulnerabilities recorded.
                  </>
                ) : (
                  "Try adjusting your search terms or severity filter to view findings."
                )}
              </p>
            </div>
          )}
        </div>
      )}

    </div>
  );
};
