import React, { useState, useEffect, useRef } from 'react';
import {
  Globe,
  Shield,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Clock,
  ExternalLink,
  Layers,
  Search,
  Filter,
  Info,
  MapPin,
  Cpu,
  Fingerprint,
  Radio,
  ArrowRight,
  Database,
  Sparkles,
  ShieldAlert,
  ChevronRight,
  AlertOctagon,
  FileCheck2
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { WorldEvent, WorldCorrelationItem, WorldSourceStatus } from '../types';
import { WorldMonitorGeospatialView } from '../components/visual/WorldMonitorGeospatialView';
import { formatToIST, formatToISTDateOnly } from '../utils/time';

export const WorldMonitorPage: React.FC = () => {
  const {
    activeAssessment,
    urlAssessmentState,
    navigate,
    selectedWorldEventId,
    setSelectedWorldEventId,
    showToast
  } = useApp();

  const [events, setEvents] = useState<WorldEvent[]>([]);
  const [sources, setSources] = useState<WorldSourceStatus[]>([]);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [feedMode, setFeedMode] = useState<'LIVE' | 'DEMO'>('DEMO');
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [correlations, setCorrelations] = useState<WorldCorrelationItem[]>([]);

  // Filter states
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Backend assessment-scoped finding count — same source of truth as
  // FindingsPage, EvidenceValidationPage, RiskScoring, and ReportExport.
  // Fetched via api.getFindings({ assessment_id }) to count ONLY findings
  // belonging to the currently active backend assessment.
  const [backendFindingsCount, setBackendFindingsCount] = useState<number>(activeAssessment?.total_findings ?? 0);

  // Load events & sources
  const fetchWorldData = async (modeArg?: 'live' | 'demo') => {
    try {
      const res = await api.getWorldEvents({
        category: selectedCategory,
        severity: selectedSeverity,
        time_range: selectedTimeRange,
        search: searchTerm,
        mode: modeArg
      });
      if (res.success) {
        setEvents(res.events);
        setSources(res.sources || []);
        setLastUpdated(res.last_updated);
        setFeedMode(res.mode);
        if (res.events.length > 0 && !selectedEventId) {
          setSelectedEventId(res.events[0].id);
        }
      }
    } catch {
      showToast('error', 'World Monitor', 'Failed to retrieve situational events.');
    } finally {
      setLoading(false);
    }
  };

  // Run correlation against active assessment or URL assessment findings
  const computeCorrelations = async () => {
    const targetUrl = urlAssessmentState.result?.target_url || activeAssessment?.target_url || '';
    const hostname = urlAssessmentState.result?.hostname || activeAssessment?.name || '';
    const localFindings = urlAssessmentState.result?.findings || [];

    try {
      const res = await api.correlateWorldEvents({
        target_url: targetUrl,
        hostname: hostname,
        findings: localFindings
      });
      if (res.success) {
        setCorrelations(res.correlations);
      }
    } catch {
      // Correlation engine offline fallback
    }
  };

  useEffect(() => {
    fetchWorldData();
  }, [selectedCategory, selectedSeverity, selectedTimeRange, searchTerm]);

  useEffect(() => {
    computeCorrelations();
  }, [urlAssessmentState.result, activeAssessment, events]);

  // Fetch backend assessment-scoped finding count whenever the active assessment
  // changes. Mirrors FindingsPage line 59: api.getFindings({ assessment_id }).
  // This is the ONLY source used for the "local findings" count in the alert.
  useEffect(() => {
    if (activeAssessment?.id) {
      if (typeof activeAssessment.total_findings === 'number') {
        setBackendFindingsCount(activeAssessment.total_findings);
      }
      api.getFindings({ assessment_id: activeAssessment.id })
        .then((data) => setBackendFindingsCount(data.length))
        .catch(() => setBackendFindingsCount(activeAssessment.total_findings ?? 0));
    } else {
      setBackendFindingsCount(0);
    }
  }, [activeAssessment?.id, activeAssessment?.total_findings]);

  // Sync selected event if triggered from external page (e.g. Findings page)
  useEffect(() => {
    if (selectedWorldEventId) {
      setSelectedEventId(selectedWorldEventId);
    }
  }, [selectedWorldEventId]);

  const handleRefresh = async (targetMode?: 'live' | 'demo') => {
    if (isRefreshing) return;
    setIsRefreshing(true);
    try {
      const res = await api.refreshWorldEvents(targetMode);
      if (res.success) {
        setEvents(res.events);
        setSources(res.sources || []);
        setLastUpdated(res.last_updated);
        setFeedMode(res.mode);
        showToast('success', 'World Monitor', `Successfully synced ${res.events.length} situational events.`);
      }
    } catch {
      showToast('error', 'World Monitor', 'Failed to refresh situational events.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const selectedEvent = events.find(e => e.id === selectedEventId) || events[0] || null;
  const activeCorrelation = correlations.find(c => c.event_id === selectedEvent?.id) || null;

  // Filter geo-tagged events for map
  const geoEvents = events.filter(e => e.location && e.location.has_coordinates);

  const categories = [
    { id: 'ALL', label: 'All Sectors' },
    { id: 'Exploited CVE', label: 'Exploited CVEs' },
    { id: 'Critical Infrastructure', label: 'Infrastructure' },
    { id: 'Zero-Day Advisory', label: 'Zero-Days' },
    { id: 'Government Directive', label: 'Gov Directives' },
  ];

  return (
    <div className="space-y-6 pb-12 animate-in fade-in duration-300">

      {/* ── Top Header Bar ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/[0.08] pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wide uppercase border ${
              feedMode === 'LIVE'
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${feedMode === 'LIVE' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              WORLD MONITOR: {feedMode === 'LIVE' ? 'LIVE DATA' : 'DEMO INTELLIGENCE'}
            </span>
            {feedMode === 'DEMO' && (
              <span className="text-[11px] font-mono text-neutral-400">
                (Verified local demonstration fixtures)
              </span>
            )}
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <Globe className="w-7 h-7 text-white" />
            World Situational Monitor
          </h1>
          <p className="text-neutral-400 text-xs sm:text-sm mt-1">
            Authoritative global cybersecurity advisories (CISA, NVD, CERT) correlated with KAVACH local assessment data.
          </p>
        </div>

        {/* Header Metrics & Refresh Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="p-2 px-3 rounded-xl bg-black/60 border border-white/[0.08] text-xs font-mono space-y-0.5">
            <div className="text-[10px] text-neutral-500 uppercase">Last Synchronized</div>
            <div className="text-neutral-200 flex items-center gap-1.5 font-semibold">
              <Clock className="w-3 h-3 text-neutral-400" />
              {lastUpdated || 'Initial load'}
            </div>
          </div>

          <div className="flex items-center gap-2 bg-black/60 p-1 rounded-xl border border-white/[0.1]">
            <button
              id="world-monitor-live-feed-btn"
              onClick={() => handleRefresh('live')}
              disabled={isRefreshing}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer ${
                feedMode === 'LIVE'
                  ? 'bg-emerald-500 text-black font-bold shadow-[0_0_12px_rgba(16,185,129,0.4)]'
                  : 'text-neutral-400 hover:text-white hover:bg-white/[0.06]'
              }`}
            >
              <Radio className={`w-3 h-3 ${feedMode === 'LIVE' ? 'animate-pulse' : ''}`} />
              Live Feed
            </button>
            <button
              id="world-monitor-demo-fixtures-btn"
              onClick={() => handleRefresh('demo')}
              disabled={isRefreshing}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer ${
                feedMode === 'DEMO'
                  ? 'bg-white text-black font-bold shadow-sm'
                  : 'text-neutral-400 hover:text-white hover:bg-white/[0.06]'
              }`}
            >
              <Sparkles className="w-3 h-3" />
              Demo Fixtures
            </button>
          </div>

          <button
            onClick={() => handleRefresh()}
            disabled={isRefreshing}
            className="btn-primary px-3.5 py-2 text-xs font-semibold rounded-xl flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? 'Syncing...' : 'Refresh Sources'}
          </button>
        </div>
      </div>

      {/* ── Active Target Context Alert ── */}
      {/* Renders for BOTH backend assessments (activeAssessment) and URL scan results.
           Local findings count source of truth priority:
           1. activeAssessment set → backendFindingsCount (from api.getFindings scoped to assessment_id)
           2. URL scan only → urlAssessmentState.result.findings?.length */}
      {(activeAssessment || urlAssessmentState.result) && (
        <div className="p-3.5 glass-level-1 border border-white/10 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
          <div className="flex items-center gap-2.5">
            <ShieldAlert className="w-4 h-4 text-cyan-400 shrink-0" />
            <span className="text-neutral-300">
              Active Assessment Target:{' '}
              <strong className="text-white">
                {urlAssessmentState.result?.hostname
                  || (activeAssessment?.target_url
                      ? activeAssessment.target_url.replace(/^https?:\/\//i, '').replace(/\/.*$/, '')
                      : '')
                  || activeAssessment?.name
                  || 'Unknown Target'}
              </strong>
              {' '}(
              {activeAssessment
                ? backendFindingsCount
                : (urlAssessmentState.result?.findings?.length ?? urlAssessmentState.result?.findings_count ?? 0)
              } local {(activeAssessment ? backendFindingsCount : (urlAssessmentState.result?.findings?.length ?? urlAssessmentState.result?.findings_count ?? 0)) === 1 ? 'finding' : 'findings'})
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-neutral-400">Correlated Global Advisories:</span>
            <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/30">
              {correlations.length} Detected
            </span>
          </div>
        </div>
      )}

      {/* ── Main 3-Column Command Center Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* ══ LEFT COLUMN: Search, Filters & Situational Event Feed (4 Cols) ══ */}
        <div className="lg:col-span-4 space-y-4">
          <div className="glass-level-2 rounded-2xl p-4 space-y-3">
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5 font-mono">
                <Filter className="w-3.5 h-3.5 text-neutral-400" />
                Advisory Feeds ({events.length})
              </span>
              <span className="text-[10px] font-mono text-neutral-500">Public & Authoritative</span>
            </div>

            {/* Search Input */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-neutral-500" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search CVE, technology, advisory..."
                className="w-full glass-input rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder-neutral-500 font-mono"
              />
            </div>

            {/* Category Filter Pills */}
            <div className="flex flex-wrap gap-1">
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`px-2 py-1 rounded-lg text-[10px] font-mono transition-all cursor-pointer ${
                    selectedCategory === cat.id
                      ? 'bg-white text-black font-bold shadow-sm'
                      : 'glass-panel text-neutral-400 hover:text-neutral-200'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Time & Severity Selectors */}
            <div className="grid grid-cols-2 gap-2 pt-1">
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="glass-select rounded-lg px-2 py-1 text-[11px] font-mono text-neutral-300 outline-none"
              >
                <option value="all">Time: All Time</option>
                <option value="24h">Time: Last 24 Hours</option>
                <option value="7d">Time: Last 7 Days</option>
                <option value="30d">Time: Last 30 Days</option>
              </select>

              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="glass-select rounded-lg px-2 py-1 text-[11px] font-mono text-neutral-300 outline-none"
              >
                <option value="ALL">Severity: All</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>

          {/* Event Feed List */}
          <div className="space-y-2.5">
            {events.length === 0 ? (
              <div className="p-8 text-center glass-level-1 rounded-2xl font-mono text-xs text-neutral-500">
                <AlertOctagon className="w-8 h-8 text-neutral-600 mx-auto mb-2" />
                <p className="text-neutral-300 font-semibold">No Advisories Found</p>
                <p className="text-[11px] mt-1">Try resetting filters or click Refresh Sources.</p>
              </div>
            ) : (
              events.map((ev) => {
                const isSelected = ev.id === selectedEvent?.id;
                const isCorrelated = correlations.some(c => c.event_id === ev.id);

                return (
                  <div
                    key={ev.id}
                    onClick={() => setSelectedEventId(ev.id)}
                    className={`p-3.5 rounded-2xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-white/[0.08] border-white/30 shadow-lg'
                        : 'glass-level-1 border-white/[0.06] hover:border-white/15 hover:bg-white/[0.03]'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <div className="flex items-center gap-1.5">
                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold uppercase border ${
                          ev.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                          ev.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-400 border-orange-500/30' :
                          'bg-amber-500/20 text-amber-400 border-amber-500/30'
                        }`}>
                          {ev.severity}
                        </span>
                        <span className="text-[10px] font-mono text-neutral-400 truncate max-w-[120px]">
                          {ev.category}
                        </span>
                      </div>

                      {/* Correlation Tag */}
                      {isCorrelated && (
                        <span className="px-1.5 py-0.5 rounded-full text-[9px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 animate-pulse">
                          CORRELATED
                        </span>
                      )}
                    </div>

                    <h4 className="text-xs font-bold text-white line-clamp-2 mb-1.5 leading-snug">
                      {ev.title}
                    </h4>

                    <div className="flex flex-wrap items-center justify-between gap-2 text-[10px] font-mono text-neutral-500 pt-1 border-t border-white/[0.04]">
                      <span className="text-neutral-400">{ev.source}</span>
                      {ev.location && ev.location.has_coordinates && (
                        <span className="flex items-center gap-1 text-cyan-400">
                          <MapPin className="w-2.5 h-2.5" />
                          {ev.location.country}
                        </span>
                      )}
                      <span>{formatToISTDateOnly(ev.published_at)}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* ══ CENTER & RIGHT COLUMNS: Situational Map & Inspector (8 Cols) ══ */}
        <div className="lg:col-span-8 space-y-6">

          {/* ── Situational World Map & 2D/3D Geospatial Globe Layer ── */}
          <div className="glass-level-2 rounded-2xl p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/[0.08] pb-3">
              <div>
                <span className="text-xs font-mono text-neutral-500 uppercase tracking-wider block">Visual Geospatial Layer</span>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Radio className="w-4 h-4 text-emerald-400" />
                  Verified Geographic Incidents & Regional Advisories ({geoEvents.length})
                </h3>
              </div>
              <div className="text-[11px] font-mono text-neutral-400 flex items-center gap-3">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-400" /> Critical</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-orange-400" /> High</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-cyan-400" /> Correlated</span>
              </div>
            </div>

            {/* Interactive 2D / 3D Geospatial Globe View */}
            <WorldMonitorGeospatialView
              events={events}
              selectedEventId={selectedEventId}
              correlations={correlations}
              onSelectEvent={(id) => setSelectedEventId(id)}
            />

            {/* Non-geographic note banner — strict adherence to requirement */}
            <div className="p-3 glass-panel rounded-xl flex items-center justify-between text-xs text-neutral-400 font-mono">
              <span className="flex items-center gap-2">
                <Info className="w-3.5 h-3.5 text-neutral-400 shrink-0" />
                Global / Software CVE Advisories without single physical locations are listed in the feed without fake map points.
              </span>
              <span className="text-neutral-300 font-semibold">{events.length - geoEvents.length} Global Advisories</span>
            </div>
          </div>

          {/* ── Event Detail Inspector & Real-World Correlation Intelligence ── */}
          {selectedEvent && (
            <div className="glass-level-2 rounded-2xl p-6 space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/[0.08] pb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1.5 font-mono">
                    <span className="text-xs text-cyan-400 font-bold">{selectedEvent.id}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase ${
                      selectedEvent.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                      selectedEvent.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-400 border-orange-500/30' :
                      'bg-amber-500/20 text-amber-400 border-amber-500/30'
                    }`}>
                      {selectedEvent.severity}
                    </span>
                    <span className="text-xs text-neutral-400">{selectedEvent.category}</span>
                  </div>
                  <h3 className="text-lg font-bold text-white leading-tight">
                    {selectedEvent.title}
                  </h3>
                </div>

                <a
                  href={selectedEvent.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-secondary flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold shrink-0 cursor-pointer"
                >
                  <span>Official Source</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>

              {/* Publication Timestamps & Freshness */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-xs font-mono glass-panel p-3 rounded-xl">
                <div>
                  <span className="text-neutral-500 block text-[10px]">ORIGIN SOURCE:</span>
                  <span className="text-white font-semibold">{selectedEvent.source_name}</span>
                </div>
                <div>
                  <span className="text-neutral-500 block text-[10px]">PUBLISHED:</span>
                  <span className="text-neutral-200">{formatToIST(selectedEvent.published_at)}</span>
                </div>
                <div>
                  <span className="text-neutral-500 block text-[10px]">INGESTED / FETCHED:</span>
                  <span className="text-cyan-300">{selectedEvent.fetched_at}</span>
                </div>
              </div>

              {/* Description */}
              <div className="space-y-1 text-xs">
                <span className="font-mono text-neutral-400 uppercase text-[10px] tracking-wider block">Advisory Brief</span>
                <p className="text-neutral-200 leading-relaxed glass-panel p-3.5 rounded-xl">
                  {selectedEvent.description}
                </p>
              </div>

              {/* Affected Technology & Identifiers */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
                <div className="p-3 glass-panel rounded-xl space-y-1">
                  <span className="text-neutral-500 block text-[10px]">AFFECTED TECHNOLOGY:</span>
                  <span className="text-white">{selectedEvent.affected_technology}</span>
                </div>
                <div className="p-3 glass-panel rounded-xl space-y-1">
                  <span className="text-neutral-500 block text-[10px]">IDENTIFIERS / CVEs:</span>
                  <div className="flex flex-wrap gap-1 mt-0.5">
                    {selectedEvent.cve_ids.length > 0 ? (
                      selectedEvent.cve_ids.map(cve => (
                        <span key={cve} className="px-1.5 py-0.5 bg-white/10 rounded text-cyan-300 text-[11px] font-bold">
                          {cve}
                        </span>
                      ))
                    ) : (
                      <span className="text-neutral-400">Infrastructure / Vendor Advisory</span>
                    )}
                  </div>
                </div>
              </div>

              {/* ══════════════════════════════════════════════════════════
                  REAL-WORLD CORRELATION ENGINE PANEL (HERO FEATURE)
                 ══════════════════════════════════════════════════════════ */}
              <div className="pt-2">
                <div className="p-4 rounded-2xl border border-cyan-500/30 glass-panel space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-cyan-400" />
                      <span className="text-xs font-bold text-white uppercase font-mono tracking-wider">
                        KAVACH Target Correlation Analysis
                      </span>
                    </div>
                    {activeCorrelation ? (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                        CONFIDENCE: {activeCorrelation.confidence}
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono text-neutral-400 bg-black/40 border border-white/10">
                        NO DIRECT LOCAL MATCH
                      </span>
                    )}
                  </div>

                  {activeCorrelation ? (
                    <div className="space-y-3 text-xs">
                      <div className="p-3 rounded-xl glass-terminal border-cyan-500/20 text-neutral-200">
                        <p className="font-semibold text-cyan-300 mb-1">{activeCorrelation.explanation}</p>
                        {activeCorrelation.related_finding_id && (
                          <div className="flex items-center justify-between pt-2 mt-2 border-t border-white/[0.08]">
                            <span className="text-neutral-400 font-mono">
                              Related Local Finding: <strong className="text-white">{activeCorrelation.related_finding_id}</strong> ({activeCorrelation.related_finding_title})
                            </span>
                            <button
                              onClick={() => navigate('findings')}
                              className="text-cyan-400 hover:text-white flex items-center gap-1 font-mono text-[11px] underline cursor-pointer"
                            >
                              <span>View in Findings</span>
                              <ArrowRight className="w-3 h-3" />
                            </button>
                          </div>
                        )}
                      </div>

                      {/* Explicit Distinction Box */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-mono">
                        <div className="p-2.5 rounded-lg glass-panel">
                          <span className="text-neutral-500 block uppercase text-[9px]">Local Technical Evidence:</span>
                          <span className="text-neutral-300">{activeCorrelation.local_evidence_summary}</span>
                        </div>
                        <div className="p-2.5 rounded-lg glass-panel">
                          <span className="text-neutral-500 block uppercase text-[9px]">External Global Context:</span>
                          <span className="text-neutral-300">{activeCorrelation.external_context_summary}</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-xs text-neutral-400 font-mono">
                      This external advisory does not match the active target endpoint's detected software stack or findings.
                      External context remains strictly isolated and is not falsely linked.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
