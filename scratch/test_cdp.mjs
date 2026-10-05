import http from 'node:http';

async function main() {
  const res = await fetch('http://127.0.0.1:9222/json');
  const targets = await res.json();
  const page = targets.find(t => t.type === 'page' && t.url.includes('5173'));
  if (!page) {
    console.error('No KAVACH page found on 9222!');
    return;
  }
  console.log('Connecting to:', page.title, page.url, page.webSocketDebuggerUrl);

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
  console.log('CDP WebSocket connected!');

  await send('Runtime.enable');
  await send('Page.enable');

  // Let's inspect the current DOM title, active elements, buttons
  const evalRes = await send('Runtime.evaluate', {
    expression: `(() => {
      const buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim());
      return {
        url: window.location.href,
        buttons: buttons.filter(Boolean).slice(0, 30),
        bodySnippet: document.body.innerText.slice(0, 300)
      };
    })()`,
    returnByValue: true
  });

  console.log('Page state:', JSON.stringify(evalRes.result?.value, null, 2));

  ws.close();
}

main().catch(console.error);
