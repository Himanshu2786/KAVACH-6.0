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

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.method === 'Runtime.consoleAPICalled') {
      console.log('CONSOLE:', data.params.type, data.params.args.map(a => a.value || a.description).join(' '));
    } else if (data.method === 'Runtime.exceptionThrown') {
      console.error('EXCEPTION THROWN:', data.params.exceptionDetails.text, data.params.exceptionDetails.exception?.description);
    }
  };

  await send('Runtime.enable');
  await send('Page.enable');

  // Check what buttons exist right now
  let res = await send('Runtime.evaluate', {
    expression: `Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean)`,
    returnByValue: true
  });
  console.log('Current buttons:', res.result?.value);

  // If Overview button exists, click it!
  res = await send('Runtime.evaluate', {
    expression: `(() => {
      const b = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.trim() === 'Overview');
      if (b) {
        b.click();
        return 'CLICKED_OVERVIEW';
      }
      return 'NO_OVERVIEW_BTN';
    })()`,
    returnByValue: true
  });
  console.log('Overview button action:', res.result?.value);

  await new Promise(r => setTimeout(r, 1000));

  res = await send('Runtime.evaluate', {
    expression: `(() => {
      const root = document.getElementById('root');
      return {
        rootInnerHtmlSnippet: root?.innerHTML?.slice(0, 200),
        rootEmpty: !root || root.innerHTML.trim() === '',
        bodyTextSnippet: document.body.innerText.slice(0, 200)
      };
    })()`,
    returnByValue: true
  });
  console.log('DOM State after clicking Overview:', res.result?.value);

  ws.close();
}
main().catch(console.error);
