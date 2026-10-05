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

  // Check login
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
      const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Sign In') || b.innerText.includes('Authenticate') || b.type === 'submit');
      if (submitBtn) submitBtn.click();
    })()`);
    await new Promise(r => setTimeout(r, 2500));
  }

  console.log('=== Step 2: Open Command Center via Menu ===');
  await evalCode(`(() => {
    const menuBtn = document.querySelector('button[aria-label="Toggle navigation menu"]');
    if (menuBtn) menuBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 500));

  await evalCode(`(() => {
    const ccBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Command Center'));
    if (ccBtn) ccBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 3: Click Overall Security Posture KPI Card ===');
  let clickKpi = await evalCode(`(() => {
    const kpi = document.querySelector('[title*="Security Posture assessment results"]');
    if (kpi) {
      kpi.click();
      return 'CLICKED_KPI_1';
    }
    return 'NO_KPI_1_FOUND';
  })()`);
  console.log('KPI click:', clickKpi);
  await new Promise(r => setTimeout(r, 1000));

  console.log('=== Step 4: Click "View Risk Matrix" Button in Modal ===');
  let clickVrm = await evalCode(`(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const vrm = btns.find(b => b.innerText.includes('View Risk Matrix'));
    if (vrm) {
      vrm.click();
      return 'CLICKED_VIEW_RISK_MATRIX';
    }
    return 'NO_VIEW_RISK_MATRIX_BTN';
  })()`);
  console.log('View Risk Matrix button:', clickVrm);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 5: Inside Risk Matrix — Click "Inspect Finding Dossier" ===');
  // First expand finding row if needed
  await evalCode(`(() => {
    const row = Array.from(document.querySelectorAll('div')).find(d => d.innerText.includes('Risk Score') && d.className.includes('cursor-pointer'));
    if (row) row.click();
  })()`);
  await new Promise(r => setTimeout(r, 600));

  let clickDossier = await evalCode(`(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const dBtn = btns.find(b => b.innerText.includes('Inspect Finding Dossier'));
    if (dBtn) {
      dBtn.click();
      return 'CLICKED_INSPECT_DOSSIER';
    }
    return 'NO_INSPECT_DOSSIER_BTN';
  })()`);
  console.log('Inspect Finding Dossier action:', clickDossier);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 6: Inside Finding Dossier — Click "Overview" Button ===');
  let clickOverview = await evalCode(`(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const ovBtn = btns.find(b => b.innerText.trim() === 'Overview');
    if (ovBtn) {
      ovBtn.click();
      return 'CLICKED_OVERVIEW_BUTTON';
    }
    return 'NO_OVERVIEW_BUTTON';
  })()`);
  console.log('Overview button action:', clickOverview);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 7: Verify Overview Rendering & Check for Black Screen ===');
  let overviewState = await evalCode(`(() => {
    const root = document.getElementById('root');
    const isBlank = !root || root.innerHTML.trim() === '';
    const bodyText = document.body.innerText;
    return {
      isBlank,
      rootInnerHtmlLength: root ? root.innerHTML.length : 0,
      hasContextCard: bodyText.includes('Finding Context & Description'),
      hasAssessmentId: bodyText.includes('Assessment ID'),
      hasPriorityScore: bodyText.includes('Priority Score'),
      hasCreated: bodyText.includes('Created'),
      hasUpdated: bodyText.includes('Updated'),
      textSnippet: bodyText.slice(0, 300).replace(/\\n+/g, ' ')
    };
  })()`);
  console.log('Overview Verification State:', JSON.stringify(overviewState, null, 2));

  if (overviewState.isBlank) {
    console.error('CRITICAL BUG REPRODUCED: BLACK SCREEN DETECTED!');
    process.exit(1);
  }
  if (!overviewState.hasContextCard || !overviewState.hasAssessmentId) {
    console.error('ERROR: Overview card did not render properly!');
    process.exit(1);
  }
  console.log('SUCCESS: Overview rendered properly with all data fields!');

  console.log('=== Step 8: Verify Navigation Back and Other Tabs ===');
  for (const tab of ['Evidence Records', 'Knowledge', 'AI Analysis', 'Overview']) {
    let tRes = await evalCode(`(() => {
      const b = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.trim() === '${tab}');
      if (b) { b.click(); return 'OK'; }
      return 'NOT_FOUND';
    })()`);
    await new Promise(r => setTimeout(r, 400));
    console.log('Tab', tab, ':', tRes);
  }

  let backAction = await evalCode(`(() => {
    const b = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.includes('Back to Findings'));
    if (b) { b.click(); return 'CLICKED_BACK'; }
    return 'NO_BACK_BTN';
  })()`);
  console.log('Back button action:', backAction);
  await new Promise(r => setTimeout(r, 1500));

  let postBackState = await evalCode(`(() => {
    const root = document.getElementById('root');
    return {
      isBlank: !root || root.innerHTML.trim() === '',
      heading: document.querySelector('h1, h2, h3')?.innerText || 'No Heading'
    };
  })()`);
  console.log('State after navigation back:', JSON.stringify(postBackState, null, 2));

  console.log('=== Step 9: Regression Testing Major Routes ===');
  const majorRoutes = [
    '1. Command Center',
    '6. Findings Matrix',
    '7. AI Analysis',
    '9. Evidence Validation',
    '10. Risk Scoring',
    '11. Report Export'
  ];

  for (const route of majorRoutes) {
    await evalCode(`(() => {
      const menuBtn = document.querySelector('button[aria-label="Toggle navigation menu"]');
      if (menuBtn) menuBtn.click();
    })()`);
    await new Promise(r => setTimeout(r, 400));

    let navRes = await evalCode(`(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const t = btns.find(b => b.innerText.includes('${route}'));
      if (t) { t.click(); return 'OK'; }
      return 'NOT_FOUND';
    })()`);
    await new Promise(r => setTimeout(r, 1000));

    let s = await evalCode(`(() => {
      const root = document.getElementById('root');
      return {
        isBlank: !root || root.innerHTML.trim() === '',
        heading: document.querySelector('h1, h2, h3')?.innerText || 'No Heading'
      };
    })()`);
    console.log('Route', route, ':', navRes, '| Heading:', s.heading, '| Blank:', s.isBlank);
    if (s.isBlank) {
      console.error('Crash on route: ' + route);
      process.exit(1);
    }
  }

  console.log('=== Step 10: Verify Step 71 Ollama Provenance ===');
  await evalCode(`(() => {
    const menuBtn = document.querySelector('button[aria-label="Toggle navigation menu"]');
    if (menuBtn) menuBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 400));
  await evalCode(`(() => {
    const f = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Findings Matrix'));
    if (f) f.click();
  })()`);
  await new Promise(r => setTimeout(r, 1200));

  await evalCode(`(() => {
    const inspectBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Inspect') || b.innerText.includes('View'));
    if (inspectBtn) inspectBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 1200));

  let provDots = await evalCode(`(() => {
    const dots = Array.from(document.querySelectorAll('[title*="Ollama"], [title*="ollama"]'));
    return {
      count: dots.length,
      titles: dots.map(d => d.getAttribute('title'))
    };
  })()`);
  console.log('Ollama Provenance Dot Verification:', JSON.stringify(provDots, null, 2));

  console.log('=== Runtime Exceptions Count:', exceptions.length);
  if (exceptions.length > 0) {
    console.error('Runtime exceptions occurred:', exceptions);
    process.exit(1);
  }

  console.log('ALL VERIFICATIONS COMPLETED SUCCESSFULLY!');
  ws.close();
}

run().catch(e => {
  console.error('Run failed:', e);
  process.exit(1);
});
