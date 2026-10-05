async function main() {
  const res = await fetch('http://127.0.0.1:9222/json');
  const targets = await res.json();
  const page = targets.find(t => t.type === 'page' && t.url.includes('5173'));
  if (!page) {
    console.error('No KAVACH page found on 9222!');
    return;
  }

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 1;
  const pending = new Map();

  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const msgId = id++;
      pending.set(msgId, { resolve, reject });
      ws.send(JSON.stringify({ id: msgId, method, params }));
    });
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.id && pending.has(data.id)) {
      const { resolve } = pending.get(data.id);
      pending.delete(data.id);
      resolve(data.result);
    } else if (data.method === 'Runtime.consoleAPICalled') {
      console.log('[BROWSER CONSOLE]', data.params.type, data.params.args.map(a => a.value || a.description).join(' '));
    } else if (data.method === 'Runtime.exceptionThrown') {
      console.error('[BROWSER EXCEPTION]', data.params.exceptionDetails.text, data.params.exceptionDetails.exception?.description);
    }
  };

  await new Promise((res) => ws.onopen = res);
  await send('Runtime.enable');
  await send('Page.enable');

  console.log('--- Navigating to Command Center ---');
  await send('Page.navigate', { url: 'http://127.0.0.1:5173/command-center' });
  await new Promise(r => setTimeout(r, 1500));

  console.log('--- STEP 2: Clicking Security Posture card ---');
  let evalRes = await send('Runtime.evaluate', {
    expression: `(() => {
      const card = document.querySelector('[title="Click to view Security Posture assessment results"]');
      if (card) {
        card.click();
        return { clickedCard: true };
      }
      return { clickedCard: false };
    })()`,
    returnByValue: true
  });
  console.log('Posture card clicked:', evalRes.result?.value);

  await new Promise(r => setTimeout(r, 600));

  console.log('--- STEP 3: Clicking "View Risk Matrix" button ---');
  evalRes = await send('Runtime.evaluate', {
    expression: `(() => {
      const btn = Array.from(document.querySelectorAll('button')).find(b => (b.innerText || '').includes('View Risk Matrix'));
      if (btn) {
        btn.click();
        return { clicked: true, text: btn.innerText.trim() };
      }
      return { clicked: false, buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()) };
    })()`,
    returnByValue: true
  });
  console.log('View Risk Matrix result:', evalRes.result?.value);

  await new Promise(r => setTimeout(r, 1000));

  console.log('--- STEP 4: Risk Prioritization page state ---');
  evalRes = await send('Runtime.evaluate', {
    expression: `(() => {
      return {
        url: window.location.href,
        h1: document.querySelector('h1')?.innerText,
        findingIds: Array.from(document.querySelectorAll('.font-bold.text-cyan-400')).map(e => e.innerText)
      };
    })()`,
    returnByValue: true
  });
  console.log('Risk page state:', evalRes.result?.value);

  console.log('--- STEP 5: Clicking "Inspect Finding Dossier" ---');
  evalRes = await send('Runtime.evaluate', {
    expression: `(() => {
      const btn = Array.from(document.querySelectorAll('button')).find(b => (b.innerText || '').includes('Inspect Finding Dossier'));
      if (btn) {
        btn.click();
        return { clicked: true, text: btn.innerText.trim() };
      }
      return { clicked: false, buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()) };
    })()`,
    returnByValue: true
  });
  console.log('Inspect Finding Dossier result:', evalRes.result?.value);

  await new Promise(r => setTimeout(r, 1200));

  console.log('--- STEP 6: Finding Detail page state ---');
  evalRes = await send('Runtime.evaluate', {
    expression: `(() => {
      return {
        url: window.location.href,
        h1: document.querySelector('h1')?.innerText,
        tabs: Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean)
      };
    })()`,
    returnByValue: true
  });
  console.log('Finding Detail state:', evalRes.result?.value);

  console.log('--- STEP 7: Clicking "Overview" tab ---');
  evalRes = await send('Runtime.evaluate', {
    expression: `(() => {
      const overviewBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Overview');
      if (overviewBtn) {
        overviewBtn.click();
        return { clicked: true, text: overviewBtn.innerText.trim() };
      }
      return { clicked: false, buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()) };
    })()`,
    returnByValue: true
  });
  console.log('Overview tab click result:', evalRes.result?.value);

  await new Promise(r => setTimeout(r, 1500));

  console.log('--- STEP 8: Inspecting Page after Overview clicked ---');
  evalRes = await send('Runtime.evaluate', {
    expression: `(() => {
      const root = document.getElementById('root');
      return {
        url: window.location.href,
        rootInnerHtml: root ? root.innerHTML.slice(0, 500) : 'no root',
        rootLength: root ? root.innerHTML.length : 0,
        bodyTextSnippet: document.body.innerText.slice(0, 300),
        isBlackScreen: !root || root.innerHTML.trim() === ''
      };
    })()`,
    returnByValue: true
  });
  console.log('FINAL RESULT:', evalRes.result?.value);

  ws.close();
}

main().catch(console.error);
