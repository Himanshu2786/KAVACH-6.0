# KAVACH 6.0 — PORTABLE USB EDITION
## AI-Assisted Security Assessment Platform (SIH PS 26163)

Welcome to the portable distribution of **KAVACH**. This package is structured to execute directly from a USB drive or portable storage on Windows systems without requiring permanent system installation.

---

## Directory Structure

`
KAVACH_USB/
│
├── KAVACH.exe                 # Single-file portable launcher & core engine (~55MB)
│
├── AI/                        # Local AI Explanation Engine Configuration
│   ├── config.json            # Centralized configuration (provider, model, timeout, masking)
│   ├── start_ai.bat           # Manual/automated background launcher for Ollama
│   └── README.md              # AI architecture and lifecycle documentation
│
├── scanners/                  # Built-in scanner definitions and permission matrices
│   └── README.md              # Inspection rules (Processes, Apps, Sockets, Posture)
│
├── evidence/                  # Real-time cryptographically hashed evidence store
│   └── README.md              # SHA-256 evidence vault specifications
│
├── database/                  # Assessment database and audit storage
│   └── kavach.db              # SQLite relational store with CWE/OWASP knowledge
│
├── DEMO/                      # SIH Presentation test suites and training samples
│   └── training_samples/      # Pre-built mock and synthetic test targets
│
├── INFO/                      # Full platform architectural documentation
│   ├── AI_SYSTEM.md
│   ├── EVIDENCE_SYSTEM.md
│   ├── PS_26163_COMPLIANCE.md
│   └── ...
│
├── logs/                      # Audit trails and engine execution logs
│   └── audit.log
│
└── README.md                  # This file
`

---

## What is Bundled vs. What Must Be Installed

### 1. 100% Bundled & Ready to Run (Zero Setup)
- **KAVACH.exe**: Contains the full FastAPI backend, React dashboard, SQLite database, offline CWE/OWASP knowledge bank, terminal verification generator, and deterministic fallback explanation engine.
- **scanners/**: Native Windows scanners for processes, listening sockets, installed applications, security products, and posture benchmarks.
- **evidence/**: Cryptographic evidence capture engine with SHA-256 integrity verification.
- **database/kavach.db**: Complete seeded database with 15+ CWEs, OWASP Top 10 mappings, remediation playbooks, and sample assessments.
- **DEMO/**: Curated SIH demonstration scenarios (DEMO-001, DEMO-002, DEMO-003).

### 2. External Prerequisites (For AI Explanation Feature Only)
> **Ollama is NOT embedded inside KAVACH.exe.**
> Falsely claiming an LLM runtime is embedded inside a 55MB executable is deceptive. Ollama is an external local AI service that runs alongside KAVACH.

- **Ollama Runtime**: If you wish to use the Local AI Explanation Engine, install Ollama from https://ollama.com or copy a portable Ollama folder to the USB.
- **Model Weights**: Run ollama pull llama3 (or ollama pull mistral).
- **AI Startup**: When KAVACH starts, it detects if Ollama is running. If not, it attempts to launch it in the background if installed at standard locations (%LOCALAPPDATA%\Programs\Ollama\ollama.exe or system PATH).

---

## Hardware & Storage Requirements

| Specification | Minimum | Recommended |
| :--- | :--- | :--- |
| **USB Storage** | 1 GB (without LLM) | 16 GB+ USB 3.0 (with Ollama & models) |
| **RAM** | 4 GB (KAVACH Rule Mode) | 16 GB DDR4/DDR5 (with Llama 3 8B) |
| **CPU** | Dual-core x86-64 | Quad-core modern Intel/AMD with AVX2 |
| **GPU (Optional)** | None required | NVIDIA GPU with 6GB+ VRAM for instant inference |
| **OS** | Windows 10 / 11 (64-bit) | Windows 11 (64-bit) with Administrator privileges for deep scanning |

---

## Offline Limitations & Deterministic AI Fallback

- **100% Air-Gapped Operation**: KAVACH works completely offline. It never dials out to OpenAI, Anthropic, or external cloud APIs.
- **Zero Hallucination Guarantee**: Ollama is **NEVER** the vulnerability detector. Scanners capture raw evidence; only verified findings are passed to Ollama for plain-English explanation.
- **AI Offline Mode**: If Ollama is not running, KAVACH switches to **AI OFFLINE** with **zero breakage**. All 7 structured explanation sections (WHAT WAS FOUND, WHERE, WHY IT MATTERS, POSSIBLE IMPACT, RECOMMENDED ACTION, HOW TO FIX, HOW TO VERIFY) are instantly served by KAVACH's deterministic security rule engine.
