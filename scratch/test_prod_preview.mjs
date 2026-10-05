async function run() {
  const targets = await (await fetch('http://127.0.0.1:9222/json')).json();
  const page = targets.find(t => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise(r => ws.onopen = r);
  let id = 1;
  const send = (method, params = {}) => new Promise((res, rej) => {
    const msgId = id++;
    const handler = (e) => {
      const data = JSON.parse(e.data);
      if (data.id === msgId) {
        ws.removeEventListener('message', handler);
        if (data.error) rej(data.error);
        else res(data.result);
      }
    };
    ws.addEventListener('message', handler);
    ws.send(JSON.stringify({ id: msgId, method, params }));
  });

  const exceptions = [];
  ws.addEventListener('message', (e) => {
    const data = JSON.parse(e.data);
    if (data.method === 'Runtime.exceptionThrown') {
      console.error('PREVIEW EXCEPTION:', data.params.exceptionDetails.text, data.params.exceptionDetails.exception?.description);
      exceptions.push(data.params.exceptionDetails);
    }
  });

  await send('Runtime.enable');
  await send('Page.enable');

  const evalCode = async (expr) => {
    const res = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    return res.result?.value;
  };

  console.log('=== Step 1: Navigate to Production Preview http://127.0.0.1:4173/login ===');
  await send('Page.navigate', { url: 'http://127.0.0.1:4173/login' });
  await new Promise(r => setTimeout(r, 2500));

  const title = await evalCode('document.title');
  console.log('Preview Page Title:', title);

  // Authenticate as ADMIN001
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
  await new Promise(r => setTimeout(r, 3000));

  const routes = [
    { url: 'http://127.0.0.1:4173/command-center', name: 'Command Center' },
    { url: 'http://127.0.0.1:4173/findings', name: 'Findings Matrix' },
    { url: 'http://127.0.0.1:4173/risk', name: 'Risk Scoring' },
    { url: 'http://127.0.0.1:4173/evidence', name: 'Evidence Validation' },
    { url: 'http://127.0.0.1:4173/report', name: 'Security Report' },
    { url: 'http://127.0.0.1:4173/ai-analysis', name: 'AI Analysis' }
  ];

  for (const r of routes) {
    await send('Page.navigate', { url: r.url });
    await new Promise(res => setTimeout(res, 2000));
    const s = await evalCode(`(() => {
      const root = document.getElementById('root');
      return {
        isBlank: !root || root.innerHTML.trim() === '',
        heading: document.querySelector('h1, h2, h3')?.innerText || 'No Heading',
        textLen: document.body.innerText.length
      };
    })()`);
    console.log(`[PROD PREVIEW] ${r.name} | Heading: ${s.heading} | textLen: ${s.textLen} | Blank: ${s.isBlank}`);
  }

  // Step 72 test on Preview
  console.log('=== Step 72 Regression on Preview ===');
  await send('Page.navigate', { url: 'http://127.0.0.1:4173/risk' });
  await new Promise(r => setTimeout(r, 2000));

  await evalCode(`(() => {
    const card = Array.from(document.querySelectorAll('div')).find(d => d.innerText.includes('Risk Score') && d.className.includes('cursor-pointer'));
    if (card) card.click();
  })()`);
  await new Promise(r => setTimeout(r, 1000));

  await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Inspect Finding Dossier'));
    if (btn) btn.click();
  })()`);
  await new Promise(r => setTimeout(r, 2000));

  await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Overview');
    if (btn) btn.click();
  })()`);
  await new Promise(r => setTimeout(r, 1500));

  const ovState = await evalCode(`(() => {
    const root = document.getElementById('root');
    const text = document.body.innerText.toLowerCase();
    return {
      isBlank: !root || root.innerHTML.trim() === '',
      hasFindingContext: text.includes('finding context'),
      hasAssessmentId: text.includes('assessment id'),
      hasPriorityScore: text.includes('priority score')
    };
  })()`);
  console.log('PREVIEW OVERVIEW STATE:', JSON.stringify(ovState, null, 2));

  console.log('=== Total Runtime Exceptions Captured on Preview:', exceptions.length);
  ws.close();
}

run().catch(err => {
  console.error('Preview error:', err);
  process.exit(1);
});
