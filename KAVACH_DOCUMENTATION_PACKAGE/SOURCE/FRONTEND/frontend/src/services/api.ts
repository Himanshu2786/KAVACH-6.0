import {
  Assessment,
  DiscoveryItem,
  Finding,
  EvidenceRecord,
  KnowledgeRecord,
  RiskItem,
  RemediationPlan,
  SystemStatus,
  OllamaStatus,
  AuditEvent,
  SecurityPosture,
  TerminalVerification,
  ReVerificationRecord,
  PortablePermission,
  PortableScanResults,
  AiStatusResponse,
  StructuredAiExplanation,
  UrlAssessmentResult,
  WorldEventsResponse,
  WorldCorrelationItem,
  WorldSourceStatus,
  RagIndexStatus,
  RagResponse,
  RagRetrievedSource,
  AuthUser,
  LoginResponse,
  UserAccount,
  UserActivityRecord,
  ActivitySummaryItem,
  UserFeedbackRecord
} from '../types';

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) || '/api';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const token = typeof window !== 'undefined' ? localStorage.getItem('kavach_token') : null;
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (res.status === 401 && !endpoint.startsWith('/auth/login')) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('kavach_token');
        localStorage.removeItem('kavach_user');
        window.dispatchEvent(new Event('kavach_unauthorized'));
      }
    }
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      const msg = errBody.detail || errBody.error?.message || `HTTP ${res.status} Error`;
      throw new Error(msg);
    }
    return await res.json();
  } catch (err: any) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export function isWorldMonitorTarget(url: string | null | undefined): boolean {
  if (!url) return false;
  let clean = url.trim();
  if (!clean.startsWith('http://') && !clean.startsWith('https://')) {
    clean = 'https://' + clean;
  }
  try {
    const parsed = new URL(clean);
    const host = parsed.hostname.toLowerCase();
    return host === 'worldmonitor.app' || host === 'www.worldmonitor.app';
  } catch {
    return false;
  }
}

export const api = {
  // System & Health
  getHealth: () => request<{ status: string; platform: string; tagline: string; version: string; demo_mode: boolean }>('/health'),
  getSystemStatus: () => request<SystemStatus>('/system/status'),
  getOllamaStatus: () => request<OllamaStatus>('/system/ollama'),
  getNetworkGeolocation: () => request<{
    success: boolean;
    location_type: string;
    latitude: number | null;
    longitude: number | null;
    country_name?: string;
    city?: string;
  }>('/system/geolocate'),
  selectOllamaModel: (model_name: string) => request<{ success: boolean; selected_model: string }>('/system/ollama/select-model', {
    method: 'POST',
    body: JSON.stringify({ model_name })
  }),
  setOllamaTimeout: (timeout_sec: number) => request<{ success: boolean; timeout_seconds: number }>('/system/ollama/timeout', {
    method: 'POST',
    body: JSON.stringify({ timeout_sec })
  }),
  getAuditTrail: (paramsOrId?: string | { assessment_id?: string; module?: string; event_type?: string; status?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (typeof paramsOrId === 'string') {
      if (paramsOrId) q.append('assessment_id', paramsOrId);
    } else if (paramsOrId) {
      if (paramsOrId.assessment_id) q.append('assessment_id', paramsOrId.assessment_id);
      if (paramsOrId.module) q.append('module', paramsOrId.module);
      if (paramsOrId.event_type) q.append('event_type', paramsOrId.event_type);
      if (paramsOrId.status) q.append('status', paramsOrId.status);
      if (paramsOrId.limit) q.append('limit', paramsOrId.limit.toString());
    }
    const qs = q.toString() ? `?${q.toString()}` : '';
    return request<AuditEvent[]>(`/system/audit${qs}`);
  },

  // Assessments
  getAssessments: () => request<Assessment[]>('/assessments'),
  getAssessment: (id: string) => request<Assessment>(`/assessments/${id}`),
  createAssessment: (data: Partial<Assessment>) => request<Assessment>('/assessments', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  advanceStage: (assessmentId: string, stage: string) => request<Assessment>(`/assessments/${assessmentId}/advance-stage`, {
    method: 'POST',
    body: JSON.stringify({ stage })
  }),
  getSecurityPosture: (assessmentId: string) => request<SecurityPosture>(`/assessments/${assessmentId}/posture`),

  // Discovery
  getDiscoveryItems: (assessmentId: string) => request<DiscoveryItem[]>(`/discovery/${assessmentId}`),
  addDiscoveryItem: (assessmentId: string, item: Partial<DiscoveryItem>) => request<DiscoveryItem>(`/discovery/${assessmentId}`, {
    method: 'POST',
    body: JSON.stringify(item)
  }),

  // Findings
  getFindings: (params?: { assessment_id?: string; category?: string; severity?: string; status?: string; is_demo?: boolean }) => {
    const q = new URLSearchParams();
    if (params?.assessment_id) q.set('assessment_id', params.assessment_id);
    if (params?.category) q.set('category', params.category);
    if (params?.severity) q.set('severity', params.severity);
    if (params?.status) q.set('status', params.status);
    if (params?.is_demo !== undefined) q.set('is_demo', String(params.is_demo));
    const qs = q.toString() ? `?${q.toString()}` : '';
    return request<Finding[]>(`/findings${qs}`);
  },
  getFinding: (id: string) => request<Finding>(`/findings/${id}`),
  analyzeFinding: (id: string) => request<{ success: boolean; data: any; updated_finding: Finding }>(`/findings/${id}/analyze`, {
    method: 'POST'
  }),

  // Knowledge
  getKnowledge: (type?: string) => {
    const q = type ? `?type=${encodeURIComponent(type)}` : '';
    return request<KnowledgeRecord[]>(`/knowledge${q}`);
  },
  getKnowledgeItem: (id: string) => request<KnowledgeRecord>(`/knowledge/${id}`),
  correlateKnowledge: (category: string, title?: string) => {
    const q = new URLSearchParams({ category, title: title || '' });
    return request<{ cwe: KnowledgeRecord | null; owasp: KnowledgeRecord | null }>(`/knowledge/correlate?${q.toString()}`);
  },

  // Evidence & Safe Probes
  getEvidence: (paramsOrFindingId?: string | { finding_id?: string; assessment_id?: string; is_demo?: boolean }) => {
    const q = new URLSearchParams();
    if (typeof paramsOrFindingId === 'string') {
      if (paramsOrFindingId) q.set('finding_id', paramsOrFindingId);
    } else if (paramsOrFindingId) {
      if (paramsOrFindingId.finding_id) q.set('finding_id', paramsOrFindingId.finding_id);
      if (paramsOrFindingId.assessment_id) q.set('assessment_id', paramsOrFindingId.assessment_id);
      if (paramsOrFindingId.is_demo !== undefined) q.set('is_demo', String(paramsOrFindingId.is_demo));
    }
    const qs = q.toString() ? `?${q.toString()}` : '';
    return request<EvidenceRecord[]>(`/evidence${qs}`);
  },
  recordEvidence: (data: Partial<EvidenceRecord>) => request<EvidenceRecord>('/evidence', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  executeProbe: (findingId: string, probeType = 'HTTP_PROBE', isDemo = true) => request<EvidenceRecord>('/evidence/probe', {
    method: 'POST',
    body: JSON.stringify({ finding_id: findingId, probe_type: probeType, is_demo: isDemo })
  }),
  getTerminalVerification: (findingId: string) => request<TerminalVerification>(`/evidence/${findingId}/terminal`),
  reVerifyFinding: (findingId: string, payload?: { command_executed?: string; output_after?: string; force_status?: string }) => request<ReVerificationRecord>(`/evidence/${findingId}/re-verify`, {
    method: 'POST',
    body: JSON.stringify(payload || {})
  }),

  // Risk Prioritization
  getRiskPrioritization: (assessmentId: string) => request<RiskItem[]>(`/risk/prioritization/${assessmentId}`),

  // Remediation
  getRemediation: (findingId: string) => request<RemediationPlan>(`/remediation/${findingId}`),

  // Reports
  getReportData: (assessmentId: string) => request<any>(`/reports/${assessmentId}`),
  getReportHtmlUrl: (assessmentId: string) => `${API_BASE}/reports/${assessmentId}/html`,

  // Portable Windows Assessment
  getPortablePermissions: () => request<{ success: boolean; permissions: PortablePermission[] }>('/portable/permissions'),
  updatePortablePermissions: (permissions: Record<string, boolean>) => request<{ success: boolean; permissions: PortablePermission[] }>('/portable/permissions', {
    method: 'POST',
    body: JSON.stringify({ permissions })
  }),
  executePortableScan: (target_folder?: string) => request<{ success: boolean; results: PortableScanResults }>('/portable/scan', {
    method: 'POST',
    body: JSON.stringify({ target_folder })
  }),
  getPortableResults: () => request<{ success: boolean; results: PortableScanResults }>('/portable/results'),
  getDemoSamples: () => request<{ success: boolean; sample_dir: string; samples: any[] }>('/portable/demo-samples'),

  // Team Desk ("ASSIGN")
  getTeamMembers: () => request<{ success: boolean; team_members: any[] }>('/team/members'),
  getTeamAssignments: () => request<{ success: boolean; count: number; assignments: any[] }>('/team/assignments'),
  assignFinding: (data: { finding_id: string; assigned_to: string; triage_status?: string; notes?: string }) => request<any>('/team/assign', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  addTeamNote: (data: { finding_id: string; notes: string }) => request<any>('/team/notes', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Experience DB ("REMEMBER")
  getExperienceSummary: () => request<any>('/experience/summary'),
  getReverificationHistory: () => request<{ success: boolean; count: number; re_verifications: any[] }>('/experience/re-verifications'),
  getFalsePositivesLibrary: () => request<{ success: boolean; count: number; false_positives: any[] }>('/experience/false-positives'),
  markFalsePositive: (data: { finding_id: string; rationale: string }) => request<any>('/experience/mark-false-positive', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Test Center
  getTestSuites: () => request<{ success: boolean; count: number; suites: any[]; environment: string; guarantee: string }>('/test-center/suites'),
  runControlledTest: (data: { suite_id: string; assessment_id?: string }) => request<any>('/test-center/run', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Local AI Explanation Engine (Ollama Integration)
  getAiStatus: () => request<AiStatusResponse>('/ai/status'),
  startAiService: () => request<{ success: boolean; status?: string; binary_path?: string; message: string }>('/ai/start', {
    method: 'POST'
  }),
  explainFinding: (findingId: string) => request<{ success: boolean; finding_id: string; explanation: StructuredAiExplanation }>('/ai/explain-finding', {
    method: 'POST',
    body: JSON.stringify({ finding_id: findingId })
  }),
  explainRisk: (findingId: string) => request<{ success: boolean; risk_explanation: any }>('/ai/explain-risk', {
    method: 'POST',
    body: JSON.stringify({ finding_id: findingId })
  }),
  getRemediationGuide: (findingId: string) => request<{ success: boolean; remediation_guide: any }>('/ai/remediation-guide', {
    method: 'POST',
    body: JSON.stringify({ finding_id: findingId })
  }),
  getAssessmentSummary: (assessmentId: string) => request<{ success: boolean; assessment_id: string; summary: StructuredAiExplanation }>('/ai/assessment-summary', {
    method: 'POST',
    body: JSON.stringify({ assessment_id: assessmentId })
  }),
  getAuditSummary: (assessmentId?: string) => request<{ success: boolean; audit_summary: any }>('/ai/audit-summary', {
    method: 'POST',
    body: JSON.stringify({ assessment_id: assessmentId })
  }),
  explainThreatAlert: (alertText: string, component = 'Application Gateway', severity = 'HIGH') => request<{ success: boolean; alert_explanation: StructuredAiExplanation }>('/ai/threat-alert', {
    method: 'POST',
    body: JSON.stringify({ alert_text: alertText, component, severity })
  }),

  // Security Intelligence RAG Pipeline
  getRagStatus: () => request<RagIndexStatus>('/rag/status'),
  rebuildRagIndex: () => request<{ success: boolean; message: string; stats: any }>('/rag/index', {
    method: 'POST'
  }),
  queryRag: (query: string, top_k = 4, filter_category?: string) => request<RagResponse>('/rag/query', {
    method: 'POST',
    body: JSON.stringify({ query, top_k, filter_category })
  }),
  analyzeFindingRag: (findingId: string, top_k = 4) => request<RagResponse>(`/rag/analyze-finding?finding_id=${encodeURIComponent(findingId)}&top_k=${top_k}`, {
    method: 'POST'
  }),

  // URL Security Assessment (Detection 1: Web Security)
  scanUrl: (url: string, parentAssessmentId?: string) => request<UrlAssessmentResult>('/url-check/scan', {
    method: 'POST',
    body: JSON.stringify({ url, parent_assessment_id: parentAssessmentId })
  }),
  getLatestUrlAssessment: () => request<UrlAssessmentResult>('/url-check/latest'),
  reverifyUrl: (url: string) => request<UrlAssessmentResult>('/url-check/re-verify', {
    method: 'POST',
    body: JSON.stringify({ url })
  }),

  // World Monitor (Situational Awareness & External Threat Intelligence)
  getWorldEvents: (params?: { category?: string; severity?: string; time_range?: string; source?: string; search?: string; mode?: string }) => {
    const q = new URLSearchParams();
    if (params?.category) q.set('category', params.category);
    if (params?.severity) q.set('severity', params.severity);
    if (params?.time_range) q.set('time_range', params.time_range);
    if (params?.source) q.set('source', params.source);
    if (params?.search) q.set('search', params.search);
    if (params?.mode) q.set('mode', params.mode);
    const qs = q.toString() ? `?${q.toString()}` : '';
    return request<WorldEventsResponse>(`/world-monitor/events${qs}`);
  },
  refreshWorldEvents: (mode?: 'live' | 'demo') => request<WorldEventsResponse>('/world-monitor/refresh', {
    method: 'POST',
    body: JSON.stringify({ mode })
  }),
  correlateWorldEvents: (data: { target_url?: string; hostname?: string; findings?: any[]; mode?: string }) => request<{ success: boolean; count: number; correlations: WorldCorrelationItem[] }>('/world-monitor/correlate', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  getWorldSources: () => request<{ success: boolean; last_updated: string; mode: string; sources: WorldSourceStatus[] }>('/world-monitor/sources'),
  getWorldMonitorTarget: () => request<{ success: boolean; target: any }>('/world-monitor/target'),
  runWorldMonitorAssessment: (data: { target_url?: string; source_path?: string; mode?: string; assessment_name?: string }) => request<any>('/assessments/world-monitor', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  getLatestWorldMonitorAssessment: () => request<any>('/assessments/world-monitor/latest'),

  // Authentication & Team Multi-User Management
  login: (username: string, password: string) => request<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  }),
  getMe: async (): Promise<AuthUser> => {
    const res = await request<any>('/auth/me');
    return (res?.user || res) as AuthUser;
  },
  logout: () => request<{ success: boolean; message: string }>('/auth/logout', {
    method: 'POST'
  }),
  getTeamUsers: () => request<AuthUser[]>('/auth/users'),

  // Activity Logging & Feedback
  logActivity: (data: {
    event_type: string;
    module?: string;
    assessment_id?: string;
    finding_id?: string;
    evidence_id?: string;
    status?: string;
    details?: any;
  }) => request<{ success: boolean; event_id: string }>('/activity/log', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  submitFeedback: (data: {
    rating: number;
    assessment_id?: string;
    what_worked?: string;
    what_confusing?: string;
    what_slow?: string;
    bug_description?: string;
    suggestions?: string;
  }) => request<{ success: boolean; feedback_id: string; message: string }>('/feedback/submit', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Sovereign Administrator Portal APIs
  adminGetUsers: () => request<{ success: boolean; count: number; users: UserAccount[] }>('/admin/users'),
  adminCreateUser: (data: { user_id: string; password: string; role?: string; full_name?: string }) =>
    request<{ success: boolean; message: string; user: UserAccount }>('/admin/users', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  adminSetUserStatus: (userId: string, is_active: boolean) =>
    request<{ success: boolean; message: string; user_id: string; is_active: boolean }>(`/admin/users/${userId}/status`, {
      method: 'POST',
      body: JSON.stringify({ is_active })
    }),
  adminResetPassword: (userId: string, new_password: string) =>
    request<{ success: boolean; message: string }>(`/admin/users/${userId}/reset-password`, {
      method: 'POST',
      body: JSON.stringify({ new_password })
    }),
  adminGetActivity: (params?: { limit?: number; user_id?: string; module?: string; event_type?: string }) => {
    const q = new URLSearchParams();
    if (params?.limit) q.set('limit', String(params.limit));
    if (params?.user_id) q.set('user_id', params.user_id);
    if (params?.module) q.set('module', params.module);
    if (params?.event_type) q.set('event_type', params.event_type);
    const qs = q.toString() ? `?${q.toString()}` : '';
    return request<{ success: boolean; count: number; activities: UserActivityRecord[] }>(`/admin/activity${qs}`);
  },
  adminGetActivitySummary: () =>
    request<{ success: boolean; total_users: number; summary: ActivitySummaryItem[] }>('/admin/activity/summary'),
  adminGetFeedback: () =>
    request<{ success: boolean; count: number; feedbacks: UserFeedbackRecord[] }>('/admin/feedback')
};


