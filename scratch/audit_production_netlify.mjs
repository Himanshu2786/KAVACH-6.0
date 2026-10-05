async function run() {
  const targets = await (await fetch('http://127.0.0.1:9222/json')).json();
  const page = targets.find(t => t.type === 'page');
  if (!page) {
    console.error('No Chrome page found on 127.0.0.1:9222');
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
      console.error('PROD BROWSER EXCEPTION:', data.params.exceptionDetails.text, data.params.exceptionDetails.exception?.description);
      exceptions.push(data.params.exceptionDetails);
    }
  };

  await send('Runtime.enable');
  await send('Page.enable');

  const evalCode = async (expr) => {
    const res = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    return res.result?.value;
  };

  console.log('=== Step 1: Navigate to Production Netlify URL ===');
  await send('Page.navigate', { url: 'https://kavach-security-system.netlify.app/login' });
  await new Promise(r => setTimeout(r, 4000));

  const prodTitle = await evalCode('document.title');
  console.log('Production Page Title:', prodTitle);

  // Authenticate as ADMIN001
  const isLoginPage = await evalCode(`Boolean(document.querySelector('input[type="password"]'))`);
  console.log('Is on Login Page:', isLoginPage);

  if (isLoginPage) {
    console.log('Submitting credentials to Render backend...');
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
    await new Promise(r => setTimeout(r, 5000));
  }

  const currentUrl = await evalCode('window.location.href');
  console.log('URL after login:', currentUrl);

  const prodRoutes = [
    { url: 'https://kavach-security-system.netlify.app/command-center', name: 'Command Center' },
    { url: 'https://kavach-security-system.netlify.app/findings', name: 'Findings Matrix' },
    { url: 'https://kavach-security-system.netlify.app/risk', name: 'Risk Scoring' },
    { url: 'https://kavach-security-system.netlify.app/evidence', name: 'Evidence Validation' },
    { url: 'https://kavach-security-system.netlify.app/report', name: 'Security Report' },
    { url: 'https://kavach-security-system.netlify.app/ai-analysis', name: 'AI Analysis' }
  ];

  for (const r of prodRoutes) {
    await send('Page.navigate', { url: r.url });
    await new Promise(res => setTimeout(res, 3000));
    const pageState = await evalCode(`(() => {
      const root = document.getElementById('root');
      return {
        isBlank: !root || root.innerHTML.trim() === '',
        textLen: document.body.innerText.length,
        heading: document.querySelector('h1, h2, h3')?.innerText || 'No Heading'
      };
    })()`);
    console.log(`[PROD] ${r.name} (${r.url}) | Heading: ${pageState.heading} | textLen: ${pageState.textLen} | Blank: ${pageState.isBlank}`);
  }

  // Step 72 test on Production
  console.log('=== Step 72 Regression on Production Netlify ===');
  await send('Page.navigate', { url: 'https://kavach-security-system.netlify.app/risk' });
  await new Promise(r => setTimeout(r, 3000));

  // Click Inspect Finding Dossier
  await evalCode(`(() => {
    const card = Array.from(document.querySelectorAll('div')).find(d => d.innerText.includes('Risk Score') && d.className.includes('cursor-pointer'));
    if (card) card.click();
  })()`);
  await new Promise(r => setTimeout(r, 1500));

  await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Inspect Finding Dossier'));
    if (btn) btn.click();
  })()`);
  await new Promise(r => setTimeout(r, 3000));

  // Click Overview tab
  await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Overview');
    if (btn) btn.click();
  })()`);
  await new Promise(r => setTimeout(r, 2000));

  const prodOverviewState = await evalCode(`(() => {
    const root = document.getElementById('root');
    const text = document.body.innerText.toLowerCase();
    return {
      isBlank: !root || root.innerHTML.trim() === '',
      hasFindingContext: text.includes('finding context'),
      hasAssessmentId: text.includes('assessment id'),
      hasPriorityScore: text.includes('priority score'),
      sample: document.body.innerText.slice(0, 200).replace(/\\n+/g, ' ')
    };
  })()`);
  console.log('PROD OVERVIEW STATE:', JSON.stringify(prodOverviewState, null, 2));

  console.log('=== Total Production Runtime Exceptions Captured:', exceptions.length);
  ws.close();
}

run().catch(err => {
  console.error('Audit production error:', err);
  process.exit(1);
});
