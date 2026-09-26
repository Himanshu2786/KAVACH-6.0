import React, { useState, useEffect, useRef } from 'react';
import {
  Shield,
  Menu,
  X,
  ChevronRight,
  Activity,
  Settings,
  Sparkles,
  ArrowRight,
  PlayCircle,
  Cpu,
  Layers,
  FileText,
  Radio,
  BookOpen,
  Database,
  History as HistoryIcon,
  Search,
  Lock,
  Compass,
  ListOrdered,
  AlertTriangle,
  BrainCircuit,
  Share2,
  CheckCircle2,
  BarChart3,
  HardDrive,
  LayoutDashboard,
  Globe,
  LogOut,
  User as UserIcon,
  ShieldAlert,
  MessageSquare
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { AiStatusResponse } from '../../types';
import { FeedbackModal } from '../common/FeedbackModal';

interface DemoStepItem {
  stepNumber: number;
  title: string;
  page: string;
  findingId?: string;
  desc: string;
  icon: React.ComponentType<{ className?: string }>;
}

const DEMO_JOURNEY_STEPS: DemoStepItem[] = [
  {
    stepNumber: 1,
    title: '1. Command Center',
    page: 'command-center',
    desc: 'Overall security posture, risk distribution & live map',
    icon: Compass
  },
  {
    stepNumber: 2,
    title: '2. System Health',
    page: 'system-status',
    desc: 'Real health of Backend, Ollama URL/model & Knowledge Engine',
    icon: Activity
  },
  {
    stepNumber: 3,
    title: '3. Scope Guard',
    page: 'new-assessment',
    desc: 'Mandatory authorization confirmation guard & modular scan scopes',
    icon: Lock
  },
  {
    stepNumber: 4,
    title: '4. Discovery',
    page: 'discovery',
    desc: 'Cataloged attack surfaces: endpoints, auth gateways & inputs',
    icon: Search
  },
  {
    stepNumber: 5,
    title: '5. 8-Stage Stepper',
    page: 'progress',
    desc: 'Complete security assessment lifecycle: DISCOVER -> REPORT',
    icon: ListOrdered
  },
  {
    stepNumber: 6,
    title: '6. Findings Matrix',
    page: 'findings',
    desc: 'Findings with state badges: POTENTIAL vs UNDER ANALYSIS vs CONFIRMED',
    icon: AlertTriangle
  },
  {
    stepNumber: 7,
    title: '7. AI Analysis',
    page: 'ai-analysis',
    findingId: 'KAV-2026-004',
    desc: 'AI root cause analysis & structured reasoning (KAV-2026-004)',
    icon: BrainCircuit
  },
  {
    stepNumber: 8,
    title: '8. Knowledge Graph',
    page: 'knowledge',
    desc: 'Local offline CWE and OWASP Top 10 mappings',
    icon: Share2
  },
  {
    stepNumber: 9,
    title: '9. Evidence Validation',
    page: 'evidence',
    findingId: 'KAV-2026-004',
    desc: 'Forensic live probe with SHA-256 hash & status transition',
    icon: CheckCircle2
  },
  {
    stepNumber: 10,
    title: '10. Risk Scoring',
    page: 'risk',
    desc: 'Deterministic multi-factor calculation & priority breakdown',
    icon: BarChart3
  },
  {
    stepNumber: 11,
    title: '11. Report Export',
    page: 'report',
    desc: 'Executive security intelligence report with printable HTML view',
    icon: FileText
  }
];

export const Navbar: React.FC = () => {
  const {
    activePage,
    navigate,
    ollamaStatus,
    isDemoMode,
    setIsDemoMode,
    presentationStep,
    setPresentationStep,
    showToast
  } = useApp();

  const { user, logout } = useAuth();

  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [aiStatus, setAiStatus] = useState<AiStatusResponse | null>(null);
  const [startingAi, setStartingAi] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const rawUserId = user?.id || (user as any)?.user?.id || user?.username || '';
  const isOwner = Boolean(
    user?.role === 'DEVELOPER_OWNER' ||
    user?.role === 'admin' ||
    user?.role === 'ADMIN' ||
    (user as any)?.user?.role === 'DEVELOPER_OWNER' ||
    (user as any)?.user?.role === 'admin' ||
    (rawUserId && rawUserId.toUpperCase().startsWith('ADMIN'))
  );

  const fetchAiStatus = async () => {
    try {
      const res = await api.getAiStatus();
      if (res.success) {
        setAiStatus(res);
      }
    } catch {
      // Keep offline
    }
  };

  useEffect(() => {
    fetchAiStatus();
    const interval = setInterval(fetchAiStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleStartLocalAi = async () => {
    setStartingAi(true);
    try {
      const res = await api.startAiService();
      showToast('info', 'AI Service', res.message);
      fetchAiStatus();
    } catch (err: any) {
      showToast('error', 'Startup Failed', 'Failed to trigger local Ollama process.');
    } finally {
      setStartingAi(false);
    }
  };

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 16);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close menu on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Close when clicking outside menu
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    if (menuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [menuOpen]);

  const isOllamaOnline = aiStatus ? aiStatus.status_code === 'ready' : ollamaStatus?.status === 'online';

  const platformModules = [
    { id: 'command-center', label: 'Command Center', desc: 'Executive security posture, risk distribution & metrics', icon: LayoutDashboard },
    { id: 'world-monitor', label: 'World Situational Monitor', desc: 'External situational awareness & global CVE/CISA feed', icon: Globe },
    { id: 'url-check', label: 'URL Check', desc: 'Real-time threat lookup & domain analysis', icon: Search },
    { id: 'portable-assessment', label: 'Local Posture', desc: 'Host & USB security assessments', icon: HardDrive },
    { id: 'experience-db', label: 'Experience DB', desc: 'Differential memory & false-positive intelligence', icon: Database },
    { id: 'audit-trail', label: 'Audit Trail', desc: 'Immutable cryptographic compliance logs', icon: Shield },
    { id: 'guide', label: 'Guide', desc: 'Architecture, workflows & operating manual', icon: BookOpen },
    { id: 'history', label: 'History', desc: 'Historical assessment reports & archives', icon: HistoryIcon },
  ];

  const handleNav = (id: string, findingId?: string) => {
    navigate(id, findingId);
    setMenuOpen(false);
  };

  const handleJourneyStep = (index: number) => {
    setPresentationStep(index);
    const step = DEMO_JOURNEY_STEPS[index];
    const targetFindingId = isDemoMode ? step.findingId : undefined;
    navigate(step.page, targetFindingId);
    setMenuOpen(false);
  };

  return (
    <>
      <header
        className={`sticky top-0 z-50 w-full transition-all duration-300 ${
          scrolled
            ? 'glass-level-1 border-b border-white/[0.08] shadow-[0_4px_24px_rgba(0,0,0,0.8)]'
            : 'bg-[#000000]/90 backdrop-blur-md border-b border-white/[0.06]'
        }`}
      >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        {/* LEFT: KAVACH Logo */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => handleNav('home')}
            className="flex items-center space-x-2.5 group cursor-pointer focus:outline-none"
            title="KAVACH 6.0 Home"
          >
            <div className="w-8 h-8 rounded-lg bg-white/[0.06] border border-white/10 backdrop-blur-md flex items-center justify-center text-white transition-all group-hover:scale-105 group-hover:border-white/25 shadow-sm">
              <Shield className="w-4 h-4 text-white" />
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="text-sm font-semibold tracking-tight text-white group-hover:text-neutral-200 transition-colors">
                KAVACH
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-full bg-white/[0.06] text-neutral-400 border border-white/[0.08]">
                6.0
              </span>
            </div>
          </button>
        </div>

        {/* RIGHT: Header Actions & Permanent 3-Line Menu Trigger Button ('≡') */}
        <div className="flex items-center space-x-2.5" ref={menuRef}>
          {/* Owner Quick Entry (Visible directly in navbar for OWNER) */}
          {user && isOwner && (
            <button
              id="owner-admin-navbar-badge-btn"
              onClick={() => handleNav('owner-admin')}
              className={`hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-mono font-semibold transition-all cursor-pointer shadow-sm ${
                activePage === 'owner-admin' || activePage === 'admin'
                  ? 'bg-amber-500/25 border-amber-400 text-amber-100 shadow-[0_0_12px_rgba(245,158,11,0.3)]'
                  : 'bg-amber-500/15 border-amber-500/30 text-amber-300 hover:bg-amber-500/25 hover:border-amber-400/50 hover:text-white'
              }`}
              title="Developer / Owner Admin Console"
            >
              <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
              <span>Owner Admin</span>
            </button>
          )}

          {/* User ID Badge in Header */}
          {user && (
            <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/[0.04] border border-white/[0.08] text-[11px] font-mono text-neutral-300">
              <span className={`w-1.5 h-1.5 rounded-full ${isOwner ? 'bg-amber-400' : 'bg-cyan-400'}`} />
              <span className="font-semibold text-white">{rawUserId || 'USER'}</span>
              <span className="text-[10px] text-neutral-400">[{isOwner ? 'OWNER' : 'TEAM'}]</span>
            </div>
          )}

          <button
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle navigation menu"
            className={`w-9 h-9 rounded-lg border transition-all flex items-center justify-center cursor-pointer ${
              menuOpen
                ? 'bg-white/15 border-white/30 text-white shadow-[0_0_12px_rgba(255,255,255,0.2)]'
                : 'bg-white/[0.06] border-white/[0.1] text-neutral-300 hover:text-white hover:bg-white/[0.12] hover:border-white/20'
            }`}
          >
            {menuOpen ? (
              <X className="w-5 h-5" />
            ) : (
              <Menu className="w-5 h-5" />
            )}
          </button>

          {/* ══ DROPDOWN / DRAWER MENU ══ */}
          {menuOpen && (
            <div
              className="absolute right-4 sm:right-6 lg:right-8 top-16 w-80 sm:w-96 max-w-[calc(100vw-2rem)] rounded-2xl glass-level-4 border border-white/15 p-4 shadow-[0_16px_40px_rgba(0,0,0,0.95)] z-50 animate-in fade-in slide-in-from-top-3 duration-200 max-h-[85vh] flex flex-col"
            >
              {/* Primary CTA: Assess Target */}
              <div className="pb-3 border-b border-white/[0.08] shrink-0">
                <button
                  onClick={() => handleNav('new-assessment')}
                  className="btn-primary w-full py-2.5 px-4 rounded-xl text-xs font-bold tracking-wider uppercase flex items-center justify-between shadow-[0_0_20px_rgba(255,255,255,0.15)] cursor-pointer"
                >
                  <span className="flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    Assess Target
                  </span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

              {/* Scrollable Body containing 11 Steps & Platform Modules */}
              <div className="py-2.5 overflow-y-auto space-y-3.5 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent pr-1">
                {/* ══ PLATFORM MODULES SECTION ══ */}
                <div>
                  <div className="text-[10px] font-mono text-neutral-500 uppercase px-2 py-1 tracking-wider">
                    Platform Modules
                  </div>
                  <div className="space-y-1 mt-1">
                    {platformModules.map((item) => {
                      const ModuleIcon = item.icon;
                      const isActive = activePage === item.id;

                      return (
                        <button
                          key={item.id}
                          onClick={() => handleNav(item.id)}
                          className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-all cursor-pointer group ${
                            isActive
                              ? 'bg-white/15 text-white font-semibold border border-white/20 shadow-sm'
                              : 'text-neutral-300 hover:text-white hover:bg-white/[0.08] border border-transparent'
                          }`}
                        >
                          <div className="flex items-center gap-2 min-w-0 pr-1">
                            <ModuleIcon className="w-3.5 h-3.5 text-neutral-400 group-hover:text-neutral-200 shrink-0" />
                            <div className="min-w-0">
                              <div className="flex items-center gap-1.5">
                                <span className="truncate">{item.label}</span>
                                {isActive && (
                                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
                                )}
                              </div>
                              <div className="text-[10px] text-neutral-500 group-hover:text-neutral-400 truncate leading-tight mt-0.5">
                                {item.desc}
                              </div>
                            </div>
                          </div>
                          <ChevronRight className="w-3.5 h-3.5 text-neutral-600 group-hover:text-neutral-300 shrink-0 ml-1" />
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* ══ 11-STEP DEMO JOURNEY (COMPACT SMALL ICONS BELOW PLATFORM MODULES) ══ */}
                <div className="pt-2.5 border-t border-white/[0.08]">
                  <div className="text-[10px] font-mono text-neutral-400 uppercase px-2 py-1 tracking-wider flex items-center justify-between font-semibold">
                    <span className="flex items-center gap-1.5 text-neutral-300">
                      <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                      Demo Journey (11 Steps)
                    </span>
                    <span className="text-[9px] text-neutral-500 font-mono">
                      {presentationStep !== null ? `Step ${presentationStep + 1}/11` : '1 – 11'}
                    </span>
                  </div>

                  {/* Active Step Indicator Pill */}
                  {presentationStep !== null && DEMO_JOURNEY_STEPS[presentationStep] && (
                    <div className="mx-1 my-1 px-2.5 py-1 rounded-lg bg-cyan-950/60 border border-cyan-500/30 text-[10px] font-mono text-cyan-300 flex items-center justify-between">
                      <span className="truncate">Active: {DEMO_JOURNEY_STEPS[presentationStep].title}</span>
                      <span className="text-[9px] text-emerald-400 flex items-center gap-1 shrink-0">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        STEP {presentationStep + 1}
                      </span>
                    </div>
                  )}

                  {/* Small Icons Grid for 11 Steps */}
                  <div className="grid grid-cols-4 sm:grid-cols-6 gap-1.5 p-1 mt-1">
                    {DEMO_JOURNEY_STEPS.map((step, idx) => {
                      const StepIcon = step.icon;
                      const isCurrentStep = presentationStep === idx && activePage === step.page;
                      const isPageMatch = activePage === step.page;

                      return (
                        <button
                          key={step.stepNumber}
                          onClick={() => handleJourneyStep(idx)}
                          title={`${step.title}\n${step.desc}`}
                          className={`relative p-2 rounded-xl flex flex-col items-center justify-center text-center transition-all cursor-pointer group ${
                            isCurrentStep
                              ? 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-400/80 shadow-[0_0_12px_rgba(6,182,212,0.4)]'
                              : isPageMatch
                              ? 'bg-white/15 text-white border border-white/30'
                              : 'bg-white/[0.04] text-neutral-400 hover:text-white hover:bg-white/[0.1] border border-white/[0.08] hover:border-white/20'
                          }`}
                        >
                          {/* Step Number Badge */}
                          <span
                            className={`absolute top-1 right-1 text-[8px] font-mono px-1 rounded ${
                              isCurrentStep
                                ? 'bg-cyan-400 text-black font-extrabold'
                                : 'text-neutral-500 group-hover:text-neutral-300'
                            }`}
                          >
                            {step.stepNumber}
                          </span>

                          {/* Small Icon */}
                          <StepIcon className={`w-4 h-4 my-0.5 ${isCurrentStep ? 'text-cyan-300 animate-pulse' : 'group-hover:text-white'}`} />

                          {/* Short Name */}
                          <span className="text-[9px] font-mono font-medium truncate max-w-full leading-tight mt-0.5">
                            {step.title.replace(/^\d+\.\s*/, '')}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* System Context, AI Engine & Settings */}
              <div className="pt-3 border-t border-white/[0.08] space-y-2 shrink-0">
                <div className="text-[10px] font-mono text-neutral-500 uppercase px-2 tracking-wider flex items-center justify-between">
                  <span>System Engine</span>
                  <button
                    onClick={() => {
                      setIsDemoMode(!isDemoMode);
                      showToast(
                        'info',
                        'Scope Changed',
                        `Mode: ${!isDemoMode ? 'Simulated Sandbox' : 'Live Scope'}`
                      );
                    }}
                    className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-white/[0.08] hover:bg-white/[0.14] text-neutral-300 border border-white/10 transition-all cursor-pointer"
                  >
                    MODE: {isDemoMode ? 'DEMO' : 'LIVE'}
                  </button>
                </div>

                {/* AI Status Card */}
                <div className="p-2.5 rounded-xl bg-white/[0.04] border border-white/[0.06] text-xs font-mono space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-neutral-400 text-[11px] flex items-center gap-1.5">
                      <span
                        className={`w-2 h-2 rounded-full ${
                          aiStatus?.status_code === 'ready'
                            ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.8)]'
                            : aiStatus?.status_code === 'starting'
                            ? 'bg-amber-400 animate-pulse'
                            : aiStatus?.status_code === 'model_unavailable'
                            ? 'bg-orange-400'
                            : 'bg-rose-500'
                        }`}
                      />
                      Ollama Engine
                    </span>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                        aiStatus?.status_code === 'ready'
                          ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/60'
                          : aiStatus?.status_code === 'starting'
                          ? 'bg-amber-950/80 text-amber-300 border border-amber-800/60'
                          : 'bg-rose-950/80 text-rose-300 border border-rose-800/60'
                      }`}
                    >
                      {aiStatus?.lifecycle_state || (isOllamaOnline ? 'AI READY' : 'AI OFFLINE')}
                    </span>
                  </div>

                  {aiStatus?.status_code !== 'ready' && (
                    <button
                      onClick={handleStartLocalAi}
                      disabled={startingAi || aiStatus?.status_code === 'starting'}
                      className="w-full mt-1 px-2 py-1 text-[10px] font-mono rounded-lg bg-white/[0.08] hover:bg-white/[0.15] text-white border border-white/10 flex items-center justify-center gap-1.5 transition-all cursor-pointer disabled:opacity-50"
                    >
                      <Sparkles className="w-3 h-3 text-amber-400" />
                      <span>{startingAi ? 'Attempting Startup...' : 'Start Local Ollama'}</span>
                    </button>
                  )}
                </div>

                {/* Secondary System Links */}
                <div className="grid grid-cols-2 gap-1 pt-1">
                  <button
                    onClick={() => handleNav('system-status')}
                    className="px-2.5 py-1.5 rounded-lg bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.06] text-[11px] font-mono text-neutral-300 hover:text-white flex items-center gap-1.5 transition-all cursor-pointer"
                  >
                    <Activity className="w-3 h-3 text-emerald-400" />
                    <span>SOC Status</span>
                  </button>
                  <button
                    onClick={() => handleNav('settings')}
                    className="px-2.5 py-1.5 rounded-lg bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.06] text-[11px] font-mono text-neutral-300 hover:text-white flex items-center gap-1.5 transition-all cursor-pointer"
                  >
                    <Settings className="w-3 h-3 text-neutral-400" />
                    <span>Settings</span>
                  </button>
                </div>

                {user && (
                  <div className="mt-3 pt-3 border-t border-white/[0.08] space-y-2">
                    {/* User Profile Card */}
                    <div className="flex items-center justify-between px-2.5 py-2 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-lg bg-white/[0.06] border border-white/[0.1] flex items-center justify-center text-cyan-400 font-mono text-[11px] font-bold">
                          {(rawUserId || 'US').slice(0, 2).toUpperCase()}
                        </div>
                        <div>
                          <div className="text-xs font-mono font-bold text-white leading-none">{rawUserId || 'User'}</div>
                          <div className="text-[10px] font-mono text-neutral-400 leading-tight mt-0.5">
                            {isOwner ? 'OWNER' : 'TEAM USER'}
                          </div>
                        </div>
                      </div>
                      <span className={`px-2 py-0.5 rounded-full text-[9px] font-mono font-bold ${
                        isOwner
                          ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                          : 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                      }`}>
                        {isOwner ? 'OWNER' : 'TEAM USER'}
                      </span>
                    </div>

                    {/* Developer / Owner Admin (OWNER ONLY) */}
                    {isOwner && (
                      <button
                        id="owner-admin-nav-btn"
                        onClick={() => {
                          handleNav('owner-admin');
                          setMenuOpen(false);
                        }}
                        className="w-full px-3 py-2 rounded-xl bg-gradient-to-r from-amber-500/20 via-orange-500/15 to-amber-500/10 hover:from-amber-500/30 hover:via-orange-500/25 hover:to-amber-500/20 border border-amber-500/35 hover:border-amber-400/60 text-xs font-mono font-semibold text-amber-200 hover:text-white flex items-center justify-between transition-all cursor-pointer shadow-sm group"
                      >
                        <div className="flex items-center gap-2">
                          <ShieldAlert className="w-3.5 h-3.5 text-amber-400 group-hover:scale-110 transition-transform" />
                          <span>Developer / Owner Admin</span>
                        </div>
                        <ChevronRight className="w-3.5 h-3.5 text-amber-400/70 group-hover:translate-x-0.5 transition-transform" />
                      </button>
                    )}

                    {/* Feedback Action */}
                    <button
                      id="feedback-nav-btn"
                      onClick={() => {
                        setShowFeedbackModal(true);
                        setMenuOpen(false);
                      }}
                      className="w-full px-3 py-1.5 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.06] hover:border-white/[0.12] text-xs font-mono text-neutral-300 hover:text-white flex items-center justify-between transition-all cursor-pointer"
                    >
                      <div className="flex items-center gap-2">
                        <MessageSquare className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Feedback</span>
                      </div>
                      <ChevronRight className="w-3 h-3 text-neutral-500" />
                    </button>

                    {/* Logout Action */}
                    <button
                      id="logout-nav-btn"
                      onClick={() => {
                        logout();
                        setMenuOpen(false);
                      }}
                      className="w-full px-3 py-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 hover:border-rose-500/40 text-xs font-mono text-rose-300 hover:text-rose-200 flex items-center justify-center gap-1.5 transition-all cursor-pointer"
                    >
                      <LogOut className="w-3.5 h-3.5 text-rose-400" />
                      <span>Logout</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      </header>
      <FeedbackModal
        isOpen={showFeedbackModal}
        onClose={() => setShowFeedbackModal(false)}
      />
    </>
  );
};



