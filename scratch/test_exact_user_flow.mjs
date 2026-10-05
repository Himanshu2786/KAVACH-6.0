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

  console.log('=== Step 1: Navigating to Command Center ===');
  await send('Page.navigate', { url: 'http://127.0.0.1:5173/' });
  await new Promise(r => setTimeout(r, 2000));

  // Check login
  let isLogin = await evalCode(`Boolean(document.querySelector('input[type="password"]'))`);
  if (isLogin) {
    console.log('Authenticating as ADMIN001...');
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

  // Go to Command Center if not there
  await evalCode(`(() => {
    const ccBtn = Array.from(document.querySelectorAll('button, a')).find(b => b.innerText.includes('Command Center'));
    if (ccBtn) ccBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 2: Open "Local Posture" modal ===');
  let openPosture = await evalCode(`(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const pBtn = btns.find(b => b.innerText.includes('Local Posture') || b.innerText.includes('POSTURE'));
    if (pBtn) {
      pBtn.click();
      return 'CLICKED_POSTURE_CARD';
    }
    return 'NO_POSTURE_BTN, buttons: ' + btns.map(b => b.innerText.trim()).filter(Boolean).join(', ');
  })()`);
  console.log('Posture modal open:', openPosture);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 3: Click "View Risk Matrix" inside modal ===');
  let clickRiskMatrix = await evalCode(`(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const rmBtn = btns.find(b => b.innerText.includes('View Risk Matrix'));
    if (rmBtn) {
      rmBtn.click();
      return 'CLICKED_VIEW_RISK_MATRIX';
    }
    return 'NO_VIEW_RISK_MATRIX_BTN, buttons: ' + btns.map(b => b.innerText.trim()).filter(Boolean).join(', ');
  })()`);
  console.log('View Risk Matrix button action:', clickRiskMatrix);
  await new Promise(r => setTimeout(r, 2000));

  console.log('=== Step 4: Inside Risk Matrix — Click Finding / Inspect Finding Dossier ===');
  let openDossier = await evalCode(`(() => {
    // Try finding "Inspect Finding Dossier" button
    let btns = Array.from(document.querySelectorAll('button'));
    let dBtn = btns.find(b => b.innerText.includes('Inspect Finding Dossier'));
    if (dBtn) {
      dBtn.click();
      return 'CLICKED_INSPECT_DOSSIER_DIRECT';
    }
    // If cards are collapsed, click first finding card header row to expand it
    const findingHeaders = Array.from(document.querySelectorAll('div')).filter(d => d.innerText.includes('Risk Score') && d.className.includes('cursor-pointer'));
    if (findingHeaders.length > 0) {
      findingHeaders[0].click();
      return 'EXPANDED_FIRST_CARD';
    }
    return 'NO_FINDING_CARDS_FOUND';
  })()`);
  console.log('Inspect Dossier step 1:', openDossier);
  await new Promise(r => setTimeout(r, 1500));

  // If we expanded first card, now click "Inspect Finding Dossier"
  let clickDossierBtn = await evalCode(`(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const dBtn = btns.find(b => b.innerText.includes('Inspect Finding Dossier'));
    if (dBtn) {
      dBtn.click();
      return 'CLICKED_INSPECT_DOSSIER_AFTER_EXPAND';
    }
    return 'NO_INSPECT_BTN_FOUND';
  })()`);
  console.log('Inspect Dossier step 2:', clickDossierBtn);
  await new Promise(r => setTimeout(r, 2000));

  console.log('=== Step 5: Inside Finding Dossier — Click "Overview" button ===');
  let clickOverview = await evalCode(`(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const ovBtn = btns.find(b => b.innerText.trim() === 'Overview');
    if (ovBtn) {
      ovBtn.click();
      return 'CLICKED_OVERVIEW_TAB';
    }
    return 'NO_OVERVIEW_TAB_FOUND, buttons: ' + btns.map(b => b.innerText.trim()).filter(Boolean).join(', ');
  })()`);
  console.log('Overview click result:', clickOverview);
  await new Promise(r => setTimeout(r, 1500));

  console.log('=== Step 6: Verify Page State and Overview Content ===');
  let verifyResult = await evalCode(`(() => {
    const root = document.getElementById('root');
    const isBlank = !root || root.innerHTML.trim() === '';
    const text = document.body.innerText;
    return {
      isBlank,
      rootChildCount: root ? root.childElementCount : 0,
      hasContextCard: text.includes('Finding Context & Description'),
      hasAssessmentId: text.includes('Assessment ID'),
      hasPriorityScore: text.includes('Priority Score'),
      hasCreated: text.includes('Created'),
      hasUpdated: text.includes('Updated'),
      textSample: text.slice(0, 400).replace(/\\n+/g, ' ')
    };
  })()`);
  console.log('Verify Result:', JSON.stringify(verifyResult, null, 2));

  if (verifyResult.isBlank) {
    console.error('FAIL: BLACK SCREEN OCCURRED!');
    process.exit(1);
  }
  if (!verifyResult.hasContextCard || !verifyResult.hasAssessmentId) {
    console.error('FAIL: Overview card content did not render!');
    process.exit(1);
  }

  console.log('SUCCESS: Overview rendered completely without black screen or errors!');

  console.log('=== Step 7: Test Navigation Back from Overview ===');
  let backResult = await evalCode(`(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const backBtn = btns.find(b => b.innerText.includes('Back to Findings') || b.innerText.includes('Back'));
    if (backBtn) {
      backBtn.click();
      return 'CLICKED_BACK_BTN';
    }
    return 'NO_BACK_BTN';
  })()`);
  console.log('Back navigation:', backResult);
  await new Promise(r => setTimeout(r, 1500));

  let afterBackCheck = await evalCode(`(() => {
    const root = document.getElementById('root');
    return {
      isBlank: !root || root.innerHTML.trim() === '',
      heading: document.querySelector('h1, h2, h3')?.innerText || 'No Heading'
    };
  })()`);
  console.log('After Back state:', JSON.stringify(afterBackCheck, null, 2));

  console.log('=== Exceptions count:', exceptions.length);
  if (exceptions.length > 0) {
    console.error('Captured exceptions:', exceptions);
    process.exit(1);
  } else {
    console.log('PERFECT: Flow completed with 0 runtime exceptions!');
  }

  ws.close();
}

run().catch(err => {
  console.error('Fatal error in script:', err);
  process.exit(1);
});
