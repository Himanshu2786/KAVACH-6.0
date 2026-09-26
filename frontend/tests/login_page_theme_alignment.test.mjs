import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const srcDir = path.resolve(__dirname, '../src');

test('1. LoginPage.tsx inherits the KAVACH 6.0 ambient background and pointer light reflection', () => {
  const loginTsx = fs.readFileSync(path.join(srcDir, 'components/auth/LoginPage.tsx'), 'utf-8');

  assert.match(loginTsx, /import\s+{\s*AmbientBackground\s*}\s+from\s+['"]\.\.\/visual\/AmbientBackground['"]/,
    'LoginPage must import AmbientBackground');
  assert.match(loginTsx, /import\s+{\s*CursorLight\s*}\s+from\s+['"]\.\.\/visual\/CursorLight['"]/,
    'LoginPage must import CursorLight');
  assert.match(loginTsx, /<AmbientBackground\s*\/>/,
    'LoginPage must render <AmbientBackground />');
  assert.match(loginTsx, /<CursorLight\s*\/>/,
    'LoginPage must render <CursorLight />');
});

test('2. LoginPage.tsx incorporates the exact KAVACH 6.0 navbar header language', () => {
  const loginTsx = fs.readFileSync(path.join(srcDir, 'components/auth/LoginPage.tsx'), 'utf-8');

  // Verify header bar structure matches Navbar height and style
  assert.match(loginTsx, /<header[\s\S]*?h-14/,
    'LoginPage must have a header with h-14 height');
  assert.match(loginTsx, /KAVACH/, 'LoginPage must display KAVACH brand');
  assert.match(loginTsx, /6\.0/, 'LoginPage must display 6.0 version pill');
  assert.match(loginTsx, /GATEWAY:\s*SECURE\s*ACCESS/, 'LoginPage must have secure access badge');
});

test('3. LoginPage.tsx uses the design system tokens (glass-level-2, glass-input, btn-primary)', () => {
  const loginTsx = fs.readFileSync(path.join(srcDir, 'components/auth/LoginPage.tsx'), 'utf-8');

  assert.match(loginTsx, /glass-level-2/, 'LoginPage must use glass-level-2 for its card');
  assert.match(loginTsx, /glass-input/, 'LoginPage must use glass-input for input styling');
  assert.match(loginTsx, /btn-primary/, 'LoginPage must use btn-primary for the submission button');
});

test('4. LoginPage.tsx preserves authentication form fields, loading, and error handling', () => {
  const loginTsx = fs.readFileSync(path.join(srcDir, 'components/auth/LoginPage.tsx'), 'utf-8');

  assert.match(loginTsx, /USER ID/, 'LoginPage must have USER ID label');
  assert.match(loginTsx, /PASSWORD/, 'LoginPage must have PASSWORD label');
  assert.match(loginTsx, /Sign In to KAVACH/, 'LoginPage must have Sign In to KAVACH action text');
  assert.match(loginTsx, /login\s*\(\s*userId\.trim\(\)\.toUpperCase\(\)\s*,\s*password\s*\)/,
    'LoginPage must call login with uppercase trimmed userId and password');
  assert.match(loginTsx, /role=["']alert["']/, 'LoginPage must display error with accessible role alert');
  assert.match(loginTsx, /animate-spin/, 'LoginPage must have loading indicator');
});
