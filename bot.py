import asyncio
import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from nudenet import NudeDetector
from database import add_user, add_warning, get_warnings

TOKEN = os.getenv("BOT_TOKEN")

detector = NudeDetector()

# ⏳ Auto delete
async def auto_delete(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass


# 👋 START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)

    msg = await update.message.reply_text(
        f"👋 Hey {user.first_name}!\n\n"
        "I'm a smart NSFW Protection Bot 🤖\n\n"
        "✨ What I do:\n"
        "• 🚫 Remove NSFW images instantly\n"
        "• ✏️ Monitor edited messages\n"
        "• 🧹 Auto-clean the chat\n\n"
        "➕ Add me to your group\n"
        "🔑 Give me admin (delete messages permission)\n\n"
        "Sit back and let me handle the mess 😎"
    )

    asyncio.create_task(auto_delete(msg, 30))


# 🖼️ PHOTO HANDLER
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = msg.from_user

    add_user(user.id)

    photo = msg.photo[-1]
    file = await photo.get_file()

    file_path = f"{user.id}.jpg"
    await file.download_to_drive(file_path)

    try:
        result = detector.detect(file_path)
    except:
        result = []

    if result:
        try:
            await msg.delete()
        except:
            pass

        add_warning(user.id)
        warnings = get_warnings(user.id)

        warn_msg = await msg.chat.send_message(
            f"{user.mention_html()} 🚫 NSFW content is not allowed!\n"
            f"⚠️ Warnings: {warnings}/3",
            parse_mode="HTML"
        )

        asyncio.create_task(auto_delete(warn_msg, 10))

        if warnings >= 3:
            try:
                await msg.chat.ban_member(user.id)
                ban_msg = await msg.chat.send_message(
                    f"🚫 {user.first_name} has been banned (Too many violations)"
                )
                asyncio.create_task(auto_delete(ban_msg, 10))
            except:
                pass

    try:
        os.remove(file_path)
    except:
        pass


# ✏️ EDITED MESSAGE
async def edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.edited_message

    try:
        warn = await msg.chat.send_message(
            f"{msg.from_user.mention_html()} edited a message.\n"
            f"⏳ This message will be deleted in 30 minutes.",
            parse_mode="HTML"
        )

        asyncio.create_task(auto_delete(msg, 1800))
        asyncio.create_task(auto_delete(warn, 20))
    except:
        pass


# ▶️ MAIN FUNCTION (IMPORTANT FIX)
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, edited_message))

    print("✅ Bot running...")

    await app.initialize()
    await app.start()
    await app.bot.initialize()   # extra safety

    # 🔥 THIS IS THE FIX (NO run_polling)
    await app.run_polling()
    # keep alive
    await asyncio.Event().wait()
