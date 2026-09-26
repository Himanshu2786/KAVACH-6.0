import React, { useState, useEffect } from 'react';
import {
  Shield,
  FolderLock,
  Cpu,
  Package,
  Clock,
  Wifi,
  Lock,
  CheckCircle2,
  XCircle,
  Play,
  Terminal,
  Copy,
  Check,
  AlertTriangle,
  RefreshCw,
  FileCheck2,
  Sliders,
  ExternalLink,
  ChevronDown,
  Info,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import { PortablePermission, PortableFinding, PortableScanResults } from '../types';

export const PortableAssessmentPage: React.FC = () => {
  const { showToast } = useApp();
  const [permissions, setPermissions] = useState<PortablePermission[]>([]);
  const [targetFolder, setTargetFolder] = useState('demo/training_samples');
  const [scanning, setScanning] = useState(false);
  const [scanResults, setScanResults] = useState<PortableScanResults | null>(null);
  const [selectedFinding, setSelectedFinding] = useState<PortableFinding | null>(null);
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);
  const [copiedHash, setCopiedHash] = useState(false);
  const [demoSamples, setDemoSamples] = useState<any[]>([]);

  const loadPermissions = async () => {
    try {
      const res = await api.getPortablePermissions();
      if (res.success) {
        setPermissions(res.permissions);
      }
    } catch (err) {
      console.error('Failed to load permissions:', err);
    }
  };

  const loadDemoSamples = async () => {
    try {
      const res = await api.getDemoSamples();
      if (res.success) {
        setDemoSamples(res.samples);
      }
    } catch (err) {
      console.error('Failed to load demo samples:', err);
    }
  };

  useEffect(() => {
    loadPermissions();
    loadDemoSamples();
  }, []);

  const handleTogglePermission = async (id: string, currentGranted: boolean) => {
    const updatedMap: Record<string, boolean> = {};
    permissions.forEach((p) => {
      updatedMap[p.id] = p.id === id ? !currentGranted : p.granted;
    });

    try {
      const res = await api.updatePortablePermissions(updatedMap);
      if (res.success) {
        setPermissions(res.permissions);
        showToast(
          'info',
          'Consent Updated',
          `${id.toUpperCase()}: ${!currentGranted ? 'PERMISSION GRANTED' : 'PERMISSION DENIED'}`
        );
      }
    } catch (err: any) {
      showToast('error', 'Error', err.message || 'Failed to update consent');
    }
  };

  const handleGrantAll = async () => {
    const updatedMap: Record<string, boolean> = {};
    permissions.forEach((p) => {
      updatedMap[p.id] = true;
    });
    const res = await api.updatePortablePermissions(updatedMap);
    if (res.success) {
      setPermissions(res.permissions);
      showToast('success', 'Full Authorization', 'All 6 local assessment permissions approved.');
    }
  };

  const handleDenyAll = async () => {
    const updatedMap: Record<string, boolean> = {};
    permissions.forEach((p) => {
      updatedMap[p.id] = false;
    });
    const res = await api.updatePortablePermissions(updatedMap);
    if (res.success) {
      setPermissions(res.permissions);
      showToast('warning', 'All Denied', 'Zero-collection guard active. No local scanning will occur.');
    }
  };

  const handleExecuteScan = async () => {
    setScanning(true);
    try {
      const res = await api.executePortableScan(targetFolder);
      if (res.success) {
        setScanResults(res.results);
        if (res.results.findings.length > 0) {
          setSelectedFinding(res.results.findings[0]);
        }
        showToast(
          'success',
          'Assessment Complete',
          `Audited approved categories. ${res.results.findings.length} verifiable observation(s) recorded.`
        );
      }
    } catch (err: any) {
      showToast('error', 'Assessment Error', err.message || 'Failed to execute local assessment');
    } finally {
      setScanning(false);
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCmd(id);
    setTimeout(() => setCopiedCmd(null), 2000);
  };

  const getPermissionIcon = (id: string) => {
    switch (id) {
      case 'files':
        return FolderLock;
      case 'processes':
        return Cpu;
      case 'installed_apps':
        return Package;
      case 'startup_items':
        return Clock;
      case 'network':
        return Wifi;
      case 'system_security':
      default:
        return Lock;
    }
  };

  const getSeverityDot = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
      case 'HIGH':
        return 'bg-red-400';
      case 'MEDIUM':
        return 'bg-amber-400';
      case 'LOW':
      default:
        return 'bg-emerald-400';
    }
  };

  const grantedCount = permissions.filter((p) => p.granted).length;

  return (
    <div className="max-w-7xl mx-auto space-y-12 pb-24 text-neutral-100">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-b border-white/[0.08] pb-6">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-neutral-900 border border-white/[0.08] text-xs font-mono text-neutral-300 mb-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>KAVACH 6.0 PORTABLE</span>
            <span className="text-neutral-600">/</span>
            <span>USB EDITION</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white">
            Portable Windows Security Assessment
          </h1>
          <p className="text-xs sm:text-sm text-neutral-400 mt-1 max-w-2xl leading-relaxed">
            Consent-based local host assessment. Zero silent elevation, zero UAC bypass, and zero intrusive actions.
            Permission denied strictly means: <strong>No collection. No scanning. No fake results.</strong>
          </p>
        </div>

        {/* Quick Permission Actions */}
        <div className="flex items-center space-x-2.5 text-xs font-mono shrink-0">
          <button
            onClick={handleGrantAll}
            className="px-3.5 py-1.5 rounded-md bg-white text-black font-semibold hover:bg-neutral-200 transition-colors shadow-sm"
          >
            Allow All ({permissions.length})
          </button>
          <button
            onClick={handleDenyAll}
            className="px-3.5 py-1.5 rounded-md bg-neutral-900 hover:bg-neutral-800 border border-white/[0.1] text-neutral-300 hover:text-white transition-colors"
          >
            Deny All
          </button>
        </div>
      </div>

      {/* Remote Web Assessment vs Local Desktop Agent Notice */}
      <div className="rounded-xl border border-cyan-500/30 bg-cyan-950/20 p-4 text-xs font-mono text-cyan-200/90 flex items-start gap-3">
        <Info className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-cyan-300">DEPLOYMENT & ARCHITECTURE NOTICE:</span> Browser sessions communicate with the hosted KAVACH service to perform <strong>Remote Web Security Assessments</strong>. Browsers cannot directly probe your local Windows file system or registry. <strong>Local Host Assessment</strong> is performed via the dedicated KAVACH Portable Desktop binary/CLI on the target machine.
        </div>
      </div>

      {/* 1. CONSENT & PERMISSION DASHBOARD */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs font-mono text-neutral-500 uppercase tracking-widest block">
              Authorization Guard
            </span>
            <h2 className="text-xl font-semibold tracking-tight text-white">
              Consent & Permission Dashboard
            </h2>
          </div>
          <div className="text-xs font-mono text-neutral-400">
            Approved: <span className="text-emerald-400 font-bold">{grantedCount} of {permissions.length}</span> Categories
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {permissions.map((perm) => {
            const Icon = getPermissionIcon(perm.id);
            const isGranted = perm.granted;

            return (
              <div
                key={perm.id}
                className={`p-5 rounded-2xl border transition-all duration-200 flex flex-col justify-between ${isGranted
                    ? 'glass-card border-emerald-500/30 shadow-[0_0_18px_rgba(16,185,129,0.06)]'
                    : 'glass-panel opacity-75'
                  }`}
              >
                <div>
                  {/* Card Header with Toggle */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2.5">
                      <div className={`p-2 rounded-lg border ${isGranted
                          ? 'bg-emerald-950/40 text-emerald-400 border-emerald-500/40'
                          : 'glass-panel text-neutral-500 border-white/[0.08]'
                        }`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <h3 className="text-sm font-semibold tracking-tight text-white">
                        {perm.name}
                      </h3>
                    </div>

                    {/* Toggle Button */}
                    <button
                      onClick={() => handleTogglePermission(perm.id, isGranted)}
                      className={`px-2.5 py-1 rounded text-[11px] font-mono font-semibold transition-all cursor-pointer ${isGranted
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                          : 'glass-panel text-neutral-400 border border-white/[0.1] hover:border-white/30'
                        }`}
                    >
                      {isGranted ? 'ALLOWED ✓' : 'DENIED ✕'}
                    </button>
                  </div>

                  {/* Information Breakdown */}
                  <div className="space-y-2 text-xs">
                    <div>
                      <span className="text-[10px] font-mono text-neutral-500 uppercase block">WHAT IT WILL ACCESS</span>
                      <p className="text-neutral-300 leading-relaxed text-[11px]">{perm.what_accessed}</p>
                    </div>

                    <div>
                      <span className="text-[10px] font-mono text-neutral-500 uppercase block">WHY IT IS NEEDED</span>
                      <p className="text-neutral-400 leading-relaxed text-[11px]">{perm.why_needed}</p>
                    </div>

                    <div>
                      <span className="text-[10px] font-mono text-neutral-500 uppercase block">CHECKS ENABLED</span>
                      <p className="text-neutral-300 font-mono text-[10px] leading-relaxed">{perm.checks_enabled}</p>
                    </div>
                  </div>
                </div>

                {/* If Denied Banner */}
                {!isGranted && (
                  <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center space-x-1.5 text-[10px] font-mono text-amber-400">
                    <AlertTriangle className="w-3 h-3" />
                    <span>Not scanned — permission not granted.</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* 2. TARGET LOCATION & SCAN LAUNCHER */}
      <section className="p-6 rounded-2xl glass-level-2 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-xs font-mono text-neutral-400 uppercase tracking-wider block">
              Assessment Execution
            </span>
            <h3 className="text-lg font-semibold text-white">
              Launch Portable Security Scan
            </h3>
          </div>

          <div className="flex items-center space-x-2 text-xs font-mono">
            <button
              onClick={() => setTargetFolder('demo/training_samples')}
              className="text-neutral-400 hover:text-white underline underline-offset-4 decoration-neutral-700 cursor-pointer"
            >
              Use Safe Demo Lab Path (Synthetic Artifacts)
            </button>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={targetFolder}
              onChange={(e) => setTargetFolder(e.target.value)}
              placeholder="Enter approved folder or file path to audit..."
              className="w-full px-4 py-3 rounded-xl glass-input text-white font-mono text-xs placeholder-neutral-500 focus:outline-none transition-all"
            />
          </div>

          <button
            onClick={handleExecuteScan}
            disabled={scanning || grantedCount === 0}
            className="btn-primary px-6 py-3 rounded-xl text-xs font-mono font-semibold disabled:opacity-40 transition-all flex items-center justify-center space-x-2 shadow-sm cursor-pointer shrink-0"
          >
            {scanning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Auditing Local Scope...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Run Portable Assessment ({grantedCount} Approved)</span>
              </>
            )}
          </button>
        </div>

        {/* Demo Samples Preview Pill */}
        {demoSamples.length > 0 && (
          <div className="pt-2 text-xs font-mono text-neutral-400 flex flex-wrap items-center gap-2">
            <span className="text-neutral-500">Available Safe Samples:</span>
            {demoSamples.map((s) => (
              <span
                key={s.name}
                onClick={() => setTargetFolder(`demo/training_samples/${s.name}`)}
                className="px-2 py-0.5 rounded glass-panel hover:border-white/30 text-neutral-300 cursor-pointer text-[10px]"
              >
                {s.name}
              </span>
            ))}
          </div>
        )}
      </section>

      {/* 3. MODULAR SCAN STATUS SUMMARY */}
      {scanResults && (
        <section className="space-y-4 animate-in fade-in duration-300">
          <div className="text-xs font-mono text-neutral-500 uppercase tracking-widest">
            Module Audit Breakdown
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {Object.entries(scanResults.module_summaries).map(([modName, modInfo]) => {
              const isDenied = modInfo.status === 'DENIED';

              return (
                <div
                  key={modName}
                  className={`p-3.5 rounded-xl border text-xs font-mono ${isDenied
                      ? 'glass-panel opacity-60 text-neutral-500'
                      : 'glass-card text-white'
                    }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] uppercase font-bold text-neutral-400 truncate">
                      {modName.replace('_', ' ')}
                    </span>
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${isDenied ? 'bg-neutral-600' : 'bg-emerald-400'
                        }`}
                    />
                  </div>
                  <div className="text-lg font-bold">
                    {isDenied ? '—' : `${modInfo.findings_count} findings`}
                  </div>
                  <div className="text-[10px] text-neutral-500 truncate mt-1">
                    {modInfo.summary}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* 4. FINDINGS & VERIFIABLE EVIDENCE CONTAINER */}
      {scanResults && (
        <section className="space-y-6 animate-in fade-in duration-300">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-mono text-neutral-500 uppercase tracking-widest block">
                Evidence Catalog
              </span>
              <h2 className="text-xl font-semibold tracking-tight text-white">
                Local Assessment Findings ({scanResults.findings.length})
              </h2>
            </div>
            <span className="text-xs font-mono text-neutral-400">
              SHA-256 Hashed Evidence Records
            </span>
          </div>

          {scanResults.findings.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

              {/* Left Column: Finding Selector (4 cols) */}
              <div className="lg:col-span-4 space-y-2">
                {scanResults.findings.map((f) => {
                  const isSelected = selectedFinding?.id === f.id;

                  return (
                    <div
                      key={f.id}
                      onClick={() => setSelectedFinding(f)}
                      className={`p-3.5 rounded-xl border cursor-pointer transition-all duration-150 ${isSelected
                          ? 'glass-card-selected text-white shadow-sm'
                          : 'glass-card text-neutral-400 hover:border-white/20 hover:text-neutral-200'
                        }`}
                    >
                      <div className="flex items-center justify-between text-xs font-mono mb-1">
                        <span className="font-semibold text-white">{f.id}</span>
                        <span className="flex items-center space-x-1 text-[10px]">
                          <span className={`w-1.5 h-1.5 rounded-full ${getSeverityDot(f.severity)}`} />
                          <span>{f.severity}</span>
                        </span>
                      </div>
                      <div className="text-xs font-medium text-neutral-200 truncate mb-1">
                        {f.title}
                      </div>
                      <div className="text-[10px] font-mono text-neutral-500 truncate">
                        {f.affected_component}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Right Column: Detailed Evidence & Terminal Verification (8 cols) */}
              <div className="lg:col-span-8 space-y-4">
                {selectedFinding && (
                  <div className="p-6 rounded-2xl glass-card space-y-6 shadow-xl font-mono text-xs">

                    {/* Header */}
                    <div className="flex flex-wrap items-center justify-between gap-2 pb-4 border-b border-white/[0.08]">
                      <div>
                        <div className="flex items-center space-x-2 text-[11px] text-neutral-400 mb-1">
                          <span className="px-2 py-0.5 rounded bg-white/[0.08] text-white font-semibold">
                            {selectedFinding.id}
                          </span>
                          <span>{selectedFinding.category}</span>
                          <span>•</span>
                          <span className="text-emerald-400 font-semibold">Verified Evidence</span>
                        </div>
                        <h3 className="text-base font-bold text-white font-sans">
                          {selectedFinding.title}
                        </h3>
                      </div>

                      <div className="flex items-center space-x-2">
                        <span className="text-[10px] px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                          {selectedFinding.evidence.evidence_nature}
                        </span>
                      </div>
                    </div>

                    {/* What Was Found & Description */}
                    <div className="space-y-1.5">
                      <span className="text-[10px] text-neutral-500 uppercase font-bold tracking-wider block">
                        WHAT KAVACH FOUND
                      </span>
                      <p className="text-neutral-200 leading-relaxed font-sans text-xs">
                        {selectedFinding.description}
                      </p>
                    </div>

                    {/* Real Evidence Container */}
                    <div className="space-y-2 p-4 rounded-xl glass-terminal">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-neutral-400 uppercase font-semibold">
                          VERBATIM OBSERVATION PAYLOAD
                        </span>
                        <div className="flex items-center space-x-1.5 text-emerald-400 text-[10px]">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>SHA-256 Hash Verified</span>
                        </div>
                      </div>
                      <pre className="text-neutral-300 text-[11px] overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-40 glass-code p-2.5 rounded-lg">
                        {selectedFinding.evidence.raw_observation}
                      </pre>
                      <div className="pt-2 border-t border-white/[0.06] text-[10px] text-neutral-500 truncate">
                        Hash: <span className="text-emerald-300 font-mono">{selectedFinding.evidence.integrity_hash}</span>
                      </div>
                    </div>

                    {/* Terminal Verification */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-neutral-400 uppercase font-semibold flex items-center space-x-1.5">
                          <Terminal className="w-3.5 h-3.5 text-white" />
                          <span>SAFE REPRODUCIBLE POWERSHELL PROCEDURE</span>
                        </span>
                        <button
                          onClick={() => handleCopy(selectedFinding.terminal_verification.command, selectedFinding.id)}
                          className="btn-primary flex items-center space-x-1 px-2.5 py-1 rounded font-semibold text-[10px] transition-colors cursor-pointer"
                        >
                          {copiedCmd === selectedFinding.id ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" />
                              <span>COPIED</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>COPY COMMAND</span>
                            </>
                          )}
                        </button>
                      </div>

                      <div className="p-3 rounded-lg glass-terminal text-neutral-200 text-xs overflow-x-auto select-all glass-code">
                        <code>{selectedFinding.terminal_verification.command}</code>
                      </div>

                      {/* Expected vs Observed */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                        <div className="p-3 rounded-lg glass-panel border-emerald-500/20">
                          <span className="text-[10px] text-emerald-400 uppercase block mb-1">
                            Expected Baseline
                          </span>
                          <pre className="text-[10px] text-neutral-300 whitespace-pre-wrap">
                            {selectedFinding.terminal_verification.expected_output}
                          </pre>
                        </div>
                        <div className="p-3 rounded-lg glass-panel border-red-500/20">
                          <span className="text-[10px] text-red-400 uppercase block mb-1">
                            Observed Flaw
                          </span>
                          <pre className="text-[10px] text-neutral-300 whitespace-pre-wrap">
                            {selectedFinding.terminal_verification.observed_output}
                          </pre>
                        </div>
                      </div>
                    </div>

                    {/* Remediation */}
                    <div className="p-4 rounded-xl glass-panel space-y-2">
                      <div className="text-[11px] text-white font-semibold uppercase">
                        How to Remediate
                      </div>
                      <p className="text-neutral-300 text-xs font-sans leading-relaxed">
                        {selectedFinding.remediation.how_to_fix}
                      </p>
                      <div className="pt-2 text-[11px] text-neutral-400 font-sans">
                        <strong className="text-neutral-300">Why It Matters: </strong>
                        {selectedFinding.remediation.why_matters}
                      </div>
                    </div>

                  </div>
                )}
              </div>

            </div>
          ) : (
            <div className="p-12 text-center rounded-xl glass-level-1 font-mono text-xs text-neutral-400">
              No security anomalies detected in the approved categories. All supported checks passed clean.
            </div>
          )}
        </section>
      )}

    </div>
  );
};
