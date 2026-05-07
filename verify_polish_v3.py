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
        # Use name='identity' for license
        await page.fill("input[name='identity']", "TCAI-DEMO-2026")

        print("Submitting...")
        # There might be multiple buttons, use type='submit'
        await page.click("button[type='submit']")

        # Give it a moment to redirect and render
        await asyncio.sleep(2)
        print(f"Current URL: {page.url}")

        # Take screenshot regardless
        await page.screenshot(path="debug_state.png")

        content = await page.content()
        if "Invalid license" in content:
            print("Login failed: Invalid license message found.")
        elif "v2-shell" in content:
            print("Dashboard V2 detected!")
        else:
            print("Unknown state. See debug_state.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
