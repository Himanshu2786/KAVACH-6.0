import React from 'react';
import {
  Shield,
  LayoutDashboard,
  PlusCircle,
  Compass,
  Activity,
  AlertOctagon,
  BrainCircuit,
  FileCheck2,
  Sliders,
  Wrench,
  FileText,
  History,
  Server,
  Settings,
  GitFork,
  Globe
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const Sidebar: React.FC = () => {
  const { activePage, navigate, isDemoMode } = useApp();

  const navItems = [
    // PRIMARY
    { id: 'home', label: 'Home (Landing)', icon: Globe, category: 'Primary' },
    { id: 'command-center', label: 'Command Center', icon: LayoutDashboard, category: 'Primary' },
    { id: 'findings', label: 'Findings Catalog', icon: AlertOctagon, category: 'Primary' },
    { id: 'evidence', label: 'Evidence & Terminal', icon: FileCheck2, category: 'Primary', hero: true },
    { id: 'report', label: 'Compliance Reports', icon: FileText, category: 'Primary' },

    // SECONDARY
    { id: 'new-assessment', label: 'Start New Assessment', icon: PlusCircle, category: 'Assessment Workflow' },
    { id: 'discovery', label: 'Discovery Inventory', icon: Compass, category: 'Assessment Workflow' },
    { id: 'progress', label: 'Live Assessment Stage', icon: Activity, category: 'Assessment Workflow' },
    { id: 'remediation', label: 'Remediation Center', icon: Wrench, category: 'Governance & Fixes' },
    { id: 'risk', label: 'Risk Prioritization', icon: Sliders, category: 'Governance & Fixes' },
    { id: 'knowledge', label: 'Security Guide & CWE', icon: GitFork, category: 'Governance & Fixes' },
    { id: 'history', label: 'Audit History', icon: History, category: 'Governance & Fixes' },

    // ADVANCED / SOC CONTEXT
    { id: 'world-monitor', label: 'World Situational Monitor', icon: Globe, category: 'Advanced / SOC' },
    { id: 'ai-analysis', label: 'AI Evidence Analysis', icon: BrainCircuit, category: 'Advanced / SOC' },
    { id: 'system-status', label: 'SOC Context & Health', icon: Server, category: 'Advanced / SOC' },
    { id: 'settings', label: 'Platform Settings', icon: Settings, category: 'Advanced / SOC' },
  ];

  return (
    <aside className="w-64 shrink-0 glass-level-1 border-r border-white/[0.08] flex flex-col h-screen sticky top-0">
      {/* Brand Header */}
      <div className="p-4 border-b border-white/[0.08] flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-white/[0.06] border border-white/10 text-white shadow-sm">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-1.5">
            <span className="font-bold text-white tracking-wider text-base">KAVACH</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/[0.08] text-neutral-300 border border-white/10">6.0</span>
          </div>
          <div className="text-[10px] text-neutral-400 font-mono uppercase tracking-wider mt-0.5">
            Security Intelligence
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {navItems.map((item, index) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          const prevItem = index > 0 ? navItems[index - 1] : null;
          const showCategoryHeader = !prevItem || prevItem.category !== item.category;

          return (
            <React.Fragment key={item.id}>
              {showCategoryHeader && (
                <div className="text-[10px] font-mono text-neutral-400 uppercase tracking-wider px-3 pt-3 pb-1">
                  {item.category}
                </div>
              )}
              <button
                onClick={() => navigate(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-white/[0.12] text-white border border-white/20 shadow-sm font-semibold'
                    : 'text-neutral-400 hover:text-white hover:bg-white/[0.05]'
                }`}
              >
                <div className="flex items-center space-x-2.5 truncate">
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-neutral-400'}`} />
                  <span className="truncate">{item.label}</span>
                </div>
                {item.hero && (
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-white/[0.1] text-white border border-white/20 font-medium">
                    HERO
                  </span>
                )}
              </button>
            </React.Fragment>
          );
        })}
      </nav>

      {/* Mode Tag & Core Tagline Footer */}
      <div className="p-3 border-t border-white/[0.08] bg-black/40">
        <div className="text-[11px] font-mono text-neutral-300 font-semibold uppercase tracking-wider flex items-center justify-between mb-1">
          <span>{isDemoMode ? 'SIMULATED DEMO' : 'LIVE SCOPE'}</span>
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
        </div>
        <div className="text-[10px] text-neutral-400 italic">
          "AI Hypothesizes. Evidence Confirms."
        </div>
      </div>
    </aside>
  );
};
