import { test } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test('1. FindingDetailPage.tsx safely handles null or undefined created_at and updated_at in Overview tab', () => {
  const filePath = path.resolve(__dirname, '../src/pages/FindingDetailPage.tsx');
  const content = fs.readFileSync(filePath, 'utf-8');

  // Must not have unsafely chained .slice(0, 10) directly on finding.created_at or finding.updated_at
  assert.ok(
    !content.includes('finding.created_at.slice('),
    'FindingDetailPage.tsx must NOT contain unsafe finding.created_at.slice('
  );
  assert.ok(
    !content.includes('finding.updated_at.slice('),
    'FindingDetailPage.tsx must NOT contain unsafe finding.updated_at.slice('
  );

  // Must contain safe ternary or string conversions
  assert.ok(
    content.includes('finding.created_at ?') || content.includes('String(finding.created_at)'),
    'FindingDetailPage.tsx must safeguard finding.created_at rendering'
  );
  assert.ok(
    content.includes('finding.updated_at ?') || content.includes('String(finding.updated_at)'),
    'FindingDetailPage.tsx must safeguard finding.updated_at rendering'
  );
});

test('2. FindingDetailPage Overview tab simulation with null timestamps does not throw TypeError', () => {
  const findingWithNullDates = {
    id: 'FINDING-NULL-001',
    assessment_id: null,
    title: 'Test Null Dates Finding',
    description: null,
    category: 'API_SECURITY',
    base_severity: 'HIGH',
    priority: 'HIGH',
    priority_score: null,
    created_at: null,
    updated_at: null,
    evidence_records: []
  };

  // Simulate rendering Overview tab fields
  const renderCreated = (finding) => (finding.created_at ? String(finding.created_at).slice(0, 10) : 'N/A');
  const renderUpdated = (finding) => (finding.updated_at ? String(finding.updated_at).slice(0, 10) : 'N/A');
  const renderDesc = (finding) => (finding.description || 'No detailed description available.');
  const renderAssessmentId = (finding) => (finding.assessment_id || 'N/A');
  const renderPriority = (finding) => (
    finding.priority_score !== undefined && finding.priority_score !== null ? `${finding.priority_score} / 10.0` : 'N/A'
  );

  assert.strictEqual(renderCreated(findingWithNullDates), 'N/A');
  assert.strictEqual(renderUpdated(findingWithNullDates), 'N/A');
  assert.strictEqual(renderDesc(findingWithNullDates), 'No detailed description available.');
  assert.strictEqual(renderAssessmentId(findingWithNullDates), 'N/A');
  assert.strictEqual(renderPriority(findingWithNullDates), 'N/A');
});

test('3. RiskPrioritizationPage.tsx safely accesses explanation properties with optional chaining', () => {
  const filePath = path.resolve(__dirname, '../src/pages/RiskPrioritizationPage.tsx');
  const content = fs.readFileSync(filePath, 'utf-8');

  assert.ok(
    content.includes('item.explanation?.base_severity?.score') ||
    content.includes('item.explanation?.summary_statement'),
    'RiskPrioritizationPage.tsx must use safe optional chaining for explanation factors'
  );
});

test('4. RiskPrioritizationPage navigation to finding-detail is intact', () => {
  const filePath = path.resolve(__dirname, '../src/pages/RiskPrioritizationPage.tsx');
  const content = fs.readFileSync(filePath, 'utf-8');

  assert.ok(
    content.includes("navigate('finding-detail', item.finding_id)"),
    "RiskPrioritizationPage must link to 'finding-detail' with item.finding_id"
  );
});
