# KAVACH 6.0 — Self-Updating Documentation Package Guide

## Overview
This package (`KAVACH_DOCUMENTATION_PACKAGE`) is the authoritative, self-contained documentation and source artifact bundle for **KAVACH 6.0** (Enterprise Security Audit Standard).

## How to Update
To regenerate and update the complete documentation package at any time:
1. Double-click or execute:
   ```cmd
   UPDATE_KAVACH_COMPLETE_PROJECT.bat
   ```
2. The batch script runs `tools/update_kavach_complete_project.py` completely offline without requiring internet access or external APIs.

## Architecture of this Package
```
KAVACH_DOCUMENTATION_PACKAGE/
│
├── ..KAVACH_COMPLETE_PROJECT.md  <-- Master System Architecture & Implementation Document
├── UPDATE_KAVACH_COMPLETE_PROJECT.bat <-- The ONLY file you need to run to update docs
├── PROJECT_FILE_MANIFEST.md        <-- Full manifest of all included files & exclusions
├── UPDATE_README.md               <-- This usage guide
│
├── tools/
│   └── update_kavach_complete_project.py <-- Self-contained offline Python updater
│
├── SOURCE/                        <-- Curated, sanitized copies of real project files
│   ├── FRONTEND/
│   ├── BACKEND/
│   ├── DATABASE/
│   ├── TESTS/
│   ├── CONFIG/
│   └── DOCUMENTATION/
│
└── SNAPSHOT/
    └── latest_update.json         <-- Metadata of latest scan, hashes, and change detection
```

## Preserving Manual Documentation
The master document `..KAVACH_COMPLETE_PROJECT.md` separates generated and manual sections:
- Sections between `<!-- AUTO-GENERATED:START -->` and `<!-- AUTO-GENERATED:END -->` are updated dynamically from source code.
- Any notes, appendices, or diagrams added outside these tags are **strictly preserved** across subsequent runs.

## Secret Protection
The updater automatically scans all files for API keys, AWS credentials, Bearer tokens, and private keys, replacing them with `[REDACTED]` before saving copies into `SOURCE/` or generating documentation.
