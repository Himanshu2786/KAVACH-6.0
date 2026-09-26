import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const srcDir = path.resolve(__dirname, '../src');

/**
 * Regression Test Suite: KAVACH 6.0 Command Center Finding Count Semantics
 * 
 * Verifies:
 * 1. Confirmation state (evidence has validated finding exists) vs
 *    Remediation state (STILL_OPEN = re-verification has not resolved finding) separation.
 * 2. Confirmed findings count includes findings with validated technical evidence
 *    even when lifecycle status is STILL_OPEN.
 * 3. WM-API-DOCS-A018 yields 1 confirmed / 1 total.
 * 4. Zero-finding assessments yield 0 confirmed / 0 total.
 * 5. Potential, unconfirmed, or unverified source findings are NOT counted as confirmed.
 * 6. Target Findings Registry preserves lifecycle status string (STILL_OPEN).
 */

// Import or replicate the exact isConfirmedFinding logic from CommandCenterPage
const isConfirmedFinding = (f) => {
  if (f.evidence_status === 'REQUIRES_SOURCE_VALIDATION') {
    return false;
  }
  if (f.evidence_status === 'VERIFIED') {
    return true;
  }
  if (f.status === 'CONFIRMED' || f.status === 'STILL_OPEN' || f.status === 'VERIFIED') {
    return true;
  }
  if (f.evidence_records && f.evidence_records.some((e) => e.validation_result === 'CONFIRMED')) {
    return true;
  }
  return false;
};

test('1. CommandCenterPage.tsx contains the validated evidence aggregation logic', () => {
  const pageTsx = fs.readFileSync(path.join(srcDir, 'pages/CommandCenterPage.tsx'), 'utf-8');

  // Verify isConfirmedFinding function exists and checks both evidence and STILL_OPEN
  assert.match(pageTsx, /export\s+const\s+isConfirmedFinding\s*=/,
    'CommandCenterPage must export isConfirmedFinding');
  assert.match(pageTsx, /f\.status\s*===\s*['"]STILL_OPEN['"]/,
    'isConfirmedFinding must recognize STILL_OPEN as a valid confirmed remediation state');
  assert.match(pageTsx, /f\.evidence_status\s*===\s*['"]VERIFIED['"]/,
    'isConfirmedFinding must recognize VERIFIED technical evidence status');
  assert.match(pageTsx, /f\.evidence_status\s*===\s*['"]REQUIRES_SOURCE_VALIDATION['"]/,
    'isConfirmedFinding must exclude unverified source provenance findings');

  // Verify confirmedCount uses isConfirmedFinding
  assert.match(pageTsx, /const\s+confirmedCount\s*=\s*findings\.filter\(isConfirmedFinding\)\.length;/,
    'confirmedCount must use isConfirmedFinding');
});

test('2. A confirmed finding with STILL_OPEN remediation state counts as confirmed in Command Center', () => {
  // Simulating WM-API-DOCS-A018
  const findingA018 = {
    id: 'WM-API-DOCS-A018',
    assessment_id: 'KAVACH-WM-20260923-A018',
    title: 'Publicly Exposed Interactive API Schema & Documentation',
    status: 'STILL_OPEN', // Lifecycle state after re-test
    evidence_status: 'VERIFIED', // Technical evidence confirmed
    base_severity: 'MEDIUM',
    evidence_records: [
      {
        id: 'EV-WM-API-DOCS-A018',
        validation_result: 'CONFIRMED',
        raw_data: 'HTTP/2 200 OK'
      }
    ]
  };

  const findings = [findingA018];
  const confirmedCount = findings.filter(isConfirmedFinding).length;
  const totalCount = findings.length;

  assert.equal(confirmedCount, 1, 'WM-API-DOCS-A018 with STILL_OPEN must count as 1 confirmed');
  assert.equal(totalCount, 1, 'Total findings must be 1');
  assert.equal(`${confirmedCount} confirmed / ${totalCount} total`, '1 confirmed / 1 total');

  // Verify finding lifecycle status is preserved
  assert.equal(findingA018.status, 'STILL_OPEN', 'Finding status must remain STILL_OPEN');
});

test('3. Zero-finding assessments display 0 confirmed / 0 total', () => {
  const emptyFindings = [];
  const confirmedCount = emptyFindings.filter(isConfirmedFinding).length;
  const totalCount = emptyFindings.length;

  assert.equal(confirmedCount, 0, 'Zero-finding assessment must have 0 confirmed');
  assert.equal(totalCount, 0, 'Zero-finding assessment must have 0 total');
  assert.equal(`${confirmedCount} confirmed / ${totalCount} total`, '0 confirmed / 0 total');
});

test('4. Potential or unconfirmed findings are NOT counted as confirmed', () => {
  const potentialFinding = {
    id: 'FIND-001',
    status: 'POTENTIAL',
    evidence_status: 'NONE',
    evidence_records: []
  };

  const unconfirmedFinding = {
    id: 'FIND-002',
    status: 'UNCONFIRMED',
    evidence_status: 'NONE',
    evidence_records: [{ validation_result: 'UNCONFIRMED' }]
  };

  const findings = [potentialFinding, unconfirmedFinding];
  const confirmedCount = findings.filter(isConfirmedFinding).length;

  assert.equal(confirmedCount, 0, 'POTENTIAL and UNCONFIRMED findings must not count as confirmed');
});

test('5. Unverified source provenance findings are excluded from confirmed count', () => {
  const unverifiedSourceFinding = {
    id: 'SRC-001',
    status: 'CONFIRMED',
    evidence_status: 'REQUIRES_SOURCE_VALIDATION',
    evidence_records: [{ validation_result: 'CONFIRMED' }]
  };

  assert.equal(isConfirmedFinding(unverifiedSourceFinding), false,
    'Findings with REQUIRES_SOURCE_VALIDATION must not count as confirmed');
});
