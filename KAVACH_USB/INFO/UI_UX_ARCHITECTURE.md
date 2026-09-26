# KAVACH 6.0 — UI/UX Architecture Specification
**Vercel-Inspired Premium Experience for AI-Assisted Security Assessment**

---

## 1. Design Philosophy

KAVACH is designed under the core product principle:
> **"AI Hypothesizes. Evidence Confirms. Engineers Verify."**

The UI/UX reflects the standards of modern enterprise developer tools (inspired by **Vercel**, **Stripe**, and **Linear**):
- **Minimalist & Clean**: Zero noisy "hacker matrix" greens, neon borders, or simulated terminal chatter.
- **Generous Whitespace & Crisp Typography**: High-contrast typography hierarchy using clean sans-serif display type paired with monospace code identifiers (`Inter` + `Geist Mono` feel).
- **Subtle Glassmorphism & Micro-Borders**: Soft neutral dark backdrops (`#000000`, `#0a0a0a`), micro-borders (`border-white/[0.08]`), and selective backdrop blurs (`backdrop-blur-md`).
- **Data Honesty**: Status colors (Emerald, Amber, Rose, Purple) are used **strictly for functional meaning**—never as decorative clutter.

---

## 2. Component Architecture

```
frontend/src/
├── App.tsx                      # Root layout, sticky Navbar, subnav controller
├── index.css                    # Design tokens, cyber-grid-bg, scrollbars, reduced motion
├── components/
│   ├── layout/
│   │   ├── Navbar.tsx           # Sticky top navigation with brand, links & system dropdown
│   │   ├── WorkspaceSubnav.tsx  # Sleek horizontal tab-strip for security modules & views
│   │   ├── DemoJourneyBar.tsx   # Floating SIH presentation toolbar for hackathon judges
│   ├── common/
│   │   ├── Badge.tsx            # Minimal high-contrast status & severity dot badges
│   │   ├── GlassCard.tsx        # Vercel-style clean card with subtle border & depth
│   │   ├── TechnicalTerminalViewer.tsx # Monospace dark CLI modal ("One Evidence, Two Views")
│   │   ├── ReVerificationModal.tsx     # Before vs. After differential re-verification
│   │   ├── AuthorizationModal.tsx     # Dual-gate legal scope authorization modal
│   │   └── ToastContainer.tsx         # Non-blocking feedback notification toasts
└── pages/
    ├── HomePage.tsx             # Large typography hero, node flow, URL CTA, 7 module cards
    ├── GuidePage.tsx            # Interactive FAQ accordion with exploration progress tracking
    ├── EvidenceValidationPage.tsx # 3-column evidence vault with interactive progress timeline
    ├── FindingsPage.tsx         # Gradual-reveal findings catalog with severity dots
    ├── CommandCenterPage.tsx    # Executive security posture & deterministic risk score
    ├── DiscoveryPage.tsx        # Attack surface inventory
    ├── AssessmentProgressPage.tsx # Live pipeline execution stepper
    ├── FindingDetailPage.tsx    # In-depth technical breakdown of individual vulnerabilities
    ├── AiAnalysisPage.tsx       # Dedicated AI reasoning & adapter inspector
    ├── KnowledgeCorrelationPage.tsx # Offline CWE & OWASP Top 10 mappings
    ├── RiskPrioritizationPage.tsx # Deterministic multi-factor scoring
    ├── RemediationCenterPage.tsx  # Step-by-step remediation playbooks & code patches
    ├── SecurityReportPage.tsx   # Executive & compliance report generation
    ├── AssessmentHistoryPage.tsx# Audit timeline & differential re-tests
    ├── SystemStatusPage.tsx     # SOC context, Ollama engine health & telemetry
    └── SettingsPage.tsx         # Platform configuration & Ollama model selection
```

---

## 3. Color System

| Token / Color | Hex / Class | Semantic Meaning |
|---|---|---|
| **Base Surface** | `#000000` | Deep black background |
| **Card Surface** | `#0a0a0a` (`bg-neutral-900/40`) | Subtle elevated card container |
| **Micro Border** | `rgba(255, 255, 255, 0.08)` | Minimal dividing lines |
| **Text Primary** | `#ffffff` | Headings, primary emphasis, active items |
| **Text Muted** | `#a3a3a3` / `#737373` | Subtitles, descriptions, secondary metadata |
| **Safe / Verified** | Emerald (`#10b981`) | Cryptographically verified evidence, resolved issues |
| **Warning / Review**| Amber (`#f59e0b`) | Inconclusive probe, manual review required |
| **Critical / High** | Red (`#ef4444`) | Severe security defect, unauthenticated access |
| **AI / Reasoning**  | Purple (`#a855f7`) | Local LLM analysis, hypothesis translation |

---

## 4. Evidence UX ("One Evidence, Two Views")

The Evidence UX is the centerpiece of KAVACH:
1. **Interactive Timeline**:
   `FINDING` $\rightarrow$ `WHY` $\rightarrow$ `WHERE` $\rightarrow$ `PROOF` $\rightarrow$ `ANALYSIS` $\rightarrow$ `VERIFY` $\rightarrow$ `FIX` $\rightarrow$ `RE-VERIFY`
   Allows engineers and auditors to jump directly to any validation stage with smooth scrolling.
2. **Simple Evidence**:
   - **What We Found**: Plain-language observed anomaly.
   - **Why It Matters**: Threat impact explanation.
   - **Where**: Target URL, endpoint, affected component.
3. **Dedicated Proof Container**:
   - Evidence ID (`EVD-001`), Source, Timestamp.
   - Verbatim captured HTTP response / header payload.
   - Integrity Verified badge backed by SHA-256 hash.
4. **AI Reasoning Separation**:
   - Marked distinctly with `✦ AI ANALYSIS` and subtle purple accents.
   - Separated into: *What this means*, *Possible impact*, and *Recommended action*.
   - 3-step checklist: `✓ Evidence understood` $\rightarrow$ `✓ Risk analyzed` $\rightarrow$ `✓ Remediation ready`.
5. **Technical Terminal Viewer**:
   - Reproducible `curl` CLI command with one-click copy.
   - Side-by-side Expected vs. Observed result comparison.
   - Shared Evidence ID, Timestamp, and SHA-256 hash proving that the simple and technical views represent the exact same truth.
6. **Differential Re-Verification**:
   - Split view: `BEFORE FIX` (Initial Probe) vs. `AFTER FIX` (Re-Test Result).

---

## 5. Responsive Behavior & Accessibility

- **Breakpoints**: Optimized across Mobile (`< 640px`), Tablet (`640px - 1024px`), and Desktop (`> 1024px`).
- **Sticky Navbar**: Collapses gracefully to a slide-over mobile drawer on smaller viewports.
- **Evidence 3-Column Layout**: Stacks seamlessly into a single vertical stream on mobile while preserving the interactive timeline and copy actions.
- **Accessibility & Motion**:
  - Full support for `prefers-reduced-motion: reduce` in `index.css`.
  - High contrast ratios conforming to WCAG AA guidelines.
  - Native focus rings (`focus:border-white/40 focus:ring-1 focus:ring-white/20`).

---

## 6. File & Route Mapping

| Navigation Route | Page Component | Core Backend API Integration |
|---|---|---|
| `home` | `HomePage.tsx` | `api.getAssessments`, `api.createAssessment` |
| `command-center` | `CommandCenterPage.tsx` | `api.getAssessments`, `api.getFindings` |
| `new-assessment` | `NewAssessmentPage.tsx` | `api.createAssessment`, `api.getOllamaStatus` |
| `discovery` | `DiscoveryPage.tsx` | `api.getDiscoveryItems` |
| `progress` | `AssessmentProgressPage.tsx` | `api.getAssessment`, `api.executeProbe` |
| `findings` | `FindingsPage.tsx` | `api.getFindings` |
| `finding-detail` | `FindingDetailPage.tsx` | `api.getFinding`, `api.getEvidence`, `api.executeProbe` |
| `evidence` | `EvidenceValidationPage.tsx` | `api.getFindings`, `api.getEvidence`, `api.getTerminalVerification`, `api.executeProbe`, `api.reVerifyFinding` |
| `ai-analysis` | `AiAnalysisPage.tsx` | `api.getFindings`, `api.getOllamaStatus` |
| `knowledge` | `KnowledgeCorrelationPage.tsx` | `api.getKnowledge` |
| `risk` | `RiskPrioritizationPage.tsx` | `api.getRiskScoring` |
| `remediation` | `RemediationCenterPage.tsx` | `api.getFindings` |
| `report` | `SecurityReportPage.tsx` | `api.getReport`, `api.getExecutiveSummary` |
| `history` | `AssessmentHistoryPage.tsx` | `api.getAssessments`, `api.getReverifications` |
| `system-status` | `SystemStatusPage.tsx` | `api.getSystemStatus`, `api.getOllamaStatus` |
| `settings` | `SettingsPage.tsx` | `api.getOllamaStatus`, `api.selectModel` |
| `guide` | `GuidePage.tsx` | Standalone interactive architecture FAQ |
