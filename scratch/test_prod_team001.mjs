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
      console.error('PROD BROWSER EXCEPTION:', data.params.exceptionDetails.text, data.params.exceptionDetails.exception?.description);
      exceptions.push(data.params.exceptionDetails);
    }
  });

  await send('Runtime.enable');
  await send('Page.enable');

  const evalCode = async (expr) => {
    const res = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    return res.result?.value;
  };

  console.log('=== Step 1: Navigate to Netlify Login ===');
  await send('Page.navigate', { url: 'https://kavach-security-system.netlify.app/login' });
  await new Promise(r => setTimeout(r, 3000));

  console.log('Logging in as TEAM001...');
  await evalCode(`(() => {
    const inputs = Array.from(document.querySelectorAll('input'));
    const userInput = inputs.find(i => i.placeholder?.includes('ID') || i.type === 'text');
    const passInput = document.querySelector('input[type="password"]');
    if (userInput) {
      userInput.value = 'TEAM001';
      userInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
    if (passInput) {
      passInput.value = 'Team@Kavach2026!';
      passInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
    const submitBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SIGN IN'));
    if (submitBtn) submitBtn.click();
  })()`);
  await new Promise(r => setTimeout(r, 5000));

  const currentUrl = await evalCode('window.location.href');
  console.log('URL after login:', currentUrl);

  const routes = [
    { url: 'https://kavach-security-system.netlify.app/command-center', name: 'Command Center' },
    { url: 'https://kavach-security-system.netlify.app/findings', name: 'Findings Matrix' },
    { url: 'https://kavach-security-system.netlify.app/risk', name: 'Risk Scoring' },
    { url: 'https://kavach-security-system.netlify.app/evidence', name: 'Evidence Validation' },
    { url: 'https://kavach-security-system.netlify.app/report', name: 'Security Report' },
    { url: 'https://kavach-security-system.netlify.app/ai-analysis', name: 'AI Analysis' }
  ];

  for (const r of routes) {
    await send('Page.navigate', { url: r.url });
    await new Promise(res => setTimeout(res, 2500));
    const s = await evalCode(`(() => {
      const root = document.getElementById('root');
      return {
        isBlank: !root || root.innerHTML.trim() === '',
        heading: document.querySelector('h1, h2, h3')?.innerText || 'No Heading',
        textLen: document.body.innerText.length
      };
    })()`);
    console.log(`[PROD NETLIFY] ${r.name} | Heading: ${s.heading} | textLen: ${s.textLen} | Blank: ${s.isBlank}`);
  }

  console.log('=== Total Runtime Exceptions Captured on Prod:', exceptions.length);
  ws.close();
}

run().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
