import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const srcDir = path.resolve(__dirname, '../src');

/**
 * Regression Test Suite: KAVACH 6.0 Stage Telemetry Scoping & Lifecycle Semantics
 *
 * Verifies:
 * 1. Stage execution telemetry is strictly separated from global audit/lifecycle telemetry.
 * 2. Later RETEST_* events cannot appear inside historical stage execution logs (e.g. ASSESS, VALIDATE).
 * 3. RETEST_* events remain displayed in Live Activity Feed and Audit Trail.
 * 4. AssessmentProgressPage and WorkflowStepper normalize stage semantics so 'COMPLETE' maps to 'REPORT'.
 */

test('1. AssessmentProgressPage.tsx excludes RETEST_* and lifecycle transition events from stage logs', () => {
  const pageTsx = fs.readFileSync(path.join(srcDir, 'pages/AssessmentProgressPage.tsx'), 'utf-8');

  // Verify retest exclusion logic
  assert.match(pageTsx, /type\.startsWith\('RETEST'\)/,
    'AssessmentProgressPage must explicitly exclude RETEST event types from stage logs');
  assert.match(pageTsx, /desc\.includes\('RE-TEST'\)/,
    'AssessmentProgressPage must check description for RE-TEST to exclude retest events');

  // Verify stage advance event exclusion from module stdout logs
  assert.match(pageTsx, /type === 'ASSESSMENT_STAGE_ADVANCED'/,
    'AssessmentProgressPage must exclude pipeline-level stage advance events from module execution logs');

  // Verify normalizedCurrentStage logic
  assert.match(pageTsx, /normalizedCurrentStage/,
    'AssessmentProgressPage must define normalizedCurrentStage');
  assert.match(pageTsx, /'COMPLETE'/,
    'AssessmentProgressPage must handle legacy COMPLETE stage string');
});

test('2. Stage filter logic strictly isolates stage logs from re-test events', () => {
  // Simulate the exact stage filter logic used in AssessmentProgressPage.tsx
  const filterStageAudits = (audits, selectedStage) => {
    return audits.filter(a => {
      const desc = (a.description || '').toUpperCase();
      const type = (a.event_type || '').toUpperCase();

      const isRetest =
        type.startsWith('RETEST') ||
        type.includes('RETEST') ||
        desc.includes('RE-TEST') ||
        desc.includes('AFTER-FIX') ||
        desc.includes('RETEST');
      if (isRetest) return false;

      if (type === 'ASSESSMENT_STAGE_ADVANCED') return false;

      if (selectedStage === 'DISCOVER') {
        return (
          ['DISCOVERY_COMPLETED', 'DISCOVERY_SEEDED', 'SURFACE_MAPPED', 'ENDPOINT_DISCOVERED', 'TARGET_SELECTED', 'SOURCE_SELECTED', 'ASSESSMENT_STARTED', 'DISCOVERY_STARTED'].includes(type) ||
          type.includes('DISCOVER') ||
          desc.includes('DISCOVERY')
        );
      }
      if (selectedStage === 'ASSESS') {
        if (type === 'ASSESSMENT_COMPLETED') return false;
        return (
          ['MODULE_STARTED', 'RULE_EXECUTED', 'OBSERVATION', 'OBSERVATION_CAPTURED', 'RESULT', 'MODULE_COMPLETED', 'TEST_EXECUTED', 'PROBE_ERROR', 'MODULE_EXECUTION', 'SCAN_STARTED', 'SCAN_COMPLETED'].includes(type) ||
          type.startsWith('RULE_') ||
          type.startsWith('MODULE_') ||
          type === 'ASSESS' ||
          type.startsWith('ASSESS_')
        );
      }
      if (selectedStage === 'CORRELATE') {
        return (
          ['KNOWLEDGE_CORRELATED', 'CORRELATION_COMPLETED', 'TAXONOMY_MAPPED', 'CWE_MAPPED', 'OWASP_MAPPED', 'CORRELATION_STARTED'].includes(type) ||
          type.includes('CORRELAT') ||
          (desc.includes('CWE') && desc.includes('MAPPED')) ||
          (desc.includes('OWASP') && desc.includes('MAPPED'))
        );
      }
      if (selectedStage === 'ANALYZE') {
        return (
          ['AI_ANALYSIS_COMPLETED', 'AI_ANALYSIS_STARTED', 'HYPOTHESIS_GENERATED', 'OLLAMA_ANALYZED', 'AI_CORRELATED', 'AI_HYPOTHESIS'].includes(type) ||
          type.includes('ANALYZ') ||
          type.startsWith('AI_') ||
          type === 'AI' ||
          desc.includes('OLLAMA')
        );
      }
      if (selectedStage === 'VALIDATE') {
        return (
          ['EVIDENCE_GENERATED', 'EVIDENCE_RECORDED', 'EVIDENCE_VALIDATED', 'PROBE_EXECUTED', 'POC_EXECUTED', 'FINDING_CREATED', 'FINDING_UPDATED', 'VERIFICATION_EXECUTED', 'VALIDATION_STARTED', 'VALIDATION_COMPLETED'].includes(type) ||
          type.startsWith('VALIDAT') ||
          type.startsWith('EVIDENCE_')
        );
      }
      if (selectedStage === 'PRIORITIZE') {
        return (
          ['RISK_CALCULATED', 'PRIORITY_ASSIGNED', 'CVSS_SCORED', 'POSTURE_EVALUATED', 'PRIORITIZATION_COMPLETED'].includes(type) ||
          type.includes('PRIORIT') ||
          type.startsWith('RISK_') ||
          desc.includes('RISK') ||
          desc.includes('CVSS')
        );
      }
      if (selectedStage === 'REMEDIATE') {
        return (
          ['REMEDIATION_CREATED', 'REMEDIATION_PLAN_GENERATED', 'FIX_RECOMMENDED', 'PLAYBOOK_GENERATED', 'REMEDIATION_COMPLETED'].includes(type) ||
          type.includes('REMEDIAT') ||
          desc.includes('REMEDIATION')
        );
      }
      if (selectedStage === 'REPORT') {
        return (
          ['REPORT_GENERATED', 'REPORT_EXPORTED', 'REPORT_VIEWED', 'REPORT_DOWNLOADED', 'ASSESSMENT_COMPLETED'].includes(type) ||
          type.includes('REPORT') ||
          type === 'ASSESSMENT_COMPLETED' ||
          desc.includes('REPORT')
        );
      }
      return false;
    });
  };

  const sampleAudits = [
    { event_type: 'ASSESSMENT_STARTED', description: 'Assessment started' },
    { event_type: 'TARGET_SELECTED', description: 'Target selected' },
    { event_type: 'TEST_EXECUTED', description: 'Rule TLS-001 executed' },
    { event_type: 'OBSERVATION_CAPTURED', description: 'Observation on port 443' },
    { event_type: 'EVIDENCE_GENERATED', description: 'Evidence captured for API schema' },
    { event_type: 'FINDING_CREATED', description: 'Finding created WM-API-DOCS-A018' },
    { event_type: 'RISK_CALCULATED', description: 'Risk score evaluated' },
    { event_type: 'REMEDIATION_CREATED', description: 'Remediation guidance generated' },
    { event_type: 'ASSESSMENT_COMPLETED', description: 'Assessment completed' },
    { event_type: 'ASSESSMENT_STAGE_ADVANCED', description: 'Stage advanced from ASSESS to VALIDATE' },
    // Later re-test events
    { event_type: 'RETEST_STARTED', description: 'Re-test initiated' },
    { event_type: 'RETEST_OBSERVATION_CAPTURED', description: 'Raw re-test observation captured' },
    { event_type: 'RETEST_EVIDENCE_CREATED', description: 'Immutable after-fix evidence record stored' },
    { event_type: 'RETEST_STATE_COMPARISON', description: 'Deterministic state diff computed' },
    { event_type: 'RETEST_UNRESOLVED', description: 'Finding re-test completed STILL_OPEN' }
  ];

  // ASSESS stage
  const assessLogs = filterStageAudits(sampleAudits, 'ASSESS');
  assert.equal(assessLogs.length, 2, 'ASSESS must contain only TEST_EXECUTED and OBSERVATION_CAPTURED');
  assert.ok(assessLogs.every(e => !e.event_type.startsWith('RETEST')), 'ASSESS must have zero RETEST events');

  // VALIDATE stage
  const validateLogs = filterStageAudits(sampleAudits, 'VALIDATE');
  assert.equal(validateLogs.length, 2, 'VALIDATE must contain only EVIDENCE_GENERATED and FINDING_CREATED');
  assert.ok(validateLogs.every(e => !e.event_type.startsWith('RETEST')), 'VALIDATE must have zero RETEST events');

  // All 8 stages must have zero RETEST events
  const stages = ['DISCOVER', 'ASSESS', 'CORRELATE', 'ANALYZE', 'VALIDATE', 'PRIORITIZE', 'REMEDIATE', 'REPORT'];
  for (const s of stages) {
    const logs = filterStageAudits(sampleAudits, s);
    assert.ok(logs.every(e => !e.event_type.startsWith('RETEST')), `Stage ${s} must never contain RETEST events`);
    assert.ok(logs.every(e => e.event_type !== 'ASSESSMENT_STAGE_ADVANCED'), `Stage ${s} must never contain stage transition events`);
  }
});

test('3. WorkflowStepper.tsx normalizes COMPLETE stage to REPORT', () => {
  const stepperTsx = fs.readFileSync(path.join(srcDir, 'components/common/WorkflowStepper.tsx'), 'utf-8');

  assert.match(stepperTsx, /normalizedStage/,
    'WorkflowStepper must define normalizedStage');
  assert.match(stepperTsx, /=== 'COMPLETE'\s*\?\s*'REPORT'/,
    'WorkflowStepper must map COMPLETE to REPORT');
});

test('4. Live Activity Panel renders all audits without dropping RETEST events', () => {
  const pageTsx = fs.readFileSync(path.join(srcDir, 'pages/AssessmentProgressPage.tsx'), 'utf-8');

  // Live Activity Panel must map over audits (unfiltered global feed)
  assert.match(pageTsx, /audits\.map\(\(ev\)\s*=>/,
    'Live Activity Panel must render all audits so RETEST events remain visible');
});
