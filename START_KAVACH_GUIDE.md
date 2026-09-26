# KAVACH 6.0 — Windows Launcher and Operator Guide

Welcome to **KAVACH 6.0** (*Sovereign Security Intelligence Platform*). This guide explains how to launch, operate, develop, and test KAVACH on Windows with a single click.

---

## 1. Quick Start: One-Click Launch

To start KAVACH, simply **double-click** the main launcher batch file in the project folder:

```
📁 KAVACH 6.0\
 └── 🚀 START_KAVACH.bat   <-- Double-click this file
```

No manual PowerShell, command prompt commands, or terminal navigation are required.

---

## 2. What `START_KAVACH.bat` Does

When you launch `START_KAVACH.bat`, the automated boot sequence executes the following five phases:

1. **Path Resolution & Portability (`%~dp0`):** Automatically computes the exact folder where the script is located. Works whether KAVACH is placed on the Desktop, in Documents, on an external drive (`D:\`, `E:\`), or in a directory containing spaces (`C:\My Projects\KAVACH\`). No hardcoded usernames or absolute paths are used.
2. **Python Environment Discovery:** Automatically searches for an existing project virtual environment (`.venv\`, `venv\`, or `env\`). If found, it uses that Python executable. Otherwise, it falls back to the system Python (`python` or `py`).
3. **Pre-flight Integrity Checks:** Calls `scripts/launch_kavach.py` to verify:
   - Python version (Python 3.10+ required).
   - Core Python dependencies (`PySide6`, `fastapi`, `uvicorn`, `requests`, `pydantic`).
   - SQLite Database integrity (`kavach.db` preserved without data loss).
   - RAG Vector Knowledge Store (`backend/app/rag/knowledge_docs/`).
   - Ollama AI Service probe (`http://localhost:11434`).
4. **Desktop Application Launch:** Starts the PySide6 sovereign desktop application interface (`main.py`).
5. **Clean Exit & Error Logging:** Logs any startup errors to `logs/kavach_launcher.log` with human-readable diagnostic messages.

---

## 3. System & Python Requirements

- **Operating System:** Windows 10 / Windows 11 (64-bit)
- **Python Version:** Python 3.10 or higher (Python 3.11 recommended)
- **Administrator Privileges:** **Not required.** KAVACH runs safely under standard user permissions.

> **Note on Python Installation:**
> If Python is missing, download it from [python.org](https://www.python.org/downloads/). During installation, ensure the checkbox **"Add Python to PATH"** is checked.

---

## 4. Dependencies & Automatic Installation

If required Python packages are missing, the launcher will notify you:
```
[!] KAVACH dependencies are missing.
```
You can install all necessary packages at any time by running:
```cmd
pip install -r requirements.txt
```

Core dependencies include:
- `PySide6` (Desktop User Interface & Glassmorphism widgets)
- `fastapi` & `uvicorn` (Backend REST API & Swagger UI)
- `requests` & `urllib3` (URL Assessment & Network scanning)
- `pytest` & `anyio` (Test execution framework)

---

## 5. Ollama AI Engine & Fallback Behavior

KAVACH is designed to be fully functional **with or without Ollama**:

- **Ollama Online:** KAVACH connects to `http://localhost:11434` and uses local LLM models (`llama3`, `mistral`, `deepseek-r1`) for grounded RAG intelligence and threat synthesis.
- **Ollama Offline (Deterministic Fallback):** If Ollama is not installed or running, KAVACH does **not** crash or fail. It automatically switches to its deterministic rule-based security intelligence engine and displays the *Ollama Offline* notification with options to continue in Demo/Rule-based mode.

---

## 6. Database & Persistence

- **Database File:** `kavach.db` (located in the project root)
- **Safety Guarantee:** Launching KAVACH never resets, deletes, or overwrites existing findings, evidence records, audit trails, or assessment history.

---

## 7. Logs & Troubleshooting

Startup and runtime logs are written to:
```
logs\kavach_launcher.log
```

### Common Issues and Solutions

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `[ERROR] Python is not installed` | Python not found in system PATH | Install Python 3.10+ from python.org and check "Add Python to PATH". |
| `[!] Missing Python packages` | Dependencies not installed | Run `pip install -r requirements.txt`. |
| `Port 8000 is occupied` | Another process is using port 8000 | Close the existing process or use KAVACH Desktop which does not require port 8000. |
| UI crashes on startup | Missing Qt graphics libraries | Ensure latest graphics drivers and Windows updates are installed. |

---

## 8. Development Mode Launcher

For developers who want to run the FastAPI backend with hot-reload and the Vite React frontend concurrently:

```
🚀 START_KAVACH_DEV.bat   <-- Double-click to launch Dev Mode
```

- **Backend API:** `http://127.0.0.1:8000/api`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
- **Vite React UI:** `http://localhost:5173`

---

## 9. Automated Test Suite Launcher

To execute all unit, integration, and scanner test suites:

```
🧪 TEST_KAVACH.bat   <-- Double-click to run full test suite
```

The test runner automatically validates:
1. **Desktop UI Initialization:** Verifies that all 14 application pages load without errors.
2. **Scanner Suite:** 8/8 tests verifying secret redaction, double extensions, insecure configurations, SHA-256 reproducibility, and directory recursion.
3. **RAG Vector Intelligence:** 8/8 pytest tests verifying document loading, chunking, vector indexing, retrieval ranking, and query grounding.

---

## 10. How to Stop KAVACH

- **Desktop Application:** Simply close the KAVACH application window.
- **Development Mode:** Close the opened command prompt windows or press `Ctrl + C`.
