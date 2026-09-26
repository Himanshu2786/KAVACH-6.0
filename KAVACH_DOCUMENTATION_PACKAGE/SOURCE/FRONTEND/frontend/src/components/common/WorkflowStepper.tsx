import React from 'react';
import { Check, ArrowRight } from 'lucide-react';

const STAGES = [
  'DISCOVER',
  'ASSESS',
  'CORRELATE',
  'ANALYZE',
  'VALIDATE',
  'PRIORITIZE',
  'REMEDIATE',
  'REPORT'
];

interface WorkflowStepperProps {
  currentStage: string;
  /** Pass true when backend assessment.status === 'COMPLETED' or progress === 100 */
  assessmentCompleted?: boolean;
  onSelectStage?: (stage: string) => void;
  interactive?: boolean;
}

export const WorkflowStepper: React.FC<WorkflowStepperProps> = ({
  currentStage,
  assessmentCompleted = false,
  onSelectStage,
  interactive = false
}) => {
  const normalizedStage = (currentStage || '').toUpperCase() === 'COMPLETE' ? 'REPORT' : (currentStage || '').toUpperCase();
  const currentIndex = STAGES.indexOf(normalizedStage);

  return (
    <div className="w-full overflow-x-auto py-2">
      <div className="flex items-center min-w-max space-x-1.5 px-1">
        {STAGES.map((stage, idx) => {
          // When the assessment is fully completed, treat the current stage
          // as completed too — the whole pipeline is done.
          const isCompleted = assessmentCompleted
            ? currentIndex >= idx          // every stage up to and including current = done
            : currentIndex > idx;
          const isCurrent = !assessmentCompleted && currentIndex === idx;
          const isPending = currentIndex < idx;

          let badgeClasses = 'glass-panel text-neutral-500';
          if (isCompleted) {
            badgeClasses = 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 glass-panel';
          } else if (isCurrent) {
            badgeClasses = 'glass-card-active text-white shadow-[0_0_12px_rgba(255,255,255,0.15)] font-semibold';
          }

          return (
            <React.Fragment key={stage}>
              <div
                onClick={() => interactive && onSelectStage && onSelectStage(stage)}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg border font-mono text-xs transition-all ${badgeClasses} ${
                  interactive ? 'cursor-pointer hover:border-white/40' : ''
                }`}
              >
                <div
                  className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    isCompleted
                      ? 'bg-emerald-400 text-black'
                      : isCurrent
                      ? 'bg-white text-black'
                      : 'bg-white/10 text-neutral-400'
                  }`}
                >
                  {isCompleted ? <Check className="w-2.5 h-2.5" /> : idx + 1}
                </div>
                <span className="tracking-wider">{stage}</span>
              </div>
              {idx < STAGES.length - 1 && (
                <ArrowRight
                  className={`w-3.5 h-3.5 ${
                    isCompleted ? 'text-emerald-500/60' : 'text-neutral-700'
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
