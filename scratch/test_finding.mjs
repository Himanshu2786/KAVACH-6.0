async function main() {
  const targets = await (await fetch('http://127.0.0.1:9222/json')).json();
  const page = targets.find(t => t.type === 'page' && t.url.includes('5173'));
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 1;
  const send = (method, params = {}) => new Promise(res => {
    const msgId = id++;
    const handler = (event) => {
      const data = JSON.parse(event.data);
      if (data.id === msgId) { ws.removeEventListener('message', handler); res(data.result); }
    };
    ws.addEventListener('message', handler);
    ws.send(JSON.stringify({ id: msgId, method, params }));
  });
  await new Promise(r => ws.onopen = r);

  const res = await send('Runtime.evaluate', {
    expression: `(() => {
      const el = Array.from(document.querySelectorAll('div')).find(d => d.innerText && d.innerText.includes('Finding Context & Description'));
      return el ? el.innerText : 'NOT_FOUND';
    })()`,
    returnByValue: true
  });
  console.log('CARD TEXT:\n', res.result?.value);
  ws.close();
}
main().catch(console.error);
