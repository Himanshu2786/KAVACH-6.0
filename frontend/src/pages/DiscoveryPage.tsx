import React, { useState, useEffect } from 'react';
import { Compass, Filter, Shield, Key, Database, Globe, UserCheck, Layers, Server } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { DiscoveryItem } from '../types';

export const DiscoveryPage: React.FC = () => {
  const { activeAssessment, isDemoMode } = useApp();
  const [items, setItems] = useState<DiscoveryItem[]>([]);
  const [activeTab, setActiveTab] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeAssessment) return;
    setLoading(true);
    api.getDiscoveryItems(activeAssessment.id)
      .then((data) => {
        setItems(data);
        setLoading(false);
      })
      .catch(() => {
        setItems([]);
        setLoading(false);
      });
  }, [activeAssessment]);

  const tabs = [
    { id: 'all', label: 'All Cataloged Surfaces', count: items.length },
    { id: 'endpoint', label: 'Discovered Endpoints', count: items.filter(i => i.item_type === 'endpoint').length },
    { id: 'component', label: 'Architecture Components', count: items.filter(i => i.item_type === 'component').length },
    { id: 'auth_point', label: 'Authentication Points', count: items.filter(i => i.item_type === 'auth_point').length },
    { id: 'input_surface', label: 'Input Surfaces', count: items.filter(i => i.item_type === 'input_surface').length },
    { id: 'api_surface', label: 'API Surfaces', count: items.filter(i => i.item_type === 'api_surface').length },
    { id: 'user_role', label: 'User Roles & RBAC', count: items.filter(i => i.item_type === 'user_role').length },
  ];

  const filteredItems = activeTab === 'all' ? items : items.filter(i => i.item_type === activeTab);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
            <Compass className="w-5 h-5 text-cyan-400" />
            <span>Target Discovery Inventory</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Automated reconnaissance and catalog of target attack surfaces, endpoints, and exposed interfaces.
          </p>
        </div>

        <div className="flex items-center space-x-2 font-mono-code text-xs">
          <span className="text-slate-400">Mode:</span>
          <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
            {isDemoMode ? 'SIMULATED DISCOVERY' : 'LIVE PROBE DISCOVERY'}
          </span>
        </div>
      </div>

      {/* Target Overview Card */}
      <GlassCard title="Target Scope & Environment Profile">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 font-mono-code text-xs">
          <div className="p-3 rounded-lg bg-slate-900/70 border border-slate-800">
            <div className="text-[10px] text-slate-400 uppercase">Target Identity</div>
            <div className="font-bold text-slate-100 mt-0.5 truncate">{activeAssessment?.name || 'World Monitor'}</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/70 border border-slate-800">
            <div className="text-[10px] text-slate-400 uppercase">Target Base URL</div>
            <div className="font-bold text-cyan-400 mt-0.5 truncate">{activeAssessment?.target_url || 'http://localhost'}</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/70 border border-slate-800">
            <div className="text-[10px] text-slate-400 uppercase">Environment Type</div>
            <div className="font-bold text-slate-200 mt-0.5">{activeAssessment?.environment || 'Testing'}</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/70 border border-slate-800">
            <div className="text-[10px] text-slate-400 uppercase">Total Cataloged</div>
            <div className="font-bold text-emerald-400 mt-0.5">{items.length} surfaces</div>
          </div>
        </div>
      </GlassCard>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 font-mono-code text-xs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-1.5 rounded-lg border whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.15)] font-bold'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
            }`}
          >
            {tab.label} ({tab.count})
          </button>
        ))}
      </div>

      {/* Surfaces Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredItems.map((it) => {
          const typeIcons: Record<string, any> = {
            endpoint: Globe,
            component: Server,
            auth_point: Key,
            input_surface: Layers,
            api_surface: Database,
            user_role: UserCheck
          };
          const Icon = typeIcons[it.item_type] || Globe;

          return (
            <GlassCard key={it.id} className="flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2 truncate pr-2">
                    <div className="p-1.5 rounded bg-slate-800 border border-slate-700 text-cyan-400">
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="font-bold text-xs text-slate-100 font-mono-code truncate">
                      {it.name}
                    </span>
                  </div>
                  <Badge label={it.security_relevance} type="severity" size="sm" />
                </div>

                <div className="font-mono-code text-xs text-cyan-300 mb-2 truncate">
                  {it.method && <span className="font-bold text-slate-300 mr-2">[{it.method}]</span>}
                  <span>{it.path}</span>
                </div>

                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  {it.details}
                </p>
              </div>

              <div className="pt-2.5 border-t border-slate-800/80 flex items-center justify-between font-mono-code text-[10px] text-slate-500">
                <span className="uppercase">{it.item_type.replace('_', ' ')}</span>
                <span>{it.id}</span>
              </div>
            </GlassCard>
          );
        })}
      </div>
    </div>
  );
};
