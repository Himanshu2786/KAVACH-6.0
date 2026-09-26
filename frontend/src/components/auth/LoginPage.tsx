import React, { useState } from 'react';
import { Shield, Lock, Key, User, AlertTriangle, CheckCircle2, Cpu } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { AmbientBackground } from '../visual/AmbientBackground';
import { CursorLight } from '../visual/CursorLight';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId.trim() || !password) {
      setError('Please provide both USER ID and Password.');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      await login(userId.trim().toUpperCase(), password);
    } catch (err: any) {
      setError(err.message || 'Invalid credentials. Please verify your USER ID and Password.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#000000] text-neutral-100 flex flex-col relative overflow-hidden select-none">
      {/* Dynamic Ambient Backgrounds */}
      <AmbientBackground />
      <CursorLight />

      {/* Top Navbar Header */}
      <header className="h-14 border-b border-white/[0.08] bg-[#000000]/80 backdrop-blur-md relative z-20 flex items-center justify-between px-6">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-neutral-900 border border-white/10 flex items-center justify-center text-white flex-shrink-0">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="text-sm font-semibold tracking-tight text-white">KAVACH</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/[0.06] text-neutral-400 border border-white/[0.08]">
              6.0
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs">
          <span className="text-[11px] font-mono px-2.5 py-1 rounded-full bg-white/[0.04] text-neutral-400 border border-white/[0.08] flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#34d399] animate-pulse" />
            <span>GATEWAY: SECURE ACCESS</span>
          </span>
        </div>
      </header>

      {/* Center Form Card */}
      <div className="flex-1 flex items-center justify-center p-6 relative z-10">
        <div className="w-full max-w-md space-y-6">
          {/* Main Card */}
          <div
            className="glass-level-2 rounded-2xl border p-8 relative overflow-hidden"
            style={{
              background: 'rgba(13, 13, 16, 0.75)',
              borderColor: 'rgba(255, 255, 255, 0.08)',
              boxShadow: '0 16px 48px 0 rgba(0, 0, 0, 0.8), inset 0 1px 0 0 rgba(255, 255, 255, 0.06)',
            }}
          >
            {/* Header info */}
            <div className="text-center mb-7">
              <p className="text-[11px] font-mono text-neutral-500 uppercase tracking-widest mb-1.5">
                Security Intelligence Platform
              </p>
              <h1 className="text-xl sm:text-2xl font-semibold tracking-tight text-white leading-tight mb-3">
                AI Hypothesizes.{' '}
                <span className="text-neutral-400">Evidence Confirms.</span>
              </h1>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono bg-white/[0.04] border border-white/[0.08] text-neutral-400">
                <Cpu className="w-3.5 h-3.5 text-[#34d399]" />
                <span>Deterministic Evidence Architecture</span>
              </div>
            </div>

            {error && (
              <div
                role="alert"
                className="mb-5 p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-200 text-xs flex items-start gap-2.5"
              >
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">Authentication Failed</p>
                  <p className="text-rose-300/80 text-[11px] mt-0.5">{error}</p>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[11px] font-mono font-medium text-neutral-400 mb-1.5 uppercase tracking-wider">
                  USER ID
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-neutral-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    placeholder="Enter USER ID"
                    className="w-full glass-input rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-neutral-600 font-mono tracking-wider transition-all focus:outline-none focus:border-white/20 focus:ring-1 focus:ring-white/10"
                    style={{
                      background: 'rgba(255, 255, 255, 0.03)',
                      borderColor: 'rgba(255, 255, 255, 0.08)',
                      borderWidth: '1px',
                    }}
                    autoComplete="username"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-mono font-medium text-neutral-400 mb-1.5 uppercase tracking-wider">
                  PASSWORD
                </label>
                <div className="relative">
                  <Key className="w-4 h-4 text-neutral-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full glass-input rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-neutral-600 font-mono transition-all focus:outline-none focus:border-white/20 focus:ring-1 focus:ring-white/10"
                    style={{
                      background: 'rgba(255, 255, 255, 0.03)',
                      borderColor: 'rgba(255, 255, 255, 0.08)',
                      borderWidth: '1px',
                    }}
                    autoComplete="current-password"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary w-full mt-2 py-3 px-4 text-xs font-semibold tracking-wider uppercase rounded-xl flex items-center justify-center gap-2 cursor-pointer transition-all disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-black border-t-transparent rounded-full animate-spin" />
                    <span>Authenticating...</span>
                  </>
                ) : (
                  <>
                    <Lock className="w-3.5 h-3.5" />
                    <span>Sign In to KAVACH</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Footer Security Badges */}
          <div className="flex items-center justify-center gap-3 text-[11px] font-mono text-neutral-500">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#34d399]" />
              <span>PBKDF2-HMAC Auth</span>
            </span>
            <span className="text-neutral-700">•</span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#34d399]" />
              <span>Isolated Tenants</span>
            </span>
            <span className="text-neutral-700">•</span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#34d399]" />
              <span>Audited SHA-256</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
