import asyncio
import threading
from flask import Flask
from bot import main as bot_main

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_bot():
    asyncio.run(bot_main())

# ✅ thread me start karo (safe way)
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
