import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.models import DiscoveryItem, Assessment
from backend.app.core.audit import log_audit_event

class DiscoveryService:
    def get_discovery_items(self, db: Session, assessment_id: str) -> List[DiscoveryItem]:
        return db.query(DiscoveryItem).filter(DiscoveryItem.assessment_id == assessment_id).all()

    def add_item(
        self,
        db: Session,
        assessment_id: str,
        item_type: str,
        name: str,
        method: str = "",
        path: str = "",
        details: str = "",
        security_relevance: str = "MEDIUM"
    ) -> DiscoveryItem:
        item = DiscoveryItem(
            id=f"DISC-{uuid.uuid4().hex[:8].upper()}",
            assessment_id=assessment_id,
            item_type=item_type,
            name=name,
            method=method,
            path=path,
            details=details,
            security_relevance=security_relevance
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def seed_demo_discovery(self, db: Session, assessment_id: str):
        """Seeds discovery inventory for World Monitor demo application."""
        items = [
            # Endpoints
            {"type": "endpoint", "name": "Authentication Gateway", "method": "POST", "path": "/api/v1/auth/login", "details": "JWT token issuer with refresh handshake", "relevance": "CRITICAL"},
            {"type": "endpoint", "name": "Workspace Tenant Retrieval", "method": "GET", "path": "/api/v1/workspaces/{id}", "details": "Direct object identifier resolution for enterprise projects", "relevance": "HIGH"},
            {"type": "endpoint", "name": "Threat Intel Search", "method": "POST", "path": "/api/v1/intel/search", "details": "Full-text query parser with dynamic SQL construction", "relevance": "HIGH"},
            {"type": "endpoint", "name": "User Profile Management", "method": "PUT", "path": "/api/v1/users/me", "details": "Self-service profile and credential updating endpoint", "relevance": "MEDIUM"},
            {"type": "endpoint", "name": "System Telemetry Health", "method": "GET", "path": "/api/v1/system/metrics", "details": "Internal cluster operational metrics export", "relevance": "LOW"},
            
            # Components
            {"type": "component", "name": "Nginx Edge Ingress", "method": "EDGE", "path": "/", "details": "Reverse proxy handling TLS termination and routing", "relevance": "HIGH"},
            {"type": "component", "name": "PostgreSQL Primary Cluster", "method": "TCP:5432", "path": "db.internal", "details": "Core database holding tenant accounts and telemetry logs", "relevance": "CRITICAL"},
            {"type": "component", "name": "Redis Session Cache", "method": "TCP:6379", "path": "cache.internal", "details": "In-memory token blacklist and rate-limiting store", "relevance": "MEDIUM"},
            
            # Authentication Points
            {"type": "auth_point", "name": "Bearer Token Verifier", "method": "AUTH", "path": "Authorization: Bearer <JWT>", "details": "Validates HS256/RS256 JWT claims across API endpoints", "relevance": "CRITICAL"},
            {"type": "auth_point", "name": "SSO SAML / OAuth Handler", "method": "POST", "path": "/api/v1/auth/sso/callback", "details": "Federated identity provider token exchange", "relevance": "HIGH"},

            # Input Surfaces
            {"type": "input_surface", "name": "Query Search String", "method": "BODY", "path": "/api/v1/intel/search:filter", "details": "Accepts user search queries; susceptible to SQL injection syntax", "relevance": "HIGH"},
            {"type": "input_surface", "name": "Workspace ID Parameter", "method": "URL", "path": "/api/v1/workspaces/{id}", "details": "URL path parameter susceptible to IDOR tampering", "relevance": "HIGH"},
            {"type": "input_surface", "name": "Avatar Upload", "method": "MULTIPART", "path": "/api/v1/users/avatar", "details": "Multipart image upload without magic bytes verification", "relevance": "MEDIUM"},

            # API Surfaces
            {"type": "api_surface", "name": "REST API v1 Gateway", "method": "HTTP", "path": "/api/v1/*", "details": "Primary REST operational surface exposed over HTTPS", "relevance": "HIGH"},
            {"type": "api_surface", "name": "WebSocket Realtime Stream", "method": "WSS", "path": "/ws/alerts", "details": "Realtime security alert broadcasting channel", "relevance": "MEDIUM"},

            # User Roles
            {"type": "user_role", "name": "System Administrator", "method": "RBAC", "path": "role:admin", "details": "Full control over all workspaces, billing, and system parameters", "relevance": "CRITICAL"},
            {"type": "user_role", "name": "Security Analyst", "method": "RBAC", "path": "role:analyst", "details": "Read/write access to alerts and validation evidence", "relevance": "HIGH"},
            {"type": "user_role", "name": "Auditor / Read-Only", "method": "RBAC", "path": "role:auditor", "details": "Inspect-only permissions across assessments and reports", "relevance": "LOW"}
        ]

        for it in items:
            self.add_item(
                db=db,
                assessment_id=assessment_id,
                item_type=it["type"],
                name=it["name"],
                method=it["method"],
                path=it["path"],
                details=it["details"],
                security_relevance=it["relevance"]
            )

        log_audit_event(
            db=db,
            event_type="DISCOVERY_COMPLETED",
            description=f"Discovery completed for assessment {assessment_id} with {len(items)} cataloged surfaces.",
            assessment_id=assessment_id
        )

discovery_service = DiscoveryService()
