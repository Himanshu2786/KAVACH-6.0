import React, { useState } from 'react';
import {
  ChevronDown,
  Shield,
  FileCheck2,
  Terminal,
  Cpu,
  AlertTriangle,
  Search,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Globe,
  Play,
  X,
  BookOpen,
  Laptop,
  CheckCircle,
  HelpCircle,
  Video
} from 'lucide-react';
import { useApp } from '../context/AppContext';

interface GuideItem {
  id: string;
  question: string;
  summary: string;
  answer: string[];
  technicalDetail: string;
  icon: React.ElementType;
}

interface DemoItem {
  id: string;
  title: string;
  category: string;
  duration: string;
  videoFile: string;
  thumbnail: string;
  description: string;
  keySteps: string[];
}

export const GuidePage: React.FC = () => {
  const { navigate } = useApp();
  const [activeTab, setActiveTab] = useState<'manual' | 'architecture'>('manual');
  const [selectedDemo, setSelectedDemo] = useState<DemoItem | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    'what-is-kavach': true,
    'what-is-world-monitor': true,
  });

  const guideItems: GuideItem[] = [
    {
      id: 'what-is-kavach',
      question: 'What is KAVACH?',
      summary: 'An AI-assisted, evidence-driven security assessment platform engineered for verifiable technical proof.',
      answer: [
        'KAVACH is a modern cybersecurity assessment system designed to eliminate false alarms and unprovable claims in web application security audits.',
        'Unlike legacy vulnerability scanners that output ambiguous risk alerts without reproducible proof, KAVACH anchors every finding to immutable cryptographic evidence (SHA-256 network response captures).',
        'It combines deterministic security probing across 7 compliance areas with local offline LLM reasoning to explain root cause and recommend actionable fixes.'
      ],
      technicalDetail: 'Engineered as the flagship benchmark solution for Smart India Hackathon Problem Statement 26163, auditing the World Monitor Situational Intelligence application.',
      icon: Shield
    },
    {
      id: 'what-is-world-monitor',
      question: 'What is World Monitor & How to Use It?',
      summary: 'External security situational-awareness layer providing real-time global context for KAVACH assessments.',
      answer: [
        'What is World Monitor? World Monitor provides external security situational-awareness, tracking real-world CVEs, CISA Known Exploited Vulnerabilities (KEV), and global security advisories.',
        'How to Use World Monitor: 1. Open World Monitor → 2. Select a time range (24h/7d/30d/All) and filter events by category (Cybersecurity, Vulnerability, Infrastructure, etc.) → 3. Select an event to inspect source fact, published time, and affected technology → 4. Check correlation with your KAVACH target assessment → 5. Inspect the correlation explanation (CVE match, technology match) and navigate to Findings/Evidence for local verification.',
        'Critical Distinction: An external event is EXTERNAL CONTEXT, NOT proof of a local target vulnerability. KAVACH never conflates external advisories with local evidence. Evidence collected by KAVACH remains the only source of truth for target compromise.'
      ],
      technicalDetail: 'Source-adapter architecture ingests CISA KEV & NVD authoritative feeds with deterministic deduplication, coordinate geo-pinning, and explainable HIGH/MEDIUM/LOW confidence correlation.',
      icon: Globe
    },
    {
      id: 'how-assessment-works',
      question: 'How does assessment work?',
      summary: 'A 7-stage deterministic pipeline from target authorization to compliance reporting.',
      answer: [
        'Step 1 (Target & Dual-Gate Auth): You specify an authorized target domain or endpoint. Assessment will never initiate without confirmed scope boundaries.',
        'Step 2 (Surface Discovery): The engine inventories attack surfaces, authentication gateways, and API routes.',
        'Step 3 (Security Checks): Modular non-destructive probes evaluate Authentication, Authorization (IDOR), Input Validation, API Security, Client Security, Secure Communication, and Data Privacy.',
        'Step 4 (Evidence Recording): Verbatim HTTP request/response pairs are captured, SHA-256 hashed, and stored in the tamper-evident catalog.',
        'Step 5 (Validation & AI): AI interprets empirical facts, calculates deterministic risk scores, and maps to CWE and OWASP Top 10 categories.'
      ],
      technicalDetail: 'All checks run asynchronously via FastAPI and SQLite, ensuring zero destructive payload injection.',
      icon: Search
    },
    {
      id: 'what-is-evidence',
      question: 'What is evidence?',
      summary: 'Verbatim, tamper-evident network artifacts that prove a vulnerability exists.',
      answer: [
        'In KAVACH, evidence is NOT an opinion or AI speculation. Evidence is a concrete, recorded HTTP response, status code, header set, or API payload.',
        'Every piece of evidence receives a unique identifier (e.g. EVD-001) and a SHA-256 cryptographic digest at the exact instant of capture.',
        'This integrity hash guarantees that security observations cannot be altered or fabricated after the test concludes.'
      ],
      technicalDetail: 'Cryptographic proof guarantees zero post-audit tampering and complete audit repeatability.',
      icon: FileCheck2
    },
    {
      id: 'how-to-remediate',
      question: 'How do I fix and verify issues?',
      summary: 'Deterministic 7-point remediation plans with automated before/after verification.',
      answer: [
        'Step 1 (Remediation Center): Review findings prioritized by deterministic CVSS 3.1 severity scores and component criticality.',
        'Step 2 (Actionable Patch): Each finding contains a 7-point structured fix plan including code patches, configuration snippets, and security principles.',
        'Step 3 (Terminal Verification): Copy the exact non-destructive curl command provided in the technical terminal to verify the vulnerability independently.',
        'Step 4 (Automated Re-Test): Apply the fix in your application and click "Run Verification Test". KAVACH re-executes the check, presents a side-by-side BEFORE vs AFTER diff, and transitions the status to RESOLVED upon verification.'
      ],
      technicalDetail: 'Lifecycle transitions are permanently recorded in the SHA-256 chained audit ledger.',
      icon: Terminal
    },
    {
      id: 'ai-role-truth-hierarchy',
      question: 'What is the role of AI & Truth Hierarchy?',
      summary: 'Ollama local intelligence grounded by empirical evidence and local CWE knowledge base.',
      answer: [
        'Axiom: "AI Hypothesizes. Evidence Confirms. Ollama is NEVER the detector."',
        'Local Privacy: All AI reasoning runs 100% locally via Ollama on localhost. Zero sensitive credentials, source code tokens, or assessment data ever leave your machine.',
        'Data Masking: Before prompts reach the LLM, sensitive tokens (passwords, AWS keys, auth headers) are automatically redacted.',
        'Truth Boundary: AI explanations are strictly grounded in empirical evidence and local CWE vector embeddings. If Ollama is offline, KAVACH falls back deterministically to rule-based explanations without interruption.'
      ],
      technicalDetail: 'Implements RAG with cosine similarity matching against local vector database (rag_vectors.npz).',
      icon: Cpu
    },
    {
      id: 'limitations-and-safety',
      question: 'What are limitations?',
      summary: 'Honest operational boundaries and safety guardrails.',
      answer: [
        'KAVACH is strictly non-destructive. It does not perform active database dumps, volumetric denial of service, or invasive shell exploitation.',
        'Deep blind authenticated flows require manual session token provisioning or credential authorization.',
        'CVE matches are classified honestly: CVE mappings require specific version proof; without confirmed software versions, KAVACH marks them as "Version Verification Required" rather than making false claims.'
      ],
      technicalDetail: 'Designed for production and staging resilience under ISO/IEC 27001 and OWASP audit standards.',
      icon: AlertTriangle
    }
  ];

  const demoCatalog: DemoItem[] = [
    {
      id: 'getting-started',
      title: '01. Getting Started & Onboarding',
      category: 'ONBOARDING',
      duration: '0:45',
      videoFile: '/demos/01_getting_started.mp4',
      thumbnail: '/images/01_getting_started.png',
      description: 'System initialization, pre-flight environment checks, and legal scope confirmation.',
      keySteps: ['Check database & Ollama status', 'Dual-Gate Authorization', 'Launch 1-Click Demo Journey']
    },
    {
      id: 'url-check',
      title: '02. URL Security Check',
      category: 'FAST AUDIT',
      duration: '0:35',
      videoFile: '/demos/02_url_check.mp4',
      thumbnail: '/images/02_url_check.png',
      description: 'Instant HTTP response header analysis and TLS cipher suite verification.',
      keySteps: ['Enter target URL', 'Execute live socket probe', 'Inspect missing security headers']
    },
    {
      id: 'ai-ready',
      title: '03. AI Ready & Truth Hierarchy',
      category: 'AI ENGINE',
      duration: '0:50',
      videoFile: '/demos/03_ai_ready.mp4',
      thumbnail: '/images/03_ai_ready.png',
      description: 'Local Ollama integration, sensitive regex masking, and 7-section structured explanation.',
      keySteps: ['4-state lifecycle monitor', 'Sensitive credential masking', 'Grounding in local CWE RAG']
    },
    {
      id: 'assess-target',
      title: '04. 17-Step Assess Target Pipeline',
      category: 'CORE PIPELINE',
      duration: '1:10',
      videoFile: '/demos/04_assess_target.mp4',
      thumbnail: '/images/04_assess_target.png',
      description: 'Full autonomous 17-stage assessment workflow from target validation to dossier export.',
      keySteps: ['Surface discovery', '7-domain probes', 'CVSS 3.1 calculation', 'Forensic export']
    },
    {
      id: 'world-monitor',
      title: '05. World Monitor Assessment',
      category: 'SIH PS 26163',
      duration: '1:00',
      videoFile: '/demos/05_world_monitor.mp4',
      thumbnail: '/images/05_world_monitor.png',
      description: 'Dual-mode (Runtime + Source AST) evaluation of https://www.worldmonitor.app.',
      keySteps: ['Load target registry', 'Audit live website', 'Verify source code AST', 'Coverage matrix']
    },
    {
      id: 'local-posture',
      title: '06. Local Posture (USB Portable)',
      category: 'HOST SCAN',
      duration: '0:45',
      videoFile: '/demos/06_local_posture.mp4',
      thumbnail: '/images/06_local_posture.png',
      description: 'Zero-collection host scanner detecting exposed API keys, passwords, and double-extension files.',
      keySteps: ['Permission boundary dialog', 'Scan approved path', 'Automatic secret redaction']
    },
    {
      id: 'finding',
      title: '07. Finding Triage & Model',
      category: 'TRIAGE',
      duration: '0:40',
      videoFile: '/demos/07_finding.mp4',
      thumbnail: '/images/07_finding.png',
      description: 'Structured finding model with CWE/OWASP mapping, CVSS vectors, and status transitions.',
      keySteps: ['Inspect finding details', 'Verify CVSS 3.1 vector', 'Assign analyst & log notes']
    },
    {
      id: 'evidence',
      title: '08. Cryptographic Evidence & SHA-256',
      category: 'EVIDENCE',
      duration: '0:50',
      videoFile: '/demos/08_evidence.mp4',
      thumbnail: '/images/08_evidence.png',
      description: 'Raw unadulterated technical observations with bitwise immutable SHA-256 digests.',
      keySteps: ['Inspect verbatim headers', 'Verify 64-char SHA-256 hash', 'Copy reproduction command']
    },
    {
      id: 'audit-trail',
      title: '09. Tamper-Evident Chained Audit Log',
      category: 'AUDIT',
      duration: '0:45',
      videoFile: '/demos/09_audit_trail.mp4',
      thumbnail: '/images/09_audit_trail.png',
      description: 'Merkle-style SHA-256 chained event ledger recording every assessment action.',
      keySteps: ['Inspect prev_hash chaining', 'Filter by module', 'Verify immutable ledger']
    },
    {
      id: 'experience-db',
      title: '10. Experience DB & False Positives',
      category: 'KNOWLEDGE',
      duration: '0:35',
      videoFile: '/demos/10_experience_db.mp4',
      thumbnail: '/images/10_experience_db.png',
      description: 'Institutional repository of verified false positives and historical re-verifications.',
      keySteps: ['View approved exceptions', 'Inspect justification notes', 'Query experience memory']
    },
    {
      id: 'history',
      title: '11. Assessment History & Trends',
      category: 'TIMELINE',
      duration: '0:30',
      videoFile: '/demos/11_history.mp4',
      thumbnail: '/images/11_history.png',
      description: 'Historical timeline tracking posture score improvements and remediation progress.',
      keySteps: ['Compare past runs', 'Review posture delta', 'Re-open archived audits']
    },
    {
      id: 'guide',
      title: '12. Platform Architecture Guide',
      category: 'DOCUMENTATION',
      duration: '0:45',
      videoFile: '/demos/12_guide.mp4',
      thumbnail: '/images/12_guide.png',
      description: 'Architecture specifications, RFC compliance principles, and knowledge graph.',
      keySteps: ['Explore 7-domain architecture', 'Review verification model', 'Inspect RFC mappings']
    },
    {
      id: 'user-manual',
      title: '13. End-User Manual & Catalog',
      category: 'OPERATOR GUIDE',
      duration: '0:40',
      videoFile: '/demos/13_user_manual.mp4',
      thumbnail: '/images/13_user_manual.png',
      description: 'Operator manual, dual simple+technical explanations, and button catalog.',
      keySteps: ['Browse 25 manual chapters', 'Inspect button catalog', 'Review SIH Quick Start']
    },
    {
      id: 'report-generation',
      title: '14. Forensic Reporting (HTML Dossier)',
      category: 'REPORTING',
      duration: '0:50',
      videoFile: '/demos/14_report_generation.mp4',
      thumbnail: '/images/14_report_generation.png',
      description: 'Exporting standalone offline HTML dossiers and JSON packages with SHA-256 manifests.',
      keySteps: ['Generate HTML dossier', 'Inspect evidence viewer', 'Download JSON hash manifest']
    },
    {
      id: 'retest',
      title: '15. Re-Test & BEFORE vs AFTER Diff',
      category: 'VERIFICATION',
      duration: '0:45',
      videoFile: '/demos/15_retest.mp4',
      thumbnail: '/images/15_retest.png',
      description: 'Differential re-verification proving vulnerability resolution upon developer patch.',
      keySteps: ['Execute re-verification check', 'Compare side-by-side diff', 'Auto-update to RESOLVED']
    },
    {
      id: 'full-sih-demo',
      title: '16. Full SIH PS 26163 Demonstration',
      category: 'SIH BENCHMARK',
      duration: '1:30',
      videoFile: '/demos/16_full_sih_demo.mp4',
      thumbnail: '/images/16_full_sih_demo.png',
      description: 'Complete 17-step end-to-end evaluation executing clean-state SIH benchmark.',
      keySteps: ['Clean DB init', 'Run 17-step pipeline', 'Verify 0 errors', 'Output forensic package']
    }
  ];

  const toggleItem = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const filteredDemos = demoCatalog.filter(d => 
    d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-20">
      
      {/* Top Header */}
      <div className="text-center space-y-3 pt-6">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-neutral-900 border border-white/[0.08] text-xs font-mono text-neutral-300">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Knowledge & Demonstration Center</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
          KAVACH 6.0 Documentation & Demos
        </h1>
        <p className="text-sm text-neutral-400 max-w-2xl mx-auto leading-relaxed">
          Comprehensive Operator Manual, Architectural Specifications, and 16 High-Definition Demonstration Recordings for Smart India Hackathon PS 26163.
        </p>

        {/* Tab Switcher */}
        <div className="flex items-center justify-center pt-4">
          <div className="inline-flex p-1 rounded-xl bg-neutral-900 border border-white/[0.08]">
            <button
              onClick={() => setActiveTab('manual')}
              className={`flex items-center space-x-2 px-5 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'manual'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-lg shadow-cyan-500/10'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>📘 User Manual & 16 Video Demos</span>
            </button>
            <button
              onClick={() => setActiveTab('architecture')}
              className={`flex items-center space-x-2 px-5 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'architecture'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-lg shadow-cyan-500/10'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              <Shield className="w-4 h-4" />
              <span>📖 Architectural Guide</span>
            </button>
          </div>
        </div>
      </div>

      {/* TAB 1: USER MANUAL & DEMOS */}
      {activeTab === 'manual' && (
        <div className="space-y-8 animate-in fade-in duration-300">
          
          {/* Search & Overview Banner */}
          <div className="relative flex flex-col md:flex-row items-center justify-between gap-4 p-5 rounded-2xl bg-neutral-900/60 border border-white/[0.08] backdrop-blur-xl">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                <Video className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">16 Playable Demonstration Recordings</h3>
                <p className="text-xs text-neutral-400">Click "▶ WATCH DEMO" on any module below to inspect real application execution.</p>
              </div>
            </div>
            
            <div className="relative w-full md:w-64">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-neutral-500" />
              <input
                type="text"
                placeholder="Search workflows & demos..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-black/40 border border-white/[0.08] text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-cyan-500/40"
              />
            </div>
          </div>

          {/* Demonstration Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredDemos.map((demo) => (
              <div
                key={demo.id}
                className="group relative p-5 rounded-2xl bg-neutral-900/40 border border-white/[0.08] hover:border-cyan-500/30 transition-all hover:shadow-xl hover:shadow-cyan-500/5 flex flex-col justify-between"
              >
                <div className="space-y-3">
                  {/* Video Thumbnail Preview Banner */}
                  <div
                    onClick={() => setSelectedDemo(demo)}
                    className="relative w-full h-36 rounded-xl overflow-hidden bg-neutral-950 border border-white/[0.06] cursor-pointer group/thumb"
                  >
                    <img
                      src={demo.thumbnail}
                      alt={demo.title}
                      className="w-full h-full object-cover opacity-80 group-hover/thumb:opacity-100 group-hover/thumb:scale-105 transition-all duration-300"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent flex items-center justify-center">
                      <div className="w-10 h-10 rounded-full bg-cyan-500/80 group-hover/thumb:bg-cyan-400 group-hover/thumb:scale-110 text-neutral-950 flex items-center justify-center shadow-lg shadow-cyan-500/30 transition-all">
                        <Play className="w-4 h-4 fill-current ml-0.5" />
                      </div>
                    </div>
                    <div className="absolute bottom-2 right-2 px-2 py-0.5 rounded bg-black/70 backdrop-blur-sm text-[10px] font-mono text-cyan-300 border border-white/[0.1]">
                      {demo.duration}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-[10px] font-mono font-semibold text-cyan-400 uppercase">
                      {demo.category}
                    </span>
                    <span className="text-[11px] font-mono text-neutral-500">
                      {demo.duration} HD
                    </span>
                  </div>

                  <h3 className="text-base font-semibold text-white group-hover:text-cyan-300 transition-colors">
                    {demo.title}
                  </h3>

                  <p className="text-xs text-neutral-400 leading-relaxed">
                    {demo.description}
                  </p>

                  <div className="space-y-1 pt-1">
                    {demo.keySteps.map((step, idx) => (
                      <div key={idx} className="flex items-center space-x-2 text-[11px] text-neutral-400">
                        <CheckCircle className="w-3 h-3 text-cyan-400 shrink-0" />
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 mt-2 border-t border-white/[0.06] flex items-center justify-between">
                  <button
                    onClick={() => setSelectedDemo(demo)}
                    className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 text-xs font-semibold transition-all shadow-md shadow-cyan-500/10"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>▶ WATCH DEMO</span>
                  </button>

                  <span className="text-[10px] font-mono text-neutral-500">
                    {demo.videoFile}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Quick Action Navigation to Core Modules */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-cyan-950/20 via-neutral-900 to-purple-950/20 border border-white/[0.08] flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="space-y-1 text-center sm:text-left">
              <h3 className="text-sm font-semibold text-white">Ready to Execute Live Security Audit?</h3>
              <p className="text-xs text-neutral-400">Jump directly into the 17-step World Monitor assessment pipeline.</p>
            </div>
            <button
              onClick={() => navigate('command-center')}
              className="px-5 py-2 rounded-xl bg-cyan-500 text-neutral-950 font-semibold text-xs hover:bg-cyan-400 transition-all shadow-lg shadow-cyan-500/20 flex items-center space-x-2 shrink-0"
            >
              <span>Launch Command Center</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* TAB 2: ARCHITECTURAL GUIDE */}
      {activeTab === 'architecture' && (
        <div className="space-y-6 animate-in fade-in duration-300">
          {guideItems.map((item) => {
            const Icon = item.icon;
            const isOpen = !!expanded[item.id];

            return (
              <div
                key={item.id}
                className={`border rounded-2xl transition-all duration-300 overflow-hidden ${
                  isOpen
                    ? 'bg-neutral-900/60 border-white/[0.12] shadow-xl shadow-black/40'
                    : 'bg-neutral-900/30 border-white/[0.06] hover:border-white/[0.1]'
                }`}
              >
                <button
                  onClick={() => toggleItem(item.id)}
                  className="w-full text-left p-5 sm:p-6 flex items-start justify-between gap-4 focus:outline-none"
                >
                  <div className="flex items-start space-x-4">
                    <div className="p-2.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-cyan-400 shrink-0 mt-0.5">
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h2 className="text-base sm:text-lg font-semibold text-white">{item.question}</h2>
                      <p className="text-xs text-neutral-400 mt-1">{item.summary}</p>
                    </div>
                  </div>
                  <div className="p-1 rounded-lg bg-white/[0.04] text-neutral-400 shrink-0">
                    <ChevronDown className={`w-4 h-4 transition-transform duration-300 ${isOpen ? 'rotate-180 text-white' : ''}`} />
                  </div>
                </button>

                {isOpen && (
                  <div className="px-5 sm:px-6 pb-6 pt-2 border-t border-white/[0.04] space-y-4">
                    <div className="space-y-2.5 text-xs sm:text-sm text-neutral-300 leading-relaxed">
                      {item.answer.map((para, i) => (
                        <p key={i}>{para}</p>
                      ))}
                    </div>

                    <div className="p-3.5 rounded-xl bg-black/40 border border-white/[0.06] flex items-start space-x-3 text-xs font-mono text-neutral-400">
                      <div className="p-1 rounded bg-cyan-500/10 text-cyan-400 shrink-0">
                        <Terminal className="w-3.5 h-3.5" />
                      </div>
                      <div>
                        <span className="text-cyan-300 font-semibold block mb-0.5">Technical Rationale:</span>
                        <span>{item.technicalDetail}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* VIDEO DEMO MODAL PLAYER */}
      {selectedDemo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="relative w-full max-w-4xl rounded-2xl bg-neutral-900 border border-white/[0.12] overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/[0.08] bg-neutral-950">
              <div className="flex items-center space-x-3">
                <span className="px-2 py-0.5 rounded-md bg-cyan-500/20 text-cyan-300 text-[10px] font-mono uppercase">
                  {selectedDemo.category}
                </span>
                <h3 className="text-sm font-semibold text-white">{selectedDemo.title}</h3>
              </div>
              <button
                onClick={() => setSelectedDemo(null)}
                className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-white/[0.06] transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Video Player Area */}
            <div className="relative bg-black aspect-video flex items-center justify-center overflow-hidden">
              <video
                key={selectedDemo.videoFile}
                src={selectedDemo.videoFile}
                poster={selectedDemo.thumbnail}
                controls
                autoPlay
                playsInline
                preload="auto"
                className="w-full h-full object-contain"
              >
                Your browser does not support HTML5 video playback.
              </video>
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-neutral-950/80 border-t border-white/[0.06] flex items-center justify-between text-xs text-neutral-400">
              <span>{selectedDemo.description}</span>
              <button
                onClick={() => setSelectedDemo(null)}
                className="px-4 py-1.5 rounded-lg bg-white/[0.08] hover:bg-white/[0.12] text-white text-xs font-semibold transition-colors"
              >
                Close Player
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
