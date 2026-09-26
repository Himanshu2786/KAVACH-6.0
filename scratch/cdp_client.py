import asyncio
import json
import urllib.request
import websockets
import subprocess
import os

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

class CDPBrowser:
    def __init__(self, profile_name="default", width=1920, height=1080):
        self.profile_dir = os.path.join(r"C:\Users\Himanshu Raj\AppData\Local\Temp", f"kavach_profile_{profile_name}")
        self.port = 9222 if profile_name == "default" else 9223 if profile_name == "team1" else 9224
        self.width = width
        self.height = height
        self.proc = None
        self.ws = None
        self.msg_id = 0
        self.console_logs = []
        self.network_events = []

    async def start(self, url="http://localhost:5173"):
        os.makedirs(self.profile_dir, exist_ok=True)
        cmd = [
            CHROME_PATH,
            f"--remote-debugging-port={self.port}",
            "--headless=new",
            f"--window-size={self.width},{self.height}",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={self.profile_dir}",
            url
        ]
        self.proc = subprocess.Popen(cmd)
        await asyncio.sleep(2)
        
        # Connect to target
        res = urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json")
        targets = json.loads(res.read().decode())
        page_target = next(t for t in targets if t.get("type") == "page")
        self.ws = await websockets.connect(page_target["webSocketDebuggerUrl"], max_size=10_000_000)
        
        # Enable domains
        await self.send("Runtime.enable")
        await self.send("Page.enable")
        await self.send("DOM.enable")
        await self.send("Console.enable")
        await self.send("Network.enable")
        
        # Set viewport
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": self.width,
            "height": self.height,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        await asyncio.sleep(1)

        # Handle boot sequence if failsafe appears
        await self.dismiss_boot_if_needed()

    async def dismiss_boot_if_needed(self):
        # Wait up to 3.5s for boot sequence
        for _ in range(8):
            has_login = await self.eval_js("Boolean(document.querySelector('#kavach-user-id'))")
            has_header = await self.eval_js("Boolean(document.querySelector('header span'))")
            if has_login or has_header:
                return
            # Check if failsafe button exists
            has_continue = await self.eval_js("""
                (() => {
                    const btns = document.querySelectorAll('button');
                    for (const b of btns) {
                        if (b.innerText.includes('Continue')) {
                            b.click();
                            return true;
                        }
                    }
                    return false;
                })()
            """)
            if has_continue:
                await asyncio.sleep(1)
                return
            await asyncio.sleep(0.5)

    async def send(self, method, params=None):
        self.msg_id += 1
        req_id = self.msg_id
        payload = {"id": req_id, "method": method}
        if params:
            payload["params"] = params
        await self.ws.send(json.dumps(payload))
        
        while True:
            msg = await self.ws.recv()
            data = json.loads(msg)
            if "method" in data:
                if data["method"] == "Console.messageAdded":
                    self.console_logs.append(data["params"]["message"])
                elif data["method"] == "Runtime.consoleAPICalled":
                    self.console_logs.append(data["params"])
                elif data["method"] == "Network.responseReceived":
                    self.network_events.append(data["params"])
            if data.get("id") == req_id:
                return data.get("result", {})

    async def eval_js(self, expression):
        res = await self.send("Runtime.evaluate", {
            "expression": expression,
            "awaitPromise": True,
            "returnByValue": True
        })
        if "exceptionDetails" in res:
            raise RuntimeError(f"JS Exception: {res['exceptionDetails']}")
        return res.get("result", {}).get("value")

    async def wait_for_selector(self, selector, timeout=10):
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < timeout:
            found = await self.eval_js(f"Boolean(document.querySelector('{selector}'))")
            if found:
                return True
            await asyncio.sleep(0.3)
        return False

    async def click(self, selector):
        script = f"""
            (() => {{
                const el = document.querySelector("{selector}");
                if (!el) throw new Error("Element not found: {selector}");
                el.scrollIntoView({{ block: "center", inline: "center" }});
                el.click();
            }})()
        """
        await self.eval_js(script)
        await asyncio.sleep(0.5)

    async def type_input(self, selector, text):
        script = f"""
            (() => {{
                const el = document.querySelector("{selector}");
                if (!el) throw new Error("Element not found: {selector}");
                el.focus();
                el.value = "";
                const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                nativeSetter.call(el, {json.dumps(text)});
                el.dispatchEvent(new Event("input", {{ bubbles: true }}));
                el.dispatchEvent(new Event("change", {{ bubbles: true }}));
            }})()
        """
        await self.eval_js(script)
        await asyncio.sleep(0.2)

    async def resize(self, width, height):
        self.width = width
        self.height = height
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": width < 600
        })
        await asyncio.sleep(0.5)

    async def navigate(self, url):
        await self.send("Page.navigate", {"url": url})
        await asyncio.sleep(1.5)
        await self.dismiss_boot_if_needed()

    async def close(self):
        if self.ws:
            await self.ws.close()
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=3)
            except Exception:
                self.proc.kill()
