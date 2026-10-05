async function run() {
  const targets = await (await fetch('http://127.0.0.1:9222/json')).json();
  const page = targets.find(t => t.type === 'page' && t.url.includes('5173'));
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

  console.log('Navigating to http://127.0.0.1:5173/command-center');
  await send('Page.navigate', { url: 'http://127.0.0.1:5173/command-center' });
  await new Promise(r => setTimeout(r, 2000));

  let loginCheck = await evalCode(`Boolean(document.querySelector('input[type="password"]'))`);
  if (loginCheck) {
    console.log('Logging in...');
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
  }

  console.log('Current page heading:', await evalCode(`document.querySelector('h1, h2, h3')?.innerText`));
  console.log('Current buttons:', await evalCode(`Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean)`));

  // If on Command Center, click Overall Security Posture KPI card or directly navigate to risk
  console.log('Navigating to /risk...');
  await send('Page.navigate', { url: 'http://127.0.0.1:5173/risk' });
  await new Promise(r => setTimeout(r, 2000));

  console.log('Risk page heading:', await evalCode(`document.querySelector('h1, h2, h3')?.innerText`));
  console.log('Buttons on Risk page:', await evalCode(`Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean)`));

  // Expand first card
  await evalCode(`(() => {
    const card = Array.from(document.querySelectorAll('div')).find(d => d.innerText.includes('Risk Score') && d.className.includes('cursor-pointer'));
    if (card) card.click();
  })()`);
  await new Promise(r => setTimeout(r, 1000));

  console.log('Buttons after expanding card:', await evalCode(`Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean)`));

  // Click Inspect Finding Dossier
  let dossierAction = await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Inspect Finding Dossier'));
    if (btn) {
      btn.click();
      return 'CLICKED_DOSSIER';
    }
    return 'NO_DOSSIER_BTN';
  })()`);
  console.log('Dossier action:', dossierAction);
  await new Promise(r => setTimeout(r, 2000));

  console.log('Page heading on Dossier:', await evalCode(`document.querySelector('h1, h2, h3')?.innerText`));
  console.log('Buttons on Dossier page:', await evalCode(`Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean)`));

  // Click Overview tab
  let ovAction = await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Overview');
    if (btn) {
      btn.click();
      return 'CLICKED_OVERVIEW';
    }
    return 'NO_OVERVIEW_BTN';
  })()`);
  console.log('Overview action:', ovAction);
  await new Promise(r => setTimeout(r, 2000));

  // Inspect state
  let state = await evalCode(`(() => {
    const root = document.getElementById('root');
    const text = document.body.innerText;
    return {
      rootLength: root ? root.innerHTML.length : 0,
      isBlank: !root || root.innerHTML.trim() === '',
      hasFindingContext: text.includes('Finding Context & Description'),
      hasAssessmentId: text.includes('Assessment ID'),
      hasPriorityScore: text.includes('Priority Score'),
      hasCreated: text.includes('Created'),
      hasUpdated: text.includes('Updated'),
      textSnippet: text.slice(0, 350).replace(/\\n+/g, ' ')
    };
  })()`);
  console.log('OVERVIEW STATE CHECK:', JSON.stringify(state, null, 2));

  // Test other tabs
  for (const tab of ['Evidence Records', 'Knowledge', 'AI Analysis', 'Risk Scoring']) {
    let t = await evalCode(`(() => {
      const b = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.trim() === '${tab}');
      if (b) { b.click(); return 'OK'; }
      return 'NOT_FOUND';
    })()`);
    await new Promise(r => setTimeout(r, 500));
    console.log('Tab', tab, ':', t);
  }

  // Click Back
  let back = await evalCode(`(() => {
    const b = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.includes('Back'));
    if (b) { b.click(); return 'CLICKED_BACK'; }
    return 'NO_BACK';
  })()`);
  console.log('Back action:', back);
  await new Promise(r => setTimeout(r, 1500));

  console.log('Exceptions count:', exceptions.length);
  if (exceptions.length > 0) {
    console.error('Exceptions:', exceptions);
    process.exit(1);
  }

  ws.close();
}

run().catch(e => {
  console.error(e);
  process.exit(1);
});
