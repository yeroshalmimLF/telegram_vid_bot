import logging
import time

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from utils import url_to_filename
from web_scrape_bot import scrape_twitter, scrape_instagram

TOKEN = "SECRET"

if TOKEN == "SECRET":
    try:
        from secret import TOKEN, ACCEPTED_TELEGRAM_USERS
    except:
        raise Exception("You need to set your telegram token in secret.py!")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me! FART!")
    # respond with current username
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your username is {update.effective_user.username}")



def check_for_downloaded_vid(vid_name: str):
    """Checks for up to 10 seconds if the video exists"""
    for i in range(10):
        try:
            with open(vid_name, "rb"):
                return True
        except FileNotFoundError:
            time.sleep(1)
    return False


async def handle_instagram_url(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("This is an instagram link!")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Instagram {url}")
    vid_name = url_to_filename(url)
    # send video.mp4
    success = await scrape_instagram(url, vid_name)
    if not success:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Failed to scrape somewhere!")
        return
    found = check_for_downloaded_vid(vid_name)
    if not found:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Failed to find video!")
        return
    await context.bot.send_video(chat_id=update.effective_chat.id, video=open(vid_name, "rb"))


async def handle_twitter_url(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("This is a twitter link!")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Twitter {url}")
    vid_name = url_to_filename(url)
    # send video.mp4
    success = await scrape_twitter(url, vid_name)
    if not success:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to scrape somewhere!")
        return
    found = check_for_downloaded_vid(vid_name)
    if not found:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to find video!")
        return
    await context.bot.send_video(chat_id=update.effective_chat.id, video=open(vid_name, "rb"))

    # download video
    # send video
    # delete video
    # delete me


async def handle_text_input(text: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    if text.startswith("https://x.com/"):
        await handle_twitter_url(text, update, context)
    elif text.startswith("https://twitter.com/"):
        await handle_twitter_url(text, update, context)
    elif ".instagram.com/" in text:
        await handle_instagram_url(text, update, context)

    else:
        print(f"This is not a twitter link! {text}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Unknown link {text}")


async def url_handler_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username not in ACCEPTED_TELEGRAM_USERS:
        print(f"User {update.effective_user.username} is not allowed to use this bot!")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"User {update.effective_user.username} is not allowed to use this bot!")
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
