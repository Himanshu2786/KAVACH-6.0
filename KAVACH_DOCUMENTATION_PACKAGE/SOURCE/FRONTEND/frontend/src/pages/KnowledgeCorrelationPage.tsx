import React, { useState, useEffect } from 'react';
import { GitFork, ArrowRight, Shield, Layers, BookOpen, Search } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { KnowledgeRecord, Finding } from '../types';

export const KnowledgeCorrelationPage: React.FC = () => {
  const { activeAssessment, navigate } = useApp();
  const [knowledgeList, setKnowledgeList] = useState<KnowledgeRecord[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [selectedItem, setSelectedItem] = useState<KnowledgeRecord | null>(null);
  const [search, setSearch] = useState('');
  const [activeType, setActiveType] = useState<'ALL' | 'CWE' | 'OWASP'>('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getKnowledge().catch(() => []),
      activeAssessment ? api.getFindings({ assessment_id: activeAssessment.id }).catch(() => []) : Promise.resolve([])
    ]).then(([knowData, findData]) => {
      setKnowledgeList(knowData);
      setFindings(findData);
      if (knowData.length > 0) setSelectedItem(knowData[0]);
      setLoading(false);
    });
  }, [activeAssessment]);

  const filteredKnowledge = knowledgeList.filter((k) => {
    const matchesSearch = k.id.toLowerCase().includes(search.toLowerCase()) ||
      k.title.toLowerCase().includes(search.toLowerCase()) ||
      k.category.toLowerCase().includes(search.toLowerCase());
    const matchesType = activeType === 'ALL' || k.type === activeType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
          <GitFork className="w-5 h-5 text-cyan-400" />
          <span>Knowledge Correlation Engine</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Local authoritative cybersecurity taxonomy linking Findings &rarr; CWE &rarr; OWASP Top 10 &rarr; Remediation Guidance.
        </p>
      </div>

      {/* Visual Relationship Flow Banner */}
      <GlassCard title="Taxonomy Correlation Pipeline" subtitle="Offline Grounding Layer for AI Reasoning">
        <div className="flex items-center justify-between overflow-x-auto py-2 font-mono-code text-xs">
          <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 text-center shrink-0 min-w-[130px]">
            <div className="text-[10px] text-slate-500 uppercase">Input Surface</div>
            <div className="font-bold text-slate-200 mt-0.5">Raw Finding</div>
          </div>
          <ArrowRight className="w-4 h-4 text-cyan-500 shrink-0 mx-2" />
          <div className="p-3 rounded-lg bg-cyan-950/40 border border-cyan-500/40 text-center shrink-0 min-w-[130px]">
            <div className="text-[10px] text-cyan-400 uppercase">CWE Weakness</div>
            <div className="font-bold text-cyan-300 mt-0.5">Defect Class</div>
          </div>
          <ArrowRight className="w-4 h-4 text-cyan-500 shrink-0 mx-2" />
          <div className="p-3 rounded-lg bg-purple-950/40 border border-purple-500/40 text-center shrink-0 min-w-[130px]">
            <div className="text-[10px] text-purple-400 uppercase">OWASP Category</div>
            <div className="font-bold text-purple-300 mt-0.5">Standard Risk</div>
          </div>
          <ArrowRight className="w-4 h-4 text-cyan-500 shrink-0 mx-2" />
          <div className="p-3 rounded-lg bg-emerald-950/40 border border-emerald-500/40 text-center shrink-0 min-w-[130px]">
            <div className="text-[10px] text-emerald-400 uppercase">Hardening</div>
            <div className="font-bold text-emerald-300 mt-0.5">Actionable Fix</div>
          </div>
        </div>
      </GlassCard>

      {/* Main Split: Records Directory vs Detail View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Knowledge Directory */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2 font-mono-code text-xs">
            {(['ALL', 'CWE', 'OWASP'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setActiveType(t)}
                className={`px-3 py-1.5 rounded-lg border transition-all ${
                  activeType === t
                    ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 font-bold'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search taxonomy records..."
              className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-900/90 border border-slate-700 focus:border-cyan-400 text-slate-100 text-xs font-mono-code outline-none transition-colors"
            />
          </div>

          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
            {filteredKnowledge.map((k) => (
              <div
                key={k.id}
                onClick={() => setSelectedItem(k)}
                className={`p-3 rounded-lg border cursor-pointer font-mono-code text-xs transition-all ${
                  selectedItem?.id === k.id
                    ? 'bg-cyan-500/15 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.15)] font-bold'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-cyan-400">{k.id}</span>
                  <span className="text-[10px] text-slate-500 uppercase">{k.type}</span>
                </div>
                <div className="text-slate-200 font-semibold truncate">{k.title}</div>
                <div className="text-[10px] text-slate-400 mt-1 truncate">{k.category}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Detail Inspection Card */}
        <div className="lg:col-span-2">
          {selectedItem ? (
            <GlassCard
              title={`${selectedItem.id} — ${selectedItem.title}`}
              subtitle={selectedItem.category}
              icon={<BookOpen className="w-5 h-5 text-cyan-400" />}
              className="space-y-4"
            >
              <div>
                <div className="text-[11px] font-mono-code text-slate-400 uppercase mb-1">Standard Description</div>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3.5 rounded-lg border border-slate-800 font-mono-code">
                  {selectedItem.description}
                </p>
              </div>

              {selectedItem.related_owasp && (
                <div>
                  <div className="text-[11px] font-mono-code text-slate-400 uppercase mb-1">Cross-Standard Mapping</div>
                  <div className="p-2.5 rounded bg-slate-900/80 border border-slate-800 text-xs font-mono-code text-purple-300">
                    {selectedItem.related_owasp}
                  </div>
                </div>
              )}

              <div>
                <div className="text-[11px] font-mono-code text-slate-400 uppercase mb-1">Remediation Guidelines</div>
                <div className="space-y-2">
                  {selectedItem.remediation?.map((r, idx) => (
                    <div key={idx} className="p-2.5 rounded bg-emerald-950/20 border border-emerald-500/20 text-emerald-300 font-mono-code text-xs flex items-start space-x-2">
                      <span className="font-bold text-emerald-400 shrink-0">&check;</span>
                      <span>{r}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Associated Active Assessment Findings */}
              <div className="pt-3 border-t border-slate-800/80">
                <div className="text-[11px] font-mono-code text-slate-400 uppercase mb-2">
                  Associated Active Assessment Findings
                </div>
                <div className="space-y-2">
                  {findings.filter(f => f.cwe_id === selectedItem.id || f.owasp_category === selectedItem.id).map(f => (
                    <div
                      key={f.id}
                      onClick={() => navigate('finding-detail', f.id)}
                      className="p-2 rounded bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-xs font-mono-code flex items-center justify-between cursor-pointer transition-colors"
                    >
                      <span className="text-cyan-400 font-bold">{f.id} &bull; {f.title}</span>
                      <Badge label={f.status} type="status" size="sm" />
                    </div>
                  ))}
                  {findings.filter(f => f.cwe_id === selectedItem.id || f.owasp_category === selectedItem.id).length === 0 && (
                    <div className="text-[11px] font-mono-code text-slate-500 italic">
                      No current findings mapped to this record.
                    </div>
                  )}
                </div>
              </div>
            </GlassCard>
          ) : (
            <div className="text-center py-20 glass-panel rounded-xl font-mono-code text-xs text-slate-400">
              Select a taxonomy record from the directory to inspect mapping details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
