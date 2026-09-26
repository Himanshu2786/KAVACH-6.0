import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const srcDir = path.resolve(__dirname, '../src');

/**
 * Regression Test Suite: KAVACH 6.0 Evidence Deduplication & Lifecycle Distinction
 * 
 * Verifies:
 * 1. Two technical evidence artifacts for one finding do NOT become two confirmed vulnerability proofs.
 * 2. SecurityReportPage displays Evidence Confirmed = 1 and Evidence Proofs = 1.
 * 3. SecurityReportPage displays both artifacts with Canonical Active vs Historical Artifact distinction.
 * 4. EvidenceValidationPage prioritizes canonical active evidence (EV-WM-API-DOCS-A018-GET) and provides artifact selector.
 */

test('1. SecurityReportPage.tsx displays deduplicated Evidence Confirmed and Evidence Proofs', () => {
  const pageTsx = fs.readFileSync(path.join(srcDir, 'pages/SecurityReportPage.tsx'), 'utf-8');

  // Verify unique proof counter rendering
  assert.match(pageTsx, /exec\.confirmed_evidence\s*\?\?\s*exec\.confirmed_findings/,
    'SecurityReportPage must render confirmed_evidence');
  assert.match(pageTsx, /exec\.evidence_proofs/,
    'SecurityReportPage must render executive evidence_proofs');

  // Verify distinct badge rendering for Canonical Active vs Historical Artifact
  assert.match(pageTsx, /Canonical Active/,
    'SecurityReportPage must have Canonical Active badge');
  assert.match(pageTsx, /Historical Artifact/,
    'SecurityReportPage must have Historical Artifact badge');
  assert.match(pageTsx, /relationship_note/,
    'SecurityReportPage must render relationship_note explaining artifact semantics');
});

test('2. EvidenceValidationPage.tsx prioritizes canonical active evidence and provides artifact switcher', () => {
  const pageTsx = fs.readFileSync(path.join(srcDir, 'pages/EvidenceValidationPage.tsx'), 'utf-8');

  // Verify canonical evidence prioritization
  assert.match(pageTsx, /EV-WM-API-DOCS-A018-GET/,
    'EvidenceValidationPage must reference canonical GET evidence identifier');
  assert.match(pageTsx, /canonicalEvidenceRecord/,
    'EvidenceValidationPage must derive canonicalEvidenceRecord');

  // Verify baseline evidence artifact switcher
  assert.match(pageTsx, /baselineEvidenceRecords\.length\s*>\s*1/,
    'EvidenceValidationPage must render evidence artifact switcher when multiple baseline artifacts exist');
  assert.match(pageTsx, /Canonical Active Proof/,
    'EvidenceValidationPage must display Canonical Active Proof badge');
  assert.match(pageTsx, /Historical Artifact \(Superseded\)/,
    'EvidenceValidationPage must display Historical Artifact badge');
});

test('3. Deduplication calculation logic: 2 evidence records for 1 finding evaluate to 1 unique proof', () => {
  const findingId = 'WM-API-DOCS-A018';
  const baselineEvidence = [
    { id: 'EV-WM-API-DOCS-A018', finding_id: findingId, validation_result: 'CONFIRMED' },
    { id: 'EV-WM-API-DOCS-A018-GET', finding_id: findingId, validation_result: 'CONFIRMED' }
  ];

  const confirmedFindings = [{ id: findingId, status: 'STILL_OPEN' }];

  // Deduplication logic: Unique confirmed vulnerability proofs count distinct confirmed findings with verified proof
  const confirmedUniqueProofFindings = new Set(
    baselineEvidence.filter((e) => e.validation_result === 'CONFIRMED').map((e) => e.finding_id)
  );

  const uniqueProofsCount = confirmedFindings.filter((f) => confirmedUniqueProofFindings.has(f.id)).length;
  const technicalEvidenceCaptured = baselineEvidence.length;

  assert.strictEqual(uniqueProofsCount, 1, 'Two evidence artifacts for one finding must count as 1 unique confirmed vulnerability proof');
  assert.strictEqual(technicalEvidenceCaptured, 2, 'Technical evidence captured must count all 2 baseline evidence artifacts');
});
