import asyncio
import os
import requests
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from database import add_user, add_warning, get_warnings

TOKEN = os.getenv("BOT_TOKEN")

API_USER = os.getenv("API_USER")
API_SECRET = os.getenv("API_SECRET")


# ⏳ Auto delete
async def auto_delete(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass


# 👋 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)

    msg = await update.message.reply_text(
        f"👋 Hey {user.first_name}!\n\n"
        "I'm a smart NSFW Protection Bot 🤖\n\n"
        "✨ What I do:\n"
        "• 🚫 Remove NSFW images instantly\n"
        "• ✏️ Monitor edited messages\n"
        "• 🧹 Keep chat clean\n\n"
        "Add me to group & give admin 😎"
    )

    asyncio.create_task(auto_delete(msg, 30))


# 🖼️ NSFW CHECK FUNCTION
def check_nsfw(image_path):
    url = "https://api.sightengine.com/1.0/check.json"

    files = {'media': open(image_path, 'rb')}
    data = {
        'models': 'nudity-2.0',
        'api_user': API_USER,
        'api_secret': API_SECRET
    }

    r = requests.post(url, files=files, data=data)
    result = r.json()

    try:
        nudity = result["nudity"]
        if nudity["sexual_activity"] > 0.5 or nudity["sexual_display"] > 0.5:
            return True
    except:
        pass

    return False


# 📸 PHOTO HANDLER
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = msg.from_user

    add_user(user.id)

    photo = msg.photo[-1]
    file = await photo.get_file()

    file_path = f"{user.id}.jpg"
    await file.download_to_drive(file_path)

    is_nsfw = check_nsfw(file_path)

    if is_nsfw:
        try:
            await msg.delete()
        except:
            pass

        add_warning(user.id)
        warnings = get_warnings(user.id)

        warn_msg = await msg.chat.send_message(
            f"{user.mention_html()} 🚫 NSFW content not allowed!\n"
            f"⚠️ Warnings: {warnings}/3",
            parse_mode="HTML"
        )

        asyncio.create_task(auto_delete(warn_msg, 10))

        if warnings >= 3:
            try:
                await msg.chat.ban_member(user.id)
            except:
                pass

    os.remove(file_path)


# ✏️ EDITED MESSAGE
async def edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.edited_message

    warn = await msg.chat.send_message(
        f"{msg.from_user.mention_html()} edited a message.\n"
        f"⏳ Will be deleted in 30 mins.",
        parse_mode="HTML"
    )

    asyncio.create_task(auto_delete(msg, 1800))
    asyncio.create_task(auto_delete(warn, 20))


# ▶️ MAIN
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, edited_message))

    print("✅ Bot running...")

    await app.run_polling()
