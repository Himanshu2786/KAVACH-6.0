export type AssessmentStatus = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED';
export type FindingStatus = 
  | 'POTENTIAL' 
  | 'UNDER ANALYSIS' 
  | 'VALIDATING' 
  | 'EVIDENCE AVAILABLE' 
  | 'CONFIRMED' 
  | 'UNCONFIRMED' 
  | 'REQUIRES MANUAL REVIEW'
  | 'STILL_OPEN'
  | 'VERIFIED'
  | 'VERIFIED_REMEDIATED'
  | 'RESOLVED';

export type SeverityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export interface AuthUser {
  id: string;
  username: string;
  role: 'admin' | 'team_member' | string;
  full_name?: string;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface UserAccount {
  user_id: string;
  role: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  first_login_at?: string;
  last_login_at?: string;
  last_active_at?: string;
  assessments_count?: number;
  sessions_count?: number;
  activities_count?: number;
}

export interface UserActivityRecord {
  id: string;
  user_id: string;
  session_id?: string;
  event_type: string;
  timestamp: string;
  assessment_id?: string;
  finding_id?: string;
  evidence_id?: string;
  module: string;
  details?: any;
  status: string;
}

export interface ActivitySummaryItem {
  user_id: string;
  role: string;
  full_name: string;
  is_active: boolean;
  usage_category: 'LOGIN ONLY' | 'ACTIVE USE' | 'MEANINGFUL USE' | 'NEVER LOGGED IN';
  total_events: number;
  meaningful_actions_count: number;
  last_login_at?: string;
  first_seen?: string;
  last_seen?: string;
}

export interface UserFeedbackRecord {
  id: string;
  user_id: string;
  assessment_id?: string;
  rating: number;
  what_worked: string;
  what_confusing: string;
  what_slow: string;
  bug_description: string;
  suggestions: string;
  created_at: string;
}

export interface Assessment {
  id: string;
  name: string;
  target_url: string;
  description: string;
  environment: string;
  scope: string;
  authorization_confirmed: boolean;
  modules_enabled: string[];
  status: AssessmentStatus;
  progress: number;
  current_stage: string;
  started_at: string;
  completed_at: string;
  is_demo: boolean;
  assessment_type?: string;
  parent_assessment_id?: string;
  total_findings?: number;
  confirmed_findings?: number;
}

export interface DiscoveryItem {
  id: string;
  assessment_id: string;
  item_type: 'endpoint' | 'component' | 'auth_point' | 'input_surface' | 'api_surface' | 'user_role';
  name: string;
  method: string;
  path: string;
  details: string;
  security_relevance: SeverityLevel;
}

export interface EvidenceRecord {
  id: string;
  finding_id: string;
  evidence_type: string;
  source: string;
  timestamp: string;
  description: string;
  raw_data: string;
  validation_result: 'CONFIRMED' | 'UNCONFIRMED' | 'INCONCLUSIVE' | 'MANUAL REVIEW REQUIRED';
  integrity_hash: string;
  is_demo: boolean;
  what_found?: string;
  why_matters?: string;
  where_found?: string;
  confidence_level?: 'HIGH' | 'MEDIUM' | 'LOW';
  verification_command?: string;
  expected_output?: string;
  observed_output?: string;
  evidence_nature?: 'REAL EVIDENCE' | 'TEST DATA' | 'DEMO DATA';
  http_method?: string;
  http_status?: number;
  content_type?: string;
  openapi_detected?: boolean;
  openapi_version?: string;
  schema_title?: string;
  unauthenticated?: boolean;
  authorization_state?: string;
  lifecycle_status?: 'CANONICAL' | 'HISTORICAL' | 'SUPERSEDED' | 'RETEST' | string;
  lifecycle_role?: string;
  is_canonical?: boolean;
  relationship_note?: string;
}

export interface TerminalVerification {
  assessment_id: string;
  evidence_id: string;
  target: string;
  timestamp: string;
  check_name: string;
  method: string;
  verification_steps: string[];
  command: string;
  expected_output: string;
  observed_output: string;
  status: string;
  integrity_hash: string;
  evidence_nature: string;
}

export interface ReVerificationRecord {
  id: string;
  finding_id: string;
  timestamp: string;
  previous_status: string;
  new_status: string;
  command_executed: string;
  output_before: string;
  output_after: string;
  summary: string;
  target_url?: string;
  before_evidence_id?: string;
  after_evidence_id?: string;
  before_evidence_hash?: string;
  after_evidence_hash?: string;
  state_diff?: string;
  verification_verdict?: string;
}

export interface Finding {
  id: string;
  assessment_id: string;
  title: string;
  description: string;
  category: string;
  affected_component: string;
  base_severity: SeverityLevel;
  priority: SeverityLevel;
  priority_score: number;
  priority_explanation?: string;
  status: FindingStatus;
  evidence_status: 'NONE' | 'PENDING' | 'AVAILABLE' | 'VERIFIED' | 'REQUIRES_SOURCE_VALIDATION' | string;
  ai_analysis_status: 'PENDING' | 'COMPLETED' | 'FAILED' | 'RULE_BASED_FALLBACK';
  ai_summary: string;
  ai_hypothesis: string;
  ai_confidence: number;
  ai_reasoning_summary: string;
  ai_potential_impact: string;
  recommended_validation: string[];
  recommended_remediation: string[];
  cwe_id: string;
  owasp_category: string;
  priority_scale?: string;
  priority_score_formatted?: string;
  cve_id?: string | null;
  cve_status?: string | null;
  nvd_cvss?: number | null;
  nvd_cvss_display?: string | null;
  nvd_reference?: string | null;
  created_at: string;
  updated_at: string;
  assigned_to?: string;
  team_notes?: string;
  triage_status?: 'NEW' | 'ASSIGNED' | 'IN_PROGRESS' | 'RESOLVED' | 'FALSE_POSITIVE';
  evidence_records?: EvidenceRecord[];
  ai_provider?: 'ollama' | 'fallback' | string;
}

export interface KnowledgeRecord {
  id: string;
  type: 'CWE' | 'OWASP';
  title: string;
  description: string;
  related_owasp: string;
  remediation: string[];
  category: string;
}

export interface RiskFactorDetail {
  level?: string;
  score: number;
  weight: string;
  rationale: string;
}

export interface RiskItem {
  finding_id: string;
  title: string;
  category: string;
  affected_component: string;
  base_severity: SeverityLevel;
  calculated_priority: SeverityLevel;
  priority_score: number;
  status: FindingStatus;
  evidence_strength: string;
  component_criticality: string;
  data_sensitivity: string;
  exposure: string;
  explanation: {
    base_severity: RiskFactorDetail;
    component_criticality: RiskFactorDetail;
    data_sensitivity: RiskFactorDetail;
    evidence_strength: RiskFactorDetail;
    exposure: RiskFactorDetail;
    summary_statement: string;
  };
}

export interface RemediationPlan {
  finding_id: string;
  title: string;
  category: string;
  affected_component: string;
  severity: SeverityLevel;
  priority: SeverityLevel;
  problem: string;
  impact: string;
  evidence_status: string;
  quick_fix: string;
  detailed_fix: string;
  prevention: string;
  verification: string;
  code_sample: string;
  cwe_id: string;
  owasp_category: string;
}

export interface SystemStatus {
  frontend_status: string;
  backend_status: string;
  ollama_status: 'ONLINE' | 'OFFLINE';
  ollama_model: string;
  ollama_base_url: string;
  ollama_models_available: string[];
  ollama_response_time_ms?: number;
  database_status: string;
  knowledge_engine: string;
  assessment_engine: string;
  validation_engine: string;
  active_assessment_count: number;
  total_findings_count: number;
}

export interface OllamaStatus {
  status: 'online' | 'offline';
  base_url: string;
  available_models: string[];
  selected_model: string;
  response_time_ms?: number;
  message?: string;
}

export interface AuditEvent {
  id: number;
  assessment_id?: string;
  finding_id?: string;
  event_type: string;
  description: string;
  timestamp: string;
  metadata_json: string;
}

export interface SecurityPosture {
  posture: string;
  risk_level: SeverityLevel;
  score: number;
  status_label: string;
  summary: string;
  total_findings?: number;
  confirmed_count?: number;
  potential_count?: number;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
}

export interface PortablePermission {
  id: string;
  name: string;
  granted: boolean;
  what_accessed: string;
  why_needed: string;
  checks_enabled: string;
  admin_required: boolean;
}

export interface PortableFinding {
  id: string;
  title: string;
  category: string;
  severity: SeverityLevel;
  status: string;
  evidence_status: string;
  affected_component: string;
  description: string;
  cwe_id: string;
  owasp_category: string;
  source: string;
  timestamp: string;
  evidence: {
    id: string;
    evidence_type: string;
    raw_observation: string;
    integrity_hash: string;
    confidence: string;
    evidence_nature: string;
  };
  terminal_verification: {
    command: string;
    expected_output: string;
    observed_output: string;
  };
  remediation: {
    how_to_fix: string;
    why_matters: string;
  };
}

export interface PortableScanResults {
  status: string;
  findings: PortableFinding[];
  module_summaries: Record<string, {
    status: string;
    summary: string;
    findings_count: number;
    scanned_count: number;
  }>;
  timestamp: string;
}

// Module 10: Audit Trail Event
export interface AuditEvent {
  id: number;
  assessment_id?: string;
  finding_id?: string;
  module: string;
  event_type: string;
  description: string;
  evidence_id?: string;
  status: string;
  timestamp: string;
  metadata_json: string;
}

// Module 8: Team Desk ("ASSIGN")
export interface TeamMember {
  id: string;
  name: string;
  role: string;
  initials: string;
}

export interface FindingAssignment {
  finding_id: string;
  assessment_id: string;
  title: string;
  category: string;
  severity: SeverityLevel;
  status: string;
  evidence_status: string;
  assigned_to: string;
  triage_status: 'NEW' | 'ASSIGNED' | 'IN_PROGRESS' | 'RESOLVED' | 'FALSE_POSITIVE';
  team_notes: string;
  cwe_id: string;
  owasp_category: string;
  updated_at: string;
}

// Module 7: Experience DB ("REMEMBER")
export interface ExperienceSummary {
  success: boolean;
  metrics: {
    total_assessments: number;
    total_findings_cataloged: number;
    confirmed_flaws: number;
    resolved_re_verifications: number;
    false_positives_prevented: number;
    under_analysis: number;
  };
  principle: string;
}

export interface FalsePositiveRecord {
  finding_id: string;
  title: string;
  category: string;
  component: string;
  status: string;
  triage_status: string;
  team_notes: string;
  why_disproved: string;
}

// Module 9: Test Center
export interface TestSuite {
  id: string;
  name: string;
  category: string;
  target_type: string;
  sample_file: string;
  description: string;
  expected_findings: Array<{
    key: string;
    expected: string;
    severity: SeverityLevel;
  }>;
  permission_required: string;
  limitations: string;
}

export interface TestRunResult {
  success: boolean;
  suite_id: string;
  suite_name: string;
  category: string;
  target_type: string;
  duration_ms: number;
  passed_checks: number;
  total_checks: number;
  overall_status: 'VERIFIED' | 'DISCREPANCY_NOTED';
  diff_report: Array<{
    key: string;
    expected_description: string;
    expected_severity: string;
    observed_description: string;
    status: 'PASSED' | 'DISCREPANCY';
    match: boolean;
  }>;
  evidence: {
    evidence_id: string;
    sha256_hash: string;
    raw_output: string[];
  };
  limitations: string;
  timestamp: string;
}

// Local AI Explanation Engine Types
export type AiLifecycleState = 'AI READY' | 'AI STARTING' | 'MODEL UNAVAILABLE' | 'AI OFFLINE';

export interface AiStatusResponse {
  success: boolean;
  lifecycle_state: AiLifecycleState;
  status_code: 'ready' | 'starting' | 'model_unavailable' | 'offline';
  status_dot: string;
  endpoint: string;
  selected_model: string;
  available_models: string[];
  has_configured_model: boolean;
  response_time_ms: number | null;
  ollama_binary: string | null;
  message: string;
}

export interface StructuredAiExplanation {
  what_was_found: string;
  where: string;
  why_it_matters: string;
  possible_impact: string;
  recommended_action: string;
  how_to_fix: string;
  how_to_verify: string;
  ai_mode?: string;
  model_used?: string;
  retrieval_mode?: string;
  embedding_model?: string;
  retrieved_sources?: RagRetrievedSource[];
  ai_provider?: 'ollama' | 'fallback' | string;
}

export interface RagRetrievedSource {
  chunk_id: string;
  document_id: string;
  title: string;
  category: string;
  cwe_id?: string | null;
  owasp_category?: string | null;
  source: string;
  text: string;
  score: number;
  chunk_type: string;
  metadata?: Record<string, any>;
}

export interface RagResponse {
  query: string;
  retrieval_mode: string;
  embedding_model: string;
  retrieved_sources: RagRetrievedSource[];
  context_tokens_approx: number;
  answer: StructuredAiExplanation;
  model_used: string;
  execution_time_ms: number;
  ai_provider?: 'ollama' | 'fallback' | string;
}

export interface RagIndexStatus {
  is_ready: boolean;
  retrieval_mode: string;
  embedding_provider: string;
  embedding_model: string;
  vector_store_type: string;
  indexed_documents_count: number;
  indexed_chunks_count: number;
  index_file_path?: string | null;
  last_indexed_at?: string | null;
  ollama_available: boolean;
  llm_model: string;
  message: string;
}

// URL Security Assessment Types
export interface UrlCheckItem {
  id: string;
  name: string;
  category: string;
  status: 'PASS' | 'WARNING' | 'FAIL' | 'NOT AVAILABLE' | 'ERROR' | 'TIMEOUT';
  execution_status?: 'SUCCESS' | 'TIMEOUT' | 'ERROR' | 'NOT_APPLICABLE';
  duration_ms?: number;
  error_reason?: string | null;
  observed: string;
  expected: string;
  importance: string;
}

export interface UrlFinding {
  id: string;
  run_id?: string;
  check_id?: string;
  title: string;
  category: string;
  severity: SeverityLevel;
  status: string;
  evidence_status: string;
  cwe_id: string;
  owasp_category: string;
  evidence: {
    id: string;
    run_id?: string;
    finding_id?: string;
    target?: string;
    detector?: string;
    raw_observation: string;
    integrity_hash: string;
    timestamp: string;
  };
  simple_evidence: {
    what_found: string;
    where_found: string;
    why_matters: string;
    possible_impact: string;
    what_you_can_do: string;
  };
  technical_evidence: {
    run_id?: string;
    target: string;
    protocol?: string;
    method?: string;
    observed: string;
    expected: string;
    scanner: string;
    rule: string;
    timestamp: string;
  };
  terminal_verification: {
    command: string;
    expected_output: string;
    observed_output: string;
  };
  remediation: {
    how_to_fix: string;
    why_matters: string;
  };
  reverification_status?: string;
}

export interface UrlAssessmentResult {
  success: boolean;
  run_id?: string;
  run_type?: string;
  assessment_type?: string;
  parent_assessment_id?: string;
  assessment_status?: 'COMPLETE' | 'PARTIAL' | 'FAILED' | 'READY';
  assessment_message?: string;
  target_url: string;
  hostname: string;
  timestamp: string;
  security_score: number;
  score_label: string;
  supported_checks: number;
  completed_checks: number;
  failed_checks?: number;
  findings_count: number;
  not_tested: number;
  limitations: string[];
  tls_info: {
    available: boolean;
    tls_version?: string;
    cipher?: string;
    subject?: string;
    issuer?: string;
    not_before?: string;
    not_after?: string;
    days_remaining?: number;
    duration_ms?: number;
    error?: string | null;
  };
  redirect_chain: Array<{
    url: string;
    status_code: number;
    location: string;
  }>;
  checks: UrlCheckItem[];
  findings: UrlFinding[];
  reverification?: {
    rechecked_at: string;
    previous_run_id?: string | null;
    current_run_id?: string;
    previous_findings_count: number;
    current_findings_count: number;
    resolved_count: number;
    resolved_findings?: Array<{
      id: string;
      title: string;
      reason: string;
    }>;
  };
}

// World Monitor Situational Awareness Types
export interface WorldEventLocation {
  has_coordinates: boolean;
  country: string;
  country_code: string;
  city: string;
  latitude: number | null;
  longitude: number | null;
}

export interface WorldEvent {
  id: string;
  source: string;
  source_name: string;
  source_url: string;
  title: string;
  description: string;
  category: string;
  severity: SeverityLevel;
  published_at: string;
  updated_at: string;
  fetched_at: string;
  location: WorldEventLocation;
  affected_technology: string;
  affected_organization: string;
  cve_ids: string[];
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  status: string;
  is_demo: boolean;
}

export interface WorldSourceStatus {
  id: string;
  name: string;
  status: string;
  events_count: number;
  type: string;
}

export interface WorldEventsResponse {
  success: boolean;
  mode: 'LIVE' | 'DEMO';
  last_updated: string;
  sources: WorldSourceStatus[];
  total_count: number;
  filtered_count: number;
  events: WorldEvent[];
  message?: string;
}

export interface WorldCorrelationItem {
  event_id: string;
  event_title: string;
  event_source: string;
  event_severity: SeverityLevel;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  correlation_type: string;
  explanation: string;
  related_finding_id?: string | null;
  related_finding_title?: string | null;
  local_evidence_summary?: string;
  external_context_summary?: string;
  distinction_note?: string;
  event?: WorldEvent;
  matched_finding_ids?: string[];
}
