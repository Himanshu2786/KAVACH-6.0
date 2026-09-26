import React, { useState } from 'react';
import { Terminal, Copy, Check, X, ShieldCheck, CheckCircle2, AlertTriangle, Hash } from 'lucide-react';
import { TerminalVerification } from '../../types';

interface TechnicalTerminalViewerProps {
  isOpen: boolean;
  data: TerminalVerification | null;
  onClose: () => void;
}

export const TechnicalTerminalViewer: React.FC<TechnicalTerminalViewerProps> = ({
  isOpen,
  data,
  onClose
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !data) return null;

  const handleCopy = () => {
    if (!data.command) return;
    navigator.clipboard.writeText(data.command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl glass-level-4 border border-white/[0.15] shadow-2xl overflow-hidden font-mono text-xs">
        
        {/* Header Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/[0.08] bg-white/[0.03]">
          <div className="flex items-center space-x-3">
            <div className="p-1.5 rounded-lg bg-white/[0.06] border border-white/[0.1] text-white">
              <Terminal className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-white tracking-tight">TECHNICAL VERIFICATION</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/[0.08] text-neutral-300 border border-white/[0.1] backdrop-blur-md">
                  ONE EVIDENCE, TWO VIEWS
                </span>
              </div>
              <p className="text-[11px] text-neutral-400 font-sans mt-0.5">
                Direct terminal correlation to evidence record <span className="text-white font-mono">{data.evidence_id}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-white/[0.08] transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Metadata Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-4 rounded-xl glass-level-2 border border-white/[0.08]">
            <div>
              <span className="text-neutral-500 text-[10px] uppercase block mb-1">Assessment</span>
              <span className="text-neutral-200 font-medium">{data.assessment_id}</span>
            </div>
            <div>
              <span className="text-neutral-500 text-[10px] uppercase block mb-1">Evidence ID</span>
              <span className="text-emerald-400 font-medium">{data.evidence_id}</span>
            </div>
            <div>
              <span className="text-neutral-500 text-[10px] uppercase block mb-1">Target Host</span>
              <span className="text-neutral-200 truncate block">{data.target}</span>
            </div>
            <div>
              <span className="text-neutral-500 text-[10px] uppercase block mb-1">Status</span>
              <span className="text-amber-400 font-medium">{data.status}</span>
            </div>
          </div>

          {/* Verification Steps */}
          <div className="p-4 rounded-xl glass-level-2 border border-white/[0.06]">
            <div className="text-neutral-400 text-[11px] font-semibold uppercase tracking-wider mb-2.5">
              Verification Steps
            </div>
            <div className="space-y-1.5 text-neutral-300">
              {data.verification_steps.map((step, idx) => (
                <div key={idx} className="flex items-start space-x-2 text-[11px]">
                  <span className="text-neutral-500 select-none">STEP {idx + 1}:</span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Run Command Card */}
          <div className="rounded-xl border border-white/[0.1] glass-terminal overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2.5 bg-white/[0.04] border-b border-white/[0.08] text-[11px] flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <span className="text-neutral-400 font-medium">SAFE REPRODUCIBLE POWERSHELL PROCEDURE</span>
                <span className="px-2 py-0.5 rounded-full bg-blue-500/15 border border-blue-500/25 text-blue-300 text-[9px] font-mono">
                  PowerShell / Windows
                </span>
              </div>
              <button
                onClick={handleCopy}
                title="Copy the exact command shown below"
                className="btn-primary flex items-center space-x-1.5 px-3 py-1 text-[11px]"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    <span>COPIED!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>COPY COMMAND</span>
                  </>
                )}
              </button>
            </div>
            {/* Context note */}
            <div className="px-4 pt-2 text-[10px] font-mono text-neutral-500">
              Run from the <span className="text-neutral-300">KAVACH project root</span>:
              <span className="ml-2 text-neutral-400">PS C:\path\to\KAVACH&gt;</span>
            </div>
            <div className="p-4 overflow-x-auto text-emerald-300 text-xs select-all">
              <code>{data.command}</code>
            </div>
            {/* HOW TO VERIFY */}
            <div className="px-4 pb-4 border-t border-white/[0.06] pt-3 space-y-2">
              <div className="text-[10px] font-mono text-neutral-500 uppercase tracking-wider">How to Verify</div>
              <ol className="text-[11px] font-mono text-neutral-400 space-y-1">
                {[
                  'Open PowerShell (Start → search "PowerShell").',
                  'Navigate to the KAVACH project root: cd "C:\\path\\to\\KAVACH 6.0"',
                  'Paste the command above and press Enter.',
                  'Compare the returned output with OBSERVED RESULT shown below.',
                  'If the output matches, the observation is independently reproducible.',
                  'If output differs (e.g. fixture modified), the command reflects the actual current state of the file.',
                ].map((step, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-neutral-600 flex-shrink-0">{i + 1}.</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
              <p className="text-[10px] font-mono text-neutral-500 pt-1 border-t border-white/[0.04]">
                ⚠ Displaying this command does <span className="text-neutral-300">not</span> automatically mark the finding as verified.
                Verification is complete only when you execute the command and confirm the output independently.
              </p>
            </div>
          </div>

          {/* Expected vs Observed Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* Expected Result */}
            <div className="rounded-xl border border-white/[0.08] glass-level-2 overflow-hidden flex flex-col">
              <div className="px-4 py-2.5 bg-emerald-950/25 border-b border-white/[0.06] text-emerald-400 font-medium text-[11px] flex items-center space-x-2">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>EXPECTED RESULT (BASELINE)</span>
              </div>
              <pre className="p-4 flex-1 text-neutral-300 text-[11px] overflow-x-auto whitespace-pre-wrap leading-relaxed">
                {data.expected_output}
              </pre>
            </div>

            {/* Observed Result */}
            <div className="rounded-xl border border-white/[0.08] glass-level-2 overflow-hidden flex flex-col">
              <div className="px-4 py-2.5 bg-rose-950/25 border-b border-white/[0.06] text-rose-400 font-medium text-[11px] flex items-center space-x-2">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>OBSERVED RESULT (KAVACH PROBE)</span>
              </div>
              <pre className="p-4 flex-1 text-neutral-300 text-[11px] overflow-x-auto whitespace-pre-wrap leading-relaxed">
                {data.observed_output}
              </pre>
            </div>
          </div>

          {/* Cryptographic Proof Footer */}
          <div className="p-4 rounded-xl glass-level-2 border border-white/[0.08] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-[11px]">
            <div className="flex items-center space-x-2">
              <Hash className="w-4 h-4 text-neutral-500" />
              <span className="text-neutral-500">SHA-256 HASH:</span>
              <span className="text-neutral-300 font-mono text-[10px] break-all">{data.integrity_hash}</span>
            </div>
            <div className="flex items-center space-x-1.5 text-neutral-400 font-semibold shrink-0 text-[10px] font-mono">
              <ShieldCheck className="w-4 h-4 text-neutral-500" />
              <span>Awaiting independent verification</span>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-white/[0.08] bg-white/[0.02] flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 text-neutral-400 text-[11px]">
          <span className="text-center sm:text-left">Non-destructive test command matches the raw evidence payload verbatim.</span>
          <button
            onClick={onClose}
            className="btn-secondary px-4 py-1.5 text-xs justify-center shrink-0"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
