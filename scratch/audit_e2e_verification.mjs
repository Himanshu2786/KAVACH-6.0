import http from 'http';

function getWebSocketUrl() {
  return new Promise((resolve, reject) => {
    http.get('http://127.0.0.1:9222/json', (res) => {
      let raw = '';
      res.on('data', chunk => raw += chunk);
      res.on('end', () => {
        try {
          const tabs = JSON.parse(raw);
          const tab = tabs.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
          if (tab) resolve(tab.webSocketDebuggerUrl);
          else reject(new Error('No page tab found'));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

function createCdpSession(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 1;
  const callbacks = new Map();
  const consoleErrors = [];

  ws.on('message', (msg) => {
    const data = JSON.parse(msg.toString());
    if (data.method === 'Runtime.exceptionThrown') {
      consoleErrors.push(data.params.exceptionDetails);
    }
    if (data.id && callbacks.has(data.id)) {
      const cb = callbacks.get(data.id);
      callbacks.delete(data.id);
      cb(data);
    }
  });

  const send = (method, params = {}) => {
    return new Promise((resolve, reject) => {
      const msgId = id++;
      callbacks.set(msgId, (res) => {
        if (res.error) reject(res.error);
        else resolve(res.result);
      });
      ws.send(JSON.stringify({ id: msgId, method, params }));
    });
  };

  const evaluate = async (expression) => {
    const res = await send('Runtime.evaluate', {
      expression,
      returnByValue: true,
      awaitPromise: true
    });
    return res.result?.value;
  };

  return new Promise((resolve, reject) => {
    ws.on('open', async () => {
      await send('Runtime.enable');
      await send('Page.enable');
      resolve({ send, evaluate, consoleErrors, close: () => ws.close() });
    });
    ws.on('error', reject);
  });
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function runAudit() {
  console.log('=== STEP 73.1 AUDIT: CONNECTING TO CDP ===');
  const wsUrl = await getWebSocketUrl();
  const session = await createCdpSession(wsUrl);
  const { evaluate, consoleErrors } = session;

  const navigate = async (url) => {
    await session.send('Page.navigate', { url });
    await sleep(2500);
  };

  try {
    // ----------------------------------------------------
    // LOCAL AUDIT (http://127.0.0.1:5173)
    // ----------------------------------------------------
    console.log('\n--- 1. TESTING LOCAL LOGIN & AUTH ---');
    await navigate('http://127.0.0.1:5173/login');
    const loginTitle = await evaluate('document.title');
    console.log('Login page title:', loginTitle);

    // Login as ADMIN001
    await evaluate(`
      (() => {
        const u = document.querySelector('input[type="text"]') || document.querySelector('input[name="user_id"]');
        const p = document.querySelector('input[type="password"]');
        if (u) { u.value = 'ADMIN001'; u.dispatchEvent(new Event('input', { bubbles: true })); }
        if (p) { p.value = 'Admin@Kavach2026!'; p.dispatchEvent(new Event('input', { bubbles: true })); }
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('AUTHENTICATE') || b.textContent.includes('LOGIN') || b.textContent.includes('Sign In'));
        if (btn) btn.click();
      })()
    `);
    await sleep(3000);

    const routesToTest = [
      { name: 'DASHBOARD / HOME', path: '/' },
      { name: 'COMMAND CENTER', path: '/command-center' },
      { name: 'WORLD MONITOR', path: '/world-monitor' },
      { name: 'NEW ASSESSMENT', path: '/new-assessment' },
      { name: 'FINDINGS', path: '/findings' },
      { name: 'EVIDENCE', path: '/evidence' },
      { name: 'RISK', path: '/risk' },
      { name: 'SECURITY REPORT', path: '/report' },
      { name: 'AI ANALYSIS', path: '/ai-analysis' }
    ];

    console.log('\n--- 2. LOCAL ROUTES & NO CRASH AUDIT ---');
    for (const r of routesToTest) {
      await navigate('http://127.0.0.1:5173' + r.path);
      const textLen = await evaluate('document.body.innerText.length');
      const hasContent = textLen > 100;
      console.log(`  Route ${r.name} (${r.path}): textLen=${textLen} - ${hasContent ? 'OK' : 'EMPTY'}`);
    }

    console.log('\n--- 3. STEP 72 REGRESSION AUDIT (VIEW RISK MATRIX -> OVERVIEW) ---');
    // Step 72 reproduction path
    await navigate('http://127.0.0.1:5173/command-center');
    await sleep(2000);

    // Click "View Risk Matrix" or navigate directly to /risk
    await navigate('http://127.0.0.1:5173/risk');
    await sleep(2000);

    // Open finding dossier
    const inspectClicked = await evaluate(`
      (() => {
        const btns = Array.from(document.querySelectorAll('button, a'));
        const inspectBtn = btns.find(b => b.textContent.includes('Inspect') || b.textContent.includes('Detail') || b.textContent.includes('View'));
        if (inspectBtn) {
          inspectBtn.click();
          return true;
        }
        return false;
      })()
    `);
    console.log('  Clicked Inspect Finding:', inspectClicked);
    await sleep(2500);

    // In Finding Detail, click "Overview" tab
    const overviewClicked = await evaluate(`
      (() => {
        const tabs = Array.from(document.querySelectorAll('button, [role="tab"], div'));
        const ovTab = tabs.find(t => t.textContent.trim().toUpperCase() === 'OVERVIEW' || t.textContent.trim().startsWith('Overview'));
        if (ovTab) {
          ovTab.click();
          return true;
        }
        return false;
      })()
    `);
    console.log('  Clicked Overview tab:', overviewClicked);
    await sleep(2000);

    const overviewText = await evaluate('document.body.innerText');
    const isBlank = overviewText.trim().length < 50;
    const hasFindingContext = overviewText.toUpperCase().includes('FINDING CONTEXT') || overviewText.toUpperCase().includes('OVERVIEW') || overviewText.toUpperCase().includes('IDENTIFIER');
    const hasAssessmentId = overviewText.toUpperCase().includes('ASSESSMENT ID') || overviewText.includes('ASM-') || overviewText.includes('WM-');
    const hasPriority = overviewText.toUpperCase().includes('PRIORITY SCORE') || overviewText.toUpperCase().includes('RISK') || overviewText.toUpperCase().includes('SCORE');

    console.log('  Step 72 Results:');
    console.log('    Blank/Black Screen:', isBlank ? 'YES (CRASH!)' : 'NO (PASSED)');
    console.log('    Finding Context visible:', hasFindingContext);
    console.log('    Assessment ID visible:', hasAssessmentId);
    console.log('    Priority Score visible:', hasPriority);

    console.log('\n--- 4. OLLAMA PROVENANCE AUDIT ---');
    await navigate('http://127.0.0.1:5173/ai-analysis');
    await sleep(2500);
    const aiAnalysisText = await evaluate('document.body.innerText');
    console.log('  AI Analysis Page rendered: textLen=', aiAnalysisText.length);

    console.log('\n--- 5. CHECK CONSOLE EXCEPTIONS ON LOCAL ---');
    console.log('  Local Uncaught Exceptions:', consoleErrors.length);
    if (consoleErrors.length > 0) {
      console.log('  Exceptions detail:', consoleErrors);
    }

    // ----------------------------------------------------
    // PUBLIC PRODUCTION AUDIT (https://kavach-security-system.netlify.app/)
    // ----------------------------------------------------
    console.log('\n--- 6. TESTING PRODUCTION NETLIFY DEPLOYMENT ---');
    consoleErrors.length = 0; // reset for prod audit
    await navigate('https://kavach-security-system.netlify.app/login');
    await sleep(3000);
    const prodTitle = await evaluate('document.title');
    console.log('  Netlify Prod Title:', prodTitle);

    // Authenticate on Netlify
    await evaluate(`
      (() => {
        const u = document.querySelector('input[type="text"]') || document.querySelector('input[name="user_id"]');
        const p = document.querySelector('input[type="password"]');
        if (u) { u.value = 'ADMIN001'; u.dispatchEvent(new Event('input', { bubbles: true })); }
        if (p) { p.value = 'Admin@Kavach2026!'; p.dispatchEvent(new Event('input', { bubbles: true })); }
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('AUTHENTICATE') || b.textContent.includes('LOGIN') || b.textContent.includes('Sign In'));
        if (btn) btn.click();
      })()
    `);
    await sleep(4000);

    const prodRoutes = [
      { name: 'COMMAND CENTER', path: '/command-center' },
      { name: 'FINDINGS', path: '/findings' },
      { name: 'RISK MATRIX', path: '/risk' },
      { name: 'EVIDENCE', path: '/evidence' },
      { name: 'REPORT', path: '/report' },
      { name: 'AI ANALYSIS', path: '/ai-analysis' }
    ];

    for (const r of prodRoutes) {
      await navigate('https://kavach-security-system.netlify.app' + r.path);
      const textLen = await evaluate('document.body.innerText.length');
      console.log(`  Prod Route ${r.name} (${r.path}): textLen=${textLen} - ${textLen > 100 ? 'OK' : 'EMPTY'}`);
    }

    // Test Step 72 on Prod
    await navigate('https://kavach-security-system.netlify.app/risk');
    await sleep(2500);
    await evaluate(`
      (() => {
        const btns = Array.from(document.querySelectorAll('button, a'));
        const inspectBtn = btns.find(b => b.textContent.includes('Inspect') || b.textContent.includes('Detail') || b.textContent.includes('View'));
        if (inspectBtn) inspectBtn.click();
      })()
    `);
    await sleep(2500);
    await evaluate(`
      (() => {
        const tabs = Array.from(document.querySelectorAll('button, [role="tab"], div'));
        const ovTab = tabs.find(t => t.textContent.trim().toUpperCase() === 'OVERVIEW' || t.textContent.trim().startsWith('Overview'));
        if (ovTab) ovTab.click();
      })()
    `);
    await sleep(2000);
    const prodOvText = await evaluate('document.body.innerText');
    const prodIsBlank = prodOvText.trim().length < 50;
    console.log('  Netlify Prod Step 72 Black Screen:', prodIsBlank ? 'YES (CRASH!)' : 'NO (PASSED)');

    console.log('\n--- 7. CHECK CONSOLE EXCEPTIONS ON PRODUCTION NETLIFY ---');
    console.log('  Prod Uncaught Exceptions:', consoleErrors.length);
    if (consoleErrors.length > 0) {
      console.log('  Prod Exceptions detail:', consoleErrors);
    }

  } finally {
    session.close();
  }
}

runAudit().catch(err => {
  console.error('Audit run error:', err);
  process.exit(1);
});
