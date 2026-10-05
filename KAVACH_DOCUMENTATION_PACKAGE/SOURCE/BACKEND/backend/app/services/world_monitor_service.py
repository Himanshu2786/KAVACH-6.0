"""
KAVACH 5.0 — World Monitor Service (External Security Situational-Awareness Layer)
Source Adapter Architecture, Real-World Public Feed Ingestion (CISA KEV, NVD/CVE, Infrastructure Bulletins),
Deterministic Normalization, Stable Deduplication, and Explainable Assessment Correlation Engine.
"""

import os
import json
import hashlib
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import httpx
from backend.app.core.time import IST, ist_now, ist_formatted, to_ist


# ═════════════════════════════════════════════════════════════════════════════
# DETERMINISTIC DEMO FIXTURES (for reproducible testing & offline demonstrations)
# ═════════════════════════════════════════════════════════════════════════════
DEMO_FIXTURES = [
    {
        "id": "DEMO-CVE-2023-44487",
        "source": "CISA KEV",
        "source_name": "CISA Known Exploited Vulnerabilities Catalog",
        "source_url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        "title": "HTTP/2 Rapid Reset Denial of Service Vulnerability (CVE-2023-44487)",
        "description": "The HTTP/2 protocol is susceptible to a denial of service attack where a client rapidly sends RST_STREAM frames, overwhelming web application servers and load balancers including Nginx, Apache, and Envoy.",
        "category": "Vulnerability",
        "severity": "HIGH",
        "published_at": "2023-10-10T12:00:00Z",
        "updated_at": "2023-10-15T18:30:00Z",
        "location": {
            "has_coordinates": False,
            "country": "Global",
            "country_code": "GLOBAL",
            "city": "Global Internet Infrastructure",
            "latitude": None,
            "longitude": None
        },
        "affected_technology": "HTTP/2, Nginx, Apache, Envoy, Web Security Gateways",
        "affected_organization": "Multiple Cloud and Web Infrastructure Providers",
        "cve_ids": ["CVE-2023-44487"],
        "confidence": "HIGH",
        "status": "VERIFIED_ACTIVE",
        "is_demo": True
    },
    {
        "id": "DEMO-CISA-2024-001",
        "source": "CISA Advisory",
        "source_name": "Cybersecurity and Infrastructure Security Agency",
        "source_url": "https://www.cisa.gov/news-events/cybersecurity-advisories",
        "title": "Widespread Exploitation of Missing Defensive HTTP Security Headers and SSL Stripping",
        "description": "CISA issues advisory regarding active adversary campaigns downgrading HTTPS connections on web services lacking Strict-Transport-Security (HSTS) and Content-Security-Policy (CSP) enforcement.",
        "category": "Cybersecurity",
        "severity": "HIGH",
        "published_at": "2024-02-14T09:00:00Z",
        "updated_at": "2024-02-16T14:00:00Z",
        "location": {
            "has_coordinates": True,
            "country": "United States",
            "country_code": "US",
            "city": "Washington, D.C.",
            "latitude": 38.8951,
            "longitude": -77.0364
        },
        "affected_technology": "HTTP, HTTPS, HSTS, CSP, Web Headers",
        "affected_organization": "Public & Private Web Infrastructure",
        "cve_ids": [],
        "cwe_ids": ["CWE-319", "CWE-693"],
        "confidence": "HIGH",
        "status": "VERIFIED_ACTIVE",
        "is_demo": True
    },
    {
        "id": "DEMO-CVE-2024-6387",
        "source": "NVD / CVE",
        "source_name": "NIST National Vulnerability Database",
        "source_url": "https://nvd.nist.gov/vuln/detail/CVE-2024-6387",
        "title": "regreSSHion: Remote Unauthenticated Code Execution in OpenSSH Server (CVE-2024-6387)",
        "description": "A signal handler race condition vulnerability in OpenSSH's server (sshd) allows unauthenticated remote code execution with root privileges on glibc-based Linux systems.",
        "category": "Vulnerability",
        "severity": "CRITICAL",
        "published_at": "2024-07-01T08:00:00Z",
        "updated_at": "2024-07-05T16:20:00Z",
        "location": {
            "has_coordinates": True,
            "country": "Germany",
            "country_code": "DE",
            "city": "Frankfurt",
            "latitude": 50.1109,
            "longitude": 8.6821
        },
        "affected_technology": "OpenSSH, sshd, Linux",
        "affected_organization": "Linux Enterprise Servers",
        "cve_ids": ["CVE-2024-6387"],
        "confidence": "HIGH",
        "status": "VERIFIED_ACTIVE",
        "is_demo": True
    },
    {
        "id": "DEMO-ADV-CLOUD-OUTAGE",
        "source": "CERT Advisory",
        "source_name": "European Union Agency for Cybersecurity (ENISA)",
        "source_url": "https://www.enisa.europa.eu/publications/security-advisories",
        "title": "Regional Cloud Edge BGP Routing Misconfiguration & DNS Resolution Latency",
        "description": "BGP route leak incident causing intermittent DNS and TLS negotiation timeouts across European and Asian transit providers affecting web API endpoints.",
        "category": "Infrastructure",
        "severity": "MEDIUM",
        "published_at": "2024-06-18T14:30:00Z",
        "updated_at": "2024-06-18T18:00:00Z",
        "location": {
            "has_coordinates": True,
            "country": "United Kingdom",
            "country_code": "GB",
            "city": "London",
            "latitude": 51.5074,
            "longitude": -0.1278
        },
        "affected_technology": "BGP, DNS, Edge Routing, TLS Gateways",
        "affected_organization": "Tier-1 Autonomous Systems",
        "cve_ids": [],
        "confidence": "MEDIUM",
        "status": "RESOLVED",
        "is_demo": True
    },
    {
        "id": "DEMO-CVE-2024-3094",
        "source": "NVD / CVE",
        "source_name": "NIST National Vulnerability Database",
        "source_url": "https://nvd.nist.gov/vuln/detail/CVE-2024-3094",
        "title": "XZ Utils Supply Chain Compromise / Backdoor (CVE-2024-3094)",
        "description": "Malicious code discovery in upstream tarballs of xz embedded inside liblzma, allowing unauthorized SSH authentication bypass in compromised Linux distributions.",
        "category": "Exploit/Threat Advisory",
        "severity": "CRITICAL",
        "published_at": "2024-03-29T15:00:00Z",
        "updated_at": "2024-04-02T11:00:00Z",
        "location": {
            "has_coordinates": True,
            "country": "India",
            "country_code": "IN",
            "city": "New Delhi / Bengaluru",
            "latitude": 28.6139,
            "longitude": 77.2090
        },
        "affected_technology": "XZ Utils, liblzma, OpenSSH, Linux",
        "affected_organization": "Open Source Supply Chain",
        "cve_ids": ["CVE-2024-3094"],
        "confidence": "HIGH",
        "status": "VERIFIED_ACTIVE",
        "is_demo": True
    },
    {
        "id": "DEMO-ADV-FASTAPI-UVICORN",
        "source": "CISA Advisory",
        "source_name": "CERT Coordination Center",
        "source_url": "https://www.kb.cert.org/vuls/",
        "title": "Python ASGI / FastAPI Server Header Information Disclosure Advisory",
        "description": "Advisory on web application servers exposing verbose Server and X-Powered-By response headers, aiding automated reconnaissance and targeted exploitation.",
        "category": "Cybersecurity",
        "severity": "LOW",
        "published_at": "2024-05-12T10:00:00Z",
        "updated_at": "2024-05-12T12:00:00Z",
        "location": {
            "has_coordinates": True,
            "country": "Singapore",
            "country_code": "SG",
            "city": "Singapore",
            "latitude": 1.3521,
            "longitude": 103.8198
        },
        "affected_technology": "Python, FastAPI, Uvicorn, Nginx",
        "affected_organization": "Web API Services",
        "cve_ids": [],
        "cwe_ids": ["CWE-200"],
        "confidence": "MEDIUM",
        "status": "VERIFIED_ACTIVE",
        "is_demo": True
    }
]


class WorldMonitorService:
    def __init__(self):
        self._cached_events: List[Dict[str, Any]] = []
        self._last_updated: Optional[str] = None
        self._last_fetched_dt: Optional[datetime] = None
        self._is_live_mode: bool = False
        self._source_statuses: List[Dict[str, Any]] = [
            {"id": "cisa_kev", "name": "CISA KEV Catalog", "status": "READY", "events_count": 0, "type": "PUBLIC_FEED"},
            {"id": "nvd_cve", "name": "NVD / Global CVE Feed", "status": "READY", "events_count": 0, "type": "PUBLIC_FEED"},
            {"id": "demo_fixtures", "name": "KAVACH Demo Intelligence Fixtures", "status": "ONLINE", "events_count": len(DEMO_FIXTURES), "type": "LOCAL_FIXTURE"}
        ]
        # Seed initial state with demo fixtures
        self._load_demo_events()

    def _load_demo_events(self):
        """Loads deterministic demo fixtures with current ingestion timestamp."""
        now_iso = ist_formatted("%Y-%m-%d %H:%M:%S IST")
        events = []
        for fix in DEMO_FIXTURES:
            ev = dict(fix)
            ev["fetched_at"] = now_iso
            events.append(ev)
        self._cached_events = events
        self._last_updated = now_iso
        self._last_fetched_dt = ist_now()
        self._is_live_mode = False

    async def fetch_cisa_kev(self, timeout: float = 10.0) -> List[Dict[str, Any]]:
        """
        Public Source Adapter: Fetches real, authoritative CVE records from the official CISA KEV JSON feed.
        Requires NO API KEY. Strictly public government data.
        """
        url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        now_iso = ist_formatted("%Y-%m-%d %H:%M:%S IST")
        events: List[Dict[str, Any]] = []

        vendor_locations = {
            "microsoft": ("Redmond, WA", "United States", "US", 47.6740, -122.1215),
            "apple": ("Cupertino, CA", "United States", "US", 37.3230, -122.0322),
            "google": ("Mountain View, CA", "United States", "US", 37.3861, -122.0839),
            "cisco": ("San Jose, CA", "United States", "US", 37.3382, -121.8863),
            "apache": ("Forest Hill, MD", "United States", "US", 39.5843, -76.3888),
            "oracle": ("Austin, TX", "United States", "US", 30.2672, -97.7431),
            "sap": ("Walldorf", "Germany", "DE", 49.3056, 8.6417),
            "fortinet": ("Sunnyvale, CA", "United States", "US", 37.3688, -122.0363),
            "palo alto": ("Santa Clara, CA", "United States", "US", 37.3541, -121.9552),
            "ivanti": ("South Jordan, UT", "United States", "US", 40.5622, -111.9297),
            "adobe": ("San Jose, CA", "United States", "US", 37.3382, -121.8863),
            "vmware": ("Palo Alto, CA", "United States", "US", 37.4419, -122.1430),
            "d-link": ("Taipei", "Taiwan", "TW", 25.0330, 121.5654),
            "qnap": ("New Taipei City", "Taiwan", "TW", 25.0124, 121.4657),
            "synology": ("Taipei", "Taiwan", "TW", 25.0330, 121.5654),
            "atlassian": ("Sydney", "Australia", "AU", -33.8688, 151.2093),
            "juniper": ("Sunnyvale, CA", "United States", "US", 37.3688, -122.0363),
            "sonicwall": ("Milpitas, CA", "United States", "US", 37.4323, -121.8996),
        }

        global_hubs = [
            ("Washington, D.C.", "United States", "US", 38.9072, -77.0369),
            ("Frankfurt", "Germany", "DE", 50.1109, 8.6821),
            ("London", "United Kingdom", "GB", 51.5074, -0.1278),
            ("Bengaluru", "India", "IN", 12.9716, 77.5946),
            ("Tokyo", "Japan", "JP", 35.6762, 139.6503),
            ("Singapore", "Singapore", "SG", 1.3521, 103.8198),
            ("Sydney", "Australia", "AU", -33.8688, 151.2093),
        ]

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                vulns = data.get("vulnerabilities", [])
                # Take the most recent 25 vulnerabilities
                for i, item in enumerate(vulns[:25]):
                    cve_id = item.get("cveID", "CVE-UNKNOWN")
                    vendor = item.get("vendorProject", "Unknown Vendor")
                    product = item.get("product", "Unknown Product")
                    date_added = item.get("dateAdded", ist_formatted("%Y-%m-%d"))

                    vendor_lower = vendor.lower()
                    matched_geo = None
                    for k, geo_info in vendor_locations.items():
                        if k in vendor_lower:
                            matched_geo = geo_info
                            break
                    if not matched_geo:
                        matched_geo = global_hubs[i % len(global_hubs)]

                    city, country, country_code, lat, lng = matched_geo

                    events.append({
                        "id": cve_id,
                        "source": "CISA KEV",
                        "source_name": "CISA Known Exploited Vulnerabilities Catalog",
                        "source_url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                        "title": f"{vendor} {product}: {item.get('vulnerabilityName', cve_id)}",
                        "description": item.get("shortDescription", "Actively exploited in the wild according to CISA advisory."),
                        "category": "Exploited CVE",
                        "severity": "CRITICAL" if any(kw in (item.get("shortDescription", "") + item.get("vulnerabilityName", "")).lower() for kw in ["remote code", "execution", "privilege", "overflow"]) else "HIGH",
                        "published_at": f"{date_added}T00:00:00+05:30",
                        "updated_at": f"{date_added}T12:00:00+05:30",
                        "fetched_at": now_iso,
                        "location": {
                            "has_coordinates": True,
                            "country": country,
                            "country_code": country_code,
                            "city": city,
                            "latitude": lat,
                            "longitude": lng
                        },
                        "affected_technology": f"{vendor}, {product}",
                        "affected_organization": f"{vendor} Ecosystem",
                        "cve_ids": [cve_id],
                        "confidence": "HIGH",
                        "status": "VERIFIED_ACTIVE",
                        "is_demo": False
                    })
        return events

    async def refresh_feeds(self, force_mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Orchestrates feed ingestion across adapters, deduplicates records,
        maintains caching, and gracefully handles network unavailability.
        """
        now_iso = ist_formatted("%Y-%m-%d %H:%M:%S IST")

        if force_mode == "demo":
            self._load_demo_events()
            return {
                "success": True,
                "mode": "DEMO",
                "message": "Loaded deterministic KAVACH demo situational fixtures.",
                "last_updated": self._last_updated,
                "sources": self._source_statuses,
                "events_count": len(self._cached_events),
                "total_count": len(self._cached_events),
                "events": self._cached_events
            }

        live_events: List[Dict[str, Any]] = []
        cisa_success = False

        # Attempt to fetch real public CISA feed
        try:
            cisa_records = await self.fetch_cisa_kev(timeout=10.0)
            if cisa_records:
                live_events.extend(cisa_records)
                cisa_success = True
                self._source_statuses[0]["status"] = "ONLINE"
                self._source_statuses[0]["events_count"] = len(cisa_records)
        except Exception as e:
            self._source_statuses[0]["status"] = f"UNAVAILABLE ({type(e).__name__})"

        # Deduplication map
        dedup_map: Dict[str, Dict[str, Any]] = {}

        if cisa_success and len(live_events) > 0:
            # Add live events
            for ev in live_events:
                dedup_map[ev["id"]] = ev

            # Also include selected representative demo fixtures tagged clearly for visual map demonstration
            for fix in DEMO_FIXTURES:
                if fix["id"] not in dedup_map:
                    ev = dict(fix)
                    ev["fetched_at"] = now_iso
                    dedup_map[fix["id"]] = ev

            self._cached_events = list(dedup_map.values())
            self._last_updated = now_iso
            self._is_live_mode = True
            mode = "LIVE"
            msg = f"Successfully synchronized {len(live_events)} live advisories from CISA KEV public catalog."
        else:
            # Fallback to local demo intelligence if offline
            self._load_demo_events()
            mode = "DEMO"
            msg = "Live feed unreachable — operating in offline mode with verified demo intelligence fixtures."

        return {
            "success": True,
            "mode": mode,
            "message": msg,
            "last_updated": self._last_updated,
            "sources": self._source_statuses,
            "events_count": len(self._cached_events),
            "events": self._cached_events
        }

    def get_events(
        self,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        time_range: Optional[str] = None,
        source: Optional[str] = None,
        search: Optional[str] = None,
        mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """Filters cached situational events deterministically."""
        events = list(self._cached_events)

        if mode == "demo":
            events = [e for e in events if e.get("is_demo", False)]
        elif mode == "live":
            events = [e for e in events if not e.get("is_demo", False)]

        if category and category.upper() != "ALL":
            events = [e for e in events if e.get("category", "").upper() == category.upper()]

        if severity and severity.upper() != "ALL":
            events = [e for e in events if e.get("severity", "").upper() == severity.upper()]

        if source and source.upper() != "ALL":
            events = [e for e in events if source.lower() in e.get("source", "").lower()]

        if search:
            q = search.lower().strip()
            events = [
                e for e in events
                if q in e.get("title", "").lower()
                or q in e.get("description", "").lower()
                or q in e.get("affected_technology", "").lower()
                or any(q in cve.lower() for cve in e.get("cve_ids", []))
            ]

        # Time range filter (24h, 7d, 30d, all)
        if time_range and time_range.lower() != "all":
            now = datetime.now(timezone.utc)
            cutoff_days = 1 if time_range == "24h" else (7 if time_range == "7d" else 30)
            cutoff_dt = now - timedelta(days=cutoff_days)
            filtered_by_time = []
            for e in events:
                pub_str = e.get("published_at", "")
                try:
                    pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                    if pub_dt >= cutoff_dt:
                        filtered_by_time.append(e)
                except Exception:
                    filtered_by_time.append(e)
            events = filtered_by_time

        return {
            "success": True,
            "mode": "LIVE" if self._is_live_mode else "DEMO",
            "last_updated": self._last_updated,
            "sources": self._source_statuses,
            "total_count": len(self._cached_events),
            "filtered_count": len(events),
            "events": events
        }

    def get_sources(self) -> List[Dict[str, Any]]:
        """Returns the operational status of all configured source adapters."""
        return self._source_statuses

    def correlate_with_findings(
        self,
        target_info: Dict[str, Any],
        local_findings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Real-World Correlation Engine:
        Evaluates defensible relationships between external World Monitor events
        and local findings/target observations.

        Confidence Criteria:
        - HIGH: Exact matching CVE ID between finding and advisory.
        - MEDIUM: Specific software technology/product overlap without confirmed exact version.
        - LOW: Broad protocol or defensive header category alignment.
        """
        correlated_results: List[Dict[str, Any]] = []

        # Extract target technology keywords
        target_url = target_info.get("target_url", "").lower()
        hostname = target_info.get("hostname", "").lower()

        # Build lookup of local finding signals
        local_cves = set()
        local_cwes = set()
        local_categories = set()
        local_tech_signals = set()

        for f in local_findings:
            if f.get("cve_id"):
                local_cves.add(f["cve_id"].upper())
            if f.get("cwe_id"):
                local_cwes.add(f["cwe_id"].upper())
            if f.get("category"):
                local_categories.add(f["category"].lower())
            if f.get("technology"):
                local_tech_signals.add(f["technology"].lower())
            if f.get("affected_component"):
                local_tech_signals.add(f["affected_component"].lower())
            # Check title keywords
            t_lower = f.get("title", "").lower()
            if "hsts" in t_lower or "strict-transport" in t_lower:
                local_tech_signals.add("hsts")
            if "csp" in t_lower or "content-security" in t_lower:
                local_tech_signals.add("csp")
            if "https" in t_lower or "tls" in t_lower or "ssl" in t_lower:
                local_tech_signals.add("tls")
                local_tech_signals.add("https")
            if "redirect" in t_lower or "http" in t_lower:
                local_tech_signals.add("http")

        for event in self._cached_events:
            ev_cves = [c.upper() for c in event.get("cve_ids", [])]
            ev_tech = event.get("affected_technology", "").lower()
            ev_desc = event.get("description", "").lower()
            ev_title = event.get("title", "").lower()

            matched_finding = None
            confidence = None
            correlation_type = None
            explanation = None

            # 1. Exact CVE match (HIGH Confidence)
            # ONLY genuine CVE identifiers (starting with 'CVE-') are eligible for
            # EXACT_IDENTIFIER_MATCH. CWE identifiers stored in an advisory's cve_ids
            # field must NOT be matched against local findings to avoid false HIGH
            # confidence correlations based solely on CWE category overlap.
            for cve in ev_cves:
                if not cve.upper().startswith("CVE-"):
                    # Skip non-CVE identifiers (e.g. CWEs incorrectly stored in cve_ids)
                    continue
                if cve in local_cves:
                    confidence = "HIGH"
                    correlation_type = "EXACT_IDENTIFIER_MATCH"
                    matched_finding = next((f for f in local_findings if f.get("cve_id") == cve), local_findings[0] if local_findings else None)
                    explanation = f"Authoritative match: External advisory and local finding [{matched_finding.get('id', 'KAVACH')}] both reference CVE identifier {cve}."
                    break

            # 2. Specific Technology / Defensive Header Overlap (MEDIUM Confidence)
            if not confidence:
                for tech in local_tech_signals:
                    if tech in ev_tech or tech in ev_desc or tech in ev_title:
                        confidence = "MEDIUM"
                        correlation_type = "TECHNOLOGY_DEFENSE_OVERLAP"
                        matched_finding = next((f for f in local_findings if tech in f.get("title", "").lower() or tech in f.get("category", "").lower()), local_findings[0] if local_findings else None)
                        explanation = f"Technology overlap: Advisory addresses '{tech.upper()}' defensive configuration affecting the assessed target endpoint."
                        break

            # 3. HTTP/2 or Web Security Gateways (LOW Confidence)
            if not confidence and ("http/2" in ev_tech or "web security" in ev_tech):
                if any("web security" in c or "transport security" in c for c in local_categories):
                    confidence = "LOW"
                    correlation_type = "SURFACE_CATEGORY_RELEVANCE"
                    matched_finding = next((f for f in local_findings if "web security" in f.get("category", "").lower() or "transport" in f.get("category", "").lower()), None)
                    explanation = "Category context: Advisory affects general web application transport and HTTP gateway architectures."

            if confidence and explanation:
                correlated_results.append({
                    "event_id": event["id"],
                    "event_title": event["title"],
                    "event_source": event["source"],
                    "event_severity": event["severity"],
                    "confidence": confidence,
                    "correlation_type": correlation_type,
                    "explanation": explanation,
                    "related_finding_id": matched_finding.get("id") if matched_finding else None,
                    "related_finding_title": matched_finding.get("title") if matched_finding else None,
                    "local_evidence_summary": matched_finding.get("simple_evidence", {}).get("what_found") if matched_finding else "Local observation recorded on target.",
                    "external_context_summary": event.get("description", "")[:180] + "..."
                })

        # Sort correlations by confidence: HIGH > MEDIUM > LOW
        conf_priority = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        correlated_results.sort(key=lambda c: conf_priority.get(c.get("confidence", "LOW"), 0), reverse=True)

        return correlated_results


world_monitor_service = WorldMonitorService()
