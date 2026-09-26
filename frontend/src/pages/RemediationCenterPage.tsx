import React, { useState, useEffect } from 'react';
import { Wrench, CheckCircle2, ShieldCheck, Code, Copy, Check, ArrowRight } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { Finding, RemediationPlan } from '../types';

export const RemediationCenterPage: React.FC = () => {
  const { activeAssessment, selectedFindingId, setSelectedFindingId, navigate, showToast } = useApp();
  const [findings, setFindings] = useState<Finding[]>([]);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [plan, setPlan] = useState<RemediationPlan | null>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeAssessment) return;
    setLoading(true);
    api.getFindings({ assessment_id: activeAssessment.id })
      .then((data) => {
        setFindings(data);
        const target = data.find(f => f.id === selectedFindingId) || data[0];
        if (target) {
          setSelectedFinding(target);
          setSelectedFindingId(target.id);
          return api.getRemediation(target.id);
        }
        return null;
      })
      .then((remPlan) => {
        setPlan(remPlan);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [activeAssessment, selectedFindingId]);

  const handleSelectFinding = (f: Finding) => {
    setSelectedFinding(f);
    setSelectedFindingId(f.id);
    api.getRemediation(f.id).then(setPlan).catch(() => setPlan(null));
  };

  const handleCopyCode = () => {
    if (!plan?.code_sample) return;
    navigator.clipboard.writeText(plan.code_sample);
    setCopied(true);
    showToast('info', 'Code Copied', 'Secure remediation snippet copied to clipboard.');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
            <Wrench className="w-5 h-5 text-emerald-400" />
            <span>Remediation & Defense Center</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Actionable developer remediation blueprints: Quick Fixes &bull; Architectural Hardening &bull; Verification Procedures.
          </p>
        </div>

        <div className="flex items-center space-x-2 font-mono-code text-xs">
          <span className="text-slate-400">Total Playbooks:</span>
          <span className="text-emerald-400 font-bold">{findings.length} findings</span>
        </div>
      </div>

      {/* Main Split: Finding Selector vs Remediation Plan */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Finding Selector */}
        <div className="space-y-3">
          <div className="text-xs font-mono-code text-slate-400 uppercase font-bold tracking-wide">
            Select Finding Playbook ({findings.length})
          </div>
          <div className="space-y-2 max-h-[550px] overflow-y-auto pr-1">
            {findings.map((f) => {
              const isSelected = selectedFinding?.id === f.id;
              return (
                <div
                  key={f.id}
                  onClick={() => handleSelectFinding(f)}
                  className={`p-3 rounded-lg border cursor-pointer font-mono-code text-xs transition-all ${
                    isSelected
                      ? 'bg-emerald-500/20 border-emerald-400 text-emerald-200 shadow-[0_0_12px_rgba(16,185,129,0.2)] font-bold'
                      : 'bg-slate-900/70 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-cyan-400">{f.id}</span>
                    <Badge label={f.base_severity} type="severity" size="sm" />
                  </div>
                  <div className="text-slate-200 font-semibold truncate">{f.title}</div>
                  <div className="text-[10px] text-slate-500 mt-1 truncate">{f.affected_component}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Remediation Blueprint */}
        <div className="lg:col-span-2 space-y-4">
          {plan ? (
            <>
              {/* Finding Header Card */}
              <GlassCard glow="green">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2 font-mono-code text-xs mb-1">
                      <span className="text-cyan-400 font-bold">[{plan.finding_id}]</span>
                      <span className="text-slate-300 font-semibold">{plan.affected_component}</span>
                    </div>
                    <h2 className="text-base font-bold text-slate-100">{plan.title}</h2>
                  </div>
                  <Badge label={plan.priority} type="severity" />
                </div>

                <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 font-mono-code text-xs">
                  <div className="p-2.5 rounded bg-slate-900/70 border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Vulnerability Defect</div>
                    <div className="text-slate-300 mt-0.5">{plan.problem}</div>
                  </div>
                  <div className="p-2.5 rounded bg-slate-900/70 border border-slate-800">
                    <div className="text-[10px] text-slate-500 uppercase">Operational Threat</div>
                    <div className="text-rose-300 mt-0.5">{plan.impact}</div>
                  </div>
                </div>
              </GlassCard>

              {/* Quick Fix Blueprint */}
              <GlassCard title="Quick Fix Implementation" subtitle="Immediate stopgap mitigation" glow="green">
                <div className="p-3.5 rounded-lg bg-emerald-950/20 border border-emerald-500/30 text-emerald-300 font-mono-code text-xs leading-relaxed">
                  {plan.quick_fix}
                </div>
              </GlassCard>

              {/* Detailed Architectural Fix */}
              <GlassCard title="Detailed Architectural Hardening" subtitle="Comprehensive remediation steps">
                <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 font-mono-code text-xs whitespace-pre-wrap leading-relaxed">
                  {plan.detailed_fix}
                </pre>
              </GlassCard>

              {/* Code Sample / Patch Snippet */}
              <GlassCard
                title="Secure Code Implementation"
                subtitle="Production-ready defensive code pattern"
                action={
                  <button
                    onClick={handleCopyCode}
                    className="flex items-center space-x-1.5 px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 font-mono-code text-xs transition-colors"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied' : 'Copy Code'}</span>
                  </button>
                }
              >
                <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-emerald-300 font-mono-code text-xs overflow-x-auto leading-relaxed whitespace-pre-wrap">
                  {plan.code_sample}
                </pre>
              </GlassCard>

              {/* Prevention & Verification */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono-code text-xs">
                <GlassCard title="Regression Prevention" subtitle="CI/CD testing policies">
                  <p className="text-slate-300 text-xs leading-relaxed">
                    {plan.prevention}
                  </p>
                </GlassCard>

                <GlassCard title="Verification Procedure" subtitle="Confirming patch efficacy">
                  <p className="text-cyan-300 text-xs leading-relaxed">
                    {plan.verification}
                  </p>
                </GlassCard>
              </div>
            </>
          ) : (
            <div className="text-center py-20 glass-panel rounded-xl font-mono-code text-xs text-slate-400">
              Select a finding playbook to inspect remediation blueprints.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
