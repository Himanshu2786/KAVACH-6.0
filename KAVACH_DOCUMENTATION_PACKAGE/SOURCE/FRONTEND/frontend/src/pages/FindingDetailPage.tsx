import React, { useState, useEffect } from 'react';
import {
  Shield,
  ArrowLeft,
  BrainCircuit,
  FileCheck2,
  GitFork,
  Sliders,
  Wrench,
  Activity,
  Sparkles,
  ExternalLink,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { Tooltip } from '../components/common/Tooltip';
import { Finding, RemediationPlan, EvidenceRecord, KnowledgeRecord } from '../types';

export const FindingDetailPage: React.FC = () => {
  const { selectedFindingId, activeAssessment, assessments, setActiveAssessment, navigate, showToast } = useApp();
  const [finding, setFinding] = useState<Finding | null>(null);
  const [remediation, setRemediation] = useState<RemediationPlan | null>(null);
  const [knowledge, setKnowledge] = useState<{ cwe: KnowledgeRecord | null; owasp: KnowledgeRecord | null } | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'ai' | 'knowledge' | 'evidence' | 'risk' | 'remediation' | 'audit'>('ai');
  const [analyzing, setAnalyzing] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchFinding = () => {
    if (!selectedFindingId) return;
    setLoading(true);
    api.getFinding(selectedFindingId)
      .then((f) => {
        setFinding(f);
        return Promise.all([
          api.getRemediation(f.id).catch(() => null),
          api.correlateKnowledge(f.category, f.title).catch(() => null)
        ]);
      })
      .then(([rem, know]) => {
        setRemediation(rem);
        setKnowledge(know);
        setLoading(false);
      })
      .catch((err) => {
        showToast('error', 'Error', err.message || 'Finding not found');
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchFinding();
  }, [selectedFindingId]);

  const handleRunAI = async () => {
    if (!finding) return;
    setAnalyzing(true);
    try {
      const res = await api.analyzeFinding(finding.id);
      setFinding(res.updated_finding);
      showToast('success', 'AI Analysis Complete', `Security hypothesis generated (${res.data.source_mode}).`);
    } catch (err: any) {
      showToast('error', 'AI Error', err.message || 'Failed to complete AI analysis');
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading || !finding) {
    return (
      <div className="py-20 text-center font-mono-code text-xs text-slate-400">
        <RefreshCw className="w-6 h-6 animate-spin mx-auto text-cyan-400 mb-2" />
        Loading Finding Intelligence Dossier...
      </div>
    );
  }

  // ── Data Isolation Enforcement ─────────────────────────────────────────────
  if (finding && activeAssessment && finding.assessment_id !== activeAssessment.id) {
    const parentAsm = assessments.find((a) => a.id === finding.assessment_id);
    return (
      <div className="py-16 max-w-2xl mx-auto text-center space-y-4">
        <div className="p-6 rounded-xl border border-amber-500/30 bg-amber-950/20 text-amber-300 font-mono-code text-xs space-y-3">
          <div className="font-bold text-sm text-amber-200">
            Finding Belongs to Another Assessment
          </div>
          <p className="text-slate-300">
            Finding <strong className="text-white">{finding.id}</strong> belongs to assessment{" "}
            <strong className="text-cyan-300">{finding.assessment_id}</strong>, but your current active context is{" "}
            <strong className="text-cyan-300">{activeAssessment.id}</strong>.
          </p>
          <p className="text-slate-400 text-[11px]">
            To maintain strict data isolation and prevent demo or cross-assessment contamination, findings cannot be viewed inside a foreign assessment scope.
          </p>
          <div className="flex items-center justify-center gap-3 pt-3">
            <button
              onClick={() => navigate('findings')}
              className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold cursor-pointer"
            >
              Return to Active Findings
            </button>
            {parentAsm && (
              <button
                onClick={() => {
                  setActiveAssessment(parentAsm);
                  fetchFinding();
                }}
                className="px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs cursor-pointer"
              >
                Switch Context to {finding.assessment_id}
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'ai', label: 'AI Analysis & Hypothesis', icon: BrainCircuit },
    { id: 'evidence', label: 'Technical Evidence', icon: FileCheck2 },
    { id: 'overview', label: 'Overview', icon: Shield },
    { id: 'knowledge', label: 'Security Knowledge', icon: GitFork },
    { id: 'risk', label: 'Risk Scoring', icon: Sliders },
    { id: 'remediation', label: 'Remediation', icon: Wrench },
  ];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <button
          onClick={() => navigate('findings')}
          className="flex items-center space-x-2 text-xs font-mono-code text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Findings Matrix</span>
        </button>

        <div className="flex items-center space-x-3 font-mono-code text-xs">
          <button
            onClick={() => navigate('evidence', finding.id)}
            className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 flex items-center space-x-1.5 font-bold transition-all"
          >
            <FileCheck2 className="w-3.5 h-3.5" />
            <span>Validate Evidence (Hero Engine)</span>
          </button>
          <button
            onClick={handleRunAI}
            disabled={analyzing}
            className="px-3.5 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold flex items-center space-x-1.5 transition-all shadow-[0_0_12px_rgba(6,182,212,0.25)]"
          >
            {analyzing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <BrainCircuit className="w-3.5 h-3.5" />}
            <span>{analyzing ? 'Reasoning...' : 'Dispatch AI Analysis'}</span>
          </button>
        </div>
      </div>

      {/* Hero Header Card */}
      <GlassCard glow={finding.status === 'CONFIRMED' ? 'green' : 'cyan'}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2.5 mb-2 font-mono-code">
              <span className="text-xs font-bold text-cyan-400 bg-cyan-950/60 px-2.5 py-0.5 rounded border border-cyan-800">
                {finding.id}
              </span>
              <span className="text-xs text-slate-400">Target Component:</span>
              <span className="text-xs font-bold text-slate-200">{finding.affected_component}</span>
            </div>
            <h1 className="text-lg md:text-xl font-bold text-slate-100">{finding.title}</h1>
            <div className="flex items-center space-x-3 mt-2 font-mono-code text-xs text-slate-400">
              <span>Category: <strong className="text-slate-200">{finding.category}</strong></span>
              <span>&bull;</span>
              <span>CWE: <Tooltip keyword="CWE" label={finding.cwe_id || 'CWE-639'} /></span>
              <span>&bull;</span>
              <span>OWASP: <Tooltip keyword="OWASP" label={finding.owasp_category || 'OWASP-A01'} /></span>
            </div>
          </div>

          <div className="flex flex-row md:flex-col items-end gap-2 shrink-0 font-mono-code">
            <div className="flex items-center space-x-2">
              <Badge label={finding.base_severity} type="severity" />
              <Badge label={finding.status} type="status" />
            </div>
            <div className="text-[11px] text-slate-400">
              Evidence: <span className={finding.evidence_status === 'VERIFIED' ? 'text-emerald-400 font-bold' : 'text-slate-400'}>{finding.evidence_status}</span>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Intelligence Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2 overflow-x-auto font-mono-code text-xs">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg transition-all ${
                isActive
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/60 shadow-[0_0_12px_rgba(6,182,212,0.15)] font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab 1: AI Analysis Section */}
      {activeTab === 'ai' && (
        <div className="space-y-6">
          {/* Critical Callout */}
          <div className="p-3.5 rounded-xl bg-purple-950/40 border border-purple-500/30 font-mono-code text-xs text-purple-300 flex items-start space-x-3">
            <Sparkles className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
            <div>
              <strong className="block text-purple-200 uppercase tracking-wide mb-0.5">
                Core KAVACH Principle: AI Confidence != Vulnerability Confirmation
              </strong>
              AI analysis provides advisory security hypotheses ({finding.ai_confidence}% analytical confidence in relevance). Technical evidence observation determines vulnerability confirmation.
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Hypothesis & Reasoning */}
            <GlassCard
              title="Security Hypothesis"
              subtitle="Testable thesis synthesized from context"
              icon={<BrainCircuit className="w-5 h-5 text-purple-400" />}
              className="lg:col-span-2 space-y-4"
            >
              <div>
                <div className="text-[11px] font-mono-code text-slate-400 uppercase mb-1">Synthesized Thesis</div>
                <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-100 text-xs leading-relaxed font-mono-code">
                  {finding.ai_hypothesis || 'No hypothesis generated yet. Click "Dispatch AI Analysis".'}
                </div>
              </div>

              <div>
                <div className="text-[11px] font-mono-code text-slate-400 uppercase mb-1">Analytical Reasoning Summary</div>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/50 p-3 rounded-lg border border-slate-800/80">
                  {finding.ai_reasoning_summary || 'Rule-based heuristics correlated finding attributes with known threat patterns.'}
                </p>
              </div>

              <div>
                <div className="text-[11px] font-mono-code text-slate-400 uppercase mb-1">Potential Operational Impact</div>
                <div className="text-xs text-rose-300 bg-rose-950/20 border border-rose-500/20 p-3 rounded-lg">
                  {finding.ai_potential_impact || 'Potential compromise of system confidentiality and data integrity.'}
                </div>
              </div>
            </GlassCard>

            {/* Validation Recommendations */}
            <GlassCard
              title="Recommended Validation"
              subtitle="Safe non-destructive probe steps"
              icon={<FileCheck2 className="w-5 h-5 text-cyan-400" />}
            >
              <div className="space-y-2.5">
                {finding.recommended_validation?.map((step, idx) => (
                  <div key={idx} className="p-2.5 rounded bg-slate-900/70 border border-slate-800 font-mono-code text-xs text-slate-300 flex items-start space-x-2">
                    <span className="text-cyan-400 font-bold shrink-0">{idx + 1}.</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800">
                <button
                  id="execute-validation-probe-btn"
                  onClick={() => navigate('evidence', finding.id)}
                  className="w-full py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-mono-code text-xs font-bold uppercase tracking-wider transition-colors flex items-center justify-center space-x-1.5 cursor-pointer"
                >
                  <FileCheck2 className="w-3.5 h-3.5" />
                  <span>Execute Validation Probe</span>
                </button>
              </div>
            </GlassCard>
          </div>
        </div>
      )}

      {/* Tab 2: Technical Evidence */}
      {activeTab === 'evidence' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold font-mono-code uppercase text-slate-100">
                Recorded Technical Observations
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Cryptographically hashed proofs gathered via safe probes and HTTP auditing.
              </p>
            </div>
            <button
              onClick={() => navigate('evidence', finding.id)}
              className="px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold font-mono-code text-xs transition-colors"
            >
              Open Full Validation Engine
            </button>
          </div>

          <div className="space-y-3">
            {finding.evidence_records && finding.evidence_records.length > 0 ? (
              finding.evidence_records.map((ev) => (
                <GlassCard key={ev.id} glow={ev.validation_result === 'CONFIRMED' ? 'green' : 'none'}>
                  <div className="flex items-center justify-between mb-2 font-mono-code text-xs">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-cyan-400">[{ev.id}]</span>
                      <span className="text-slate-200">{ev.evidence_type}</span>
                      <span className="text-slate-500">via {ev.source}</span>
                    </div>
                    <Badge label={ev.validation_result} variant={ev.validation_result} size="sm" />
                  </div>

                  <p className="text-xs text-slate-300 mb-3">{ev.description}</p>

                  <div className="mb-2">
                    <div className="text-[10px] font-mono-code text-slate-500 uppercase mb-1">
                      Raw Probe Payload Snippet:
                    </div>
                    <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-mono-code text-emerald-300 overflow-x-auto whitespace-pre-wrap">
                      {ev.raw_data}
                    </pre>
                  </div>

                  <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between font-mono-code text-[10px] text-slate-500">
                    <span className="truncate mr-4">SHA-256: {ev.integrity_hash}</span>
                    <span className="shrink-0">{ev.timestamp}</span>
                  </div>
                </GlassCard>
              ))
            ) : (
              <div className="text-center py-10 glass-panel rounded-xl font-mono-code text-xs text-slate-400">
                No technical evidence captured yet for this finding.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Overview */}
      {activeTab === 'overview' && (
        <GlassCard title="Finding Context & Description">
          <p className="text-xs text-slate-300 leading-relaxed font-mono-code mb-4">
            {finding.description}
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono-code text-xs">
            <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800">
              <div className="text-[10px] text-slate-500 uppercase">Assessment ID</div>
              <div className="text-slate-200 mt-0.5">{finding.assessment_id}</div>
            </div>
            <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800">
              <div className="text-[10px] text-slate-500 uppercase">Priority Score</div>
              <div className="text-cyan-400 font-bold mt-0.5">{finding.priority_score} / 10.0</div>
            </div>
            <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800">
              <div className="text-[10px] text-slate-500 uppercase">Created</div>
              <div className="text-slate-400 mt-0.5">{finding.created_at.slice(0, 10)}</div>
            </div>
            <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800">
              <div className="text-[10px] text-slate-500 uppercase">Updated</div>
              <div className="text-slate-400 mt-0.5">{finding.updated_at.slice(0, 10)}</div>
            </div>
          </div>
        </GlassCard>
      )}

      {/* Tab 4: Security Knowledge */}
      {activeTab === 'knowledge' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <GlassCard title="CWE Taxonomy Record" subtitle={knowledge?.cwe?.id || 'CWE-639'}>
            <div className="space-y-3 font-mono-code text-xs">
              <div className="text-slate-200 font-bold">{knowledge?.cwe?.title}</div>
              <p className="text-slate-400 leading-relaxed">{knowledge?.cwe?.description}</p>
            </div>
          </GlassCard>

          <GlassCard title="OWASP Top 10 Mapping" subtitle={knowledge?.owasp?.id || 'OWASP-A01'}>
            <div className="space-y-3 font-mono-code text-xs">
              <div className="text-slate-200 font-bold">{knowledge?.owasp?.title}</div>
              <p className="text-slate-400 leading-relaxed">{knowledge?.owasp?.description}</p>
            </div>
          </GlassCard>

          <GlassCard title="CVE / NVD Intelligence" subtitle={finding.cve_id || 'Not identified'}>
            <div className="space-y-2 font-mono-code text-xs">
              <div className="flex justify-between border-b border-slate-800 pb-1">
                <span className="text-slate-400">CVE Status:</span>
                <span className="text-slate-200 font-bold">{finding.cve_id ? (finding.cve_status || 'Version Verification Required') : 'Not identified'}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800 pb-1">
                <span className="text-slate-400">NVD CVSS:</span>
                <span className="text-slate-200 font-bold">
                  {finding.cve_id && finding.nvd_cvss !== null && finding.nvd_cvss !== undefined ? `${finding.nvd_cvss.toFixed(1)} / 10.0` : 'Not available'}
                </span>
              </div>
              <p className="text-slate-400 leading-relaxed pt-1">
                {finding.cve_id
                  ? `Correlated CVE ${finding.cve_id} tracked with authoritative NVD provenance.`
                  : 'No specific CVE record is associated with this finding. CWE-200 taxonomy is validated without speculative CVE assignment.'}
              </p>
            </div>
          </GlassCard>
        </div>
      )}

      {/* Tab 5: Risk Scoring */}
      {activeTab === 'risk' && (
        <GlassCard title="Multi-Factor Prioritization Breakdown">
          <div className="font-mono-code text-xs text-slate-300 leading-relaxed">
            Deterministic risk prioritization score calculated as <strong className="text-cyan-400">{finding.priority_score} / 10.0</strong> mapped to tier <Badge label={finding.priority} type="severity" size="sm" />.
          </div>
        </GlassCard>
      )}

      {/* Tab 6: Remediation */}
      {activeTab === 'remediation' && remediation && (
        <div className="space-y-4">
          <GlassCard title="Actionable Developer Remediation">
            <div className="space-y-4 font-mono-code text-xs">
              <div>
                <div className="text-[11px] font-bold text-emerald-400 uppercase mb-1">Quick Fix</div>
                <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-emerald-200">
                  {remediation.quick_fix}
                </div>
              </div>

              <div>
                <div className="text-[11px] font-bold text-slate-300 uppercase mb-1">Implementation Guidance</div>
                <pre className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {remediation.detailed_fix}
                </pre>
              </div>

              <div>
                <div className="text-[11px] font-bold text-cyan-300 uppercase mb-1">Secure Code Reference</div>
                <pre className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 text-emerald-400 font-mono-code overflow-x-auto">
                  {remediation.code_sample}
                </pre>
              </div>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
};
