import React, { useState, useEffect } from 'react';
import { Settings, Cpu, Clock, RefreshCw, Sparkles, Check, Server, Shield } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';

export const SettingsPage: React.FC = () => {
  const { ollamaStatus, isDemoMode, setIsDemoMode, refreshData, showToast } = useApp();

  const [activeModel, setActiveModel] = useState<string>(ollamaStatus?.selected_model || 'llama3');
  const [timeoutSec, setTimeoutSec] = useState<number>(15.0);
  const [baseUrl, setBaseUrl] = useState<string>(ollamaStatus?.base_url || 'http://localhost:11434');
  const [refreshing, setRefreshing] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (ollamaStatus) {
      setActiveModel(ollamaStatus.selected_model);
      setBaseUrl(ollamaStatus.base_url);
    }
  }, [ollamaStatus]);

  const handleRefreshModels = async () => {
    setRefreshing(true);
    try {
      await refreshData();
      showToast('success', 'Models Refreshed', 'Queried Ollama /api/tags successfully.');
    } catch (err: any) {
      showToast('error', 'Ollama Error', err.message || 'Failed to refresh models');
    } finally {
      setRefreshing(false);
    }
  };

  const handleSaveModel = async () => {
    setSaving(true);
    try {
      await api.selectOllamaModel(activeModel);
      await api.setOllamaTimeout(timeoutSec);
      await refreshData();
      showToast('success', 'Settings Saved', `Active AI model set to ${activeModel} (Timeout: ${timeoutSec}s).`);
    } catch (err: any) {
      showToast('error', 'Error', err.message || 'Failed to update settings');
    } finally {
      setSaving(false);
    }
  };

  const availableModels = ollamaStatus?.available_models || [];
  const displayModels = availableModels.length > 0 ? availableModels : ['llama3', 'mistral', 'qwen2.5-coder', 'phi3'];

  return (
    <div className="space-y-6 animate-fadeIn max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
          <Settings className="w-5 h-5 text-cyan-400" />
          <span>Platform Settings & AI Configuration</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1 font-mono-code">
          Configure local Ollama endpoint, model selection, reasoning timeout, and presentation mode.
        </p>
      </div>

      {/* Ollama & Model Configuration */}
      <GlassCard
        title="Ollama Local AI Engine"
        subtitle="Manage local LLM execution on your PC"
        icon={<Cpu className="w-5 h-5 text-purple-400" />}
        action={
          <button
            onClick={handleRefreshModels}
            disabled={refreshing}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-mono-code flex items-center space-x-1"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh Models</span>
          </button>
        }
      >
        <div className="space-y-4 font-mono-code text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 uppercase mb-1.5">Ollama Base URL</label>
              <input
                type="text"
                value={baseUrl}
                disabled
                className="w-full px-3 py-2 rounded-lg bg-slate-900/90 border border-slate-700 text-slate-300 text-xs font-mono-code opacity-80"
              />
              <span className="text-[10px] text-slate-500 mt-1 block">Configured via OLLAMA_BASE_URL environment variable</span>
            </div>

            <div>
              <label className="block text-slate-400 uppercase mb-1.5">Active AI Model</label>
              <select
                value={activeModel}
                onChange={(e) => setActiveModel(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 focus:border-cyan-400 text-slate-100 text-xs font-mono-code outline-none"
              >
                {displayModels.map((m) => (
                  <option key={m} value={m}>
                    {m} {m === ollamaStatus?.selected_model ? '(Current)' : ''}
                  </option>
                ))}
              </select>
              <span className="text-[10px] text-slate-500 mt-1 block">
                {availableModels.length > 0 ? `${availableModels.length} model(s) detected locally` : 'Showing common models'}
              </span>
            </div>
          </div>

          {/* AI Timeout Slider */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-slate-400 uppercase">Reasoning Timeout (Seconds)</label>
              <span className="text-cyan-400 font-bold">{timeoutSec}s</span>
            </div>
            <input
              type="range"
              min="5"
              max="60"
              step="5"
              value={timeoutSec}
              onChange={(e) => setTimeoutSec(Number(e.target.value))}
              className="w-full accent-cyan-400 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>5s (Fastest)</span>
              <span>15s (Recommended)</span>
              <span>60s (Deep Reasoning)</span>
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              onClick={handleSaveModel}
              disabled={saving}
              className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold uppercase tracking-wider flex items-center space-x-1.5 transition-all shadow-[0_0_15px_rgba(6,182,212,0.25)]"
            >
              <Check className="w-3.5 h-3.5" />
              <span>{saving ? 'Saving...' : 'Save AI Configuration'}</span>
            </button>
          </div>
        </div>
      </GlassCard>

      {/* Demo Mode Switcher */}
      <GlassCard
        title="Application Presentation Mode"
        subtitle="Control simulated vs authorized live testing"
        icon={<Sparkles className="w-5 h-5 text-amber-400" />}
      >
        <div className="space-y-3 font-mono-code text-xs">
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800">
            <div>
              <div className="font-bold text-slate-200">
                {isDemoMode ? 'Demo Mode (Simulated Data)' : 'Live Mode (Authorized Targets)'}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                {isDemoMode
                  ? 'All telemetry is clearly labelled as simulated for reliable presentation.'
                  : 'Live probes are executed against authorized targets.'}
              </div>
            </div>

            <button
              onClick={() => {
                setIsDemoMode(!isDemoMode);
                showToast('info', 'Mode Toggled', `Switched to ${!isDemoMode ? 'DEMO MODE' : 'LIVE MODE'}`);
              }}
              className={`px-4 py-2 rounded-lg font-bold transition-all ${
                isDemoMode
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                  : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
              }`}
            >
              {isDemoMode ? 'Switch to LIVE MODE' : 'Switch to DEMO MODE'}
            </button>
          </div>
        </div>
      </GlassCard>

      {/* Build & Runtime Info */}
      <GlassCard title="Build & Architecture Profile" subtitle="Enterprise Security Platform">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono-code text-xs">
          <div className="p-3 rounded-lg bg-slate-900/70 border border-slate-800">
            <div className="text-[10px] text-slate-500 uppercase">Platform Version</div>
            <div className="text-slate-100 font-bold mt-0.5">KAVACH 6.0.0</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/70 border border-slate-800">
            <div className="text-[10px] text-slate-500 uppercase">Frontend Framework</div>
            <div className="text-cyan-400 font-bold mt-0.5">React 19 + Vite</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/70 border border-slate-800">
            <div className="text-[10px] text-slate-500 uppercase">Backend Framework</div>
            <div className="text-emerald-400 font-bold mt-0.5">Python 3.11 + FastAPI</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/70 border border-slate-800">
            <div className="text-[10px] text-slate-500 uppercase">Architecture</div>
            <div className="text-purple-300 font-bold mt-0.5">Evidence-Driven RAG</div>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};
