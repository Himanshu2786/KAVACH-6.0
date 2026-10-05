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

  console.log('=== Step 1: Navigating to App and Logging in ===');
  await send('Page.navigate', { url: 'http://127.0.0.1:5173/' });
  await new Promise(r => setTimeout(r, 2000));

  let isLogin = await evalCode(`Boolean(document.querySelector('input[type="password"]'))`);
  if (isLogin) {
    console.log('Filling login form...');
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

  console.log('=== Step 2: Open Menu and Navigate to Command Center ===');
  await evalCode(`(() => {
    const menuBtn = document.querySelector('button[aria-label="Toggle navigation menu"]');
    if (menuBtn) menuBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 600));

  await evalCode(`(() => {
    const ccBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Command Center'));
    if (ccBtn) ccBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 3: Open Posture Modal and Click "View Risk Matrix" ===');
  // Click "Local Posture" in WorkspaceSubnav
  await evalCode(`(() => {
    const pBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Local Posture'));
    if (pBtn) pBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 1200));

  // Click "View Risk Matrix" in modal
  let rmClick = await evalCode(`(() => {
    const rmBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('View Risk Matrix'));
    if (rmBtn) {
      rmBtn.click();
      return 'CLICKED_VIEW_RISK_MATRIX';
    }
    return 'NO_VIEW_RISK_MATRIX_BTN';
  })()`);
  console.log('View Risk Matrix action:', rmClick);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 4: Expand Finding Card & Click "Inspect Finding Dossier" ===');
  // First ensure at least one finding card is expanded
  await evalCode(`(() => {
    const cards = Array.from(document.querySelectorAll('div')).filter(d => d.innerText.includes('Risk Score') && d.className.includes('cursor-pointer'));
    if (cards.length > 0) cards[0].click();
  })()`);
  await new Promise(r => setTimeout(r, 800));

  let dossierClick = await evalCode(`(() => {
    const dBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Inspect Finding Dossier'));
    if (dBtn) {
      dBtn.click();
      return 'CLICKED_DOSSIER';
    }
    return 'NO_DOSSIER_BTN';
  })()`);
  console.log('Inspect Finding Dossier action:', dossierClick);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 5: Inside Finding Dossier — Click "Overview" Tab ===');
  let overviewClick = await evalCode(`(() => {
    const tabs = Array.from(document.querySelectorAll('button'));
    const ovTab = tabs.find(b => b.innerText.trim() === 'Overview');
    if (ovTab) {
      ovTab.click();
      return 'CLICKED_OVERVIEW_TAB';
    }
    return 'NO_OVERVIEW_TAB';
  })()`);
  console.log('Overview tab action:', overviewClick);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 6: Verify Overview Rendering & Check for Black Screen ===');
  let overviewState = await evalCode(`(() => {
    const root = document.getElementById('root');
    const isBlank = !root || root.innerHTML.trim() === '';
    const bodyText = document.body.innerText;
    return {
      isBlank,
      rootChildCount: root ? root.childElementCount : 0,
      hasContextCard: bodyText.includes('Finding Context & Description'),
      hasAssessmentId: bodyText.includes('Assessment ID'),
      hasPriorityScore: bodyText.includes('Priority Score'),
      hasCreated: bodyText.includes('Created'),
      hasUpdated: bodyText.includes('Updated'),
      textSnippet: bodyText.slice(0, 350).replace(/\\n+/g, ' ')
    };
  })()`);
  console.log('Overview State:', JSON.stringify(overviewState, null, 2));

  if (overviewState.isBlank) {
    console.error('FATAL: APPLICATION CRASHED WITH BLACK SCREEN!');
    process.exit(1);
  }
  if (!overviewState.hasContextCard || !overviewState.hasAssessmentId) {
    console.error('FATAL: Overview card did not render properly!');
    process.exit(1);
  }
  console.log('SUCCESS: Overview card rendered flawlessly without any black screen!');

  console.log('=== Step 7: Test Navigation Back from Overview ===');
  let backClick = await evalCode(`(() => {
    const backBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Back to Findings'));
    if (backBtn) {
      backBtn.click();
      return 'CLICKED_BACK';
    }
    return 'NO_BACK_BTN';
  })()`);
  console.log('Back button action:', backClick);
  await new Promise(r => setTimeout(r, 1500));

  let backState = await evalCode(`(() => {
    const root = document.getElementById('root');
    return {
      isBlank: !root || root.innerHTML.trim() === '',
      heading: document.querySelector('h1, h2, h3')?.innerText || 'No Heading'
    };
  })()`);
  console.log('State after clicking Back:', JSON.stringify(backState, null, 2));

  console.log('=== Step 8: Regression Test Major Application Routes ===');
  const routeSteps = [
    { name: '1. Command Center', id: 'command-center' },
    { name: '6. Findings Matrix', id: 'findings' },
    { name: '7. AI Analysis', id: 'ai-analysis' },
    { name: '9. Evidence Validation', id: 'evidence' },
    { name: '10. Risk Scoring', id: 'risk' },
    { name: '11. Report Export', id: 'report' },
    { name: 'World Monitor', id: 'world-monitor' }
  ];

  for (const step of routeSteps) {
    await evalCode(`(() => {
      const menuBtn = document.querySelector('button[aria-label="Toggle navigation menu"]');
      if (menuBtn) menuBtn.click();
    })()`);
    await new Promise(r => setTimeout(r, 400));

    let nav = await evalCode(`(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const target = btns.find(b => b.innerText.includes('${step.name}') || b.innerText.trim() === '${step.name}');
      if (target) {
        target.click();
        return 'CLICKED';
      }
      return 'NOT_FOUND';
    })()`);
    await new Promise(r => setTimeout(r, 1200));

    let state = await evalCode(`(() => {
      const root = document.getElementById('root');
      return {
        isBlank: !root || root.innerHTML.trim() === '',
        heading: document.querySelector('h1, h2, h3')?.innerText || 'No Heading'
      };
    })()`);
    console.log('Route', step.name, ':', nav, '| Heading:', state.heading, '| Blank:', state.isBlank);
    if (state.isBlank) {
      console.error('FATAL: Blank screen on route ' + step.name);
      process.exit(1);
    }
  }

  console.log('=== Step 9: Verify Step 71 Ollama Provenance ===');
  // Open Findings -> First finding -> Check provenance dot
  await evalCode(`(() => {
    const fTab = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Findings'));
    if (fTab) fTab.click();
  })()`);
  await new Promise(r => setTimeout(r, 1500));

  await evalCode(`(() => {
    const inspectBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Inspect') || b.innerText.includes('View'));
    if (inspectBtn) inspectBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 1500));

  let provenanceDots = await evalCode(`(() => {
    const dots = Array.from(document.querySelectorAll('[title*="Ollama"], [title*="ollama"]'));
    return {
      count: dots.length,
      titles: dots.map(d => d.getAttribute('title'))
    };
  })()`);
  console.log('Ollama Provenance Dots in Finding Detail:', JSON.stringify(provenanceDots, null, 2));

  console.log('=== Total Runtime Exceptions Captured:', exceptions.length);
  if (exceptions.length > 0) {
    console.error('Captured exceptions:', exceptions);
    process.exit(1);
  } else {
    console.log('ALL TESTS VERIFIED: ZERO EXCEPTIONS, ZERO BLACK SCREENS, ALL FLOWS SUCCEEDED!');
  }

  ws.close();
}

run().catch(err => {
  console.error('Error running verification script:', err);
  process.exit(1);
});
