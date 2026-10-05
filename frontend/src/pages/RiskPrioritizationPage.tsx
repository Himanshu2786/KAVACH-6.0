import React, { useState, useEffect } from 'react';
import { Sliders, ArrowRight, ShieldAlert, CheckCircle2, ChevronDown, ChevronUp, Layers, Sparkles } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { RiskItem } from '../types';

export const RiskPrioritizationPage: React.FC = () => {
  const { activeAssessment, navigate } = useApp();
  const [riskItems, setRiskItems] = useState<RiskItem[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeAssessment) return;
    setLoading(true);
    api.getRiskPrioritization(activeAssessment.id)
      .then((data) => {
        setRiskItems(data);
        if (data.length > 0) setExpandedId(data[0].finding_id);
        setLoading(false);
      })
      .catch(() => {
        setRiskItems([]);
        setLoading(false);
      });
  }, [activeAssessment]);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-cyan-400" />
            <span>Deterministic Risk Prioritization Engine</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Deterministic multi-factor risk calculation: Base Severity &bull; Component Criticality &bull; Data Sensitivity &bull; Evidence Strength &bull; Exposure Boundary.
          </p>
        </div>

        <div className="flex items-center space-x-2 font-mono-code text-xs">
          <span className="text-slate-400">Environment Multiplier:</span>
          <span className="text-cyan-400 font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
            {activeAssessment?.environment || 'Testing'} (0.90x)
          </span>
        </div>
      </div>

      {/* Multi-Factor Formula Banner */}
      <GlassCard title="Deterministic Multi-Factor Scoring Formula" subtitle="Rigorous mathematical prioritization without AI hallucinations">
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 font-mono-code text-xs text-center">
          <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="text-[10px] text-cyan-400 font-bold">30% Weight</div>
            <div className="text-slate-200 mt-0.5">Base Severity</div>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="text-[10px] text-cyan-400 font-bold">25% Weight</div>
            <div className="text-slate-200 mt-0.5">Component Criticality</div>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="text-[10px] text-cyan-400 font-bold">20% Weight</div>
            <div className="text-slate-200 mt-0.5">Data Sensitivity</div>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="text-[10px] text-cyan-400 font-bold">15% Weight</div>
            <div className="text-slate-200 mt-0.5">Evidence Strength</div>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 col-span-2 sm:col-span-1">
            <div className="text-[10px] text-cyan-400 font-bold">10% Weight</div>
            <div className="text-slate-200 mt-0.5">Network Exposure</div>
          </div>
        </div>
      </GlassCard>

      {/* Prioritized Findings List */}
      <div className="space-y-4">
        {riskItems.map((item, index) => {
          const isExpanded = expandedId === item.finding_id;
          return (
            <GlassCard
              key={item.finding_id}
              glow={item.calculated_priority === 'CRITICAL' ? 'red' : item.calculated_priority === 'HIGH' ? 'amber' : 'none'}
              className="transition-all"
            >
              {/* Card Header Row */}
              <div
                onClick={() => toggleExpand(item.finding_id)}
                className="flex flex-col md:flex-row md:items-center justify-between gap-4 cursor-pointer"
              >
                <div className="flex items-start space-x-3">
                  <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center font-mono-code text-xs font-bold text-cyan-400 shrink-0">
                    #{index + 1}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2 font-mono-code text-xs mb-1">
                      <span className="font-bold text-cyan-400">{item.finding_id}</span>
                      <span className="text-slate-400 truncate">&bull; {item.affected_component}</span>
                    </div>
                    <div className="text-sm font-bold text-slate-100">{item.title}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-4 font-mono-code text-xs shrink-0">
                  <div className="text-right">
                    <div className="text-[10px] text-slate-400 uppercase">Risk Score</div>
                    <div className="text-base font-black text-cyan-400">{item.priority_score} / 10.0</div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Badge label={item.calculated_priority} type="severity" />
                    <Badge label={item.status} type="status" size="sm" />
                  </div>

                  <button className="text-slate-400 hover:text-slate-200 p-1">
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Collapsible Factor Breakdown */}
              {isExpanded && (
                <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-4 animate-fadeIn font-mono-code text-xs">
                  {/* Summary Statement */}
                  {item.explanation?.summary_statement && (
                    <div className="p-3 rounded-lg bg-slate-900/90 border border-cyan-500/20 text-cyan-300">
                      <strong className="block text-slate-200 uppercase mb-0.5">WHY THIS IS PRIORITIZED:</strong>
                      {item.explanation.summary_statement}
                    </div>
                  )}

                  {/* Factor Matrix */}
                  {item.explanation && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-slate-400 font-bold uppercase">Base Severity (30%)</span>
                          <span className="text-cyan-400 font-bold">{item.explanation.base_severity?.score ?? 0}/10</span>
                        </div>
                        <p className="text-slate-300 text-[11px]">{item.explanation.base_severity?.rationale || 'N/A'}</p>
                      </div>

                      <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-slate-400 font-bold uppercase">Component Criticality (25%)</span>
                          <span className="text-cyan-400 font-bold">{item.explanation.component_criticality?.score ?? 0}/10</span>
                        </div>
                        <p className="text-slate-300 text-[11px]">{item.explanation.component_criticality?.rationale || 'N/A'}</p>
                      </div>

                      <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-slate-400 font-bold uppercase">Data Sensitivity (20%)</span>
                          <span className="text-cyan-400 font-bold">{item.explanation.data_sensitivity?.score ?? 0}/10</span>
                        </div>
                        <p className="text-slate-300 text-[11px]">{item.explanation.data_sensitivity?.rationale || 'N/A'}</p>
                      </div>

                      <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-slate-400 font-bold uppercase">Evidence Strength (15%)</span>
                          <span className="text-emerald-400 font-bold">{item.explanation.evidence_strength?.score ?? 0}/10</span>
                        </div>
                        <p className="text-slate-300 text-[11px]">{item.explanation.evidence_strength?.rationale || 'N/A'}</p>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-end space-x-3 pt-2">
                    <button
                      onClick={() => navigate('finding-detail', item.finding_id)}
                      className="text-cyan-400 hover:text-cyan-300 flex items-center space-x-1"
                    >
                      <span>Inspect Finding Dossier</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )}
            </GlassCard>
          );
        })}
      </div>
    </div>
  );
};
