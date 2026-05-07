import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Login
        await page.goto("http://127.0.0.1:8000/login")
        await page.fill("input[name='identity']", "TCAI-DEMO-2026")
        await page.click("button[type='submit']")
        await page.wait_for_url("http://127.0.0.1:8000/")

        # Take screenshot of polished Dashboard with AI insights
        await page.screenshot(path="polished_dashboard.png")
        print("Captured polished_dashboard.png")

        # Go to Alerts
        await page.goto("http://127.0.0.1:8000/alerts")
        await page.screenshot(path="polished_alerts.png")
        print("Captured polished_alerts.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
