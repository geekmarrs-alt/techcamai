import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        print("Navigating to login...")
        await page.goto("http://127.0.0.1:8000/login")

        print("Filling license...")
        await page.fill("input[name='identity']", "TCAI-DEMO-2026")

        print("Submitting...")
        await page.click("button[type='submit']")

        # Wait for something that indicates we are on the dashboard
        print("Waiting for dashboard element...")
        try:
            await page.wait_for_selector(".v2-shell", timeout=10000)
            print("Dashboard loaded.")
        except Exception as e:
            print(f"Dashboard did not load as expected: {e}")
            await page.screenshot(path="debug_failed_login.png")
            await browser.close()
            return

        # Take screenshot of polished Dashboard
        await page.screenshot(path="polished_dashboard_v2.png")
        print("Captured polished_dashboard_v2.png")

        # Check AI Assistant trigger - we can't easily test prompt() but we can check the JS is loaded
        js_loaded = await page.evaluate("typeof window.techcamaiAssistant !== 'undefined'")
        print(f"AI Assistant JS loaded: {js_loaded}")

        # Go to Alerts
        print("Navigating to alerts...")
        await page.goto("http://127.0.0.1:8000/alerts")
        await page.wait_for_selector(".alertlist", timeout=5000)
        await page.screenshot(path="polished_alerts_v2.png")
        print("Captured polished_alerts_v2.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
