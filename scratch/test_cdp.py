import subprocess
import time
import urllib.request
import json
import asyncio
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

async def test():
    # Start Chrome with remote debugging
    cmd = [
        CHROME_PATH,
        "--remote-debugging-port=9222",
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--user-data-dir=C:\\Users\\Himanshu Raj\\AppData\\Local\\Temp\\kavach_cdp_profile",
        "http://localhost:5173"
    ]
    proc = subprocess.Popen(cmd)
    try:
        await asyncio.sleep(2)
        # Query targets
        res = urllib.request.urlopen("http://127.0.0.1:9222/json")
        targets = json.loads(res.read().decode())
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]
        print("Connected to target:", page_target["title"], ws_url)
        
        async with websockets.connect(ws_url) as ws:
            # Enable Runtime and Page
            await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
            await ws.send(json.dumps({"id": 2, "method": "Page.enable"}))
            
            # Evaluate document.title and body text
            await ws.send(json.dumps({
                "id": 3,
                "method": "Runtime.evaluate",
                "params": {"expression": "document.title"}
            }))
            
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                if data.get("id") == 3:
                    print("Page Title Result:", data["result"]["result"]["value"])
                    break
    finally:
        proc.terminate()

asyncio.run(test())
