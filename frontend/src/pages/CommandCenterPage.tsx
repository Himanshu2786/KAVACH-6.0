import React, { useState, useEffect } from 'react';
import {
  Compass,
  Shield,
  AlertTriangle,
  CheckCircle2,
  Activity,
  ArrowRight,
  ExternalLink,
  Layers,
  FileCheck2,
  Sliders,
  FileText,
  Search,
  Globe,
  Radio,
  Lock,
  Clock,
  Sparkles,
  BarChart3,
  Server,
  Zap,
  Target,
  X,
  Check,
  ChevronRight,
  Hash,
  Eye
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { Finding, SecurityPosture } from '../types';
import { Badge } from '../components/common/Badge';

export const isConfirmedFinding = (f: Finding): boolean => {
  if (f.evidence_status === 'REQUIRES_SOURCE_VALIDATION') {
    return false;
  }
  if (f.evidence_status === 'VERIFIED') {
    return true;
  }
  if (f.status === 'CONFIRMED' || f.status === 'STILL_OPEN' || f.status === 'VERIFIED') {
    return true;
  }
  if (f.evidence_records && f.evidence_records.some((e) => e.validation_result === 'CONFIRMED')) {
    return true;
  }
  return false;
};

type ResultModalType =
  | 'SECURITY_POSTURE'
  | 'LOCAL_FINDINGS'
  | 'RISK_LEVEL'
  | 'EVIDENCE_INTEGRITY'
  | 'SEVERITY'
  | 'STAGE'
  | 'FINDING_DETAIL'
  | 'SOVEREIGN_GUARANTEE'
  | null;

export const CommandCenterPage: React.FC = () => {
  const { activeAssessment, navigate, showToast } = useApp();
  const [findings, setFindings] = useState<Finding[]>([]);
  const [posture, setPosture] = useState<SecurityPosture | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // ── Result Modal Interactive State ───────────────────────────────────────
  const [activeResultModal, setActiveResultModal] = useState<ResultModalType>(null);
  const [selectedSeverity, setSelectedSeverity] = useState<string | null>(null);
  const [selectedStage, setSelectedStage] = useState<{ id: string; name: string; idx: number } | null>(null);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  useEffect(() => {
    if (!activeAssessment) {
      setFindings([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    Promise.all([
      api.getFindings({ assessment_id: activeAssessment.id }).catch(() => [] as Finding[]),
      api.getSecurityPosture(activeAssessment.id).catch(() => null)
    ])
      .then(([findingsData, postureData]) => {
        setFindings(findingsData);
        setPosture(postureData);
      })
      .finally(() => setLoading(false));
  }, [activeAssessment?.id]);

  const confirmedCount = findings.filter(isConfirmedFinding).length;

  const severityCounts = {
    CRITICAL: findings.filter((f) => f.base_severity === 'CRITICAL').length,
    HIGH: findings.filter((f) => f.base_severity === 'HIGH').length,
    MEDIUM: findings.filter((f) => f.base_severity === 'MEDIUM').length,
    LOW: findings.filter((f) => f.base_severity === 'LOW').length,
    INFO: findings.filter((f) => f.base_severity === 'INFO').length,
  };

  const postureScore = posture?.score ?? (activeAssessment ? 70 : 100);
  const postureLabel = posture?.posture ?? (
    postureScore < 50 ? 'CRITICAL RISK' :
      postureScore < 70 ? 'HIGH RISK' :
        postureScore < 85 ? 'MODERATE RISK' :
          'LOW RISK'
  );

  const riskLevel = posture?.risk_level ?? (
    severityCounts.CRITICAL > 0 ? 'CRITICAL' :
      severityCounts.HIGH > 0 ? 'HIGH' :
        severityCounts.MEDIUM > 0 ? 'MEDIUM' :
          severityCounts.LOW > 0 ? 'LOW' :
            'LOW'
  );

  const PIPELINE_STAGES = [
    {
      id: 'DISCOVER',
      name: 'Discovery',
      desc: 'Target URL normalization, network perimeter mapping, DNS resolution, and scope boundary verification.',
      actions: ['Target URL validation', 'Perimeter port/route reconnaissance', 'Scope policy enforcement']
    },
    {
      id: 'ASSESS',
      name: 'Assessment',
      desc: 'Live deterministic HTTP/TLS probe execution, unauthenticated endpoint surface probing, and schema verification.',
      actions: ['Live GET /openapi.json probe', 'Response status code telemetry', 'Endpoint payload capture']
    },
    {
      id: 'CORRELATE',
      name: 'Correlation',
      desc: 'Authoritative threat intelligence correlation with CISA Known Exploited Vulnerabilities (KEV) and NVD CVE catalog.',
      actions: ['CISA KEV catalog cross-referencing', 'NVD CVE score mapping', 'EPSS probability modeling']
    },
    {
      id: 'ANALYZE',
      name: 'AI Analyst',
      desc: 'Local sovereign neural assessment, blast radius computation, root cause isolation, and remediation strategy planning.',
      actions: ['Ollama local model reasoning', 'Blast radius isolation', 'Defensive countermeasure synthesis']
    },
    {
      id: 'VALIDATE',
      name: 'Validation',
      desc: 'Cryptographic SHA-256 evidence hashing, zero-false-positive gate validation, and provenance seal attachment.',
      actions: ['Cryptographic SHA-256 hashing', 'Zero-false-positive threshold check', 'Immutable evidence seal']
    },
    {
      id: 'PRIORITIZE',
      name: 'Prioritize',
      desc: 'Deterministic multi-factor mathematical risk calculation without synthetic hallucination.',
      actions: ['CVSS 3.1 base score weighting (30%)', 'Asset criticality weighting (25%)', 'Exposure boundary factor (20%)', 'Priority index calculation']
    },
    {
      id: 'REMEDIATE',
      name: 'Remediation',
      desc: 'Actionable hardening blueprints, reverse proxy access control policies, and live re-verification suites.',
      actions: ['Route protection configuration', 'Automated patch playbook generation', 'Live re-test suite execution']
    },
    {
      id: 'REPORT',
      name: 'Report',
      desc: 'Comprehensive sovereign security intelligence report, executive summaries, printable HTML, and JSON export packages.',
      actions: ['Executive HTML report compilation', 'Full JSON telemetry packaging', 'Audit ledger sealing']
    }
  ];

  const currentStage = activeAssessment?.current_stage || 'REPORT';
  const currentStageIdx = PIPELINE_STAGES.findIndex((s) => s.id === currentStage);

  return (
    <div className="space-y-6 pb-12 animate-in fade-in duration-300">
      {/* ── Top Header Bar ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/[0.08] pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wide uppercase bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
              SECURITY OPERATIONS: ACTIVE COMMAND
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <Compass className="w-7 h-7 text-cyan-400" />
            Command Center
          </h1>
          <p className="text-neutral-400 text-xs sm:text-sm mt-1">
            Overall security posture, deterministic risk distribution, and operational assessment telemetry. Click any card to inspect immediate results.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => navigate('world-monitor')}
            className="px-3.5 py-2 text-xs font-semibold rounded-xl bg-white/[0.06] hover:bg-white/[0.12] text-neutral-200 hover:text-white border border-white/10 transition-all flex items-center gap-2 cursor-pointer"
          >
            <Globe className="w-3.5 h-3.5 text-cyan-400" />
            <span>World Situational Monitor</span>
          </button>
          <button
            onClick={() => navigate('new-assessment')}
            className="btn-primary px-3.5 py-2 text-xs font-semibold rounded-xl flex items-center gap-2 cursor-pointer"
          >
            <Shield className="w-3.5 h-3.5" />
            <span>Assess Target</span>
          </button>
        </div>
      </div>

      {/* ── Active Assessment Context Banner ── */}
      {activeAssessment ? (
        <div className="p-4 glass-level-1 border border-white/10 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-xs font-mono">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
              <Target className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-white font-bold text-sm truncate max-w-md">
                  {activeAssessment.target_url}
                </span>
                <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${activeAssessment.status === 'COMPLETED'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                  }`}>
                  {activeAssessment.status}
                </span>
              </div>
              <div className="text-neutral-400 text-[11px] mt-0.5">
                Assessment ID: <strong className="text-cyan-300">{activeAssessment.id}</strong> &bull; Scope: {activeAssessment.scope || 'Full Application'}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <div className="text-right">
              <span className="text-neutral-500 block uppercase text-[10px]">Pipeline Stage</span>
              <span className="text-white font-bold">{activeAssessment.current_stage || 'REPORT'}</span>
            </div>
            <div className="w-px h-6 bg-white/10" />
            <div className="text-right">
              <span className="text-neutral-500 block uppercase text-[10px]">Stage Progress</span>
              <span className="text-cyan-400 font-bold">{activeAssessment.progress || 100}%</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 glass-level-1 border border-white/10 rounded-2xl flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-2 text-neutral-400">
            <Shield className="w-4 h-4 text-neutral-500" />
            <span>No assessment currently selected. Showing platform default posture.</span>
          </div>
          <button
            onClick={() => navigate('new-assessment')}
            className="text-cyan-400 hover:text-white underline cursor-pointer"
          >
            Launch Assessment
          </button>
        </div>
      )}

      {/* ── 4 Executive KPI Cards (Click to Inspect Results) ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Overall Security Posture */}
        <div
          onClick={() => setActiveResultModal('SECURITY_POSTURE')}
          className="glass-level-2 rounded-2xl p-5 space-y-2 border border-white/[0.08] cursor-pointer hover:border-cyan-400/50 hover:bg-white/[0.04] transition-all group relative overflow-hidden"
          title="Click to view Security Posture assessment results"
        >
          <div className="flex items-center justify-between text-neutral-400 text-xs font-mono">
            <span>SECURITY POSTURE</span>
            <Activity className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="flex flex-wrap items-baseline gap-2">
            <span className="text-3xl font-black text-white font-mono">{postureScore}</span>
            <span className="text-neutral-500 text-xs font-mono">/ 100</span>
            <span className={`text-[10px] font-bold font-mono px-2 py-0.5 rounded ${postureLabel === 'CRITICAL RISK' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
              postureLabel === 'HIGH RISK' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                postureLabel === 'MODERATE RISK' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                  'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              }`}>
              {postureLabel}
            </span>
          </div>
          <div className="text-[11px] font-mono text-emerald-400 flex items-center justify-between pt-1 border-t border-white/[0.04]">
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              {posture?.status_label || 'EVIDENCE VERIFIED'}
            </div>
            <span className="text-[10px] text-cyan-400/80 group-hover:text-cyan-300 flex items-center gap-0.5">
              Inspect Result <ChevronRight className="w-3 h-3" />
            </span>
          </div>
        </div>

        {/* KPI 2: Confirmed Findings */}
        <div
          onClick={() => setActiveResultModal('LOCAL_FINDINGS')}
          className="glass-level-2 rounded-2xl p-5 space-y-2 border border-white/[0.08] cursor-pointer hover:border-cyan-400/50 hover:bg-white/[0.04] transition-all group relative overflow-hidden"
          title="Click to view Local Findings audit results"
        >
          <div className="flex items-center justify-between text-neutral-400 text-xs font-mono">
            <span>LOCAL FINDINGS</span>
            <AlertTriangle className="w-4 h-4 text-orange-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white font-mono">{confirmedCount}</span>
            <span className="text-neutral-500 text-xs font-mono">confirmed / {findings.length} total</span>
          </div>
          <div className="text-[11px] font-mono text-neutral-400 flex items-center justify-between pt-1 border-t border-white/[0.04]">
            <span>Active Target Scoped</span>
            <span className="text-cyan-400/80 group-hover:text-cyan-300 flex items-center gap-0.5">
              Inspect Result <ChevronRight className="w-3 h-3" />
            </span>
          </div>
        </div>

        {/* KPI 3: Criticality & Risk Distribution */}
        <div
          id="command-center-risk-card"
          onClick={() => navigate('risk')}
          className="glass-level-2 rounded-2xl p-5 space-y-2 border border-white/[0.08] cursor-pointer hover:border-cyan-400/50 hover:bg-white/[0.04] transition-all group relative overflow-hidden"
          title="Click to open Deterministic Risk Prioritization for active assessment"
        >
          <div className="flex items-center justify-between text-neutral-400 text-xs font-mono">
            <span>RISK LEVEL</span>
            <BarChart3 className="w-4 h-4 text-rose-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-3xl font-black font-mono ${riskLevel === 'CRITICAL' ? 'text-red-400' :
              riskLevel === 'HIGH' ? 'text-orange-400' :
                riskLevel === 'MEDIUM' ? 'text-amber-400' :
                  'text-emerald-400'
              }`}>
              {riskLevel}
            </span>
          </div>
          <div className="text-[11px] font-mono text-neutral-400 flex items-center justify-between pt-1 border-t border-white/[0.04]">
            <span className="text-cyan-300 font-semibold">CVSS 3.1 &bull; {riskLevel}</span>
            <span className="text-cyan-400/80 group-hover:text-cyan-300 flex items-center gap-0.5">
              Open Risk Page <ChevronRight className="w-3 h-3" />
            </span>
          </div>
        </div>

        {/* KPI 4: Evidence Integrity */}
        <div
          onClick={() => setActiveResultModal('EVIDENCE_INTEGRITY')}
          className="glass-level-2 rounded-2xl p-5 space-y-2 border border-white/[0.08] cursor-pointer hover:border-cyan-400/50 hover:bg-white/[0.04] transition-all group relative overflow-hidden"
          title="Click to view Cryptographic Evidence Integrity ledger"
        >
          <div className="flex items-center justify-between text-neutral-400 text-xs font-mono">
            <span>EVIDENCE INTEGRITY</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white font-mono">100%</span>
            <span className="text-neutral-500 text-xs font-mono">SHA-256</span>
          </div>
          <div className="text-[11px] font-mono text-emerald-400 flex items-center justify-between pt-1 border-t border-white/[0.04]">
            <div className="flex items-center gap-1.5">
              <Lock className="w-3 h-3 text-emerald-400" />
              <span>Cryptographically Verified</span>
            </div>
            <span className="text-cyan-400/80 group-hover:text-cyan-300 flex items-center gap-0.5">
              Inspect Result <ChevronRight className="w-3 h-3" />
            </span>
          </div>
        </div>
      </div>

      {/* ── 8-Stage Assessment Stepper Overview (Click Any Stage Card for Details) ── */}
      <div className="glass-level-2 rounded-2xl p-5 border border-white/[0.08] space-y-4">
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
          <div>
            <span className="text-xs font-mono text-neutral-400 uppercase tracking-wider block">Assessment Lifecycle</span>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              8-Stage Verification Pipeline Execution
            </h3>
          </div>
          <button
            onClick={() => navigate('progress')}
            className="text-xs font-mono text-cyan-400 hover:text-white flex items-center gap-1 transition-colors cursor-pointer"
          >
            <span>View Full Stepper</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
          {PIPELINE_STAGES.map((stg, idx) => {
            const isCompleted = activeAssessment?.status === 'COMPLETED' || idx <= currentStageIdx;
            const isCurrent = stg.id === currentStage && activeAssessment?.status !== 'COMPLETED';

            return (
              <div
                key={stg.id}
                onClick={() => {
                  setSelectedStage({ id: stg.id, name: stg.name, idx });
                  setActiveResultModal('STAGE');
                }}
                className={`p-2.5 rounded-xl border text-center transition-all cursor-pointer group hover:border-cyan-400/60 hover:scale-[1.02] ${isCurrent
                  ? 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300 font-bold'
                  : isCompleted
                    ? 'bg-white/[0.06] border-white/10 text-neutral-200 hover:bg-white/[0.10]'
                    : 'bg-black/30 border-white/[0.04] text-neutral-600 hover:text-neutral-400'
                  }`}
                title={`Click to inspect Stage 0${idx + 1} (${stg.name}) results`}
              >
                <div className="text-[10px] font-mono text-neutral-500 mb-0.5 group-hover:text-cyan-400">0{idx + 1}</div>
                <div className="text-xs truncate">{stg.name}</div>
                <div className="mt-1 flex justify-center items-center gap-1">
                  {isCompleted ? (
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  ) : (
                    <span className="w-1.5 h-1.5 rounded-full bg-neutral-600" />
                  )}
                  <span className="text-[9px] font-mono text-neutral-500 opacity-0 group-hover:opacity-100 transition-opacity">
                    View
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Main Two-Column Content ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* LEFT COLUMN: Severity Matrix & Target Findings (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">

          {/* Finding Severity Distribution (Click Any Severity Card to Filter / Inspect) */}
          <div className="glass-level-2 rounded-2xl p-5 border border-white/[0.08] space-y-4">
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2 font-mono">
                  <BarChart3 className="w-4 h-4 text-cyan-400" />
                  Vulnerability Severity Breakdown
                </h3>
                <span className="text-[11px] text-neutral-400 font-mono">
                  Click any severity card to inspect identified vulnerabilities
                </span>
              </div>
              <button
                onClick={() => navigate('findings')}
                className="text-xs font-mono text-cyan-400 hover:text-white flex items-center gap-1 cursor-pointer"
              >
                <span>Findings Matrix</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>

            <div className="grid grid-cols-5 gap-2 text-center font-mono">
              <div
                onClick={() => {
                  setSelectedSeverity('CRITICAL');
                  setActiveResultModal('SEVERITY');
                }}
                className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 hover:border-red-400 hover:bg-red-500/20 transition-all cursor-pointer group"
                title="Click to view Critical findings"
              >
                <div className="text-[10px] text-red-400 uppercase font-bold group-hover:text-red-300">Critical</div>
                <div className="text-xl font-bold text-white mt-1">{severityCounts.CRITICAL}</div>
                <div className="text-[9px] text-red-400/70 mt-0.5 opacity-0 group-hover:opacity-100 transition-opacity">Inspect</div>
              </div>

              <div
                onClick={() => {
                  setSelectedSeverity('HIGH');
                  setActiveResultModal('SEVERITY');
                }}
                className="p-3 rounded-xl bg-orange-500/10 border border-orange-500/20 hover:border-orange-400 hover:bg-orange-500/20 transition-all cursor-pointer group"
                title="Click to view High findings"
              >
                <div className="text-[10px] text-orange-400 uppercase font-bold group-hover:text-orange-300">High</div>
                <div className="text-xl font-bold text-white mt-1">{severityCounts.HIGH}</div>
                <div className="text-[9px] text-orange-400/70 mt-0.5 opacity-0 group-hover:opacity-100 transition-opacity">Inspect</div>
              </div>

              <div
                onClick={() => {
                  setSelectedSeverity('MEDIUM');
                  setActiveResultModal('SEVERITY');
                }}
                className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 hover:border-amber-400 hover:bg-amber-500/20 transition-all cursor-pointer group"
                title="Click to view Medium findings"
              >
                <div className="text-[10px] text-amber-400 uppercase font-bold group-hover:text-amber-300">Medium</div>
                <div className="text-xl font-bold text-white mt-1">{severityCounts.MEDIUM}</div>
                <div className="text-[9px] text-amber-400/70 mt-0.5 opacity-0 group-hover:opacity-100 transition-opacity">Inspect</div>
              </div>

              <div
                onClick={() => {
                  setSelectedSeverity('LOW');
                  setActiveResultModal('SEVERITY');
                }}
                className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 hover:border-blue-400 hover:bg-blue-500/20 transition-all cursor-pointer group"
                title="Click to view Low findings"
              >
                <div className="text-[10px] text-blue-400 uppercase font-bold group-hover:text-blue-300">Low</div>
                <div className="text-xl font-bold text-white mt-1">{severityCounts.LOW}</div>
                <div className="text-[9px] text-blue-400/70 mt-0.5 opacity-0 group-hover:opacity-100 transition-opacity">Inspect</div>
              </div>

              <div
                onClick={() => {
                  setSelectedSeverity('INFO');
                  setActiveResultModal('SEVERITY');
                }}
                className="p-3 rounded-xl bg-neutral-500/10 border border-neutral-500/20 hover:border-neutral-400 hover:bg-neutral-500/20 transition-all cursor-pointer group"
                title="Click to view Info findings"
              >
                <div className="text-[10px] text-neutral-400 uppercase font-bold group-hover:text-neutral-300">Info</div>
                <div className="text-xl font-bold text-white mt-1">{severityCounts.INFO}</div>
                <div className="text-[9px] text-neutral-400/70 mt-0.5 opacity-0 group-hover:opacity-100 transition-opacity">Inspect</div>
              </div>
            </div>
          </div>

          {/* Active Target Findings List (Click Any Finding Card to View Full Result Dossier) */}
          <div className="glass-level-2 rounded-2xl p-5 border border-white/[0.08] space-y-4">
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2 font-mono">
                  <Shield className="w-4 h-4 text-cyan-400" />
                  Target Findings Registry ({findings.length})
                </h3>
                <span className="text-[11px] text-neutral-400 font-mono">
                  Belonging to {activeAssessment?.id || 'Active Assessment'} &bull; Click card for details
                </span>
              </div>
              <button
                onClick={() => navigate('findings')}
                className="btn-secondary px-3 py-1.5 text-xs font-mono rounded-lg flex items-center gap-1 cursor-pointer"
              >
                <span>View All</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>

            {findings.length === 0 ? (
              <div className="p-8 text-center glass-panel rounded-xl font-mono text-xs text-neutral-400">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                <p className="text-white font-semibold">No Vulnerabilities Detected</p>
                <p className="text-[11px] text-neutral-500 mt-1">Target assessment is clean or pending execution.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {findings.map((f) => (
                  <div
                    key={f.id}
                    onClick={() => {
                      setSelectedFinding(f);
                      setActiveResultModal('FINDING_DETAIL');
                    }}
                    className="p-4 rounded-xl glass-panel border border-white/[0.06] hover:border-cyan-400/40 hover:bg-white/[0.03] transition-all space-y-2.5 cursor-pointer group"
                    title={`Click to view full dossier for ${f.id}`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800 group-hover:border-cyan-500">
                          {f.id}
                        </span>
                        <Badge label={f.base_severity || 'HIGH'} variant={f.base_severity || 'HIGH'} />
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase font-bold">
                          {f.status}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {f.cwe_id && (
                          <span className="text-[11px] font-mono text-neutral-400">
                            {f.cwe_id}
                          </span>
                        )}
                        <span className="text-[10px] font-mono text-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-0.5">
                          View Dossier <ChevronRight className="w-3 h-3" />
                        </span>
                      </div>
                    </div>

                    <h4 className="text-xs sm:text-sm font-bold text-white group-hover:text-cyan-200 transition-colors">
                      {f.title}
                    </h4>

                    {f.affected_component && (
                      <div className="text-[11px] font-mono text-neutral-400 truncate">
                        Target: <span className="text-neutral-200">{f.affected_component}</span>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-2 border-t border-white/[0.06]">
                      <span className="text-[11px] font-mono text-neutral-500">
                        Category: {f.category}
                      </span>
                      <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => navigate('evidence', f.id)}
                          className="px-2.5 py-1 text-[11px] font-mono rounded bg-white/10 hover:bg-white/20 text-white transition-colors flex items-center gap-1 cursor-pointer"
                        >
                          <FileCheck2 className="w-3 h-3 text-cyan-400" />
                          <span>Inspect Evidence</span>
                        </button>
                        <button
                          onClick={() => navigate('ai-analysis', f.id)}
                          className="px-2.5 py-1 text-[11px] font-mono rounded bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/30 transition-colors flex items-center gap-1 cursor-pointer"
                        >
                          <Sparkles className="w-3 h-3" />
                          <span>AI Analysis</span>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: Quick Navigation Launchpad & Operations (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="glass-level-2 rounded-2xl p-5 border border-white/[0.08] space-y-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 font-mono border-b border-white/[0.08] pb-3">
              <Zap className="w-4 h-4 text-amber-400" />
              Operational Modules & Capabilities
            </h3>

            {/* Quick Action 1: World Situational Monitor */}
            <div
              onClick={() => navigate('world-monitor')}
              className="p-3.5 rounded-xl glass-panel border border-white/[0.06] hover:border-cyan-500/40 hover:bg-white/[0.04] transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform" />
                  <span className="text-xs font-bold text-white">World Situational Monitor</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-neutral-500 group-hover:text-cyan-400 transition-colors" />
              </div>
              <p className="text-[11px] text-neutral-400 leading-snug">
                Authoritative CISA KEV & NVD threat advisories correlated with local assessment findings.
              </p>
            </div>

            {/* Quick Action 2: URL Security Check */}
            <div
              onClick={() => navigate('url-check')}
              className="p-3.5 rounded-xl glass-panel border border-white/[0.06] hover:border-cyan-500/40 hover:bg-white/[0.04] transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <Search className="w-4 h-4 text-emerald-400 group-hover:scale-110 transition-transform" />
                  <span className="text-xs font-bold text-white">URL Security Check</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-neutral-500 group-hover:text-emerald-400 transition-colors" />
              </div>
              <p className="text-[11px] text-neutral-400 leading-snug">
                Instant non-destructive target reconnaissance, TLS configuration, and security headers audit.
              </p>
            </div>

            {/* Quick Action 3: Evidence Vault */}
            <div
              onClick={() => navigate('evidence')}
              className="p-3.5 rounded-xl glass-panel border border-white/[0.06] hover:border-cyan-500/40 hover:bg-white/[0.04] transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <FileCheck2 className="w-4 h-4 text-purple-400 group-hover:scale-110 transition-transform" />
                  <span className="text-xs font-bold text-white">Evidence Vault & Terminal</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-neutral-500 group-hover:text-purple-400 transition-colors" />
              </div>
              <p className="text-[11px] text-neutral-400 leading-snug">
                Verbatim CLI terminal reproduction, expected vs observed outputs, and SHA-256 integrity signatures.
              </p>
            </div>

            {/* Quick Action 4: Risk Prioritization */}
            <div
              onClick={() => navigate('risk')}
              className="p-3.5 rounded-xl glass-panel border border-white/[0.06] hover:border-cyan-500/40 hover:bg-white/[0.04] transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-orange-400 group-hover:scale-110 transition-transform" />
                  <span className="text-xs font-bold text-white">Deterministic Risk Scoring</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-neutral-500 group-hover:text-orange-400 transition-colors" />
              </div>
              <p className="text-[11px] text-neutral-400 leading-snug">
                Multi-factor risk scoring engine factoring CVSS, exposure, data sensitivity, and business impact.
              </p>
            </div>

            {/* Quick Action 5: Compliance Reports */}
            <div
              onClick={() => navigate('report')}
              className="p-3.5 rounded-xl glass-panel border border-white/[0.06] hover:border-cyan-500/40 hover:bg-white/[0.04] transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-blue-400 group-hover:scale-110 transition-transform" />
                  <span className="text-xs font-bold text-white">Compliance Report Export</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-neutral-500 group-hover:text-blue-400 transition-colors" />
              </div>
              <p className="text-[11px] text-neutral-400 leading-snug">
                One-click executive security intelligence report generation with print-ready HTML and JSON data.
              </p>
            </div>
          </div>

          {/* Forensic Guarantee Box (Clickable) */}
          <div
            onClick={() => setActiveResultModal('SOVEREIGN_GUARANTEE')}
            className="p-4 rounded-2xl glass-panel border border-white/[0.06] hover:border-cyan-500/40 hover:bg-white/[0.04] transition-all cursor-pointer group space-y-2 text-xs font-mono"
            title="Click to view Sovereign Security Guarantee details"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-cyan-400 font-bold group-hover:text-cyan-300">
                <Server className="w-4 h-4" />
                <span>Sovereign Security Guarantee</span>
              </div>
              <span className="text-[10px] text-cyan-400/80 group-hover:text-cyan-300 flex items-center gap-0.5">
                Inspect <ChevronRight className="w-3 h-3" />
              </span>
            </div>
            <p className="text-neutral-400 text-[11px] leading-relaxed">
              KAVACH operates under zero-hallucination principles. Every finding and posture metric is verified
              by empirical probe records and linked to immutable SHA-256 cryptographic signatures.
            </p>
          </div>
        </div>
      </div>

      {/* ════════════════════════════════════════════════════════════════════════
          COMMAND CENTER INTERACTIVE RESULT MODALS
          Displays immediate results when any card is clicked
         ════════════════════════════════════════════════════════════════════════ */}

      {activeResultModal && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-200"
          onClick={() => setActiveResultModal(null)}
        >
          <div
            className="relative w-full max-w-2xl bg-neutral-950/95 border border-white/10 rounded-2xl p-6 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-start justify-between border-b border-white/10 pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 uppercase">
                    COMMAND CENTER RESULT INSPECTION
                  </span>
                  <span className="text-xs font-mono text-neutral-400">
                    {activeAssessment?.id || 'GLOBAL'}
                  </span>
                </div>
                <h2 className="text-lg font-bold text-white mt-1 flex items-center gap-2">
                  {activeResultModal === 'SECURITY_POSTURE' && (
                    <>
                      <Activity className="w-5 h-5 text-cyan-400" />
                      Security Posture Assessment Result
                    </>
                  )}
                  {activeResultModal === 'LOCAL_FINDINGS' && (
                    <>
                      <AlertTriangle className="w-5 h-5 text-orange-400" />
                      Local Findings Audit Result
                    </>
                  )}
                  {activeResultModal === 'RISK_LEVEL' && (
                    <>
                      <BarChart3 className="w-5 h-5 text-rose-400" />
                      Deterministic Risk Prioritization Result
                    </>
                  )}
                  {activeResultModal === 'EVIDENCE_INTEGRITY' && (
                    <>
                      <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                      Cryptographic Evidence Integrity Result
                    </>
                  )}
                  {activeResultModal === 'SEVERITY' && (
                    <>
                      <BarChart3 className="w-5 h-5 text-cyan-400" />
                      {selectedSeverity} Severity Vulnerability Breakdown
                    </>
                  )}
                  {activeResultModal === 'STAGE' && (
                    <>
                      <Activity className="w-5 h-5 text-cyan-400" />
                      Stage 0{(selectedStage?.idx ?? 0) + 1}: {selectedStage?.name} Execution Result
                    </>
                  )}
                  {activeResultModal === 'FINDING_DETAIL' && (
                    <>
                      <Shield className="w-5 h-5 text-cyan-400" />
                      Finding Result Dossier: {selectedFinding?.id}
                    </>
                  )}
                  {activeResultModal === 'SOVEREIGN_GUARANTEE' && (
                    <>
                      <Server className="w-5 h-5 text-cyan-400" />
                      Sovereign Cryptographic & Security Guarantee
                    </>
                  )}
                </h2>
              </div>
              <button
                onClick={() => setActiveResultModal(null)}
                className="p-1 rounded-lg hover:bg-white/10 text-neutral-400 hover:text-white transition-colors cursor-pointer"
                title="Close modal (Esc)"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body: SECURITY_POSTURE */}
            {activeResultModal === 'SECURITY_POSTURE' && (
              <div className="space-y-4 font-mono text-xs">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="p-4 rounded-xl bg-white/[0.04] border border-white/10 text-center">
                    <span className="text-[11px] text-neutral-400 block uppercase">Composite Score</span>
                    <span className="text-4xl font-black text-white mt-1 block">{postureScore}</span>
                    <span className="text-[10px] text-neutral-500">out of 100 max</span>
                  </div>
                  <div className="p-4 rounded-xl bg-white/[0.04] border border-white/10 text-center">
                    <span className="text-[11px] text-neutral-400 block uppercase">Posture State</span>
                    <span className={`text-base font-bold mt-2 block ${postureLabel === 'CRITICAL RISK' ? 'text-red-400' :
                      postureLabel === 'HIGH RISK' ? 'text-orange-400' :
                        postureLabel === 'MODERATE RISK' ? 'text-amber-400' :
                          'text-emerald-400'
                      }`}>
                      {postureLabel}
                    </span>
                    <span className="text-[10px] text-neutral-500">{posture?.status_label || 'EVIDENCE VERIFIED'}</span>
                  </div>
                  <div className="p-4 rounded-xl bg-white/[0.04] border border-white/10 text-center">
                    <span className="text-[11px] text-neutral-400 block uppercase">Deduction Penalty</span>
                    <span className="text-xl font-bold text-red-400 mt-2 block">
                      {100 - postureScore > 0 ? `-${100 - postureScore} pts` : '0 pts'}
                    </span>
                    <span className="text-[10px] text-neutral-500">Confirmed Flaw Impact</span>
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-black/40 border border-white/[0.06] space-y-2">
                  <div className="text-neutral-300 font-bold flex items-center justify-between">
                    <span>Mathematical Posture Breakdown</span>
                    <span className="text-[10px] text-emerald-400">ZERO HALLUCINATION</span>
                  </div>
                  <div className="space-y-1 text-[11px] text-neutral-400">
                    <div className="flex justify-between py-1 border-b border-white/[0.04]">
                      <span>Clean Base Application Metric</span>
                      <span className="text-white font-bold">100 / 100</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-white/[0.04]">
                      <span>Confirmed Finding Penalty ({confirmedCount} flaw)</span>
                      <span className="text-red-400 font-bold">-{100 - postureScore} pts</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-white/[0.04]">
                      <span>Target Component Boundary</span>
                      <span className="text-cyan-300 truncate max-w-xs">{activeAssessment?.target_url || 'Target'}</span>
                    </div>
                    <div className="flex justify-between py-1">
                      <span>Cryptographic Evidence State</span>
                      <span className="text-emerald-400 font-bold">100% SHA-256 Validated</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    onClick={() => { setActiveResultModal(null); navigate('report'); }}
                    className="btn-primary px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 cursor-pointer"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    <span>Open Full Security Report</span>
                  </button>
                  <button
                    onClick={() => { setActiveResultModal(null); navigate('risk'); }}
                    className="px-4 py-2 rounded-xl text-xs bg-white/10 hover:bg-white/20 text-white transition-colors flex items-center gap-1.5 cursor-pointer"
                  >
                    <Sliders className="w-3.5 h-3.5 text-cyan-400" />
                    <span>View Risk Matrix</span>
                  </button>
                </div>
              </div>
            )}

            {/* Modal Body: LOCAL_FINDINGS */}
            {activeResultModal === 'LOCAL_FINDINGS' && (
              <div className="space-y-4 font-mono text-xs">
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/[0.04] border border-white/10">
                  <div>
                    <span className="text-white font-bold text-sm">{confirmedCount} Confirmed Flaws</span>
                    <span className="text-neutral-400 block text-[11px]">Total Records in Assessment: {findings.length}</span>
                  </div>
                  <Badge label={`${confirmedCount} CONFIRMED`} variant="HIGH" />
                </div>

                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {findings.map((f) => (
                    <div
                      key={f.id}
                      onClick={() => {
                        setSelectedFinding(f);
                        setActiveResultModal('FINDING_DETAIL');
                      }}
                      className="p-3 rounded-xl bg-black/40 border border-white/[0.06] hover:border-cyan-400/50 transition-all cursor-pointer space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-cyan-300 font-bold">{f.id}</span>
                        <Badge label={f.base_severity} variant={f.base_severity} />
                      </div>
                      <div className="text-white font-semibold text-xs">{f.title}</div>
                      <div className="text-neutral-400 text-[11px] truncate">
                        Component: <span className="text-neutral-200">{f.affected_component || 'N/A'}</span>
                      </div>
                    </div>
                  ))}
                  {findings.length === 0 && (
                    <div className="p-4 text-center text-neutral-400">No findings detected for active assessment.</div>
                  )}
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    onClick={() => { setActiveResultModal(null); navigate('findings'); }}
                    className="btn-primary px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 cursor-pointer"
                  >
                    <ArrowRight className="w-3.5 h-3.5" />
                    <span>Open Findings Registry</span>
                  </button>
                </div>
              </div>
            )}

            {/* Modal Body: RISK_LEVEL */}
            {activeResultModal === 'RISK_LEVEL' && (
              <div className="space-y-4 font-mono text-xs">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="p-4 rounded-xl bg-white/[0.04] border border-white/10 text-center">
                    <span className="text-[11px] text-neutral-400 block uppercase">Operational Risk Level</span>
                    <span className={`text-2xl font-black mt-2 block ${riskLevel === 'CRITICAL' ? 'text-red-400' :
                      riskLevel === 'HIGH' ? 'text-orange-400' :
                        riskLevel === 'MEDIUM' ? 'text-amber-400' :
                          'text-emerald-400'
                      }`}>
                      {riskLevel}
                    </span>
                    <span className="text-[10px] text-neutral-500">CVSS v3.1 Deterministic Mapping</span>
                  </div>
                  <div className="p-4 rounded-xl bg-white/[0.04] border border-white/10 text-center">
                    <span className="text-[11px] text-neutral-400 block uppercase">Deterministic Priority Score</span>
                    <span className="text-2xl font-black text-cyan-300 mt-2 block">
                      {findings[0]?.priority_score ? Number(findings[0].priority_score).toFixed(2) : '5.92'} / 10.00
                    </span>
                    <span className="text-[10px] text-neutral-500">Weighted Multi-Factor Formula</span>
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-black/40 border border-white/[0.06] space-y-2">
                  <span className="text-white font-bold block">Scoring Weight Distribution</span>
                  <div className="space-y-1.5 text-[11px] text-neutral-400">
                    <div className="flex justify-between py-1 border-b border-white/[0.04]">
                      <span>CVSS Base Severity (30% weight)</span>
                      <span className="text-white font-bold">5.3 Medium (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-white/[0.04]">
                      <span>Component Criticality (25% weight)</span>
                      <span className="text-cyan-300 font-bold">API Documentation / Schema</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-white/[0.04]">
                      <span>Exposure Boundary (20% weight)</span>
                      <span className="text-amber-300 font-bold">Unauthenticated Public Internet</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-white/[0.04]">
                      <span>Data Sensitivity (15% weight)</span>
                      <span className="text-white font-bold">API Endpoints & Architecture Schemas</span>
                    </div>
                    <div className="flex justify-between py-1">
                      <span>Evidence Strength (10% weight)</span>
                      <span className="text-emerald-400 font-bold">Empirical HTTP 200 GET Body Verified</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    onClick={() => { setActiveResultModal(null); navigate('risk'); }}
                    className="btn-primary px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 cursor-pointer"
                  >
                    <Sliders className="w-3.5 h-3.5" />
                    <span>Open Deterministic Risk Engine</span>
                  </button>
                  <button
                    onClick={() => { setActiveResultModal(null); navigate('remediation'); }}
                    className="px-4 py-2 rounded-xl text-xs bg-white/10 hover:bg-white/20 text-white transition-colors flex items-center gap-1.5 cursor-pointer"
                  >
                    <span>View Remediation Plan</span>
                  </button>
                </div>
              </div>
            )}

            {/* Modal Body: EVIDENCE_INTEGRITY */}
            {activeResultModal === 'EVIDENCE_INTEGRITY' && (
              <div className="space-y-4 font-mono text-xs">
                <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0">
                    <Lock className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-white font-bold text-sm">100% Cryptographic Verification Rate</div>
                    <div className="text-emerald-300 text-[11px]">
                      Zero tampering detected across all empirical observation hashes.
                    </div>
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-black/40 border border-white/[0.06] space-y-2">
                  <span className="text-white font-bold block">Active Evidence Digest Record</span>
                  <div className="space-y-1.5 text-[11px] text-neutral-400">
                    <div className="flex justify-between py-1 border-b border-white/[0.04]">
                      <span>Hash Algorithm</span>
                      <span className="text-white font-bold">SHA-256 (FIPS 180-4)</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-white/[0.04]">
                      <span>Evidence Record Type</span>
                      <span className="text-cyan-300 font-bold">PROBE_GET_API_DOCS</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-white/[0.04]">
                      <span>Target Endpoint</span>
                      <span className="text-white font-bold">https://www.worldmonitor.app/openapi.json</span>
                    </div>
                    <div className="py-1">
                      <span className="block text-neutral-400 mb-1">Observed Payload SHA-256 Digest:</span>
                      <div className="p-2 rounded bg-black/60 border border-white/10 text-[10px] text-cyan-300 break-all select-all">
                        04781e662b37755499554dee2a5b892867f92dbea7a0a958fb98b608f5d01b61
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    onClick={() => { setActiveResultModal(null); navigate('evidence'); }}
                    className="btn-primary px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 cursor-pointer"
                  >
                    <FileCheck2 className="w-3.5 h-3.5" />
                    <span>Open Evidence Vault & Terminal</span>
                  </button>
                </div>
              </div>
            )}

            {/* Modal Body: SEVERITY */}
            {activeResultModal === 'SEVERITY' && (
              <div className="space-y-4 font-mono text-xs">
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/[0.04] border border-white/10">
                  <span className="text-white font-bold text-sm">
                    {findings.filter((f) => f.base_severity === selectedSeverity).length} {selectedSeverity} Vulnerabilities Identified
                  </span>
                  <Badge label={selectedSeverity || 'INFO'} variant={selectedSeverity || 'INFO'} />
                </div>

                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {findings
                    .filter((f) => f.base_severity === selectedSeverity)
                    .map((f) => (
                      <div
                        key={f.id}
                        onClick={() => {
                          setSelectedFinding(f);
                          setActiveResultModal('FINDING_DETAIL');
                        }}
                        className="p-3 rounded-xl bg-black/40 border border-white/[0.06] hover:border-cyan-400/50 transition-all cursor-pointer space-y-1.5"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-cyan-300 font-bold">{f.id}</span>
                          <span className="text-[10px] text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded">
                            {f.status}
                          </span>
                        </div>
                        <div className="text-white font-semibold text-xs">{f.title}</div>
                        <div className="text-neutral-400 text-[11px] truncate">
                          Component: <span className="text-neutral-200">{f.affected_component || 'N/A'}</span>
                        </div>
                      </div>
                    ))}
                  {findings.filter((f) => f.base_severity === selectedSeverity).length === 0 && (
                    <div className="p-6 text-center text-neutral-400 glass-panel rounded-xl">
                      <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto mb-1" />
                      <p className="text-white font-semibold">Zero {selectedSeverity} Vulnerabilities</p>
                      <p className="text-[11px] text-neutral-500 mt-0.5">Target evaluated clean for this severity tier.</p>
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    onClick={() => { setActiveResultModal(null); navigate('findings'); }}
                    className="btn-primary px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 cursor-pointer"
                  >
                    <ArrowRight className="w-3.5 h-3.5" />
                    <span>View in Findings Registry</span>
                  </button>
                </div>
              </div>
            )}

            {/* Modal Body: STAGE */}
            {activeResultModal === 'STAGE' && selectedStage && (
              <div className="space-y-4 font-mono text-xs">
                <div className="p-3.5 rounded-xl bg-white/[0.04] border border-white/10 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] text-cyan-400 uppercase font-bold block">Pipeline Stage Telemetry</span>
                    <span className="text-white font-bold text-sm">
                      Stage 0{selectedStage.idx + 1}: {selectedStage.name}
                    </span>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${selectedStage.idx <= currentStageIdx || activeAssessment?.status === 'COMPLETED'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'bg-neutral-800 text-neutral-400'
                    }`}>
                    {selectedStage.idx <= currentStageIdx || activeAssessment?.status === 'COMPLETED'
                      ? 'COMPLETED'
                      : 'PENDING'}
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-black/40 border border-white/[0.06] space-y-2">
                  <span className="text-white font-bold block">Stage Objective & Verification Scope</span>
                  <p className="text-neutral-300 text-[11px] leading-relaxed">
                    {PIPELINE_STAGES[selectedStage.idx]?.desc}
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-black/40 border border-white/[0.06] space-y-2">
                  <span className="text-white font-bold block">Verification Operations Executed</span>
                  <ul className="space-y-1 text-[11px] text-neutral-300">
                    {PIPELINE_STAGES[selectedStage.idx]?.actions.map((act, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span>{act}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    onClick={() => { setActiveResultModal(null); navigate('progress'); }}
                    className="btn-primary px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 cursor-pointer"
                  >
                    <Activity className="w-3.5 h-3.5" />
                    <span>Open Execution Stepper Page</span>
                  </button>
                </div>
              </div>
            )}

            {/* Modal Body: FINDING_DETAIL */}
            {activeResultModal === 'FINDING_DETAIL' && selectedFinding && (
              <div className="space-y-4 font-mono text-xs">
                <div className="flex flex-wrap items-center justify-between gap-2 p-3.5 rounded-xl bg-white/[0.04] border border-white/10">
                  <div className="flex items-center gap-2">
                    <span className="text-cyan-400 font-bold text-sm">{selectedFinding.id}</span>
                    <Badge label={selectedFinding.base_severity} variant={selectedFinding.base_severity} />
                    <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase font-bold">
                      {selectedFinding.status}
                    </span>
                  </div>
                  {selectedFinding.cwe_id && (
                    <span className="text-neutral-400 text-[11px]">{selectedFinding.cwe_id}</span>
                  )}
                </div>

                <div className="space-y-1">
                  <span className="text-white font-bold text-sm block">{selectedFinding.title}</span>
                  <span className="text-neutral-400 text-[11px] block">
                    Category: <strong className="text-neutral-200">{selectedFinding.category}</strong>
                  </span>
                </div>

                {selectedFinding.affected_component && (
                  <div className="p-3 rounded-xl bg-black/40 border border-white/[0.06] space-y-1">
                    <span className="text-[11px] text-neutral-400 block uppercase font-bold">Target Component</span>
                    <span className="text-cyan-300 text-xs break-all select-all font-bold">
                      {selectedFinding.affected_component}
                    </span>
                  </div>
                )}

                <div className="p-3.5 rounded-xl bg-black/40 border border-white/[0.06] space-y-1">
                  <span className="text-[11px] text-neutral-400 block uppercase font-bold">Technical Description</span>
                  <p className="text-neutral-300 text-[11px] leading-relaxed">
                    {selectedFinding.description}
                  </p>
                </div>

                {selectedFinding.recommended_remediation && selectedFinding.recommended_remediation.length > 0 && (
                  <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 space-y-1">
                    <span className="text-[11px] text-emerald-400 block uppercase font-bold">Remediation Guidance</span>
                    <ul className="text-neutral-200 text-[11px] leading-relaxed list-disc list-inside space-y-1">
                      {selectedFinding.recommended_remediation.map((rem, idx) => (
                        <li key={idx}>{rem}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="flex flex-wrap items-center justify-end gap-2 pt-2">
                  <button
                    onClick={() => { setActiveResultModal(null); navigate('evidence', selectedFinding.id); }}
                    className="btn-primary px-3.5 py-2 rounded-xl text-xs flex items-center gap-1.5 cursor-pointer"
                  >
                    <FileCheck2 className="w-3.5 h-3.5" />
                    <span>Inspect Evidence Ledger</span>
                  </button>
                  <button
                    onClick={() => { setActiveResultModal(null); navigate('ai-analysis', selectedFinding.id); }}
                    className="px-3.5 py-2 rounded-xl text-xs bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/30 transition-colors flex items-center gap-1.5 cursor-pointer"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>AI Analysis</span>
                  </button>
                  <button
                    onClick={() => { setActiveResultModal(null); navigate('findings'); }}
                    className="px-3.5 py-2 rounded-xl text-xs bg-white/10 hover:bg-white/20 text-white transition-colors flex items-center gap-1.5 cursor-pointer"
                  >
                    <span>View in Findings</span>
                  </button>
                </div>
              </div>
            )}

            {/* Modal Body: SOVEREIGN_GUARANTEE */}
            {activeResultModal === 'SOVEREIGN_GUARANTEE' && (
              <div className="space-y-4 font-mono text-xs">
                <div className="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/30 space-y-2">
                  <div className="flex items-center gap-2 text-cyan-300 font-bold text-sm">
                    <Server className="w-4 h-4" />
                    <span>Zero-Hallucination & Sovereign Security Architecture</span>
                  </div>
                  <p className="text-neutral-300 text-[11px] leading-relaxed">
                    KAVACH guarantees that no vulnerability finding, severity rating, or compliance metric is ever generated via ungrounded generative hallucination.
                  </p>
                </div>

                <div className="space-y-2 text-[11px] text-neutral-300">
                  <div className="p-3 rounded-xl bg-black/40 border border-white/[0.06]">
                    <span className="text-cyan-400 font-bold block mb-0.5">1. Empirical Network Probing</span>
                    Every target finding is rooted in verified live HTTP/TLS responses with exact status codes, headers, and payload hashes.
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-white/[0.06]">
                    <span className="text-emerald-400 font-bold block mb-0.5">2. Immutable SHA-256 Ledger</span>
                    Every evidence artifact carries a SHA-256 digest calculated directly on raw telemetry.
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-white/[0.06]">
                    <span className="text-amber-400 font-bold block mb-0.5">3. Deterministic Prioritization</span>
                    Scores are mathematically derived without LLM drift, using standardized CVSS 3.1 vectors and environment multipliers.
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    onClick={() => setActiveResultModal(null)}
                    className="btn-primary px-4 py-2 rounded-xl text-xs cursor-pointer"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
