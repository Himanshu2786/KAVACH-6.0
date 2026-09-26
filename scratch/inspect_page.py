import asyncio
import json
import urllib.request
import websockets
import subprocess
import os

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

async def inspect_ui():
    profile_dir = r"C:\Users\Himanshu Raj\AppData\Local\Temp\inspect_profile"
    cmd = [
        CHROME_PATH,
        "--remote-debugging-port=9225",
        "--headless=new",
        f"--user-data-dir={profile_dir}",
        "http://localhost:5173"
    ]
    proc = subprocess.Popen(cmd)
    try:
        await asyncio.sleep(2)
        res = urllib.request.urlopen("http://127.0.0.1:9225/json")
        targets = json.loads(res.read().decode())
        page_target = next(t for t in targets if t.get("type") == "page")
        
        async with websockets.connect(page_target["webSocketDebuggerUrl"]) as ws:
            async def send(method, params=None):
                payload = {"id": 1, "method": method}
                if params: payload["params"] = params
                await ws.send(json.dumps(payload))
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if data.get("id") == 1:
                        return data.get("result", {})

            await send("Runtime.enable")
            
            # Check what's in DOM
            res_html = await send("Runtime.evaluate", {
                "expression": "document.body.innerHTML",
                "returnByValue": True
            })
            html = res_html.get("result", {}).get("value", "")
            print("BODY HTML LENGTH:", len(html))
            print("BODY HTML SNIPPET:", html[:500])
            
            res_text = await send("Runtime.evaluate", {
                "expression": "document.body.innerText",
                "returnByValue": True
            })
            print("BODY INNER TEXT:\n", res_text.get("result", {}).get("value", ""))
    finally:
        proc.terminate()

asyncio.run(inspect_ui())
