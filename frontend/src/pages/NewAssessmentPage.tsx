import React, { useState } from 'react';
import { ShieldCheck, AlertCircle, PlusCircle, Globe, Lock, Layers } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api, isWorldMonitorTarget } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';

const MODULES_LIST = [
  'Authentication',
  'Authorization',
  'API Security',
  'Input Validation',
  'Security Headers',
  'Configuration Review'
];

export const NewAssessmentPage: React.FC = () => {
  const { navigate, setActiveAssessment, showToast, refreshData } = useApp();

  const [name, setName] = useState('');
  const [targetUrl, setTargetUrl] = useState('');
  const [description, setDescription] = useState('');
  const [environment, setEnvironment] = useState('Testing Environment');
  const [scope, setScope] = useState('Full Application Surface & API');
  const [authorizationConfirmed, setAuthorizationConfirmed] = useState(false);
  const [selectedModules, setSelectedModules] = useState<string[]>([
    'Authentication',
    'Authorization',
    'API Security',
    'Input Validation',
    'Security Headers'
  ]);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const toggleModule = (mod: string) => {
    if (selectedModules.includes(mod)) {
      setSelectedModules(selectedModules.filter((m) => m !== mod));
    } else {
      setSelectedModules([...selectedModules, mod]);
    }
  };

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (!name.trim()) {
      setErrorMsg('Target Name is required.');
      return;
    }
    if (!targetUrl.trim()) {
      setErrorMsg('Target URL is required.');
      return;
    }
    if (!authorizationConfirmed) {
      setErrorMsg('You must confirm that you are authorized to assess this target.');
      return;
    }
    if (selectedModules.length === 0) {
      setErrorMsg('At least one assessment module must be selected.');
      return;
    }

    setSubmitting(true);
    try {
      const isWM = isWorldMonitorTarget(targetUrl) && environment !== 'Demo Environment';
      if (isWM) {
        // Route World Monitor target through dedicated empirical assessment engine
        const wmResult = await api.runWorldMonitorAssessment({
          target_url: targetUrl.trim(),
          mode: 'HYBRID',
          assessment_name: name.trim() || 'World Monitor Security Assessment'
        });

        await refreshData();

        // The returned backend assessment_id becomes active assessment
        const asmId = wmResult.assessment_id;
        const resolved = {
          id: asmId,
          name: name.trim() || `World Monitor Assessment ${asmId}`,
          target_url: targetUrl.trim(),
          description: wmResult.summary || description || 'Dedicated empirical World Monitor assessment.',
          environment: environment,
          scope: scope,
          authorization_confirmed: true,
          modules_enabled: selectedModules,
          status: 'COMPLETED' as const,
          progress: 100,
          current_stage: 'REPORT',
          started_at: wmResult.start_time || new Date().toISOString(),
          completed_at: wmResult.completed_at || new Date().toISOString(),
          is_demo: false,
          assessment_type: 'WORLD_MONITOR_EMPIRICAL',
          total_findings: wmResult.total_findings ?? 1,
          confirmed_findings: wmResult.confirmed_findings ?? 1,
        };

        setActiveAssessment(resolved);
        showToast('success', 'World Monitor Assessment Completed', `Empirical assessment ${asmId} completed with ${wmResult.confirmed_findings ?? 1} confirmed finding.`);
        navigate('findings');
        return;
      }

      const newAsm = await api.createAssessment({
        name,
        target_url: targetUrl,
        description,
        environment,
        scope,
        authorization_confirmed: authorizationConfirmed,
        modules_enabled: selectedModules,
        is_demo: environment === 'Demo Environment'
      });

      await refreshData();
      setActiveAssessment(newAsm);
      showToast('success', 'Assessment Initiated', `Assessment ${newAsm.id} started for ${newAsm.name}.`);
      navigate('progress');
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to create assessment.');
      showToast('error', 'Error', err.message || 'Failed to create assessment.');
    } finally {
      setSubmitting(false);
    }
  };

  const loadSampleTarget = () => {
    setName('WORLD MONITOR');
    setTargetUrl('https://www.worldmonitor.app');
    setDescription('Authorized security posture evaluation and vulnerability assessment of the World Monitor situational crisis tracking platform.');
    setEnvironment('Local Development');
    setScope('Complete Web Platform, Situational Telemetry & REST API Surface');
    setAuthorizationConfirmed(true);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-cyan-400" />
            <span>New Security Assessment</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure target boundaries, security scope, and authorized testing modules.
          </p>
        </div>
        <button
          type="button"
          onClick={loadSampleTarget}
          className="text-xs font-mono-code px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 transition-colors cursor-pointer"
        >
          Autofill WORLD MONITOR
        </button>
      </div>

      {errorMsg && (
        <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-300 font-mono-code text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      <form onSubmit={handleStart} className="space-y-6">
        {/* Target Details Bento */}
        <GlassCard title="Target Specification" subtitle="Define endpoint parameters and operational environment">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-mono-code text-slate-300 mb-1.5 uppercase">
                Target Name *
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. WORLD MONITOR"
                className="w-full px-3.5 py-2 rounded-lg bg-slate-900/90 border border-slate-700 focus:border-cyan-400 text-slate-100 text-xs font-mono-code outline-none transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-mono-code text-slate-300 mb-1.5 uppercase">
                Target URL / Host *
              </label>
              <input
                type="text"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="e.g. https://www.worldmonitor.app"
                className="w-full px-3.5 py-2 rounded-lg bg-slate-900/90 border border-slate-700 focus:border-cyan-400 text-slate-100 text-xs font-mono-code outline-none transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-mono-code text-slate-300 mb-1.5 uppercase">
                Environment Type
              </label>
              <select
                value={environment}
                onChange={(e) => setEnvironment(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg bg-slate-900/90 border border-slate-700 focus:border-cyan-400 text-slate-100 text-xs font-mono-code outline-none transition-colors"
              >
                <option value="Local Development">Local Development</option>
                <option value="Testing Environment">Testing Environment</option>
                <option value="Staging">Staging</option>
                <option value="Demo Environment">Demo Environment</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono-code text-slate-300 mb-1.5 uppercase">
                Assessment Scope Boundary
              </label>
              <input
                type="text"
                value={scope}
                onChange={(e) => setScope(e.target.value)}
                placeholder="e.g. Complete Web Platform, Situational Telemetry & REST API Surface"
                className="w-full px-3.5 py-2 rounded-lg bg-slate-900/90 border border-slate-700 focus:border-cyan-400 text-slate-100 text-xs font-mono-code outline-none transition-colors"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs font-mono-code text-slate-300 mb-1.5 uppercase">
                Target Description (Optional)
              </label>
              <textarea
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Authorized security posture evaluation and vulnerability assessment of the World Monitor situational crisis tracking platform."
                className="w-full px-3.5 py-2 rounded-lg bg-slate-900/90 border border-slate-700 focus:border-cyan-400 text-slate-100 text-xs font-mono-code outline-none transition-colors"
              />
            </div>
          </div>
        </GlassCard>

        {/* Modular Assessment Toggles */}
        <GlassCard title="Assessment Modules" subtitle="Select security testing capabilities for this run">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {MODULES_LIST.map((mod) => {
              const active = selectedModules.includes(mod);
              return (
                <div
                  key={mod}
                  onClick={() => toggleModule(mod)}
                  className={`p-3 rounded-lg border cursor-pointer font-mono-code text-xs flex items-center justify-between transition-all ${active
                      ? 'bg-cyan-500/15 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.15)]'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
                    }`}
                >
                  <span className="font-semibold">{mod}</span>
                  <div
                    className={`w-3.5 h-3.5 rounded flex items-center justify-center text-[10px] ${active ? 'bg-cyan-400 text-slate-950 font-bold' : 'border border-slate-700'
                      }`}
                  >
                    {active ? '✓' : ''}
                  </div>
                </div>
              );
            })}
          </div>
        </GlassCard>

        {/* Security Scope Guard - Mandatory Authorization Checkbox */}
        <GlassCard
          title="Security Scope Guard"
          subtitle="Mandatory authorization confirmation prior to assessment initialization"
          glow="amber"
          className="border-amber-500/30"
        >
          <div className="flex items-start space-x-3 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/25">
            <input
              type="checkbox"
              id="auth-guard"
              checked={authorizationConfirmed}
              onChange={(e) => setAuthorizationConfirmed(e.target.checked)}
              className="mt-1 w-4 h-4 rounded border-slate-700 text-cyan-500 focus:ring-cyan-400 cursor-pointer"
            />
            <label htmlFor="auth-guard" className="text-xs text-slate-200 cursor-pointer leading-relaxed">
              <strong className="text-amber-300 font-mono-code uppercase block mb-0.5">
                Authorization Confirmed
              </strong>
              I confirm that I am explicitly authorized to perform non-destructive security assessment and observation against this target. Testing will respect defined scope boundaries without harmful exploitation.
            </label>
          </div>
        </GlassCard>

        {/* Submit Button */}
        <div className="flex justify-end space-x-3 pt-2">
          <button
            type="button"
            onClick={() => navigate('command-center')}
            className="px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono-code text-xs transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting || !authorizationConfirmed}
            className="px-6 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 disabled:opacity-40 disabled:cursor-not-allowed text-slate-950 font-bold font-mono-code text-xs tracking-wider uppercase transition-all shadow-[0_0_20px_rgba(6,182,212,0.3)] flex items-center space-x-2"
          >
            <PlusCircle className="w-4 h-4" />
            <span>{submitting ? 'INITIALIZING WORKFLOW...' : 'START SECURITY ASSESSMENT'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
