"""
KAVACH 5.0 - Local Network Scanner
Collects: Local network interfaces, active local listening services, and port bindings.
Non-intrusive: Read-only inspection via psutil / socket. Does not send malicious packets.
"""

import hashlib
from datetime import datetime
from typing import List, Dict, Any
from backend.app.core.time import ist_isoformat, ist_formatted
import psutil

INSECURE_PORTS = {
    21: {"name": "FTP (Cleartext)", "severity": "MEDIUM", "cwe": "CWE-319", "owasp": "A02:2021 Cryptographic Failures"},
    23: {"name": "Telnet (Cleartext)", "severity": "HIGH", "cwe": "CWE-319", "owasp": "A02:2021 Cryptographic Failures"},
    80: {"name": "HTTP (Unencrypted Web)", "severity": "LOW", "cwe": "CWE-319", "owasp": "A02:2021 Cryptographic Failures"},
    445: {"name": "SMB Direct Host", "severity": "MEDIUM", "cwe": "CWE-284", "owasp": "A01:2021 Broken Access Control"},
    6379: {"name": "Redis Database Listener", "severity": "HIGH", "cwe": "CWE-306", "owasp": "A07:2021 Identification and Authentication Failures"},
    27017: {"name": "MongoDB Database Listener", "severity": "HIGH", "cwe": "CWE-306", "owasp": "A07:2021 Identification and Authentication Failures"}
}

EXPOSURE_PORTS = {
    8080: {"name": "HTTP Alternate / Dev Proxy", "severity": "LOW", "cwe": "CWE-200", "owasp": "A05:2021 Security Misconfiguration"},
    8000: {"name": "Application Development Listener", "severity": "LOW", "cwe": "CWE-200", "owasp": "A05:2021 Security Misconfiguration"},
    3000: {"name": "Node / Frontend Dev Server", "severity": "LOW", "cwe": "CWE-200", "owasp": "A05:2021 Security Misconfiguration"},
    5000: {"name": "Flask / Python Dev Server", "severity": "LOW", "cwe": "CWE-200", "owasp": "A05:2021 Security Misconfiguration"},
    8888: {"name": "Jupyter / HTTP Gateway", "severity": "LOW", "cwe": "CWE-200", "owasp": "A05:2021 Security Misconfiguration"}
}

class NetworkScanner:
    def __init__(self):
        pass

    def scan_network(self) -> Dict[str, Any]:
        listeners: List[Dict[str, Any]] = []
        findings: List[Dict[str, Any]] = []
        interfaces: List[Dict[str, Any]] = []

        # 1. Collect interfaces
        try:
            net_if_addrs = psutil.net_if_addrs()
            for iface_name, addrs in net_if_addrs.items():
                ip_list = [a.address for a in addrs if a.family.name in ('AF_INET', 'AF_INET6')]
                interfaces.append({
                    "interface": iface_name,
                    "addresses": ip_list
                })
        except Exception:
            pass

        # 2. Collect listening sockets
        try:
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.status == 'LISTEN':
                    laddr = conn.laddr
                    port = laddr.port if laddr else 0
                    ip = laddr.ip if laddr else ""
                    pid = conn.pid

                    proc_name = "Unknown"
                    if pid:
                        try:
                            proc = psutil.Process(pid)
                            proc_name = proc.name()
                        except Exception:
                            pass

                    entry = {
                        "ip": ip,
                        "port": port,
                        "pid": pid,
                        "process_name": proc_name
                    }
                    listeners.append(entry)

                    # Check: Insecure service bound to all interfaces (0.0.0.0 or ::)
                    is_wildcard = ip in ('0.0.0.0', '::', '')
                    if port in INSECURE_PORTS and is_wildcard:
                        pinfo = INSECURE_PORTS[port]
                        finding_id = f"KAV-NET-{len(findings) + 1:03d}"
                        evidence_id = f"EVD-NET-{len(findings) + 1:03d}"
                        raw_obs = (
                            f"Listening Port: {port} ({pinfo['name']})\n"
                            f"Binding Address: {ip} (Wildcard - Accessible from all network adapters)\n"
                            f"Process: {proc_name} (PID: {pid})"
                        )
                        ev_hash = hashlib.sha256(raw_obs.encode()).hexdigest()

                        findings.append({
                            "id": finding_id,
                            "title": f"Insecure Service Bound to Wildcard Interface: {pinfo['name']} (Port {port})",
                            "category": "Secure Communication & Transport",
                            "severity": pinfo["severity"],
                            "status": "CONFIRMED",
                            "evidence_status": "VERIFIED",
                            "affected_component": f"{ip}:{port} ({proc_name})",
                            "description": f"Service '{proc_name}' is listening on port {port} ({pinfo['name']}) bound to '{ip}'. Wildcard binding exposes this local listener to the entire local network segment.",
                            "cwe_id": pinfo["cwe"],
                            "owasp_category": pinfo["owasp"],
                            "source": "KAVACH Network Scanner",
                            "timestamp": ist_formatted("%Y-%m-%d %H:%M:%S IST"),
                            "evidence": {
                                "id": evidence_id,
                                "evidence_type": "TCP Socket State Table Record",
                                "raw_observation": raw_obs,
                                "integrity_hash": ev_hash,
                                "confidence": "HIGH",
                                "evidence_nature": "REAL EVIDENCE"
                            },
                            "terminal_verification": {
                                "command": f"Get-NetTCPConnection -State Listen -LocalPort {port} | Select-Object LocalAddress, LocalPort, OwningProcess",
                                "expected_output": f"# Expected: Service bound to 127.0.0.1 or encrypted\nLocalAddress: 127.0.0.1\nLocalPort: {port}",
                                "observed_output": f"LocalAddress: {ip}\nLocalPort: {port}\nOwningProcess: {pid}"
                            },
                            "remediation": {
                                "how_to_fix": f"Reconfigure '{proc_name}' to bind explicitly to loopback ('127.0.0.1') instead of wildcard '0.0.0.0', or enable TLS transport encryption.",
                                "why_matters": "Cleartext or unauthenticated services bound to 0.0.0.0 allow any host on the same Wi-Fi or local network to intercept traffic or interact with administrative interfaces."
                            }
                        })

                    # Check: Service Exposure Assessment (Detection 2: Port listening does not automatically mean vulnerable)
                    elif port in EXPOSURE_PORTS:
                        ep = EXPOSURE_PORTS[port]
                        finding_id = f"KAV-NET-{len(findings) + 1:03d}"
                        evidence_id = f"EVD-NET-{len(findings) + 1:03d}"
                        raw_obs = (
                            f"Protocol: TCP\n"
                            f"Local Address: {ip}\n"
                            f"Port: {port}\n"
                            f"Connection State: LISTEN\n"
                            f"Process: {proc_name} (PID: {pid})\n"
                            f"Listening Status: Active\n"
                            f"Service Information: {ep['name']}\n"
                            f"Assessment: Service Exposure Detected (Non-Vulnerability Calibration: Needs Review)"
                        )
                        ev_hash = hashlib.sha256(raw_obs.encode()).hexdigest()
                        now_str = ist_formatted("%Y-%m-%d %H:%M:%S IST")

                        findings.append({
                            "id": finding_id,
                            "title": f"Service Exposure Detected: {ep['name']} (Port {port})",
                            "category": "Network & Sockets",
                            "severity": ep["severity"],
                            "status": "NEEDS REVIEW",
                            "evidence_status": "VERIFIED",
                            "affected_component": f"{ip}:{port} ({proc_name})",
                            "description": (
                                f"Service '{proc_name}' (PID: {pid}) is listening on TCP port {port} bound to {ip}. "
                                f"Service Exposure Detected: A listening port does not automatically indicate an exploitable vulnerability, "
                                f"but increases the reachable host attack surface and requires review."
                            ),
                            "cwe_id": ep["cwe"],
                            "owasp_category": ep["owasp"],
                            "source": "KAVACH Network Exposure Scanner",
                            "timestamp": now_str,
                            "evidence": {
                                "id": evidence_id,
                                "evidence_type": "TCP Socket State Table Record",
                                "raw_observation": raw_obs,
                                "integrity_hash": ev_hash,
                                "confidence": "HIGH",
                                "evidence_nature": "REAL EVIDENCE"
                            },
                            "simple_evidence": {
                                "what_found": f"A listening network service was detected on port {port} associated with process '{proc_name}'.",
                                "where_found": f"{ip}:{port} (PID: {pid})",
                                "why_matters": "A listening port does not automatically mean a vulnerability exists. It indicates an active service waiting for inbound connections.",
                                "possible_impact": "Exposure to network reconnaissance, unauthorized API interaction, or software vulnerability exploitation if the service lacks authentication.",
                                "what_you_can_do": "Verify whether this service is intended to accept network traffic. Bind to 127.0.0.1 or terminate if unused."
                            },
                            "technical_evidence": {
                                "protocol": "TCP",
                                "local_address": ip,
                                "port": port,
                                "connection_state": "LISTEN",
                                "process_name": proc_name,
                                "pid": pid,
                                "listening_status": "ACTIVE",
                                "scanner": "KAVACH Network Scanner",
                                "rule": "NET-SERVICE-EXPOSURE-CALIBRATED",
                                "timestamp": now_str
                            },
                            "terminal_verification": {
                                "command": f"Get-NetTCPConnection -State Listen -LocalPort {port} | Select-Object LocalAddress, LocalPort, OwningProcess",
                                "expected_output": f"# Observation check\nLocalAddress: 127.0.0.1\nLocalPort: {port}",
                                "observed_output": f"LocalAddress: {ip}\nLocalPort: {port}\nOwningProcess: {pid}"
                            },
                            "remediation": {
                                "how_to_fix": f"Review whether '{proc_name}' must be reachable externally. If not required, bind exclusively to loopback ('127.0.0.1') or shut down the service.",
                                "why_matters": "Reducing unnecessary listening services minimizes the host's exposed attack surface."
                            }
                        })

        except Exception:
            pass

        summary = (
            f"Audited {len(interfaces)} interface(s) and {len(listeners)} active listening socket(s). "
            f"Identified {len(findings)} noteworthy network binding observation(s)."
            if findings else
            f"Audited {len(interfaces)} interface(s) and {len(listeners)} listening socket(s). No issues detected by supported checks."
        )

        return {
            "status": "COMPLETED",
            "scanned_count": len(listeners),
            "findings": findings,
            "interfaces": interfaces,
            "listeners_sample": listeners[:25],
            "summary": summary,
            "timestamp": ist_isoformat()
        }

network_scanner = NetworkScanner()
