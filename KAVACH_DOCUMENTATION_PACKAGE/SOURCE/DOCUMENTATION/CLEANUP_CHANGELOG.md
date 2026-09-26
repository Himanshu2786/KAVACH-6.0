# KAVACH 6.0 — Cleanup Changelog
**Audit Date**: 2026-09-22 | **Environment**: Windows 11 / Python 3.11.9 / PySide6 / React + Vite + TypeScript

---

### Record 1: Deprecated Pydantic V1 Config in Schemas
- **FILE/CODE**: `backend/app/schemas/schemas.py`
- **REASON**: Class-based `class Config: from_attributes = True` produced 6 Pydantic V2 deprecation warnings in pytest runs.
- **REFERENCE SEARCH**: Checked all references across `backend/app/` and test suites.
- **WHY SAFE TO EDIT**: Pydantic V2 native `model_config = ConfigDict(from_attributes=True)` is the standard successor for Pydantic V2.8+.
- **REPLACEMENT**: Modernized with `model_config = ConfigDict(from_attributes=True)`.
- **TEST RESULT**: All 23 API/portable tests and all 111 full suite tests passed with 0 warnings.

---

### Record 2: Deprecated Field Keyword in URL Check Route
- **FILE/CODE**: `backend/app/api/routes/url_check.py`
- **REASON**: `Field(..., example="https://example.com")` produced Pydantic V2 deprecation warnings.
- **REFERENCE SEARCH**: Checked `UrlScanRequest` schema usage across `url_check.py` and frontend callers.
- **WHY SAFE TO EDIT**: `json_schema_extra={"example": "https://example.com"}` complies with OpenAPI 3.1 / Pydantic V2 standards.
- **REPLACEMENT**: `Field(..., json_schema_extra={"example": "https://example.com"})`.
- **TEST RESULT**: All URL scanner and API tests passed.

---

### Record 3: Deprecated `.dict()` Method in Portable Routes
- **FILE/CODE**: `backend/app/api/routes/portable.py`
- **REASON**: Calling `.dict()` on Pydantic models generated 12 deprecation warnings in test suites.
- **REFERENCE SEARCH**: Checked `PermissionUpdateRequest` and `PermissionDetail` usage.
- **WHY SAFE TO EDIT**: `.model_dump()` is standard Pydantic V2 serialization.
- **REPLACEMENT**: `[p.model_dump() for p in ...]`
- **TEST RESULT**: `test_portable_scanners.py` passed with 0 warnings.

---

### Record 4: Broken Pip Comment Syntax in Requirements
- **FILE/CODE**: `backend/requirements.txt`
- **REASON**: Comments used `-->` syntax instead of standard `#`, causing pip requirement parser failure.
- **REFERENCE SEARCH**: Checked `backend/requirements.txt` and deployment documentation.
- **WHY SAFE TO EDIT**: Standard `#` comments are universally supported by pip.
- **REPLACEMENT**: Converted all annotations to `# ...`.
- **TEST RESULT**: Verified requirement parsing.

---

### Record 5: Obsolete Root Compressed Cache Archives
- **FILE/CODE**: `.pytest_cache.zip` (448 MB), `.zip` (224 MB)
- **REASON**: Abandoned historical zip archives in root workspace consuming over 670 MB of disk space.
- **REFERENCE SEARCH**: Ripgrep search confirmed 0 references in Python, TypeScript, YAML, JSON, or scripts.
- **WHY SAFE TO DELETE**: Temporary artifacts created during past manual packaging.
- **REPLACEMENT**: None needed. Active cache is managed in `.pytest_cache/`.
- **TEST RESULT**: PyTest and all builds unaffected.

---

### Record 6: Redundant Root Project Snapshot File
- **FILE/CODE**: `2.0 KAVACH_COMPLETE_PROJECT.md` (37 MB)
- **REASON**: Stale duplicate of `INFO/KAVACH_COMPLETE_PROJECT.md` left in root directory.
- **REFERENCE SEARCH**: Canonical context updater `1.0 UPDATE CONTEXT.bat` generates `INFO/KAVACH_COMPLETE_PROJECT.md`.
- **WHY SAFE TO DELETE**: `INFO/KAVACH_COMPLETE_PROJECT.md` and `INFO/KAVACH_5_COMPLETE_CONTEXT.md` are the canonical files.
- **REPLACEMENT**: `INFO/KAVACH_COMPLETE_PROJECT.md`.
- **TEST RESULT**: Build, tests, and context generation fully intact.

---

### Record 7: Assessment Progress Page � REPORT Stage Shows RUNNING Instead of COMPLETED

- **Bug**: For any completed assessment (status=COMPLETED, progress=100, current_stage=REPORT), the Stage Status badge showed **RUNNING** instead of **COMPLETED**. WorkflowStepper showed REPORT as pulsing active instead of green check.
- **Confirmed Case**: `ASM-F8CFA2EB` � backend: status=COMPLETED, progress=100, current_stage=REPORT. UI showed: Stage Status: RUNNING.
- **Root Cause**: `selectedIdx === currentIdx ? RUNNING` had no exception for assessment completion. When current_stage=REPORT and assessment is done, condition was true so badge showed RUNNING.
- **Files Changed**:
  - `frontend/src/pages/AssessmentProgressPage.tsx` � added assessmentCompleted boolean (status===COMPLETED OR progress>=100). Priority A badge: if done AND selectedIdx<=currentIdx ? COMPLETED.
  - `frontend/src/components/common/WorkflowStepper.tsx` � added optional assessmentCompleted prop; when true, isCompleted=currentIndex>=idx (includes current), isCurrent=false.
- **Fix Priority Order**: (A) done + stage<=current ? COMPLETED; (B) not done + stage<current ? COMPLETED; (C) not done + stage=current ? RUNNING; (D) stage>current ? PENDING.
- **Tests**: ASM-F8CFA2EB?REPORT=COMPLETED PASS | Refresh?COMPLETED persists PASS | Running asm?RUNNING+PENDING correct PASS | Prev stages?COMPLETED PASS | TSC: 0 errors | Vite build: 1890 modules OK | Pytest: 19/19 PASSED.
- **Backend**: Unchanged. No backend files modified.

