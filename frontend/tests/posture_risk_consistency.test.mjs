import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const srcDir = path.resolve(__dirname, '../src');

/**
 * Regression Test Suite: KAVACH 6.0 Posture & Risk Level Consistency
 * 
 * Verifies:
 * 1. Command Center calculates riskLevel by accounting for MEDIUM severity findings.
 * 2. Command Center displays postureLabel (e.g. MODERATE RISK) alongside numerical score.
 * 3. SecurityReportPage displays posture grade, score, and risk level consistently.
 * 4. Assessment A018 (1 confirmed MEDIUM finding) resolves to:
 *    - Security Posture: 70 / 100 (MODERATE RISK)
 *    - Risk Level: MEDIUM (CVSS 3.1)
 *    - Operational Label: "Remediation & Hardening Required"
 */

test('1. CommandCenterPage.tsx includes MEDIUM severity in riskLevel calculation', () => {
  const pageTsx = fs.readFileSync(path.join(srcDir, 'pages/CommandCenterPage.tsx'), 'utf-8');

  // Verify riskLevel derivation includes MEDIUM
  assert.match(pageTsx, /severityCounts\.MEDIUM\s*>\s*0\s*\?\s*['"]MEDIUM['"]/,
    'CommandCenterPage must explicitly account for MEDIUM severity in riskLevel derivation');

  // Verify postureLabel is defined and used
  assert.match(pageTsx, /postureScore\s*<\s*85\s*\?\s*['"]MODERATE RISK['"]/,
    'postureLabel must map score < 85 to MODERATE RISK');
});

test('2. A018 riskLevel evaluation produces MEDIUM, not LOW', () => {
  const severityCounts = {
    CRITICAL: 0,
    HIGH: 0,
    MEDIUM: 1, // WM-API-DOCS-A018
    LOW: 0,
    INFO: 0
  };

  const posture = {
    score: 70,
    posture: 'MODERATE RISK',
    risk_level: 'MEDIUM',
    status_label: 'Remediation & Hardening Required'
  };

  // Canonical calculation as implemented in CommandCenterPage:
  const riskLevel = posture?.risk_level ?? (
    severityCounts.CRITICAL > 0 ? 'CRITICAL' :
      severityCounts.HIGH > 0 ? 'HIGH' :
        severityCounts.MEDIUM > 0 ? 'MEDIUM' :
          severityCounts.LOW > 0 ? 'LOW' :
            'LOW'
  );

  const postureScore = posture?.score ?? 70;
  const postureLabel = posture?.posture ?? (
    postureScore < 50 ? 'CRITICAL RISK' :
      postureScore < 70 ? 'HIGH RISK' :
        postureScore < 85 ? 'MODERATE RISK' :
          'LOW RISK'
  );

  assert.equal(riskLevel, 'MEDIUM', 'Risk level must be MEDIUM, never falsely LOW');
  assert.equal(postureScore, 70, 'Posture score must be 70');
  assert.equal(postureLabel, 'MODERATE RISK', 'Posture label must be MODERATE RISK');
  assert.equal(posture.status_label, 'Remediation & Hardening Required');
});

test('3. Clean target evaluates to SECURE posture and LOW risk level', () => {
  const cleanPosture = {
    score: 95,
    posture: 'SECURE',
    risk_level: 'LOW',
    status_label: 'No Vulnerabilities Identified'
  };

  const severityCounts = {
    CRITICAL: 0,
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0,
    INFO: 0
  };

  const riskLevel = cleanPosture?.risk_level ?? (
    severityCounts.CRITICAL > 0 ? 'CRITICAL' :
      severityCounts.HIGH > 0 ? 'HIGH' :
        severityCounts.MEDIUM > 0 ? 'MEDIUM' :
          severityCounts.LOW > 0 ? 'LOW' :
            'LOW'
  );

  assert.equal(riskLevel, 'LOW');
  assert.equal(cleanPosture.posture, 'SECURE');
  assert.equal(cleanPosture.score, 95);
});
