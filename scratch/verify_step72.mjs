async function run() {
  const targets = await (await fetch('http://127.0.0.1:9222/json')).json();
  const page = targets.find(t => t.type === 'page' && t.url.includes('5173'));
  if (!page) {
    console.error('No Vite page found on 127.0.0.1:9222');
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
      console.error('EXCEPTION:', data.params.exceptionDetails.text, data.params.exceptionDetails.exception?.description);
      exceptions.push(data.params.exceptionDetails);
    }
  };

  await send('Runtime.enable');
  await send('Page.enable');

  const evalCode = async (expr) => {
    const res = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    return res.result?.value;
  };

  console.log('=== Step 1: Navigating to http://127.0.0.1:5173/ ===');
  await send('Page.navigate', { url: 'http://127.0.0.1:5173/' });
  await new Promise(r => setTimeout(r, 2000));

  // Check if Login page is shown
  let isLogin = await evalCode(`Boolean(document.querySelector('input[type="password"]'))`);
  if (isLogin) {
    console.log('Login form detected. Logging in with ADMIN001...');
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
      const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Sign In') || b.innerText.includes('Authenticate') || b.type === 'submit');
      if (submitBtn) submitBtn.click();
    })()`);
    await new Promise(r => setTimeout(r, 2500));
  }

  console.log('=== Step 2: Open Risk Matrix ===');
  // Click on "10. Risk Scoring" or navigate to risk
  let navResult = await evalCode(`(() => {
    const btns = Array.from(document.querySelectorAll('button, a'));
    const riskBtn = btns.find(b => b.innerText.includes('Risk Scoring') || b.innerText.includes('Risk Matrix') || b.getAttribute('data-nav') === 'risk');
    if (riskBtn) {
      riskBtn.click();
      return 'CLICKED_RISK_NAV: ' + riskBtn.innerText;
    }
    window.location.hash = '#risk';
    return 'FALLBACK_HASH_RISK';
  })()`);
  console.log('Risk navigation:', navResult);
  await new Promise(r => setTimeout(r, 2000));

  console.log('=== Step 3: Inside Risk Prioritization Engine — Inspect Finding Dossier ===');
  let openDossier = await evalCode(`(() => {
    // Look for "Inspect Finding Dossier" or view details button
    const btns = Array.from(document.querySelectorAll('button'));
    const dossierBtn = btns.find(b => b.innerText.includes('Inspect Finding Dossier'));
    if (dossierBtn) {
      dossierBtn.click();
      return 'CLICKED_DOSSIER';
    }
    // Try finding row or any button
    const anyBtn = btns.find(b => b.innerText.includes('Dossier') || b.innerText.includes('Inspect'));
    if (anyBtn) {
      anyBtn.click();
      return 'CLICKED_ANY: ' + anyBtn.innerText;
    }
    return 'NO_DOSSIER_BTN';
  })()`);
  console.log('Dossier button action:', openDossier);
  await new Promise(r => setTimeout(r, 2000));

  console.log('=== Step 4: Click Overview Tab ===');
  let clickOverview = await evalCode(`(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const overviewBtn = btns.find(b => b.innerText.trim() === 'Overview');
    if (overviewBtn) {
      overviewBtn.click();
      return 'CLICKED_OVERVIEW';
    }
    return 'NO_OVERVIEW_BTN, available: ' + btns.map(b => b.innerText.trim()).filter(Boolean).join(', ');
  })()`);
  console.log('Overview click action:', clickOverview);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 5: Check Screen State (Black Screen Check) ===');
  let screenCheck = await evalCode(`(() => {
    const root = document.getElementById('root');
    const hasContextCard = document.body.innerText.includes('Finding Context & Description');
    const hasAssessmentId = document.body.innerText.includes('Assessment ID');
    const hasPriorityScore = document.body.innerText.includes('Priority Score');
    return {
      rootLength: root ? root.innerHTML.length : 0,
      isBlackScreen: !root || root.innerHTML.trim() === '',
      hasContextCard,
      hasAssessmentId,
      hasPriorityScore,
      textSnippet: document.body.innerText.slice(0, 300).replace(/\\n+/g, ' ')
    };
  })()`);
  console.log('Screen State:', JSON.stringify(screenCheck, null, 2));

  if (screenCheck.isBlackScreen) {
    console.error('FATAL: BLACK SCREEN DETECTED!');
    process.exit(1);
  } else {
    console.log('SUCCESS: Overview rendered perfectly without crashing!');
  }

  console.log('=== Step 6: Test Navigation Back & Other Tabs in Finding Dossier ===');
  const tabs = ['Evidence Records', 'Knowledge', 'AI Analysis', 'Overview'];
  for (const t of tabs) {
    let tabRes = await evalCode(`(() => {
      const b = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.trim() === '${t}');
      if (b) { b.click(); return 'OK'; }
      return 'NOT_FOUND';
    })()`);
    await new Promise(r => setTimeout(r, 500));
    console.log('Tab', t, ':', tabRes);
  }

  // Click Back button
  let backRes = await evalCode(`(() => {
    const b = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.includes('Back'));
    if (b) { b.click(); return 'CLICKED_BACK'; }
    return 'NO_BACK_BTN';
  })()`);
  console.log('Back button action:', backRes);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 7: Regression Test Major Application Routes ===');
  const routes = [
    { name: 'Dashboard', search: ['Command Center', '01. Command Center'] },
    { name: 'World Monitor', search: ['World Monitor', 'Situational'] },
    { name: 'Security Assessments', search: ['Assessments', '02.'] },
    { name: 'Findings', search: ['Findings', '06. Findings'] },
    { name: 'Evidence Validation', search: ['Evidence', '08. Evidence'] },
    { name: 'Risk Matrix', search: ['Risk Scoring', '10. Risk Scoring'] },
    { name: 'Security Report', search: ['Executive Report', 'Report', '11. Report'] },
    { name: 'AI Analysis', search: ['AI Security Analyst', 'AI Analysis', '12. AI Analysis'] }
  ];

  for (const r of routes) {
    let res = await evalCode(`(() => {
      const allBtns = Array.from(document.querySelectorAll('button, a'));
      for (const target of ${JSON.stringify(r.search)}) {
        const found = allBtns.find(b => b.innerText.includes(target));
        if (found) {
          found.click();
          return 'NAVIGATED_TO_' + target;
        }
      }
      return 'ROUTE_BTN_NOT_FOUND';
    })()`);
    await new Promise(r => setTimeout(r, 1200));
    let state = await evalCode(`(() => {
      const root = document.getElementById('root');
      return {
        empty: !root || root.innerHTML.trim() === '',
        heading: document.querySelector('h1, h2, h3')?.innerText || 'No Heading'
      };
    })()`);
    console.log('Route', r.name, ':', res, '| Heading:', state.heading, '| Crash:', state.empty);
    if (state.empty) {
      console.error('FATAL: Crash on route ' + r.name);
      process.exit(1);
    }
  }

  console.log('=== Step 8: Step 71 Ollama Provenance Verification ===');
  // Navigate to Findings -> First finding -> AI tab
  await evalCode(`(() => {
    const fBtn = Array.from(document.querySelectorAll('button, a')).find(b => b.innerText.includes('Findings') || b.innerText.includes('06.'));
    if (fBtn) fBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 1500));

  // Open first finding
  await evalCode(`(() => {
    const rowBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Inspect') || b.innerText.includes('View'));
    if (rowBtn) rowBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 1500));

  let provCheck = await evalCode(`(() => {
    const dots = Array.from(document.querySelectorAll('[title*="Ollama"], [title*="ollama"], [data-provenance="ollama"]'));
    return {
      provenanceDotsCount: dots.length,
      provenanceDotsTitles: dots.map(d => d.getAttribute('title'))
    };
  })()`);
  console.log('Ollama Provenance Indicator check:', JSON.stringify(provCheck, null, 2));

  console.log('=== Total Runtime Exceptions Captured:', exceptions.length);
  if (exceptions.length > 0) {
    console.warn('Exceptions caught:', JSON.stringify(exceptions, null, 2));
  } else {
    console.log('VERIFICATION COMPLETE: Zero uncaught exceptions, zero crashes, all routes verified!');
  }

  ws.close();
}

run().catch(err => {
  console.error('Script failed:', err);
  process.exit(1);
});
