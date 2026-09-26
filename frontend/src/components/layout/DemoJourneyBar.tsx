import React from 'react';
import { PlayCircle, ChevronRight, ChevronLeft, Sparkles } from 'lucide-react';
import { useApp } from '../../context/AppContext';

interface JourneyStep {
  title: string;
  page: string;
  findingId?: string;
  tip: string;
}

const JOURNEY_STEPS: JourneyStep[] = [
  {
    title: '1. Command Center',
    page: 'command-center',
    tip: 'Show overall security posture, deterministic risk distribution, and system status.'
  },
  {
    title: '2. System Health',
    page: 'system-status',
    tip: 'Show real health of Backend, Ollama URL/model, and Knowledge Engine records to judges.'
  },
  {
    title: '3. Scope Guard',
    page: 'new-assessment',
    tip: 'Highlight mandatory authorization confirmation guard and modular assessment toggles.'
  },
  {
    title: '4. Discovery',
    page: 'discovery',
    tip: 'Demonstrate cataloged attack surfaces: endpoints, auth gateways, and input fields.'
  },
  {
    title: '5. 8-Stage Stepper',
    page: 'progress',
    tip: 'Walk judges through the complete lifecycle: DISCOVER -> REPORT.'
  },
  {
    title: '6. Findings Matrix',
    page: 'findings',
    tip: 'Show findings with state badges: POTENTIAL vs UNDER ANALYSIS vs CONFIRMED.'
  },
  {
    title: '7. AI Analysis',
    page: 'ai-analysis',
    findingId: 'KAV-2026-004',
    tip: 'CRITICAL DEMO: Emphasize that AI confidence != vulnerability confirmation!'
  },
  {
    title: '8. Knowledge Graph',
    page: 'knowledge',
    tip: 'Display local offline CWE and OWASP Top 10 mappings.'
  },
  {
    title: '9. Evidence Validation',
    page: 'evidence',
    findingId: 'KAV-2026-004',
    tip: 'HERO FEATURE: Run safe probe. Show cryptographic SHA-256 hash and status transition.'
  },
  {
    title: '10. Risk Scoring',
    page: 'risk',
    tip: 'Show deterministic multi-factor calculation and "Why This Is Prioritized" breakdown.'
  },
  {
    title: '11. Report Export',
    page: 'report',
    tip: 'Generate executive security intelligence report with printable HTML view.'
  }
];

export const DemoJourneyBar: React.FC = () => {
  const { presentationStep, setPresentationStep, navigate, isDemoMode } = useApp();
  const current = JOURNEY_STEPS[presentationStep] || JOURNEY_STEPS[0];

  const handleStep = (index: number) => {
    setPresentationStep(index);
    const target = JOURNEY_STEPS[index];
    const targetFindingId = isDemoMode ? target.findingId : undefined;
    navigate(target.page, targetFindingId);
  };

  const handleNext = () => {
    if (presentationStep < JOURNEY_STEPS.length - 1) {
      handleStep(presentationStep + 1);
    }
  };

  const handlePrev = () => {
    if (presentationStep > 0) {
      handleStep(presentationStep - 1);
    }
  };

  return (
    <div className="glass-level-1 rounded-lg border border-white/[0.08] p-2.5 flex flex-col gap-2 font-mono text-xs shadow-lg">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center space-x-2 min-w-0">
          <div className="flex items-center space-x-1 px-2 py-0.5 rounded bg-white/[0.08] border border-white/10 text-white font-semibold flex-shrink-0">
            <Sparkles className="w-3.5 h-3.5 text-neutral-300" />
            <span className="tracking-wider text-[10px]">DEMO</span>
          </div>
          <div className="text-neutral-200 font-medium text-xs truncate">
            Step {presentationStep + 1}/{JOURNEY_STEPS.length}:{' '}
            <span className="text-white font-semibold">{current.title}</span>
          </div>
        </div>

        <div className="flex items-center space-x-1.5 flex-shrink-0">
          <button
            onClick={handlePrev}
            disabled={presentationStep === 0}
            className="btn-secondary px-2 py-1 text-xs disabled:opacity-30 disabled:cursor-not-allowed flex items-center space-x-0.5 cursor-pointer"
            title="Previous step"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Prev</span>
          </button>

          <button
            onClick={handleNext}
            disabled={presentationStep === JOURNEY_STEPS.length - 1}
            className="btn-primary px-2.5 py-1 text-xs font-semibold disabled:opacity-30 disabled:cursor-not-allowed flex items-center space-x-0.5 cursor-pointer"
            title="Next step"
          >
            <span>Next</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="text-neutral-400 text-[11px] leading-relaxed bg-black/40 border border-white/[0.04] rounded px-2.5 py-1.5 text-left break-words">
        <span className="text-neutral-300 font-semibold">Tip: </span>
        {current.tip}
      </div>
    </div>
  );
};
