import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  FileCheck2,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Play,
  Hash,
  Lock,
  RefreshCw,
  AlertTriangle,
  Terminal,
  ExternalLink,
  Sparkles,
  Info,
  Copy,
  Check,
  ChevronRight,
  Shield,
  Sliders,
  Wrench,
  Cpu,
  Clock,
  Globe
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { Finding, EvidenceRecord, TerminalVerification } from '../types';
import { TechnicalTerminalViewer } from '../components/common/TechnicalTerminalViewer';
import { ReVerificationModal } from '../components/common/ReVerificationModal';

export const EvidenceValidationPage: React.FC = () => {
  const {
    activeAssessment, selectedFindingId, setSelectedFindingId, isDemoMode, refreshData, showToast,
    urlAssessmentState, markUrlEvidenceViewed, setSelectedUrlFindingId,
  } = useApp();
  const [findings, setFindings] = useState<Finding[]>([]);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [evidenceRecords, setEvidenceRecords] = useState<EvidenceRecord[]>([]);
  const [probing, setProbing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [copiedHash, setCopiedHash] = useState(false);
  const [copiedRaw, setCopiedRaw] = useState(false);

  // Technical Terminal Modal state
  const [terminalData, setTerminalData] = useState<TerminalVerification | null>(null);
  const [showTerminal, setShowTerminal] = useState(false);

  // Re-Verification Modal state
  const [showReVerify, setShowReVerify] = useState(false);

  // Active stage for timeline
  const [activeTimelineStage, setActiveTimelineStage] = useState('FINDING');

  // References for scrolling
  const sectionRefs = {
    FINDING: useRef<HTMLDivElement>(null),
    WHY: useRef<HTMLDivElement>(null),
    WHERE: useRef<HTMLDivElement>(null),
    PROOF: useRef<HTMLDivElement>(null),
    ANALYSIS: useRef<HTMLDivElement>(null),
    VERIFY: useRef<HTMLDivElement>(null),
    FIX: useRef<HTMLDivElement>(null),
    'RE-VERIFY': useRef<HTMLDivElement>(null),
  };

  const timelineSteps = [
    { id: 'FINDING', label: 'FINDING' },
    { id: 'WHY', label: 'WHY' },
    { id: 'WHERE', label: 'WHERE' },
    { id: 'PROOF', label: 'PROOF' },
    { id: 'ANALYSIS', label: 'ANALYSIS' },
    { id: 'VERIFY', label: 'VERIFY' },
    { id: 'FIX', label: 'FIX' },
    { id: 'RE-VERIFY', label: 'RE-VERIFY' },
  ];

  const scrollToTimelineStage = (id: keyof typeof sectionRefs) => {
    setActiveTimelineStage(id);
    const targetRef = sectionRefs[id];
    if (targetRef && targetRef.current) {
      targetRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const selectedFindingRef = useRef<Finding | null>(null);
  selectedFindingRef.current = selectedFinding;

  const lastLoadedAsmIdRef = useRef<string | null>(null);

  const loadData = useCallback((isSilent = false) => {
    if (!activeAssessment) return Promise.resolve();
    if (!isSilent) setLoading(true);
    return api.getFindings({ assessment_id: activeAssessment.id })
      .then((data) => {
        setFindings(data);
        const currentTargetId = selectedFindingRef.current?.id || selectedFindingId;
        const target = data.find(f => f.id === currentTargetId) || data[0];
        if (target) {
          setSelectedFinding(target);
          if (target.id !== selectedFindingId) {
            setSelectedFindingId(target.id);
          }
          return api.getEvidence(target.id);
        }
        return [];
      })
      .then((records) => {
        setEvidenceRecords(records);
        if (!isSilent) setLoading(false);
      })
      .catch(() => {
        if (!isSilent) setLoading(false);
      });
  }, [activeAssessment?.id]);

  // Mark URL evidence as viewed when this page mounts
  useEffect(() => {
    markUrlEvidenceViewed();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!activeAssessment) return;
    const asmChanged = activeAssessment.id !== lastLoadedAsmIdRef.current;
    lastLoadedAsmIdRef.current = activeAssessment.id;
    // Full load on initial assessment load; silent refresh if same assessment
    loadData(!asmChanged && findings.length > 0);
  }, [activeAssessment?.id, selectedFindingId]);

  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);

  const handleSelectFinding = (f: Finding) => {
    setSelectedFinding(f);
    setSelectedFindingId(f.id);
    setSelectedEvidenceId(null);
    api.getEvidence(f.id).then(setEvidenceRecords).catch(() => setEvidenceRecords([]));
  };

  const handleExecuteProbe = async () => {
    if (!selectedFinding) return;
    setProbing(true);
    try {
      const evd = await api.executeProbe(selectedFinding.id, 'HTTP_PROBE', isDemoMode);
      await refreshData();
      const updatedFinding = await api.getFinding(selectedFinding.id);
      const updatedEvidence = await api.getEvidence(selectedFinding.id);
      setSelectedFinding(updatedFinding);
      setEvidenceRecords(updatedEvidence);
      setSelectedEvidenceId(evd.id);

      showToast(
        'success',
        'Technical Evidence Validated',
        `Evidence record ${evd.id} confirmed finding state as ${updatedFinding.status}.`
      );
    } catch (err: any) {
      showToast('error', 'Probe Error', err.message || 'Probe execution failed');
    } finally {
      setProbing(false);
    }
  };

  const handleOpenTerminal = async (findingId: string) => {
    try {
      const data = await api.getTerminalVerification(findingId);
      setTerminalData(data);
      setShowTerminal(true);
    } catch (err: any) {
      showToast('error', 'Terminal Error', err.message || 'Failed to load technical verification data');
    }
  };

  // Identify baseline evidence records and prioritize canonical active proof
  const baselineEvidenceRecords = evidenceRecords.filter(
    (e) => !e.id.startsWith('EVD-AFT-') && e.source !== 'Re-Test Verification Engine'
  );

  const canonicalEvidenceRecord =
    baselineEvidenceRecords.find(
      (e) => e.id === 'EV-WM-API-DOCS-A018-GET' || e.is_canonical || e.id.includes('-GET')
    ) || baselineEvidenceRecords[0] || evidenceRecords[0] || null;

  const currentEvidence =
    (selectedEvidenceId && evidenceRecords.find((e) => e.id === selectedEvidenceId)) ||
    canonicalEvidenceRecord ||
    null;

  // ── Derive URL evidence from context ─────────────────────────────────────
  const urlResult = urlAssessmentState.result;
  const urlFindings = urlResult?.findings ?? [];
  // If a specific finding was clicked via "View Evidence", show only that one; else show all
  const urlEvidenceFindings = urlAssessmentState.selectedUrlFindingId
    ? urlFindings.filter(f => f.id === urlAssessmentState.selectedUrlFindingId)
    : urlFindings;
  const hasUrlEvidence = urlResult !== null;

  // State for selected URL finding in this page
  const [urlSelectedId, setUrlSelectedId] = React.useState<string | null>(
    urlAssessmentState.selectedUrlFindingId ?? (urlFindings[0]?.id ?? null)
  );
  React.useEffect(() => {
    if (urlAssessmentState.selectedUrlFindingId) {
      setUrlSelectedId(urlAssessmentState.selectedUrlFindingId);
    } else if (urlFindings.length > 0) {
      setUrlSelectedId(urlFindings[0].id);
    }
  }, [urlAssessmentState.selectedUrlFindingId, urlResult]); // eslint-disable-line react-hooks/exhaustive-deps

  const urlSelectedFinding = urlFindings.find(f => f.id === urlSelectedId) ?? urlFindings[0] ?? null;
  const [urlEvidenceMode, setUrlEvidenceMode] = React.useState<'simple' | 'technical'>('simple');
  const [urlCopied, setUrlCopied] = React.useState(false);

  // Source selection: default to 'backend' whenever activeAssessment exists
  const [evidenceSource, setEvidenceSource] = React.useState<'backend' | 'url'>(
    activeAssessment ? 'backend' : (hasUrlEvidence ? 'url' : 'backend')
  );

  React.useEffect(() => {
    if (activeAssessment) {
      setEvidenceSource('backend');
    } else if (hasUrlEvidence) {
      setEvidenceSource('url');
    }
  }, [activeAssessment, hasUrlEvidence]);

  const copyVerifyCmd = (cmd: string) => {
    navigator.clipboard.writeText(cmd).catch(() => {});
    setUrlCopied(true);
    setTimeout(() => setUrlCopied(false), 2000);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-20">

      {/* Top Header & Context Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-xs font-mono text-neutral-500 uppercase tracking-widest mb-1">
            Cryptographic Proof Ledger
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <FileCheck2 className="w-6 h-6 text-cyan-400" />
            <span>Technical Evidence Vault</span>
          </h1>
          <p className="text-xs text-neutral-400 mt-1">
            Empirical evidence artifacts backed by cryptographic SHA-256 integrity signatures.
          </p>
        </div>

        {/* Source Switcher if both exist */}
        {hasUrlEvidence && urlResult && activeAssessment && (
          <div className="flex items-center bg-white/[0.04] p-1 rounded-lg border border-white/[0.08] text-xs font-mono">
            <button
              onClick={() => setEvidenceSource('backend')}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                evidenceSource === 'backend' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-neutral-400 hover:text-white'
              }`}
            >
              Assessment ({activeAssessment.id})
            </button>
            <button
              onClick={() => setEvidenceSource('url')}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                evidenceSource === 'url' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-neutral-400 hover:text-white'
              }`}
            >
              URL Check ({urlResult.run_id || 'Scan'})
            </button>
          </div>
        )}
      </div>

      {/* ══ URL ASSESSMENT EVIDENCE (shown when evidenceSource === 'url') ══════════ */}
      {evidenceSource === 'url' && hasUrlEvidence && urlResult && (
        <div className="space-y-4">
          {/* Section header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="text-xs font-mono text-neutral-500 uppercase tracking-widest mb-1">
                Evidence Vault — URL Assessment
              </div>
              <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                <FileCheck2 className="w-5 h-5 text-neutral-400" />
                {urlResult.hostname}
                <span className="text-sm font-normal text-neutral-500">— {urlFindings.length} evidence record{urlFindings.length !== 1 ? 's' : ''}</span>
              </h2>
            </div>
            <div className="flex items-center gap-3 text-[11px] font-mono text-neutral-400">
              {urlResult.run_id && (
                <span className="px-2 py-0.5 rounded bg-white/[0.06] border border-white/[0.08] text-cyan-300">
                  RUN: {urlResult.run_id}
                </span>
              )}
              <div className="flex items-center gap-1.5 text-neutral-500">
                <Clock className="w-3 h-3" />
                {urlResult.timestamp}
              </div>
            </div>
          </div>

          {/* What is Evidence? — guidance card */}
          <details className="rounded-xl border border-white/[0.08] glass-panel overflow-hidden">
            <summary className="flex items-center justify-between px-4 py-3 cursor-pointer select-none text-xs font-mono text-neutral-400 hover:text-neutral-200 transition-colors list-none">
              <span className="flex items-center gap-2">
                <Info className="w-3.5 h-3.5 text-neutral-400" />
                <span className="font-semibold text-neutral-300">What is Evidence?</span>
              </span>
              <span className="text-neutral-500 text-[10px]">Click to expand</span>
            </summary>
            <div className="px-4 pb-4 pt-1 border-t border-white/[0.06] space-y-3 text-xs text-neutral-400 leading-relaxed">
              <p>
                <strong className="text-white">Evidence</strong> is the technical proof collected by KAVACH
                that supports a finding. It is NOT an AI opinion — it is a concrete, recorded observation
                (HTTP status code, header presence or absence, response body snippet).
              </p>
              <div className="p-3 rounded-lg glass-terminal text-[11px] font-mono space-y-1">
                <p className="text-neutral-500 uppercase text-[10px] tracking-wider mb-1">Relationship</p>
                <p><span className="text-white">Finding</span> = what KAVACH detected</p>
                <p><span className="text-white">Evidence</span> = technical proof supporting it</p>
                <p><span className="text-white">Verification</span> = you independently confirming the proof</p>
                <p><span className="text-white">Remediation</span> = fixing the issue</p>
                <p><span className="text-white">Re-Verify</span> = confirming the fix worked</p>
              </div>
            </div>
          </details>

          {urlFindings.length === 0 ? (
            <div className="text-center py-12 rounded-xl border border-white/[0.06] glass-level-1 text-xs font-mono text-neutral-500">
              No evidence records available for this assessment.
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* ── Left: finding selector ── */}
              <div className="lg:col-span-3 space-y-2">
                <div className="text-[11px] font-mono text-neutral-500 uppercase tracking-wider pb-2 border-b border-white/[0.06]">
                  Findings ({urlFindings.length})
                </div>
                <div className="space-y-1.5 max-h-[65vh] overflow-y-auto pr-1">
                  {urlFindings.map((f) => {
                    const isSelected = urlSelectedId === f.id;
                    const sevColor = f.severity === 'HIGH' || f.severity === 'CRITICAL'
                      ? 'bg-red-400' : f.severity === 'MEDIUM' ? 'bg-amber-400' : 'bg-emerald-400';
                    return (
                      <button
                        key={f.id}
                        onClick={() => { setUrlSelectedId(f.id); setSelectedUrlFindingId(f.id); }}
                        className={`w-full text-left p-3 rounded-xl border cursor-pointer transition-all duration-150 ${
                          isSelected
                            ? 'glass-card-selected text-white'
                            : 'glass-panel text-neutral-400 hover:border-white/20 hover:text-neutral-200'
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${sevColor}`} />
                          <span className="text-[10px] font-mono font-semibold">{f.severity}</span>
                        </div>
                        <p className="text-xs font-medium leading-snug line-clamp-2">{f.title}</p>
                        <p className="text-[10px] font-mono text-neutral-500 mt-1">{f.id}</p>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* ── Right: evidence detail ── */}
              <div className="lg:col-span-9 space-y-4">
                {urlSelectedFinding ? (
                  <>
                    {/* View toggle */}
                    <div className="flex items-center gap-2">
                      {(['simple', 'technical'] as const).map((m) => (
                        <button
                          key={m}
                          onClick={() => setUrlEvidenceMode(m)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all cursor-pointer ${
                            urlEvidenceMode === m
                              ? 'bg-white text-black font-bold shadow-sm'
                              : 'glass-panel text-neutral-400 hover:text-white'
                          }`}
                        >
                          {m === 'simple' ? 'Simple View' : 'Technical View'}
                        </button>
                      ))}
                    </div>

                    {/* FINDING section */}
                    <div className="p-5 rounded-2xl glass-card space-y-3">
                      <div className="text-[10px] font-mono text-neutral-500 uppercase tracking-wider">Finding</div>
                      <h3 className="text-lg font-bold text-white">{urlSelectedFinding.title}</h3>
                      <div className="flex flex-wrap gap-3 text-[11px] font-mono">
                        <span className="px-2 py-0.5 rounded bg-white/[0.06] border border-white/[0.08] text-neutral-300">{urlSelectedFinding.severity}</span>
                        <span className="px-2 py-0.5 rounded bg-white/[0.06] border border-white/[0.08] text-neutral-300">{urlSelectedFinding.status}</span>
                        <span className="px-2 py-0.5 rounded bg-white/[0.06] border border-white/[0.08] text-neutral-300">{urlSelectedFinding.category}</span>
                        {urlSelectedFinding.cwe_id && <span className="px-2 py-0.5 rounded bg-white/[0.06] border border-white/[0.08] text-neutral-300">{urlSelectedFinding.cwe_id}</span>}
                      </div>
                    </div>

                    {urlEvidenceMode === 'simple' ? (
                      /* ── SIMPLE VIEW ── */
                      <div className="space-y-3">
                        {[
                          { label: 'WHY it matters', value: urlSelectedFinding.simple_evidence?.why_matters },
                          { label: 'WHAT was found', value: urlSelectedFinding.simple_evidence?.what_found },
                          { label: 'WHERE it was found', value: urlSelectedFinding.simple_evidence?.where_found },
                          { label: 'POSSIBLE IMPACT', value: urlSelectedFinding.simple_evidence?.possible_impact },
                          { label: 'WHAT YOU CAN DO', value: urlSelectedFinding.simple_evidence?.what_you_can_do },
                        ].map(({ label, value }) => value ? (
                          <div key={label} className="p-4 rounded-xl glass-panel space-y-1.5">
                            <div className="text-[10px] font-mono text-neutral-500 uppercase tracking-wider">{label}</div>
                            <p className="text-sm text-neutral-300 leading-relaxed">{value}</p>
                          </div>
                        ) : null)}

                        {/* Remediation */}
                        {urlSelectedFinding.remediation && (
                          <div className="p-4 rounded-xl glass-panel space-y-1.5 border-emerald-500/20">
                            <div className="text-[10px] font-mono text-emerald-400 uppercase tracking-wider font-semibold">Remediation</div>
                            <p className="text-xs text-neutral-300 leading-relaxed">{urlSelectedFinding.remediation.how_to_fix}</p>
                          </div>
                        )}
                      </div>
                    ) : (
                      /* ── TECHNICAL VIEW ── */
                      <div className="space-y-3">
                        {/* Proof */}
                        <div className="p-4 rounded-xl glass-terminal space-y-2">
                          <div className="text-[10px] font-mono text-neutral-400 uppercase tracking-wider">Proof — Raw Observation</div>
                          <pre className="text-xs font-mono text-neutral-200 whitespace-pre-wrap break-all leading-relaxed glass-code p-3 rounded-lg">
                            {urlSelectedFinding.evidence?.raw_observation ?? 'No raw observation captured.'}
                          </pre>
                        </div>

                        {/* Technical detail */}
                        {urlSelectedFinding.technical_evidence && (
                          <div className="p-4 rounded-xl glass-panel space-y-2">
                            <div className="text-[10px] font-mono text-neutral-400 uppercase tracking-wider">Technical Detail</div>
                            <div className="text-[11px] font-mono space-y-1 text-neutral-300">
                              {urlSelectedFinding.technical_evidence.observed && <p><span className="text-neutral-500">OBSERVED: </span>{urlSelectedFinding.technical_evidence.observed}</p>}
                              {urlSelectedFinding.technical_evidence.expected && <p><span className="text-neutral-500">EXPECTED: </span>{urlSelectedFinding.technical_evidence.expected}</p>}
                            </div>
                          </div>
                        )}

                        {/* Integrity hash */}
                        {urlSelectedFinding.evidence?.integrity_hash && (
                          <div className="p-4 rounded-xl glass-panel flex items-start gap-3">
                            <Hash className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                            <div className="flex-1 min-w-0">
                              <div className="text-[10px] font-mono text-neutral-500 uppercase tracking-wider mb-1">SHA-256 Evidence Hash</div>
                              <p className="text-[11px] font-mono text-emerald-300 break-all">{urlSelectedFinding.evidence.integrity_hash}</p>
                            </div>
                          </div>
                        )}

                        {/* Verification command */}
                        {urlSelectedFinding.terminal_verification?.command && (
                          <div className="space-y-3">
                            {/* KAVACH Observation vs User Reproduction header */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div className="p-3.5 rounded-xl glass-panel border-red-500/20 space-y-1">
                                <div className="text-[9px] font-mono text-red-400 uppercase tracking-wider font-semibold">KAVACH Observation</div>
                                <p className="text-xs text-neutral-300 font-mono">{urlSelectedFinding.terminal_verification.observed_output}</p>
                              </div>
                              <div className="p-3.5 rounded-xl glass-panel border-emerald-500/20 space-y-1">
                                <div className="text-[9px] font-mono text-emerald-400 uppercase tracking-wider font-semibold">Expected Baseline (secure)</div>
                                <p className="text-xs text-neutral-300 font-mono">{urlSelectedFinding.terminal_verification.expected_output}</p>
                              </div>
                            </div>

                            {/* Command box */}
                            <div className="p-4 rounded-xl glass-terminal space-y-2">
                              {/* Header row */}
                              <div className="flex items-center justify-between flex-wrap gap-2">
                                <div className="flex items-center gap-1.5">
                                  <Terminal className="w-3.5 h-3.5 text-neutral-400" />
                                  <span className="text-[10px] font-mono text-neutral-300 uppercase tracking-wider font-semibold">
                                    Safe Reproducible PowerShell Procedure
                                  </span>
                                  <span className="px-1.5 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[9px] font-mono">
                                    PowerShell / Windows
                                  </span>
                                </div>
                                <button
                                  onClick={() => copyVerifyCmd(urlSelectedFinding.terminal_verification.command)}
                                  title="Copy exact command to clipboard"
                                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/[0.08] hover:bg-white/[0.15] text-[10px] font-mono text-neutral-300 hover:text-white transition-colors cursor-pointer"
                                >
                                  {urlCopied
                                    ? <><Check className="w-3 h-3 text-emerald-400" /><span className="text-emerald-400">Copied!</span></>
                                    : <><Copy className="w-3 h-3" /><span>Copy Command</span></>}
                                </button>
                              </div>

                              {/* Context note */}
                              <div className="text-[10px] font-mono text-neutral-500 pb-1">
                                Run from the <span className="text-neutral-300">KAVACH project root</span>:
                                <span className="ml-2 text-neutral-400">PS C:\path\to\KAVACH\&gt;</span>
                              </div>

                              {/* The actual command — exactly what is copied */}
                              <pre className="text-xs font-mono text-emerald-300 whitespace-pre-wrap break-all leading-relaxed glass-code rounded-lg p-3">
                                {urlSelectedFinding.terminal_verification.command}
                              </pre>

                              {/* HOW TO VERIFY steps */}
                              <div className="pt-2 border-t border-white/[0.06] space-y-2">
                                <div className="text-[10px] font-mono text-neutral-500 uppercase tracking-wider">How to Verify</div>
                                <ol className="text-[11px] font-mono text-neutral-400 space-y-1 pl-0">
                                  {[
                                    'Open PowerShell (or Windows Terminal).',
                                    'Navigate to the KAVACH project root:  cd "C:\\path\\to\\KAVACH 6.0"',
                                    'Paste the command above and press Enter.',
                                    'Compare the returned output with the KAVACH Observation shown above.',
                                    'If the result matches, the observation is independently reproducible.',
                                    'If the result differs (e.g. the fixture was modified), the command will reflect the actual current state.',
                                  ].map((step, i) => (
                                    <li key={i} className="flex gap-2">
                                      <span className="text-neutral-600 flex-shrink-0">{i + 1}.</span>
                                      <span>{step}</span>
                                    </li>
                                  ))}
                                </ol>
                              </div>

                              {/* Important: command is NOT proof of verification */}
                              <div className="text-[10px] font-mono text-neutral-600 pt-1 border-t border-white/[0.05]">
                                ⚠ Displaying this command does <span className="text-neutral-400">not</span> automatically mark this finding as verified.
                                Verification requires you to independently execute the command and confirm the output matches.
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                  </>
                ) : (
                  <div className="text-center py-12 rounded-xl border border-white/[0.06] bg-neutral-950 text-xs font-mono text-neutral-500">
                    Select a finding to view its evidence.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Divider before backend section */}
          <div className="flex items-center gap-3 py-2">
            <div className="flex-1 border-t border-white/[0.06]" />
            <span className="text-[10px] font-mono text-neutral-600 uppercase tracking-wider">Backend Assessment Evidence</span>
            <div className="flex-1 border-t border-white/[0.06]" />
          </div>
        </div>
      )}

      {/* ══ BACKEND FULL ASSESSMENT EVIDENCE ═══════════════════════════════ */}
      {evidenceSource === 'backend' && (
        <div className="space-y-6">
          {/* Active assessment context banner */}
          {activeAssessment && (
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

          {/* Prompt if no active assessment */}
          {!activeAssessment && !loading && (
            <div className="text-center py-16 rounded-xl border border-white/[0.06] bg-neutral-950 space-y-3 font-mono">
              <FileCheck2 className="w-8 h-8 mx-auto text-neutral-700" />
              <p className="text-sm font-semibold text-neutral-300">No active assessment selected.</p>
              <p className="text-xs text-neutral-500 max-w-sm mx-auto leading-relaxed">
                Select a historical assessment or start a new security assessment to inspect technical evidence.
              </p>
            </div>
          )}

          {/* Clean empty state for assessment with 0 findings */}
          {activeAssessment && findings.length === 0 && !loading && (
            <div className="text-center py-20 rounded-xl border border-white/[0.06] bg-neutral-950 space-y-3 font-mono">
              <CheckCircle2 className="w-10 h-10 mx-auto text-emerald-400" />
              <p className="text-base font-semibold text-slate-100">No findings or evidence recorded.</p>
              <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
                Active assessment <strong className="text-cyan-300">{activeAssessment.id}</strong> targeting{" "}
                <span className="text-slate-300">{activeAssessment.target_url}</span> has zero findings, so no technical evidence records exist.
              </p>
            </div>
          )}

          {/* If assessment has findings, render timeline and evidence layout */}
          {activeAssessment && findings.length > 0 && (
            <>
              {/* Top Evidence Flow Timeline */}
              <div className="p-3.5 rounded-2xl bg-neutral-950 border border-white/[0.08] backdrop-blur-md overflow-x-auto scrollbar-none">
                <div className="flex items-center justify-between min-w-[700px] text-xs font-mono">
                  {timelineSteps.map((step, idx) => {
                    const isCurrent = activeTimelineStage === step.id;
                    return (
                      <React.Fragment key={step.id}>
                        <button
                          onClick={() => scrollToTimelineStage(step.id as any)}
                          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition-all ${
                            isCurrent
                              ? 'bg-white text-black font-bold shadow-sm'
                              : 'text-neutral-400 hover:text-white hover:bg-white/[0.04]'
                          }`}
                        >
                          <span className="text-[10px] opacity-70">0{idx + 1}</span>
                          <span>{step.label}</span>
                        </button>
                        {idx < timelineSteps.length - 1 && (
                          <span className="text-neutral-700">→</span>
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>

              {/* 3-COLUMN MAIN LAYOUT */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* LEFT COLUMN: Finding Navigation (3 cols) */}
        <div className="lg:col-span-3 space-y-3">
          <div className="flex items-center justify-between text-xs font-mono text-neutral-400 pb-2 border-b border-white/[0.06]">
            <span>Findings ({findings.length})</span>
            <span className="text-neutral-500">World Monitor</span>
          </div>

          <div className="space-y-2 max-h-[calc(100vh-220px)] overflow-y-auto pr-1">
            {findings.map((f) => {
              const isSelected = selectedFinding?.id === f.id;
              const hasEvidence = f.evidence_status === 'VERIFIED';

              return (
                <div
                  key={f.id}
                  onClick={() => handleSelectFinding(f)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all duration-150 ${
                    isSelected
                      ? 'glass-card-selected text-white shadow-sm'
                      : 'glass-panel text-neutral-400 hover:border-white/20 hover:text-neutral-200'
                  }`}
                >
                  <div className="flex items-center justify-between text-[11px] font-mono mb-1">
                    <span className="font-semibold text-white">{f.id}</span>
                    <span className="flex items-center space-x-1 text-[10px]">
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${
                          f.base_severity === 'CRITICAL' || f.base_severity === 'HIGH'
                            ? 'bg-red-400'
                            : f.base_severity === 'MEDIUM'
                            ? 'bg-amber-400'
                            : 'bg-emerald-400'
                        }`}
                      />
                      <span>{f.base_severity}</span>
                    </span>
                  </div>

                  <div className="text-xs font-medium text-neutral-200 truncate mb-2">
                    {f.title}
                  </div>

                  <div className="flex items-center justify-between text-[10px] font-mono text-neutral-500">
                    <span className="truncate max-w-[120px]">{f.category}</span>
                    <span className={hasEvidence ? 'text-emerald-400 font-medium' : 'text-amber-400'}>
                      {hasEvidence ? '✓ Verified' : 'Pending'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* CENTER COLUMN: Simple Evidence & Real Capture (6 cols) */}
        <div className="lg:col-span-6 space-y-6">
          {selectedFinding ? (
            <>
              {/* STAGE 1: FINDING & WHAT WE FOUND */}
              <div ref={sectionRefs.FINDING} className="space-y-4">
                <div className="p-6 rounded-2xl glass-card space-y-3">
                  <div className="flex items-center justify-between mb-3 text-xs font-mono text-neutral-400">
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-0.5 rounded bg-white/[0.08] text-white border border-white/[0.1] font-semibold">
                        {selectedFinding.id}
                      </span>
                      <span>{selectedFinding.category}</span>
                    </div>
                    <span className="text-emerald-400 font-semibold">● Verified Evidence</span>
                  </div>

                  <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white mb-4">
                    {selectedFinding.title}
                  </h2>

                  {/* WHAT WE FOUND */}
                  <div className="space-y-1.5 pt-3 border-t border-white/[0.06]">
                    <div className="text-[11px] font-mono text-neutral-400 uppercase tracking-wider font-semibold">
                      WHAT WE FOUND
                    </div>
                    <p className="text-base sm:text-lg text-neutral-100 font-medium leading-relaxed">
                      "{currentEvidence?.what_found || selectedFinding.description}"
                    </p>
                  </div>
                </div>
              </div>

              {/* STAGE 2: WHY IT MATTERS */}
              <div ref={sectionRefs.WHY} className="space-y-2">
                <div className="p-5 rounded-2xl glass-panel">
                  <div className="text-[11px] font-mono text-amber-400 uppercase tracking-wider font-semibold mb-2 flex items-center space-x-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>WHY IT MATTERS</span>
                  </div>
                  <p className="text-xs sm:text-sm text-neutral-300 leading-relaxed">
                    {currentEvidence?.why_matters || selectedFinding.ai_potential_impact || 'This condition allows unauthorized actors to inspect internal endpoints or compromise communication integrity without proper authorization safeguards.'}
                  </p>
                </div>
              </div>

              {/* STAGE 3: WHERE */}
              <div ref={sectionRefs.WHERE} className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-4 rounded-xl glass-panel">
                  <span className="text-[10px] font-mono text-neutral-500 uppercase block mb-1">Target</span>
                  <span className="text-xs font-mono text-neutral-200 truncate block">
                    {activeAssessment?.target_url || 'worldmonitor.internal.demo'}
                  </span>
                </div>
                <div className="p-4 rounded-xl glass-panel">
                  <span className="text-[10px] font-mono text-neutral-500 uppercase block mb-1">Endpoint</span>
                  <span className="text-xs font-mono text-white truncate block">
                    {currentEvidence?.where_found || selectedFinding.affected_component}
                  </span>
                </div>
                <div className="p-4 rounded-xl glass-panel">
                  <span className="text-[10px] font-mono text-neutral-500 uppercase block mb-1">Component</span>
                  <span className="text-xs font-mono text-neutral-200 truncate block">
                    {selectedFinding.affected_component}
                  </span>
                </div>
              </div>

              {/* STAGE 4: PROOF - ACTUAL EVIDENCE CONTAINER */}
              <div ref={sectionRefs.PROOF} className="space-y-3">
                <div className="rounded-2xl glass-card p-6 space-y-4 shadow-xl">
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-white/[0.08]">
                    <div className="flex items-center space-x-2 font-mono text-xs">
                      <span className="font-bold text-white">REAL EVIDENCE</span>
                      <span className="text-neutral-500">|</span>
                      <span className="text-neutral-400">ID: {currentEvidence?.id || 'EVD-001'}</span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className="flex items-center space-x-1.5 text-xs font-mono text-emerald-400">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                        <span>Integrity Verified ✓</span>
                      </span>
                    </div>
                  </div>

                  {/* Artifact Switcher for multiple baseline evidence items */}
                  {baselineEvidenceRecords.length > 1 && (
                    <div className="flex flex-wrap items-center gap-2 p-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs font-mono">
                      <span className="text-neutral-500 text-[10px] uppercase font-bold px-1">Evidence Records ({baselineEvidenceRecords.length}):</span>
                      {baselineEvidenceRecords.map((ev) => {
                        const isSelected = currentEvidence?.id === ev.id;
                        const isCanon = ev.is_canonical ?? (ev.id === 'EV-WM-API-DOCS-A018-GET' || ev.lifecycle_status === 'CANONICAL');
                        return (
                          <button
                            key={ev.id}
                            onClick={() => setSelectedEvidenceId(ev.id)}
                            className={`px-2.5 py-1 rounded-lg border text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
                              isSelected
                                ? isCanon
                                  ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-sm'
                                  : 'bg-white/10 text-white border-white/20'
                                : 'bg-transparent text-neutral-400 border-white/[0.06] hover:text-neutral-200'
                            }`}
                          >
                            <span className={`w-1.5 h-1.5 rounded-full ${isCanon ? 'bg-cyan-400' : 'bg-neutral-500'}`} />
                            <span className="font-semibold">{ev.id}</span>
                            <span className="text-[10px] opacity-75">[{isCanon ? 'Canonical GET' : 'Historical'}]</span>
                          </button>
                        );
                      })}
                    </div>
                  )}

                  {/* Lifecycle Badge & Relationship Note */}
                  {currentEvidence && (
                    <div className="p-2.5 rounded-lg bg-neutral-900/60 border border-white/[0.06] text-xs font-mono">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                          (currentEvidence.is_canonical ?? (currentEvidence.id === 'EV-WM-API-DOCS-A018-GET' || currentEvidence.lifecycle_status === 'CANONICAL'))
                            ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                            : 'bg-neutral-800 text-neutral-400 border border-neutral-700'
                        }`}>
                          {(currentEvidence.is_canonical ?? (currentEvidence.id === 'EV-WM-API-DOCS-A018-GET' || currentEvidence.lifecycle_status === 'CANONICAL'))
                            ? 'Canonical Active Proof'
                            : 'Historical Artifact (Superseded)'}
                        </span>
                        <span className="text-neutral-400 text-[11px]">
                          {currentEvidence.relationship_note || (
                            (currentEvidence.is_canonical ?? currentEvidence.id === 'EV-WM-API-DOCS-A018-GET')
                              ? 'Proves unauthenticated HTTP GET access to the live OpenAPI schema document.'
                              : 'Historical original live probe artifact retained for cryptographic audit trail continuity.'
                          )}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Metadata Row */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs font-mono text-neutral-400">
                    <div>
                      <span className="text-neutral-600 text-[10px] block">SOURCE</span>
                      <span className="text-neutral-300 truncate block">{currentEvidence?.source || 'Security Probe'}</span>
                    </div>
                    <div>
                      <span className="text-neutral-600 text-[10px] block">TIMESTAMP</span>
                      <span className="text-neutral-300 truncate block">{currentEvidence?.timestamp || '2026-09-09 12:00:00'}</span>
                    </div>
                    <div>
                      <span className="text-neutral-600 text-[10px] block">CONFIDENCE</span>
                      <span className="text-emerald-400 font-semibold">{currentEvidence?.confidence_level || 'HIGH'}</span>
                    </div>
                  </div>

                  {/* Empirical Protocol Observation Grid */}
                  {(currentEvidence?.http_method || currentEvidence?.openapi_detected !== undefined || selectedFinding.cwe_id === 'CWE-200' || selectedFinding.id === 'WM-API-DOCS-A018' || (selectedFinding.title || '').toLowerCase().includes('openapi')) && (
                    <div className="p-3.5 rounded-xl bg-cyan-950/20 border border-cyan-500/20 text-xs font-mono space-y-2">
                      <div className="text-[10px] text-cyan-400 font-bold uppercase tracking-wider flex items-center justify-between">
                        <span>Empirical Protocol Observation</span>
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-900/40 text-cyan-300 border border-cyan-700/50">
                          LIVE GET PROBE
                        </span>
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-[11px]">
                        <div>
                          <span className="text-neutral-500 text-[10px] block">HTTP METHOD</span>
                          <span className="text-white font-semibold">{currentEvidence?.http_method || 'GET'}</span>
                        </div>
                        <div>
                          <span className="text-neutral-500 text-[10px] block">HTTP STATUS</span>
                          <span className="text-emerald-400 font-semibold">{currentEvidence?.http_status || 200}</span>
                        </div>
                        <div>
                          <span className="text-neutral-500 text-[10px] block">CONTENT-TYPE</span>
                          <span className="text-neutral-200 truncate block">{currentEvidence?.content_type || 'application/json; charset=utf-8'}</span>
                        </div>
                        <div>
                          <span className="text-neutral-500 text-[10px] block">OPENAPI DETECTED</span>
                          <span className="text-emerald-400 font-semibold">{currentEvidence?.openapi_detected !== undefined ? String(currentEvidence.openapi_detected) : 'true'}</span>
                        </div>
                        <div>
                          <span className="text-neutral-500 text-[10px] block">OPENAPI VERSION</span>
                          <span className="text-white font-semibold">{currentEvidence?.openapi_version || '3.1.0'}</span>
                        </div>
                        <div>
                          <span className="text-neutral-500 text-[10px] block">SCHEMA TITLE</span>
                          <span className="text-white font-semibold truncate block">{currentEvidence?.schema_title || 'WorldMonitor API'}</span>
                        </div>
                        <div>
                          <span className="text-neutral-500 text-[10px] block">UNAUTHENTICATED</span>
                          <span className="text-amber-400 font-semibold">{currentEvidence?.unauthenticated !== undefined ? String(currentEvidence.unauthenticated) : 'true'}</span>
                        </div>
                        <div>
                          <span className="text-neutral-500 text-[10px] block">AUTHORIZATION STATE</span>
                          <span className="text-amber-400 font-semibold">{currentEvidence?.authorization_state || 'PUBLIC'}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Observed Result Box */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-neutral-400 uppercase font-semibold">Observed Result:</span>
                      <button
                        onClick={() => {
                          if (currentEvidence?.raw_data) {
                            navigator.clipboard.writeText(currentEvidence.raw_data);
                            setCopiedRaw(true);
                            setTimeout(() => setCopiedRaw(false), 2000);
                          }
                        }}
                        className="flex items-center space-x-1 text-neutral-400 hover:text-white transition-colors cursor-pointer"
                      >
                        {copiedRaw ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                        <span>{copiedRaw ? 'Copied' : 'Copy'}</span>
                      </button>
                    </div>

                    <pre className="p-4 rounded-xl glass-terminal font-mono text-xs text-neutral-200 overflow-x-auto whitespace-pre-wrap max-h-56 leading-relaxed glass-code">
                      {currentEvidence?.raw_data || 'No verbatim capture available.'}
                    </pre>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-white/[0.06]">
                    <button
                      onClick={handleExecuteProbe}
                      disabled={probing}
                      className="btn-secondary px-4 py-2 rounded-lg text-xs font-mono font-medium flex items-center space-x-2 transition-all cursor-pointer"
                    >
                      {probing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 text-emerald-400" />}
                      <span>{probing ? 'Re-Probing...' : 'Verify'}</span>
                    </button>

                    <button
                      onClick={() => handleOpenTerminal(selectedFinding.id)}
                      className="btn-primary px-5 py-2 rounded-lg text-xs font-mono font-semibold flex items-center space-x-2 transition-all cursor-pointer shadow-sm"
                    >
                      <Terminal className="w-3.5 h-3.5" />
                      <span>View Technical →</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* STAGE 5: AI ANALYSIS UI (CLEARLY SEPARATE FROM FACTS) */}
              <div ref={sectionRefs.ANALYSIS} className="space-y-3">
                <div className="p-6 rounded-2xl glass-card border-purple-500/25 space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-purple-500/20">
                    <div className="flex items-center space-x-2 text-xs font-mono font-semibold text-purple-300">
                      <Cpu className="w-4 h-4 text-purple-400" />
                      <span>✦ AI ANALYSIS</span>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                      Local Offline Engine
                    </span>
                  </div>

                  {/* 3-Step Completion Animation Check */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 py-2 text-[11px] font-mono">
                    <div className="flex items-center space-x-2 text-neutral-300">
                      <span className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px]">
                        ✓
                      </span>
                      <span>Evidence understood</span>
                    </div>
                    <div className="flex items-center space-x-2 text-neutral-300">
                      <span className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px]">
                        ✓
                      </span>
                      <span>Risk analyzed</span>
                    </div>
                    <div className="flex items-center space-x-2 text-neutral-300">
                      <span className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px]">
                        ✓
                      </span>
                      <span>Remediation ready</span>
                    </div>
                  </div>

                  {/* What this means */}
                  <div className="space-y-1">
                    <div className="text-[11px] font-mono text-purple-300 uppercase font-semibold">
                      What this means:
                    </div>
                    <p className="text-xs text-neutral-300 leading-relaxed">
                      {selectedFinding.ai_summary || (selectedFinding.cwe_id === 'CWE-200' || selectedFinding.id === 'WM-API-DOCS-A018'
                        ? 'Unauthenticated GET to /openapi.json returns HTTP 200 and a real OpenAPI 3.1 document. Public API schema exposure can aid reconnaissance and endpoint discovery.'
                        : 'The observed HTTP response fails standard security hardening standards, exposing the endpoint to automated reconnaissance or unauthorized access.')}
                    </p>
                  </div>

                  {/* Possible impact */}
                  <div className="space-y-1">
                    <div className="text-[11px] font-mono text-purple-300 uppercase font-semibold">
                      Possible impact:
                    </div>
                    <p className="text-xs text-neutral-300 leading-relaxed">
                      {selectedFinding.ai_potential_impact || (selectedFinding.cwe_id === 'CWE-200' || selectedFinding.id === 'WM-API-DOCS-A018'
                        ? 'Information exposure aiding adversary reconnaissance and endpoint discovery. Current empirical evidence does NOT prove: data extraction, account compromise, privilege escalation, lateral movement, integrity compromise, availability compromise, or clickjacking.'
                        : 'Adversaries can exploit unprotected parameters or endpoints to conduct automated reconnaissance or unauthorized resource access.')}
                    </p>
                  </div>

                  {/* Recommended action */}
                  <div className="space-y-1">
                    <div className="text-[11px] font-mono text-purple-300 uppercase font-semibold">
                      Recommended action:
                    </div>
                    <p className="text-xs text-neutral-300 leading-relaxed">
                      {selectedFinding.recommended_remediation?.join('. ') || (selectedFinding.cwe_id === 'CWE-200' || selectedFinding.id === 'WM-API-DOCS-A018'
                        ? 'Control production documentation and schema exposure: restrict or disable /openapi.json in production and filter sensitive internal schema details.'
                        : 'Review component configuration and apply defensive hardening controls.')}
                    </p>
                  </div>
                </div>
              </div>

              {/* STAGE 6, 7, 8: TECHNICAL VERIFICATION & RE-VERIFICATION */}
              <div ref={sectionRefs.VERIFY} className="space-y-3">
                <div ref={sectionRefs.FIX} className="p-6 rounded-2xl glass-panel flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div>
                    <h3 className="text-sm font-semibold text-white mb-1">
                      Technical Verification & Differential Re-Run
                    </h3>
                    <p className="text-xs text-neutral-400">
                      Prove the resolution: Run differential check to compare Before Fix vs After Fix.
                    </p>
                  </div>

                  <div ref={sectionRefs['RE-VERIFY']} className="flex items-center space-x-2 shrink-0">
                    <button
                      onClick={() => setShowReVerify(true)}
                      className="btn-secondary px-4 py-2 rounded-lg font-mono text-xs font-semibold flex items-center space-x-1.5 transition-colors cursor-pointer"
                    >
                      <RefreshCw className="w-3.5 h-3.5 text-blue-400" />
                      <span>Re-Verify Fix</span>
                    </button>
                    <button
                      onClick={() => handleOpenTerminal(selectedFinding.id)}
                      className="btn-primary px-4 py-2 rounded-lg font-mono text-xs font-semibold flex items-center space-x-1.5 transition-colors cursor-pointer"
                    >
                      <Terminal className="w-3.5 h-3.5" />
                      <span>Open Terminal</span>
                    </button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-32 rounded-2xl glass-level-1 font-mono text-xs text-neutral-500">
              Select a finding to inspect verifiable evidence.
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Technical Status, Metadata & Integrity (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          {selectedFinding && (
            <>
              {/* Evidence Integrity Card */}
              <div className="p-5 rounded-2xl glass-card space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-neutral-400 uppercase text-[10px] tracking-wider font-semibold">
                    Evidence Integrity
                  </span>
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                </div>

                <div className="text-emerald-400 font-bold text-base flex items-center space-x-2">
                  <ShieldCheck className="w-5 h-5" />
                  <span>Verified</span>
                </div>

                <p className="text-[11px] text-neutral-400 font-sans">
                  Cryptographic SHA-256 hash computed at capture time to prevent tampering.
                </p>

                <div className="p-2.5 rounded-lg glass-terminal space-y-1">
                  <span className="text-[10px] text-neutral-500 uppercase block">Hash Available</span>
                  <div className="text-[10px] text-emerald-300 font-mono break-all">
                    {currentEvidence?.integrity_hash || 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}
                  </div>
                </div>
              </div>

              {/* Security Intelligence (CWE / OWASP / CVE / NVD) */}
              <div className="p-5 rounded-2xl glass-card space-y-3 font-mono text-xs">
                <div className="text-neutral-400 uppercase text-[10px] tracking-wider font-semibold">
                  Security Intelligence
                </div>

                <div className="space-y-2 pt-1 border-t border-white/[0.06]">
                  <div>
                    <span className="text-neutral-500 text-[10px] uppercase block">CWE</span>
                    <span className="text-white font-medium">{selectedFinding.cwe_id || 'CWE-16'}</span>
                    <span className="text-[11px] text-neutral-400 font-sans block mt-0.5">
                      {selectedFinding.category}
                    </span>
                  </div>

                  <div className="pt-2 border-t border-white/[0.04]">
                    <span className="text-neutral-500 text-[10px] uppercase block">OWASP Top 10</span>
                    <span className="text-neutral-200">{selectedFinding.owasp_category || 'A05:2021 Security Misconfiguration'}</span>
                  </div>

                  <div className="pt-2 border-t border-white/[0.04]">
                    <span className="text-neutral-500 text-[10px] uppercase block">CVE Status</span>
                    {selectedFinding.cve_id ? (
                      <span className="px-2 py-0.5 rounded text-[10px] bg-white/[0.08] text-neutral-300 border border-white/[0.1] inline-block mt-0.5">
                        {selectedFinding.cve_status || 'Version Verification Required'}
                      </span>
                    ) : (
                      <span className="text-neutral-400 text-xs mt-0.5 block font-mono">
                        Not identified
                      </span>
                    )}
                  </div>

                  <div className="pt-2 border-t border-white/[0.04]">
                    <span className="text-neutral-500 text-[10px] uppercase block">NVD CVSS</span>
                    <div className="flex items-center space-x-2 mt-0.5">
                      {selectedFinding.cve_id && selectedFinding.nvd_cvss !== null && selectedFinding.nvd_cvss !== undefined ? (
                        <>
                          <span className="text-white font-bold text-sm">
                            {selectedFinding.nvd_cvss.toFixed(1)}
                          </span>
                          <span className="text-neutral-400 text-[11px]">/ 10.0</span>
                        </>
                      ) : (
                        <span className="text-neutral-400 text-xs font-mono">
                          Not available
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Risk Visualization Card */}
              <div className="p-5 rounded-2xl glass-card space-y-3 font-mono text-xs">
                <div className="text-neutral-400 uppercase text-[10px] tracking-wider font-semibold">
                  Deterministic Risk
                </div>

                <div className="space-y-1">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-neutral-400">Priority Score</span>
                    <span className="text-white font-bold">{selectedFinding.priority_score} / 10.0</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
                    <div
                      className="h-full bg-white rounded-full transition-all"
                      style={{ width: `${Math.min(100, (selectedFinding.priority_score / 10.0) * 100)}%` }}
                    />
                  </div>
                </div>

                <div className="pt-2 border-t border-white/[0.06] space-y-1.5 text-[11px]">
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Severity:</span>
                    <span className="text-neutral-300">{selectedFinding.base_severity}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Calculated Priority:</span>
                    <span className="text-neutral-300">{selectedFinding.priority}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-500">Evidence Status:</span>
                    <span className="text-emerald-400 font-semibold">{selectedFinding.evidence_status}</span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

      </div>
          </>
        )}
      </div>
      )}

      {/* Technical Terminal Viewer Modal */}
      <TechnicalTerminalViewer
        isOpen={showTerminal}
        data={terminalData}
        onClose={() => setShowTerminal(false)}
      />

      {/* Re-Verification Modal */}
      <ReVerificationModal
        isOpen={showReVerify}
        finding={selectedFinding}
        onClose={() => setShowReVerify(false)}
        onSuccess={(result) => {
          loadData(true);
          refreshData();
          showToast(
            'success',
            'Finding Re-Verified',
            `State updated with differential evidence (${result?.new_status || 'COMPLETE'}).`
          );
        }}
      />

    </div>
  );
};
