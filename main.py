import asyncio
import threading
import os
from flask import Flask
from bot import main as bot_main

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_bot():
    asyncio.run(bot_main())

# start bot in background
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # 🔥 IMPORTANT
    app.run(host="0.0.0.0", port=port)
