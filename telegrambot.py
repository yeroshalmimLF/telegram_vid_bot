import logging
import time

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from utils import url_to_filename, get_vid_size
from web_scrape_bot import scrape_reddit, scrape_twitter, scrape_instagram

TOKEN = "SECRET"

if TOKEN == "SECRET":
    try:
        from secret import TOKEN, ACCEPTED_TELEGRAM_USERS
    except:
        raise Exception("You need to set your telegram token in secret.py!")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me! FART!"
    )
    # respond with current username
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"Your username is {update.effective_user.username}"
    )


def check_for_downloaded_vid(vid_name: str):
    """Checks for up to 10 seconds if the video exists"""
    for i in range(10):
        try:
            with open(vid_name, "rb"):
                return True
        except FileNotFoundError:
            time.sleep(1)
    return False


async def handle_instagram_url(
    url: str, update: Update, context: ContextTypes.DEFAULT_TYPE, message_id: int = None
):
    print("This is an instagram link!")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Instagram {url}")
    vid_name = url_to_filename(url)
    # send video.mp4
    success = await scrape_instagram(url, vid_name)
    if not success:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Failed to scrape somewhere!"
        )
        return
    found = check_for_downloaded_vid(vid_name)
    if not found:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Failed to find video!"
        )
        return
    width, height = get_vid_size(vid_name)
    await context.bot.send_video(
        chat_id=update.effective_chat.id, video=open(vid_name, "rb"), width=width, height=height
    )


async def handle_reddit_url(
    url: str, update: Update, context: ContextTypes.DEFAULT_TYPE, message_id: int = None
):
    print("This is a reddit link!")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Reddit link found.", reply_to_message_id=message_id
    )
    vid_name = url_to_filename(url)
    # send video.mp4
    success = await scrape_reddit(url, vid_name_and_path=vid_name)
    if not success:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Failed to scrape somewhere!",
            reply_to_message_id=message_id,
        )
        return
    found = check_for_downloaded_vid(vid_name)
    if not found:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Failed to find video!",
            reply_to_message_id=message_id,
        )
        return
    width, height = get_vid_size(vid_name)
    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=open(vid_name, "rb"),
        width=width,
        height=height,
        reply_to_message_id=message_id,
    )


async def handle_twitter_url(
    url: str, update: Update, context: ContextTypes.DEFAULT_TYPE, message_id: int = None
):
    print("This is a twitter link!")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"Twitter {url}", reply_to_message_id=message_id
    )
    vid_name = url_to_filename(url)
    # send video.mp4
    max_attempts = 5
    for i in range(max_attempts):
        vids = await scrape_twitter(url, vid_name)
        if vids:
            break
        print(f"Failed to scrape {i} times!")
    if not vids:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Failed to scrape somewhere!",
            reply_to_message_id=message_id,
        )
        return
    print(vids)
    for vid in vids:
        found = check_for_downloaded_vid(vid_name=vid)
        # found = None
        if not found:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Failed to find video!",
                reply_to_message_id=message_id,
            )
            return
        width, height = get_vid_size(vid)
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=open(vid, "rb"),
            width=width,
            height=height,
            reply_to_message_id=message_id,
        )


async def handle_text_input(text: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_id = update.message.message_id
    if text.startswith("https://x.com/"):
        await handle_twitter_url(text, update, context, message_id)
    elif text.startswith("https://twitter.com/"):
        await handle_twitter_url(text, update, context, message_id)
    elif text.startswith("https://www.reddit.com"):
        # elif text.startswith("https://v.redd.it/"):
        await handle_reddit_url(text, update, context, message_id)
    elif "instagram.com/" in text:
        await handle_instagram_url(text, update, context, message_id)

    else:
        print(f"This is not a twitter link! {text}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Unknown link {text}",
            reply_to_message_id=update.message.message_id,
        )


async def url_handler_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username not in ACCEPTED_TELEGRAM_USERS:
        print(f"User {update.effective_user.username} is not allowed to use this bot!")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"User {update.effective_user.username} is not allowed to use this bot!",
        )
        return
    if update.message is None:
        print("This is not a message!")
        return
    text = update.message.text
    if text is None:
        print("This is not text!")
        return
    await handle_text_input(text, update, context)
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me! FARTSSSS! {}")


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)

    # message handler to handle random strings
    message_handler = MessageHandler(filters.TEXT, url_handler_func)

    application.add_handler(start_handler)
    application.add_handler(message_handler)

    application.run_polling()
