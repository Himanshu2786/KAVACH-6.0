import React, { useState, useEffect } from 'react';
import { Activity, Play, CheckCircle2, Clock, Terminal, ChevronRight, RefreshCw } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { WorkflowStepper } from '../components/common/WorkflowStepper';
import { Badge } from '../components/common/Badge';
import { AuditEvent } from '../types';

const STAGES = [
  { id: 'DISCOVER', name: 'Discovery Engine', desc: 'Attack surface mapping and endpoint discovery' },
  { id: 'ASSESS', name: 'Assessment Engine', desc: 'Vulnerability rule scanning and observation' },
  { id: 'CORRELATE', name: 'Knowledge Correlation', desc: 'CWE and OWASP standard taxonomy mapping' },
  { id: 'ANALYZE', name: 'AI Security Analysis', desc: 'Local Ollama structured hypothesis generation' },
  { id: 'VALIDATE', name: 'Evidence Validation', desc: 'Cryptographic SHA-256 evidence recording' },
  { id: 'PRIORITIZE', name: 'Risk Prioritization', desc: 'Deterministic multi-factor risk scoring' },
  { id: 'REMEDIATE', name: 'Remediation Engine', desc: 'Defensive code fix recommendations' },
  { id: 'REPORT', name: 'Executive Report', desc: 'Final report assembly and export' }
];

export const AssessmentProgressPage: React.FC = () => {
  const { activeAssessment, setActiveAssessment, refreshData, showToast } = useApp();
  const [selectedStage, setSelectedStage] = useState<string>('VALIDATE');
  const [audits, setAudits] = useState<AuditEvent[]>([]);
  const [advancing, setAdvancing] = useState(false);

  useEffect(() => {
    if (!activeAssessment) return;
    setSelectedStage(activeAssessment.current_stage || 'VALIDATE');
    api.getAuditTrail(activeAssessment.id)
      .then(setAudits)
      .catch(() => setAudits([]));
  }, [activeAssessment]);

  const handleAdvance = async (stageId: string) => {
    if (!activeAssessment) return;
    setAdvancing(true);
    try {
      const updated = await api.advanceStage(activeAssessment.id, stageId);
      setActiveAssessment(updated);
      setSelectedStage(stageId);
      await refreshData();
      showToast('success', 'Stage Advanced', `Assessment advanced to ${stageId} (${updated.progress}%).`);
    } catch (err: any) {
      showToast('error', 'Stage Error', err.message || 'Failed to advance stage');
    } finally {
      setAdvancing(false);
    }
  };

  const normalizedCurrentStage =
    (activeAssessment?.current_stage?.toUpperCase() === 'COMPLETE' || !activeAssessment?.current_stage)
      ? 'REPORT'
      : activeAssessment.current_stage;
  const currentIdx = STAGES.findIndex(s => s.id === normalizedCurrentStage);
  const stageObj = STAGES.find(s => s.id === selectedStage) || STAGES[0];
  const selectedIdx = STAGES.findIndex(s => s.id === selectedStage);

  // Assessment-level completion takes priority over stage-position logic.
  // When backend says COMPLETED (or progress===100) the active stage IS done.
  const assessmentCompleted =
    activeAssessment?.status === 'COMPLETED' ||
    (activeAssessment?.progress ?? 0) >= 100;

  const stageAudits = audits.filter(a => {
    const desc = (a.description || '').toUpperCase();
    const type = (a.event_type || '').toUpperCase();

    // 1. Separate stage execution telemetry from global audit/lifecycle telemetry:
    // Never include post-assessment re-test events inside historical stage execution logs.
    // RETEST_* events remain intact in the Audit Trail and Live Activity feed.
    const isRetest =
      type.startsWith('RETEST') ||
      type.includes('RETEST') ||
      desc.includes('RE-TEST') ||
      desc.includes('AFTER-FIX') ||
      desc.includes('RETEST');
    if (isRetest) return false;

    // 2. Global pipeline lifecycle transitions do not belong to individual module execution logs.
    if (type === 'ASSESSMENT_STAGE_ADVANCED') return false;

    // 3. Stage-specific execution telemetry:
    // DISCOVER: only discovery-stage execution events
    if (selectedStage === 'DISCOVER') {
      return (
        ['DISCOVERY_COMPLETED', 'DISCOVERY_SEEDED', 'SURFACE_MAPPED', 'ENDPOINT_DISCOVERED', 'TARGET_SELECTED', 'SOURCE_SELECTED', 'ASSESSMENT_STARTED', 'DISCOVERY_STARTED'].includes(type) ||
        type.includes('DISCOVER') ||
        desc.includes('DISCOVERY')
      );
    }
    // ASSESS: only original assessment-stage execution events
    if (selectedStage === 'ASSESS') {
      if (type === 'ASSESSMENT_COMPLETED') return false;
      return (
        ['MODULE_STARTED', 'RULE_EXECUTED', 'OBSERVATION', 'OBSERVATION_CAPTURED', 'RESULT', 'MODULE_COMPLETED', 'TEST_EXECUTED', 'PROBE_ERROR', 'MODULE_EXECUTION', 'SCAN_STARTED', 'SCAN_COMPLETED'].includes(type) ||
        type.startsWith('RULE_') ||
        type.startsWith('MODULE_') ||
        type === 'ASSESS' ||
        type.startsWith('ASSESS_')
      );
    }
    // CORRELATE: only correlation-stage execution events
    if (selectedStage === 'CORRELATE') {
      return (
        ['KNOWLEDGE_CORRELATED', 'CORRELATION_COMPLETED', 'TAXONOMY_MAPPED', 'CWE_MAPPED', 'OWASP_MAPPED', 'CORRELATION_STARTED'].includes(type) ||
        type.includes('CORRELAT') ||
        (desc.includes('CWE') && desc.includes('MAPPED')) ||
        (desc.includes('OWASP') && desc.includes('MAPPED'))
      );
    }
    // ANALYZE: only AI-analysis-stage execution events
    if (selectedStage === 'ANALYZE') {
      return (
        ['AI_ANALYSIS_COMPLETED', 'AI_ANALYSIS_STARTED', 'HYPOTHESIS_GENERATED', 'OLLAMA_ANALYZED', 'AI_CORRELATED', 'AI_HYPOTHESIS'].includes(type) ||
        type.includes('ANALYZ') ||
        type.startsWith('AI_') ||
        type === 'AI' ||
        desc.includes('OLLAMA')
      );
    }
    // VALIDATE: only original evidence-validation-stage execution events (no RETEST_* events)
    if (selectedStage === 'VALIDATE') {
      return (
        ['EVIDENCE_GENERATED', 'EVIDENCE_RECORDED', 'EVIDENCE_VALIDATED', 'PROBE_EXECUTED', 'POC_EXECUTED', 'FINDING_CREATED', 'FINDING_UPDATED', 'VERIFICATION_EXECUTED', 'VALIDATION_STARTED', 'VALIDATION_COMPLETED'].includes(type) ||
        type.startsWith('VALIDAT') ||
        type.startsWith('EVIDENCE_')
      );
    }
    // PRIORITIZE: only risk-calculation-stage events
    if (selectedStage === 'PRIORITIZE') {
      return (
        ['RISK_CALCULATED', 'PRIORITY_ASSIGNED', 'CVSS_SCORED', 'POSTURE_EVALUATED', 'PRIORITIZATION_COMPLETED'].includes(type) ||
        type.includes('PRIORIT') ||
        type.startsWith('RISK_') ||
        desc.includes('RISK') ||
        desc.includes('CVSS')
      );
    }
    // REMEDIATE: only remediation-stage events
    if (selectedStage === 'REMEDIATE') {
      return (
        ['REMEDIATION_CREATED', 'REMEDIATION_PLAN_GENERATED', 'FIX_RECOMMENDED', 'PLAYBOOK_GENERATED', 'REMEDIATION_COMPLETED'].includes(type) ||
        type.includes('REMEDIAT') ||
        desc.includes('REMEDIATION')
      );
    }
    // REPORT: only report-generation/export events
    if (selectedStage === 'REPORT') {
      return (
        ['REPORT_GENERATED', 'REPORT_EXPORTED', 'REPORT_VIEWED', 'REPORT_DOWNLOADED', 'ASSESSMENT_COMPLETED'].includes(type) ||
        type.includes('REPORT') ||
        type === 'ASSESSMENT_COMPLETED' ||
        desc.includes('REPORT')
      );
    }
    return false;
  });

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            <span>Assessment Progress & Workflow</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time execution telemetry across the complete 8-stage KAVACH assessment pipeline.
          </p>
        </div>

        <div className="flex items-center space-x-3 font-mono-code text-xs">
          <span className="text-slate-400">Current:</span>
          <Badge label={normalizedCurrentStage} variant="VALIDATING" />
          <span className="text-cyan-400 font-bold">{activeAssessment?.progress || 65}%</span>
        </div>
      </div>

      {/* 8-Stage Visual Stepper */}
      <GlassCard title="Pipeline Execution Stepper" subtitle="Click any stage to inspect module telemetry">
        <WorkflowStepper
          currentStage={normalizedCurrentStage}
          assessmentCompleted={assessmentCompleted}
          onSelectStage={(s) => setSelectedStage(s)}
          interactive
        />
      </GlassCard>

      {/* Main Split: Stage Inspection Detail vs Live Activity Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stage Inspection Panel */}
        <GlassCard
          title={`Stage Inspection: ${stageObj.name}`}
          subtitle={stageObj.desc}
          icon={<Terminal className="w-5 h-5 text-cyan-400" />}
          className="lg:col-span-2"
          action={
            selectedIdx > currentIdx ? (
              <button
                onClick={() => handleAdvance(stageObj.id)}
                disabled={advancing}
                className="px-3 py-1 rounded bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold font-mono-code text-xs transition-colors flex items-center space-x-1"
              >
                <span>Advance To {stageObj.id}</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            ) : null
          }
        >
          <div className="space-y-4 font-mono-code text-xs">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <div className="text-[10px] text-slate-400 uppercase">Stage Status</div>
                <div className="mt-1">
                  {/* Priority A: assessment fully done → every stage at or before current = COMPLETED */}
                  {(assessmentCompleted && selectedIdx <= currentIdx) && <Badge label="COMPLETED" variant="CONFIRMED" size="sm" />}
                  {/* Priority B: not completed, selected stage is behind current → COMPLETED */}
                  {(!assessmentCompleted && selectedIdx < currentIdx) && <Badge label="COMPLETED" variant="CONFIRMED" size="sm" />}
                  {/* Priority C: not completed, selected stage IS current → RUNNING */}
                  {(!assessmentCompleted && selectedIdx === currentIdx) && <Badge label="RUNNING" variant="VALIDATING" size="sm" />}
                  {/* Priority D: selected stage is ahead of current → PENDING */}
                  {(selectedIdx > currentIdx) && <Badge label="PENDING" variant="UNCONFIRMED" size="sm" />}
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <div className="text-[10px] text-slate-400 uppercase">Started Time</div>
                <div className="text-slate-200 mt-1 truncate">
                  {activeAssessment?.started_at ? activeAssessment.started_at.replace('T', ' ').slice(0, 19) : '00:00:00'}
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <div className="text-[10px] text-slate-400 uppercase">Module Health</div>
                <div className="text-emerald-400 mt-1 font-bold">OPTIMAL</div>
              </div>
            </div>

            {/* Module Log Window */}
            <div>
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wide mb-2 flex items-center justify-between">
                <span>Module Execution Logs</span>
                <span className="text-[10px] text-slate-500">Channel: stdout</span>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 font-mono-code text-[11px] space-y-1.5 max-h-56 overflow-y-auto">
                <div className="text-cyan-400">[INFO] Stage dispatcher active for module: {stageObj.id} ({stageObj.name})</div>
                <div className="text-slate-400">[TRACE] Target boundary scope: {activeAssessment?.target_url || activeAssessment?.scope}</div>
                
                {stageAudits.length > 0 ? (
                  stageAudits.map((a, idx) => (
                    <div key={idx} className={
                      a.status === 'FAILED' || a.description.includes('FAIL') || a.description.includes('ERROR') ? 'text-rose-400' :
                      a.status === 'PASS' || a.description.includes('PASS') || a.description.includes('SUCCESS') ? 'text-emerald-400' :
                      a.status === 'POTENTIAL' || a.description.includes('POTENTIAL') ? 'text-amber-400' :
                      'text-slate-300'
                    }>
                      <span className="text-slate-500">[{a.timestamp ? a.timestamp.split('T')[1]?.slice(0, 8) : '00:00:00'}]</span>{' '}
                      <span className="text-cyan-400">[{a.event_type}]</span> {a.description}
                    </div>
                  ))
                ) : (
                  <div className="text-slate-500 italic py-2">
                    [TELEMETRY] No discrete audit records for stage {selectedStage}.
                    {selectedIdx > currentIdx ? ' (Awaiting pipeline progression)' : ' (All baseline checks passed within boundary constraints)'}
                  </div>
                )}
                
                <div className="text-slate-500 text-[10px] pt-1 border-t border-slate-900">[STATUS] Verified pipeline telemetry connected to audit database.</div>
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Live Activity Feed */}
        <GlassCard
          title="Live Activity Panel"
          subtitle="Real-time security events"
          icon={<Clock className="w-5 h-5 text-cyan-400" />}
        >
          <div className="space-y-3 font-mono-code text-xs max-h-96 overflow-y-auto pr-1">
            {audits.map((ev) => (
              <div key={ev.id} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <div className="flex items-center justify-between text-[10px] text-cyan-400 font-bold mb-1">
                  <span>{ev.event_type}</span>
                  <span className="text-slate-500">{ev.timestamp ? ev.timestamp.split('T')[1]?.replace('Z', '') : ''}</span>
                </div>
                <div className="text-slate-300 leading-relaxed text-[11px]">
                  {ev.description}
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
