from playwright.sync_api import sync_playwright, Playwright
import time
import requests


def download_video(url: str):
    print(f"Downloading video... {url}")
    # download url
    # use requests to download video to file from url
    request = requests.get(url)
    with open("video.mp4", "wb") as f:
        f.write(request.content)
    print("Done!")


def handle_request(request):
    print(">>", request.method, request.url)
    if ".mp4" in request.url:
        "This is the video!"
        download_video(request.url)


def run(playwright: Playwright):
    # use a browserless chromium instance

    chromium = playwright.chromium
    # browser = chromium.launch(headless=False)
    browser = chromium.connect_over_cdp('ws://10.0.0.69:3000/')
    context = browser.new_context(storage_state="twitter.json")
    page = context.new_page()

    # Subscribe to "request" and "response" events.
    page.on("request", handle_request)
    page.on("response", lambda response: print("<<", response.status, response.url))
    page.goto("https://twitter.com/Israel/status/1710690179558555708?lang=en")
    time.sleep(45)
    # page.goto("https://twitter.com/")
    # time.sleep(10)

    browser.close()


with sync_playwright() as playwright:
    run(playwright)
