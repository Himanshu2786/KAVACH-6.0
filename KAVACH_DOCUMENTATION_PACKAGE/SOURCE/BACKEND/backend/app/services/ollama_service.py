"""
KAVACH Local AI Engine Service (Ollama Integration)
Strict Architecture:
  REAL SCANNER -> RAW RESULT -> EVIDENCE ENGINE -> VALIDATED FINDING -> OLLAMA -> AI EXPLANATION -> REMEDIATION -> USER

Ollama is NOT the vulnerability detector.
Ollama only receives sanitized, validated findings and never invents vulnerabilities, CVEs, or evidence.
"""

import httpx
import time
import json
import os
import sys
import shutil
import subprocess
import re
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.selected_model = settings.OLLAMA_MODEL
        self.timeout = settings.AI_TIMEOUT
        self.is_starting = False
        self.start_attempted_at = 0.0
        self.process_handle = None
        self.detected_ollama_path = self._locate_ollama_binary()

    @property
    def api_key(self) -> str:
        return getattr(settings, "OLLAMA_API_KEY", "") or ""

    def _get_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        key = self.api_key.strip()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        return headers

    def _locate_ollama_binary(self) -> Optional[str]:
        """Check for local Ollama executable in PATH or standard installation locations."""
        # 1. System PATH
        in_path = shutil.which("ollama")
        if in_path:
            return in_path

        # 2. Windows Local AppData
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            candidate = os.path.join(local_app_data, "Programs", "Ollama", "ollama.exe")
            if os.path.exists(candidate):
                return candidate

        # 3. Program Files
        prog_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        candidate_pf = os.path.join(prog_files, "Ollama", "ollama.exe")
        if os.path.exists(candidate_pf):
            return candidate_pf

        return None

    def mask_sensitive_data(self, text: str) -> str:
        """Sanitizes passwords, credentials, keys, and tokens prior to forwarding to the AI model."""
        if not text or not settings.AI_MASK_SENSITIVE:
            return text

        masked = text

        # 1. Mask AWS Access Keys (AKIA...)
        masked = re.sub(r'AKIA[0-9A-Z]{16}', 'AKIA***[MASKED_AWS_KEY]', masked)

        # 2. Mask Database Connection Strings with Passwords (e.g. postgresql://user:pass@host)
        masked = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***[MASKED_PASSWORD]@', masked)

        # 3. Mask Bearer Authorization tokens
        masked = re.sub(r'(Bearer\s+)[A-Za-z0-9\-_\.=]{8,}', r'\1***[MASKED_BEARER_TOKEN]', masked, flags=re.IGNORECASE)

        # 4. Mask Slack Webhook URLs
        masked = re.sub(r'hooks\.slack\.com/services/[A-Za-z0-9/]+', 'hooks.slack.com/services/***[MASKED_WEBHOOK]', masked)

        # 5. Mask Generic API Secrets / Passwords in JSON or key-value format
        masked = re.sub(r'("?(?:password|secret|jwt_secret|api_key|access_key|auth_token|client_secret)"?\s*[:=]\s*)"([^"]+)"', r'\1"***[MASKED]"', masked, flags=re.IGNORECASE)
        masked = re.sub(r'("?(?:password|secret|jwt_secret|api_key|access_key|auth_token|client_secret)"?\s*[:=]\s*)([^\s,;}{]+)', r'\1"***[MASKED]"', masked, flags=re.IGNORECASE)

        # 6. Mask Private Key blocks
        masked = re.sub(r'-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+PRIVATE KEY-----', '[REDACTED_CRYPTOGRAPHIC_PRIVATE_KEY]', masked)

        return masked

    def set_model(self, model_name: str):
        self.selected_model = model_name

    def set_timeout(self, timeout_sec: float):
        self.timeout = timeout_sec

    def attempt_auto_start(self) -> Dict[str, Any]:
        """Transparent, documented background startup of local Ollama service if installed."""
        is_local = "127.0.0.1" in self.base_url or "localhost" in self.base_url
        if self.api_key.strip() or not is_local:
            return {
                "success": False,
                "message": "Remote or Cloud Ollama configured. Local background service startup skipped."
            }

        if not self.detected_ollama_path:
            return {
                "success": False,
                "message": "Ollama executable not found on local host. Please install from https://ollama.com."
            }

        # Check if already starting recently (within 10s)
        if self.is_starting and (time.time() - self.start_attempted_at < 10):
            return {
                "success": True,
                "status": "AI STARTING",
                "message": "Local Ollama service startup already in progress."
            }

        try:
            self.is_starting = True
            self.start_attempted_at = time.time()

            # Set OLLAMA_ORIGINS=* for seamless web connectivity
            env = os.environ.copy()
            env["OLLAMA_ORIGINS"] = "*"

            # Start detached process without opening console window on Windows
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS

            self.process_handle = subprocess.Popen(
                [self.detected_ollama_path, "serve"],
                env=env,
                creationflags=creation_flags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return {
                "success": True,
                "status": "AI STARTING",
                "binary_path": self.detected_ollama_path,
                "message": f"Transparently launched local Ollama service (PID: {self.process_handle.pid})."
            }
        except Exception as e:
            self.is_starting = False
            return {
                "success": False,
                "status": "AI OFFLINE",
                "message": f"Failed starting local Ollama service: {str(e)}"
            }

    async def check_health(self) -> Dict[str, Any]:
        """
        Evaluates Ollama health across 4 distinct lifecycle states:
          - AI READY: Service online + configured model present
          - AI STARTING: Service startup recently attempted
          - MODEL UNAVAILABLE: Service online, but configured model not pulled
          - AI OFFLINE: Service unreachable
        """
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags", headers=self._get_headers())
                elapsed_ms = round((time.time() - start_time) * 1000, 2)
                
                if res.status_code == 200:
                    self.is_starting = False
                    data = res.json()
                    models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
                    raw_model_names = [m.get("name", "") for m in data.get("models", [])]

                    # Check configured model presence
                    configured_base = self.selected_model.split(":")[0]
                    has_configured_model = (
                        configured_base in models or 
                        self.selected_model in raw_model_names or
                        any(self.selected_model in m for m in raw_model_names)
                    )

                    if has_configured_model:
                        status_label = "AI READY"
                        status_code = "ready"
                        status_dot = "🟢"
                        message = f"Local Ollama engine online with model '{self.selected_model}'."
                    else:
                        status_label = "MODEL UNAVAILABLE"
                        status_code = "model_unavailable"
                        status_dot = "🟠"
                        message = (
                            f"Ollama is online, but model '{self.selected_model}' is not installed. "
                            f"Run 'ollama pull {self.selected_model}' or choose an installed model."
                        )

                    return {
                        "status": "online",
                        "lifecycle_state": status_label,
                        "status_code": status_code,
                        "status_dot": status_dot,
                        "base_url": self.base_url,
                        "available_models": raw_model_names,
                        "selected_model": self.selected_model,
                        "has_configured_model": has_configured_model,
                        "response_time_ms": elapsed_ms,
                        "ollama_binary": self.detected_ollama_path,
                        "message": message
                    }
                else:
                    return {
                        "status": "offline",
                        "lifecycle_state": "AI OFFLINE",
                        "status_code": "offline",
                        "status_dot": "🔴",
                        "base_url": self.base_url,
                        "available_models": [],
                        "selected_model": self.selected_model,
                        "has_configured_model": False,
                        "response_time_ms": None,
                        "ollama_binary": self.detected_ollama_path,
                        "message": f"Ollama returned unexpected HTTP {res.status_code}"
                    }
        except Exception as ex:
            # If recently starting, show AI STARTING
            if self.is_starting and (time.time() - self.start_attempted_at < 8):
                return {
                    "status": "starting",
                    "lifecycle_state": "AI STARTING",
                    "status_code": "starting",
                    "status_dot": "🟡",
                    "base_url": self.base_url,
                    "available_models": [],
                    "selected_model": self.selected_model,
                    "has_configured_model": False,
                    "response_time_ms": None,
                    "ollama_binary": self.detected_ollama_path,
                    "message": "Local Ollama service is initializing..."
                }

            # If auto_start is enabled, binary exists, and not remote/cloud, trigger one attempt
            is_local = "127.0.0.1" in self.base_url or "localhost" in self.base_url
            if settings.AI_AUTO_START and self.detected_ollama_path and is_local and not self.api_key.strip() and not self.is_starting:
                self.attempt_auto_start()

            return {
                "status": "offline",
                "lifecycle_state": "AI OFFLINE",
                "status_code": "offline",
                "status_dot": "🔴",
                "base_url": self.base_url,
                "available_models": [],
                "selected_model": self.selected_model,
                "has_configured_model": False,
                "response_time_ms": None,
                "ollama_binary": self.detected_ollama_path,
                "message": f"Ollama service is not reachable on {self.base_url}. Running in deterministic rule mode."
            }

    async def generate_completion(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """
        Sends sanitized prompt to local Ollama.
        Guarantees all credentials/secrets are masked before leaving KAVACH.
        """
        if not settings.AI_ENABLED:
            return None

        # Mask sensitive secrets
        sanitized_user_prompt = self.mask_sensitive_data(user_prompt)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.selected_model,
                    "system": system_prompt,
                    "prompt": sanitized_user_prompt,
                    "format": "json",
                    "stream": False
                }
                res = await client.post(f"{self.base_url}/api/generate", json=payload, headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "")
                return None
        except Exception:
            return None

ollama_service = OllamaService()
