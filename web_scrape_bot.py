import asyncio
import aiohttp
import urllib.request
from typing import TYPE_CHECKING, Tuple
from playwright.async_api import Playwright, async_playwright
import subprocess
from rich import print
from utils import filename_enumerated

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
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(url) as response:
    #         content = await response.read()

    # with open(vid_name, "wb") as f:
    #     f.write(content)
    # was getting 20 byte files for some reason
    # run ffmpeg to convert to mp4
    # This is now an m3u8 file
    print("Converting to mp4...")
    subprocess.run(f'ffmpeg -y -i "{url}" -c copy "{vid_name}"', shell=True, check=True)
    print("Done Converting!")
    # GET THE EXIT CODE AND RETURN TRUE OR FALSE?
    return True
    # print("Done!")


async def download_video_instagram(url: str, vid_name: str):
    urllib.request.urlretrieve(url, vid_name)


async def handle_request_twitter(vid_name: str, request, unused_variable):
    # print(">>", request.method, request.url)
    # print(vid_name_small)
    if ".m3u8" in request.url:
        if "variant_version" in request.url:
            print("This is  maybe the video!", request.url)
            print(request.__dict__)
            print(dir(request))
            print("#" * 50)
            print(unused_variable)
            print("#" * 50)
            return request.url
            # There can still be multiple vids at this point from comments
            # await download_video_twitter(request.url, vid_name)
    return "NOT_M3U8"


async def handle_request_instagram(vid_name: str, request):
    print(">>", request.method, request.url)
    if ".mp4" in request.url:
        print(f"This is the video! {request.url}")
        await download_video_instagram(request.url, vid_name)


async def setup_browser(playwright: Playwright, storage_state: str) -> Tuple["Browser", "Page"]:
    chromium = playwright.chromium
    browser = await chromium.connect_over_cdp(BROWSERLESS_URL)
    context = await browser.new_context(storage_state=f"storage_states/{storage_state}")
    page = await context.new_page()
    return browser, page


async def scrape_twitter(url: str, vid_name: str):
    try:
        async with async_playwright() as playwright:
            # Connect to Browser and load context
            browser, page = await setup_browser(playwright, "twitter.json")

            await page.goto(url)

            # Create an empty list to store the coroutines
            request_handlers = []

            # Subscribe to "request" event and append the coroutines to the list
            page.on(
                "request",
                lambda request: request_handlers.append(
                    handle_request_twitter(vid_name, request, "ignore this")
                ),
            )
            await asyncio.sleep(5)

            # Close the browser
            await browser.close()

            # Return the list of coroutines
            urls = []
            for i, req in enumerate(request_handlers):
                vid_url = await req
                if vid_url != "NOT_M3U8":
                    print(i, vid_url, req)
                    urls.append(vid_url)
            print("!!!!" * 90)
            print(urls)
            print("!!!!" * 90)
            vids = []
            # urls = []  # remove this line to download all videos
            for x, url in enumerate(urls):
                # change Vid_name to be unique for each video
                vid_name_enumerated = filename_enumerated(vid_name, x)
                video_succeeded = await download_video_twitter(url, vid_name_enumerated)
                if video_succeeded:
                    vids.append(vid_name_enumerated)
            return vids
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

            page.on(
                "request",
                lambda request: asyncio.create_task(handle_request_instagram(vid_name, request)),
            )

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
