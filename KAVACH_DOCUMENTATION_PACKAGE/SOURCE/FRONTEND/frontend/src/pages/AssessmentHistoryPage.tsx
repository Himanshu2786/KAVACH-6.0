import React, { useState, useEffect } from 'react';
import { History, ArrowRight, ShieldCheck, Clock, PlusCircle } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { Assessment } from '../types';

export const AssessmentHistoryPage: React.FC = () => {
  const { assessments, activeAssessment, setActiveAssessment, navigate, refreshData } = useApp();
  const [list, setList] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getAssessments()
      .then((data) => {
        setList(data);
        setLoading(false);
      })
      .catch(() => {
        setList(assessments);
        setLoading(false);
      });
  }, [assessments]);

  const handleSelectAssessment = (asm: Assessment) => {
    setActiveAssessment(asm);
    navigate('command-center');
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
            <History className="w-5 h-5 text-cyan-400" />
            <span>Assessment Audit History</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Historical registry of executed security assessments, verified evidence trails, and posture trends.
          </p>
        </div>

        <button
          onClick={() => navigate('new-assessment')}
          className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold font-mono-code text-xs uppercase tracking-wider flex items-center space-x-2 shadow-[0_0_15px_rgba(6,182,212,0.25)] transition-all"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          <span>New Assessment</span>
        </button>
      </div>

      {/* History Grid */}
      <div className="space-y-3">
        {list.map((asm) => {
          const isActive = activeAssessment?.id === asm.id;
          return (
            <div
              key={asm.id}
              onClick={() => handleSelectAssessment(asm)}
              className={`glass-panel p-5 rounded-xl border transition-all duration-200 cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                isActive
                  ? 'border-cyan-400/80 bg-slate-800/60 shadow-[0_0_20px_rgba(6,182,212,0.15)]'
                  : 'border-slate-800 hover:border-slate-700 hover:bg-slate-800/30'
              }`}
            >
              <div className="space-y-1.5 flex-1 min-w-0">
                <div className="flex items-center space-x-2.5">
                  <span className="text-xs font-mono-code font-bold text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800">
                    {asm.id}
                  </span>
                  <span className="text-sm font-bold text-slate-100 truncate">
                    {asm.name}
                  </span>
                  <span className={`text-[10px] font-mono-code px-2 py-0.5 rounded font-bold uppercase ${
                    asm.is_demo 
                      ? 'bg-amber-950/80 text-amber-400 border border-amber-800/60'
                      : 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60'
                  }`}>
                    {asm.is_demo ? 'DEMO' : 'REAL'}
                  </span>
                  {isActive && (
                    <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-cyan-500 text-slate-950 font-bold">
                      ACTIVE
                    </span>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 font-mono-code text-xs text-slate-400">
                  <span>Target: <strong className="text-slate-300">{asm.target_url}</strong></span>
                  <span>&bull;</span>
                  <span>Environment: <span className="text-slate-300">{asm.environment}</span></span>
                  <span>&bull;</span>
                  <span>Scope: <span className="text-slate-300">{asm.scope}</span></span>
                </div>
              </div>

              <div className="flex items-center space-x-4 shrink-0 font-mono-code text-xs">
                <div className="text-right">
                  <div className="text-[10px] text-slate-500 uppercase">Status</div>
                  <div className={`font-bold text-xs ${asm.status === 'COMPLETED' ? 'text-emerald-400' : 'text-cyan-400'}`}>
                    {asm.status}
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-[10px] text-slate-500 uppercase">Findings</div>
                  <div className="text-slate-200 font-bold">
                    <span className="text-emerald-400">{asm.confirmed_findings ?? 0} confirmed</span> / {asm.total_findings ?? 0} total
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-[10px] text-slate-500 uppercase">Stage</div>
                  <Badge label={asm.current_stage || 'REPORT'} variant="VALIDATING" size="sm" />
                </div>

                <div className="p-2 rounded-lg bg-slate-800 text-cyan-400 hover:bg-cyan-500 hover:text-slate-950 transition-colors">
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            </div>
          );
        })}

        {list.length === 0 && (
          <div className="text-center py-16 glass-panel rounded-xl font-mono-code text-xs text-slate-400">
            No previous assessments found in local database.
          </div>
        )}
      </div>
    </div>
  );
};
