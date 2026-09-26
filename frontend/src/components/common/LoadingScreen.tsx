import React, { useState, useEffect } from 'react';
import { Shield, CheckCircle2, AlertTriangle, RefreshCw, Play, Activity } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { api } from '../../services/api';

interface ModuleCheck {
  name: string;
  key: string;
  status: 'pending' | 'loading' | 'ready' | 'offline';
}

export const LoadingScreen: React.FC = () => {
  const { finishBootLoading, ollamaStatus, setIsDemoMode, navigate, refreshData } = useApp();

  const [modules, setModules] = useState<ModuleCheck[]>([
    { name: 'Interface Engine',  key: 'ui',         status: 'loading' },
    { name: 'Assessment Engine', key: 'assessment', status: 'pending' },
    { name: 'Knowledge Engine',  key: 'knowledge',  status: 'pending' },
    { name: 'Evidence Engine',   key: 'evidence',   status: 'pending' },
    { name: 'AI Engine',         key: 'ai',         status: 'pending' },
    { name: 'Ollama Connection', key: 'ollama',     status: 'pending' },
  ]);

  const [bootComplete, setBootComplete]   = useState(false);
  const [showFailsafe, setShowFailsafe]   = useState(false);
  const [visible,      setVisible]        = useState(false);
  const [retrying,     setRetrying]       = useState(false);

  // Fade-in on mount
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 40);
    return () => clearTimeout(t);
  }, []);

  // Auto-recover when Ollama status becomes online
  useEffect(() => {
    if (ollamaStatus?.status === 'online') {
      setModules(prev => prev.map(m => m.key === 'ollama' ? { ...m, status: 'ready' } : m));
      setShowFailsafe(false);
      setBootComplete(true);
      const t = setTimeout(() => finishBootLoading(), 600);
      return () => clearTimeout(t);
    }
  }, [ollamaStatus, finishBootLoading]);

  // Stepped boot sequence
  useEffect(() => {
    const timeouts: ReturnType<typeof setTimeout>[] = [];

    timeouts.push(setTimeout(() => {
      setModules(prev => prev.map(m =>
        m.key === 'ui'         ? { ...m, status: 'ready'   } :
        m.key === 'assessment' ? { ...m, status: 'loading' } : m));
    }, 400));

    timeouts.push(setTimeout(() => {
      setModules(prev => prev.map(m =>
        m.key === 'assessment' ? { ...m, status: 'ready'   } :
        m.key === 'knowledge'  ? { ...m, status: 'loading' } : m));
    }, 800));

    timeouts.push(setTimeout(() => {
      setModules(prev => prev.map(m =>
        m.key === 'knowledge' ? { ...m, status: 'ready'   } :
        m.key === 'evidence'  ? { ...m, status: 'loading' } : m));
    }, 1200));

    timeouts.push(setTimeout(() => {
      setModules(prev => prev.map(m =>
        m.key === 'evidence' ? { ...m, status: 'ready'   } :
        m.key === 'ai'       ? { ...m, status: 'loading' } : m));
    }, 1600));

    timeouts.push(setTimeout(() => {
      setModules(prev => prev.map(m =>
        m.key === 'ai'     ? { ...m, status: 'ready'   } :
        m.key === 'ollama' ? { ...m, status: 'loading' } : m));
    }, 2000));

    timeouts.push(setTimeout(async () => {
      let isOllamaOnline = ollamaStatus?.status === 'online';

      // If ollamaStatus is not yet available, directly verify with the API
      if (!isOllamaOnline) {
        try {
          const direct = await api.getOllamaStatus();
          if (direct?.status === 'online') {
            isOllamaOnline = true;
          }
        } catch {
          // Backend or Ollama truly unreachable
        }
      }

      setModules(prev => prev.map(m =>
        m.key === 'ollama' ? { ...m, status: isOllamaOnline ? 'ready' : 'offline' } : m));
      setBootComplete(true);

      if (!isOllamaOnline) {
        setShowFailsafe(true);
      } else {
        setTimeout(() => finishBootLoading(), 600);
      }
    }, 2400));

    return () => timeouts.forEach(clearTimeout);
  }, []); // Run boot sequence once on mount

  const handleContinueDemo = () => { setIsDemoMode(true); finishBootLoading(); };
  const handleOpenStatus   = () => { finishBootLoading(); navigate('system-status'); };

  const handleRetry = async () => {
    setRetrying(true);
    try {
      const res = await api.getOllamaStatus();
      if (res?.status === 'online') {
        setModules(prev => prev.map(m => m.key === 'ollama' ? { ...m, status: 'ready' } : m));
        setShowFailsafe(false);
        setTimeout(() => finishBootLoading(), 500);
        return;
      }
    } catch {}
    await refreshData();
    setRetrying(false);
  };

  const statusDot = (status: ModuleCheck['status']) => {
    if (status === 'ready')   return <span className="w-1.5 h-1.5 rounded-full bg-[#34d399] flex-shrink-0" />;
    if (status === 'loading') return (
      <span className="w-1.5 h-1.5 rounded-full bg-white/50 flex-shrink-0 animate-pulse" />
    );
    if (status === 'offline') return <span className="w-1.5 h-1.5 rounded-full bg-[#fbbf24] flex-shrink-0" />;
    return <span className="w-1.5 h-1.5 rounded-full bg-white/[0.12] flex-shrink-0" />;
  };

  const statusLabel = (status: ModuleCheck['status']) => {
    if (status === 'ready')   return <span className="text-[#34d399] font-mono text-[10px] tracking-widest">READY</span>;
    if (status === 'loading') return <span className="text-white/60 font-mono text-[10px] tracking-widest animate-pulse">INITIALIZING</span>;
    if (status === 'offline') return <span className="text-[#fbbf24] font-mono text-[10px] tracking-widest">OFFLINE</span>;
    return <span className="text-white/[0.18] font-mono text-[10px] tracking-widest">PENDING</span>;
  };

  return (
    /* Pure Black background #000000 */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#000000]"
      style={{
        backgroundColor: '#000000',
        /* Padding respects phone safe areas */
        paddingTop:    'max(1.5rem, env(safe-area-inset-top))',
        paddingBottom: 'max(1.5rem, env(safe-area-inset-bottom))',
        paddingLeft:   'max(1rem,   env(safe-area-inset-left))',
        paddingRight:  'max(1rem,   env(safe-area-inset-right))',
        opacity: visible ? 1 : 0,
        transition: 'opacity 0.35s ease',
      }}
      aria-live="polite"
      aria-label="KAVACH system initializing"
    >
      {/* ── Boot Card — uses glass-level-3 design token ─────────────────── */}
      <div
        className="w-full"
        style={{ maxWidth: 'min(440px, 100%)' }}
      >
        {/* ── Brand Header — mirrors Navbar logo ──────────────────────────── */}
        <div className="flex items-center space-x-2.5 mb-8">
          {/* Shield icon: same as Navbar: w-8 h-8 rounded-lg bg-neutral-900 border border-white/10 */}
          <div className="w-8 h-8 rounded-lg bg-neutral-900 border border-white/10 flex items-center justify-center text-white flex-shrink-0">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <div className="flex items-center space-x-1.5 min-w-0">
            <span className="text-sm font-semibold tracking-tight text-white">KAVACH</span>
            {/* Version badge: matches Navbar exactly */}
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/[0.06] text-neutral-400 border border-white/[0.08] flex-shrink-0">
              6.0
            </span>
          </div>
        </div>

        {/* ── Tagline — styled as a dashboard system subtitle ─────────────── */}
        <div className="mb-8 space-y-1">
          <p className="text-[11px] font-mono text-neutral-500 uppercase tracking-widest">
            Security Intelligence Platform
          </p>
          <p className="text-xl sm:text-2xl font-semibold tracking-tight text-white leading-tight">
            AI Hypothesizes.<br className="sm:hidden" />{' '}
            <span className="text-neutral-400">Evidence Confirms.</span>
          </p>
        </div>

        {/* ── Module checklist card — glass-level-2 style ──────────────────── */}
        <div
          className="rounded-xl border mb-4 overflow-hidden"
          style={{
            background:   'rgba(13, 13, 16, 0.62)',
            borderColor:  'rgba(255, 255, 255, 0.08)',
            boxShadow:    '0 8px 32px 0 rgba(0,0,0,0.65), inset 0 1px 0 0 rgba(255,255,255,0.05)',
          }}
        >
          {/* Card header label — same uppercase mono label style as dashboard section headers */}
          <div className="px-4 pt-4 pb-2.5 border-b border-white/[0.06]">
            <span className="text-[10px] font-mono text-neutral-500 uppercase tracking-widest">
              System Modules Initialization
            </span>
          </div>

          {/* Module rows */}
          <div className="px-4 py-3 space-y-0">
            {modules.map((m, idx) => (
              <div
                key={m.key}
                className="flex items-center justify-between py-2.5"
                style={{
                  borderBottom: idx < modules.length - 1
                    ? '1px solid rgba(255,255,255,0.04)'
                    : 'none',
                }}
              >
                <span className="text-xs text-neutral-300 font-sans truncate pr-4">
                  {m.name}
                </span>
                <div className="flex items-center space-x-2 flex-shrink-0">
                  {statusDot(m.status)}
                  {statusLabel(m.status)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Footer status line ────────────────────────────────────────────── */}
        {!showFailsafe && (
          <div className="flex items-center space-x-2 text-[11px] font-mono text-neutral-500">
            {bootComplete ? (
              <>
                <span className="w-1.5 h-1.5 rounded-full bg-[#34d399]" />
                <span className="text-[#34d399] tracking-widest uppercase">System Ready</span>
              </>
            ) : (
              <>
                <RefreshCw
                  className="w-3 h-3 flex-shrink-0"
                  style={{ animation: 'spin 1.2s linear infinite' }}
                  aria-hidden="true"
                />
                <span className="tracking-widest uppercase">Boot Sequence Running</span>
              </>
            )}
          </div>
        )}

        {/* ── Failsafe panel (Ollama offline) ─────────────────────────────── */}
        {showFailsafe && (
          <div
            className="rounded-2xl p-5 space-y-4 glass-modal border border-amber-500/20"
            style={{
              animation: 'fadeIn 0.3s ease forwards',
            }}
            role="alert"
          >
            {/* Warning header */}
            <div className="flex items-center space-x-2 text-[#fbbf24]">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
              <span className="text-xs font-mono uppercase tracking-widest font-semibold">
                Ollama Offline — Rule-Based Engine Active
              </span>
            </div>

            {/* Description */}
            <p className="text-xs text-neutral-300 leading-relaxed">
              Local Ollama service was not detected at port 11434.
              KAVACH will use deterministic rule-based security intelligence.
            </p>

            {/* Action buttons — adaptive responsive stacking on mobile screens */}
            <div className="btn-group-responsive pt-1">
              <button
                onClick={handleContinueDemo}
                className="btn-primary text-xs py-2 px-3.5 justify-center cursor-pointer"
                aria-label="Continue in demo mode without Ollama"
              >
                <Play className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
                <span>Continue — Demo Mode</span>
              </button>
              <button
                onClick={handleOpenStatus}
                className="btn-secondary text-xs py-2 px-3.5 justify-center cursor-pointer"
                aria-label="Open system status page"
              >
                <Activity className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
                <span>System Status</span>
              </button>
              <button
                onClick={handleRetry}
                disabled={retrying}
                className="btn-secondary text-xs py-2 px-3.5 justify-center cursor-pointer disabled:opacity-50"
                aria-label="Retry initialization"
              >
                <RefreshCw className={`w-3.5 h-3.5 flex-shrink-0 ${retrying ? 'animate-spin' : ''}`} aria-hidden="true" />
                <span>{retrying ? 'Checking Ollama...' : 'Retry'}</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Keyframes injected inline for the spin (avoids CSS file changes) */}
      <style>{`
        @keyframes spin   { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }

        @media (prefers-reduced-motion: reduce) {
          .animate-pulse { animation: none !important; }
          [style*="spin"] { animation: none !important; }
          [style*="fadeIn"] { animation: none !important; }
        }
      `}</style>
    </div>
  );
};
