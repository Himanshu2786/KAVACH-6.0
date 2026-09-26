import React, { useState, useEffect, useRef } from 'react';
import {
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  X,
  Shield,
  ArrowRight,
  ShieldAlert,
  ShieldCheck,
  FileCheck2,
  Terminal,
  Activity,
  GitCompare,
  HelpCircle,
  Check
} from 'lucide-react';
import { Finding, ReVerificationRecord, EvidenceRecord } from '../../types';
import { api } from '../../services/api';
import { formatToIST } from '../../utils/time';

interface ReVerificationModalProps {
  isOpen: boolean;
  finding: Finding | null;
  onClose: () => void;
  onSuccess?: (result?: ReVerificationRecord) => void;
}

export const ReVerificationModal: React.FC<ReVerificationModalProps> = ({
  isOpen,
  finding,
  onClose,
  onSuccess
}) => {
  const [running, setRunning] = useState(false);
  const [reResult, setReResult] = useState<ReVerificationRecord | null>(null);
  const [beforeEvidence, setBeforeEvidence] = useState<EvidenceRecord | null>(null);
  const [parsedDiff, setParsedDiff] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Track finding ID and open state to prevent wiping reResult on parent data refresh
  const activeFindingIdRef = useRef<string | null>(null);
  const prevIsOpenRef = useRef<boolean>(false);

  useEffect(() => {
    const justOpened = isOpen && !prevIsOpenRef.current;
    const findingChanged = isOpen && Boolean(finding && finding.id !== activeFindingIdRef.current);

    prevIsOpenRef.current = isOpen;

    if (!isOpen) {
      activeFindingIdRef.current = null;
      return;
    }

    if (justOpened || findingChanged) {
      if (finding) {
        activeFindingIdRef.current = finding.id;
        setReResult(null);
        setParsedDiff(null);
        setErrorMsg(null);
        // Fetch latest before evidence record
        api.getEvidence(finding.id)
          .then((records: EvidenceRecord[]) => {
            if (records && records.length > 0) {
              setBeforeEvidence(records[0]);
            } else {
              setBeforeEvidence(null);
            }
          })
          .catch(() => setBeforeEvidence(null));
      }
    }
  }, [isOpen, finding?.id]);

  if (!isOpen || !finding) return null;

  const handleRunReverification = async () => {
    if (!finding) return;
    setRunning(true);
    setErrorMsg(null);
    try {
      // Execute genuine empirical re-test probe without simulation overrides
      const res = await api.reVerifyFinding(finding.id);
      setReResult(res);
      if (res.state_diff) {
        try {
          setParsedDiff(JSON.parse(res.state_diff));
        } catch {
          setParsedDiff(null);
        }
      }
      if (onSuccess) {
        onSuccess(res);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Empirical re-verification probe encountered an error.');
    } finally {
      setRunning(false);
    }
  };

  const isVerified = reResult?.new_status === 'VERIFIED_REMEDIATED' || reResult?.new_status === 'RESOLVED';
  const isStillOpen = reResult?.new_status === 'STILL_OPEN' || reResult?.new_status === 'STILL OBSERVED';
  const isUnable = reResult?.new_status === 'UNABLE_TO_VERIFY';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl max-h-[92vh] flex flex-col rounded-2xl glass-level-4 border border-white/[0.15] shadow-2xl overflow-hidden font-mono text-xs">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/[0.08] bg-white/[0.03]">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-white/[0.06] border border-white/[0.1] text-white backdrop-blur-md">
              <RefreshCw className={`w-4 h-4 text-cyan-400 ${running ? 'animate-spin' : ''}`} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-white tracking-tight uppercase">EMPIRICAL RE-TEST & RE-VERIFICATION</h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  SIH PS 26163
                </span>
              </div>
              <p className="text-[11px] text-neutral-400 font-sans">
                Deterministic security probe verifying whether vulnerability condition was resolved.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-white/[0.08] transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          
          {/* Finding Context & Target Card */}
          <div className="p-4 rounded-xl glass-level-2 border border-white/[0.08] grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2 space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-neutral-500 uppercase font-mono">Finding {finding.id}</span>
                <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 uppercase">
                  {finding.base_severity}
                </span>
                <span className="text-[10px] text-neutral-400 font-sans">{finding.category}</span>
              </div>
              <h4 className="text-sm font-bold text-white font-sans">{finding.title}</h4>
              <p className="text-neutral-400 text-xs font-sans leading-relaxed">
                {finding.description}
              </p>
            </div>

            <div className="p-3 rounded-lg bg-black/40 border border-white/[0.06] space-y-1.5 text-[11px]">
              <div>
                <span className="text-[10px] text-neutral-500 uppercase block">Target Component:</span>
                <span className="text-cyan-300 font-semibold break-all font-mono block" title={finding.affected_component}>{finding.affected_component}</span>
              </div>
              <div>
                <span className="text-[10px] text-neutral-500 uppercase block">Current Baseline:</span>
                <span className="text-neutral-200 font-bold">{finding.status}</span>
              </div>
              <div>
                <span className="text-[10px] text-neutral-500 uppercase block">Knowledge Ref:</span>
                <span className="text-neutral-400">{finding.cwe_id || finding.owasp_category || 'CWE-Mapped'}</span>
              </div>
            </div>
          </div>

          {/* Remediation Plan Summary */}
          {finding.recommended_remediation && (
            <div className="p-3.5 rounded-xl bg-cyan-950/20 border border-cyan-500/20 text-xs font-sans space-y-1">
              <div className="text-[10px] font-mono uppercase font-bold text-cyan-400 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5" />
                Required Defensive Remediation:
              </div>
              <p className="text-neutral-300 text-[11px] leading-relaxed">
                {Array.isArray(finding.recommended_remediation)
                  ? finding.recommended_remediation.join(' • ')
                  : finding.recommended_remediation}
              </p>
            </div>
          )}

          {errorMsg && (
            <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-300 font-mono text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Re-Verification Results (Before vs After Evidence) */}
          {reResult ? (
            <div className="space-y-4 animate-in fade-in duration-300">
              
              {/* Verdict Banner */}
              <div className={`flex items-center justify-between p-4 rounded-xl border ${
                isVerified
                  ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300 shadow-[0_0_15px_rgba(16,185,129,0.15)]'
                  : isStillOpen
                  ? 'bg-rose-950/40 border-rose-500/40 text-rose-300 shadow-[0_0_15px_rgba(244,63,94,0.15)]'
                  : 'bg-amber-950/40 border-amber-500/40 text-amber-300'
              }`}>
                <div className="flex items-center space-x-3">
                  {isVerified ? (
                    <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
                  ) : isStillOpen ? (
                    <ShieldAlert className="w-6 h-6 text-rose-400 shrink-0" />
                  ) : (
                    <AlertCircle className="w-6 h-6 text-amber-400 shrink-0" />
                  )}
                  <div>
                    <div className="text-xs font-bold font-mono uppercase tracking-wider">
                      VERIFICATION VERDICT: {reResult.new_status}
                    </div>
                    <div className="text-[11px] font-sans text-neutral-300 mt-0.5">
                      {isVerified
                        ? 'Deterministic security check confirmed: The vulnerability has been successfully remediated.'
                        : isStillOpen
                        ? 'Vulnerability is still open: The requested defensive control remains absent upon live target re-test.'
                        : 'Re-test could not reach the target endpoint or host.'}
                    </div>
                  </div>
                </div>
                <div className="text-right text-[10px] font-mono text-neutral-400 hidden sm:block">
                  <div>RECORD ID: {reResult.id}</div>
                  <div>TIMESTAMP: {formatToIST(reResult.timestamp)}</div>
                </div>
              </div>

              {/* Side-by-Side Evidence Comparison Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* BEFORE EVIDENCE */}
                <div className="rounded-xl border border-rose-500/25 bg-black/50 p-4 flex flex-col space-y-2">
                  <div className="flex items-center justify-between border-b border-white/[0.06] pb-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-rose-400" />
                      BEFORE EVIDENCE (BASELINE)
                    </span>
                    <span className="text-[9px] text-neutral-500 font-mono">
                      {reResult.before_evidence_id || beforeEvidence?.id || 'BASELINE'}
                    </span>
                  </div>
                  
                  <div className="text-[10px] text-neutral-400 font-mono">
                    <span className="text-neutral-500">SHA-256 HASH:</span>{' '}
                    <span className="text-rose-300 break-all font-mono">
                      {reResult.before_evidence_hash || beforeEvidence?.integrity_hash || 'SHA-256-BASELINE'}
                    </span>
                  </div>

                  <div className="text-[10px] text-neutral-400 font-mono">
                    <span className="text-neutral-500">PROBE COMMAND:</span>{' '}
                    <span className="text-neutral-200">{reResult.command_executed}</span>
                  </div>

                  <div className="flex-1 rounded-lg bg-black/60 border border-white/[0.04] p-2.5 overflow-x-auto">
                    <pre className="text-neutral-300 font-mono text-[10px] whitespace-pre-wrap leading-relaxed max-h-44">
                      {reResult.output_before || beforeEvidence?.what_found || beforeEvidence?.raw_data || 'Baseline observation recorded.'}
                    </pre>
                  </div>
                </div>

                {/* AFTER EVIDENCE */}
                <div className={`rounded-xl border p-4 flex flex-col space-y-2 ${
                  isVerified
                    ? 'border-emerald-500/30 bg-emerald-950/10'
                    : 'border-rose-500/25 bg-black/50'
                }`}>
                  <div className="flex items-center justify-between border-b border-white/[0.06] pb-2">
                    <span className={`text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5 ${
                      isVerified ? 'text-emerald-400' : 'text-rose-400'
                    }`}>
                      <span className={`w-2 h-2 rounded-full ${isVerified ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                      AFTER EVIDENCE (RE-TEST RESULT)
                    </span>
                    <span className="text-[9px] text-neutral-500 font-mono">
                      {reResult.after_evidence_id || 'NEW EVIDENCE RECORD'}
                    </span>
                  </div>

                  <div className="text-[10px] text-neutral-400 font-mono">
                    <span className="text-neutral-500">SHA-256 HASH:</span>{' '}
                    <span className={`break-all font-mono ${isVerified ? 'text-emerald-300' : 'text-rose-300'}`}>
                      {reResult.after_evidence_hash || 'SHA-256-CALCULATED'}
                    </span>
                  </div>

                  <div className="text-[10px] text-neutral-400 font-mono">
                    <span className="text-neutral-500">RE-TEST COMMAND:</span>{' '}
                    <span className="text-neutral-200">{reResult.command_executed}</span>
                  </div>

                  <div className="flex-1 rounded-lg bg-black/60 border border-white/[0.04] p-2.5 overflow-x-auto">
                    <pre className={`font-mono text-[10px] whitespace-pre-wrap leading-relaxed max-h-44 ${
                      isVerified ? 'text-emerald-300' : 'text-rose-300'
                    }`}>
                      {reResult.output_after}
                    </pre>
                  </div>
                </div>

              </div>

              {/* Deterministic State Diff Card */}
              {parsedDiff && (
                <div className="p-4 rounded-xl glass-level-2 border border-white/[0.08] space-y-2 font-mono text-xs">
                  <div className="text-[10px] font-bold uppercase text-neutral-400 flex items-center gap-1.5">
                    <GitCompare className="w-3.5 h-3.5 text-cyan-400" />
                    DETERMINISTIC STATE DIFF & AUDIT VALIDATION:
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px]">
                    <div className="p-2 rounded bg-black/40 border border-white/[0.04]">
                      <span className="text-[10px] text-neutral-500 block">Condition Improved:</span>
                      <span className={parsedDiff.security_improved ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                        {parsedDiff.security_improved ? 'YES (TRUE)' : 'NO (FALSE)'}
                      </span>
                    </div>
                    <div className="p-2 rounded bg-black/40 border border-white/[0.04]">
                      <span className="text-[10px] text-neutral-500 block">Change Detected:</span>
                      <span className="text-neutral-200 font-bold">
                        {parsedDiff.change_detected ? 'YES' : 'NO CHANGE'}
                      </span>
                    </div>
                    <div className="p-2 rounded bg-black/40 border border-white/[0.04]">
                      <span className="text-[10px] text-neutral-500 block">Final Status:</span>
                      <span className="text-cyan-300 font-bold">{reResult.new_status}</span>
                    </div>
                  </div>
                  <p className="text-neutral-300 font-sans text-xs pt-1 border-t border-white/[0.04]">
                    {parsedDiff.verdict_reason || reResult.summary}
                  </p>
                </div>
              )}

            </div>
          ) : (
            /* Pre-Execution Readiness State */
            <div className="p-8 rounded-xl border border-white/[0.08] glass-panel text-center space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mx-auto">
                <Terminal className="w-6 h-6" />
              </div>
              <div className="max-w-md mx-auto space-y-1">
                <h4 className="text-sm font-bold text-white font-sans">Ready to Execute Empirical Re-Test</h4>
                <p className="text-neutral-400 text-xs font-sans leading-relaxed">
                  KAVACH will execute a live, non-destructive diagnostic check against <strong className="text-cyan-300">{finding.affected_component}</strong>, capture post-fix evidence, compute SHA-256 hashes, compare before vs after observations, and record immutable audit events.
                </p>
              </div>
            </div>
          )}

        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-white/[0.08] bg-white/[0.02] flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary px-4 py-2 text-xs justify-center cursor-pointer"
          >
            {reResult ? 'Close Dossier' : 'Cancel'}
          </button>

          <button
            type="button"
            onClick={handleRunReverification}
            disabled={running}
            className="btn-primary px-6 py-2.5 text-xs font-bold tracking-wider uppercase flex items-center justify-center space-x-2 cursor-pointer shadow-[0_0_15px_rgba(255,255,255,0.15)]"
          >
            <RefreshCw className={`w-3.5 h-3.5 flex-shrink-0 ${running ? 'animate-spin' : ''}`} />
            <span>{running ? 'Executing Live Re-Test...' : reResult ? 'Re-Run Re-Test Probe' : errorMsg ? 'Retry Real Re-Test' : 'Execute Real Re-Test'}</span>
          </button>
        </div>

      </div>
    </div>
  );
};

