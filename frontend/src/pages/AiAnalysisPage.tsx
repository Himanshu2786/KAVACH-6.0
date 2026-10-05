import React, { useState, useEffect } from 'react';
import { 
  BrainCircuit, 
  Play, 
  CheckCircle2, 
  AlertTriangle, 
  Sparkles, 
  RefreshCw, 
  Layers, 
  ShieldCheck, 
  Lock, 
  FileText, 
  Activity, 
  AlertOctagon, 
  History, 
  ExternalLink,
  ChevronRight,
  Terminal,
  Clock,
  Database,
  Search,
  BookOpen,
  Cpu
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { AiProvenanceDot } from '../components/common/AiProvenanceDot';
import { 
  Finding, 
  AiStatusResponse, 
  StructuredAiExplanation, 
  RagIndexStatus, 
  RagResponse, 
  RagRetrievedSource 
} from '../types';

export const AiAnalysisPage: React.FC = () => {
  const { activeAssessment, selectedFindingId, setSelectedFindingId, showToast } = useApp();
  const [findings, setFindings] = useState<Finding[]>([]);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [aiStatus, setAiStatus] = useState<AiStatusResponse | null>(null);
  const [ragStatus, setRagStatus] = useState<RagIndexStatus | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [startingAi, setStartingAi] = useState(false);
  const [indexingRag, setIndexingRag] = useState(false);

  // Active AI Function Tab
  const [activeFunction, setActiveFunction] = useState<
    'explain_finding' | 'explain_risk' | 'remediation_guide' | 'assessment_summary' | 'audit_summary' | 'threat_alert' | 'rag_intelligence'
  >('explain_finding');

  // Outputs
  const [explanation, setExplanation] = useState<StructuredAiExplanation | null>(null);
  const [riskData, setRiskData] = useState<any>(null);
  const [remediationData, setRemediationData] = useState<any>(null);
  const [assessmentSummaryData, setAssessmentSummaryData] = useState<StructuredAiExplanation | null>(null);
  const [auditSummaryData, setAuditSummaryData] = useState<any>(null);
  const [threatAlertText, setThreatAlertText] = useState(
    'Anomalous rate of 401 Unauthorized responses with rotating Authorization tokens detected on /api/v1/auth/verify.'
  );
  const [threatAlertResult, setThreatAlertResult] = useState<StructuredAiExplanation | null>(null);

  // RAG Ad-Hoc Query
  const [ragQueryText, setRagQueryText] = useState('How to prevent SQL injection and enforce parameterized queries in backend APIs?');
  const [ragResult, setRagResult] = useState<RagResponse | null>(null);

  const fetchStatus = async () => {
    try {
      const res = await api.getAiStatus();
      if (res.success) setAiStatus(res);
    } catch {
      // offline
    }

    try {
      const rStatus = await api.getRagStatus();
      setRagStatus(rStatus);
    } catch {
      // offline
    }
  };

  useEffect(() => {
    fetchStatus();
    if (!activeAssessment) return;
    api.getFindings({ assessment_id: activeAssessment.id })
      .then((data) => {
        setFindings(data);
        const target = data.find(f => f.id === selectedFindingId) || data[0];
        if (target) {
          setSelectedFinding(target);
          setSelectedFindingId(target.id);
        }
      })
      .catch(() => setFindings([]));
  }, [activeAssessment]);

  const handleStartLocalAi = async () => {
    setStartingAi(true);
    try {
      const res = await api.startAiService();
      showToast('info', 'AI Process', res.message);
      fetchStatus();
    } catch {
      showToast('error', 'Error', 'Failed starting local Ollama service.');
    } finally {
      setStartingAi(false);
    }
  };

  const handleRebuildRagIndex = async () => {
    setIndexingRag(true);
    try {
      const res = await api.rebuildRagIndex();
      if (res.success) {
        showToast('success', 'RAG Index Refreshed', `${res.stats.chunks_created} chunks indexed with ${res.stats.embedding_model}.`);
        fetchStatus();
      }
    } catch (err: any) {
      showToast('error', 'Index Error', err.message || 'Failed rebuilding RAG index');
    } finally {
      setIndexingRag(false);
    }
  };

  const handleSelectFinding = (finding: Finding) => {
    setSelectedFinding(finding);
    setSelectedFindingId(finding.id);
    setExplanation(null);
    setRiskData(null);
    setRemediationData(null);
  };

  const handleRunActiveFunction = async () => {
    setAnalyzing(true);
    try {
      if (activeFunction === 'explain_finding' && selectedFinding) {
        const res = await api.explainFinding(selectedFinding.id);
        if (res.success) {
          const prov = res.ai_provider || res.explanation.ai_provider;
          setExplanation({ ...res.explanation, ai_provider: prov });
          showToast('success', 'RAG Grounded Explanation Generated', `Mode: ${res.explanation.ai_mode || 'OLLAMA'}`);
        }
      } else if (activeFunction === 'explain_risk' && selectedFinding) {
        const res = await api.explainRisk(selectedFinding.id);
        if (res.success) {
          const prov = res.ai_provider || res.risk_explanation?.ai_provider;
          setRiskData({ ...res.risk_explanation, ai_provider: prov });
          showToast('success', 'Risk Breakdown Ready', `Severity reasoning synthesized.`);
        }
      } else if (activeFunction === 'remediation_guide' && selectedFinding) {
        const res = await api.getRemediationGuide(selectedFinding.id);
        if (res.success) {
          const prov = res.ai_provider || res.remediation_guide?.ai_provider;
          setRemediationData({ ...res.remediation_guide, ai_provider: prov });
          showToast('success', 'Remediation Guide Formatted', `Steps and verification checks ready.`);
        }
      } else if (activeFunction === 'assessment_summary' && activeAssessment) {
        const res = await api.getAssessmentSummary(activeAssessment.id);
        if (res.success) {
          const prov = res.ai_provider || res.summary?.ai_provider;
          setAssessmentSummaryData({ ...res.summary, ai_provider: prov });
          showToast('success', 'Assessment Summary Generated', `Executive context compiled.`);
        }
      } else if (activeFunction === 'audit_summary') {
        const res = await api.getAuditSummary(activeAssessment?.id);
        if (res.success) {
          const prov = res.ai_provider || res.audit_summary?.ai_provider;
          setAuditSummaryData({ ...res.audit_summary, ai_provider: prov });
          showToast('success', 'Audit Forensic Summary Generated', `Re-verifications and actions reviewed.`);
        }
      } else if (activeFunction === 'threat_alert') {
        const res = await api.explainThreatAlert(threatAlertText, 'API Gateway / Auth Router', 'HIGH');
        if (res.success) {
          const prov = res.ai_provider || res.alert_explanation?.ai_provider;
          setThreatAlertResult({ ...res.alert_explanation, ai_provider: prov });
          showToast('success', 'Threat Alert Explained', `Plain language translation compiled.`);
        }
      } else if (activeFunction === 'rag_intelligence') {
        const res = await api.queryRag(ragQueryText, 4);
        setRagResult(res);
        showToast('success', 'RAG Query Processed', `Retrieved ${res.retrieved_sources.length} sources.`);
      }
    } catch (err: any) {
      showToast('error', 'Execution Error', err.message || 'AI request failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const getStatusBadge = () => {
    if (!aiStatus) {
      return (
        <span className="px-2.5 py-1 text-xs font-mono rounded-full bg-rose-950/80 text-rose-300 border border-rose-800/80 flex items-center space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-rose-500" />
          <span>AI OFFLINE (Rule Mode Active)</span>
        </span>
      );
    }
    switch (aiStatus.status_code) {
      case 'ready':
        return (
          <span className="px-2.5 py-1 text-xs font-mono rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-700 shadow-[0_0_10px_rgba(16,185,129,0.3)] flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>AI READY ({aiStatus.selected_model})</span>
          </span>
        );
      case 'starting':
        return (
          <span className="px-2.5 py-1 text-xs font-mono rounded-full bg-amber-950/80 text-amber-300 border border-amber-800 animate-pulse flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            <span>AI STARTING...</span>
          </span>
        );
      case 'model_unavailable':
        return (
          <span className="px-2.5 py-1 text-xs font-mono rounded-full bg-orange-950/80 text-orange-300 border border-orange-800 flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-orange-400" />
            <span>MODEL UNAVAILABLE ({aiStatus.selected_model})</span>
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 text-xs font-mono rounded-full bg-rose-950/80 text-rose-300 border border-rose-800/80 flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-rose-500" />
            <span>AI OFFLINE (Rule Mode Active)</span>
          </span>
        );
    }
  };

  // Helper component to render Retrieved Knowledge Chunks
  const renderRetrievedSources = (sources: RagRetrievedSource[]) => {
    if (!sources || sources.length === 0) return null;

    return (
      <div className="p-4 rounded-xl bg-slate-950/90 border border-cyan-800/50 space-y-3 font-mono text-xs">
        <div className="flex items-center justify-between border-b border-cyan-900/40 pb-2">
          <div className="flex items-center space-x-2 text-cyan-300 font-bold">
            <Database className="w-4 h-4 text-cyan-400" />
            <span className="uppercase tracking-wider">Retrieved Security Knowledge (RAG Evidence Grounding)</span>
          </div>
          <span className="text-[11px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/60">
            {sources.length} Sources Injected
          </span>
        </div>

        <p className="text-[11px] text-slate-400">
          The following authoritative security standards were retrieved from the KAVACH vector store and supplied directly to the LLM prompt:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {sources.map((s, idx) => {
            const matchPct = Math.round(s.score * 100);
            return (
              <div 
                key={s.chunk_id || idx}
                className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 hover:border-cyan-700/60 transition-all space-y-1.5"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center space-x-1.5 text-slate-200 font-bold truncate">
                    <BookOpen className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                    <span className="truncate">{s.title}</span>
                  </div>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold shrink-0 ${
                    matchPct >= 70 ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                  }`}>
                    {matchPct}% Match
                  </span>
                </div>

                <div className="flex items-center space-x-2 text-[10px] text-slate-400 font-mono">
                  {s.cwe_id && <span className="text-purple-300 bg-purple-950/60 px-1.5 py-0.2 rounded">{s.cwe_id}</span>}
                  {s.owasp_category && <span className="text-amber-300 bg-amber-950/60 px-1.5 py-0.2 rounded truncate">{s.owasp_category}</span>}
                </div>

                <div className="text-[11px] text-slate-300 line-clamp-3 bg-slate-950/60 p-2 rounded border border-slate-800/80">
                  {s.text}
                </div>

                <div className="text-[10px] text-slate-500 truncate pt-0.5">
                  Source: {s.source}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3 mb-1">
            <h1 className="text-xl font-bold tracking-wide text-slate-100 uppercase font-mono-code flex items-center space-x-2">
              <BrainCircuit className="w-5 h-5 text-purple-400" />
              <span>Local AI & RAG Security Intelligence Engine</span>
            </h1>
            <Badge variant="outline">Module 6</Badge>
          </div>
          <p className="text-sm text-slate-400">
            Retrieval-Augmented Generation (RAG): Ingests CWE/OWASP knowledge, indexes local vectors, and passes grounded context to Ollama.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {getStatusBadge()}
          {aiStatus?.status_code !== 'ready' && (
            <button
              onClick={handleStartLocalAi}
              disabled={startingAi}
              className="px-3 py-1 text-xs font-mono rounded border border-purple-700/80 bg-purple-950/40 text-purple-300 hover:bg-purple-900/50 flex items-center space-x-1 disabled:opacity-50"
            >
              <Sparkles className="w-3 h-3 text-amber-400" />
              <span>{startingAi ? 'Starting...' : 'Start Ollama'}</span>
            </button>
          )}
        </div>
      </div>

      {/* RAG & Data Masking Status Bar */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
        <div className="p-3 rounded-lg bg-slate-900/80 border border-purple-800/40 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-purple-300">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span><strong>Data Masking Shield:</strong> Secrets/Tokens masked before model ingestion.</span>
          </div>
          <span className="text-[10px] text-slate-500 shrink-0">127.0.0.1:11434</span>
        </div>

        <div className="p-3 rounded-lg bg-slate-900/80 border border-cyan-800/40 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-cyan-300 truncate">
            <Database className="w-4 h-4 text-cyan-400 shrink-0" />
            <span className="truncate">
              <strong>RAG Vector Store:</strong> {ragStatus?.indexed_chunks_count || 51} Chunks ({ragStatus?.retrieval_mode || 'VECTOR INDEX'})
            </span>
          </div>
          <button
            onClick={handleRebuildRagIndex}
            disabled={indexingRag}
            className="px-2.5 py-1 text-[11px] rounded bg-cyan-950 text-cyan-300 border border-cyan-800 hover:bg-cyan-900/60 transition-all flex items-center space-x-1 shrink-0 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${indexingRag ? 'animate-spin' : ''}`} />
            <span>{indexingRag ? 'Indexing...' : 'Refresh Index'}</span>
          </button>
        </div>
      </div>

      {/* 7 AI & RAG Functions Tab Selector */}
      <div className="flex items-center space-x-1 border-b border-slate-800 overflow-x-auto pb-1 scrollbar-none text-xs font-mono">
        <button
          onClick={() => setActiveFunction('explain_finding')}
          className={`px-3 py-2 rounded-t-lg transition-all flex items-center space-x-1.5 whitespace-nowrap ${
            activeFunction === 'explain_finding'
              ? 'bg-purple-950/80 text-purple-300 border-b-2 border-purple-400 font-bold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>1. Simple Explanation</span>
        </button>

        <button
          onClick={() => setActiveFunction('explain_risk')}
          className={`px-3 py-2 rounded-t-lg transition-all flex items-center space-x-1.5 whitespace-nowrap ${
            activeFunction === 'explain_risk'
              ? 'bg-purple-950/80 text-purple-300 border-b-2 border-purple-400 font-bold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <AlertOctagon className="w-3.5 h-3.5" />
          <span>2. Risk Explanation</span>
        </button>

        <button
          onClick={() => setActiveFunction('remediation_guide')}
          className={`px-3 py-2 rounded-t-lg transition-all flex items-center space-x-1.5 whitespace-nowrap ${
            activeFunction === 'remediation_guide'
              ? 'bg-purple-950/80 text-purple-300 border-b-2 border-purple-400 font-bold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>3. Remediation Guide</span>
        </button>

        <button
          onClick={() => setActiveFunction('assessment_summary')}
          className={`px-3 py-2 rounded-t-lg transition-all flex items-center space-x-1.5 whitespace-nowrap ${
            activeFunction === 'assessment_summary'
              ? 'bg-purple-950/80 text-purple-300 border-b-2 border-purple-400 font-bold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>4. Assessment Summary</span>
        </button>

        <button
          onClick={() => setActiveFunction('audit_summary')}
          className={`px-3 py-2 rounded-t-lg transition-all flex items-center space-x-1.5 whitespace-nowrap ${
            activeFunction === 'audit_summary'
              ? 'bg-purple-950/80 text-purple-300 border-b-2 border-purple-400 font-bold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <History className="w-3.5 h-3.5" />
          <span>5. Audit Summary</span>
        </button>

        <button
          onClick={() => setActiveFunction('threat_alert')}
          className={`px-3 py-2 rounded-t-lg transition-all flex items-center space-x-1.5 whitespace-nowrap ${
            activeFunction === 'threat_alert'
              ? 'bg-purple-950/80 text-purple-300 border-b-2 border-purple-400 font-bold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          <span>6. Threat Alert Explanation</span>
        </button>

        <button
          onClick={() => setActiveFunction('rag_intelligence')}
          className={`px-3 py-2 rounded-t-lg transition-all flex items-center space-x-1.5 whitespace-nowrap ${
            activeFunction === 'rag_intelligence'
              ? 'bg-cyan-950/80 text-cyan-300 border-b-2 border-cyan-400 font-bold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Search className="w-3.5 h-3.5 text-cyan-400" />
          <span>7. RAG Security Intelligence</span>
        </button>
      </div>

      {/* Main Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Finding Selector (For Functions 1, 2, 3) */}
        {['explain_finding', 'explain_risk', 'remediation_guide'].includes(activeFunction) && (
          <div className="space-y-3">
            <div className="text-xs font-mono uppercase font-bold tracking-wide text-slate-400">
              Select Validated Finding ({findings.length})
            </div>
            <div className="space-y-2 max-h-[550px] overflow-y-auto pr-1">
              {findings.map((f) => {
                const isSelected = selectedFinding?.id === f.id;
                return (
                  <div
                    key={f.id}
                    onClick={() => handleSelectFinding(f)}
                    className={`p-3 rounded-lg border cursor-pointer font-mono text-xs transition-all ${
                      isSelected
                        ? 'bg-purple-950/60 border-purple-500 text-purple-200 shadow-md font-bold'
                        : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-cyan-400 font-bold">{f.id}</span>
                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">
                        {f.base_severity}
                      </span>
                    </div>
                    <div className="text-slate-200 font-medium truncate">{f.title}</div>
                    <div className="text-[10px] text-slate-500 mt-1 truncate">{f.affected_component}</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Function 6: Threat Alert Input */}
        {activeFunction === 'threat_alert' && (
          <div className="space-y-3">
            <div className="text-xs font-mono uppercase font-bold tracking-wide text-slate-400">
              Raw Security Threat Alert
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3 font-mono text-xs">
              <label className="text-slate-400 block text-[11px]">Paste or Edit Raw Threat Alert Indicator:</label>
              <textarea
                rows={5}
                value={threatAlertText}
                onChange={e => setThreatAlertText(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded p-2.5 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
              />
              <div className="text-[10px] text-slate-500">
                Ollama will translate this technical alert into plain language and structured remediation actions.
              </div>
            </div>
          </div>
        )}

        {/* Function 7: RAG Query Input */}
        {activeFunction === 'rag_intelligence' && (
          <div className="space-y-3">
            <div className="text-xs font-mono uppercase font-bold tracking-wide text-slate-400">
              RAG Knowledge Search
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-cyan-900/40 space-y-3 font-mono text-xs">
              <label className="text-slate-400 block text-[11px]">Security Query or Architecture Topic:</label>
              <textarea
                rows={4}
                value={ragQueryText}
                onChange={e => setRagQueryText(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded p-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                placeholder="e.g. How to mitigate exposed AWS Access Keys and rotate credentials?"
              />
              <div className="text-[10px] text-slate-400 flex items-center space-x-1">
                <Cpu className="w-3 h-3 text-cyan-400" />
                <span>Retrieves top-4 semantic chunks & grounds Ollama response.</span>
              </div>
            </div>
          </div>
        )}

        {/* Functions 4 & 5 Context Column */}
        {['assessment_summary', 'audit_summary'].includes(activeFunction) && (
          <div className="space-y-3">
            <div className="text-xs font-mono uppercase font-bold tracking-wide text-slate-400">
              Scope & Target Information
            </div>
            <GlassCard className="p-4 border-slate-800 bg-slate-950/60 font-mono text-xs space-y-2.5">
              <div>
                <div className="text-[10px] text-slate-500 uppercase">Assessment Target</div>
                <div className="text-slate-200 font-bold">{activeAssessment?.name || 'Active Assessment'}</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500 uppercase">Target Endpoint</div>
                <div className="text-cyan-400 truncate">{activeAssessment?.target_url || 'http://localhost'}</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-500 uppercase">Total Cataloged Findings</div>
                <div className="text-amber-400 font-bold">{findings.length} findings</div>
              </div>
              <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-400">
                Evaluates entire assessment progress, priority actions, and re-verification evidence.
              </div>
            </GlassCard>
          </div>
        )}

        {/* Right 2 Columns: AI & RAG Explanation */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-mono uppercase tracking-wider text-slate-400">
              {activeFunction === 'explain_finding' && 'Standardized 7-Section Explanation (RAG Grounded)'}
              {activeFunction === 'explain_risk' && 'Risk & Impact Breakdown'}
              {activeFunction === 'remediation_guide' && 'Remediation & Technical Verification'}
              {activeFunction === 'assessment_summary' && 'Executive Assessment Summary'}
              {activeFunction === 'audit_summary' && 'Forensic Audit & Action History'}
              {activeFunction === 'threat_alert' && 'Threat Alert Plain Language Translation'}
              {activeFunction === 'rag_intelligence' && 'RAG Grounded Security Intelligence Analysis'}
            </h2>

            <button
              onClick={handleRunActiveFunction}
              disabled={analyzing}
              className={`px-4 py-2 rounded-lg text-white font-bold font-mono text-xs flex items-center space-x-2 transition-all shadow-md disabled:opacity-50 ${
                activeFunction === 'rag_intelligence' 
                  ? 'bg-cyan-600 hover:bg-cyan-500' 
                  : 'bg-purple-600 hover:bg-purple-500'
              }`}
            >
              {analyzing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
              <span>{analyzing ? 'Reasoning...' : (activeFunction === 'rag_intelligence' ? 'Run RAG Query' : 'Run AI Explanation')}</span>
            </button>
          </div>

          {/* RAG Grounding Sources Display (Function 1 or 7) */}
          {activeFunction === 'explain_finding' && explanation?.retrieved_sources && renderRetrievedSources(explanation.retrieved_sources)}
          {activeFunction === 'rag_intelligence' && ragResult?.retrieved_sources && renderRetrievedSources(ragResult.retrieved_sources)}

          {/* Render 7-Section Output Card when available */}
          {(explanation || assessmentSummaryData || threatAlertResult || ragResult?.answer) && (
            (() => {
              const activeResult = (activeFunction === 'rag_intelligence' ? (ragResult?.answer ? { ...ragResult.answer, ai_provider: ragResult.ai_provider || (ragResult.answer as any).ai_provider, model_used: ragResult.model_used } : null) : null) || explanation || assessmentSummaryData || threatAlertResult;
              if (!activeResult) return null;

              return (
                <div className="relative space-y-3 font-mono animate-fadeIn">
                  {/* Mode Banner */}
                  <div className="flex items-center justify-between p-2.5 rounded bg-slate-900/90 border border-slate-800 text-xs">
                    <span className="text-slate-400">Engine Source:</span>
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-purple-300">
                        {activeResult.ai_mode === 'OLLAMA_RAG' || activeResult.ai_mode === 'OLLAMA_LLM' 
                          ? `Local Ollama (${activeResult.model_used || 'phi3'})` 
                          : (activeResult.model_used || 'KAVACH Grounded Engine')}
                      </span>
                      {activeResult.ai_provider === 'ollama' && (
                        <AiProvenanceDot provider={activeResult.ai_provider} />
                      )}
                    </div>
                  </div>

                  {/* Section 1: WHAT WAS FOUND */}
                  <div className="p-3.5 rounded-lg bg-slate-950/70 border border-purple-800/40 space-y-1">
                    <div className="text-[11px] uppercase font-bold text-purple-400 flex items-center space-x-1.5">
                      <span className="w-2 h-2 rounded-full bg-purple-400" />
                      <span>1. WHAT WAS FOUND</span>
                    </div>
                    <p className="text-xs text-slate-200 leading-relaxed">{activeResult.what_was_found}</p>
                  </div>

                  {/* Section 2: WHERE */}
                  <div className="p-3.5 rounded-lg bg-slate-950/70 border border-slate-800 space-y-1">
                    <div className="text-[11px] uppercase font-bold text-cyan-400 flex items-center space-x-1.5">
                      <span className="w-2 h-2 rounded-full bg-cyan-400" />
                      <span>2. WHERE</span>
                    </div>
                    <p className="text-xs text-slate-200 font-mono">{activeResult.where}</p>
                  </div>

                  {/* Section 3: WHY IT MATTERS */}
                  <div className="p-3.5 rounded-lg bg-slate-950/70 border border-amber-900/40 space-y-1">
                    <div className="text-[11px] uppercase font-bold text-amber-400 flex items-center space-x-1.5">
                      <span className="w-2 h-2 rounded-full bg-amber-400" />
                      <span>3. WHY IT MATTERS</span>
                    </div>
                    <p className="text-xs text-slate-200 leading-relaxed">{activeResult.why_it_matters}</p>
                  </div>

                  {/* Section 4: POSSIBLE IMPACT */}
                  <div className="p-3.5 rounded-lg bg-slate-950/70 border border-rose-900/40 space-y-1">
                    <div className="text-[11px] uppercase font-bold text-rose-400 flex items-center space-x-1.5">
                      <span className="w-2 h-2 rounded-full bg-rose-400" />
                      <span>4. POSSIBLE IMPACT</span>
                    </div>
                    <p className="text-xs text-slate-200 leading-relaxed">{activeResult.possible_impact}</p>
                  </div>

                  {/* Section 5: RECOMMENDED ACTION */}
                  <div className="p-3.5 rounded-lg bg-slate-950/70 border border-indigo-900/40 space-y-1">
                    <div className="text-[11px] uppercase font-bold text-indigo-400 flex items-center space-x-1.5">
                      <span className="w-2 h-2 rounded-full bg-indigo-400" />
                      <span>5. RECOMMENDED ACTION</span>
                    </div>
                    <p className="text-xs text-slate-200 leading-relaxed">{activeResult.recommended_action}</p>
                  </div>

                  {/* Section 6: HOW TO FIX */}
                  <div className="p-3.5 rounded-lg bg-slate-950/70 border border-emerald-900/40 space-y-1">
                    <div className="text-[11px] uppercase font-bold text-emerald-400 flex items-center space-x-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      <span>6. HOW TO FIX</span>
                    </div>
                    <pre className="text-xs text-emerald-300 font-mono whitespace-pre-line bg-slate-900/60 p-2.5 rounded border border-emerald-950">
                      {activeResult.how_to_fix}
                    </pre>
                  </div>

                  {/* Section 7: HOW TO VERIFY */}
                  <div className="p-3.5 rounded-lg bg-slate-950/70 border border-blue-900/40 space-y-1">
                    <div className="text-[11px] uppercase font-bold text-blue-400 flex items-center space-x-1.5">
                      <Terminal className="w-3.5 h-3.5" />
                      <span>7. HOW TO VERIFY (SAFE PROBE)</span>
                    </div>
                    <pre className="text-xs text-blue-300 font-mono bg-slate-900/60 p-2.5 rounded border border-blue-950 whitespace-pre-wrap">
                      {activeResult.how_to_verify}
                    </pre>
                  </div>
                </div>
              );
            })()
          )}

          {/* Render Function 2: Risk Explanation */}
          {activeFunction === 'explain_risk' && riskData && (
            <div className="space-y-3 font-mono text-xs animate-fadeIn">
              {/* Mode Banner */}
              <div className="flex items-center justify-between p-2.5 rounded bg-slate-900/90 border border-slate-800 text-xs">
                <span className="text-slate-400">Engine Source:</span>
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-purple-300">
                    {riskData.ai_provider === 'ollama' ? 'Local Ollama' : 'KAVACH Rule Engine'}
                  </span>
                  {riskData.ai_provider === 'ollama' && (
                    <AiProvenanceDot provider={riskData.ai_provider} />
                  )}
                </div>
              </div>
              <div className="p-4 rounded-lg bg-slate-950 border border-rose-900/50 space-y-2">
                <div className="text-xs font-bold text-rose-400 uppercase">Reason for Severity Rating ({riskData.severity})</div>
                <p className="text-slate-200">{riskData.reason_for_severity}</p>
              </div>
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-amber-400 uppercase">Affected Component & Surface</div>
                <p className="text-slate-200">{riskData.affected_component}</p>
              </div>
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-slate-300 uppercase">Estimated Impact</div>
                <p className="text-slate-200">{riskData.possible_impact}</p>
              </div>
            </div>
          )}

          {/* Render Function 3: Remediation Guide */}
          {activeFunction === 'remediation_guide' && remediationData && (
            <div className="space-y-3 font-mono text-xs animate-fadeIn">
              {/* Mode Banner */}
              <div className="flex items-center justify-between p-2.5 rounded bg-slate-900/90 border border-slate-800 text-xs">
                <span className="text-slate-400">Engine Source:</span>
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-purple-300">
                    {remediationData.ai_provider === 'ollama' ? 'Local Ollama' : 'KAVACH Rule Engine'}
                  </span>
                  {remediationData.ai_provider === 'ollama' && (
                    <AiProvenanceDot provider={remediationData.ai_provider} />
                  )}
                </div>
              </div>
              <div className="p-4 rounded-lg bg-slate-950 border border-emerald-900/50 space-y-2">
                <div className="text-xs font-bold text-emerald-400 uppercase">Step-by-Step Remediation Strategy</div>
                <pre className="text-slate-200 whitespace-pre-line">{remediationData.how_to_fix}</pre>
              </div>
              <div className="p-4 rounded-lg bg-slate-950 border border-blue-900/50 space-y-2">
                <div className="text-xs font-bold text-blue-400 uppercase">Safe Fix Verification Check</div>
                <pre className="text-blue-300 whitespace-pre-wrap bg-slate-900/60 p-2.5 rounded">{remediationData.how_to_verify}</pre>
              </div>
            </div>
          )}

          {/* Render Function 5: Audit Summary */}
          {activeFunction === 'audit_summary' && auditSummaryData && (
            <div className="space-y-3 font-mono text-xs animate-fadeIn">
              {/* Mode Banner */}
              <div className="flex items-center justify-between p-2.5 rounded bg-slate-900/90 border border-slate-800 text-xs">
                <span className="text-slate-400">Engine Source:</span>
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-purple-300">
                    {auditSummaryData.ai_provider === 'ollama' ? 'Local Ollama' : 'KAVACH Rule Engine'}
                  </span>
                  {auditSummaryData.ai_provider === 'ollama' && (
                    <AiProvenanceDot provider={auditSummaryData.ai_provider} />
                  )}
                </div>
              </div>
              <div className="p-4 rounded-lg bg-slate-950 border border-purple-900/50 space-y-2">
                <div className="text-xs font-bold text-purple-400 uppercase">Forensic Ledger Overview</div>
                <p className="text-slate-200">{auditSummaryData.what_was_found}</p>
                <div className="flex items-center space-x-4 pt-2 text-[11px] text-slate-400">
                  <span>Events Audited: <strong className="text-cyan-400">{auditSummaryData.total_events_audited}</strong></span>
                  <span>Patches Proven: <strong className="text-emerald-400">{auditSummaryData.reverifications_resolved}</strong></span>
                </div>
              </div>
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                <div className="text-xs font-bold text-emerald-400 uppercase">Verification Integrity</div>
                <p className="text-slate-200">{auditSummaryData.how_to_verify}</p>
              </div>
            </div>
          )}

          {/* Initial Blank State */}
          {!explanation && !riskData && !remediationData && !assessmentSummaryData && !auditSummaryData && !threatAlertResult && !ragResult && (
            <div className="text-center py-20 glass-panel rounded-xl font-mono text-xs text-slate-400 border border-slate-800 space-y-2">
              <Sparkles className="w-6 h-6 text-purple-400 mx-auto" />
              <p>Click "Run AI Explanation" to generate standardized 7-section structured insights with RAG evidence grounding.</p>
              <p className="text-[11px] text-slate-500">Operates 100% locally via Ollama or deterministic vector fallback.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
