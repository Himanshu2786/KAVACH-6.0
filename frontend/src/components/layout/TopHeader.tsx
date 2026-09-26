import React from 'react';
import { Globe, Cpu, RefreshCw, PlusCircle, ExternalLink, ShieldAlert } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const TopHeader: React.FC = () => {
  const { activeAssessment, ollamaStatus, isDemoMode, setIsDemoMode, navigate, refreshData, showToast } = useApp();

  const isOllamaOnline = ollamaStatus?.status === 'online';

  const handleRefresh = async () => {
    await refreshData();
    showToast('info', 'System Sync', 'Refreshed system metrics and assessment telemetry.');
  };

  return (
    <header className="h-16 bg-[#080d1a]/80 backdrop-blur-md border-b border-slate-800/80 px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Left: Active Target Scope */}
      <div className="flex items-center space-x-3 truncate max-w-xl">
        <div className="p-1.5 rounded-md bg-slate-800 border border-slate-700 text-slate-300">
          <Globe className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="truncate">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold text-slate-100 font-mono-code truncate">
              {activeAssessment ? activeAssessment.name : 'No Target Selected'}
            </span>
            <span className="text-[10px] font-mono-code px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              {activeAssessment?.environment || 'Sandbox'}
            </span>
          </div>
          <div className="text-[11px] text-slate-400 font-mono-code truncate">
            {activeAssessment?.target_url || 'https://localhost'}
          </div>
        </div>
      </div>

      {/* Right: Status Indicators & Quick Actions */}
      <div className="flex items-center space-x-3 font-mono-code text-xs">
        {/* Demo / Live Mode Indicator */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700">
          <button
            onClick={() => {
              setIsDemoMode(!isDemoMode);
              showToast('info', 'Mode Switched', `Active Mode: ${!isDemoMode ? 'DEMO MODE (Simulated)' : 'LIVE MODE (Authorized Targets)'}`);
            }}
            className="flex items-center space-x-1.5 hover:opacity-80 transition-opacity"
            title="Click to toggle between Demo Mode and Live Mode"
          >
            <span
              className={`w-2 h-2 rounded-full ${isDemoMode ? 'bg-amber-400' : 'bg-emerald-400'} animate-pulse`}
            />
            <span className="text-[11px] font-semibold text-slate-200 uppercase">
              {isDemoMode ? 'DEMO MODE' : 'LIVE MODE'}
            </span>
          </button>
        </div>

        {/* Ollama Status Badge */}
        <div
          onClick={() => navigate('settings')}
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border cursor-pointer transition-all ${
            isOllamaOnline
              ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300 hover:border-emerald-400'
              : 'bg-amber-950/40 border-amber-500/40 text-amber-300 hover:border-amber-400'
          }`}
          title="Click to inspect Ollama settings and AI models"
        >
          <Cpu className="w-3.5 h-3.5" />
          <span className="font-bold text-[11px]">
            {isOllamaOnline ? 'OLLAMA ONLINE' : 'OLLAMA OFFLINE'}
          </span>
          <span className="text-[10px] text-slate-400 font-normal">
            ({ollamaStatus?.selected_model || 'llama3'})
          </span>
        </div>

        {/* Quick Refresh Button */}
        <button
          onClick={handleRefresh}
          className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 transition-colors"
          title="Refresh Telemetry"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>

        {/* New Assessment Quick Button */}
        <button
          onClick={() => navigate('new-assessment')}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold transition-all shadow-[0_0_12px_rgba(6,182,212,0.25)]"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          <span>New Assessment</span>
        </button>
      </div>
    </header>
  );
};
