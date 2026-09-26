import React, { useState } from 'react';
import { ShieldAlert, CheckSquare, Square, X, ArrowRight, Lock } from 'lucide-react';

interface AuthorizationModalProps {
  isOpen: boolean;
  targetUrl: string;
  onConfirm: (url: string) => void;
  onClose: () => void;
}

export const AuthorizationModal: React.FC<AuthorizationModalProps> = ({
  isOpen,
  targetUrl,
  onConfirm,
  onClose
}) => {
  const [ownsOrAuthorized, setOwnsOrAuthorized] = useState(false);
  const [understandsScope, setUnderstandsScope] = useState(false);

  if (!isOpen) return null;

  const canProceed = ownsOrAuthorized && understandsScope;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg rounded-2xl glass-level-4 border border-white/[0.15] p-6 md:p-8 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-neutral-400 hover:text-white transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 rounded-xl bg-white/[0.06] border border-white/10 text-white backdrop-blur-md">
            <Lock className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-bold tracking-wide text-white">AUTHORIZATION REQUIRED</h3>
            <p className="text-xs text-neutral-400">Legal Compliance & Security Scope Verification</p>
          </div>
        </div>

        <div className="p-3 rounded-xl glass-level-2 border border-white/[0.08] text-xs font-mono text-cyan-300 break-all mb-6">
          <span className="text-neutral-500 select-none">Target URL: </span>
          {targetUrl || 'https://example.com'}
        </div>

        <p className="text-sm text-neutral-300 leading-relaxed mb-6">
          KAVACH performs authorized technical security assessments using non-destructive empirical probing. 
          To protect systems and adhere to cybersecurity legal frameworks, you must explicitly confirm your authorization before scanning can commence.
        </p>

        <div className="space-y-4 mb-8">
          <div
            onClick={() => setOwnsOrAuthorized(!ownsOrAuthorized)}
            className={`flex items-start space-x-3 p-3.5 rounded-xl border cursor-pointer transition-all ${
              ownsOrAuthorized
                ? 'bg-cyan-500/10 border-cyan-500/40 text-white shadow-[0_0_16px_rgba(6,182,212,0.1)]'
                : 'glass-level-2 border-white/[0.08] text-neutral-400 hover:border-white/20'
            }`}
          >
            {ownsOrAuthorized ? (
              <CheckSquare className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
            ) : (
              <Square className="w-5 h-5 text-neutral-500 shrink-0 mt-0.5" />
            )}
            <span className="text-xs font-medium leading-relaxed select-none">
              I own this application <strong className="text-cyan-300">OR</strong> I have explicit authorization to assess this target from its owner.
            </span>
          </div>

          <div
            onClick={() => setUnderstandsScope(!understandsScope)}
            className={`flex items-start space-x-3 p-3.5 rounded-xl border cursor-pointer transition-all ${
              understandsScope
                ? 'bg-cyan-500/10 border-cyan-500/40 text-white shadow-[0_0_16px_rgba(6,182,212,0.1)]'
                : 'glass-level-2 border-white/[0.08] text-neutral-400 hover:border-white/20'
            }`}
          >
            {understandsScope ? (
              <CheckSquare className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
            ) : (
              <Square className="w-5 h-5 text-neutral-500 shrink-0 mt-0.5" />
            )}
            <span className="text-xs font-medium leading-relaxed select-none">
              I understand that KAVACH must only be used on authorized systems within agreed testing boundaries.
            </span>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary px-5 py-2.5 text-xs font-semibold justify-center"
          >
            CANCEL
          </button>
          <button
            type="button"
            disabled={!canProceed}
            onClick={() => onConfirm(targetUrl)}
            className={`btn-primary px-6 py-2.5 text-xs font-semibold flex items-center justify-center space-x-2 ${
              !canProceed ? 'opacity-40 cursor-not-allowed' : ''
            }`}
          >
            <span>CONFIRM & SCAN</span>
            <ArrowRight className="w-4 h-4 flex-shrink-0" />
          </button>
        </div>
      </div>
    </div>
  );
};
