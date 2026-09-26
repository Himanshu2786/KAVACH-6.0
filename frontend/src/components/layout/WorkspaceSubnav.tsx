import React from 'react';
import { useApp } from '../../context/AppContext';
import {
  LayoutDashboard,
  AlertOctagon,
  FileCheck2,
  Globe,
  Radio,
  Shield,
  Database,
  ShieldCheck
} from 'lucide-react';

export const WorkspaceSubnav: React.FC = () => {
  const {
    activePage, navigate, activeAssessment,
    urlFindingsCount, urlEvidenceCount,
    urlAssessmentState,
    markUrlFindingsViewed, markUrlEvidenceViewed,
  } = useApp();

  // Glow is "bright" until user visits the page, then "soft" until next scan
  const findingsGlowing = urlFindingsCount > 0 && !urlAssessmentState.findingsViewed;
  const evidenceGlowing = urlEvidenceCount > 0 && !urlAssessmentState.evidenceViewed;

  const workspaceTabs = [
    { id: 'command-center',      label: 'Command Center', icon: LayoutDashboard },
    { id: 'world-monitor',       label: 'World Monitor', icon: Radio },
    { id: 'url-check',           label: 'URL Check',     icon: Globe },
    { id: 'portable-assessment', label: 'Local Posture', icon: Shield },
    {
      id: 'findings', label: 'Findings', icon: AlertOctagon,
      badge: urlFindingsCount > 0 ? urlFindingsCount : 0,
      glowing: findingsGlowing,
      onActivate: markUrlFindingsViewed,
    },
    { id: 'experience-db', label: 'Experience DB', icon: Database },
    { id: 'audit-trail',   label: 'Audit Trail',   icon: ShieldCheck },
    {
      id: 'evidence', label: 'Evidence', icon: FileCheck2,
      badge: urlEvidenceCount > 0 ? urlEvidenceCount : 0,
      glowing: evidenceGlowing,
      onActivate: markUrlEvidenceViewed,
    },
  ] as const;

  return (
    <div className="border-b border-white/[0.06] bg-[#000000]/80 backdrop-blur-md px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto flex items-center justify-between overflow-x-auto py-2 scrollbar-none">
        {/* Scope pill — target URL from URL assessment or backend assessment */}
        <div className="hidden lg:flex items-center space-x-2 mr-4 shrink-0 pr-4 border-r border-white/[0.06]">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          <span
            className="text-[11px] font-mono text-neutral-400 truncate max-w-[220px]"
            title={urlAssessmentState.result?.target_url ?? activeAssessment?.target_url}
          >
            {urlAssessmentState.result?.hostname
              ? urlAssessmentState.result.hostname
              : (activeAssessment?.name || 'No active target')}
          </span>
        </div>

        {/* Tab list */}
        <div className="flex items-center space-x-1 shrink-0">
          {workspaceTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activePage === tab.id;
            // Support narrower type by accessing optional props safely
            const badge = 'badge' in tab ? tab.badge : 0;
            const glowing = 'glowing' in tab ? tab.glowing : false;
            const onActivate = 'onActivate' in tab ? tab.onActivate : undefined;

            return (
              <button
                key={tab.id}
                onClick={() => {
                  navigate(tab.id);
                  onActivate?.();
                }}
                aria-label={`${tab.label}${badge ? ` — ${badge} new results` : ''}`}
                className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-white/[0.1] text-white shadow-sm'
                    : glowing
                    ? 'text-white hover:bg-white/[0.07]'
                    : 'text-neutral-400 hover:text-neutral-200 hover:bg-white/[0.04]'
                }`}
              >
                {/* Glow halo behind the button when new results available */}
                {glowing && (
                  <span
                    className="absolute inset-0 rounded-md pointer-events-none"
                    style={{
                      boxShadow: '0 0 0 1px rgba(255,255,255,0.22), 0 0 12px 0 rgba(255,255,255,0.12)',
                      animation: 'pulse 2.5s ease-in-out infinite',
                    }}
                  />
                )}

                <Icon
                  className={`w-3.5 h-3.5 flex-shrink-0 ${
                    isActive ? 'text-white' : glowing ? 'text-white' : 'text-neutral-500'
                  }`}
                />
                <span>{tab.label}</span>

                {/* Count badge — always visible once results exist, dims after viewing */}
                {badge > 0 && (
                  <span
                    className={`ml-0.5 px-1.5 py-0 rounded-full text-[10px] font-bold font-mono leading-[1.6] transition-all ${
                      glowing
                        ? 'bg-white text-black'
                        : 'bg-white/[0.15] text-neutral-200'
                    }`}
                    aria-hidden="true"
                  >
                    {badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
