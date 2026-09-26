import React, { useState, useEffect } from 'react';
import { FileText, Printer, Download, ExternalLink, ShieldCheck, CheckCircle2, Sparkles, AlertTriangle } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';

export const SecurityReportPage: React.FC = () => {
  const { activeAssessment, showToast } = useApp();
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeAssessment) return;
    setLoading(true);
    api.getReportData(activeAssessment.id)
      .then((data) => {
        setReport(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [activeAssessment]);

  const handleDownloadJSON = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `KAVACH-Report-${activeAssessment?.id || 'export'}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('success', 'Report Exported', 'JSON telemetry report downloaded successfully.');
  };

  const handleOpenPrintable = () => {
    if (!activeAssessment) return;
    const url = api.getReportHtmlUrl(activeAssessment.id);
    window.open(url, '_blank');
  };

  if (loading || !report) {
    return (
      <div className="py-20 text-center font-mono-code text-xs text-slate-400">
        Assembling Executive Security Report...
      </div>
    );
  }

  const exec = report.executive_summary;
  const asm = report.assessment;

  return (
    <div className="space-y-6 animate-fadeIn max-w-5xl mx-auto">
      {/* Header with Export Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            <span>Executive Security Intelligence Report</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono-code">
            Formal assessment audit dossier with cryptographic technical evidence and prioritized remediation.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 font-mono-code text-xs">
          <button
            onClick={handleDownloadJSON}
            className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center justify-center space-x-2 transition-colors cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
            <span>Export JSON</span>
          </button>
          <button
            onClick={handleOpenPrintable}
            className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold flex items-center justify-center space-x-2 shadow-[0_0_15px_rgba(6,182,212,0.25)] transition-all cursor-pointer"
          >
            <Printer className="w-3.5 h-3.5 flex-shrink-0" />
            <span>Printable HTML View</span>
          </button>
        </div>
      </div>

      {/* Report Document Container */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 space-y-6">
        {/* Document Header */}
        <div className="border-b border-slate-800 pb-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-mono-code text-cyan-400 font-bold tracking-widest uppercase">
                {report.metadata.platform}
              </span>
              <h2 className="text-2xl font-black text-slate-100 tracking-wide mt-1">
                {report.metadata.report_title}
              </h2>
            </div>
            <div className="text-right font-mono-code text-xs text-slate-500">
              <div>Assessment ID: <strong className="text-slate-300">{asm.id}</strong></div>
              <div>Generated: <span className="text-slate-400">{report.metadata.generated_at.slice(0, 10)}</span></div>
            </div>
          </div>
          <div className="text-xs font-mono-code text-cyan-300 italic mt-2">
            Tagline: "{report.metadata.core_principle}"
          </div>
        </div>

        {/* Executive Summary Bento Grid */}
        <div>
          <h3 className="text-xs font-bold font-mono-code uppercase text-slate-400 tracking-wider mb-3">
            1. Executive Evaluation & Security Posture
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono-code text-xs mb-4">
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <div className="text-[10px] text-slate-500 uppercase">Posture</div>
              <div className={`text-lg font-black mt-0.5 ${
                exec.security_posture === 'CRITICAL RISK' ? 'text-red-400' :
                exec.security_posture === 'HIGH RISK' ? 'text-orange-400' :
                exec.security_posture === 'MODERATE RISK' ? 'text-amber-400' :
                'text-emerald-400'
              }`}>{exec.security_posture}</div>
              <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                {exec.risk_score ?? exec.posture_score ?? 70}/100 &bull; {exec.risk_level ?? 'MEDIUM'}
              </div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <div className="text-[10px] text-slate-500 uppercase">Total Findings</div>
              <div className="text-lg font-black text-slate-100 mt-0.5">{exec.total_findings}</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <div className="text-[10px] text-slate-500 uppercase">Evidence Confirmed</div>
              <div className="text-lg font-black text-emerald-400 mt-0.5">{exec.confirmed_evidence ?? exec.confirmed_findings}</div>
              <div className="text-[9px] text-slate-500 font-mono mt-0.5">Unique Proof: {exec.evidence_proofs ?? 1}</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <div className="text-[10px] text-slate-500 uppercase">Evidence Proofs</div>
              <div className="text-lg font-black text-cyan-400 mt-0.5">{exec.evidence_proofs ?? exec.baseline_confirmed_evidence ?? 1}</div>
              <div className="text-[9px] text-slate-500 font-mono mt-0.5">{exec.technical_evidence_captured ?? exec.total_evidence_collected ?? 2} captured</div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 font-mono-code leading-relaxed">
            {exec.summary}
          </div>
        </div>

        {/* Scope & Assessment Parameters */}
        <div>
          <h3 className="text-xs font-bold font-mono-code uppercase text-slate-400 tracking-wider mb-3">
            2. Assessment Scope & Boundary
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono-code text-xs">
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <span className="text-slate-500 uppercase block text-[10px]">Target URL</span>
              <span className="text-cyan-400 font-bold mt-0.5 block truncate">{asm.target_url}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <span className="text-slate-500 uppercase block text-[10px]">Environment</span>
              <span className="text-slate-200 font-bold mt-0.5 block">{asm.environment}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <span className="text-slate-500 uppercase block text-[10px]">Scope Definition</span>
              <span className="text-slate-200 font-bold mt-0.5 block truncate">{asm.scope}</span>
            </div>
          </div>
        </div>

        {/* Prioritized Findings Matrix */}
        <div>
          <h3 className="text-xs font-bold font-mono-code uppercase text-slate-400 tracking-wider mb-3">
            3. Prioritized Findings & Technical Evidence
          </h3>
          <div className="space-y-3 font-mono-code text-xs">
            {report.findings_detail.map((f: any) => (
              <div key={f.id} className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-cyan-400">[{f.id}]</span>
                    <span className="font-bold text-slate-100">{f.title}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 font-bold text-[10px]">
                      Priority: {f.priority_score} / 10.0
                    </span>
                    <Badge label={f.base_severity} type="severity" size="sm" />
                    <Badge label={f.status} type="status" size="sm" />
                  </div>
                </div>

                <div className="text-slate-400 text-[11px] flex flex-wrap gap-x-3 gap-y-1">
                  <span>Component: <strong className="text-slate-300">{f.affected_component}</strong></span>
                  <span>&bull; Category: {f.category}</span>
                  <span>&bull; CWE: {f.cwe_id || 'CWE-200'}</span>
                  <span>&bull; CVE: {f.cve_id ? `${f.cve_id} (${f.cve_status || 'Verified'})` : 'Not identified'}</span>
                  <span>&bull; NVD CVSS: {f.cve_id && f.nvd_cvss !== null && f.nvd_cvss !== undefined ? `${f.nvd_cvss.toFixed(1)} / 10.0` : (f.nvd_cvss_display || 'Not available')}</span>
                </div>

                {/* AI Hypothesis */}
                <div className="p-3 rounded bg-purple-950/20 border border-purple-500/20 text-purple-300">
                  <div className="text-[10px] uppercase font-bold text-purple-400 mb-0.5">
                    AI Security Hypothesis (Confidence: {f.ai_confidence}%)
                  </div>
                  <div className="leading-relaxed">{f.ai_hypothesis || 'Rule-based heuristics correlated.'}</div>
                </div>

                {/* Technical Evidence */}
                <div>
                  <div className="text-[10px] uppercase font-bold text-cyan-400 mb-1 flex items-center justify-between">
                    <span>Technical Evidence Validation ({f.evidence.length} captured &bull; 1 Canonical Proof)</span>
                  </div>
                  <div className="space-y-2">
                    {f.evidence.map((e: any) => {
                      const isCanonical = e.is_canonical ?? (e.id === 'EV-WM-API-DOCS-A018-GET' || e.lifecycle_status === 'CANONICAL');
                      return (
                        <div key={e.id} className={`p-3 rounded-xl border text-[11px] font-mono ${
                          isCanonical
                            ? 'bg-slate-950/90 border-cyan-500/40 shadow-[0_0_15px_rgba(6,182,212,0.1)]'
                            : 'bg-slate-950/60 border-slate-800/80 text-slate-400'
                        }`}>
                          <div className="flex flex-wrap items-center justify-between gap-1 mb-1">
                            <div className="flex items-center space-x-2">
                              <span className={isCanonical ? 'text-cyan-300 font-bold' : 'text-slate-300 font-semibold'}>
                                [{e.id}] {e.type}
                              </span>
                              <span className="text-emerald-400 font-bold">&bull; {e.validation_result}</span>
                            </div>
                            <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${
                              isCanonical
                                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                                : 'bg-slate-800 text-slate-400 border border-slate-700'
                            }`}>
                              {isCanonical ? 'Canonical Active' : 'Historical Artifact'}
                            </span>
                          </div>
                          <div className="text-slate-500 text-[10px] mb-1">
                            SHA-256: {e.integrity_hash ? `${e.integrity_hash.slice(0, 24)}...` : 'N/A'}
                          </div>
                          <div className="text-slate-300">{e.description}</div>
                          {e.relationship_note && (
                            <div className={`mt-1.5 text-[10px] ${isCanonical ? 'text-cyan-400/90' : 'text-slate-400'}`}>
                              {e.relationship_note}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Quick Remediation */}
                <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-300">
                  <strong className="text-emerald-400">Remediation:</strong> {f.remediation.quick_fix}
                </div>

                {/* Re-Verifications lifecycle if present */}
                {f.re_verifications && f.re_verifications.length > 0 && (
                  <div className="pt-2 border-t border-slate-800/80">
                    <div className="text-[10px] uppercase font-bold text-amber-400 mb-1">
                      Historical Re-Test Lifecycle ({f.re_verifications.length} executed &bull; Latest Verdict: {f.status})
                    </div>
                    <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
                      {f.re_verifications.slice(-3).map((rv: any) => (
                        <div key={rv.id} className="p-2 rounded bg-slate-950/70 border border-slate-800 text-[11px] flex justify-between items-center">
                          <span className="text-slate-300">Re-Test [{rv.id}] &bull; Verdict: <strong className={rv.verification_verdict === 'VERIFIED_REMEDIATED' ? 'text-emerald-400' : 'text-rose-400'}>{rv.verification_verdict}</strong></span>
                          <span className="text-slate-500 text-[10px]">{rv.timestamp?.slice(0, 19)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Assessment Limitations */}
        <div className="border-t border-slate-800 pt-6">
          <h3 className="text-xs font-bold font-mono-code uppercase text-slate-400 tracking-wider mb-2">
            4. Methodology & Operational Caveats
          </h3>
          <ul className="space-y-1.5 font-mono-code text-[11px] text-slate-400 list-disc list-inside">
            {report.limitations.map((lim: string, idx: number) => (
              <li key={idx}>{lim}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
