import React, { useState, useEffect } from 'react';
import { 
  FlaskConical, 
  Play, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  FileCode2, 
  ShieldCheck, 
  Clock, 
  Hash, 
  Info,
  Terminal,
  FileCheck2,
  RefreshCw
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { TestSuite, TestRunResult } from '../types';

export const TestCenterPage: React.FC = () => {
  const { showToast } = useApp();
  const [suites, setSuites] = useState<TestSuite[]>([]);
  const [selectedSuiteId, setSelectedSuiteId] = useState<string>('');
  const [testResult, setTestResult] = useState<TestRunResult | null>(null);
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchSuites = async () => {
    try {
      const res = await api.getTestSuites();
      if (res.success) {
        setSuites(res.suites);
        if (res.suites.length > 0 && !selectedSuiteId) {
          setSelectedSuiteId(res.suites[0].id);
        }
      }
    } catch {
      showToast('error', 'Error', 'Failed to load test suites.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuites();
  }, []);

  const handleRunTest = async () => {
    if (!selectedSuiteId) return;
    setRunning(true);
    setTestResult(null);
    try {
      const res = await api.runControlledTest({
        suite_id: selectedSuiteId,
        assessment_id: 'TEST-CENTER-EXEC'
      });
      if (res.success) {
        setTestResult(res);
        showToast('success', 'Test Suite Completed', `${res.passed_checks}/${res.total_checks} assertions verified.`);
      }
    } catch (err: any) {
      showToast('error', 'Execution Error', 'Failed to run controlled test.');
    } finally {
      setRunning(false);
    }
  };

  const selectedSuite = suites.find(s => s.id === selectedSuiteId);

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3 mb-1">
            <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
              <FlaskConical className="w-5 h-5 text-amber-400" />
              <span>Module 9: Test Center</span>
            </h1>
            <Badge variant="outline">SIH PS 26163</Badge>
            <span className="px-2 py-0.5 text-xs font-mono rounded bg-amber-950 text-amber-300 border border-amber-800">
              SAFE SANDBOX
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Controlled verification laboratory evaluating KAVACH's detection logic against intentionally vulnerable, non-malicious synthetic test artifacts with expected vs. actual diffs.
          </p>
        </div>

        <div className="flex items-center space-x-2 bg-slate-900/80 border border-slate-800 px-3 py-2 rounded-lg text-xs font-mono text-emerald-400">
          <ShieldCheck className="w-4 h-4" />
          <span>Zero Malware Guarantee • Safe Synthetic Testing</span>
        </div>
      </div>

      {/* Test Suites Selector */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="md:col-span-1 space-y-2">
          <label className="text-xs font-mono uppercase tracking-wider text-slate-400 block mb-1">
            Available Test Suites
          </label>
          {loading ? (
            <div className="text-xs font-mono text-slate-500 py-4">Loading test catalog...</div>
          ) : (
            suites.map(s => (
              <button
                key={s.id}
                onClick={() => {
                  setSelectedSuiteId(s.id);
                  setTestResult(null);
                }}
                className={`w-full text-left p-3 rounded-lg border text-xs font-mono transition-all flex flex-col space-y-1 ${
                  selectedSuiteId === s.id
                    ? 'bg-amber-950/40 border-amber-600/70 text-amber-300 shadow-sm'
                    : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                }`}
              >
                <div className="font-bold flex items-center justify-between">
                  <span>{s.name}</span>
                </div>
                <div className="text-[10px] text-slate-500 truncate">{s.category}</div>
              </button>
            ))
          )}
        </div>

        {/* Suite Details & Runner */}
        <div className="md:col-span-3 space-y-4">
          {selectedSuite && (
            <GlassCard className="p-5 border-slate-800 bg-slate-950/60 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
                <div>
                  <span className="text-xs font-mono text-amber-400 font-bold">{selectedSuite.id}</span>
                  <h2 className="text-base font-bold text-slate-100">{selectedSuite.name}</h2>
                  <p className="text-xs text-slate-400 mt-0.5">{selectedSuite.description}</p>
                </div>

                <button
                  onClick={handleRunTest}
                  disabled={running}
                  className="px-4 py-2 text-xs font-mono rounded-lg bg-amber-600 hover:bg-amber-500 text-black font-bold flex items-center justify-center space-x-2 transition-all shrink-0 disabled:opacity-50 cursor-pointer min-w-0 max-w-full"
                >
                  {running ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin flex-shrink-0" />
                      <span>Executing Safe Probe...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5 fill-current flex-shrink-0" />
                      <span>Run Controlled Test</span>
                    </>
                  )}
                </button>
              </div>

              {/* Suite Metadata Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
                <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase">Target Sample</div>
                  <div className="text-slate-200 font-bold truncate mt-0.5">{selectedSuite.sample_file}</div>
                </div>
                <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase">Permissions</div>
                  <div className="text-emerald-400 truncate mt-0.5">{selectedSuite.permission_required}</div>
                </div>
                <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase">Expected Assertions</div>
                  <div className="text-cyan-400 font-bold mt-0.5">{selectedSuite.expected_findings.length} Conditions</div>
                </div>
              </div>

              {/* Expected Assertions Table */}
              <div>
                <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-2 flex items-center space-x-1.5">
                  <FileCode2 className="w-3.5 h-3.5 text-slate-500" />
                  <span>Configured Assertions & Baseline Standards</span>
                </h3>
                <div className="border border-slate-800 rounded-lg overflow-hidden">
                  <table className="w-full text-xs font-mono text-left">
                    <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800">
                      <tr>
                        <th className="p-2.5">Assertion Key</th>
                        <th className="p-2.5">Expected Condition</th>
                        <th className="p-2.5">Severity</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 bg-slate-950/30">
                      {selectedSuite.expected_findings.map((ef, idx) => (
                        <tr key={idx}>
                          <td className="p-2.5 text-amber-300 font-bold">{ef.key}</td>
                          <td className="p-2.5 text-slate-300">{ef.expected}</td>
                          <td className="p-2.5">
                            <span className="px-1.5 py-0.5 text-[10px] rounded bg-slate-800 text-slate-300 border border-slate-700">
                              {ef.severity}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </GlassCard>
          )}

          {/* Test Execution Results & Expected vs Actual Diff */}
          {testResult && (
            <GlassCard className="p-5 border-amber-900/50 bg-slate-950/80 space-y-4 animate-fadeIn">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div className="flex items-center space-x-2.5">
                  {testResult.overall_status === 'VERIFIED' ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-amber-400" />
                  )}
                  <div>
                    <h3 className="text-sm font-bold text-slate-100 flex items-center space-x-2">
                      <span>Execution Result:</span>
                      <span className={testResult.overall_status === 'VERIFIED' ? 'text-emerald-400' : 'text-amber-400'}>
                        {testResult.overall_status}
                      </span>
                    </h3>
                    <p className="text-[11px] font-mono text-slate-400">
                      {testResult.passed_checks} of {testResult.total_checks} assertions verified ({testResult.duration_ms} ms)
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{testResult.timestamp}</span>
                </div>
              </div>

              {/* Side by Side Diff Matrix */}
              <div className="space-y-2">
                <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400">
                  Expected vs. Observed Technical Discrepancy Analysis
                </h4>
                <div className="border border-slate-800 rounded-lg overflow-hidden">
                  <table className="w-full text-xs font-mono text-left">
                    <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800">
                      <tr>
                        <th className="p-2.5">Check Key</th>
                        <th className="p-2.5">Expected Condition</th>
                        <th className="p-2.5">Observed In Sandbox</th>
                        <th className="p-2.5 text-center">Outcome</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                      {testResult.diff_report.map((item, idx) => (
                        <tr key={idx} className={item.match ? 'hover:bg-slate-900/40' : 'bg-amber-950/10'}>
                          <td className="p-2.5 font-bold text-slate-200">{item.key}</td>
                          <td className="p-2.5 text-slate-400">{item.expected_description}</td>
                          <td className="p-2.5 text-slate-200 font-medium">{item.observed_description}</td>
                          <td className="p-2.5 text-center">
                            {item.match ? (
                              <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                                MATCH
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-amber-950 text-amber-300 border border-amber-800">
                                DISCREPANCY
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Cryptographic Evidence Block */}
              <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400 font-bold flex items-center space-x-1.5">
                    <Hash className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Cryptographic Evidence Record ({testResult.evidence.evidence_id})</span>
                  </span>
                  <span className="text-slate-500 truncate max-w-[280px]">
                    SHA-256: <code className="text-emerald-400">{testResult.evidence.sha256_hash}</code>
                  </span>
                </div>
                <div className="bg-slate-950 rounded p-2.5 text-[11px] font-mono text-slate-300 max-h-32 overflow-y-auto space-y-1">
                  {testResult.evidence.raw_output.map((line, idx) => (
                    <div key={idx} className="text-slate-400">
                      <span className="text-slate-600 mr-2">›</span>
                      {line}
                    </div>
                  ))}
                </div>
              </div>
            </GlassCard>
          )}
        </div>
      </div>

      {/* Limitations Banner */}
      <div className="border border-slate-800/80 rounded-lg p-3 bg-slate-900/30 text-xs text-slate-500 font-mono flex items-start space-x-2">
        <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-400">Test Center Safety Scope:</strong> All test samples (configs, mock environment files, pinned dependency lists) are synthetic and intentionally vulnerable for verification benchmarking. Zero live weaponized payloads or denial-of-service tests are executed.
        </div>
      </div>
    </div>
  );
};
