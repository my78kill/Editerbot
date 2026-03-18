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

# ⏳ Auto delete function
async def auto_delete(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

# 👋 START COMMAND (ENGLISH WELCOME)
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


# 🖼️ PHOTO HANDLER (NSFW DETECTION)
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

    # 🔞 If NSFW detected
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

        # 🚫 Ban after 3 warnings
        if warnings >= 3:
            try:
                await msg.chat.ban_member(user.id)
                ban_msg = await msg.chat.send_message(
                    f"🚫 {user.first_name} has been banned (Too many NSFW violations)"
                )
                asyncio.create_task(auto_delete(ban_msg, 10))
            except:
                pass

    # 🧹 delete local file
    try:
        os.remove(file_path)
    except:
        pass


# ✏️ EDITED MESSAGE HANDLER
async def edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.edited_message

    try:
        warn = await msg.chat.send_message(
            f"{msg.from_user.mention_html()} edited a message.\n"
            f"⏳ This message will be deleted in 30 minutes.",
            parse_mode="HTML"
        )

        asyncio.create_task(auto_delete(msg, 1800))   # 30 min
        asyncio.create_task(auto_delete(warn, 20))

    except:
        pass


# 💬 OPTIONAL: NORMAL MESSAGE CLEAN (BOT MESSAGES AUTO DELETE)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    # Agar bot reply kare future me, to auto delete kar sake
    # (abhi placeholder hai)
    pass


# ▶️ RUN BOT
def run_bot():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))

    # Photo (NSFW check)
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Edited messages
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, edited_message))

    # Normal messages (optional)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    print("✅ Bot is running...")
    app.run_polling()
