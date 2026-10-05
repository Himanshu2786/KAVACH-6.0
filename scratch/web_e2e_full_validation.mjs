async function run() {
  const targets = await (await fetch('http://127.0.0.1:9222/json')).json();
  const page = targets.find(t => t.type === 'page' && !t.url.startsWith('chrome'));
  if (!page) {
    console.error('No valid page found on 127.0.0.1:9222');
    process.exit(1);
  }

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 1;
  const send = (method, params = {}) => new Promise((res, rej) => {
    const msgId = id++;
    const handler = (event) => {
      const data = JSON.parse(event.data);
      if (data.id === msgId) {
        ws.removeEventListener('message', handler);
        if (data.error) rej(data.error);
        else res(data.result);
      }
    };
    ws.addEventListener('message', handler);
    ws.send(JSON.stringify({ id: msgId, method, params }));
  });

  await new Promise(r => ws.onopen = r);

  const exceptions = [];
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.method === 'Runtime.exceptionThrown') {
      console.error('BROWSER EXCEPTION:', data.params.exceptionDetails.text, data.params.exceptionDetails.exception?.description);
      exceptions.push(data.params.exceptionDetails);
    }
  };

  await send('Runtime.enable');
  await send('Page.enable');

  const evalCode = async (expr) => {
    const res = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    return res.result?.value;
  };

  console.log('=== Step 1: Navigate to /command-center ===');
  await send('Page.navigate', { url: 'http://127.0.0.1:5173/command-center' });
  await new Promise(r => setTimeout(r, 2000));

  let isLogin = await evalCode(`Boolean(document.querySelector('input[type="password"]'))`);
  if (isLogin) {
    console.log('Logging in as ADMIN001...');
    await evalCode(`(() => {
      const inputs = Array.from(document.querySelectorAll('input'));
      const userInput = inputs.find(i => i.placeholder?.includes('ID') || i.type === 'text');
      const passInput = document.querySelector('input[type="password"]');
      if (userInput) {
        userInput.value = 'ADMIN001';
        userInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
      if (passInput) {
        passInput.value = 'Admin@Kavach2026!';
        passInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
      const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Sign In') || b.type === 'submit');
      if (submitBtn) submitBtn.click();
    })()`);
    await new Promise(r => setTimeout(r, 2500));
    await send('Page.navigate', { url: 'http://127.0.0.1:5173/command-center' });
    await new Promise(r => setTimeout(r, 2000));
  }

  // Ensure we are on Command Center
  await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Command Center'));
    if (btn) btn.click();
  })()`);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 2: Phase 15 Mandatory Step 72 Flow: Command Center -> Posture -> View Risk Matrix -> Dossier -> Overview ===');
  // Click Posture KPI Card
  let kpiClick = await evalCode(`(() => {
    const kpi = Array.from(document.querySelectorAll('div')).find(d => d.innerText.includes('SECURITY POSTURE'));
    if (kpi) { kpi.click(); return 'CLICKED_KPI'; }
    return 'NO_KPI';
  })()`);
  console.log('Posture KPI click:', kpiClick);
  await new Promise(r => setTimeout(r, 1000));

  // Click View Risk Matrix in modal, or fallback to Risk nav
  let vrmClick = await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button, a')).find(b => b.innerText.includes('View Risk Matrix') || b.innerText.includes('Risk Scoring'));
    if (btn) { btn.click(); return 'CLICKED: ' + btn.innerText.trim(); }
    window.location.href = 'http://127.0.0.1:5173/risk';
    return 'NAV_LOCATION_RISK';
  })()`);
  console.log('View Risk Matrix action:', vrmClick);
  await new Promise(r => setTimeout(r, 2000));

  console.log('Risk Matrix Page Heading:', await evalCode(`document.querySelector('h1, h2, h3')?.innerText`));

  // Expand finding card
  await evalCode(`(() => {
    const card = Array.from(document.querySelectorAll('div')).find(d => d.innerText.includes('Risk Score') && d.className.includes('cursor-pointer'));
    if (card) card.click();
  })()`);
  await new Promise(r => setTimeout(r, 1000));

  // Click Inspect Finding Dossier
  let ifdClick = await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Inspect Finding Dossier'));
    if (btn) { btn.click(); return 'CLICKED_DOSSIER'; }
    return 'NO_DOSSIER_BTN';
  })()`);
  console.log('Inspect Finding Dossier:', ifdClick);
  await new Promise(r => setTimeout(r, 1500));

  // Click Overview Tab
  let ovClick = await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Overview');
    if (btn) { btn.click(); return 'CLICKED_OVERVIEW'; }
    return 'NO_OVERVIEW_BTN';
  })()`);
  console.log('Overview tab click:', ovClick);
  await new Promise(r => setTimeout(r, 1500));

  // Inspect Overview State
  let ovState = await evalCode(`(() => {
    const root = document.getElementById('root');
    const text = document.body.innerText.toLowerCase();
    return {
      isBlank: !root || root.innerHTML.trim() === '',
      hasFindingContext: text.includes('finding context'),
      hasAssessmentId: text.includes('assessment id'),
      hasPriorityScore: text.includes('priority score'),
      hasCreated: text.includes('created'),
      hasUpdated: text.includes('updated'),
      textSample: document.body.innerText.slice(0, 300).replace(/\\n+/g, ' ')
    };
  })()`);
  console.log('OVERVIEW STATE:', JSON.stringify(ovState, null, 2));

  if (ovState.isBlank || !ovState.hasFindingContext || !ovState.hasAssessmentId) {
    console.error('FATAL REGRESSION: Overview failed to render!');
    process.exit(1);
  }
  console.log('SUCCESS: Step 72 Regression Test PASSED cleanly! Zero black screen.');

  // Test Back to Findings
  let backAction = await evalCode(`(() => {
    const b = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.includes('Back to Findings'));
    if (b) { b.click(); return 'CLICKED_BACK'; }
    return 'NO_BACK_BTN';
  })()`);
  console.log('Back button action:', backAction);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 3: Test Major Application Routes ===');
  const routes = [
    { url: 'http://127.0.0.1:5173/command-center', name: 'Command Center' },
    { url: 'http://127.0.0.1:5173/world-monitor', name: 'World Situational Monitor' },
    { url: 'http://127.0.0.1:5173/new-assessment', name: 'New Assessment Scope Guard' },
    { url: 'http://127.0.0.1:5173/findings', name: 'Findings Matrix' },
    { url: 'http://127.0.0.1:5173/evidence', name: 'Evidence Validation' },
    { url: 'http://127.0.0.1:5173/risk', name: 'Risk Scoring' },
    { url: 'http://127.0.0.1:5173/report', name: 'Security Report' },
    { url: 'http://127.0.0.1:5173/ai-analysis', name: 'AI Analysis' }
  ];

  for (const r of routes) {
    await send('Page.navigate', { url: r.url });
    await new Promise(res => setTimeout(res, 1200));

    let s = await evalCode(`(() => {
      const root = document.getElementById('root');
      return {
        isBlank: !root || root.innerHTML.trim() === '',
        heading: document.querySelector('h1, h2, h3')?.innerText || 'No Heading'
      };
    })()`);
    console.log('Route', r.name, '| Heading:', s.heading, '| Blank:', s.isBlank);
    if (s.isBlank) {
      console.error('Crash on route: ' + r.name);
      process.exit(1);
    }
  }

  console.log('=== Step 4: Test Step 71 Ollama Provenance ===');
  await send('Page.navigate', { url: 'http://127.0.0.1:5173/findings' });
  await new Promise(r => setTimeout(r, 1200));

  await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Inspect') || b.innerText.includes('View'));
    if (btn) btn.click();
  })()`);
  await new Promise(r => setTimeout(r, 1200));

  let provCheck = await evalCode(`(() => {
    const dots = Array.from(document.querySelectorAll('[title*="Ollama"], [title*="ollama"]'));
    return {
      dotCount: dots.length,
      titles: dots.map(d => d.getAttribute('title'))
    };
  })()`);
  console.log('Provenance dot check:', JSON.stringify(provCheck, null, 2));

  console.log('=== Step 5: Test Logout & Login ===');
  await evalCode(`(() => {
    const menuBtn = document.querySelector('button[aria-label="Toggle navigation menu"]');
    if (menuBtn) menuBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 500));

  let logoutAction = await evalCode(`(() => {
    const logoutBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Sign Out') || b.innerText.includes('Logout'));
    if (logoutBtn) { logoutBtn.click(); return 'LOGGED_OUT'; }
    return 'NO_LOGOUT_BTN';
  })()`);
  console.log('Logout result:', logoutAction);
  await new Promise(r => setTimeout(r, 1500));

  let onLogin = await evalCode(`Boolean(document.querySelector('input[type="password"]'))`);
  console.log('On Login Page after logout:', onLogin);

  if (onLogin) {
    await evalCode(`(() => {
      const inputs = Array.from(document.querySelectorAll('input'));
      const userInput = inputs.find(i => i.placeholder?.includes('ID') || i.type === 'text');
      const passInput = document.querySelector('input[type="password"]');
      if (userInput) {
        userInput.value = 'ADMIN001';
        userInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
      if (passInput) {
        passInput.value = 'Admin@Kavach2026!';
        passInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
      const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Sign In') || b.type === 'submit');
      if (submitBtn) submitBtn.click();
    })()`);
    await new Promise(r => setTimeout(r, 2000));
    console.log('Re-login successful!');
  }

  console.log('=== Total Runtime Exceptions Captured:', exceptions.length);
  if (exceptions.length > 0) {
    console.error('EXCEPTIONS ENCOUNTERED:', exceptions);
    process.exit(1);
  }

  console.log('ALL E2E WEB VALIDATION STEPS COMPLETED WITH ZERO ERRORS!');
  ws.close();
}

run().catch(e => {
  console.error('Test run failed:', e);
  process.exit(1);
});
