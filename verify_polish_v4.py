import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        print("Navigating to login...")
        await page.goto("http://127.0.0.1:8000/login")

        print("Filling admin credentials...")
        await page.fill("input[name='identity']", "admin")
        await page.fill("input[name='password']", "techcamai123")

        print("Submitting...")
        await page.click("button[type='submit']")

        # Give it a moment to redirect and render
        await asyncio.sleep(3)
        print(f"Current URL: {page.url}")

        # Take screenshot
        await page.screenshot(path="polished_dashboard_v2.png")

        content = await page.content()
        if "v2-shell" in content:
            print("Dashboard V2 detected!")
        else:
            print("Dashboard V2 NOT detected.")

        # Go to Alerts
        print("Navigating to alerts...")
        await page.goto("http://127.0.0.1:8000/alerts")
        await asyncio.sleep(2)
        await page.screenshot(path="polished_alerts_v2.png")
        print("Captured polished_alerts_v2.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
