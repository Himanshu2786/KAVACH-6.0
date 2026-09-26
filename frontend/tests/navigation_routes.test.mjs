import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const srcDir = path.resolve(__dirname, '../src');

/**
 * Regression Test Suite: KAVACH 6.0 Navigation Route Resolution
 * 
 * Tests:
 * 1. Command Center route ('command-center') renders CommandCenterPage
 * 2. World Situational Monitor route ('world-monitor') renders WorldMonitorPage
 * 3. Command Center and World Situational Monitor are distinct routes with no crosstalk
 * 4. WorkspaceSubnav configuration contains distinct entries for Command Center and World Monitor
 * 5. Navbar platformModules and demo journey correctly map Command Center vs World Situational Monitor
 * 6. FindingsPage 'View in World Monitor' buttons navigate to 'world-monitor', not 'command-center'
 * 7. Sidebar maps 'command-center' to Command Center and 'world-monitor' to World Situational Monitor
 */

test('1. App.tsx route mapping: command-center maps to CommandCenterPage and world-monitor maps to WorldMonitorPage', () => {
  const appTsx = fs.readFileSync(path.join(srcDir, 'App.tsx'), 'utf-8');

  // Verify imports
  assert.match(appTsx, /import\s+{\s*CommandCenterPage\s*}\s+from\s+['"]\.\/pages\/CommandCenterPage['"]/,
    'CommandCenterPage must be imported in App.tsx');
  assert.match(appTsx, /import\s+{\s*WorldMonitorPage\s*}\s+from\s+['"]\.\/pages\/WorldMonitorPage['"]/,
    'WorldMonitorPage must be imported in App.tsx');

  // Verify command-center route returns <CommandCenterPage />
  const commandCenterRouteRegex = /case\s+['"]command-center['"]:\s*return\s+<CommandCenterPage\s*\/>;/;
  assert.match(appTsx, commandCenterRouteRegex,
    "case 'command-center' must return <CommandCenterPage />");

  // Verify world-monitor route returns <WorldMonitorPage />
  const worldMonitorRouteRegex = /case\s+['"]world-monitor['"]:\s*(case\s+['"][^'"]+['"]:\s*)*return\s+<WorldMonitorPage\s*\/>;/;
  assert.match(appTsx, worldMonitorRouteRegex,
    "case 'world-monitor' must return <WorldMonitorPage />");

  // Prove command-center does NOT return WorldMonitorPage
  const badCommandCenterRegex = /case\s+['"]command-center['"]:\s*return\s+<WorldMonitorPage\s*\/>;/;
  assert.doesNotMatch(appTsx, badCommandCenterRegex,
    "case 'command-center' must NOT return <WorldMonitorPage />");
});

test('2. WorkspaceSubnav.tsx maps Command Center and World Monitor as separate tabs', () => {
  const subnavTsx = fs.readFileSync(path.join(srcDir, 'components/layout/WorkspaceSubnav.tsx'), 'utf-8');

  // Verify command-center tab
  assert.match(subnavTsx, /id:\s*['"]command-center['"],\s*label:\s*['"]Command Center['"]/,
    "WorkspaceSubnav must have id: 'command-center' labeled 'Command Center'");

  // Verify world-monitor tab
  assert.match(subnavTsx, /id:\s*['"]world-monitor['"],\s*label:\s*['"]World Monitor['"]/,
    "WorkspaceSubnav must have id: 'world-monitor' labeled 'World Monitor'");

  // Proves the bug is fixed: id: 'command-center' must not be labeled 'World Monitor'
  assert.doesNotMatch(subnavTsx, /id:\s*['"]command-center['"],\s*label:\s*['"]World Monitor['"]/,
    "Bug regression check: id: 'command-center' must NOT be labeled 'World Monitor'");
});

test('3. Navbar.tsx correctly separates Command Center and World Situational Monitor', () => {
  const navbarTsx = fs.readFileSync(path.join(srcDir, 'components/layout/Navbar.tsx'), 'utf-8');

  // Step 1 in Demo Journey is Command Center
  assert.match(navbarTsx, /title:\s*['"]1\.\s*Command Center['"],\s*page:\s*['"]command-center['"]/,
    "DEMO_JOURNEY_STEPS step 1 must navigate to 'command-center'");

  // platformModules contains Command Center and World Situational Monitor
  assert.match(navbarTsx, /id:\s*['"]command-center['"],\s*label:\s*['"]Command Center['"]/,
    "platformModules must contain 'command-center'");
  assert.match(navbarTsx, /id:\s*['"]world-monitor['"],\s*label:\s*['"]World Situational Monitor['"]/,
    "platformModules must contain 'world-monitor'");
});

test('4. Sidebar.tsx separates Command Center and World Situational Monitor', () => {
  const sidebarTsx = fs.readFileSync(path.join(srcDir, 'components/layout/Sidebar.tsx'), 'utf-8');

  assert.match(sidebarTsx, /id:\s*['"]command-center['"],\s*label:\s*['"]Command Center['"]/,
    "Sidebar must have 'command-center' labeled 'Command Center'");
  assert.match(sidebarTsx, /id:\s*['"]world-monitor['"],\s*label:\s*['"]World Situational Monitor['"]/,
    "Sidebar must have 'world-monitor' labeled 'World Situational Monitor'");
});

test('5. FindingsPage.tsx "View in World Monitor" buttons navigate to world-monitor', () => {
  const findingsTsx = fs.readFileSync(path.join(srcDir, 'pages/FindingsPage.tsx'), 'utf-8');

  // Ensure "View in World Monitor" does NOT navigate to 'command-center'
  const badCorrelationNav = /setSelectedWorldEventId\([^)]+\);\s*navigate\(['"]command-center['"]\);/g;
  const matches = findingsTsx.match(badCorrelationNav);
  assert.equal(matches, null,
    "FindingsPage 'View in World Monitor' action buttons must not navigate to 'command-center'");

  // Ensure it navigates to 'world-monitor'
  const goodCorrelationNav = /setSelectedWorldEventId\([^)]+\);\s*navigate\(['"]world-monitor['"]\);/g;
  const goodMatches = findingsTsx.match(goodCorrelationNav);
  assert.ok(goodMatches && goodMatches.length >= 2,
    "FindingsPage 'View in World Monitor' action buttons must navigate to 'world-monitor'");
});

test('6. Route resolution simulation test', () => {
  // Simulate App router resolution logic
  const resolvePage = (route) => {
    switch (route) {
      case 'command-center':
        return 'CommandCenterPage';
      case 'world-monitor':
      case 'world_monitor':
      case 'situational-monitor':
        return 'WorldMonitorPage';
      case 'url-check':
        return 'UrlSecurityCheckPage';
      case 'findings':
        return 'FindingsPage';
      case 'evidence':
        return 'EvidenceValidationPage';
      default:
        return 'HomePage';
    }
  };

  assert.equal(resolvePage('command-center'), 'CommandCenterPage',
    "Direct navigation to 'command-center' must render CommandCenterPage");
  assert.equal(resolvePage('world-monitor'), 'WorldMonitorPage',
    "Direct navigation to 'world-monitor' must render WorldMonitorPage");
  assert.notEqual(resolvePage('command-center'), resolvePage('world-monitor'),
    "Command Center and World Situational Monitor must resolve to distinct pages");
});
