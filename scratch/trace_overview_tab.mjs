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
  await send('Runtime.enable');
  await send('Page.enable');

  const evalCode = async (expr) => {
    const res = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    return res.result?.value;
  };

  console.log('--- Step A: Navigate to /risk ---');
  await send('Page.navigate', { url: 'http://127.0.0.1:5173/risk' });
  await new Promise(r => setTimeout(r, 2000));

  console.log('Heading on /risk:', await evalCode(`document.querySelector('h1, h2, h3')?.innerText`));

  console.log('--- Step B: Expand Card & Click Inspect Finding Dossier ---');
  await evalCode(`(() => {
    const card = Array.from(document.querySelectorAll('div')).find(d => d.innerText.includes('Risk Score') && d.className.includes('cursor-pointer'));
    if (card) card.click();
  })()`);
  await new Promise(r => setTimeout(r, 800));

  let clickD = await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Inspect Finding Dossier'));
    if (btn) {
      btn.click();
      return 'CLICKED_DOSSIER';
    }
    return 'NO_DOSSIER_BTN';
  })()`);
  console.log('Inspect Finding Dossier click:', clickD);
  await new Promise(r => setTimeout(r, 2000));

  console.log('Heading on Dossier:', await evalCode(`document.querySelector('h1, h2, h3')?.innerText`));

  console.log('--- Step C: Click Overview Tab ---');
  let clickO = await evalCode(`(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Overview');
    if (btn) {
      btn.click();
      return 'CLICKED_OVERVIEW';
    }
    return 'NO_OVERVIEW_BTN';
  })()`);
  console.log('Overview click:', clickO);
  await new Promise(r => setTimeout(r, 1500));

  const pageContent = await evalCode(`document.body.innerText`);
  console.log('FULL PAGE TEXT AFTER CLICKING OVERVIEW:\n', pageContent);

  const rootCheck = await evalCode(`(() => {
    const r = document.getElementById('root');
    return {
      exists: Boolean(r),
      children: r ? r.childElementCount : 0,
      innerHTMLSnippet: r ? r.innerHTML.slice(0, 300) : ''
    };
  })()`);
  console.log('ROOT CHECK:', JSON.stringify(rootCheck, null, 2));

  ws.close();
}
run();
