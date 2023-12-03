import asyncio
import aiohttp
from typing import TYPE_CHECKING, Tuple
from playwright.async_api import Playwright, async_playwright

if TYPE_CHECKING:
    from playwright.async_api._generated import Browser, Page

BROWSERLESS_URL = "SECRET"  # "ws://10.0.0.69:3000/"

if BROWSERLESS_URL == "SECRET":
    try:
        from secret import BROWSERLESS_URL
    except:
        raise Exception("You need to set your Browserless Url in secret.py!")


async def download_video_twitter(url: str, vid_name: str):
    # print(f"Downloading video... {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.read()

    with open(vid_name, "wb") as f:
        f.write(content)
    # print("Done!")


async def handle_request_twitter(vid_name: str, request):
    # print(">>", request.method, request.url)
    if ".mp4" in request.url:
        # print("This is the video!")
        await download_video_twitter(request.url, vid_name)


async def handle_request_instagram(vid_name: str, request):
    # print(">>", request.method, request.url)
    if ".mp4" in request.url:
        # print("This is the video!")
        await download_video_twitter(request.url, vid_name)


async def setup_browser(playwright: Playwright, storage_state: str) -> Tuple["Browser", "Page"]:
    chromium = playwright.chromium
    browser = await chromium.connect_over_cdp(BROWSERLESS_URL)
    context = await browser.new_context(storage_state=storage_state)
    page = await context.new_page()
    return browser, page


async def scrape_twitter(url: str, vid_name: str):
    try:
        async with async_playwright() as playwright:
            # Connect to Browser and load context
            browser, page = await setup_browser(playwright, "twitter.json")

            # Subscribe to "request" and "response" events.
            # page.on("request", handle_request_twitter)
            page.on("request", lambda request: asyncio.create_task(handle_request_twitter(vid_name, request)))
            # page.on("response", lambda response: print("<<", response.status, response.url))

            await page.goto(url)
            await asyncio.sleep(5)
            await browser.close()
        return True
    except Exception as e:
        print(e)
        return False


async def find_element_with_text(page, text):
    elements = await page.query_selector_all("*")
    for element in elements:
        if await element.text_content() == text:
            return element
    return None


async def scrape_instagram(url: str, vid_name: str):
    try:
        async with async_playwright() as playwright:
            # Connect to Browser and load context
            browser, page = await setup_browser(playwright, "instagram.json")

            page.on("request", lambda request: asyncio.create_task(handle_request_instagram(vid_name, request)))

            await page.goto(url)
            view_story_button = await find_element_with_text(page, "View story")
            if view_story_button:
                "Found View Story button!"
                await view_story_button.click()
            await asyncio.sleep(5)
            await browser.close()
        return True
    except Exception as e:
        print(e)
        return False


# # Replace with your actual URL and video name
# asyncio.run(scrape_twitter("https://twitter.com/example", "example_video"))
