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

  await send('Network.enable');
  const netRequests = [];
  const responses = [];
  ws.addEventListener('message', (e) => {
    const data = JSON.parse(e.data);
    if (data.method === 'Network.requestWillBeSent') {
      if (data.params.request.url.includes('/api/')) {
        netRequests.push({ url: data.params.request.url, method: data.params.request.method });
      }
    }
    if (data.method === 'Network.responseReceived') {
      if (data.params.response.url.includes('/api/')) {
        responses.push({ url: data.params.response.url, status: data.params.response.status });
      }
    }
  });

  // Type login credentials and click SIGN IN
  await send('Runtime.evaluate', {
    expression: `(() => {
      const inputs = Array.from(document.querySelectorAll('input'));
      const u = inputs.find(i => i.placeholder?.includes('ID') || i.type === 'text');
      const p = document.querySelector('input[type="password"]');
      if (u) { u.value = 'ADMIN001'; u.dispatchEvent(new Event('input', { bubbles: true })); }
      if (p) { p.value = 'Admin@Kavach2026!'; p.dispatchEvent(new Event('input', { bubbles: true })); }
      const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SIGN IN'));
      if (btn) btn.click();
    })()`
  });

  await new Promise(r => setTimeout(r, 6000));
  console.log('API requests made:', netRequests);
  console.log('API responses:', responses);
  const text = (await send('Runtime.evaluate', { expression: 'document.body.innerText', returnByValue: true })).result.value;
  console.log('After login text sample:', text.slice(0, 300).replace(/\n+/g, ' '));
  ws.close();
}

run().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
