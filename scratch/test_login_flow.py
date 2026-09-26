import asyncio
import json
from cdp_client import CDPBrowser

async def test_auth():
    browser = CDPBrowser("auth_quick", 1920, 1080)
    await browser.start("http://localhost:5173")
    try:
        # Clear session
        await browser.eval_js("""
            localStorage.removeItem('kavach_auth_token');
            localStorage.removeItem('kavach_auth_user');
            window.location.reload();
        """)
        await asyncio.sleep(1)
        await browser.dismiss_boot_if_needed()

        print("Waiting for login input #kavach-user-id...")
        found = await browser.wait_for_selector("#kavach-user-id", timeout=8)
        print("Login input found:", found)

        # 1. Invalid credentials
        print("Testing invalid credentials...")
        await browser.type_input("#kavach-user-id", "TEAM001")
        await browser.type_input("#kavach-password", "WrongPassword123!")
        await browser.click("button[type='submit']")
        await asyncio.sleep(1)
        
        err = await browser.eval_js("""
            (() => {
                const el = document.querySelector('[role=\"alert\"]');
                return el ? el.innerText : null;
            })()
        """)
        print("Error banner observed:", err)

        # 2. Valid credentials
        print("Testing valid credentials (TEAM001)...")
        await browser.type_input("#kavach-user-id", "TEAM001")
        await browser.type_input("#kavach-password", "Team@Kavach2026!")
        await browser.click("button[type='submit']")
        await asyncio.sleep(2)

        # 3. Check dashboard
        badge = await browser.eval_js("""
            (() => {
                const b = document.querySelector('header');
                return b ? b.innerText : null;
            })()
        """)
        print("Header content after login:", repr(badge[:100] if badge else None))

    finally:
        await browser.close()

asyncio.run(test_auth())
